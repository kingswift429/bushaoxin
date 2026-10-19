import Foundation
import SwiftData

/// 本地体验数据。首次启动灌入一批"广场"内容，
/// 保证用户零等待就能理解产品玩法（冷启动必做）。
///
/// 种子内容按语言准备：海外用户第一次打开看到的是英文/日文/韩文商品，
/// 而不是"一杯杨枝甘露" —— 这一条决定了本地化的第一印象。
enum SeedData {

    private struct Seed {
        let goods: String
        let price: String          // 用字符串构造 Decimal，避免浮点字面量误差
        let category: SpendCategory
        let reason: String
        let alternative: String
        let pass: Int
        let reject: Int
    }

    // MARK: 简体中文

    private static let zhHans: [Seed] = [
        .init(goods: "一杯杨枝甘露", price: "15", category: .dining,
              reason: "今天被老板骂了，需要一点甜的东西安慰自己。",
              alternative: "白开水，但没味道", pass: 2, reject: 9),
        .init(goods: "电蚊拍", price: "30", category: .other,
              reason: "领导老在耳边嗡嗡响。",
              alternative: "巴掌，但手会疼", pass: 7, reject: 3),
        .init(goods: "全身镜", price: "35", category: .fashion,
              reason: "家里只有半身镜，没法照全身。",
              alternative: "在半身镜前跳起来欣赏 0.1 秒自己的全身穿搭", pass: 5, reject: 6),
        .init(goods: "演唱会内场票", price: "1360", category: .other,
              reason: "喜欢了八年的歌手，可能是最后一次巡演。",
              alternative: "看台票 380 元，也能听到", pass: 6, reject: 4),
        .init(goods: "一杯冰美式", price: "10", category: .dining,
              reason: "可恶的调休一直在折磨我。",
              alternative: "直接在工位上睡觉", pass: 8, reject: 1),
        .init(goods: "机械键盘", price: "699", category: .digital,
              reason: "现在这个键盘空格键有点黏，打字影响了。",
              alternative: "先拆开清理一次，说不定还能用半年", pass: 3, reject: 7),
        .init(goods: "健身年卡", price: "2680", category: .sports,
              reason: "想认真减脂，办卡能逼自己坚持。",
              alternative: "先买张 199 的月卡，撑满 20 天再考虑年卡", pass: 4, reject: 5),
        .init(goods: "第九个手机壳", price: "39", category: .digital,
              reason: "这个配色好看。",
              alternative: "你现在用的那个还没坏", pass: 1, reject: 8)
    ]

    // MARK: English

    private static let en: [Seed] = [
        .init(goods: "A mango sago", price: "4.20", category: .dining,
              reason: "Got yelled at by my boss today. Need something sweet.",
              alternative: "Tap water, but it tastes like nothing", pass: 2, reject: 9),
        .init(goods: "Electric fly swatter", price: "4.30", category: .other,
              reason: "My manager keeps buzzing in my ear.",
              alternative: "My hand, but it hurts", pass: 7, reject: 3),
        .init(goods: "Full-length mirror", price: "5.00", category: .fashion,
              reason: "Only have a half mirror, can't see my whole outfit.",
              alternative: "Jump in front of the half mirror for 0.1s", pass: 5, reject: 6),
        .init(goods: "Front-row concert ticket", price: "190", category: .other,
              reason: "Loved this artist for eight years. Maybe the last tour.",
              alternative: "Balcony seat at $54, you'll still hear it", pass: 6, reject: 4),
        .init(goods: "Iced americano", price: "1.40", category: .dining,
              reason: "The rescheduled work week is torturing me.",
              alternative: "Sleep at my desk", pass: 8, reject: 1),
        .init(goods: "Mechanical keyboard", price: "98", category: .digital,
              reason: "My spacebar is sticky and my typing is suffering.",
              alternative: "Take it apart and clean it. Might last half a year", pass: 3, reject: 7),
        .init(goods: "Annual gym membership", price: "375", category: .sports,
              reason: "Want to lose fat properly. Paying forces me to commit.",
              alternative: "A $28 monthly pass first. 20 days in, then decide", pass: 4, reject: 5),
        .init(goods: "Ninth phone case", price: "5.50", category: .digital,
              reason: "This colorway is nice.",
              alternative: "The one on your phone isn't broken", pass: 1, reject: 8)
    ]

    // MARK: 日本語

