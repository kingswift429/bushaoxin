import Foundation
// Vision 的 VNImageRequestHandler / VNRecognizeTextRequest 至今没有标注 Sendable，
// 在 Swift 6 的严格并发检查下会持续报警告。
// @preconcurrency 表示"这个模块里的类型我承诺妥善处理并发"，正好用于这种情况。
@preconcurrency import Vision
import UIKit
import CoreImage

/// 从购物截图/照片中抽取「商品名 + 价格」
///
/// 这是小程序做不了的原生优势：本地离线、无上传、无服务端成本。
enum ReceiptParser {

    struct Parsed {
        var goods: String?
        var price: Double?
        var rawText: String
        /// 0~1，用于在 UI 上提示"识别置信度低，请核对"
        var confidence: Double
        /// 从符号推断出的币种（nil 表示用系统默认）
        var currencyCode: String?
    }

    // MARK: - 主入口

    static func parse(image: UIImage) async -> Parsed? {
        guard let text = await recognizeText(from: image) else { return nil }
        return parse(text: text)
    }

    // MARK: - OCR

    static func recognizeText(from image: UIImage) async -> String? {
        guard let cg = image.cgImage else { return nil }

        // 同一 continuation 只能 resume 一次，否则运行时崩溃。
        // Vision 出错时 completion 也可能被调用，用锁保证幂等。
        final class OnceBox: @unchecked Sendable {
            private let lock = NSLock()
            private var done = false
            func tryComplete() -> Bool {
                lock.lock(); defer { lock.unlock() }
                if done { return false }
                done = true
                return true
            }
        }
        let once = OnceBox()

        return await withCheckedContinuation { (cont: CheckedContinuation<String?, Never>) in
            // 关键：VNImageRequestHandler 和 VNRecognizeTextRequest 都不是 Sendable，
            // 在外层创建再传进 DispatchQueue.async 的 @Sendable 闭包会被 Swift 6 判为
            // "capture of non-sendable type in a @Sendable closure"。
            // 改成**在闭包内部创建**，对象不跨并发域，警告消失且语义不变
            // （它们本来也只在这一次识别里用一次）。
            DispatchQueue.global(qos: .userInitiated).async {
                let request = VNRecognizeTextRequest { req, _ in
                    let lines = (req.results as? [VNRecognizedTextObservation] ?? [])
                        .compactMap { $0.topCandidates(1).first?.string }
                    if once.tryComplete() {
                        cont.resume(returning: lines.joined(separator: "\n"))
                    }
                }
                request.recognitionLevel = .accurate
                // 中英混合，购物截图里同时有中文商品名和 "¥"/"RMB"
                request.recognitionLanguages = ["zh-Hans", "en-US"]
                request.usesLanguageCorrection = true

                let handler = VNImageRequestHandler(cgImage: cg, options: [:])
                do { try handler.perform([request]) }
                catch {
                    if once.tryComplete() { cont.resume(returning: nil) }
                }
            }
        }
    }

    // MARK: - 解析规则

    static func parse(text: String) -> Parsed {
        let rawLines = text
            .components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }

        // ---- 价格 ----
        // 覆盖主要市场的购物页写法：
        //   ¥15 / ￥1,299.00（中） $12.99（英） 580円 / 1,200円（日）
        //   ₩6,800 / 12,000원（韩） €9,99（欧式逗号小数）
        var candidates: [Double] = []
        let patterns: [String] = [
            #"[¥￥$£€₩]\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)"#,          // 符号在前
            #"([0-9][0-9,]*(?:\.[0-9]{1,2})?)\s*(?:元|円|원|won|yen|JPY|KRW)"#, // 符号在后
            #"(?i)(?:RMB|CNY|USD|EUR|GBP|HKD|TWD|MOP)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)"#
        ]
        for p in patterns {
            if let re = try? NSRegularExpression(pattern: p) {
                let ns = text as NSString
                re.enumerateMatches(in: text, range: NSRange(location: 0, length: ns.length)) { m, _, _ in
                    guard let m, m.numberOfRanges > 1,
                          let r = Range(m.range(at: 1), in: text) else { return }
                    // 去掉千分位逗号后再转数字
                    let raw = text[r].replacingOccurrences(of: ",", with: "")
                    if let v = Double(raw) { candidates.append(v) }
                }
            }
        }
        // 价格合理性过滤：0~10,000,000（韩元/日元/越南盾数值天然很大）
        let valid = candidates.filter { $0 > 0 && $0 < 10_000_000 }

