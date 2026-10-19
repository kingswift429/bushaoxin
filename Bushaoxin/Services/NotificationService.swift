import Foundation
import UserNotifications

/// 本地通知。
///
/// 这是 App 相对小程序的关键优势之一：冷静期到点必须能"叫醒"用户，
/// 小程序只能靠订阅消息模板，用户极易流失。
enum NotificationService {

    static func requestAuthorization() {
        UNUserNotificationCenter.current()
            .requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }

    /// 冷静期结束提醒："现在还想买吗？"
    static func scheduleCooldownReminder(for app: Application) {
        // 只有还在投票中的申请才需要提醒。
        // 原写法 max(5, remaining) 后再判 > 5 是死条件，且会把已过期的单也排进去。
        guard app.status == "voting" else { return }
        let remaining = app.cooldownRemaining
        guard remaining > 5 else { return }

        let content = UNMutableNotificationContent()
        content.title = L.notifyCoolingTitle
        // 商品名可能含换行或极长，通知中心会截断
        content.body = L.notifyCoolingBody(String(app.goods.prefix(30)), app.priceText)
        content.sound = .default

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: remaining, repeats: false)
        let req = UNNotificationRequest(
            identifier: "cooldown-\(app.id.uuidString)",
            content: content,
            trigger: trigger
        )
        UNUserNotificationCenter.current().add(req)
    }

    static func cancelCooldownReminder(for app: Application) {
        UNUserNotificationCenter.current()
            .removePendingNotificationRequests(withIdentifiers: ["cooldown-\(app.id.uuidString)"])
    }

    /// 驳回省钱的即时反馈（1 秒后弹，制造"刚刚发生了什么"的小惊喜）
    static func notifySaved(amount: Decimal, code: String) {
        let content = UNMutableNotificationContent()
        content.title = L.notifySavedTitle(MoneyFormatter.string(amount, code: code))
        content.body = L.notifySavedBody
        content.sound = nil

        let req = UNNotificationRequest(
            identifier: "saved-\(UUID().uuidString)",
            content: content,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 1.2, repeats: false)
        )
        UNUserNotificationCenter.current().add(req)
    }
}
