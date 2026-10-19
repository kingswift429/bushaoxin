#!/usr/bin/env python3
"""第二批候选图标：换配色体系 + 换形状语言。

配色策略（每套都是一个独立的色彩意图，不是随便调色）：

1. INK      墨黑 + 亮黄。高对比，像警示牌。省钱的"省"有锋利感。
2. MINT     薄荷绿 + 奶油白。冷静、医疗感，对应"冷静一下"。
3. INDIGO   靛蓝 + 浅底。金融信任感，银行/记账类通用语言。
4. SAND     沙棕 + 陶土。日式、侘寂，克制、不喧闹。
5. ORANGE   橘 + 深棕。暖但比珊瑚红更饱和，更有食欲般的驱动感。
6. PLUM     深紫 + 粉。夜间、高级，几乎无竞品用这个组合。
7. TEAL     青绿 + 米白。冷静但比薄荷更有性格。
8. MONO     纯黑白。最极端的极简，靠形状本身说话。

形状策略：
- 尽量选"能被一句话说清"的符号。
- 每个都单独测过 60px 清晰度。
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

SIZE = 1024
SS = 4
W = SIZE * SS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "candidates2")


def finish(img, name):
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    assert out.mode == "RGB"
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, f"{name}.png"), "PNG", optimize=True)
    out.resize((60, 60), Image.LANCZOS).save(os.path.join(OUT, f"{name}-60.png"))
    print(f"  {name}.png")


def soft_shadow(base, cx, cy, w, h, color, blur=0.025):
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=(*color, 200))
    layer = layer.filter(ImageFilter.GaussianBlur(int(W * blur)))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


# ═══════════════════════════════════════════════════════
# 1. INK — 墨黑底 + 亮黄。一个"卡住的硬币"。
# ═══════════════════════════════════════════════════════
def j_ink():
    BG = (24, 24, 26)
    ACCENT = (255, 199, 44)      # 亮黄，警示牌那种黄
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # 一枚硬币以边缘立着，倾斜（像停下了）
    r = int(W * 0.26)
    thick = int(W * 0.085)
    tilt = 18
    coin = Image.new("RGBA", (int(W * 0.9), int(W * 0.9)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(coin)
    cc = coin.size[0] // 2
    cd.ellipse([cc - thick // 2, cc - r, cc + thick // 2, cc + r], fill=(*ACCENT, 255))
    coin = coin.rotate(tilt, resample=Image.BICUBIC, expand=False)
    layer.alpha_composite(coin, ((W - coin.size[0]) // 2, (W - coin.size[1]) // 2))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "J-ink-coin")


# ═══════════════════════════════════════════════════════
# 2. MINT — 薄荷绿 + 奶油白。一个"呼气的泡泡"。
# ═══════════════════════════════════════════════════════
def k_mint():
    BG = (240, 247, 243)
    MINT = (74, 168, 140)
    MINT_D = (56, 137, 113)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W*0.20), int(W*0.40), int(W*0.05), (214, 232, 224))
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # 三个由大到小的圆，向右上散开（呼出的气泡）
    specs = [(0, 0, 0.155), (0.185, -0.155, 0.090), (0.30, -0.275, 0.045)]
    for i, (dx, dy, rr) in enumerate(specs):
        R = int(W * rr)
        x = cx + int(W * dx)
        y = cy + int(W * dy)
        col = MINT if i == 0 else MINT_D
        a = 255 if i == 0 else (200 if i == 1 else 150)
        d.ellipse([x-R, y-R, x+R, y+R], fill=(*col, a))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "K-mint-bubbles")


# ═══════════════════════════════════════════════════════
# 3. INDIGO — 靛蓝 + 浅底。一个"天平"（衡量值不值）。
# ═══════════════════════════════════════════════════════
def l_indigo():
    BG = (244, 246, 251)
    IND = (58, 82, 156)
    IND_L = (108, 132, 200)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W*0.245), int(W*0.42), int(W*0.045), (222, 228, 242))
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    beam_w = int(W * 0.50)
    stroke = int(W * 0.048)
    beam_y = cy - int(W * 0.115)

    # 立柱
    d.rounded_rectangle([cx - stroke//2, beam_y, cx + stroke//2, cy + int(W*0.155)],
                        radius=stroke//2, fill=(*IND, 255))
    # 底座
    base_w = int(W * 0.24)
    d.rounded_rectangle([cx - base_w//2, cy + int(W*0.155) - stroke//2,
                         cx + base_w//2, cy + int(W*0.155) + stroke//2],
                        radius=stroke//2, fill=(*IND, 255))
    # 横梁（略微倾斜，表示失衡）
    beam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.rounded_rectangle([cx - beam_w//2, beam_y - stroke//2,
                          cx + beam_w//2, beam_y + stroke//2],
                         radius=stroke//2, fill=(*IND, 255))
    beam = beam.rotate(-9, resample=Image.BICUBIC, center=(cx, beam_y))
    layer.alpha_composite(beam)

    # 两端吊盘
    pan_r = int(W * 0.085)
    for sign in (-1, 1):
        px = cx + sign * int(beam_w * 0.42)
        py = beam_y + int(W * 0.055) + sign * int(W * 0.022)
        d.line([(px, beam_y), (px, py - pan_r//3)], fill=(*IND, 255), width=int(stroke*0.6))
        d.ellipse([px - pan_r, py - pan_r//2, px + pan_r, py + pan_r//2], fill=(*IND_L, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "L-indigo-scale")


# ═══════════════════════════════════════════════════════
# 4. SAND — 沙陶色 + 深棕。一个"慢下来"的沙漏。
# ═══════════════════════════════════════════════════════
def m_sand():
    BG = (247, 240, 228)
    CLAY = (176, 106, 74)
    SAND_D = (138, 78, 52)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W*0.245), int(W*0.36), int(W*0.045), (226, 212, 192))
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    hw = int(W * 0.175)     # 半宽
    hh = int(W * 0.135)     # 半高
    cap = int(W * 0.030)

    # 上下木盖
    for yy in (cy - hh, cy + hh):
        d.rounded_rectangle([cx - hw - cap//2, yy - cap//2, cx + hw + cap//2, yy + cap//2],
                            radius=cap//2, fill=(*SAND_D, 255))
    # 沙漏主体（两个三角对接）
    body = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.polygon([(cx - hw, cy - hh), (cx + hw, cy - hh), (cx, cy)], fill=(*CLAY, 255))
    bd.polygon([(cx - hw, cy + hh), (cx + hw, cy + hh), (cx, cy)], fill=(*CLAY, 255))
    layer.alpha_composite(body)

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "M-sand-hourglass")


# ═══════════════════════════════════════════════════════
# 5. ORANGE — 饱和橘 + 深棕。一个"被划掉的价签"。
# ═══════════════════════════════════════════════════════
def n_orange():
    BG = (255, 249, 240)
    ORG = (240, 122, 42)
    DARK = (74, 48, 32)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W*0.225), int(W*0.40), int(W*0.045), (240, 226, 208))
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 圆底
    R = int(W * 0.275)
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(*ORG, 255))

    # 一条斜杠穿过（"不买了"）
    sw = int(W * 0.062)
    line = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(line)
    ld.rounded_rectangle([cx - R*1.02, cy - sw//2, cx + R*1.02, cy + sw//2],
                         radius=sw//2, fill=(*DARK, 255))
    line = line.rotate(-42, resample=Image.BICUBIC, center=(cx, cy))
    layer.alpha_composite(line)

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "N-orange-slash")


# ═══════════════════════════════════════════════════════
# 6. PLUM — 深紫 + 粉。"一颗静止的心跳"（平线）。
# ═══════════════════════════════════════════════════════
def o_plum():
    BG = (48, 36, 62)
    PINK = (240, 138, 168)
    PINK_L = (255, 186, 206)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    sw = int(W * 0.058)
    amp = int(W * 0.115)     # 心跳振幅
    span = int(W * 0.33)     # 半宽

    # 一条心跳线（一个尖峰，然后归于平缓）
    pts = [
        (cx - span, cy),
        (cx - int(span*0.42), cy),
        (cx - int(span*0.26), cy - amp),
        (cx - int(span*0.10), cy + amp),
        (cx + int(span*0.06), cy),
        (cx + span, cy),
    ]
    d.line(pts, fill=(*PINK, 255), width=sw, joint="curve")
    # 端点圆角
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0]-sw//2, p[1]-sw//2, p[0]+sw//2, p[1]+sw//2], fill=(*PINK, 255))
    # 尖峰顶点加个小光点
    d.ellipse([cx - int(span*0.26) - sw//2, cy - amp - sw//2,
               cx - int(span*0.26) + sw//2, cy - amp + sw//2], fill=(*PINK_L, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "O-plum-pulse")


# ═══════════════════════════════════════════════════════
# 7. TEAL — 青绿 + 米白。一个"被按住的手势"（一个点 + 一个环）。
# ═══════════════════════════════════════════════════════
def p_teal():
    BG = (250, 248, 243)
    TEAL = (30, 122, 124)
    TEAL_L = (94, 176, 172)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 中心实心点
    R = int(W * 0.115)
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(*TEAL, 255))

    # 两圈外环，间距拉开（像水波，也像"停"）
    for i, (rr, ww, alpha) in enumerate([(0.205, 0.045, 255), (0.285, 0.032, 140)]):
        Ro = int(W * rr)
        sw = int(W * ww)
        d.ellipse([cx-Ro, cy-Ro, cx+Ro, cy+Ro],
                  outline=(*TEAL_L, alpha), width=sw)

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "P-teal-ripple")


# ═══════════════════════════════════════════════════════
# 8. MONO — 纯黑白。一个"话到嘴边收回去"的形状。
# ═══════════════════════════════════════════════════════
def q_mono():
    BG = (252, 252, 252)
    INK = (22, 22, 22)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 一个方框 + 一条从内延伸出去的细线（被截断了）
    bw = int(W * 0.30)
    bh = int(W * 0.23)
    rad = int(W * 0.055)
    sw = int(W * 0.055)
    # 只画左侧和下半（一个"未完成"的框）
    d.rounded_rectangle([cx - bw//2 - sw//2, cy - bh//2 - sw//2,
                         cx + bw//2 + sw//2, cy + bh//2 + sw//2],
                        radius=rad, outline=(*INK, 0), width=0)
    # 用弧线画开口框
    d.arc([cx - bw//2, cy - bh//2, cx + bw//2, cy + bh//2],
          start=35, end=215, fill=(*INK, 255), width=sw)
    d.arc([cx - bw//2, cy - bh//2, cx + bw//2, cy + bh//2],
          start=290, end=325, fill=(*INK, 255), width=sw)

    # 从开口延伸出去、又被切断的线
    d.rounded_rectangle([cx + bw//2 - int(W*0.01), cy - sw//2,
                         cx + bw//2 + int(W*0.135), cy + sw//2],
                        radius=sw//2, fill=(*INK, 255))
    # 一个断点
    dot_r = int(W * 0.022)
    dx = cx + bw//2 + int(W*0.175)
    d.ellipse([dx-dot_r, cy-dot_r, dx+dot_r, cy+dot_r], fill=(*INK, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "Q-mono-open")


SCHEMES = [
    ("J 墨黑+亮黄  立着的硬币",   j_ink),
    ("K 薄荷绿     呼出的气泡",   k_mint),
    ("L 靛蓝       天平",         l_indigo),
    ("M 沙陶       沙漏",         m_sand),
    ("N 饱和橘     划掉的圆",     n_orange),
    ("O 深紫+粉    心跳平线",     o_plum),
    ("P 青绿       水波",         p_teal),
    ("Q 纯黑白     未完成的框",   q_mono),
]


def main():
    print("第二批候选：")
    for name, fn in SCHEMES:
        try:
            fn()
        except Exception as e:
            print(f"  {name} 失败: {e}")
    print(f"\n输出: {OUT}")


if __name__ == "__main__":
    main()
