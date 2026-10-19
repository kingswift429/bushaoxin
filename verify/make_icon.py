#!/usr/bin/env python3
"""生成 App 图标：程序化绘制，可控、干净、可复现。

设计思路（为什么是这样）：
- iOS 图标在桌面只有 60pt，细节全糊。所以只放**一个**符号，图形要大、边缘要粗。
- 品牌色珊瑚红必须占据主体面积，否则远看是一片米色，认不出来。
  但也不能反过来占满画布——那样会变成一个纯红色方块，失去辨识度。
  目标：珊瑚红 30~40%，米色背景 55~65%。
- 不用描边勾线：描边在缩小后会和填充混成灰糊。只用色块。
- 背景用品牌米色而非纯白。

图形：一个"停下来的购物袋"。
- 袋身略微倾斜（-8 度），暗示"被放下、不再往前"。
- 提手用开口弧线，像一个放松的肩带。
- 底部一条很淡的阴影，让图标有重量感但不做 3D。

关键实现注意：
旋转必须用 **rotate(expand=False) 但配合精确的尺寸控制**，
或者干脆先画在独立图层上、旋转后再按包围盒贴回中心。
上一版直接对整张图 rotate，导致蒙版把整幅画布填满（红色占 91.8%）。
"""
from PIL import Image, ImageDraw
import os

SIZE = 1024
SS = 4                      # 超采样倍数，抗锯齿用
W = SIZE * SS

# 品牌色
CREAM      = (251, 248, 244)
CORAL      = (217, 102, 74)
CORAL_DARK = (196, 86, 60)
SHADOW     = (238, 230, 220)


def draw_bag_layer(size, tilt_deg):
    """在透明图层上画出袋子+提手，返回旋转后的图层。

    关键：图层尺寸比袋子略大即可，旋转后按包围盒贴回，不会撑满画布。
    """
    # 袋子尺寸：占画布的 52% 宽、42% 高
    bag_w = int(size * 0.52)
    bag_h = int(size * 0.42)
    radius = int(size * 0.058)

    # 提手尺寸
    handle_w = int(size * 0.27)
    handle_h = int(size * 0.19)
    stroke = int(size * 0.055)

    # 图层要比内容大一圈，留出旋转余量
    pad = int(size * 0.10)
    layer_size = max(bag_w, handle_w) + pad * 2
    layer_h = bag_h + handle_h + pad * 2

    layer = Image.new("RGBA", (layer_size, layer_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    lcx = layer_size // 2
    bag_left = lcx - bag_w // 2
    bag_top = pad + handle_h
    bag_right = bag_left + bag_w
    bag_bottom = bag_top + bag_h

    # 1. 提手先画（在袋子后面）
    hx = lcx - handle_w // 2
    hy = bag_top - handle_h
    d.arc(
        [hx, hy, hx + handle_w, hy + handle_h * 2],
        start=188, end=352,
        fill=(*CORAL_DARK, 255), width=stroke
    )

    # 2. 袋身
    d.rounded_rectangle(
        [bag_left, bag_top, bag_right, bag_bottom],
        radius=radius, fill=(*CORAL, 255)
    )

    # 3. 袋身上的品牌圆点
    dot_r = int(size * 0.040)
    dctr_x = lcx + int(size * 0.008)
    dctr_y = bag_top + bag_h // 2 + int(size * 0.022)
    d.ellipse(
        [dctr_x - dot_r, dctr_y - dot_r, dctr_x + dot_r, dctr_y + dot_r],
        fill=(*CREAM, 255)
    )

    # 4. 旋转（expand=True 保留完整内容，不会被裁）
    return layer.rotate(tilt_deg, resample=Image.BICUBIC, expand=True)


def main():
    img = Image.new("RGB", (W, W), CREAM)

    # ── 1. 底部柔和阴影 ────────────────────────────────
    shadow_layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sw = int(W * 0.42)
    sh = int(W * 0.045)
    cx = cy = W // 2
    sd.ellipse(
        [cx - sw // 2, cy + int(W * 0.225), cx + sw // 2, cy + int(W * 0.225) + sh],
        fill=(*SHADOW, 255)
    )
    img = Image.alpha_composite(img.convert("RGBA"), shadow_layer).convert("RGB")

    # ── 2. 袋子图层 ────────────────────────────────────
    bag = draw_bag_layer(W, -8)

    # ── 3. 贴到画布中心（按旋转后的包围盒居中）───────────
    bw, bh = bag.size
    # 袋子视觉重心略低于几何中心（因为提手在上方），所以上移一点点
    ox = (W - bw) // 2
    oy = (W - bh) // 2 + int(W * 0.02)

    base = img.convert("RGBA")
    base.alpha_composite(bag, (ox, oy))
    img = base.convert("RGB")

    # ── 4. 降采样 ──────────────────────────────────────
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")

    assert out.mode == "RGB", "iOS 图标不能有 alpha 通道"
    assert out.size == (SIZE, SIZE), "必须正好 1024x1024"

    here = os.path.dirname(os.path.abspath(__file__))
    dest = os.path.normpath(os.path.join(
        here, "..", "Bushaoxin", "Assets.xcassets",
        "AppIcon.appiconset", "icon-1024.png"
    ))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    out.save(dest, "PNG", optimize=True)

    preview_dir = os.path.join(here, "preview")
    os.makedirs(preview_dir, exist_ok=True)
    out.save(os.path.join(preview_dir, "icon-1024.png"), "PNG")
    out.resize((180, 180), Image.LANCZOS).save(os.path.join(preview_dir, "icon-180.png"))
    out.resize((60, 60), Image.LANCZOS).save(os.path.join(preview_dir, "icon-60.png"))

    print("saved", dest, out.size, out.mode)
    print("preview", preview_dir)


if __name__ == "__main__":
    main()
