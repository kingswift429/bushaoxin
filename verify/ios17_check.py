"""iOS 17 / Swift 5.9 API 兼容性检查。

为什么需要这个：
    这台机器是 Windows，没法编译。而"能否编译"最常栽在
    「用了 iOS 18+ 才有的 API」或「#Predicate 用了它不支持的表达式」上。
    这类错误人眼审查看不出来，但一定会让 xcodebuild 失败。

    这个脚本把已知的高危模式扫一遍，输出「文件:行号 + 原因 + 改法」。

用法：python verify/ios17_check.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)
SRC = os.path.join(ROOT, "Bushaoxin")

# (正则, 说明, 严重度)
# 严重度 E = 大概率编译失败；W = 可能失败/行为异常；I = 提示
RULES = [
    # ---------- SwiftData #Predicate 的已知限制 ----------
    (r"#Predicate[^}]*?\$0\.\w+\s*==\s*nil",
     "#Predicate 对可选属性的 nil 比较支持不完整，可能编译失败或运行时报错",
     "E"),
    (r"#Predicate[^}]*?\.count",
     "#Predicate 不支持集合的 .count，需先取回再过滤",
     "E"),
    (r"#Predicate[^}]*?\.contains\(",
     "#Predicate 对 contains 支持受限（仅限数组字面量/关系），确认类型",
     "W"),
    (r"#Predicate[^}]*?\|\|",
     "#Predicate 支持 || 但嵌套复杂表达式易触发类型推断超时",
     "W"),

    # ---------- iOS 18+ 才有的 API ----------
    (r"\.scrollIndicators\(\.never\)",
     "scrollIndicators 需要 iOS 16+（本项目 iOS 17 没问题，仅提示）", "I"),
    (r"TabView\s*\([^)]*\)\s*\{[^}]*Tab\s*\(",
     "SwiftUI 新的 Tab 值类型需要 iOS 18+，iOS 17 必须用 .tabItem", "E"),
    (r"\.containerRelativeFrame\(",
     "containerRelativeFrame 需要 iOS 17+（可用，确认 deployment target ≥17）", "I"),
    (r"\.symbolEffect\(",
     "symbolEffect 需要 iOS 17+", "I"),
    # 只报「单参数闭包」的旧写法。
    # 两参数写法是 `.onChange(of: x) { old, new in` 或 `.onChange(of: x) { _, new in`，
    # 特征是 `{` 后到第一个换行前出现了逗号。所以：匹配 `{` 后不含逗号的行。
    (r"\.onChange\(of:[^\n]*\)[ \t]*\{[ \t]*[A-Za-z_]?[A-Za-z0-9_]*[ \t]*\n",
     "onChange 旧单参数闭包在 iOS 17 已废弃，应写成 { old, new in }", "W"),
    (r"\.contentMargins\(",
     "contentMargins 需要 iOS 17+", "I"),
    (r"\.scrollTargetBehavior\(",
     "scrollTargetBehavior 需要 iOS 17+", "I"),
    (r"\.scrollPosition\(",
     "scrollPosition 需要 iOS 17+", "I"),

    # ---------- Observation / @Observable ----------
    # import 是否齐全由上面的 IMPORT_REQUIREMENTS 精确检查，这里不重复报。

    # ---------- StoreKit 2 ----------
    (r"Product\.products\(",
     "StoreKit 2 需 iOS 15+，确认已 import StoreKit", "I"),
    (r"Transaction\.updates",
     "Transaction.updates 是无限 AsyncSequence，必须放在 Task 里且不要 break", "W"),
    (r"\.distantFuture",
     "StoreKit 用 distantFuture 表示永久授权会误导用户，确认是刻意行为", "W"),

    # ---------- Vision / OCR ----------
    (r"VNRecognizeTextRequest",
     "Vision OCR 需 iOS 13+，确认已 import Vision", "I"),
    (r"\.recognitionLanguages\s*=",
     "设置识别语言时要用 supportedRecognitionLanguages 里存在的代码", "W"),

    # ---------- Concurrency ----------
    (r"withCheckedContinuation",
     "必须保证恰好 resume 一次，建议用锁保护（项目已有 OnceBox）", "W"),
    (r"DispatchQueue\.main\.asyncAfter",
     "会让 View 生命周期与定时器脱钩，优先用 .task + Task.sleep", "W"),
    (r"Task\.detached",
     "detached 不继承 actor 上下文，访问 @MainActor 状态需显式 await", "W"),
    (r"\.sleep\(nanoseconds",
     "Task.sleep(nanoseconds:) 在 iOS 17 已废弃，用 .sleep(for:)", "W"),

    # ---------- 可选值 / 强制解包 ----------
    (r"randomElement\(\)\s*!",
     "语料为空时会崩溃", "E"),
    (r"\.first\s*!\s",
     "集合为空时会崩溃", "E"),
    (r"\btry!\b",
     "try! 会在失败时崩溃", "E"),
    (r"\bas!\b",
     "as! 会在类型不符时崩溃", "E"),
    (r"URL\(string:\s*(?!\s*\")[^)]*\)\s*!",
     "URL(string:) 传变量时结果可能为 nil，加 ! 会在解析失败时崩溃", "E"),
    (r"URL\(string:\s*\"[^\"]*\"\)\s*!",
     "URL(string:) 传常量字面量时结果在编译期可确定（通常安全，仅提示）", "I"),
    (r"UserDefaults\.standard\.set\([^,]+,\s*forKey:\s*\"",
     "确认 key 是常量不是拼接", "I"),

    # ---------- SwiftUI 常见编译错误 ----------
    (r"\.sheet\(\s*isPresented:\s*\$",
     "多层 sheet 挂到子视图上会被静默丢弃，确认挂在最外层", "W"),
    # 注意：只报「直接对 prefix/suffix 做 ForEach」而没包 Array() 的情况。
    # `ForEach(Array(list.prefix(n)))` 是正确的，不应报警。
    (r"ForEach\(\s*[A-Za-z_][A-Za-z0-9_\.]*\.(?:prefix|suffix)\(",
     "ForEach 直接接收 Slice 不行，需要包一层 Array()", "E"),
    (r"ForEach\(\s*\d*\s*\.\.<",
     "Range<Int> 做 ForEach 需要 id: \\.self", "W"),
    (r"Text\([^)]*\\\(",
     "确认插值在本地化 key 中用 %@/%lld，否则查不到译文", "I"),
    (r"Button\([^)]*\)\s*\{\s*\}\s*label:",
     "Button 的 action 为空闭包会静默失效", "W"),

    # ---------- 多语言 ----------
    (r'String\(localized:\s*"[^"]*\\\(',
     "localized key 里不能有 Swift 插值，必须用 %@/%lld + String(format:)", "E"),
    (r'String\(localized:\s*"[^"]*%d"',
     "%d 与 Int 在 String Catalog 中不匹配，要用 %lld", "W"),
]

COMPILED = []
for pat, desc, sev in RULES:
    try:
        COMPILED.append((re.compile(pat, re.S), desc, sev))
    except re.error as e:
        print("规则正则写错: %s -> %s" % (pat, e))
        sys.exit(2)

findings = []

# 需要 import 才能用的符号 -> 可接受的 import 列表
IMPORT_REQUIREMENTS = [
    (r"@Observable\b", ["Observation", "SwiftUI"], "Observation"),
    (r"@Bindable\b", ["SwiftUI", "SwiftData"], "SwiftUI"),
    (r"\bModelContainer\b|\b@Model\b|\b@Query\b|\bFetchDescriptor\b",
     ["SwiftData"], "SwiftData"),
    (r"\bVNRecognizeTextRequest\b|\bVNImageRequestHandler\b", ["Vision"], "Vision"),
    (r"\bProduct\.products\b|\bTransaction\.updates\b", ["StoreKit"], "StoreKit"),
    (r"\bPhotosPicker\b", ["PhotosUI"], "PhotosUI"),
    (r"\bUNUserNotificationCenter\b", ["UserNotifications"], "UserNotifications"),
    (r"\bUIViewControllerRepresentable\b|\bUIGraphicsImageRenderer\b", ["UIKit", "SwiftUI"], "UIKit"),
]

for dirpath, _, names in os.walk(SRC):
    for name in sorted(names):
        if not name.endswith(".swift"):
            continue
        fp = os.path.join(dirpath, name)
        rel = os.path.relpath(fp, ROOT).replace("\\", "/")
        with io.open(fp, encoding="utf-8") as f:
            lines = f.readlines()
        text = "".join(lines)

        # 把注释行替换成等长空白（保留行号），避免注释里的示例代码被误报。
        masked = []
        in_block = False
        for ln in lines:
            stripped = ln.strip()
            if in_block:
                if "*/" in stripped:
                    in_block = False
                masked.append(" " * len(ln.rstrip("\n")) + "\n")
                continue
            if stripped.startswith("/*"):
                if "*/" not in stripped:
                    in_block = True
                masked.append(" " * len(ln.rstrip("\n")) + "\n")
                continue
            if stripped.startswith("//"):
                masked.append(" " * len(ln.rstrip("\n")) + "\n")
                continue
            # 行尾注释也去掉，但保留代码部分
            code_part = ln
            idx = ln.find("//")
            if idx > 0 and '"' not in ln[:idx]:
                code_part = ln[:idx] + " " * (len(ln.rstrip("\n")) - idx) + "\n"
            masked.append(code_part)
        scan_text = "".join(masked)

        # ---------- import 完整性检查（真问题，会直接编译失败） ----------
        imported = set(re.findall(r"^\s*import\s+(\w+)", scan_text, re.M))
        for sym_rx, need_any, module in IMPORT_REQUIREMENTS:
            if re.search(sym_rx, scan_text):
                if not any(m in imported for m in need_any):
                    m = re.search(sym_rx, scan_text)
                    line_no = scan_text.count("\n", 0, m.start()) + 1
                    findings.append((
                        "E", rel, line_no,
                        "用到了 %s 但没有 import %s（实际已 import: %s）"
                        % (module, " 或 ".join(need_any), ", ".join(sorted(imported)) or "无"),
                        lines[line_no - 1].strip()
                    ))

        for rx, desc, sev in COMPILED:
            for m in rx.finditer(scan_text):
                line_no = scan_text.count("\n", 0, m.start()) + 1
                snippet = lines[line_no - 1].strip()
                findings.append((sev, rel, line_no, desc, snippet))

# 按严重度排序
order = {"E": 0, "W": 1, "I": 2}
findings.sort(key=lambda x: (order[x[0]], x[1], x[2]))

e_count = sum(1 for f in findings if f[0] == "E")
w_count = sum(1 for f in findings if f[0] == "W")
i_count = sum(1 for f in findings if f[0] == "I")

print("=" * 70)
print("iOS 17 API 兼容性检查")
print("=" * 70)

shown_e = shown_w = 0
for sev, rel, line_no, desc, snippet in findings:
    if sev == "E":
        shown_e += 1
        print("\n[E] %s:%d" % (rel, line_no))
        print("    问题: %s" % desc)
        print("    代码: %s" % snippet[:110])
    elif sev == "W":
        shown_w += 1
        if shown_w <= 25:
            print("\n[W] %s:%d" % (rel, line_no))
            print("    提示: %s" % desc)
            print("    代码: %s" % snippet[:110])

print("\n" + "=" * 70)
print("E (大概率编译失败/崩溃): %d" % e_count)
print("W (需人工确认): %d" % w_count)
print("I (提示): %d" % i_count)
print("=" * 70)

sys.exit(1 if e_count > 0 else 0)
