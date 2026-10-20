# -*- coding: utf-8 -*-
"""导出所有待翻译条目，供翻译用"""
import json

path = r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin\Bushaoxin\Localization\Localizable.xcstrings"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

strings = data["strings"]
print("总条目:", len(strings))
print()

# 按 key 前缀分组统计
from collections import Counter
prefixes = Counter()
for k in strings:
    p = k.split(".")[0] if "." in k else "(无前缀)"
    prefixes[p] += 1

print("按前缀分组:")
for p, n in sorted(prefixes.items(), key=lambda x: -x[1]):
    print(f"  {p:<20} {n}")

print()
print("=" * 70)
print("全部条目（key => 中文 / 英文参考）")
print("=" * 70)
for k in sorted(strings):
    locs = strings[k].get("localizations", {})
    zh = (locs.get("zh-Hans", {}).get("stringUnit") or {}).get("value", "")
    en = (locs.get("en", {}).get("stringUnit") or {}).get("value", "")
    print(f"{k}\n  ZH: {zh}\n  EN: {en}\n")
