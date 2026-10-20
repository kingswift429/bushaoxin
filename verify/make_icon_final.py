# -*- coding: utf-8 -*-
"""把 Gemini 冰购物车图做成 iOS 图标：版本 A（原样）/ 版本 B（拉平背景）"""
import os
from PIL import Image, ImageDraw, ImageFilter

SRC = r"F:\Administrator\Gemini_Generated_Image_kvl9lckvl9lckvl9.jpg"
OUT = r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin\verify\preview\icon-final"
os.makedirs(OUT, exist_ok=True)

TARGET = 1024


def bright(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def find_subject_box(im, delta=45):
    """在缩小图上找主体包围盒（亮度偏离背景）"""
    s = im.resize((256, 256), Image.LANCZOS)
    px = s.load()
    edge = []
    for x in range(0, 256, 8):
        edge += [px[x, 2], px[x, 253]]
    for y in range(0, 256, 8):
        edge += [px[2, y], px[253, y]]
    bb = bright(tuple(sum(c[i] for c in edge) // len(edge) for i in range(3)))

    xs, ys = [], []
    for y in range(256):
        for x in range(256):
            if abs(bright(px[x, y]) - bb) > delta:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys), bb)


def make_version(src, flatten_bg=False, out_name="v.png"):
    im = Image.open(src).convert("RGB")
    W, H = im.size

    # 先缩放
    im = im.resize((TARGET, TARGET), Image.LANCZOS)

    if flatten_bg:
        # 用高斯模糊估计"背景场"，然后只在背景区域替换成平坦色
        # 这样主体（购物车）不受影响，背景变成均匀深蓝
        blurred = im.filter(ImageFilter.GaussianBlur(radius=TARGET * 0.06))

        # 背景基准色 = 边缘平均
        px_edge = []
        for x in range(0, TARGET, 16):
            px_edge += [im.getpixel((x, 4)), im.getpixel((x, TARGET - 5))]
        for y in range(0, TARGET, 16):
            px_edge += [im.getpixel((4, y)), im.getpixel((TARGET - 5, y))]
        base = tuple(sum(c[i] for c in px_edge) // len(px_edge) for i in range(3))

        # 逐像素：远离主体（模糊图接近基色的地方）替换为基色，主体保留
        src_px = im.load()
        blur_px = blurred.load()
        base_b = bright(base)
        out = Image.new("RGB", (TARGET, TARGET))
        op = out.load()
        for y in range(TARGET):
            for x in range(TARGET):
                sb = bright(src_px[x, y])
                bb = bright(blur_px[x, y])
                # 模糊场接近基色 且 自身也不亮 => 是背景
                if abs(bb - base_b) < 25 and abs(sb - base_b) < 45:
                    op[x, y] = base
                else:
                    op[x, y] = src_px[x, y]
        im = out

    # 居中修正
    box = find_subject_box(im)
    if box:
        x0, y0, x1, y1, _ = box
        # 映射到目标尺寸
        sc = TARGET / 256
        cx = (x0 + x1) / 2 * sc
        cy = (y0 + y1) / 2 * sc
        dx = TARGET / 2 - cx
        dy = TARGET / 2 - cy
        if abs(dx) > 1 or abs(dy) > 1:
            # 用边缘像素填充后平移
            padded = Image.new("RGB", (TARGET, TARGET))
            # 复制边缘行/列做外扩填充
            for yy in range(TARGET):
                for xx in range(TARGET):
                    sx = min(TARGET - 1, max(0, xx + int(round(dx))))
                    sy = min(TARGET - 1, max(0, yy + int(round(dy))))
                    padded.putpixel((xx, yy), im.getpixel((sx, sy)))
            im = padded
            print(f"  居中修正: dx={dx:+.1f} dy={dy:+.1f}")

    # 确保 RGB 无 alpha
    im = im.convert("RGB")
    path = os.path.join(OUT, out_name)
    im.save(path, "PNG", optimize=True)
    return im, path


def stats(im, label):
    px = list(im.resize((128, 128), Image.LANCZOS).getdata())
    edge = []
    for x in range(0, 128, 4):
        edge += [px[x * 128 + 2], px[x * 128 + 125]]
    bb = bright(tuple(sum(c[i] for c in edge) // len(edge) for i in range(3)))
    cov = sum(1 for c in px if abs(bright(c) - bb) > 45) / len(px) * 100

    tiny = list(im.resize((60, 60), Image.LANCZOS).getdata())
    cov60 = sum(1 for c in tiny if abs(bright(c) - bb) > 45) / len(tiny) * 100

    corners = [im.getpixel((3, 3)), im.getpixel((1020, 3)),
               im.getpixel((3, 1020)), im.getpixel((1020, 1020))]
    cs = [f"#{c[0]:02X}{c[1]:02X}{c[2]:02X}" for c in corners]
    cb = [round(bright(c)) for c in corners]

    print(f"\n{label}")
    print(f"  128px 主体: {cov:5.1f}%")
    print(f"  60px 主体:  {cov60:5.1f}%")
    print(f"  四角颜色: {' '.join(cs)}")
    print(f"  四角亮度: {cb}  极差 {max(cb)-min(cb)}")
    return cov, cov60, max(cb) - min(cb)


print("=" * 60)
print("版本 A：原样缩放 + 居中")
ia, pa = make_version(SRC, flatten_bg=False, out_name="A-原样-1024.png")
stats(ia, "A 原样")

print("\n" + "=" * 60)
print("版本 B：拉平背景 + 居中")
ib, pb = make_version(SRC, flatten_bg=True, out_name="B-拉平背景-1024.png")
stats(ib, "B 拉平背景")

# 生成对比图：1024 并排 + 60px 缩略
print("\n生成对比图...")
sheet_w = 1024 * 2 + 60
sheet_h = 1024 + 200
sheet = Image.new("RGB", (sheet_w, sheet_h), (250, 250, 250))
sheet.paste(ia, (0, 0))
sheet.paste(ib, (1024, 0))

d = ImageDraw.Draw(sheet)
d.text((20, 1040), "A - Original", fill=(0, 0, 0))
d.text((1044, 1040), "B - Flattened BG", fill=(0, 0, 0))

# 60px 缩略展示（模拟桌面）
a60 = ia.resize((60, 60), Image.LANCZOS)
b60 = ib.resize((60, 60), Image.LANCZOS)
sheet.paste(a60, (20, 1080))
sheet.paste(b60, (1044, 1080))
d.text((95, 1100), "60px", fill=(0, 0, 0))
d.text((1119, 1100), "60px", fill=(0, 0, 0))

sheet_path = os.path.join(OUT, "AB对比.png")
sheet.save(sheet_path, "PNG")
print("对比图:", sheet_path)
print("\n完成")
