import Foundation

/// 所有面向用户文案的键。
///
/// 集中定义的目的：Xcode 的 String Catalog 靠字面量自动提取很难覆盖
/// 动态拼接的场景，把 key 写成常量可以让漏翻变成**编译期可见**的问题。
enum L {

    // MARK: 品牌与主标语
    static var appName: String { String(localized: "app.name") }
    static var tagline: String { String(localized: "app.tagline") }
    static var slogan: String { String(localized: "plaza.slogan") }

    // MARK: 标签栏
    static var tabPlaza: String { String(localized: "tab.plaza") }
    static var tabMine: String { String(localized: "tab.mine") }
    static var post: String { String(localized: "action.post") }

    // MARK: 审批卡片
    static var pass: String { String(localized: "vote.pass") }
    static var reject: String { String(localized: "vote.reject") }
    static var watch: String { String(localized: "vote.watch") }
    static var reasonLabel: String { String(localized: "card.reason") }
    static var alternativeLabel: String { String(localized: "card.alternative") }

    static func voteCount(_ n: Int) -> String {
        // 显式用 %lld，与 String Catalog 的 key 完全对齐；
        // 用 "\(n)" 插值会让 Xcode 推断出不同的占位符形式，导致查不到译文。
        String(format: String(localized: "card.voteCount %lld"), n)
    }
    static var youPassed: String { String(localized: "card.youPassed") }
    static var youRejected: String { String(localized: "card.youRejected") }
    static var youWatched: String { String(localized: "card.youWatched") }
    static var voteNow: String { String(localized: "card.voteNow") }

    static func savedAmount(_ amount: String) -> String {
        String(format: String(localized: "card.saved %@"), amount)
    }
    static func passCount(_ n: Int) -> String {
        String(format: String(localized: "card.passCount %lld"), n)
    }
    static func rejectCount(_ n: Int) -> String {
        String(format: String(localized: "card.rejectCount %lld"), n)
    }
    static func viewAllReasons(_ n: Int) -> String {
        String(format: String(localized: "card.viewAllReasons %lld"), n)
    }

    // MARK: 广场空态
    static var plazaEmpty: String { String(localized: "plaza.empty") }

    // MARK: 发起页
    static var composeTitle: String { String(localized: "compose.title") }
    static var composeCancel: String { String(localized: "compose.cancel") }
    static var composeSubmit: String { String(localized: "compose.submit") }
    static var composeSubmitDisabled: String { String(localized: "compose.submitDisabled") }

    static var importTitle: String { String(localized: "import.title") }
    static var importSubtitle: String { String(localized: "import.subtitle") }
    static var importPick: String { String(localized: "import.pick") }
    static var importLowConfidence: String { String(localized: "import.lowConfidence") }
    static var importMediumConfidence: String { String(localized: "import.mediumConfidence") }
    static var importHighConfidence: String { String(localized: "import.highConfidence") }
    static var importFailed: String { String(localized: "import.failed") }

    static var fieldGoods: String { String(localized: "field.goods") }
    static var fieldGoodsPlaceholder: String { String(localized: "field.goodsPlaceholder") }
    static var fieldPrice: String { String(localized: "field.price") }
    static var fieldPricePlaceholder: String { String(localized: "field.pricePlaceholder") }
    static var fieldCategory: String { String(localized: "field.category") }
    static var fieldReason: String { String(localized: "field.reason") }
    static var fieldReasonPlaceholder: String { String(localized: "field.reasonPlaceholder") }
    static var fieldAlternative: String { String(localized: "field.alternative") }
    static var fieldAlternativePlaceholder: String {
        String(localized: "field.alternativePlaceholder")
    }
    static var reasonHint: String { String(localized: "field.reasonHint") }

    // MARK: 冷静期
    static var cooldownTitle: String { String(localized: "cooldown.title") }
    static var cooldown2h: String { String(localized: "cooldown.2h") }
    static var cooldown12h: String { String(localized: "cooldown.12h") }
    static var cooldown24h: String { String(localized: "cooldown.24h") }
    static var cooldown3d: String { String(localized: "cooldown.3d") }
    static var cooldownHint: String { String(localized: "cooldown.hint") }
    static var cooldownFlash: String { String(localized: "cooldown.flash") }
    static var cooldownNormal: String { String(localized: "cooldown.normal") }
    static var cooldownGolden: String { String(localized: "cooldown.golden") }
    static var cooldownLong: String { String(localized: "cooldown.long") }

    // MARK: 审批范围
    static var channelTitle: String { String(localized: "channel.title") }
    static var channelPlaza: String { String(localized: "channel.plaza") }
    static var channelGroup: String { String(localized: "channel.group") }
    static var channelPrivate: String { String(localized: "channel.private") }
    static var channelGroupPlaceholder: String {
        String(localized: "channel.groupPlaceholder")
    }

    // MARK: 投票弹窗
    static var sheetTitle: String { String(localized: "sheet.title") }
    static var sheetClose: String { String(localized: "sheet.close") }
    static var sheetSubmit: String { String(localized: "sheet.submit") }
    static var sheetPassHeadline: String { String(localized: "sheet.passHeadline") }
    static var sheetRejectHeadline: String { String(localized: "sheet.rejectHeadline") }
    static var sheetPassPlaceholder: String { String(localized: "sheet.passPlaceholder") }
    static var sheetRejectPlaceholder: String { String(localized: "sheet.rejectPlaceholder") }

