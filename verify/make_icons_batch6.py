#!/usr/bin/env python3
"""第六批：种子 / 发芽 / 生长 系列。

为什么这条线值得做：
- 它有一个"时间轴"：种子 -> 芽 -> 苗 -> 树。图标只是起点，
  品牌视觉可以顺着这条线一路展开（启动页、成就、年度报告都用得上）。
- 语义有两层：少买东西 = 钱留下了 = 会长大。
  这是唯一一个把"省"表达成"增值"而不是"失去"的方向。
- 全球通用：种子和树在任何文化里都是正面的。

几何上必须解决的问题：植物的自然形态是细长、分叉、不对称的，
而细线在 60px 下会消失。所有方案都要靠**粗茎**才站得住。
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

SIZE = 1024
SS = 4
W = SIZE * SS
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "candidates6")


def finish(img, name):
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    assert out.mode == "RGB" and out.size == (SIZE, SIZE)
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, f"{name}.png"), "PNG", optimize=True)
    out.resize((60, 60), Image.LANCZOS).save(os.path.join(OUT, f"{name}-60.png"))
    print(f"  {name}.png")
    return out


def blend(base, layer):
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


def leaf(d, x, y, length, width, angle, color, alpha=255):
    """画一片叶子：一个尖椭圆，绕 (x,y) 旋转 angle 度。
    叶子指向外边，根部在 (x,y)。"""
    box_w = int(length)
    box_h = int(width)
    pad = int(max(length, width))
    tmp = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.ellipse([pad - box_w // 2, pad - box_h // 2, pad + box_w // 2, pad + box_h // 2],
               fill=(*color, alpha))
    # 叶子要一头尖：用三角补在两端
    tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=False)
    d._image.paste(tmp, (x - pad, y - pad), tmp)


# ══════════════════════════════════════════════════════════
# 1. 一颗种子 + 一条根 —— 最克制
# ══════════════════════════════════════════════════════════
def seed_only():
    BG = (250, 246, 238)
    SEED = (96, 72, 52)
    ROOT = (196, 118, 86)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2 - int(W * 0.03)
    # 种子：水滴形，头朝上
    rw = int(W * 0.175)     # 半宽
    rh = int(W * 0.215)     # 半高

    # 下半圆
    d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(*SEED, 255))
    # 上尖
    d.polygon([(cx - rw * 0.92, cy - rh * 0.28),
               (cx + rw * 0.92, cy - rh * 0.28),
               (cx, cy - rh * 1.95)], fill=(*SEED, 255))

    # 一道浅色的中缝（种子的接缝）
    d.line([(cx, cy - rh * 1.2), (cx, cy + rh * 0.75)],
           fill=(*BG, 150), width=int(W * 0.020))

    # 下方一条短根
    d.rounded_rectangle([cx - int(W*0.028), cy + rh * 0.85,
                         cx + int(W*0.028), cy + rh * 0.85 + int(W*0.10)],
                        radius=int(W*0.028), fill=(*ROOT, 255))

    img = blend(img, layer)
    return finish(img, "S1-seed")


# ══════════════════════════════════════════════════════════
# 2. 发芽 —— 一颗种子，上面冒出一片粗叶
# ══════════════════════════════════════════════════════════
def sprout():
    BG = (249, 246, 238)
    SEED = (92, 68, 48)
    STEM = (76, 142, 92)
    LEAF = (110, 176, 110)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    seed_y = int(W * 0.695)

    # 茎（粗，从种子往上）
    sw = int(W * 0.072)
    stem_top = int(W * 0.395)
    d.rounded_rectangle([cx - sw//2, stem_top, cx + sw//2, seed_y],
                        radius=sw//2, fill=(*STEM, 255))

    # 左右各一片叶子（宽椭圆，斜向上）
    for sign in (-1, 1):
        lw = int(W * 0.215)     # 叶长
        lh = int(W * 0.115)     # 叶宽
        lx = cx + sign * int(W * 0.030)
        ly = stem_top + int(W * 0.045)
        tmp = Image.new("RGBA", (lw * 2, lw * 2), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        c = lw
        td.ellipse([c, c - lh//2, c + lw, c + lh//2], fill=(*LEAF, 255))
        # 叶片尖端
        td.polygon([(c + lw - int(lw*0.12), c - lh//2), (c + lw - int(lw*0.12), c + lh//2),
                    (c + lw + int(lw*0.22), c)], fill=(*LEAF, 255))
        ang = -32 if sign > 0 else 180 + 32
        tmp = tmp.rotate(ang, resample=Image.BICUBIC, expand=False)
        layer.alpha_composite(tmp, (lx - lw, ly - lw))

    # 种子（在下方，露出上半）
    rw, rh = int(W * 0.135), int(W * 0.165)
    d.ellipse([cx - rw, seed_y, cx + rw, seed_y + rh * 2], fill=(*SEED, 255))
    d.polygon([(cx - rw * 0.93, seed_y + rh * 0.45), (cx + rw * 0.93, seed_y + rh * 0.45),
               (cx, seed_y - rh * 0.55)], fill=(*SEED, 255))

    img = blend(img, layer)
    return finish(img, "S2-sprout")


# ══════════════════════════════════════════════════════════
# 3. 两片叶子 —— 没有种子，只有对称的双叶（最简洁的"生长"）
# ══════════════════════════════════════════════════════════
def two_leaves():
    BG = (247, 245, 237)
    STEM = (58, 122, 88)
    LEAF_A = (94, 166, 112)
    LEAF_B = (72, 144, 100)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    bottom = int(W * 0.775)
    sw = int(W * 0.068)

    # 茎
    d.rounded_rectangle([cx - sw//2, int(W*0.445), cx + sw//2, bottom],
                        radius=sw//2, fill=(*STEM, 255))

    # 两片大叶子（左右对称，像刚出土）
    lw = int(W * 0.255)
    lh = int(W * 0.140)
    for sign, col, ang in ((-1, LEAF_B, 195), (1, LEAF_A, -15)):
        tmp = Image.new("RGBA", (lw * 2, lw * 2), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        c = lw
        td.ellipse([c, c - lh//2, c + lw, c + lh//2], fill=(*col, 255))
        td.polygon([(c + lw - int(lw*0.10), c - lh//2), (c + lw - int(lw*0.10), c + lh//2),
                    (c + lw + int(lw*0.26), c)], fill=(*col, 255))
        tmp = tmp.rotate(ang, resample=Image.BICUBIC, expand=False)
        layer.alpha_composite(tmp, (cx - lw, int(W * 0.445) - lw + int(W*0.052)))

    img = blend(img, layer)
    return finish(img, "S3-two-leaves")


# ══════════════════════════════════════════════════════════
# 4. 幼苗 —— 茎 + 三片叶，有层次
# ══════════════════════════════════════════════════════════
def seedling():
    BG = (250, 247, 240)
    STEM = (52, 112, 78)
    L1 = (86, 158, 106)
    L2 = (116, 184, 126)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    bottom = int(W * 0.80)
    sw = int(W * 0.078)

    d.rounded_rectangle([cx - sw//2, int(W*0.315), cx + sw//2, bottom],
                        radius=sw//2, fill=(*STEM, 255))

    def put_leaf(lx, ly, length, width, angle, col):
        pad = length * 2
        tmp = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        c = pad // 2
        td.ellipse([c - width//2, c - length//2, c + width//2, c + length//2],
                   fill=(*col, 255))
        td.polygon([(c - width//2, c), (c + width//2, c), (c, c - length//2 - int(length*0.30))],
                   fill=(*col, 255))
        tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=False)
        layer.alpha_composite(tmp, (lx - c, ly - c))

    # 顶部一片（小）
    put_leaf(cx, int(W * 0.295), int(W * 0.215), int(W * 0.120), 0, L2)
    # 左右两片
    put_leaf(cx - int(W * 0.115), int(W * 0.415), int(W * 0.235), int(W * 0.135), -62, L1)
    put_leaf(cx + int(W * 0.115), int(W * 0.415), int(W * 0.235), int(W * 0.135), 62, L1)

    # 土（一条弧）
    d.ellipse([cx - int(W*0.30), bottom - int(W*0.048),
               cx + int(W*0.30), bottom + int(W*0.062)],
              outline=(*STEM, 255), width=int(W*0.030))

    img = blend(img, layer)
    return finish(img, "S4-seedling")


# ══════════════════════════════════════════════════════════
# 5. 一棵简化的树 —— 圆冠 + 树干，最经典
# ══════════════════════════════════════════════════════════
def tree_simple():
    BG = (248, 245, 236)
    TRUNK = (120, 88, 60)
    CROWN = (82, 156, 104)
    CROWN2 = (104, 176, 120)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    bottom = int(W * 0.795)

    # 树干
    tw = int(W * 0.098)
    d.rounded_rectangle([cx - tw//2, int(W*0.475), cx + tw//2, bottom],
                        radius=int(tw*0.30), fill=(*TRUNK, 255))

    # 冠：三个圆叠
    R = int(W * 0.205)
    cyc = int(W * 0.365)
    d.ellipse([cx - R, cyc - R, cx + R, cyc + R], fill=(*CROWN, 255))
    r2 = int(R * 0.68)
    d.ellipse([cx - R*0.92 - r2, cyc + int(R*0.28) - r2,
               cx - R*0.92 + r2, cyc + int(R*0.28) + r2], fill=(*CROWN2, 255))
    d.ellipse([cx + R*0.92 - r2, cyc + int(R*0.28) - r2,
               cx + R*0.92 + r2, cyc + int(R*0.28) + r2], fill=(*CROWN2, 255))

    img = blend(img, layer)
    return finish(img, "S5-tree")


# ══════════════════════════════════════════════════════════
# 6. 年轮 —— 三个同心圆环 + 中心一点
#    抽象，但"时间"和"生长"都在里面
# ══════════════════════════════════════════════════════════
def rings():
    BG = (250, 246, 236)
    A = (196, 122, 78)
    B = (222, 158, 108)
    C = (236, 190, 148)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = cy = W // 2
    for R, sw, col in [(0.335, 0.085, A), (0.225, 0.072, B), (0.125, 0.062, C)]:
        Rr = int(W * R)
        d.ellipse([cx-Rr, cy-Rr, cx+Rr, cy+Rr], outline=(*col, 255), width=int(W*sw))
    # 中心点
    dr = int(W * 0.042)
    d.ellipse([cx-dr, cy-dr, cx+dr, cy+dr], fill=(*A, 255))

    img = blend(img, layer)
    return finish(img, "S6-rings")


# ══════════════════════════════════════════════════════════
# 7. 种子长成一条上升的线 —— 抽象的生长曲线
# ══════════════════════════════════════════════════════════
def growth_curve():
    BG = (245, 246, 240)
    ACC = (62, 132, 92)
    DOT = (232, 148, 76)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 一条 S 形曲线，从左下升到右上
    pts = []
    steps = 160
    for k in range(steps + 1):
        t = k / steps
        x = int(W * (0.165 + 0.67 * t))
        # 先平后陡再平
        y = int(W * (0.755 - 0.44 * (t ** 1.7)))
        pts.append((x, y))
    sw = int(W * 0.088)
    d.line(pts, fill=(*ACC, 255), width=sw, joint="curve")
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0]-sw//2, p[1]-sw//2, p[0]+sw//2, p[1]+sw//2], fill=(*ACC, 255))

    # 起点一颗种子圆点（橙色，强调"开始"）
    sr = int(W * 0.085)
    p0 = pts[0]
    d.ellipse([p0[0]-sr, p0[1]-sr, p0[0]+sr, p0[1]+sr], fill=(*DOT, 255))

    img = blend(img, layer)
    return finish(img, "S7-growth")


# ══════════════════════════════════════════════════════════
# 8. 花苞 —— 一颗水滴状的苞，中间一条缝，快开了
# ══════════════════════════════════════════════════════════
def bud():
    BG = (252, 248, 244)
    OUT = (214, 108, 130)
    IN = (176, 72, 100)
    STEM = (74, 132, 92)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    bottom = int(W * 0.80)
    sw = int(W * 0.062)

    # 茎
    d.rounded_rectangle([cx - sw//2, int(W*0.545), cx + sw//2, bottom],
                        radius=sw//2, fill=(*STEM, 255))

    # 花苞：水滴朝上
    rw = int(W * 0.185)
    rh = int(W * 0.215)
    byc = int(W * 0.445)
    d.ellipse([cx - rw, byc - rh, cx + rw, byc + rh], fill=(*OUT, 255))
    d.polygon([(cx - rw * 0.90, byc - rh * 0.32),
               (cx + rw * 0.90, byc - rh * 0.32),
               (cx, byc - rh * 1.75)], fill=(*OUT, 255))

    # 中缝（深色），表示"还没开"
    d.line([(cx, byc - rh * 1.15), (cx, byc + rh * 0.55)],
           fill=(*IN, 255), width=int(W * 0.030))

    # 花萼（底部两片小叶）
    for sign in (-1, 1):
        pad = int(W * 0.30)
        tmp = Image.new("RGBA", (pad*2, pad*2), (0,0,0,0))
        td = ImageDraw.Draw(tmp)
        c = pad
        td.ellipse([c, c - int(W*0.045), c + int(W*0.14), c + int(W*0.045)],
                   fill=(*STEM, 255))
        tmp = tmp.rotate(-28 if sign > 0 else 208, resample=Image.BICUBIC, expand=False)
        layer.alpha_composite(tmp, (cx - c, byc + rh - int(W*0.045) - c))

    img = blend(img, layer)
    return finish(img, "S8-bud")


# ══════════════════════════════════════════════════════════
# 9. 收割/收藏 —— 一个圆 + 从中长出的一根茎（"留了一颗"）
# ══════════════════════════════════════════════════════════
def keep_one():
    BG = (247, 244, 250)
    BOX = (110, 78, 164)
    STEM = (86, 160, 110)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2

    # 圆（容器）
    R = int(W * 0.255)
    cyc = int(W * 0.585)
    d.ellipse([cx - R, cyc - R, cx + R, cyc + R], fill=(*BOX, 255))

    # 从圆顶长出的茎
    sw = int(W * 0.062)
    top = int(W * 0.235)
    d.rounded_rectangle([cx - sw//2, top, cx + sw//2, cyc - int(R*0.72)],
                        radius=sw//2, fill=(*STEM, 255))

    # 顶部一片叶
    pad = int(W * 0.60)
    tmp = Image.new("RGBA", (pad, pad), (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    c = pad // 2
    lw, lh = int(W*0.175), int(W*0.100)
    td.ellipse([c - lw, c - lh//2, c, c + lh//2], fill=(*STEM, 255))
    td.polygon([(c - lw + int(lw*0.10), c - lh//2), (c - lw + int(lw*0.10), c + lh//2),
                (c - lw - int(lw*0.22), c)], fill=(*STEM, 255))
    tmp = tmp.rotate(18, resample=Image.BICUBIC, expand=False)
    layer.alpha_composite(tmp, (cx - c, top - c))

    img = blend(img, layer)
    return finish(img, "S9-keep-one")


# ══════════════════════════════════════════════════════════
# 10. 发芽 + 深绿底（夜/高级感版本）
# ══════════════════════════════════════════════════════════
def sprout_dark():
    BG = (22, 44, 38)
    STEM = (232, 240, 226)
    LEAF = (126, 208, 158)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    sw = int(W * 0.085)
    stem_top = int(W * 0.375)
    bottom = int(W * 0.755)

    d.rounded_rectangle([cx - sw//2, stem_top, cx + sw//2, bottom],
                        radius=sw//2, fill=(*STEM, 255))

    # 两片对称大叶
    for sign, ang in ((-1, 205), (1, -25)):
        pad = int(W * 0.62)
        tmp = Image.new("RGBA", (pad, pad), (0,0,0,0))
        td = ImageDraw.Draw(tmp)
        c = pad // 2
        lw, lh = int(W*0.235), int(W*0.130)
        td.ellipse([c, c - lh//2, c + lw, c + lh//2], fill=(*LEAF, 255))
        td.polygon([(c + lw - int(lw*0.10), c - lh//2), (c + lw - int(lw*0.10), c + lh//2),
                    (c + lw + int(lw*0.24), c)], fill=(*LEAF, 255))
        tmp = tmp.rotate(ang, resample=Image.BICUBIC, expand=False)
        layer.alpha_composite(tmp, (cx - c, stem_top - c + int(W*0.035)))

    img = blend(img, layer)
    return finish(img, "S10-sprout-dark")


# ══════════════════════════════════════════════════════════
# 11. 月牙形的芽 —— 只用一条粗弧线，最抽象
# ══════════════════════════════════════════════════════════
def arc_sprout():
    BG = (33, 36, 42)
    A = (250, 214, 122)
    B = (126, 200, 152)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    R = int(W * 0.265)
    sw = int(W * 0.125)

    # 外弧（黄色）
    d.arc([cx-R, cy-R, cx+R, cy+R], start=200, end=340, fill=(*A, 255), width=sw)
    # 内弧（绿色），短一些
    r2 = int(R * 0.62)
    d.arc([cx-r2, cy-r2 + int(W*0.02), cx+r2, cy+r2 + int(W*0.02)],
          start=205, end=335, fill=(*B, 255), width=int(sw*0.82))

    # 两个圆头收尾
    import math as _m
    for ang, rad, col, wdt in [(200, R, A, sw), (340, R, A, sw)]:
        a = _m.radians(ang)
        px = cx + rad * _m.cos(a); py = cy + rad * _m.sin(a)
        d.ellipse([px-wdt//2, py-wdt//2, px+wdt//2, py+wdt//2], fill=(*col, 255))

    img = blend(img, layer)
    return finish(img, "S11-arc")


# ══════════════════════════════════════════════════════════
# 12. 一颗种子在正中间，光从上方照下（"它在等"）
# ══════════════════════════════════════════════════════════
def seed_glow():
    BG = (28, 30, 34)
    SEED = (240, 216, 168)
    GLOW = (255, 226, 150)
    img = Image.new("RGB", (W, W), BG)

    # 背景径向发光
    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    steps = 40
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(W * 0.52 * t)
        a = int(70 * (1 - t) ** 2)
        gd.ellipse([W//2 - r, W//2 - r - int(W*0.06), W//2 + r, W//2 + r - int(W*0.06)],
                   fill=(*GLOW, a))
    img = blend(img, glow)

    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, W // 2
    rw, rh = int(W * 0.150), int(W * 0.185)
    d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(*SEED, 255))
    d.polygon([(cx - rw*0.92, cy - rh*0.30), (cx + rw*0.92, cy - rh*0.30),
               (cx, cy - rh*1.90)], fill=(*SEED, 255))
    # 中缝
    d.line([(cx, cy - rh*1.15), (cx, cy + rh*0.70)], fill=(*BG, 120), width=int(W*0.018))

    img = blend(img, layer)
    return finish(img, "S12-seed-glow")


SCHEMES = [
    ("S1  一颗种子",        seed_only),
    ("S2  发芽",            sprout),
    ("S3  双叶",            two_leaves),
    ("S4  幼苗",            seedling),
    ("S5  树",              tree_simple),
    ("S6  年轮",            rings),
    ("S7  生长曲线",        growth_curve),
    ("S8  花苞",            bud),
    ("S9  留一颗",          keep_one),
    ("S10 发芽·深绿底",     sprout_dark),
    ("S11 弧线芽",          arc_sprout),
    ("S12 种子·发光",       seed_glow),
]


def main():
    print("第六批（种子/发芽/生长）：")
    for name, fn in SCHEMES:
        try:
            fn()
        except Exception as e:
            print(f"  {name} 失败: {type(e).__name__}: {e}")
    print(f"\n输出: {OUT}")


if __name__ == "__main__":
    main()
