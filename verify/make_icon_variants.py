# -*- coding: utf-8 -*-
"""
生成 iOS 26 需要的三种图标变体：
  - 默认（浅色）
  - 深色（dark）
  - 着色（tinted）

为什么需要三个：
iOS 18 起引入了"深色模式图标"和"着色图标"。
Xcode 26 的 actool 在只有单一 default 变体时，
可能生成不出 AppIcon 条目 —— 结果就是 App 装上后显示系统占位图标。

三个变体的处理：
  默认：原图
  深色：原图（深蓝背景本来就是深色友好，直接复用）
  着色：转成灰度（系统会自己上色）
"""
import os
from PIL import Image

BASE = r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin"
ICON_DIR = os.path.join(BASE, "Bushaoxin", "Assets.xcassets", "AppIcon.appiconset")
SRC = os.path.join(BASE, r"verify\preview\icon-final\A-原样-1024.png")

os.makedirs(ICON_DIR, exist_ok=True)

im = Image.open(SRC).convert("RGB")
assert im.size == (1024, 1024), im.size

# 1. 默认
p_default = os.path.join(ICON_DIR, "icon-1024.png")
im.save(p_default, "PNG", optimize=True)
print("默认:", os.path.basename(p_default), round(os.path.getsize(p_default) / 1024, 1), "KB")

# 2. 深色：原图本身背景就是深夜蓝，直接复用
p_dark = os.path.join(ICON_DIR, "icon-1024-dark.png")
im.save(p_dark, "PNG", optimize=True)
print("深色:", os.path.basename(p_dark), round(os.path.getsize(p_dark) / 1024, 1), "KB")

# 3. 着色：灰度图，系统会按用户选择的色调映射
p_tinted = os.path.join(ICON_DIR, "icon-1024-tinted.png")
gray = im.convert("L").convert("RGB")
gray.save(p_tinted, "PNG", optimize=True)
print("着色:", os.path.basename(p_tinted), round(os.path.getsize(p_tinted) / 1024, 1), "KB")

print("\n完成，三个变体都已生成")
