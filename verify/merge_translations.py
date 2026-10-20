# -*- coding: utf-8 -*-
"""
把 translations_1.json / translations_2.json 合并进 Localizable.xcstrings。

安全检查：
1. 占位符（%@ %lld）必须一一对应，顺序可不同但数量必须一致
2. 空字符串拒绝写入
3. 不认识的 key 报警但不写入
4. 写入前备份原文件
"""
import json
import re
import shutil
from pathlib import Path

BASE = Path(r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin")
XCSTRINGS = BASE / "Bushaoxin" / "Localization" / "Localizable.xcstrings"
VERIFY = BASE / "verify"

PLACEHOLDER_RE = re.compile(r"%(?:@|lld|d|s)")

NEW_LANGS = ["fr", "de", "es", "pt-BR", "ru", "ar", "it", "nl"]


def count_placeholders(text):
    """返回占位符计数字典"""
    out = {}
    for m in PLACEHOLDER_RE.findall(text):
        out[m] = out.get(m, 0) + 1
    return out


def main():
    # 1. 载入原始 xcstrings
    with open(XCSTRINGS, encoding="utf-8") as f:
        data = json.load(f)
    strings = data["strings"]

    # 2. 载入翻译
    merged = {}
    for name in ["translations_1.json", "translations_2.json"]:
        p = VERIFY / name
        with open(p, encoding="utf-8") as f:
            part = json.load(f)
        for k, v in part.items():
            if k.startswith("_"):
                continue
            merged[k] = v

    print(f"翻译表条目数: {len(merged)}")
    print(f"xcstrings 条目数: {len(strings)}")

    # 3. 校验
    errors = []
    warnings = []
    applied = 0

    # 未知 key
    unknown = [k for k in merged if k not in strings]
    if unknown:
        warnings.append(f"未知 key（{len(unknown)} 个，将跳过）: {unknown[:5]}")

    # 逐条写入
    for key, langs in merged.items():
        if key not in strings:
            continue

        entry = strings[key]
        locs = entry.setdefault("localizations", {})

        # 用中文原文做占位符基准
        zh = (locs.get("zh-Hans", {}).get("stringUnit") or {}).get("value", "")
        zh_ph = count_placeholders(zh)

        for lang, text in langs.items():
            if not text or not text.strip():
                errors.append(f"{key} [{lang}]: 空字符串")
                continue

            ph = count_placeholders(text)
            if ph != zh_ph:
                errors.append(
                    f"{key} [{lang}]: 占位符不匹配\n"
                    f"    原文({zh_ph}): {zh}\n"
                    f"    译文({ph}): {text}"
                )
                continue

            # 写入
            if "stringUnit" not in locs.get(lang, {}):
                locs.setdefault(lang, {})
            locs[lang]["stringUnit"] = {"state": "translated", "value": text}
            applied += 1

    # 4. 报告
    print(f"\n已写入 {applied} 条翻译")

    if warnings:
        print(f"\n警告 ({len(warnings)}):")
        for w in warnings:
            print("  " + w)

    if errors:
        print(f"\n错误 ({len(errors)})，这些条目未写入:")
        for e in errors[:30]:
            print("  " + e)
        if len(errors) > 30:
            print(f"  ... 还有 {len(errors) - 30} 条")
    else:
        print("\n占位符校验全部通过")

    # 5. 覆盖率
    print("\n各语言覆盖率:")
    total = len(strings)
    lang_counts = {}
    for key, entry in strings.items():
        for lang, v in entry.get("localizations", {}).items():
            val = (v.get("stringUnit") or {}).get("value")
            if val:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

    for lang in sorted(lang_counts):
        n = lang_counts[lang]
        pct = round(n / total * 100, 1)
        mark = "OK  " if pct >= 99.9 else "WARN"
        print(f"  [{mark}] {lang:<8} {n}/{total} ({pct}%)")

    # 6. 备份并写入
    backup = XCSTRINGS.with_suffix(".xcstrings.bak")
    shutil.copy2(XCSTRINGS, backup)
    print(f"\n原文件已备份到: {backup.name}")

    # xcstrings 需要保持排序，否则 Xcode 每次打开都会重排
    data["strings"] = dict(sorted(strings.items()))

    with open(XCSTRINGS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, separators=(",", " : "))
        f.write("\n")

    print(f"已写入: {XCSTRINGS}")


if __name__ == "__main__":
    main()
