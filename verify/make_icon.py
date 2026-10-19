"""
生成 App 图标占位图。
真正上架前应换成设计师版本，但没有图标会直接导致编译失败。
"""
from PIL import Image, ImageDraw, ImageFont
import os

SIZE = 1024
# 本脚本在 verify/ 下，图标要写到上一层的 Bushaoxin/Assets.xcassets/
OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "Bushaoxin", "Assets.xcassets", "AppIcon.appiconset", "icon-1024.png"
)
OUT = os.path.normpath(OUT)

# 品牌色：暖橙红（和 Theme 里的 accent 一致）
BG = (217, 102, 74)
FG = (255, 253, 250)

img = Image.new("RGB", (SIZE, SIZE), BG)
d = ImageDraw.Draw(img)

# 背景加一点纵向渐变，避免纯色显得廉价
for y in range(SIZE):
    t = y / SIZE
    r = int(217 - 18 * t)
    g = int(102 + 30 * t)
    b = int(74 + 34 * t)
    d.line([(0, y), (SIZE, y)], fill=(r, g, b))

# 中央画一个「不」的意象：一横 + 一个断点圆
cx, cy = SIZE // 2, SIZE // 2

# 主体粗横线（代表"拦下")
bar_w, bar_h = 560, 92
d.rounded_rectangle(
    [cx - bar_w // 2, cy - bar_h // 2, cx + bar_w // 2, cy + bar_h // 2],
    radius=bar_h // 2, fill=FG
)

# 上方撇捺简化成一个元素
d.rounded_rectangle(
    [cx - 300, cy - 250, cx - 190, cy - 250 + 96],
    radius=48, fill=FG
)
d.rounded_rectangle(
    [cx + 190, cy - 250, cx + 300, cy - 250 + 96],
    radius=48, fill=FG
)

# 下方两点
dot_r = 54
d.ellipse([cx - 170 - dot_r, cy + 130, cx - 170 + dot_r, cy + 130 + 2 * dot_r], fill=FG)
d.ellipse([cx + 170 - dot_r, cy + 130, cx + 170 + dot_r, cy + 130 + 2 * dot_r], fill=FG)

img.save(OUT, "PNG")
print(f"saved {OUT}  {img.size}")
