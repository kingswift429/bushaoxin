import Foundation
import Observation

// MARK: - 会员权益的单一真相源

/// 免费/会员的能力矩阵。
///
/// 把「谁能用什么」集中在一处，而不是散落在各个视图里写 `if isPro`。
/// 好处：改定价策略时只动这一个文件，不会漏改。
enum Entitlement {

    // MARK: 免费额度

    /// 免费用户每月截图识别次数
    static let freeOCRPerMonth = 10
    /// 免费用户可以创建的审批群数量
    static let freeGroupLimit = 1
    /// 免费审批群人数上限
    static let freeGroupMemberLimit = 10
    /// 会员审批群人数上限
    static let plusGroupMemberLimit = 500

    // MARK: 冷静期

    /// 免费用户固定的冷静期档位（小时）
    static let freeCooldownHours: Double = 24
    /// 会员可选的冷静期档位（小时）
    static let plusCooldownOptions: [Double] = [2, 12, 24, 72]

    /// 免费用户也能用 24 小时这一档，但其它档位锁定
    static func allowedCooldownOptions(isPlus: Bool) -> [Double] {
        isPlus ? plusCooldownOptions : [freeCooldownHours]
    }

    // MARK: 广告

    /// 我们**不投放广告**。
    ///
    /// 原作者的判断在商业上也成立：产品叙事是"帮你少花钱"，
    /// 广告的逻辑是"让你多花钱"，两者直接冲突。
    /// 保留这个常量是为了让团队在未来有人提"接个开屏广告吧"时，有据可依。
    static let showsAds = false
}

// MARK: - 套餐

enum Plan: String, CaseIterable, Identifiable {
    case monthly
    case yearly

    var id: String { rawValue }

    /// StoreKit 商品 ID —— 需在 App Store Connect 建好同名商品
    var productID: String {
        switch self {
        case .monthly: return "com.yourteam.bushaoxin.plus.monthly"
        case .yearly:  return "com.yourteam.bushaoxin.plus.yearly"
        }
    }

    /// 展示用价格（实际应从 StoreKit 拉取本地化价格）
    var displayPrice: String {
        switch self {
        case .monthly: return "¥18"
        case .yearly:  return "¥128"
        }
    }

    var caption: String {
        switch self {
        case .monthly: return L.planMonthly
        case .yearly:  return L.planYearly
        }
    }

    /// 年费相对月费的折算
    var savingsPercent: Int {
        switch self {
        case .monthly: return 0
        case .yearly:  return 41
        }
    }
}

// MARK: - 付费触发点

/// 所有会引导到付费墙的场景。
///
/// 集中定义的目的：能统计"哪个入口真的能转化"，
/// 而不是盲目在所有地方弹窗——这个产品的用户对推销极其敏感。
enum PaywallTrigger: String, Identifiable {
    case ocrQuotaExhausted   = "ocr_quota_exhausted"
    case cooldownOptionLocked = "cooldown_option_locked"
    case groupLimitReached   = "group_limit_reached"
    case reportDetail        = "report_detail"
    case milestoneSaved      = "milestone_saved"

    var id: String { rawValue }

    var headline: String {
        switch self {
        case .ocrQuotaExhausted:
            return L.paywallOCRHeadline
        case .cooldownOptionLocked:
            return L.paywallCooldownHeadline
        case .groupLimitReached:
            return L.paywallGroupHeadline
        case .reportDetail:
            return L.paywallReportHeadline
        case .milestoneSaved:
            return L.paywallMilestoneHeadline
        }
    }

    var detail: String {
        switch self {
        case .ocrQuotaExhausted:
            return L.paywallOCRDetail
        case .cooldownOptionLocked:
            return L.paywallCooldownDetail
        case .groupLimitReached:
            return L.paywallGroupDetail
        case .reportDetail:
            return L.paywallReportDetail
        case .milestoneSaved:
            return L.paywallMilestoneDetail
        }
    }
}

// MARK: - 本地权益状态

/// 当前用户的会员状态。
///
/// 生产环境必须由服务端（App Store Server API）
/// 校验订阅状态，**不能只信客户端**——否则越狱设备可直接解锁。
@MainActor
@Observable
final class Membership {
    static let shared = Membership()

    private let key = "bushaoxin.plus.expiry"

    /// 仅作 UI 快速判断，真实权益以服务端为准
    private(set) var isPlus: Bool = false
    private(set) var expiry: Date?

    /// 本月已用截图识别次数（按 "yyyy-MM" 分桶）
    private(set) var ocrUsedThisMonth: Int = 0
    private let ocrKey = "bushaoxin.ocr.usage"

    init() {
        // 读取缓存（离线时也能正确展示已付费状态）
        if let d = UserDefaults.standard.object(forKey: key) as? Date, d > Date() {
            isPlus = true
            expiry = d
        }
        loadOCRUsage()
    }

    // MARK: 截图识别额度

    private func currentMonthTag() -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM"
        return f.string(from: Date())
    }

    private func loadOCRUsage() {
        let dict = UserDefaults.standard.dictionary(forKey: ocrKey) as? [String: Int] ?? [:]
        ocrUsedThisMonth = dict[currentMonthTag()] ?? 0
    }

    /// nil 表示无限额度（会员）。
    /// 不要用 Int.max —— 一旦有人把它直接拼进 Text，界面上会出现一串天文数字。
    var ocrRemaining: Int? {
        isPlus ? nil : max(0, Entitlement.freeOCRPerMonth - ocrUsedThisMonth)
    }

    var canUseOCR: Bool { ocrRemaining.map { $0 > 0 } ?? true }

    func consumeOCR() {
        guard !isPlus else { return }
        var dict = UserDefaults.standard.dictionary(forKey: ocrKey) as? [String: Int] ?? [:]
        let tag = currentMonthTag()
        dict[tag] = (dict[tag] ?? 0) + 1
        UserDefaults.standard.set(dict, forKey: ocrKey)
        ocrUsedThisMonth = dict[tag] ?? 0
    }

    // MARK: 状态更新（由 PurchaseService 调用）

    func markPlus(until date: Date) {
        isPlus = date > Date()
        expiry = date
        UserDefaults.standard.set(date, forKey: key)
    }

    func revoke() {
        isPlus = false
        expiry = nil
        UserDefaults.standard.removeObject(forKey: key)
    }
}
