#!/usr/bin/env python3
"""第四批：以「不」字为主体的图标方案。

为什么用「不」字：
- 品牌名「不烧心」的第一个字，辨识度直接来自产品名。
- 「不」在中文里是最高频的否定词，字形本身有强烈的"阻断"意象：
  一横在上、一撇一竖在下的结构，天然像一个"截断"的符号。
- 中文字做图标的风险是：海外用户看不懂。所以这批里有一半方案
  把字处理成几何/抽象形态，脱离语言也能成立。

技术上：用 NotoSansSC 可变字重的 Black（900），
墨迹覆盖率 28.7%——正好落在 60px 清晰的安全区间。
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

SIZE = 1024
SS = 4
W = SIZE * SS
GLYPH = "不"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "candidates4")

FONT_PATH = "C:/Windows/Fonts/NotoSansSC-VF.ttf"
FONT_WEIGHT = 900


def get_font(size):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_axes([FONT_WEIGHT])
    except Exception:
        pass
    return f


def render_glyph(canvas_size, fill_frac=0.82, color=(0, 0, 0), bold_extra=0):
    """把「不」渲染到 canvas_size 见方的图层上，居中，字形占 fill_frac。

    始终返回 RGBA，方便直接 alpha_composite。
    bold_extra: 额外膨胀像素，用来人工加粗（在超采样空间里算）。
    """
    mask = Image.new("L", (canvas_size, canvas_size), 0)
    d = ImageDraw.Draw(mask)
    fs = int(canvas_size * fill_frac)
    f = get_font(fs)
    bbox = d.textbbox((0, 0), GLYPH, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (canvas_size - tw) / 2 - bbox[0]
    y = (canvas_size - th) / 2 - bbox[1]
    d.text((x, y), GLYPH, fill=255, font=f)

    if bold_extra > 0:
        mask = mask.filter(ImageFilter.MaxFilter(bold_extra * 2 + 1))

    rgba = Image.new("RGBA", (canvas_size, canvas_size), (*color, 0))
    rgba.putalpha(mask)
    return rgba


def finish(img, name):
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    assert out.mode == "RGB" and out.size == (SIZE, SIZE)
    os.makedirs(OUT, exist_ok=True)
    out.save(os.path.join(OUT, f"{name}.png"), "PNG", optimize=True)
    out.resize((60, 60), Image.LANCZOS).save(os.path.join(OUT, f"{name}-60.png"))
    print(f"  {name}.png")
    return out


def blend(base, layer_rgba):
    return Image.alpha_composite(base.convert("RGBA"), layer_rgba).convert("RGB")


def ink_ratio(img):
    """墨迹占比：与四角背景色差异显著的像素比例"""
    a = np.array(img.convert("RGB")).astype(int)
    bg = a[0, 0]
    return (np.abs(a - bg).sum(axis=2) > 45).sum() * 100 / a[:, :, 0].size


# ══════════════════════════════════════════════════════════
# 1. 纯字 —— 米色底 + 墨色「不」。最克制。
# ══════════════════════════════════════════════════════════
def al_1_plain():
    BG = (248, 245, 238)
    INK = (26, 26, 30)
    img = Image.new("RGB", (W, W), BG)
    g = render_glyph(W, 0.74, INK)
    img = blend(img, g)
    return finish(img, "AL-1-plain")


# ══════════════════════════════════════════════════════════
# 2. 反白 —— 珊瑚色满屏 + 米色「不」。最直接。
# ══════════════════════════════════════════════════════════
def al_2_reverse():
    BG = (217, 102, 74)
    FG = (252, 249, 243)
    img = Image.new("RGB", (W, W), BG)
    g = render_glyph(W, 0.74, FG)
    img = blend(img, g)
    return finish(img, "AL-2-reverse")


# ══════════════════════════════════════════════════════════
# 3. 方底 —— 圆角方块内白字。最像"App"的做法。
# ══════════════════════════════════════════════════════════
def al_3_badge():
    BG = (250, 247, 240)
    BOX = (33, 32, 36)
    FG = (250, 247, 240)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # 圆角方
    pad = int(W * 0.135)
    d.rounded_rectangle([pad, pad, W - pad, W - pad],
                        radius=int(W * 0.155), fill=(*BOX, 255))
    img = blend(img, layer)
    # 字压在方上，字号略小
    g = render_glyph(W, 0.56, FG)
    img = blend(img, g)
    return finish(img, "AL-3-badge")


# ══════════════════════════════════════════════════════════
# 4. 竖排横线 —— 字上下各一条规则线，报纸/印章感
# ══════════════════════════════════════════════════════════
def al_4_rules():
    BG = (247, 244, 236)
    INK = (28, 30, 34)
    ACC = (198, 72, 58)
    img = Image.new("RGB", (W, W), BG)
    g = render_glyph(W, 0.62, INK)
    img = blend(img, g)

    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    th = int(W * 0.028)
    lw = int(W * 0.50)
    x0 = (W - lw) // 2
    top = int(W * 0.155)
    bot = int(W * 0.845)
    d.rectangle([x0, top, x0 + lw, top + th], fill=(*INK, 255))
    d.rectangle([x0, bot - th, x0 + lw, bot], fill=(*ACC, 255))
    img = blend(img, layer)
    return finish(img, "AL-4-rules")


# ══════════════════════════════════════════════════════════
# 5. 双色叠加 —— 同一个字偏移重叠，一次墨色一次珊瑚
#    错位感 = "犹豫"的视觉隐喻
# ══════════════════════════════════════════════════════════
def al_5_offset():
    BG = (250, 248, 242)
    A = (217, 102, 74)
    B = (30, 30, 34)
    img = Image.new("RGB", (W, W), BG)

    off = int(W * 0.028)
    g1 = render_glyph(W, 0.70, A)
    # 把红字往左上平移，露出右下角的黑字
    shifted = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    shifted.alpha_composite(g1, (-off, -off))
    img = blend(img, shifted)

    g2 = render_glyph(W, 0.70, B)
    img = blend(img, g2)
    return finish(img, "AL-5-offset")


# ══════════════════════════════════════════════════════════
# 6. 网格切割 —— 字被细线网格切开，像制图/蓝图
# ══════════════════════════════════════════════════════════
def al_6_grid():
    BG = (24, 38, 58)
    FG = (108, 196, 220)
    img = Image.new("RGB", (W, W), BG)
    g = render_glyph(W, 0.72, FG)
    img = blend(img, g)

    # 在字上叠一层暗色网格线
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    n = 5
    th = int(W * 0.016)
    for i in range(1, n):
        p = int(W * i / n)
        d.rectangle([p, 0, p + th, W], fill=(*BG, 230))
        d.rectangle([0, p, W, p + th], fill=(*BG, 230))
    img = blend(img, layer)
    return finish(img, "AL-6-grid")


# ══════════════════════════════════════════════════════════
# 7. 斜切 —— 字被一条斜线切成上下两块，下半反色
# ══════════════════════════════════════════════════════════
def al_7_split():
    BG = (248, 244, 236)
    INK = (26, 28, 32)
    ACC = (214, 96, 70)
    img = Image.new("RGB", (W, W), BG)

    # 上半：黑字
    g = render_glyph(W, 0.74, INK)
    # 生成斜切蒙版
    mask = Image.new("L", (W, W), 0)
    md = ImageDraw.Draw(mask)
    # 从左上到右下，斜线
    tilt = int(W * 0.10)
    md.polygon([(0, 0), (W, 0), (W, W - tilt), (0, tilt)], fill=255)

    upper = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    upper.paste(g, (0, 0), mask)
    img = blend(img, upper)

    # 下半：珊瑚字（在斜线以下）
    g2 = render_glyph(W, 0.74, ACC)
    lower_mask = Image.new("L", (W, W), 255)
    ImageDraw.Draw(lower_mask).polygon(
        [(0, 0), (W, 0), (W, W - tilt), (0, tilt)], fill=0)
    lower = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    lower.paste(g2, (0, 0), lower_mask)
    img = blend(img, lower)
    return finish(img, "AL-7-split")


# ══════════════════════════════════════════════════════════
# 8. 圆内 —— 细圆环包住字，印章/认证感
# ══════════════════════════════════════════════════════════
def al_8_circle():
    BG = (245, 242, 234)
    RING = (196, 66, 52)
    INK = (28, 28, 32)
    img = Image.new("RGB", (W, W), BG)

    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    R = int(W * 0.325)
    sw = int(W * 0.032)
    d.ellipse([W//2 - R, W//2 - R, W//2 + R, W//2 + R],
              outline=(*RING, 255), width=sw)
    img = blend(img, layer)

    g = render_glyph(W, 0.52, INK)
    img = blend(img, g)
    return finish(img, "AL-8-circle")


# ══════════════════════════════════════════════════════════
# 9. 极粗 —— 人工膨胀到极限，字快糊成一个块
#    牺牲可读性换冲击力，适合"品牌感优先"
# ══════════════════════════════════════════════════════════
def al_9_heavy():
    BG = (255, 214, 92)
    INK = (24, 24, 26)
    img = Image.new("RGB", (W, W), BG)
    # bold_extra 在超采样空间里，4x 后相当于 4*extra
    g = render_glyph(W, 0.70, INK, bold_extra=10)
    img = blend(img, g)
    return finish(img, "AL-9-heavy")


# ══════════════════════════════════════════════════════════
# 10. 模糊晕染 —— 字边缘有柔光，像印在纸上渗开
# ══════════════════════════════════════════════════════════
def al_10_soft():
    BG = (250, 246, 238)
    INK = (32, 34, 38)
    img = Image.new("RGB", (W, W), BG)

    # 底层：模糊放大的字（晕染）
    glow = render_glyph(W, 0.74, INK)
    alpha = glow.getchannel("A").filter(ImageFilter.GaussianBlur(int(W * 0.022)))
    alpha = alpha.point(lambda v: int(v * 0.42))
    gimg = Image.new("RGBA", (W, W), (*INK, 0))
    gimg.putalpha(alpha)
    img = blend(img, gimg)

    # 上层：清晰的字
    g = render_glyph(W, 0.74, INK)
    img = blend(img, g)
    return finish(img, "AL-10-soft")


# ══════════════════════════════════════════════════════════
# 11. 字 + 数字 —— 「不」在上，"0" 在下，小尺寸
#     表达"零浪费"，但视觉上仍是字
# ══════════════════════════════════════════════════════════
def al_11_zero():
    BG = (238, 244, 240)
    GREEN = (32, 92, 74)
    img = Image.new("RGB", (W, W), BG)

    g = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    glyph = render_glyph(W, 0.52, GREEN)
    g.alpha_composite(glyph, (0, -int(W * 0.055)))
    img = blend(img, g)

    # 下面一个 "0"（用椭圆环画，不用字体，保证几何干净）
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = int(W * 0.088)
    sw = int(W * 0.030)
    cy = int(W * 0.755)
    d.ellipse([W//2 - r, cy - r, W//2 + r, cy + r],
              outline=(*GREEN, 255), width=sw)
    img = blend(img, layer)
    return finish(img, "AL-11-zero")


# ══════════════════════════════════════════════════════════
# 12. 深底荧光 —— 炭黑底 + 荧光绿字。赛博/极客
# ══════════════════════════════════════════════════════════
def al_12_neon():
    BG = (22, 24, 26)
    FG = (140, 240, 176)
    img = Image.new("RGB", (W, W), BG)

    # 外发光
    glow_alpha = render_glyph(W, 0.70, FG, bold_extra=4).getchannel("A")
    glow_alpha = glow_alpha.filter(ImageFilter.GaussianBlur(int(W * 0.030)))
    gimg = Image.new("RGBA", (W, W), (*FG, 0))
    gimg.putalpha(glow_alpha)
    img = blend(img, gimg)

    g = render_glyph(W, 0.70, FG)
    img = blend(img, g)
    return finish(img, "AL-12-neon")


SCHEMES = [
    ("AL-1  纯字·米底墨字",     al_1_plain),
    ("AL-2  反白·珊瑚满屏",     al_2_reverse),
    ("AL-3  圆角方底",          al_3_badge),
    ("AL-4  上下横线",          al_4_rules),
    ("AL-5  双色错位",          al_5_offset),
    ("AL-6  网格切割",          al_6_grid),
    ("AL-7  斜切双色",          al_7_split),
    ("AL-8  圆环内",            al_8_circle),
    ("AL-9  极粗·黄底黑字",     al_9_heavy),
    ("AL-10 柔光晕染",          al_10_soft),
    ("AL-11 字+零",             al_11_zero),
    ("AL-12 深底荧光",          al_12_neon),
]


def main():
    print("第四批（「不」字系列）：")
    for name, fn in SCHEMES:
        try:
            out = fn()
            print(f"       主体 {ink_ratio(out):.1f}%")
        except Exception as e:
            print(f"  {name} 失败: {e}")
    print(f"\n输出: {OUT}")


if __name__ == "__main__":
    main()
