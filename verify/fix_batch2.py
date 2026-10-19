#!/usr/bin/env python3
"""修正第二批里占比过小的三个方案（J / O / Q），把图形本身画大。

之前的问题：硬币太窄、心跳线太细、开口框笔画太轻，
导致主体像素占比只有 3~6%，60px 下几乎看不见。
这里直接放大核心参数，而不是事后缩放（事后缩放会被边界截断）。
"""
from PIL import Image, ImageDraw
import os

SIZE = 1024
SS = 4
W = SIZE * SS
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "candidates2")


def finish(img, name):
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    out.save(os.path.join(OUT, f"{name}.png"), "PNG", optimize=True)
    out.resize((60, 60), Image.LANCZOS).save(os.path.join(OUT, f"{name}-60.png"))
    print(f"  {name}.png")


# ── J 墨黑 + 亮黄：立着的硬币（加厚、加大）────────────
def j_ink():
    BG = (24, 24, 26)
    ACCENT = (255, 199, 44)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 原本 thick=0.085 太细，改成 0.16，高度也加大
    r = int(W * 0.34)
    thick = int(W * 0.175)
    coin = Image.new("RGBA", (int(W * 1.0), int(W * 1.0)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(coin)
    cc = coin.size[0] // 2
    cd.ellipse([cc - thick // 2, cc - r, cc + thick // 2, cc + r], fill=(*ACCENT, 255))
    coin = coin.rotate(16, resample=Image.BICUBIC, expand=False)
    layer.alpha_composite(coin, ((W - coin.size[0]) // 2, (W - coin.size[1]) // 2))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "J-ink-coin")


# ── O 深紫 + 粉：心跳线（加粗线条）───────────────────
def o_plum():
    BG = (48, 36, 62)
    PINK = (240, 138, 168)
    PINK_L = (255, 186, 206)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    sw = int(W * 0.115)          # 原来是 0.058，翻倍
    amp = int(W * 0.215)         # 振幅加大
    span = int(W * 0.40)

    pts = [
        (cx - span, cy),
        (cx - int(span*0.40), cy),
        (cx - int(span*0.22), cy - amp),
        (cx - int(span*0.02), cy + amp),
        (cx + int(span*0.18), cy),
        (cx + span, cy),
    ]
    d.line(pts, fill=(*PINK, 255), width=sw, joint="curve")
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0]-sw//2, p[1]-sw//2, p[0]+sw//2, p[1]+sw//2], fill=(*PINK, 255))
    # 尖峰顶点光点
    d.ellipse([cx - int(span*0.22) - sw//2, cy - amp - sw//2,
               cx - int(span*0.22) + sw//2, cy - amp + sw//2], fill=(*PINK_L, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "O-plum-pulse")


# ── Q 纯黑白：未完成的框（笔画加粗，整体放大）────────
def q_mono():
    BG = (252, 252, 252)
    INK = (22, 22, 22)
    img = Image.new("RGB", (W, W), BG)
    cx = cy = W // 2
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    bw = int(W * 0.46)
    bh = int(W * 0.34)
    sw = int(W * 0.115)          # 原来 0.055

    # 开口框（用粗弧线）
    d.arc([cx - bw//2, cy - bh//2, cx + bw//2, cy + bh//2],
          start=40, end=210, fill=(*INK, 255), width=sw)
    d.arc([cx - bw//2, cy - bh//2, cx + bw//2, cy + bh//2],
          start=288, end=322, fill=(*INK, 255), width=sw)

    # 开口处伸出的短横线
    d.rounded_rectangle([cx + bw//2 - int(W*0.02), cy - sw//2,
                         cx + bw//2 + int(W*0.115), cy + sw//2],
                        radius=sw//2, fill=(*INK, 255))
    # 断点
    dot_r = int(W * 0.048)
    dx = cx + bw//2 + int(W*0.165)
    d.ellipse([dx-dot_r, cy-dot_r, dx+dot_r, cy+dot_r], fill=(*INK, 255))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return finish(img, "Q-mono-open")


if __name__ == "__main__":
    print("修正 J / O / Q：")
    j_ink()
    o_plum()
    q_mono()
