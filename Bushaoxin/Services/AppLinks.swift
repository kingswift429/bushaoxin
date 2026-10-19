import Foundation

/// 外部链接与联系方式的唯一来源。
///
/// 为什么集中管理：
/// 1. 上架前必须把占位域名换掉，分散在三处容易漏；
/// 2. Apple 审核会真的点开隐私政策和用户协议链接 ——
///    如果返回 404，直接以「隐私政策不可访问」被拒。
///
/// 当前托管在 GitHub Pages：
///   仓库 bushiaoxin 的根目录（main 分支）
///   → https://kingswift429.github.io/bushaoxin/privacy.html
///   → https://kingswift429.github.io/bushaoxin/terms.html
enum AppLinks {

    // MARK: - 对外地址

    /// 客服邮箱。必须是真实可收信的地址，审核可能会发邮件验证。
    static let supportEmail = "support@bushaoxin.app"

    /// 隐私政策。**必须真实可访问**，不能是 404。
    static let privacyPolicy = "https://kingswift429.github.io/bushaoxin/privacy.html"

    /// 用户协议。
    static let terms = "https://kingswift429.github.io/bushaoxin/terms.html"

    /// 项目主页（「关于」页展示）
    static let homepage = "https://github.com/kingswift429/bushaoxin"

    // MARK: - 派生

    /// 客服邮件链接（已做百分号编码，避免 @ 和中文主题干扰解析）
    static var supportMailURL: URL? {
        var comps = URLComponents()
        comps.scheme = "mailto"
        comps.path = supportEmail
        return comps.url
    }

    static var privacyURL: URL? { URL(string: privacyPolicy) }
    static var termsURL: URL? { URL(string: terms) }

    /// 是否还在用占位配置。
    /// 用于在设置页显示一行提示，避免自己忘记替换就提交审核。
    static var isUsingPlaceholder: Bool {
        privacyPolicy.contains("example.com") || supportEmail.contains("example.com")
    }

    /// 隐私政策是否真的能打开（需要网络，异步）。
    /// 上架前调用一次，能提前发现 404，而不是等审核被拒。
    static func verifyPrivacyPolicyReachable() async -> Bool {
        guard let url = privacyURL else { return false }
        var req = URLRequest(url: url)
        req.httpMethod = "HEAD"
        req.timeoutInterval = 10
        do {
            let (_, resp) = try await URLSession.shared.data(for: req)
            guard let http = resp as? HTTPURLResponse else { return false }
            return (200..<400).contains(http.statusCode)
        } catch {
            return false
        }
    }
}
