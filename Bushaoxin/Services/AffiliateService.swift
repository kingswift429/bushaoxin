import Foundation

/// P2 阶段的平替返利。
///
/// 为什么这条变现路径与产品逻辑自洽：
///   产品里本来就有「替代方案」字段。用户被驳回后，最自然的下一步就是
///   "那有没有更便宜的？" —— 在这个位置推荐平替，用户不会觉得被打扰。
///
/// 合规红线（必须遵守，否则构成隐性广告）：
///   1. 必须显著标注「本页含推广链接，成交后我们可能获得佣金」
///   2. 不能只推有佣金的商品而隐藏更好更便宜的选项
///   3. 绝不为了佣金推荐更贵的商品 —— 一旦被发现，社区信任瞬间崩塌
enum AffiliateService {

    struct Alternative: Identifiable {
        let id = UUID()
        let title: String
        /// 价格（同币种，随原申请）
        let price: Decimal
        let currencyCode: String
        let merchant: String
        /// 落地页
        let url: URL
        /// 是否带推广参数（用于合规展示与统计）
        let isAffiliate: Bool
    }

    /// 是否对用户展示返利模块。
    ///
    /// 默认关闭。理由：P2 之前没有接入联盟资质，
    /// 且没有足量数据支撑"这个推荐对用户真的有用"。
    /// 打开前请确认已在页面上展示了 affiliateDisclosure。
    static var isEnabled: Bool {
        false
    }

    /// 给跳转链接挂上推广参数。
    ///
    /// 各平台参数名不同：
    ///   - 淘宝联盟：union_id / pid
    ///   - 京东联盟：unionId / positionId
    ///   - 拼多多：pdd_user_id
    /// 这里只做参数注入的通用实现，真实接入需替换为各联盟 SDK 的签名链接。
    static func makeAffiliateURL(base: URL, source: String = "bushaoxin") -> URL {
        guard var comps = URLComponents(url: base, resolvingAgainstBaseURL: false) else {
            return base
        }
        var items = comps.queryItems ?? []
        items.append(URLQueryItem(name: "utm_source", value: source))
        items.append(URLQueryItem(name: "utm_medium", value: "affiliate"))
        comps.queryItems = items
        return comps.url ?? base
    }

    /// 从审批理由里粗提取"平替"线索。
    ///
    /// 不直接生成商品推荐——那是编造内容，会伤害信任。
    /// 只把网友真正提到过的关键词呈现出来，并说明来自哪条理由。
    static func extractMentions(from comments: [String]) -> [String] {
        let markers = ["平替", "更便宜", "搜一下", "去看", "测评", "替代",
                       "cheaper", "alternative", "review", "代わり", "대안"]
        return comments
            .filter { c in markers.contains { c.localizedCaseInsensitiveContains($0) } }
            .prefix(3)
            .map { $0 }
    }
}