    private static let ja: [Seed] = [
        .init(goods: "マンゴーサゴ 1杯", price: "580", category: .dining,
              reason: "今日上司に怒られて、甘いものが欲しい。",
              alternative: "白湯、でも味がない", pass: 2, reject: 9),
        .init(goods: "電撃殺虫ラケット", price: "1200", category: .other,
              reason: "上司がずっと耳元でブンブン言う。",
              alternative: "手のひら、でも痛い", pass: 7, reject: 3),
        .init(goods: "全身鏡", price: "2400", category: .fashion,
              reason: "家に半分の鏡しかなくて全身が確認できない。",
              alternative: "半分の鏡の前でジャンプして0.1秒だけ確認", pass: 5, reject: 6),
        .init(goods: "ライブの前方席", price: "13600", category: .other,
              reason: "8年好きなアーティスト。最後のツアーかもしれない。",
              alternative: "スタンド席3800円でも聞こえる", pass: 6, reject: 4),
        .init(goods: "アイスアメリカーノ", price: "450", category: .dining,
              reason: "理不尽なシフト変更にずっと耐えている。",
              alternative: "デスクで寝る", pass: 8, reject: 1),
        .init(goods: "メカニカルキーボード", price: "9800", category: .digital,
              reason: "今のキーボードのスペースキーが粘って打ちにくい。",
              alternative: "まず分解して掃除。半年は持つかも", pass: 3, reject: 7),
        .init(goods: "ジム年間パス", price: "33000", category: .sports,
              reason: "本気で絞りたい。お金を払えば続けられる気がする。",
              alternative: "まず月額3000円で20日続いたら考える", pass: 4, reject: 5),
        .init(goods: "9個目のスマホケース", price: "1980", category: .digital,
              reason: "この配色がかわいい。",
              alternative: "今つけているものはまだ壊れていない", pass: 1, reject: 8)
    ]

    // MARK: 한국어

    private static let ko: [Seed] = [
        .init(goods: "망고 사고 한 잔", price: "6800", category: .dining,
              reason: "오늘 상사한테 혼나서 단 게 필요해요.",
              alternative: "물, 하지만 아무 맛도 없음", pass: 2, reject: 9),
        .init(goods: "전기 모기채", price: "12000", category: .other,
              reason: "상사가 계속 귀에서 윙윙거려요.",
              alternative: "손바닥, 하지만 아파요", pass: 7, reject: 3),
        .init(goods: "전신 거울", price: "24000", category: .fashion,
              reason: "집에 반신 거울밖에 없어서 전신이 안 보여요.",
              alternative: "반신 거울 앞에서 점프해 0.1초만 확인", pass: 5, reject: 6),
        .init(goods: "콘서트 앞자리 티켓", price: "190000", category: .other,
              reason: "8년 동안 좋아한 가수, 마지막 투어일지도 몰라요.",
              alternative: "스탠드석 4만원이어도 들려요", pass: 6, reject: 4),
        .init(goods: "아이스 아메리카노", price: "4500", category: .dining,
              reason: "말도 안 되는 일정 변경이 계속 저를 괴롭혀요.",
              alternative: "자리에서 그냥 자기", pass: 8, reject: 1),
        .init(goods: "기계식 키보드", price: "89000", category: .digital,
              reason: "지금 키보드 스페이스바가 끈적해서 타이핑이 힘들어요.",
              alternative: "일단 분해해서 청소. 반년은 더 쓸지도", pass: 3, reject: 7),
        .init(goods: "헬스장 연간권", price: "290000", category: .sports,
              reason: "진짜로 빼고 싶어서 돈을 내면 지킬 것 같아요.",
              alternative: "먼저 한 달 2만원으로 20일 채우고 결정", pass: 4, reject: 5),
        .init(goods: "아홉 번째 휴대폰 케이스", price: "5900", category: .digital,
              reason: "색이 예뻐요.",
              alternative: "지금 쓰는 건 아직 멀쩡해요", pass: 1, reject: 8)
    ]

    private static func seedsForCurrentLanguage() -> [Seed] {
        switch Locale.current.language.languageCode?.identifier ?? "en" {
        case "zh": return zhHans
        case "ja": return ja
        case "ko": return ko
        default: return en
        }
    }

    @MainActor
    static func seedIfNeeded(_ context: ModelContext) {
        let descriptor = FetchDescriptor<Application>()
        let count = (try? context.fetchCount(descriptor)) ?? 0
        guard count == 0 else { return }

        let currency = MoneyFormatter.deviceCurrencyCode

        for s in seedsForCurrentLanguage() {
            let app = Application(
                goods: s.goods,
                price: Decimal(string: s.price) ?? 0,
                currencyCode: currency,
                categoryKey: s.category.rawValue,
                reason: s.reason,
                alternative: s.alternative,
                channel: "plaza"
            )
            // 种子内容往前推时间，看起来像真实社区
            app.createdAt = Date().addingTimeInterval(-Double.random(in: 600...86_400))
            // 种子内容是别人的，不能算作"我的"，否则会污染省钱账本
            app.authorKey = "seed-\(UUID().uuidString.prefix(8))"
            app.passCount = s.pass
            app.rejectCount = s.reject
            context.insert(app)

            // 配几条真实感的审批理由。
            // 数量必须对得上：卡片显示"11 人已审批"，点开却只有 2 条理由，
            // 用户一眼就看得出数据是假的，直接伤信任。
            // 所以这里按预设比例生成，并保证至少覆盖展示的条数。
            let corpus = CrowdCorpus.current()
            let wantPass = min(max(s.pass, 0), 5)
            let wantReject = min(max(s.reject, 0), 5)

            for i in 0..<(wantPass + wantReject) {
                let isPass = i < wantPass
                let pool = isPass ? corpus.pass : corpus.reject
                guard let comment = pool.randomElement() else { continue }
                context.insert(Vote(
                    applicationID: app.id,
                    verdict: isPass ? "pass" : "reject",
                    comment: comment,
                    isSimulated: true
                ))
            }
        }

        try? context.save()
    }
}
