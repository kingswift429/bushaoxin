"""
把 Localizable.xcstrings 重新格式化成 Xcode 自己的风格。

背景：之前用 PowerShell 的 ConvertTo-Json 写过这个文件，
它把每个 stringUnit 展开成 5 行，137 个 key 撑到 3842 行。
Xcode 自己保存的格式是把 "state" 和 "value" 写在同一行，
可读性和 diff 噪音都明显更好。

用法：python verify/format_xcstrings.py
"""
import json
import io
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.normpath(os.path.join(
    HERE, "..", "Bushaoxin", "Localization", "Localizable.xcstrings"
))

with io.open(PATH, encoding="utf-8") as f:
    data = json.load(f, object_pairs_hook=OrderedDict)

strings = data["strings"]
langs = ["en", "ja", "ko", "zh-Hans"]

out = io.StringIO()
out.write('{\n')
out.write('  "sourceLanguage" : "%s",\n' % data["sourceLanguage"])
out.write('  "strings" : {\n')

keys = sorted(strings.keys())
for ki, key in enumerate(keys):
    entry = strings[key]
    out.write('    %s : {\n' % json.dumps(key, ensure_ascii=False))
    out.write('      "localizations" : {\n')

    loc = entry.get("localizations", {})
    present = [l for l in langs if l in loc]
    for li, lang in enumerate(present):
        unit = loc[lang].get("stringUnit", {})
        state = unit.get("state", "translated")
        value = unit.get("value", "")
        comma = "," if li < len(present) - 1 else ""
        out.write(
            '        %s : {\n'
            '          "stringUnit" : {\n'
            '            "state" : "%s",\n'
            '            "value" : %s\n'
            '          }\n'
            '        }%s\n'
            % (json.dumps(lang), state,
               json.dumps(value, ensure_ascii=False), comma)
        )
    out.write('      }\n')
    out.write('    }%s\n' % ("," if ki < len(keys) - 1 else ""))
    # Xcode 在 key 之间不加空行

out.write('  },\n')
out.write('  "version" : "%s"\n' % data.get("version", "1.0"))
out.write('}\n')

text = out.getvalue()

# 先验证重新解析后内容完全一致，再写盘
reparsed = json.loads(text, object_pairs_hook=OrderedDict)
assert reparsed["sourceLanguage"] == data["sourceLanguage"], "sourceLanguage 变了"
assert reparsed.get("version") == data.get("version"), "version 变了"
assert set(reparsed["strings"].keys()) == set(strings.keys()), "key 集合变了"
for k in strings:
    for l in langs:
        a = strings[k].get("localizations", {}).get(l, {}).get("stringUnit", {}).get("value")
        b = reparsed["strings"][k].get("localizations", {}).get(l, {}).get("stringUnit", {}).get("value")
        assert a == b, "内容不一致: %s / %s" % (k, l)

with io.open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

old_lines = 3842
new_lines = text.count("\n")
print("OK  keys=%d  %d lines -> %d lines" % (len(keys), old_lines, new_lines))
