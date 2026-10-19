import Foundation
import Observation
import StoreKit

/// StoreKit 2 订阅接入。
///
/// 佣金说明（2026/3/15 起，中国大陆）：
///   - 标准 25%
///   - Small Business Program（年收入 < 100 万美元）12%
///   - 首年后的自动续费 12%
///   务必申请 Small Business Program，12% 与 25% 相差一倍。
///   来源：https://stcn.com/article/detail/3675130.html
///
/// ⚠️ 上线前必须补的两件事：
///   1. App Store Server API 服务端校验（客户端可被越狱绕过）
///   2. App Store Server Notifications V2 处理续订/退款/取消
@MainActor
@Observable
final class PurchaseService {

    static let shared = PurchaseService()

    private(set) var products: [Product] = []
    private(set) var isPurchasing = false
    private(set) var lastError: String?

    private var updatesTask: Task<Void, Never>?

    init() {
        // 监听交易更新：续订、退款、家庭共享都会从这里进来。
        //
        // 两个关键点：
        // 1. 不能用 `guard let self else { return }` —— 那会让 for-await 循环
        //    在 self 释放时永久退出，之后再也收不到交易更新。
        // 2. 不要用 .background 优先级：handle 是 @MainActor，
        //    退款/撤销这类事件被排到后台会延迟处理，
        //    表现就是"用户已经退款了但会员还在"——这是收入漏洞。
        updatesTask = Task(priority: .userInitiated) { @MainActor in
            for await result in Transaction.updates {
                await PurchaseService.shared.handle(result)
            }
        }
    }

    // MARK: 加载商品

    func loadProducts() async {
        do {
            let ids = Plan.allCases.map(\.productID)
            products = try await Product.products(for: ids)
                .sorted { $0.price < $1.price }
        } catch {
            lastError = error.localizedDescription
        }
    }

    func product(for plan: Plan) -> Product? {
        products.first { $0.id == plan.productID }
    }

    /// StoreKit 返回的本地化价格（比写死的 ¥18 准确，会跟随地区变化）
    func localizedPrice(for plan: Plan) -> String? {
        product(for: plan)?.displayPrice
    }

    // MARK: 购买

    func purchase(_ plan: Plan) async -> Bool {
        guard let product = product(for: plan) ?? (try? await Product.products(for: [plan.productID]))?.first else {
            lastError = "商品未加载，请稍后重试"
            return false
        }

        isPurchasing = true
        defer { isPurchasing = false }

        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                await handle(verification)
                return Membership.shared.isPlus

            case .userCancelled:
                return false

            case .pending:
                // 家长控制等待批准等场景
                lastError = "购买待确认"
                return false

            @unknown default:
                return false
            }
        } catch {
            lastError = error.localizedDescription
            return false
        }
    }

    // MARK: 恢复购买

    func restore() async {
        try? await AppStore.sync()
        await refreshEntitlement()
    }

    // MARK: 交易处理

    private func handle(_ result: VerificationResult<Transaction>) async {
        guard case .verified(let transaction) = result else {
            // 未通过校验的交易一律忽略，不要给权益
            return
        }
        // 已退款的交易不能给权益
        guard transaction.revocationDate == nil else {
            await transaction.finish()
            return
        }

        // 到这里只代表签名有效；生产环境还要调用 App Store Server API 复核
        switch transaction.productType {
        case .autoRenewable:
            // 订阅必须有过期时间。拿不到就不解锁，绝不退化成 .distantFuture，
            // 否则一次异常就会变成永久会员。
            if let expiry = transaction.expirationDate {
                Membership.shared.markPlus(until: expiry)
            }
        case .nonConsumable:
            // 本产品不卖一次性买断商品，忽略
            break
        default:
            break
        }

        await transaction.finish()
    }

    /// 启动时与回前台时调用，校正本地状态。
    ///
    /// 关键：**不能**因为 `currentEntitlements` 暂时为空就立刻撤销权益。
    /// 沙盒 / TestFlight / 弱网下它可能短暂返回空，
    /// 直接 revoke 会让刚付款的用户看到"没买成功"。
    func refreshEntitlement() async {
        var best: Date?

        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result else { continue }
            guard transaction.revocationDate == nil else { continue }

            // 只认自动续期订阅（本产品唯一的商品类型）
            guard transaction.productType == .autoRenewable,
                  let expiry = transaction.expirationDate else { continue }

            if expiry > (best ?? .distantPast) { best = expiry }
        }

        if let best, best > Date() {
            Membership.shared.markPlus(until: best)
        } else if let cached = Membership.shared.expiry, cached > Date() {
            // 本地缓存还在有效期内，服务端暂时没返回 -> 保持不动，下次再校验
            return
        } else {
            Membership.shared.revoke()
        }
    }
}
