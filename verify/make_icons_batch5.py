#!/usr/bin/env python3
"""第五批：跨语言 logo 方案。

设计前提（和之前四批的区别）：
- 市场：中国 + 海外都要 => 不能用汉字，也不能只靠单个拉丁字母
- 语义必须能用一句话说清（图标是符号，不是插画）
- 60px 下必须认得出

选定的核心隐喻：**"存起来"**。
一层符号同时承载三个意思，这是好标志的特征：
  1. 暂停     —— 先不拆开、先不用
  2. 存钱     —— 钱留下来了
  3. 包裹     —— 想买的东西被搁置

在这个隐喻下做形状变体，而不是换一堆无关的符号。
配色也不再局限珊瑚红：每套给定一个独立色彩主张。
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

SIZE = 1024
SS = 4
W = SIZE * SS
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "candidates5")


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


def rr(d, box, radius, fill, alpha=255):
    d.rounded_rectangle(box, radius=radius, fill=(*fill, alpha))


# ══════════════════════════════════════════════════════════
# 1. 盒子 —— 等距视角的包裹，顶部开着一条缝
#    意思：东西在里面，但还没打开
# ══════════════════════════════════════════════════════════
def box_gap():
    BG = (249, 245, 238)
    A = (226, 108, 78)      # 正面
    B = (196, 84, 58)       # 侧面（暗）
    C = (245, 160, 130)     # 顶面（亮）
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    hw = int(W * 0.245)     # 半宽
    th = int(W * 0.115)     # 顶面高度
    bh = int(W * 0.245)     # 侧身高

    # 顶面（菱形）
    top = [(cx, cy - th - bh // 2), (cx + hw, cy - bh // 2),
           (cx, cy + th - bh // 2), (cx - hw, cy - bh // 2)]
    # 正面
    front = [top[3], top[2], (cx, cy + th - bh // 2 + bh), (cx - hw, cy - bh // 2 + bh)]
    # 侧面
    side = [top[2], top[1], (cx + hw, cy - bh // 2 + bh), (cx, cy + th - bh // 2 + bh)]

    d.polygon(side, fill=(*B, 255))
    d.polygon(front, fill=(*A, 255))
    d.polygon(top, fill=(*C, 255))

    # 顶面中间开一条缝（深色），表示"还没封上"
    gap_c = int(W * 0.030)
    d.line([(cx, cy - th - bh // 2 + int(th * 0.10)),
            (cx, cy + th - bh // 2 - int(th * 0.10))],
           fill=(*BG, 255), width=gap_c)

    img = blend(img, layer)
    return finish(img, "BOX-1-gap")


# ══════════════════════════════════════════════════════════
# 2. 盒子 + 封带 —— 正面一道竖带，最标准的包裹
# ══════════════════════════════════════════════════════════
def box_tape():
    BG = (250, 246, 239)
    A = (222, 104, 76)
    B = (190, 80, 56)
    C = (246, 156, 128)
    TAPE = (250, 246, 239)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    hw = int(W * 0.255)
    th = int(W * 0.120)
    bh = int(W * 0.255)

    top = [(cx, cy - th - bh // 2), (cx + hw, cy - bh // 2),
           (cx, cy + th - bh // 2), (cx - hw, cy - bh // 2)]
    front = [top[3], top[2], (cx, cy + th - bh // 2 + bh), (cx - hw, cy - bh // 2 + bh)]
    side = [top[2], top[1], (cx + hw, cy - bh // 2 + bh), (cx, cy + th - bh // 2 + bh)]

    d.polygon(side, fill=(*B, 255))
    d.polygon(front, fill=(*A, 255))
    d.polygon(top, fill=(*C, 255))

    # 正面一条竖带（从上顶点到下边）
    tw = int(W * 0.058)
    y0 = cy + th - bh // 2
    y1 = y0 + bh
    d.polygon([(cx - tw//2, y0), (cx + tw//2, y0),
               (cx + tw//2, y1 - int(th*0.35)), (cx - tw//2, y1 - int(th*0.35))],
              fill=(*TAPE, 210))
    # 顶面一条横带
    d.line([(cx - hw + int(W*0.012), cy - bh//2), (cx + hw - int(W*0.012), cy - bh//2)],
           fill=(*TAPE, 200), width=int(W*0.030))

    img = blend(img, layer)
    return finish(img, "BOX-2-tape")


# ══════════════════════════════════════════════════════════
# 3. 存钱罐 —— 一个圆 + 顶部投币口。最能表达"存下来"
# ══════════════════════════════════════════════════════════
def piggy():
    BG = (248, 244, 253)
    PUR = (122, 82, 186)
    PUR_D = (96, 62, 152)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2 + int(W * 0.030)
    R = int(W * 0.255)

    # 主体圆
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(*PUR, 255))

    # 顶部投币口：一条水平深色缝，从圆的上方切入
    slot_w = int(W * 0.165)
    slot_h = int(W * 0.036)
    slot_y = cy - int(R * 0.72)
    d.rounded_rectangle([cx - slot_w//2, slot_y, cx + slot_w//2, slot_y + slot_h],
                        radius=slot_h//2, fill=(*BG, 255))

    # 底部两条小短腿
    leg_w = int(W * 0.052)
    leg_h = int(W * 0.055)
    for sign in (-1, 1):
        lx = cx + sign * int(R * 0.52)
        d.rounded_rectangle([lx - leg_w//2, cy + R - leg_h, lx + leg_w//2, cy + R + leg_h],
                            radius=leg_w//2, fill=(*PUR_D, 255))

    img = blend(img, layer)
    return finish(img, "PIG-3-slot")


# ══════════════════════════════════════════════════════════
# 4. 锁扣 —— 一个 U 型搭扣，顶端留缝（半开的锁）
#    意思：锁住了，但不是永久
# ══════════════════════════════════════════════════════════
def shackle():
    BG = (243, 247, 250)
    IND = (54, 86, 148)
    ACC = (240, 148, 72)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    sw = int(W * 0.105)      # 笔画宽
    R = int(W * 0.175)       # U 型半径
    uy = cy - int(W * 0.105)

    # U 型：半圆 + 两条竖线
    d.arc([cx-R, uy-R, cx+R, uy+R], start=180, end=360, fill=(*IND, 255), width=sw)
    for sign in (-1, 1):
        x = cx + sign * R
        d.rectangle([x - sw//2, uy, x + sw//2, uy + int(W * 0.115)], fill=(*IND, 255))

    # 下方一个圆角方块（锁体）
    bw = int(W * 0.29)
    bh = int(W * 0.175)
    by = uy + int(W * 0.098)
    d.rounded_rectangle([cx - bw//2, by, cx + bw//2, by + bh],
                        radius=int(W * 0.038), fill=(*ACC, 255))

    # 锁体上的钥匙孔
    kr = int(W * 0.028)
    d.ellipse([cx-kr, by + int(bh*0.28) - kr, cx+kr, by + int(bh*0.28) + kr], fill=(*BG, 255))
    d.polygon([(cx - int(kr*0.5), by + int(bh*0.36)),
               (cx + int(kr*0.5), by + int(bh*0.36)),
               (cx, by + int(bh*0.78))], fill=(*BG, 255))

    img = blend(img, layer)
    return finish(img, "LOCK-4-shackle")


# ══════════════════════════════════════════════════════════
# 5. 两个圆环相扣 —— 抽象、无具象物，但暗示"扣住"
# ══════════════════════════════════════════════════════════
def linked():
    BG = (34, 38, 44)
    A = (250, 200, 76)
    B = (240, 138, 96)
    img = Image.new("RGB", (W, W), BG)

    # 左环先画，右环后画并盖住，重叠处用 BG 挖
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    R = int(W * 0.155)
    sw = int(W * 0.058)
    cy = W // 2
    lcx = W // 2 - int(R * 0.62)
    rcx = W // 2 + int(R * 0.62)

    d.ellipse([lcx-R, cy-R, lcx+R, cy+R], outline=(*A, 255), width=sw)
    d.ellipse([rcx-R, cy-R, rcx+R, cy+R], outline=(*B, 255), width=sw)

    # 在重叠处给左环挖一条缺口，制造"相扣"
    mask = Image.new("L", (W, W), 0)
    md = ImageDraw.Draw(mask)
    gap_ang = 46
    # 用一个小扇形盖掉左环右侧一段
    md.pieslice([lcx-R-sw, cy-R-sw, lcx+R+sw, cy+R+sw],
                start=-gap_ang, end=gap_ang, fill=255)
    bg_layer = Image.new("RGBA", (W, W), (*BG, 0))
    bg_layer.putalpha(mask)
    layer = Image.alpha_composite(layer, bg_layer)

    img = blend(img, layer)
    return finish(img, "LINK-5-rings")


# ══════════════════════════════════════════════════════════
# 6. 向下压的箭头 → 变成一条水平线（"到底了，停"）
#    动作变静止，这是最有故事感的一个
# ══════════════════════════════════════════════════════════
def arrow_floor():
    BG = (252, 249, 244)
    INK = (38, 40, 46)
    ACC = (216, 100, 74)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    sw = int(W * 0.078)

    # 箭头竖杆（从上方落下）
    top = int(W * 0.235)
    mid = int(W * 0.545)
    d.rounded_rectangle([cx - sw//2, top, cx + sw//2, mid], radius=sw//2, fill=(*INK, 255))

    # 箭头头部（三角）
    ah = int(W * 0.115)
    aw = int(W * 0.175)
    d.polygon([(cx - aw//2, mid - int(ah*0.30)), (cx + aw//2, mid - int(ah*0.30)),
               (cx, mid + ah)], fill=(*INK, 255))

    # 地面线（粗，珊瑚色）—— 箭头撞上去停了
    fl_y = int(W * 0.695)
    fl_h = int(W * 0.072)
    fw = int(W * 0.62)
    d.rounded_rectangle([cx - fw//2, fl_y, cx + fw//2, fl_y + fl_h],
                        radius=fl_h//2, fill=(*ACC, 255))

    img = blend(img, layer)
    return finish(img, "STOP-6-floor")


# ══════════════════════════════════════════════════════════
# 7. 一颗被切开一半的果子（"核"）—— 种子在里面
#    意思：留下的是种子，会长大
# ══════════════════════════════════════════════════════════
def seed():
    BG = (250, 247, 239)
    OUTER = (214, 96, 74)
    INNER = (250, 240, 226)
    SEED = (74, 56, 42)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    R = int(W * 0.285)

    # 外圈（果肉）
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(*OUTER, 255))
    # 内圈（果核腔）
    r2 = int(R * 0.70)
    d.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=(*INNER, 255))
    # 中央种子（水滴形）
    sr = int(R * 0.30)
    d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill=(*SEED, 255))
    d.polygon([(cx - sr*0.62, cy - sr*0.62), (cx + sr*0.62, cy - sr*0.62), (cx, cy - sr*1.75)],
              fill=(*SEED, 255))

    img = blend(img, layer)
    return finish(img, "SEED-7-core")


# ══════════════════════════════════════════════════════════
# 8. 波浪 + 一条直线 —— "情绪在下面，表面是平的"
#    抽象但可读，适合"不烧心"这个名字
# ══════════════════════════════════════════════════════════
def calm_water():
    BG = (238, 246, 245)
    WATER = (32, 116, 112)
    LINE = (240, 152, 80)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = W // 2
    sw = int(W * 0.070)
    amp = int(W * 0.058)
    span = int(W * 0.255)

    # 直线（水面）在上面
    line_y = int(W * 0.375)
    d.rounded_rectangle([cx - span, line_y - sw//2, cx + span, line_y + sw//2],
                        radius=sw//2, fill=(*LINE, 255))

    # 两条波浪线在下面（正弦）
    for i, yy in enumerate([int(W * 0.545), int(W * 0.690)]):
        pts = []
        steps = 120
        for k in range(steps + 1):
            t = k / steps
            x = cx - span + t * span * 2
            y = yy + int(amp * math.sin(t * math.pi * 2.6) * (1 if i == 0 else 0.72))
            pts.append((x, y))
        wdt = sw if i == 0 else int(sw * 0.78)
        d.line(pts, fill=(*WATER, 255), width=wdt, joint="curve")
        for p in (pts[0], pts[-1]):
            r = wdt // 2
            d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=(*WATER, 255))

    img = blend(img, layer)
    return finish(img, "CALM-8-water")


# ══════════════════════════════════════════════════════════
# 9. 数字 0 + 一个缺口 —— 零浪费，缺口表示"留了余地"
# ══════════════════════════════════════════════════════════
def zero_gap():
    BG = (30, 32, 36)
    ACC = (255, 196, 66)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    R = int(W * 0.295)
    sw = int(W * 0.098)

    # 用弧线画 0，右上方留一个缺口
    d.arc([cx-R, cy-R, cx+R, cy+R], start=318, end=360 + 282, fill=(*ACC, 255), width=sw)
    # 缺口两端加圆头
    for ang in (318, 240):
        a = math.radians(ang)
        px = cx + (R) * math.cos(a)
        py = cy + (R) * math.sin(a)
        d.ellipse([px-sw//2, py-sw//2, px+sw//2, py+sw//2], fill=(*ACC, 255))

    img = blend(img, layer)
    return finish(img, "ZERO-9-gap")


# ══════════════════════════════════════════════════════════
# 10. 暂停键 == 两个竖条，但做成蜡烛（"烧"的对照）
#     两根竖条，上方有小火苗 —— 直接呼应"不烧"
# ══════════════════════════════════════════════════════════
def candles():
    BG = (250, 245, 238)
    WAX = (232, 190, 148)
    FLAME = (232, 96, 62)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    bw = int(W * 0.105)
    bh = int(W * 0.315)
    gap = int(W * 0.075)
    by = cy - int(bh * 0.28)

    for sign in (-1, 1):
        x0 = cx + sign * (gap//2 + bw//2) - bw//2
        # 烛身
        d.rounded_rectangle([x0, by, x0 + bw, by + bh],
                            radius=int(bw*0.20), fill=(*WAX, 255))
        # 火苗（水滴）
        fr = int(bw * 0.46)
        fx = x0 + bw // 2
        fy = by - fr
        d.ellipse([fx-fr, fy-fr, fx+fr, fy+fr], fill=(*FLAME, 255))
        d.polygon([(fx - fr*0.70, fy), (fx + fr*0.70, fy), (fx, fy - fr*2.05)],
                  fill=(*FLAME, 255))

    img = blend(img, layer)
    return finish(img, "CANDLE-10-pair")


# ══════════════════════════════════════════════════════════
# 11. 圆形进度环，停在 1/4 —— "还在等"
#     极简，但"未完成"的状态感很强
# ══════════════════════════════════════════════════════════
def progress():
    BG = (246, 244, 251)
    TRACK = (222, 218, 238)
    FILL = (108, 84, 200)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = W // 2, W // 2
    R = int(W * 0.285)
    sw = int(W * 0.105)

    # 底环
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=(*TRACK, 255), width=sw)
    # 进度弧（从顶部起，顺时针 100 度）
    d.arc([cx-R, cy-R, cx+R, cy+R], start=-90, end=-90+100, fill=(*FILL, 255), width=sw)
    # 弧的两个圆头
    for ang in (-90, -90 + 100):
        a = math.radians(ang)
        px = cx + R * math.cos(a)
        py = cy + R * math.sin(a)
        d.ellipse([px-sw//2, py-sw//2, px+sw//2, py+sw//2], fill=(*FILL, 255))

    img = blend(img, layer)
    return finish(img, "RING-11-progress")


# ══════════════════════════════════════════════════════════
# 12. 三个圆点排成"暂停" —— 极简到极致，只有节奏
#     中间大、两边小，形成"咚·停·咚"
# ══════════════════════════════════════════════════════════
def dots_three():
    BG = (24, 26, 30)
    A = (255, 255, 255)
    B = (240, 150, 100)
    img = Image.new("RGB", (W, W), BG)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cy = W // 2
    spac = int(W * 0.215)
    specs = [(-1, 0.070, A), (0, 0.125, B), (1, 0.070, A)]
    for sign, rf, col in specs:
        x = W // 2 + sign * spac
        r = int(W * rf)
        d.ellipse([x-r, cy-r, x+r, cy+r], fill=(*col, 255))

    img = blend(img, layer)
    return finish(img, "DOT-12-three")


SCHEMES = [
    ("BOX-1     盒子开口",     box_gap),
    ("BOX-2     盒子胶带",     box_tape),
    ("PIG-3     存钱罐",       piggy),
    ("LOCK-4    半开的锁",     shackle),
    ("LINK-5    相扣双环",     linked),
    ("STOP-6    箭头落地",     arrow_floor),
    ("SEED-7    果核种子",     seed),
    ("CALM-8    平静水面",     calm_water),
    ("ZERO-9    零的缺口",     zero_gap),
    ("CANDLE-10 两根蜡烛",     candles),
    ("RING-11   进度环",       progress),
    ("DOT-12    三点节奏",     dots_three),
]


def main():
    print("第五批（跨语言 logo）：")
    for name, fn in SCHEMES:
        try:
            fn()
        except Exception as e:
            print(f"  {name} 失败: {e}")
    print(f"\n输出: {OUT}")


if __name__ == "__main__":
    main()
