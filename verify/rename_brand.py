# -*- coding: utf-8 -*-
"""
把品牌名从 Cool Head 改成 Wait A Day，并重写各语言的标语。

改名理由：
- Cool Head 在英语母语者眼里像退烧贴/冰敷帽，是医疗品类暗示
- 「不烧心」的双关（烧心=后悔上火）翻不出去，只能意译
- Wait A Day 是英语习语「先等一天」，
  正好是本 App 的核心动作，也是 24 小时冷静期的通俗说法

中文名保留「不烧心」不变——它在中文里成立，且用户已经认知。

标语各语言重写，不再直译「花得值，不烧心」，
而是用各语言自己的说法表达「不后悔 / 睡得着」这层意思。
"""
import json
from pathlib import Path

XC = Path(r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin\Bushaoxin\Localization\Localizable.xcstrings")

NAME = {
    "zh-Hans": "不烧心",
    "en": "Wait A Day",
    "ja": "Wait A Day",
    "ko": "Wait A Day",
    "fr": "Wait A Day",
    "de": "Wait A Day",
    "es": "Wait A Day",
    "pt-BR": "Wait A Day",
    "ru": "Wait A Day",
    "ar": "Wait A Day",
    "it": "Wait A Day",
    "nl": "Wait A Day",
}

# 标语：表达「花得值、不后悔」，不用直译
TAGLINE = {
    "zh-Hans": "花得值，不烧心",
    # 英语习语：买之前先睡一觉。双关 spend/sleep
    "en": "Spend better. Sleep easy.",
    "ja": "買う前に、ひと晩。",
    "ko": "사기 전에, 하룻밤.",
    "fr": "Achetez mieux. Dormez tranquille.",
    "de": "Besser kaufen. Ruhiger schlafen.",
    "es": "Compra mejor. Duerme tranquilo.",
    "pt-BR": "Compre melhor. Durma tranquilo.",
    "ru": "Покупайте лучше. Спите спокойно.",
    "ar": "اشترِ أفضل. ونم مرتاحًا.",
    "it": "Compra meglio. Dormi sereno.",
    "nl": "Beter kopen. Rustiger slapen.",
}

# 付费墙标题也要跟着品牌走
PAYWALL_TITLE = "Wait A Day Plus"

# 商店页副标题式的推广语，放进 xcstrings 不合适，
# 但 app.tagline 在 App 内会显示，必须同步


def set_value(locs, locale, text):
    if "stringUnit" not in locs.get(locale, {}):
        locs.setdefault(locale, {})
    locs[locale]["stringUnit"] = {"state": "translated", "value": text}


def main():
    with open(XC, encoding="utf-8") as f:
        data = json.load(f)

    strings = data["strings"]

    # ── app.name ──
    entry = strings["app.name"]
    locs = entry.setdefault("localizations", {})
    for loc, val in NAME.items():
        set_value(locs, loc, val)
    print("app.name:")
    for loc in sorted(NAME):
        print(f"  {loc:<8} {NAME[loc]}")

    # ── app.tagline ──
    entry = strings["app.tagline"]
    locs = entry.setdefault("localizations", {})
    for loc, val in TAGLINE.items():
        set_value(locs, loc, val)
    print("\napp.tagline:")
    for loc in sorted(TAGLINE):
        print(f"  {loc:<8} {TAGLINE[loc]}")

    # ── paywall.title ──
    entry = strings["paywall.title"]
    locs = entry.setdefault("localizations", {})
    for loc in NAME:
        set_value(locs, loc, PAYWALL_TITLE)
    print(f"\npaywall.title: 全部改为 {PAYWALL_TITLE}")

    data["strings"] = dict(sorted(strings.items()))
    with open(XC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, separators=(",", " : "))
        f.write("\n")

    print(f"\n已写入 {XC}")


if __name__ == "__main__":
    main()
