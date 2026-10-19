import Foundation
import SwiftData

/// 模拟网友审批。
///
/// 作用：在没有后端或早期无人使用的情况下，"广场"依然是活的，
/// 用户第一次打开就能体验到完整闭环 —— 这是冷启动的关键。
///
/// 接入 Supabase 后，它退居为「演示模式」与「内容预热」。
enum CrowdSimulator {

    /// 根据金额与理由质量，给一个"通过概率"
    private static func passProbability(for app: Application) -> Double {
        var p = 0.42
        let price = NSDecimalNumber(decimal: app.price).doubleValue

        // 小额更容易被放行（阈值不写死币种，用相对量级判断）
        // JPY/KRW 数值天然大 10~100 倍，用当地货币的"日常消费"量级换算
        let scale = magnitudeScale(for: app.currencyCode)
        let normalized = price / scale

        if normalized <= 30 { p += 0.22 }
        else if normalized <= 100 { p += 0.10 }
        else if normalized >= 1000 { p -= 0.18 }

        // 有替代方案说明认真想过了，评审更愿意放行
        if !app.alternative.trimmingCharacters(in: .whitespaces).isEmpty { p += 0.10 }
        // 理由够长说明是真需求而非随手一买
        if app.reason.count >= 20 { p += 0.10 }
        if app.reason.count <= 6 { p -= 0.12 }
        return min(max(p, 0.08), 0.9)
    }

    /// 各币种相对人民币的量级倍数，用于把"多少钱算小钱"换算到同一尺度
    private static func magnitudeScale(for code: String) -> Double {
        switch code.uppercased() {
        case "JPY": return 20      // 1 CNY ≈ 20 JPY
        case "KRW": return 190     // 1 CNY ≈ 190 KRW
        case "VND": return 3500
        case "IDR": return 2200
        default: return 1
        }
    }

    /// 对一条申请生成若干模拟票。
    /// 语料为空时返回空数组，绝不用 `!` 强解包——那会在语料被改空时直接崩。
    static func simulate(_ app: Application, count: Int) -> [(verdict: String, comment: String)] {
        let corpus = CrowdCorpus.current()
        let p = passProbability(for: app)
        return (0..<count).compactMap { _ in
            let pass = Double.random(in: 0...1) < p
            let pool = pass ? corpus.pass : corpus.reject
            guard let comment = pool.randomElement() else { return nil }
            return (pass ? "pass" : "reject", comment)
        }
    }

    /// 把模拟票写入数据库并聚合计数
    @MainActor
    static func apply(to app: Application, in context: ModelContext, count: Int = 3) {
        for vote in simulate(app, count: count) {
            let v = Vote(
                applicationID: app.id,
                verdict: vote.verdict,
                comment: vote.comment,
                isSimulated: true
            )
            context.insert(v)
            if vote.verdict == "pass" { app.passCount += 1 } else { app.rejectCount += 1 }
        }
        try? context.save()
    }
}
