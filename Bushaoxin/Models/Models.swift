import Foundation
import SwiftData

// MARK: - 消费申请

@Model
final class Application {
    @Attribute(.unique) var id: UUID
    var goods: String
    /// 金额用 Decimal 存储（Double 累积误差在账本场景不可接受）
    var price: Decimal
    /// ISO 4217 币种代码，如 CNY / USD / HKD / JPY / KRW
    var currencyCode: String
    /// 分类的稳定 key（dining/fashion/...），显示时再本地化
    var categoryKey: String
    var reason: String
    var alternative: String

    /// plaza = 陌生人广场；group = 审批群；private_ = 仅自己
    var channel: String
    var groupName: String?

    /// voting / passed / rejected
    var status: String

    /// 我的判断：nil = 还没投；"pass" / "reject"
    var myVerdict: String?

    /// 冷静期截止时间（原产品只有 Slogan，我们做成真机制）
    var cooldownUntil: Date

    /// 到达冷静期后用户是否确认「还是要买」
    var confirmedAfterCooldown: Bool

    var createdAt: Date

    /// 投票计数（先在本地聚合，接 Supabase 后由服务端回填）
    var passCount: Int
    var rejectCount: Int

    /// 截图导入时保留的原始文本，便于二次校正
    var sourceText: String?

    /// 是否已围观过（围观不是判断，不写 myVerdict，避免污染统计）
    var hasViewed: Bool

    /// 被举报后本地立即隐藏（不等服务端审核）
    var isHidden: Bool = false

    /// 作者标识。拉黑按它过滤；也是"匿名但可追溯"的最小代价方案。
    var authorKey: String = "self"

    /// 我做出判断的时间（不是申请创建时间）。
    /// 连续克制天数必须用它——用户今天驳回上周创建的单，该算今天。
    var verdictAt: Date?

    init(
        goods: String,
        price: Decimal,
        currencyCode: String = Locale.current.currency?.identifier ?? "CNY",
        categoryKey: String = SpendCategory.other.rawValue,
        reason: String,
        alternative: String = "",
        channel: String = "plaza",
        groupName: String? = nil,
        cooldownHours: Double = 24
    ) {
        self.id = UUID()
        self.goods = goods
        self.price = price
        self.currencyCode = currencyCode
        self.categoryKey = categoryKey
        self.reason = reason
        self.alternative = alternative
        self.channel = channel
        self.groupName = groupName
        self.status = "voting"
        self.myVerdict = nil
        self.cooldownUntil = Date().addingTimeInterval(cooldownHours * 3600)
        self.confirmedAfterCooldown = false
        self.createdAt = Date()
        self.passCount = 0
        self.rejectCount = 0
        self.sourceText = nil
        self.hasViewed = false
        self.isHidden = false
        self.authorKey = "self"
        self.verdictAt = nil
    }
}

// MARK: - 审批票

@Model
final class Vote {
    @Attribute(.unique) var id: UUID
    var applicationID: UUID
    /// pass / reject
    var verdict: String
    /// 必填 —— 产品的灵魂字段
    var comment: String
    var flowers: Int
    var createdAt: Date
    /// 是否为模拟网友（本地体验用）
    var isSimulated: Bool

    init(applicationID: UUID, verdict: String, comment: String, isSimulated: Bool = false) {
        self.id = UUID()
        self.applicationID = applicationID
        self.verdict = verdict
        self.comment = comment
        self.flowers = 0
        self.createdAt = Date()
        self.isSimulated = isSimulated
    }
}

// MARK: - 派生统计

extension Application {
    var totalVotes: Int { passCount + rejectCount }

    var passRatio: Double {
        totalVotes == 0 ? 0 : Double(passCount) / Double(totalVotes)
    }

    var isCoolingDown: Bool {
        status == "voting" && Date() < cooldownUntil
    }

    var cooldownRemaining: TimeInterval {
        max(0, cooldownUntil.timeIntervalSinceNow)
    }

    /// 我是否已经表过态（通过 / 驳回 / 围观都算）
    var hasActed: Bool { myVerdict != nil }

    /// 我是否真的投了票（围观不算）
    var castRealVote: Bool { myVerdict == "pass" || myVerdict == "reject" }

