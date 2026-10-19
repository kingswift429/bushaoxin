#!/usr/bin/env python3
"""批量生成 App 图标候选方案。

每个方案是一个独立函数，输出到 verify/preview/candidates/。
所有方案统一：
- 1024x1024，RGB 无 alpha（Apple 硬性要求）
- 4 倍超采样抗锯齿
- 珊瑚红占比目标 20~35%（低于 15% 远看认不出，高于 40% 变成纯色块）

设计原则：
- 只放一个符号。桌面 60pt 下任何第二个元素都会糊成噪点。
- 不用描边。缩小时描边和填充混合成灰糊。
- 背景满幅。iOS 自己会切圆角，我们不能留白边。
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

SIZE = 1024
SS = 4
W = SIZE * SS

CREAM      = (251, 248, 244)
CREAM_DEEP = (243, 237, 228)
CORAL      = (217, 102, 74)
CORAL_DARK = (196, 86, 60)
CORAL_LIGHT= (232, 138, 112)
CHARCOAL   = (43, 42, 40)
SAGE       = (122, 145, 122)
NAVY       = (58, 74, 92)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "candidates")


def canvas(bg=CREAM):
    return Image.new("RGB", (W, W), bg)


def finish(img, name, bg_note=""):
    """降采样、转 RGB、保存"""
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    assert out.mode == "RGB"
    assert out.size == (SIZE, SIZE)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}.png")
    out.save(p, "PNG", optimize=True)
    out.resize((60, 60), Image.LANCZOS).save(
        os.path.join(OUT, f"{name}-60.png"), "PNG"
    )
    print(f"  {name}.png {bg_note}")
    return p


def paste_rotated(base, layer, cx, cy, tilt):
    """把图层绕自身中心旋转后，贴到 base 的 (cx, cy)"""
    r = layer.rotate(tilt, resample=Image.BICUBIC, expand=True)
    b = base.convert("RGBA")
    b.alpha_composite(r, (int(cx - r.size[0] / 2), int(cy - r.size[1] / 2)))
    return b.convert("RGB")


def soft_shadow(base, cx, cy, w, h, color, blur_frac=0.02):
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=(*color, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(int(W * blur_frac)))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


# ─────────────────────────────────────────────────────
# A. 购物袋（当前版本）
# ─────────────────────────────────────────────────────
def scheme_a_bag():
    img = canvas()
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W * 0.20), int(W * 0.44), int(W * 0.05), CREAM_DEEP)

    bag_w, bag_h = int(W * 0.52), int(W * 0.42)
    radius = int(W * 0.058)
    handle_w, handle_h = int(W * 0.27), int(W * 0.19)
    stroke = int(W * 0.055)

    pad = int(W * 0.10)
    lw = max(bag_w, handle_w) + pad * 2
    lh = bag_h + handle_h + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    lcx = lw // 2
    top = pad + handle_h
    d.arc([lcx - handle_w // 2, top - handle_h, lcx + handle_w // 2, top + handle_h],
          start=188, end=352, fill=(*CORAL_DARK, 255), width=stroke)
    d.rounded_rectangle([lcx - bag_w // 2, top, lcx + bag_w // 2, top + bag_h],
                        radius=radius, fill=(*CORAL, 255))
    dot_r = int(W * 0.040)
    d.ellipse([lcx - dot_r, top + bag_h // 2 - dot_r + int(W * 0.015),
               lcx + dot_r, top + bag_h // 2 + dot_r + int(W * 0.015)],
              fill=(*CREAM, 255))

    img = paste_rotated(img, layer, cx, cy + int(W * 0.02), -8)
    return finish(img, "A-bag")


# ─────────────────────────────────────────────────────
# B. 价格标签（服装吊牌）
# ─────────────────────────────────────────────────────
def scheme_b_tag():
    img = canvas()
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W * 0.22), int(W * 0.40), int(W * 0.045), CREAM_DEEP)

    tw, th = int(W * 0.54), int(W * 0.40)
    cut = int(W * 0.10)          # 左上角切角大小
    radius = int(W * 0.035)
    hole_r = int(W * 0.030)

    pad = int(W * 0.08)
    lw, lh = tw + pad * 2, th + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 带切角的圆角矩形（吊牌）
    x0, y0 = pad, pad
    x1, y1 = pad + tw, pad + th
    pts = [
        (x0 + cut, y0), (x1 - radius, y0), (x1, y0 + radius),
        (x1, y1 - radius), (x1 - radius, y1),
        (x0 + radius, y1), (x0, y1 - radius),
        (x0, y0 + cut),
    ]
    d.polygon(pts, fill=(*CORAL, 255))
    d.rounded_rectangle([x0, y0 + cut - radius, x0 + tw, y1], radius=radius, fill=(*CORAL, 255))
    # 再切掉左上角（用背景色盖）
    d.polygon([(x0 - 2, y0 - 2), (x0 + cut + radius, y0 - 2), (x0 - 2, y0 + cut + radius)],
              fill=(0, 0, 0, 0))

    # 穿绳孔
    hx, hy = x0 + cut * 0.62, y0 + cut * 0.62
    d.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r], fill=(0, 0, 0, 0))

    # 两条装饰横线（模拟价格占位）
    bar_w = int(tw * 0.46)
    bar_h = int(W * 0.026)
    bx = x0 + int(tw * 0.28)
    for i, yy in enumerate([y0 + int(th * 0.46), y0 + int(th * 0.46) + bar_h * 3]):
        d.rounded_rectangle([bx, yy, bx + bar_w, yy + bar_h],
                            radius=bar_h // 2, fill=(*CREAM, 255))

    img = paste_rotated(img, layer, cx, cy, 12)
    return finish(img, "B-tag")


# ─────────────────────────────────────────────────────
# C. 水滴 / 静止的水面
# ─────────────────────────────────────────────────────
def scheme_c_drop():
    img = canvas()
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W * 0.24), int(W * 0.34), int(W * 0.045), CREAM_DEEP)

    pad = int(W * 0.06)
    lw = int(W * 0.62)
    layer = Image.new("RGBA", (lw, lw), (0, 0, 0, 0))

    # 水滴：上方一个尖角 + 下方一个圆
    r = int(lw * 0.30)
    ccx = lw // 2
    ccy = lw // 2 + int(lw * 0.08)
    d = ImageDraw.Draw(layer)

    # 圆身
    d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=(*CORAL, 255))
    # 上方三角
    tip_h = int(lw * 0.34)
    d.polygon([
        (ccx, ccy - r - tip_h),
        (ccx - r * 0.80, ccy - r * 0.30),
        (ccx + r * 0.80, ccy - r * 0.30),
    ], fill=(*CORAL, 255))
    # 水滴里的高光（一个月牙）
    hr = int(r * 0.42)
    d.ellipse([ccx - hr - int(r * 0.16), ccy - hr - int(r * 0.16),
               ccx + hr - int(r * 0.16), ccy + hr - int(r * 0.16)],
              fill=(*CORAL_LIGHT, 255))
    d.ellipse([ccx - hr - int(r * 0.16) + hr // 2, ccy - hr - int(r * 0.16) + hr // 2,
               ccx + hr - int(r * 0.16) + hr // 2, ccy + hr - int(r * 0.16) + hr // 2],
              fill=(*CORAL, 255))

    img = paste_rotated(img, layer, cx, cy, 0)
    return finish(img, "C-drop")


# ─────────────────────────────────────────────────────
# D. 圆形徽章 + 横杠（"暂停"的最简表达）
# ─────────────────────────────────────────────────────
def scheme_d_pause():
    img = canvas()
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W * 0.23), int(W * 0.38), int(W * 0.045), CREAM_DEEP)

    R = int(W * 0.27)
    # 外圆环
    ring = int(W * 0.070)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(*CORAL, 255), width=ring)

    # 中间两条竖杠（暂停符）
    bar_w = int(W * 0.055)
    bar_h = int(W * 0.22)
    gap = int(W * 0.055)
    for sign in (-1, 1):
        bx = cx + sign * gap // 2 - (bar_w // 2 if sign < 0 else -bar_w // 2 + bar_w)
        bx = cx + sign * (gap // 2 + bar_w // 2) - bar_w // 2
        d.rounded_rectangle([bx, cy - bar_h // 2, bx + bar_w, cy + bar_h // 2],
                            radius=bar_w // 2, fill=(*CORAL, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "D-pause")


# ─────────────────────────────────────────────────────
# E. 硬币堆 + 一点点下沉（"钱还在"）
# ─────────────────────────────────────────────────────
def scheme_e_coins():
    img = canvas()
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W * 0.24), int(W * 0.44), int(W * 0.045), CREAM_DEEP)

    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    ew = int(W * 0.42)       # 椭圆宽
    eh = int(W * 0.115)      # 椭圆高
    thickness = int(W * 0.058)
    base_y = cy + int(W * 0.10)
    n = 3

    for i in range(n):
        y = base_y - i * thickness
        # 硬币侧面
        d.rounded_rectangle(
            [cx - ew // 2, y - thickness, cx + ew // 2, y + eh // 2],
            radius=eh // 2, fill=(*CORAL_DARK, 255)
        )
        # 硬币顶面
        color = CORAL if i % 2 == 0 else CORAL_LIGHT
        d.ellipse([cx - ew // 2, y - eh // 2, cx + ew // 2, y + eh // 2],
                  fill=(*color, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "E-coins")


# ─────────────────────────────────────────────────────
# F. 购物袋 + 向下箭头（"先放下"）
# ─────────────────────────────────────────────────────
def scheme_f_bag_arrow():
    img = canvas()
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W * 0.22), int(W * 0.42), int(W * 0.045), CREAM_DEEP)

    bag_w, bag_h = int(W * 0.46), int(W * 0.36)
    radius = int(W * 0.052)
    handle_w, handle_h = int(W * 0.24), int(W * 0.16)
    stroke = int(W * 0.048)

    pad = int(W * 0.09)
    lw = max(bag_w, handle_w) + pad * 2
    lh = bag_h + handle_h + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lcx = lw // 2
    top = pad + handle_h

    d.arc([lcx - handle_w // 2, top - handle_h, lcx + handle_w // 2, top + handle_h],
          start=188, end=352, fill=(*CORAL_DARK, 255), width=stroke)
    d.rounded_rectangle([lcx - bag_w // 2, top, lcx + bag_w // 2, top + bag_h],
                        radius=radius, fill=(*CORAL, 255))

    # 中间一个向下的箭头（挖空）
    aw = int(W * 0.11)
    ah = int(W * 0.13)
    acx = lcx
    acy = top + bag_h // 2
    shaft_w = int(aw * 0.42)
    d.rounded_rectangle([acx - shaft_w // 2, acy - ah // 2,
                         acx + shaft_w // 2, acy + ah * 0.10],
                        radius=shaft_w // 3, fill=(*CREAM, 255))
    d.polygon([(acx - aw // 2, acy + ah * 0.05),
               (acx + aw // 2, acy + ah * 0.05),
               (acx, acy + ah * 0.52)], fill=(*CREAM, 255))

    img = paste_rotated(img, layer, cx, cy + int(W * 0.01), -6)
    return finish(img, "F-bag-arrow")


# ─────────────────────────────────────────────────────
# G. 深色底 + 珊瑚红（夜间模式感）
# ─────────────────────────────────────────────────────
def scheme_g_dark():
    img = canvas(CHARCOAL)
    cx = cy = W // 2

    bag_w, bag_h = int(W * 0.54), int(W * 0.44)
    radius = int(W * 0.060)
    handle_w, handle_h = int(W * 0.28), int(W * 0.20)
    stroke = int(W * 0.058)

    pad = int(W * 0.10)
    lw = max(bag_w, handle_w) + pad * 2
    lh = bag_h + handle_h + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lcx = lw // 2
    top = pad + handle_h

    d.arc([lcx - handle_w // 2, top - handle_h, lcx + handle_w // 2, top + handle_h],
          start=188, end=352, fill=(*CORAL, 255), width=stroke)
    d.rounded_rectangle([lcx - bag_w // 2, top, lcx + bag_w // 2, top + bag_h],
                        radius=radius, fill=(*CORAL, 255))
    dot_r = int(W * 0.042)
    d.ellipse([lcx - dot_r, top + bag_h // 2 - dot_r + int(W * 0.015),
               lcx + dot_r, top + bag_h // 2 + dot_r + int(W * 0.015)],
              fill=(*CHARCOAL, 255))

    img = paste_rotated(img, layer, cx, cy + int(W * 0.02), -8)
    return finish(img, "G-dark")


# ─────────────────────────────────────────────────────
# H. 极简：只有一个"停顿点"
# ─────────────────────────────────────────────────────
def scheme_h_minimal():
    img = canvas()
    cx = cy = W // 2

    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 一个大圆（珊瑚红）+ 一个缺口（用背景色挖掉）
    R = int(W * 0.30)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(*CORAL, 255))

    # 挖掉右侧一块 -> 变成一个 "C" 形，像暂停的手势
    cut_cx = cx + int(W * 0.115)
    cut_cy = cy - int(W * 0.155)
    cut_r = int(W * 0.245)
    d.ellipse([cut_cx - cut_r, cut_cy - cut_r,
               cut_cx + cut_r, cut_cy + cut_r], fill=(0, 0, 0, 0))

    # 中心一个米色小圆
    dr = int(W * 0.072)
    d.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill=(*CREAM, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "H-minimal")


# ─────────────────────────────────────────────────────
# I. 价格标签 + 打勾（"决定好了"）
# ─────────────────────────────────────────────────────
def scheme_i_tag_check():
    img = canvas()
    cx = cy = W // 2
    img = soft_shadow(img, cx, cy + int(W * 0.23), int(W * 0.38), int(W * 0.045), CREAM_DEEP)

    R = int(W * 0.30)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 圆形底板
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(*CORAL, 255))

    # 白色对勾
    lw_ = int(W * 0.062)
    d.line([(cx - int(W * 0.13), cy + int(W * 0.01)),
            (cx - int(W * 0.02), cy + int(W * 0.12))],
           fill=(*CREAM, 255), width=lw_, joint="curve")
    d.line([(cx - int(W * 0.02), cy + int(W * 0.12)),
            (cx + int(W * 0.15), cy - int(W * 0.11))],
           fill=(*CREAM, 255), width=lw_, joint="curve")

    # 圆形端点，让勾的转角圆润
    for pt in [(cx - int(W * 0.13), cy + int(W * 0.01)),
               (cx + int(W * 0.15), cy - int(W * 0.11)),
               (cx - int(W * 0.02), cy + int(W * 0.12))]:
        d.ellipse([pt[0] - lw_ // 2, pt[1] - lw_ // 2,
                   pt[0] + lw_ // 2, pt[1] + lw_ // 2], fill=(*CREAM, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "I-check")


SCHEMES = [
    ("A-bag        购物袋（当前）",       scheme_a_bag),
    ("B-tag        价格吊牌",             scheme_b_tag),
    ("C-drop       水滴",                 scheme_c_drop),
    ("D-pause      圆形暂停符",           scheme_d_pause),
    ("E-coins      硬币堆",               scheme_e_coins),
    ("F-bag-arrow  袋子+向下箭头",        scheme_f_bag_arrow),
    ("G-dark       深色底珊瑚红",         scheme_g_dark),
    ("H-minimal    极简C形",              scheme_h_minimal),
    ("I-check      圆底对勾",             scheme_i_tag_check),
]


def main():
    print("生成候选图标：")
    for name, fn in SCHEMES:
        try:
            fn()
        except Exception as e:
            print(f"  {name} 失败: {e}")
    print(f"\n输出目录: {OUT}")


if __name__ == "__main__":
    main()
