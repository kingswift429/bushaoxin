# -*- coding: utf-8 -*-
"""检查 Localizable.xcstrings 的多语言覆盖率"""
import json

path = r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin\Bushaoxin\Localization\Localizable.xcstrings"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

print("源语言:", data.get("sourceLanguage", "(未标注)"))
strings = data.get("strings", {})
print("条目总数:", len(strings))

langs = {}
for key, entry in strings.items():
    locs = entry.get("localizations", {})
    for lang, v in locs.items():
        val = (v.get("stringUnit") or {}).get("value")
        if val:
            langs.setdefault(lang, 0)
            langs[lang] += 1

print("\n各语言覆盖率:")
total = len(strings)
for lang in sorted(langs):
    n = langs[lang]
    pct = round(n / total * 100, 1) if total else 0
    flag = "OK" if pct >= 95 else "WARN"
    print(f"  [{flag}] {lang:<10} {n}/{total}  ({pct}%)")

# 找出缺翻译的 key
print("\n缺翻译的条目（按语言）:")
for lang in sorted(langs):
    missing = []
    for key, entry in strings.items():
        locs = entry.get("localizations", {})
        v = locs.get(lang, {})
        val = (v.get("stringUnit") or {}).get("value")
        if not val:
            missing.append(key)
    if missing:
        print(f"  {lang}: {len(missing)} 条")
        for m in missing[:10]:
            print(f"     - {m}")
        if len(missing) > 10:
            print(f"     ... 还有 {len(missing) - 10} 条")
    else:
        print(f"  {lang}: 完整")