        // 购物页通常同时显示「原价 ¥299」和「到手价 ¥199」。
        // 无脑取 max() 永远取到原价，会夸大会省下的金额 —— 与产品立场相反。
        // 所以：有优惠标记时取最小的（最可能是实付），否则取最大（页面上唯一/主价格）。
        let discountMarkers = ["到手", "实付", "券后", "优惠后", "应付", "合计",
                               "final", "total", "sale", "割引", "적용가"]
        let hasDiscount = discountMarkers.contains { text.localizedCaseInsensitiveContains($0) }
        let price = hasDiscount ? valid.min() : valid.max()

        // ---- 商品名 ----
        // 先剔除明确是营销/UI 的行，再在剩余行里挑最像商品名的一条
        let noiseWords = [
            // 中文
            "券", "包邮", "月销", "已售", "好评", "补贴",
            "¥", "￥", "元", "合计", "总计", "运费", "满减",
            "立即购买", "加入购物车", "限时", "秒杀", "拼单",
            // English
            "off", "coupon", "shipping", "sold", "reviews", "add to cart",
            "buy now", "free delivery", "%",
            // 日本語
            "円", "ポイント", "送料", "レビュー", "購入", "カート",
            // 한국어
            "원", "배송", "리뷰", "구매", "장바구니", "할인"
        ]
        let uiNoise = [
            "搜索", "返回", "客服", "购物车", "我的", "首页", "分类",
            "关注", "评价", "详情", "规格", "选择", "支付", "订单",
            "Search", "Back", "Help", "Cart", "Home", "Reviews", "Details",
            "検索", "戻る", "カート", "ホーム", "詳細",
            "검색", "뒤로", "장바구니", "홈", "상세"
        ]

        // 不是商品名的行
        func isNotGoods(_ line: String) -> Bool {
            if noiseWords.contains(where: { line.contains($0) }) { return true }
            if uiNoise.contains(where: { line.hasPrefix($0) }) { return true }
            // 纯数字/符号行
            let letters = line.filter { $0.isLetter }
            if letters.count < 2 { return true }
            // 注意：这里不要再卡 line.count < 4。
            // 中文里「耳機」「電蚊拍」这类短商品名很常见，
            // 长度下限统一交给下面的商品名筛选（>= 2）把关。
            return false
        }

        let candidatesLines = rawLines.filter { !isNotGoods($0) }

        // 商品名通常是描述最长的那行（2~40 字）
        let goods = candidatesLines
            .filter { $0.count >= 2 && $0.count <= 40 }
            .max(by: { $0.count < $1.count })

        // ---- 置信度 ----
        var conf = 0.0
        if goods != nil { conf += 0.45 }
        if price != nil { conf += 0.45 }
        if !candidates.isEmpty { conf += 0.1 }

        return Parsed(
            goods: goods,
            price: price,
            rawText: text,
            confidence: min(conf, 1.0),
            currencyCode: detectCurrency(in: text)
        )
    }

    // MARK: - 多币种（原产品爆火后紧急补的功能，我们出厂即支持）

    /// 从截图文本推断币种。
    ///
    /// 顺序很重要：必须先匹配 "HK$" 再匹配 "$"，否则香港价格会被记成美元。
    /// `¥` 在多地区共用，这里按日韩符号优先、再退到人民币的次序判断。
    static func detectCurrency(in text: String) -> String? {
        // 先处理带明确地区前缀的复合符号
        let prefixed: [(String, String)] = [
            ("HK$", "HKD"), ("NT$", "TWD"), ("US$", "USD"), ("A$", "AUD"),
            ("C$", "CAD"), ("S$", "SGD"), ("RMB", "CNY"), ("CNY", "CNY"),
            ("USD", "USD"), ("EUR", "EUR"), ("GBP", "GBP")
        ]
        for (token, code) in prefixed where text.contains(token) {
            return code
        }

        // 单一符号。
        // 顺序关键：`円`/`원` 这些明确后缀必须排在 `元` 之前。
        // 否则日本商品页里出现「元値」（原价）这种字，就会被误记成人民币。
        let single: [(String, String)] = [
            ("€", "EUR"), ("£", "GBP"), ("₩", "KRW"),
            ("円", "JPY"), ("원", "KRW"),
            ("元", "CNY"), ("¥", "CNY"), ("￥", "CNY"), ("$", "USD")
        ]
        for (token, code) in single where text.contains(token) {
            return code
        }
        return nil
    }
}
