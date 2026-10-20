# -*- coding: utf-8 -*-
"""
分析一张候选图标图：尺寸、颜色、主体占比、是否带 alpha、
缩到 60px 后是否还认得出。
"""
import sys
from collections import Counter
from PIL import Image

path = sys.argv[1]
print("=" * 60)
print("文件:", path)

im = Image.open(path)
print("原始模式:", im.mode)
print("原始尺寸:", im.size)

# 转 RGB 分析（图标不能带 alpha）
rgb = im.convert("RGB")
W, H = rgb.size

if W != H:
    print(f"⚠️ 不是正方形：{W}x{H}（比例 {W/H:.3f}）")
else:
    print(f"✅ 正方形 {W}x{H}")

# 颜色统计
small = rgb.resize((128, 128), Image.LANCZOS)
px = list(small.getdata())
cnt = Counter(px)
total = len(px)

print("\n--- 主色 TOP 10 ---")
for color, n in cnt.most_common(10):
    pct = n / total * 100
    print(f"  RGB{color}  #{color[0]:02X}{color[1]:02X}{color[2]:02X}  {pct:5.1f}%")

print(f"\n唯一颜色数（128px 采样）: {len(cnt)}")

# 背景色 = 四角最常见的颜色
corners = [
    rgb.getpixel((2, 2)),
    rgb.getpixel((W - 3, 2)),
    rgb.getpixel((2, H - 3)),
    rgb.getpixel((W - 3, H - 3)),
]
print("\n--- 四角颜色 ---")
for i, c in enumerate(corners):
    print(f"  {['左上','右上','左下','右下'][i]}: #{c[0]:02X}{c[1]:02X}{c[2]:02X}")

bg = Counter(corners).most_common(1)[0][0]
uniform = all(
    abs(c[0] - bg[0]) <= 12 and abs(c[1] - bg[1]) <= 12 and abs(c[2] - bg[2]) <= 12
    for c in corners
)
print(f"\n背景色: #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}   四角一致={uniform}")


def coverage(img, bg, tol=40):
    """统计非背景像素占比"""
    w, h = img.size
    data = img.getdata()
    n = 0
    for c in data:
        if abs(c[0] - bg[0]) > tol or abs(c[1] - bg[1]) > tol or abs(c[2] - bg[2]) > tol:
            n += 1
    return n / (w * h) * 100


print("\n--- 主体占比（非背景像素）---")
for size, label in [(128, "128px"), (60, "60px")]:
    r = rgb.resize((size, size), Image.LANCZOS)
    cov = coverage(r, bg)
    if 20 <= cov <= 28:
        verdict = "✅ 理想区间 20–28%"
    elif 15 <= cov < 20:
        verdict = "⚠️ 略小，60px 可能偏弱"
    elif cov < 15:
        verdict = "❌ 太小，桌面会认不出"
    elif cov <= 35:
        verdict = "⚠️ 略大"
    else:
        verdict = "❌ 太大，显得拥挤"
    print(f"  {label}: {cov:5.1f}%  {verdict}")

# 亮度/对比度
print("\n--- 明暗分布 ---")
gray = rgb.convert("L")
gpx = list(gray.resize((64, 64)).getdata())
dark = sum(1 for v in gpx if v < 85) / len(gpx) * 100
mid = sum(1 for v in gpx if 85 <= v < 170) / len(gpx) * 100
light = sum(1 for v in gpx if v >= 170) / len(gpx) * 100
print(f"  暗部 {dark:5.1f}%   中间调 {mid:5.1f}%   亮部 {light:5.1f}%")

# alpha 检查
has_alpha = "A" in im.mode and im.convert("RGBA").getchannel("A").getextrema() != (255, 255)
print(f"\n带透明通道: {has_alpha}  {'❌ 上传会报 Invalid app icon' if has_alpha else '✅'}")

# 边缘留白检查：主体是否贴边
print("\n--- 边缘检查（主体是否贴边）---")
edges = {
    "上": [rgb.getpixel((x, 0)) for x in range(0, W, max(1, W // 50))],
    "下": [rgb.getpixel((x, H - 1)) for x in range(0, W, max(1, W // 50))],
    "左": [rgb.getpixel((0, y)) for y in range(0, H, max(1, H // 50))],
    "右": [rgb.getpixel((W - 1, y)) for y in range(0, H, max(1, H // 50))],
}
for name, samples in edges.items():
    nonbg = sum(
        1 for c in samples
        if abs(c[0] - bg[0]) > 40 or abs(c[1] - bg[1]) > 40 or abs(c[2] - bg[2]) > 40
    )
    pct = nonbg / len(samples) * 100
    flag = "（主体贴边）" if pct > 5 else ""
    print(f"  {name}边: {pct:5.1f}% 非背景 {flag}")

print("=" * 60)
