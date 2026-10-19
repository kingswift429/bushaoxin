import Foundation
import SwiftData

/// 举报上报与拉黑管理。
///
/// 设计要点：**本地优先**。
/// 用户点举报/拉黑后必须立刻生效，不能等网络——
/// 如果因为离线就让人继续看到骚扰内容，那是产品事故，也是审核会挑的问题。
@MainActor
final class ReportService {
    static let shared = ReportService()

    private init() {}

    /// 上报所有未同步的举报。
    ///
    /// 失败不清除记录，下次启动或下次举报时重试 ——
    /// 举报数据丢失比上报失败严重得多。
    /// 限制每次最多 20 条，避免离线久了之后一次性发几百个请求。
    func flush(context: ModelContext) async {
        guard SupabaseConfig.isConfigured else { return }

        let pending: [Report]
        do {
            // 刻意不在 #Predicate 里写 `$0.syncedAt == nil`：
            // SwiftData 的 #Predicate 对**可选属性的 nil 比较**支持不完整，
            // 在部分 iOS 17 版本上会编译失败或运行时抛错。
            // 举报表数据量很小（本地待同步通常个位数），全量取回再内存过滤最稳。
            let all = try context.fetch(FetchDescriptor<Report>())
            pending = Array(all.filter { $0.syncedAt == nil }.prefix(20))
        } catch {
            return
        }
        guard !pending.isEmpty else { return }

        for report in pending {
            if await upload(report) {
                report.syncedAt = Date()
            }
        }
        try? context.save()
    }

    private func upload(_ report: Report) async -> Bool {
        let base = SupabaseConfig.url.absoluteString
            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard let url = URL(string: "\(base)/rest/v1/reports") else {
            return false
        }

        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue(SupabaseConfig.anonKey, forHTTPHeaderField: "apikey")
        // return=minimal 不返回数据体；ignore-duplicates 让重复举报撞唯一索引时静默成功
        req.setValue("return=minimal, resolution=ignore-duplicates",
                     forHTTPHeaderField: "Prefer")

        if let token = await SupabaseClient.shared.currentAccessToken() {
            req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        } else {
            req.setValue("Bearer \(SupabaseConfig.anonKey)", forHTTPHeaderField: "Authorization")
        }

        let body: [String: Any] = [
            "target_id": report.targetID.uuidString,
            "reason": report.reasonKey,
            "detail": report.detail
        ]
        guard let data = try? JSONSerialization.data(withJSONObject: body) else {
            return false
        }
        req.httpBody = data

        do {
            let (respData, response) = try await URLSession.shared.data(for: req)
            guard let http = response as? HTTPURLResponse else { return false }
            if !(200...299).contains(http.statusCode) {
                // 保留错误体，排查 RLS 配置问题时能看到真实原因
                let msg = String(data: respData, encoding: .utf8) ?? ""
                print("[ReportService] 上报失败 \(http.statusCode): \(msg)")
                return false
            }
            return true
        } catch {
            print("[ReportService] 上报异常: \(error.localizedDescription)")
            return false
        }
    }

    // MARK: 拉黑

    /// 拉黑作者，并立刻把该作者的本地内容全部隐藏。
    func block(authorKey: String, displayName: String, context: ModelContext) {
        // 防呆：authorKey == "self" 表示自己的内容。
        // 一旦拉黑 "self"，会把用户自己发的所有申请一起隐藏，等于自毁数据。
        guard authorKey != "self" else { return }

        let existing = try? context.fetch(
            FetchDescriptor<BlockedAuthor>(predicate: #Predicate { $0.authorKey == authorKey })
        )
        if existing?.isEmpty ?? true {
            context.insert(BlockedAuthor(authorKey: authorKey, displayName: displayName))
        }

        // 本地内容立刻隐藏
        if let apps = try? context.fetch(FetchDescriptor<Application>()) {
            for app in apps where app.authorKey == authorKey {
                app.isHidden = true
            }
        }

        try? context.save()
        Haptics.success()
    }

    func unblock(authorKey: String, context: ModelContext) {
        if let list = try? context.fetch(
            FetchDescriptor<BlockedAuthor>(predicate: #Predicate { $0.authorKey == authorKey })
        ) {
            for b in list { context.delete(b) }
        }
        // 解除拉黑后恢复该作者内容
        if let apps = try? context.fetch(FetchDescriptor<Application>()) {
            for app in apps where app.authorKey == authorKey {
                app.isHidden = false
            }
        }
        try? context.save()
    }

    /// 当前所有被拉黑的 authorKey，供列表过滤
    func blockedKeys(context: ModelContext) -> Set<String> {
        let list = (try? context.fetch(FetchDescriptor<BlockedAuthor>())) ?? []
        return Set(list.map(\.authorKey))
    }
}
