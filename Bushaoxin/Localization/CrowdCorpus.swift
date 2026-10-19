import Foundation

/// 模拟网友语料（多语言）。
///
/// 冷启动阶段广场的"人气"全靠这批语料，如果海外用户看到的是中文理由，
/// 产品的本地化感会立刻穿帮。所以语料必须跟着语言走。
enum CrowdCorpus {

    /// 简体中文
    static let zhHans: (reject: [String], pass: [String]) = (
        reject: [
            "先冷静 24 小时，睡一觉大概就不想了。",
            "这个价格能买三顿正经饭了，不值。",
            "同类平替很多，搜一下能省一半。",
            "你上个月是不是也买过差不多的？",
            "先加入购物车放三天，还想要再说。",
            "不是刚需，是情绪在花钱。",
            "这个钱省下来，年底能心疼自己一次。",
            "看评论说质量一般，别踩雷。",
            "有更便宜质量也好的，去看博主的测评。",
            "你这理由说服不了我，重写。"
        ],
        pass: [
            "确实需要，买吧。",
            "这个价格合理，不算冲动。",
            "支持你，人生苦短。",
            "刚需就买，别内耗。",
            "看得出你真的很想要，值。",
            "用得久就是划算，通过。",
            "替你想了一圈，没有更好的替代，过。",
            "这钱花得踏实，不烧心。"
        ]
    )

    /// English
    static let en: (reject: [String], pass: [String]) = (
        reject: [
            "Sleep on it for 24 hours. You'll probably forget about it.",
            "That price buys three proper meals. Not worth it.",
            "There are plenty of cheaper equivalents. Search first.",
            "Didn't you buy something like this last month?",
            "Add to cart, wait three days, then ask again.",
            "Not a need — your mood is spending.",
            "Skip it and you'll thank yourself at year end.",
            "Reviews say the quality is mediocre. Don't risk it.",
            "There's a cheaper one with better reviews. Go read up.",
            "Your reason doesn't convince me. Try again."
        ],
        pass: [
            "You actually need it. Buy.",
            "Fair price, not an impulse.",
            "Go for it — life is short.",
            "If it's a real need, just buy it.",
            "You clearly want it. Worth it.",
            "You'll use it for years. Approved.",
            "I looked for alternatives. Nothing better.",
            "This is money well spent. Sleep fine."
        ]
    )

    /// 日本語
    static let ja: (reject: [String], pass: [String]) = (
        reject: [
            "24時間寝かせましょう。たぶん忘れます。",
            "その値段ならちゃんとした食事が3回できます。",
            "似たもので安いものがあります。まず検索を。",
            "先月も似たようなもの買いませんでした？",
            "カートに入れて3日待ってから決めましょう。",
            "必要じゃなくて、気分がお金を使っています。",
            "今は我慢すると、年末に自分を褒められます。",
            "レビューで品質が今ひとつと言われています。",
            "安くて評価の高いものがあります。調べてみては。",
            "その理由では納得できません。書き直してください。"
        ],
        pass: [
            "本当に必要ですね。買ってよし。",
            "妥当な価格で、衝動買いではありません。",
            "応援します。人生は短い。",
            "必要なものなら買いましょう。",
            "本当に欲しそうですね。価値あり。",
            "長く使えるならお得です。承認。",
            "代替案を探しましたが、これ以上のものはありません。",
            "後悔しない買い物です。"
        ]
    )

    /// 한국어
    static let ko: (reject: [String], pass: [String]) = (
        reject: [
            "24시간 두고 보세요. 아마 잊을 거예요.",
            "그 돈이면 제대로 된 밥을 세 끼 먹을 수 있어요.",
            "비슷한데 더 싼 게 많아요. 검색부터 해 보세요.",
            "지난달에도 비슷한 걸 사지 않았나요?",
            "장바구니에 넣고 3일 뒤에 다시 생각해 보세요.",
            "필요해서가 아니라 기분이 돈을 쓰고 있어요.",
            "지금 참으면 연말에 스스로를 칭찬하게 될 거예요.",
            "리뷰에서 품질이 별로라고 하네요. 걸러요.",
            "더 싸고 평가 좋은 게 있어요. 찾아보세요.",
            "이유가 납득이 안 돼요. 다시 써 주세요."
        ],
        pass: [
            "정말 필요하네요. 사세요.",
            "가격이 적당하고 충동적이지 않아요.",
            "응원합니다. 인생은 짧아요.",
            "필수품이면 그냥 사세요.",
            "간절해 보여요. 살 만해요.",
            "오래 쓰면 오히려 이득입니다. 승인.",
            "대안을 찾아봤는데 더 나은 게 없네요.",
            "후회 없는 지출이에요."
        ]
    )

    /// 按当前语言取语料；不支持的语言回落到英文
    static func current() -> (reject: [String], pass: [String]) {
        let code = Locale.current.language.languageCode?.identifier ?? "en"
        switch code {
        case "zh": return zhHans
        case "ja": return ja
        case "ko": return ko
        default: return en
        }
    }
}
