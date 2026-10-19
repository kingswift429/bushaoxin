import Foundation

// MARK: - 配置

/// Supabase 配置。把 YOUR_xxx 换成你在 supabase.com 建的项目值，
/// 并确认 Schema 已按 docs/supabase_schema.sql 建好。
enum SupabaseConfig {
    static let url = URL(string: "https://YOUR_PROJECT_REF.supabase.co")!
    /// 只用 anon key，绝不要把 service_role key 放进客户端
    static let anonKey = "YOUR_ANON_PUBLIC_KEY"

    static var isConfigured: Bool {
        guard !anonKey.hasPrefix("YOUR_") else { return false }
        // 不用 url.host! —— URL 解析异常时 host 为 nil 会直接崩溃。
        // 配置缺失只应导致"后端不可用"，绝不该让 App 起不来。
        guard let host = url.host else { return false }
        return !host.contains("YOUR_PROJECT_REF")
    }
}

// MARK: - 错误

enum APIError: LocalizedError {
    case notConfigured
    case http(Int, String)
    case decoding(String)

    var errorDescription: String? {
        switch self {
        case .notConfigured:
            return "还没配置 Supabase，当前使用本地模式"
        case let .http(code, body):
            return "请求失败(\(code))：\(body.prefix(120))"
        case let .decoding(msg):
            return "数据解析失败：\(msg)"
        }
    }
}

// MARK: - DTO

struct ApplicationDTO: Codable {
    var id: UUID
    var author_id: UUID?
    var goods: String
    var price: Double
    var category: String
    var reason: String
    var alternative: String
    var channel: String
    var status: String
    var passCount: Int
    var rejectCount: Int
    var createdAt: String

    enum CodingKeys: String, CodingKey {
        case id, author_id, goods, price, category, reason, alternative, channel, status
        case passCount = "pass_count"
        case rejectCount = "reject_count"
        case createdAt = "created_at"
    }
}

struct VoteDTO: Codable {
    var id: UUID
    var applicationID: UUID
    var voter_id: UUID?
    var verdict: String
    var comment: String
    var flowers: Int
    var createdAt: String

    enum CodingKeys: String, CodingKey {
        case id, verdict, comment, flowers, voter_id
        case applicationID = "application_id"
        case createdAt = "created_at"
    }
}

// MARK: - 客户端

