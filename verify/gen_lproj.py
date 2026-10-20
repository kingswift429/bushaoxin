# -*- coding: utf-8 -*-
"""
生成 12 种语言的本地化资源，采用 Xcode 标准 lproj 结构：

    Bushaoxin/Resources/
        zh-Hans.lproj/InfoPlist.strings
        en.lproj/InfoPlist.strings
        ...

为什么必须是 <locale>.lproj/InfoPlist.strings 这个结构：

1. InfoPlist.strings 是 Xcode 的特殊保留文件名——
   只有在 .lproj 目录里才会被识别为「覆盖 Info.plist 的值」。
   如果叫 InfoPlist.zh-Hans.strings 放在平铺目录里，
   actool/copy 阶段只会把它当成普通资源拷进去，
   CFBundleDisplayName 根本不会被覆盖，图标名永远是中文。

2. .lproj 也是运行时 Bundle 查本地化资源的依据。
   Bundle.main.path(forResource:ofType:inDirectory:) 找的就是它。

图标名策略：
- 中文（zh-Hans）：「不烧心」——中文特有的双关，翻译不出去
- 其余 11 种：Wait A Day ——英语固定习语「先等一天」，
  正好是本 App 的核心动作，且各语言用户对英语短名接受度高

权限弹窗文案也必须本地化。只有中文的提示语会让法语/阿语用户
看到串味的界面，App Store 审核也会挑这一点。
"""
import json
import shutil
from pathlib import Path

BASE = Path(r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin\Bushaoxin")
RES_DIR = BASE / "Resources"

LOCALES = ["zh-Hans", "en", "ja", "ko", "fr", "de", "es", "pt-BR", "ru", "ar", "it", "nl"]

NAMES = {
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

PHOTO = {
    "zh-Hans": "用来从购物截图里自动识别商品名和价格，快速发起审批。",
    "en": "Reads the item name and price from your shopping screenshots to fill in a request.",
    "ja": "買い物のスクリーンショットから商品名と価格を読み取り、申請をすぐ入力できます。",
    "ko": "쇼핑 스크린샷에서 상품명과 가격을 읽어 요청을 빠르게 채웁니다.",
    "fr": "Lit le nom et le prix de l'article sur vos captures d'écran pour remplir une demande.",
    "de": "Liest Artikelname und Preis aus deinen Einkaufs-Screenshots, um eine Anfrage auszufüllen.",
    "es": "Lee el nombre y el precio del artículo en tus capturas para rellenar una solicitud.",
    "pt-BR": "Lê o nome e o preço do item nas suas capturas de tela para preencher uma solicitação.",
    "ru": "Считывает название и цену товара со скриншотов, чтобы заполнить заявку.",
    "ar": "يقرأ اسم المنتج وسعره من لقطات الشاشة لملء الطلب.",
    "it": "Legge nome e prezzo dell'articolo dagli screenshot per compilare una richiesta.",
    "nl": "Leest de artikelnaam en prijs uit je schermafbeeldingen om een verzoek in te vullen.",
}

CAMERA = {
    "zh-Hans": "用来拍摄价签或商品页，自动填入审批单。",
    "en": "Photograph a price tag or product page to fill in the request automatically.",
    "ja": "値札や商品ページを撮影して、申請を自動入力します。",
    "ko": "가격표나 상품 페이지를 촬영해 요청을 자동으로 채웁니다.",
    "fr": "Photographiez une étiquette ou une page produit pour remplir la demande automatiquement.",
    "de": "Fotografiere ein Preisschild oder eine Produktseite, um die Anfrage automatisch auszufüllen.",
    "es": "Fotografía una etiqueta o una página de producto para rellenar la solicitud automáticamente.",
    "pt-BR": "Fotografe uma etiqueta ou página de produto para preencher a solicitação automaticamente.",
    "ru": "Сфотографируйте ценник или страницу товара, чтобы заполнить заявку автоматически.",
    "ar": "صوّر بطاقة السعر أو صفحة المنتج لملء الطلب تلقائيًا.",
    "it": "Fotografa un cartellino o una pagina prodotto per compilare la richiesta automaticamente.",
    "nl": "Fotografeer een prijskaartje of productpagina om het verzoek automatisch in te vullen.",
}


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    if RES_DIR.exists():
        shutil.rmtree(RES_DIR)
    RES_DIR.mkdir(parents=True)

    for loc in LOCALES:
        d = RES_DIR / f"{loc}.lproj"
        d.mkdir()
        body = (
            "/* 自动生成，请勿手改。源：verify/gen_lproj.py */\n"
            "\n"
            '/* 桌面图标下显示的名字 */\n'
            f'"CFBundleDisplayName" = "{esc(NAMES[loc])}";\n'
            "\n"
            "/* 权限弹窗文案 */\n"
            f'"NSPhotoLibraryUsageDescription" = "{esc(PHOTO[loc])}";\n'
            f'"NSCameraUsageDescription" = "{esc(CAMERA[loc])}";\n'
        )
        (d / "InfoPlist.strings").write_text(body, encoding="utf-8")
        print(f"  {loc:<8}.lproj/InfoPlist.strings   {NAMES[loc]}")

    print(f"\n共生成 {len(LOCALES)} 个 lproj 目录")
    print(f"位置: {RES_DIR}")


if __name__ == "__main__":
    main()
