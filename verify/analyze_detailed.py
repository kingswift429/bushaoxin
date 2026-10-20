# -*- coding: utf-8 -*-
"""分析 Gemini 冰购物车图标：找主体位置、范围、颜色分布"""
import sys
from collections import Counter
from PIL import Image

path = sys.argv[1]
im = Image.open(path).convert("RGB")
W, H = im.size
print(f"尺寸: {W}x{H}\n")

# 缩小到 256 做分析
s = im.resize((256, 256), Image.LANCZOS)
px = s.load()

# 背景估：四角 + 边缘平均
def bright(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

edge_samples = []
for x in range(0, 256, 8):
    edge_samples += [px[x, 2], px[x, 253]]
for y in range(0, 256, 8):
    edge_samples += [px[2, y], px[253, y]]
bg = tuple(sum(c[i] for c in edge_samples) // len(edge_samples) for i in range(3))
print(f"背景色（边缘平均）: #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}  亮度 {bright(bg):.0f}")

bg_bright = bright(bg)

# 找"显著不同"的像素 = 主体
print("\n--- 亮度阈值扫描（找到主体）---")
for delta in [20, 30, 40, 50, 60, 80]:
    n = 0
    for y in range(256):
        for x in range(256):
            if abs(bright(px[x, y]) - bg_bright) > delta:
                n += 1
    print(f"  亮度差 > {delta}: {n/(256*256)*100:5.1f}%")

# 用 delta=40 做主体现
mask = [[abs(bright(px[x, y]) - bg_bright) > 40 for x in range(256)] for y in range(256)]

xs = [x for y in range(256) for x in range(256) if mask[y][x]]
ys = [y for y in range(256) for x in range(256) if mask[y][x]]
if xs:
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(f"\n主体包围盒（256 坐标）: x {x0}~{x1}, y {y0}~{y1}")
    print(f"主体占画面宽 {((x1-x0+1)/256*100):.1f}%  高 {((y1-y0+1)/256*100):.1f}%")
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    print(f"中心偏移: ({cx-128:+.1f}, {cy-128:+.1f})  距正中 {((cx-128)**2+(cy-128)**2)**0.5:.1f}px")
else:
    print("\n未检测到明显主体")

# 主体的颜色
subj_colors = Counter()
for y in range(256):
    for x in range(256):
        if mask[y][x]:
            subj_colors[px[x, y]] += 1
print("\n--- 主体颜色 TOP 8 ---")
tot = sum(subj_colors.values()) or 1
for c, n in subj_colors.most_common(8):
    print(f"  #{c[0]:02X}{c[1]:02X}{c[2]:02X}  {n/tot*100:5.1f}%  亮度 {bright(c):.0f}")

# 背景是否渐变
print("\n--- 背景是否渐变 ---")
for label, (x, y) in [("左上", (8, 8)), ("右上", (247, 8)), ("左下", (8, 247)), ("右下", (247, 247)), ("中心", (128, 128))]:
    c = px[x, y]
    print(f"  {label}: #{c[0]:02X}{c[1]:02X}{c[2]:02X}  亮度 {bright(c):.0f}")

# 60px 下主体是否糊
print("\n--- 60px 缩略后的主体完整度 ---")
tiny = im.resize((60, 60), Image.LANCZOS)
tp = tiny.load()
tb = bright(bg)
n60 = sum(1 for y in range(60) for x in range(60) if abs(bright(tp[x, y]) - tb) > 40)
print(f"  60px 主体占比: {n60/3600*100:.1f}%")

# 对比度：主体 vs 背景亮度差
if subj_colors:
    main_subj = subj_colors.most_common(1)[0][0]
    contrast = abs(bright(main_subj) - bg_bright)
    print(f"\n主体/背景亮度差: {contrast:.0f}")
    if contrast < 50:
        print("  ⚠️ 对比度偏低，缩小后容易糊")
    else:
        print("  ✅ 对比度足够")