    /// 这笔消费是不是「我自己」发起的。
    /// 种子内容和别人的申请 authorKey 不是 "self"。
    var isMine: Bool { authorKey == "self" }

    /// 真正「为我省下钱」的条目。
    ///
    /// 这是个容易写错的口径，必须只认两种情况：
    ///   1. 我自己的单，经过网友审批被我（或最终结果）驳回
    ///   2. 我自己的单，冷静期结束后我主动放弃
    ///
    /// **不能**把「我驳回别人的申请」算进来 ——
    /// 那省的是别人的钱，记到自己账上是虚报。
    var savedForMe: Bool {
        isMine && (myVerdict == "reject" || (status == "rejected" && myVerdict == nil))
    }

    /// 已本地化的金额文本
    var priceText: String { MoneyFormatter.string(price, code: currencyCode) }

    /// 已本地化的分类名
    var categoryName: String {
        SpendCategory(key: categoryKey)?.localizedName ?? categoryKey
    }
}

// MARK: - 判断枚举

/// 我的态度。杜绝字符串散落导致的漏判。
enum MyVerdict: String {
    case pass
    case reject
    case skip
}

extension Application {
    var verdictEnum: MyVerdict? {
        guard let myVerdict else { return nil }
        return MyVerdict(rawValue: myVerdict)
    }
}

// MARK: - 分类

/// rawValue 是稳定 key，**存库用 key、显示用 localizedName**。
/// 这样切换语言时历史数据不会变成乱码字符串。
enum SpendCategory: String, CaseIterable, Identifiable {
    case dining
    case fashion
    case digital
    case game
    case sports
    case other

    var id: String { rawValue }

    init?(key: String) {
        self.init(rawValue: key)
    }

    var localizedName: String {
        String(localized: LocalizedStringResource(stringLiteral: nameKey))
    }

    private var nameKey: String {
        switch self {
        case .dining: return "category.dining"
        case .fashion: return "category.fashion"
        case .digital: return "category.digital"
        case .game: return "category.game"
        case .sports: return "category.sports"
        case .other: return "category.other"
        }
    }

    var icon: String {
        switch self {
        case .dining: return "cup.and.saucer.fill"
        case .fashion: return "tshirt.fill"
        case .digital: return "iphone"
        case .game: return "gamecontroller.fill"
        case .sports: return "figure.run"
        case .other: return "shippingbox.fill"
        }
    }
}

// MARK: - 举报（Apple UGC 硬性要求）

/// 举报记录。
///
/// App Store 审核指南 1.2 要求 UGC 产品必须具备：过滤、举报、屏蔽、客服联系。
/// 缺任何一项都会被拒。这是上架的阻塞项，不是可选项。
@Model
final class Report {
    @Attribute(.unique) var id: UUID
    /// 被举报内容的 id（Application.id）
    var targetID: UUID
    /// 举报原因 key（spam/abuse/adult/fraud/other）
    var reasonKey: String
    var detail: String
    var createdAt: Date
    /// nil = 还在本地待提交
    var syncedAt: Date?

    init(targetID: UUID, reasonKey: String, detail: String = "") {
        self.id = UUID()
        self.targetID = targetID
        self.reasonKey = reasonKey
        self.detail = detail
        self.createdAt = Date()
        self.syncedAt = nil
    }
}

/// 举报原因。存 key、显示时本地化。
enum ReportReason: String, CaseIterable, Identifiable {
    case spam
    case fraud
    case abuse
    case adult
    case other

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .spam:  return L.reportSpam
        case .fraud: return L.reportFraud
        case .abuse: return L.reportAbuse
        case .adult: return L.reportAdult
        case .other: return L.reportOther
        }
    }
}

// MARK: - 拉黑

/// 被拉黑的作者。
///
/// 本地优先：即使没联网也要能立刻屏蔽，不能等服务器。
/// 联网后再同步到 blocked_authors 表。
@Model
final class BlockedAuthor {
    @Attribute(.unique) var authorKey: String
    var displayName: String
    var createdAt: Date

    init(authorKey: String, displayName: String) {
        self.authorKey = authorKey
        self.displayName = displayName
        self.createdAt = Date()
    }
}
