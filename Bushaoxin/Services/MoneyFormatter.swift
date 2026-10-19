import Foundation

/// 多币种金额格式化与识别。
///
/// 设计要点：
/// - 金额一律用 `Decimal` 存，避免 Double 在账本累加中的精度漂移；
/// - 显示交给 `NumberFormatter`，自动跟随系统地区的小数位与符号位置
///   （日元韩元无小数位、欧元小数点用逗号，全部自动正确）；
/// - **不做汇率换算**。海外用户看到自己输入的币种数字才直观，
///   而且汇率需要联网与合规声明，本期刻意不碰。
enum MoneyFormatter {

    /// 带币种符号的完整金额，如 ¥15 / $15.00 / 1,360 円
    static func string(_ value: Decimal, code: String, locale: Locale = .current) -> String {
        let f = NumberFormatter()
        f.numberStyle = .currency
        f.locale = locale
        f.currencyCode = code
        // 金额是账本数字，不做四舍五入猜测，按币种默认精度
        f.minimumFractionDigits = 0
        let ns = NSDecimalNumber(decimal: value)
        return f.string(from: ns) ?? "\(ns)"
    }

    /// 只要数字部分，用于图表/卡片大字号展示
    static func plainNumber(_ value: Decimal, locale: Locale = .current) -> String {
        let f = NumberFormatter()
        f.numberStyle = .decimal
        f.locale = locale
        f.maximumFractionDigits = 2
        return f.string(from: NSDecimalNumber(decimal: value)) ?? "\(value)"
    }

    /// 币种符号，单独展示用
    static func symbol(for code: String, locale: Locale = .current) -> String {
        let f = NumberFormatter()
        f.numberStyle = .currency
        f.locale = locale
        f.currencyCode = code
        return f.currencySymbol ?? code
    }

    /// 按系统地区取默认币种
    static var deviceCurrencyCode: String {
        Locale.current.currency?.identifier ?? "CNY"
    }

    /// 把用户输入的字符串解析成 Decimal。
    ///
    /// 关键：**不能无条件删掉逗号**。
    /// 德语/法语/西语用户输入 `9,99` 表示 9.99，无脑删逗号会变成 999 —— 放大 100 倍。
    /// 所以先按当前地区解析，解析不出来再回退到"逗号=千分位"的假设。
    static func parse(_ text: String, locale: Locale = .current) -> Decimal? {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }

        let f = NumberFormatter()
        f.numberStyle = .decimal
        f.locale = locale
        f.generatesDecimalNumbers = true
        if let n = f.number(from: trimmed) as? NSDecimalNumber, n != .notANumber {
            return n.decimalValue
        }

        // 回退：当作"逗号是千分位、句点是小数点"处理（中文/英文习惯）
        let cleaned = trimmed
            .replacingOccurrences(of: ",", with: "")
            .replacingOccurrences(of: " ", with: "")
        return Decimal(string: cleaned)
    }
}

// MARK: - 汇率无关的多币种账本

/// 账本统计：**分币种累加，绝不跨币种相加**。
/// 把 ¥100 和 $100 加到一起是最常见也最尴尬的本地化 bug。
struct MoneyBucket {
    private(set) var totals: [String: Decimal] = [:]

    mutating func add(_ value: Decimal, code: String) {
        totals[code, default: 0] += value
    }

    var isEmpty: Bool { totals.isEmpty }

    /// 按金额从大到小
    var sorted: [(code: String, amount: Decimal)] {
        totals.map { (code: $0.key, amount: $0.value) }
            .sorted { $0.amount > $1.amount }
    }

    /// 主币种（金额最大者），用于大字号主展示
    var primary: (code: String, amount: Decimal)? { sorted.first }
}