/// 极简 PostgREST 封装：不引入第三方 SDK，避免依赖地狱，方便你审每一行代码。
actor SupabaseClient {
    static let shared = SupabaseClient()

    private let session: URLSession
    private let decoder: JSONDecoder

    /// 匿名登录后拿到的用户 id（对应 auth.users.id）
    private(set) var currentUserID: UUID?
    private var accessToken: String?

    private static let tokenKey = "sb_anon_token"
    private static let uidKey = "sb_anon_uid"

    init(session: URLSession = .shared) {
        self.session = session
        self.decoder = JSONDecoder()
        if let s = UserDefaults.standard.string(forKey: Self.uidKey) {
            self.currentUserID = UUID(uuidString: s)
        }
        self.accessToken = UserDefaults.standard.string(forKey: Self.tokenKey)
    }

    // MARK: 匿名登录

    /// 供其它服务（如 ReportService）复用已登录的 token。
    /// 未登录时返回 nil，调用方应回退到 anonKey。
    func currentAccessToken() -> String? { accessToken }

    /// Supabase Anonymous Sign-in：无需手机号/微信，用户无感知，直接可用。
    /// 需要在 Dashboard → Authentication → Providers 里打开 Anonymous。
    func signInAnonymouslyIfNeeded() async throws {
        guard SupabaseConfig.isConfigured else { throw APIError.notConfigured }
        if currentUserID != nil, accessToken != nil { return }

        let base = SupabaseConfig.url.absoluteString
            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard var comps = URLComponents(string: "\(base)/auth/v1/signup") else { return }

        // 关键：关闭邮箱确认，匿名登录直接返回 session
        comps.queryItems = [.init(name: "gotrue_meta_security", value: "{}")]

        var req = URLRequest(url: comps.url!)
        req.httpMethod = "POST"
        req.setValue(SupabaseConfig.anonKey, forHTTPHeaderField: "apikey")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        // 不带 email/password 即为匿名用户
        req.httpBody = Data("{}".utf8)

        let (data, resp) = try await session.data(for: req)
        guard let http = resp as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            let body = String(data: data, encoding: .utf8) ?? ""
            throw APIError.http((resp as? HTTPURLResponse)?.statusCode ?? -1, body)
        }

        struct AuthResp: Decodable {
            struct User: Decodable { let id: UUID }
            let access_token: String?
            let user: User?
        }
        let auth = try decoder.decode(AuthResp.self, from: data)

        // 拿不到 token 必须报错。
        // 否则函数静默返回，后续所有写请求都会以 anonKey 身份发出，
        // RLS 里 auth.uid() 为 null -> 全部 401，而 UI 上什么都看不到。
        guard let token = auth.access_token, !token.isEmpty else {
            throw APIError.http(-1,
                "匿名登录未返回 access_token。请确认 Supabase 已开启 Authentication → Providers → Anonymous。")
        }
        accessToken = token
        UserDefaults.standard.set(token, forKey: Self.tokenKey)

        if let uid = auth.user?.id {
            currentUserID = uid
            UserDefaults.standard.set(uid.uuidString, forKey: Self.uidKey)
        }
    }

    private func request(
        path: String,
        method: String = "GET",
        query: [URLQueryItem] = [],
        body: Data? = nil,
        prefer: String? = nil
    ) async throws -> Data {
        guard SupabaseConfig.isConfigured else { throw APIError.notConfigured }

        // 手拼 URL：appendingPathComponent 会把 "/" 转义成 %2F，导致 PostgREST 404
        let base = SupabaseConfig.url.absoluteString
            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard var comps = URLComponents(string: "\(base)/rest/v1/\(path)") else {
            throw APIError.http(-1, "URL 拼接失败")
        }
        if !query.isEmpty { comps.queryItems = query }

        var req = URLRequest(url: comps.url!)
        req.httpMethod = method
        req.setValue(SupabaseConfig.anonKey, forHTTPHeaderField: "apikey")
        // 有登录态时用用户 token，RLS 才能认出 auth.uid()
        req.setValue("Bearer \(accessToken ?? SupabaseConfig.anonKey)",
                     forHTTPHeaderField: "Authorization")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let prefer { req.setValue(prefer, forHTTPHeaderField: "Prefer") }
        req.httpBody = body

        let (data, resp) = try await session.data(for: req)
        guard let http = resp as? HTTPURLResponse else {
            throw APIError.http(-1, "无响应")
        }
        guard (200..<300).contains(http.statusCode) else {
            throw APIError.http(http.statusCode, String(data: data, encoding: .utf8) ?? "")
        }
        return data
    }

    // MARK: 广场

    func fetchPlaza(limit: Int = 30) async throws -> [ApplicationDTO] {
        let data = try await request(
            path: "applications",
            query: [
                .init(name: "select", value: "*"),
                .init(name: "channel", value: "eq.plaza"),
                .init(name: "status", value: "eq.voting"),
                .init(name: "order", value: "created_at.desc"),
                .init(name: "limit", value: "\(limit)")
            ]
        )
        do { return try decoder.decode([ApplicationDTO].self, from: data) }
        catch { throw APIError.decoding(error.localizedDescription) }
    }

    // MARK: 提交申请

    func submit(_ dto: ApplicationDTO) async throws {
        let enc = JSONEncoder()
        let body = try enc.encode([dto])
        _ = try await request(
            path: "applications",
            method: "POST",
            body: body,
            prefer: "return=minimal"
        )
    }

    // MARK: 投票

    func castVote(_ dto: VoteDTO) async throws {
        let enc = JSONEncoder()
        let body = try enc.encode([dto])
        _ = try await request(
            path: "votes",
            method: "POST",
            body: body,
            prefer: "return=minimal"
        )
    }

    func fetchVotes(applicationID: UUID) async throws -> [VoteDTO] {
        let data = try await request(
            path: "votes",
            query: [
                .init(name: "select", value: "*"),
                .init(name: "application_id", value: "eq.\(applicationID.uuidString)"),
                .init(name: "order", value: "created_at.desc")
            ]
        )
        do { return try decoder.decode([VoteDTO].self, from: data) }
        catch { throw APIError.decoding(error.localizedDescription) }
    }
}
