import SwiftUI

/// 品牌色：暖米底 + 墨黑主色 + 一抹"不烧心"的琥珀。
/// 刻意避开金融 App 的冷蓝（我们不碰钱），也避开消费 App 的高饱和红（我们不催买）。
enum Theme {
    static let bg = Color(red: 0.965, green: 0.960, blue: 0.949)          // #F6F5F2
    static let card = Color.white
    static let ink = Color(red: 0.110, green: 0.106, blue: 0.098)         // #1C1B19
    static let sub = Color(red: 0.545, green: 0.529, blue: 0.494)         // #8B877E
    static let line = Color(red: 0.914, green: 0.902, blue: 0.875)        // #E9E6DF

    static let pass = Color(red: 0.184, green: 0.620, blue: 0.420)        // #2F9E6B
    static let reject = Color(red: 0.831, green: 0.333, blue: 0.239)      // #D4553D
    static let amber = Color(red: 0.941, green: 0.706, blue: 0.161)       // #F0B429

    static let cardRadius: CGFloat = 18
    static let shadow = Color.black.opacity(0.06)
}

extension View {
    func cardStyle(padding: CGFloat = 16) -> some View {
        self
            .padding(padding)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.card)
            .clipShape(RoundedRectangle(cornerRadius: Theme.cardRadius, style: .continuous))
            .shadow(color: Theme.shadow, radius: 10, x: 0, y: 3)
    }
}
