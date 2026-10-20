# -*- coding: utf-8 -*-
"""
把标语从「睡一觉」意象改为「等一天」意象。

原因：品牌名从 Sleep On It 改成 Wait A Day 后，
标语里如果还留着 "Sleep easy" / "ひと晩"，
名字和口号就对不上了。

新标语围绕「等一天」这个动作，各语言用自己最自然的说法：
- 英语 wait a day 本身就是习语，标语直接呼应
- 日语「一日置く」、韩语「하루만 더」都是当地人自然的表达
- 中文保留原标题「花得值，不烧心」，它不依赖睡眠意象
"""
import json
from pathlib import Path

XC = Path(r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin\Bushaoxin\Localization\Localizable.xcstrings")

TAGLINE = {
    "zh-Hans": "花得值，不烧心",
    "en": "Wait a day. Spend better.",
    "ja": "一日置いて、買う。",
    "ko": "하루만 더, 그리고 결정.",
    "fr": "Attendez un jour. Achetez mieux.",
    "de": "Einen Tag warten. Besser kaufen.",
    "es": "Espera un día. Compra mejor.",
    "pt-BR": "Espere um dia. Compre melhor.",
    "ru": "День подождите. Купите лучше.",
    "ar": "انتظر يومًا. واشترِ أفضل.",
    "it": "Aspetta un giorno. Compra meglio.",
    "nl": "Wacht een dag. Koop beter.",
}


def main():
    with open(XC, encoding="utf-8") as f:
        data = json.load(f)

    entry = data["strings"]["app.tagline"]
    locs = entry.setdefault("localizations", {})
    for loc, text in TAGLINE.items():
        locs.setdefault(loc, {})["stringUnit"] = {"state": "translated", "value": text}

    data["strings"] = dict(sorted(data["strings"].items()))
    with open(XC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, separators=(",", " : "))
        f.write("\n")

    print("app.tagline 已更新：")
    for loc in sorted(TAGLINE):
        print(f"  {loc:<8} {TAGLINE[loc]}")


if __name__ == "__main__":
    main()
