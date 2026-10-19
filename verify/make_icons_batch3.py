#!/usr/bin/env python3
"""第三批：打破常规的 12 个方向。

设计约束刻意放弃：
- 不再用"购物袋/硬币/标签"这类直接符号（太安全、太像同行）
- 不再用居中对称构图（对称 = 沉稳 = 无趣）
- 允许不规则形状、允许负空间、允许只有色块没有图形
- 允许字体作为图形（数字/符号），但要能脱离文字独立成立

每一条都是一个完整的视觉主张，不是配色变体。
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math
import os

SIZE = 1024
SS = 4
W = SIZE * SS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "candidates3")


def finish(img, name):
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    assert out.mode == "RGB" and out.size == (SIZE, SIZE)
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, f"{name}.png"), "PNG", optimize=True)
    out.resize((60, 60), Image.LANCZOS).save(os.path.join(OUT, f"{name}-60.png"))
    print(f"  {name}.png")


def blend(base, layer):
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


# ══════════════════════════════════════════════════════════
# R. 渐变落日 —— 纯粹的情绪，没有一个"物品"
#    橙色到紫的垂直渐变，水平线切断，像"一天结束前"
# ══════════════════════════════════════════════════════════
def r_sunset():
    top = (255, 138, 76)
    bot = (196, 78, 148)
    img = Image.new("RGB", (W, W))
    d = ImageDraw.Draw(img)
    for y in range(W):
        t = y / W
        # 非线性插值，中段更亮
        tt = t ** 0.85
        c = tuple(int(top[i] + (bot[i] - top[i]) * tt) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # 一条水平暗线切开画面，下方一块更深的色块（像地平线）
    horizon = int(W * 0.635)
    ld.rectangle([0, horizon, W, W], fill=(64, 32, 60, 70))
    ld.rectangle([0, horizon - int(W*0.012), W, horizon], fill=(255, 235, 220, 255))
    # 上方一个太阳的半圆
    sr = int(W * 0.115)
    ld.ellipse([W//2 - sr, horizon - sr*2, W//2 + sr, horizon], fill=(255, 245, 225, 240))
    img = blend(img, layer)
    return finish(img, "R-sunset")


# ══════════════════════════════════════════════════════════
# S. 负空间数字 —— 米色底，中间挖出一个 "0"
#    "0" = 零冲动/零浪费，同时是"圆圈"最简形态
# ══════════════════════════════════════════════════════════
def s_negative_zero():
    BG = (245, 241, 233)
    ACC = (28, 30, 58)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # 一个巨大的实心圆，中间挖空成粗环（0 形）
    R = int(W * 0.325)
    inner = int(R * 0.44)
    cx = cy = W // 2
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(*ACC, 255))
    d.ellipse([cx-inner, cy-inner, cx+inner, cy+inner], fill=(*BG, 255))
    img = blend(img, layer)
    return finish(img, "S-negative-zero")


# ══════════════════════════════════════════════════════════
# T. 半格 —— 画面被斜切成两半，两种颜色，没有任何图形
#    最激进：图标里什么也没有，只有颜色关系
# ══════════════════════════════════════════════════════════
def t_split():
    A = (33, 150, 136)      # 青
    B = (255, 202, 58)      # 黄
    # 左上三角 A，右下三角 B，沿对角线分开
    img = Image.new("RGB", (W, W), A)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon([(0, 0), (W, 0), (W, W)], fill=(*B, 255))
    img = blend(img, layer)
    return finish(img, "T-split")


# ══════════════════════════════════════════════════════════
# U. 阶梯向下 —— 五级台阶，最后一级悬空
#    "一步一步往下降" = 消费降级 / 冷静下来
# ══════════════════════════════════════════════════════════
def u_stairs():
    BG = (250, 247, 242)
    C1 = (46, 71, 122)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    n = 5
    step_w = int(W * 0.125)
    step_h = int(W * 0.075)
    start_x = int(W * 0.155)
    top_y = int(W * 0.235)
    for i in range(n):
        x = start_x + i * step_w
        y = top_y + i * step_h
        h = int(W * 0.46) - i * step_h
        # 最后一级悬空（不到底）
        if i == n - 1:
            h = int(h * 0.42)
        col = C1 if i < n - 1 else (120, 148, 200)
        top_col = (90, 118, 175) if i == n - 1 else (70, 100, 160)
        d.rectangle([x, y + step_h, x + step_w, y + step_h + h], fill=(*col, 255))
        # 台阶顶面（亮一点）
        d.rectangle([x, y, x + step_w, y + step_h], fill=(*top_col, 255))
    img = blend(img, layer)
    return finish(img, "U-stairs")


# ══════════════════════════════════════════════════════════
# V. 一个非常粗的斜杠 —— 极简到接近符号
#    黑底 + 一根珊瑚/粉色粗斜杠。绝对最小信息量。
# ══════════════════════════════════════════════════════════
def v_slash():
    BG = (18, 18, 20)
    ACC = (255, 106, 92)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w = int(W * 0.185)
    d.rounded_rectangle([W//2 - w//2, -int(W*0.1), W//2 + w//2, W + int(W*0.1)],
                        radius=w//2, fill=(*ACC, 255))
    layer = layer.rotate(-38, resample=Image.BICUBIC, center=(W//2, W//2))
    img = blend(img, layer)
    return finish(img, "V-slash")


# ══════════════════════════════════════════════════════════
# W. 像素/网格 —— 用方格拼一个"下降的方块"
#    有一点数字感，适合"数据化消费"
# ══════════════════════════════════════════════════════════
def w_pixels():
    BG = (240, 238, 232)
    DARK = (34, 36, 34)
    ACC = (86, 184, 122)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    n = 6
    cell = int(W * 0.105)
    gap = int(W * 0.014)
    total = n * cell + (n - 1) * gap
    x0 = (W - total) // 2
    y0 = (W - total) // 2

    # 阶梯状下降的方块图案
    pattern = [
        [1,1,0,0,0,0],
        [1,1,1,0,0,0],
        [0,1,1,1,0,0],
        [0,0,1,1,1,0],
        [0,0,0,1,1,1],
        [0,0,0,0,1,1],
    ]
    for r in range(n):
        for c in range(n):
            if pattern[r][c]:
                x = x0 + c * (cell + gap)
                y = y0 + r * (cell + gap)
                col = ACC if r >= 4 else DARK
                d.rounded_rectangle([x, y, x+cell, y+cell], radius=int(cell*0.18), fill=(*col, 255))

    img = blend(img, layer)
    return finish(img, "W-pixels")


# ══════════════════════════════════════════════════════════
# X. 印章 —— 一个不规则的圆，里面是粗竖线（像盖了个戳）
#    手作感，边缘有轻微抖动
# ══════════════════════════════════════════════════════════
def x_stamp():
    BG = (252, 249, 243)
    RED = (198, 58, 46)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = cy = W // 2
    R = int(W * 0.315)

    # 用多边形近似一个略不规则的圆
    pts = []
    steps = 96
    for i in range(steps):
        a = 2 * math.pi * i / steps
        wobble = 1 + 0.012 * math.sin(a * 7) + 0.008 * math.cos(a * 11)
        pts.append((cx + R * wobble * math.cos(a), cy + R * wobble * math.sin(a)))
    d.polygon(pts, fill=(*RED, 255))

    # 中间挖一条竖缝
    sw = int(W * 0.075)
    sh = int(R * 0.86)
    d.rounded_rectangle([cx - sw//2, cy - sh//2, cx + sw//2, cy + sh//2],
                        radius=sw//2, fill=(*BG, 255))

    img = blend(img, layer)
    return finish(img, "X-stamp")


# ══════════════════════════════════════════════════════════
# Y. 同心方框 —— 三个由大到小的方框，最后一个是实心
#    "收拢"，有冥想/聚焦的感觉
# ══════════════════════════════════════════════════════════
def y_nested():
    BG = (243, 240, 250)
    PUR = (92, 70, 168)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = cy = W // 2
    sizes = [(0.34, 0.052, 255), (0.235, 0.048, 255), (0.145, 0, 255)]
    for frac, wfrac, alpha in sizes:
        s = int(W * frac)
        if wfrac == 0:
            d.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=int(s*0.30), fill=(*PUR, alpha))
        else:
            ww = int(W * wfrac)
            d.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=int(s*0.30),
                                outline=(*PUR, alpha), width=ww)
    img = blend(img, layer)
    return finish(img, "Y-nested")


# ══════════════════════════════════════════════════════════
# Z. 液体/墨滴 —— 一团有机形状，像一滴墨落在纸上
#    完全不对称，最有"手工"感的方案
# ══════════════════════════════════════════════════════════
def z_blob():
    BG = (248, 246, 240)
    INK = (32, 56, 74)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, W // 2

    # 用极坐标生成一个有机 blob
    pts = []
    steps = 120
    R = int(W * 0.30)
    for i in range(steps):
        a = 2 * math.pi * i / steps
        r = R * (
            1.0
            + 0.16 * math.sin(a * 3 + 0.6)
            + 0.09 * math.sin(a * 5 - 1.2)
            + 0.05 * math.cos(a * 8)
        )
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=(*INK, 255))

    # 挖一个米色的缺口（负空间），制造方向感
    d.ellipse([cx + int(W*0.055), cy - int(W*0.135),
               cx + int(W*0.245), cy + int(W*0.055)], fill=(*BG, 255))

    img = blend(img, layer)
    return finish(img, "Z-blob")


# ══════════════════════════════════════════════════════════
# AA. 网格点阵 —— 9 个点，右下缺一个
#     "少一点"，极客/数据感
# ══════════════════════════════════════════════════════════
def aa_dots():
    BG = (255, 253, 248)
    DOT = (26, 26, 30)
    ACC = (245, 88, 96)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    n = 3
    spacing = int(W * 0.215)
    total = spacing * (n - 1)
    x0 = (W - total) // 2
    y0 = (W - total) // 2
    r = int(W * 0.072)

    for i in range(n):
        for j in range(n):
            x = x0 + j * spacing
            y = y0 + i * spacing
            if i == 2 and j == 2:
                # 右下角换成一个小圆点（红色），且半径更小
                rr = int(r * 0.62)
                d.ellipse([x-rr, y-rr, x+rr, y+rr], fill=(*ACC, 255))
            else:
                d.ellipse([x-r, y-r, x+r, y+r], fill=(*DOT, 255))

    img = blend(img, layer)
    return finish(img, "AA-dots")


# ══════════════════════════════════════════════════════════
# AB. 折纸 —— 两个三角形拼成一个"翻页"的封面色
#     几何、锐利、有体积感但完全扁平
# ══════════════════════════════════════════════════════════
def ab_fold():
    BG = (245, 243, 238)
    A = (218, 96, 64)
    B = (168, 62, 42)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 一个正方形旋转 45 度，被对角线分成明暗两半
    s = int(W * 0.355)
    cx = cy = W // 2
    pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
    # 左半
    d.polygon([pts[0], pts[3], pts[2]], fill=(*A, 255))
    # 右半
    d.polygon([pts[0], pts[1], pts[2]], fill=(*B, 255))

    img = blend(img, layer)
    return finish(img, "AB-fold")


# ══════════════════════════════════════════════════════════
# AC. 单色全屏 —— 整块珊瑚色，中间一个极小的白点
#     最反常规：几乎没有图形，靠"留白"制造注意力
# ══════════════════════════════════════════════════════════
def ac_dot():
    BG = (222, 106, 78)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = int(W * 0.072)
    d.ellipse([W//2-r, W//2-r, W//2+r, W//2+r], fill=(255, 250, 244, 255))
    img = blend(img, layer)
    return finish(img, "AC-dot")


SCHEMES = [
    ("R  渐变落日",     r_sunset),
    ("S  负空间零",     s_negative_zero),
    ("T  斜切双色",     t_split),
    ("U  下降阶梯",     u_stairs),
    ("V  粗斜杠",       v_slash),
    ("W  像素阶梯",     w_pixels),
    ("X  印章",         x_stamp),
    ("Y  同心方框",     y_nested),
    ("Z  墨滴",         z_blob),
    ("AA 点阵",         aa_dots),
    ("AB 折纸菱形",     ab_fold),
    ("AC 单色全屏",     ac_dot),
]


def main():
    print("第三批（打破常规）：")
    for name, fn in SCHEMES:
        try:
            fn()
        except Exception as e:
            print(f"  {name} 失败: {e}")
    print(f"\n输出: {OUT}")


if __name__ == "__main__":
    main()
