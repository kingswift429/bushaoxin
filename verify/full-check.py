"""全量校验：本地化完整性 + 文件结构。"""
import io
import json
import os
import re
import sys

root = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(root)  # 到 bushaoxin/

ok = True


def fail(msg):
    global ok
    ok = False
    print("  FAIL " + msg)


# ---- 1. xcstrings 合法 ----
xc_path = os.path.join(root, "Bushaoxin", "Localization", "Localizable.xcstrings")
with io.open(xc_path, encoding="utf-8") as f:
    xc = json.load(f)
cat_keys = set(xc["strings"].keys())
print("[1] xcstrings: %d keys, sourceLanguage=%s" % (len(cat_keys), xc["sourceLanguage"]))

# ---- 2. L.swift 引用的 key 都存在 ----
l_path = os.path.join(root, "Bushaoxin", "Localization", "L.swift")
src = io.open(l_path, encoding="utf-8").read()
pattern = r'String\((?:format:\s*String\()?localized:\s*"([^"]+)"'
used = set(re.findall(pattern, src))
missing = used - cat_keys
print("[2] L.swift uses %d keys, missing in catalog: %d" % (len(used), len(missing)))
if missing:
    fail("missing keys: %s" % sorted(missing))

# ---- 3. 四语翻译完整 + 占位符一致 ----
langs = ["en", "ja", "ko", "zh-Hans"]
empty = []
ph_bad = []
for key, entry in xc["strings"].items():
    loc = entry.get("localizations", {})
    expect_ph = sorted(re.findall(r"%[@dlif]+", key))
    for lang in langs:
        unit = loc.get(lang, {}).get("stringUnit", {})
        val = unit.get("value", "")
        if not val:
            empty.append("%s/%s" % (key, lang))
            continue
        got_ph = sorted(re.findall(r"%[@dlif]+", val))
        if got_ph != expect_ph:
            ph_bad.append("%s/%s exp=%s got=%s" % (key, lang, expect_ph, got_ph))
print("[3] empty translations: %d, placeholder mismatches: %d" % (len(empty), len(ph_bad)))
for e in empty[:10]:
    fail("empty: " + e)
for p in ph_bad[:10]:
    fail("placeholder: " + p)

# ---- 4. Swift 括号平衡 ----
swift_dir = os.path.join(root, "Bushaoxin")
files = []
for dirpath, _, names in os.walk(swift_dir):
    for n in names:
        if n.endswith(".swift"):
            files.append(os.path.join(dirpath, n))
unbalanced = []
for fp in files:
    t = io.open(fp, encoding="utf-8").read()
    if t.count("{") != t.count("}"):
        unbalanced.append(os.path.basename(fp))
print("[4] swift files: %d, unbalanced: %d" % (len(files), len(unbalanced)))
for u in unbalanced:
    fail("unbalanced braces: " + u)

# ---- 5. 必要文件存在 ----
required = [
    "project.yml",
    ".gitignore",
    ".github/workflows/build-ios.yml",
    "Bushaoxin/Assets.xcassets/AppIcon.appiconset/icon-1024.png",
    "Bushaoxin/Assets.xcassets/AppIcon.appiconset/Contents.json",
    "Bushaoxin/Assets.xcassets/AccentColor.colorset/Contents.json",
    "Bushaoxin/PrivacyInfo.xcprivacy",
    "docs/supabase_schema.sql",
]
missing_files = [r for r in required if not os.path.exists(os.path.join(root, r))]
print("[5] required files missing: %d" % len(missing_files))
for m in missing_files:
    fail("missing file: " + m)

# ---- 6. Assets Contents.json 引用了真实图标 ----
icon_json = os.path.join(root, "Bushaoxin", "Assets.xcassets",
                         "AppIcon.appiconset", "Contents.json")
with io.open(icon_json, encoding="utf-8") as f:
    ij = json.load(f)
img = ij["images"][0]
icon_file = os.path.join(os.path.dirname(icon_json), img.get("filename", ""))
if not os.path.exists(icon_file):
    fail("AppIcon Contents.json 指向不存在的文件: %s" % img.get("filename"))
else:
    print("[6] AppIcon -> %s  OK" % img["filename"])

print("")
if ok:
    print("全部校验通过")
    sys.exit(0)
else:
    print("存在失败项，见上")
    sys.exit(1)