    // MARK: 我的
    static var savedTotalLabel: String { String(localized: "mine.savedTotal") }
    static var streakTitle: String { String(localized: "mine.streak") }
    static var streakUnit: String { String(localized: "mine.dayUnit") }
    static var streakStart: String { String(localized: "mine.streakStart") }
    static var streakHint: String { String(localized: "mine.streakHint") }
    static var coolingSection: String { String(localized: "mine.coolingSection") }
    static var coolingEnded: String { String(localized: "mine.coolingEnded") }
    static func coolingLeft(h: Int, m: Int) -> String {
        h > 0
            ? String(format: String(localized: "mine.coolingLeftHM %lld %lld"), h, m)
            : String(format: String(localized: "mine.coolingLeftM %lld"), m)
    }
    static var stillWant: String { String(localized: "mine.stillWant") }
    static var neverMind: String { String(localized: "mine.neverMind") }

    static var whereSaved: String { String(localized: "mine.whereSaved") }
    static var historyTitle: String { String(localized: "mine.history") }
    static var historyEmpty: String { String(localized: "mine.historyEmpty") }

    // MARK: 通知
    static var notifyCoolingTitle: String { String(localized: "notify.cooldownTitle") }
    static func notifyCoolingBody(_ goods: String, _ price: String) -> String {
        String(format: String(localized: "notify.cooldownBody %@ %@"), goods, price)
    }
    static func notifySavedTitle(_ amount: String) -> String {
        String(format: String(localized: "notify.savedTitle %@"), amount)
    }
    static var notifySavedBody: String { String(localized: "notify.savedBody") }

    // MARK: 付费墙

    static var paywallOCRHeadline: String { String(localized: "paywall.ocrHeadline") }
    static var paywallOCRDetail: String { String(localized: "paywall.ocrDetail") }
    static var paywallCooldownHeadline: String { String(localized: "paywall.cooldownHeadline") }
    static var paywallCooldownDetail: String { String(localized: "paywall.cooldownDetail") }
    static var paywallGroupHeadline: String { String(localized: "paywall.groupHeadline") }
    static var paywallGroupDetail: String { String(localized: "paywall.groupDetail") }
    static var paywallReportHeadline: String { String(localized: "paywall.reportHeadline") }
    static var paywallReportDetail: String { String(localized: "paywall.reportDetail") }
    static var paywallMilestoneHeadline: String { String(localized: "paywall.milestoneHeadline") }
    static var paywallMilestoneDetail: String { String(localized: "paywall.milestoneDetail") }

    static var paywallTitle: String { String(localized: "paywall.title") }
    static var paywallSubtitle: String { String(localized: "paywall.subtitle") }
    static var paywallSubscribe: String { String(localized: "paywall.subscribe") }
    static var paywallTrial: String { String(localized: "paywall.trial") }
    static var paywallRestore: String { String(localized: "paywall.restore") }
    static var paywallLater: String { String(localized: "paywall.later") }
    static var paywallTerms: String { String(localized: "paywall.terms") }

    // MARK: 返利合规

    static var affiliateDisclosure: String { String(localized: "affiliate.disclosure") }
    static var affiliateAlternatives: String { String(localized: "affiliate.alternatives") }

    // MARK: 举报与拉黑（上架必需）

    static var reportAction: String { String(localized: "report.action") }
    static var reportTitle: String { String(localized: "report.title") }
    static var reportSubtitle: String { String(localized: "report.subtitle") }
    static var reportSpam: String { String(localized: "report.spam") }
    static var reportFraud: String { String(localized: "report.fraud") }
    static var reportAbuse: String { String(localized: "report.abuse") }
    static var reportAdult: String { String(localized: "report.adult") }
    static var reportOther: String { String(localized: "report.other") }
    static var reportDetailPlaceholder: String { String(localized: "report.detailPlaceholder") }
    static var reportSubmit: String { String(localized: "report.submit") }
    static var reportCancel: String { String(localized: "report.cancel") }
    static var reportThanks: String { String(localized: "report.thanks") }

    static var blockAction: String { String(localized: "block.action") }
    static var blockTitle: String { String(localized: "block.title") }
    static var blockConfirm: String { String(localized: "block.confirm") }
    static var blockDone: String { String(localized: "block.done") }
    static var blockManage: String { String(localized: "block.manage") }
    static var blockEmpty: String { String(localized: "block.empty") }
    static var blockUnblock: String { String(localized: "block.unblock") }

    static var moreAction: String { String(localized: "more.action") }
    static var supportTitle: String { String(localized: "support.title") }
    static var supportEmail: String { String(localized: "support.email") }
    static var supportHint: String { String(localized: "support.hint") }
    static var privacyPolicy: String { String(localized: "support.privacy") }
    static var termsOfUse: String { String(localized: "support.terms") }

    static var loadMore: String { String(localized: "plaza.loadMore") }

    static var shareAction: String { String(localized: "share.action") }

    static var planMonthly: String { String(localized: "plan.monthly") }
    static var planYearly: String { String(localized: "plan.yearly") }

    static func savePercent(_ p: Int) -> String {
        // 注意：key 里只用 %lld，百分号放在译文里。
        // 若把 %% 写进 key，String(localized:) 的查表会与 String(format:) 的转义互相打架。
        String(format: String(localized: "paywall.savePercent %lld"), p)
    }
}
