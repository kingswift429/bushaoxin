import SwiftUI
import UIKit

/// 分享卡片。
///
/// 这是整个产品的**病毒引擎**：每一次成功的驳回，都是一次免费传播。
/// 设计目标是"让用户忍不住截图"——
///   1. 竖版 9:16，直接适配小红书/朋友圈/Story
///   2. 把最扎心的那条理由放在正中间，字号最大
///   3. App 名只放底部一行，不做满屏水印（压水印会让人不想发）
struct ShareCard: View {
    let goods: String
    let priceText: String
    let reason: String
    let rejectCount: Int
    let passCount: Int

    /// 分享图的固定尺寸（iPhone 竖屏比例）
    private let cardWidth: CGFloat = 340

    var body: some View {
        VStack(spacing: 0) {
            header
            commentBlock
            statsRow
            footer
        }
        .frame(width: cardWidth)
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.996, green: 0.988, blue: 0.969),
                    Color(red: 0.976, green: 0.965, blue: 0.941)
                ],
                startPoint: .top, endPoint: .bottom
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(Color(red: 0.90, green: 0.88, blue: 0.84), lineWidth: 1)
        )
    }

    // MARK: 顶部：商品与金额

    private var header: some View {
        VStack(spacing: 7) {
            Text(goods)
                .font(.system(size: 19, weight: .semibold))
                .foregroundStyle(Color(red: 0.16, green: 0.15, blue: 0.13))
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .padding(.horizontal, 22)

            Text(priceText)
                .font(.system(size: 32, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.reject)
        }
        .padding(.top, 28)
        .padding(.bottom, 20)
    }

    // MARK: 中间：最扎心的理由（视觉重心）

    private var commentBlock: some View {
        VStack(spacing: 11) {
            Text("“")
                .font(.system(size: 30, weight: .bold, design: .serif))
                .foregroundStyle(Theme.reject.opacity(0.3))
                .frame(height: 16, alignment: .top)

            Text(reason)
                .font(.system(size: 17, weight: .medium))
                .foregroundStyle(Color(red: 0.20, green: 0.19, blue: 0.17))
                .multilineTextAlignment(.center)
                .lineSpacing(4)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.horizontal, 24)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 22)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(.white.opacity(0.75))
                .padding(.horizontal, 18)
        )
    }

    // MARK: 票数

    private var statsRow: some View {
        HStack(spacing: 0) {
            statItem(count: rejectCount, label: "驳回", color: Theme.reject)
            Divider().frame(height: 26).opacity(0.4)
            statItem(count: passCount, label: "通过", color: Theme.pass)
        }
        .padding(.vertical, 18)
    }

    private func statItem(count: Int, label: String, color: Color) -> some View {
        VStack(spacing: 3) {
            Text("\(count)")
                .font(.system(size: 20, weight: .bold, design: .rounded))
                .foregroundStyle(color)
            Text(label)
                .font(.system(size: 10.5))
                .foregroundStyle(Color(red: 0.45, green: 0.43, blue: 0.39))
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: 底部：App 名（克制，不做满屏水印）

    private var footer: some View {
        HStack(spacing: 6) {
            Image(systemName: "leaf.fill")
                .font(.system(size: 10))
                .foregroundStyle(Theme.pass)
            Text(L.appName)
                .font(.system(size: 12.5, weight: .semibold))
                .foregroundStyle(Color(red: 0.30, green: 0.28, blue: 0.25))
            Text("·")
                .font(.system(size: 12))
                .foregroundStyle(Color(red: 0.62, green: 0.60, blue: 0.56))
            Text(L.tagline)
                .font(.system(size: 11.5))
                .foregroundStyle(Color(red: 0.45, green: 0.43, blue: 0.39))
        }
        .padding(.bottom, 22)
        .padding(.top, 4)
    }
}

// MARK: - 渲染成图片

enum ShareCardRenderer {
    /// 把 SwiftUI 视图渲染成可直接分享的 UIImage。
    ///
    /// 用 ImageRenderer（iOS 16+），支持深色/浅色外的完整样式，
    /// 且不依赖把视图挂到窗口上。
    ///
    /// **必须设置 proposedSize**：
    /// 卡片里有 fixedSize 和自动换行的多行文本，不给建议尺寸时
    /// ImageRenderer 可能量不出高度，`uiImage` 直接返回 nil ——
    /// 表现就是"点分享没反应"，而且没有任何报错，极难排查。
    @MainActor
    static func render(
        _ view: some View,
        width: CGFloat = 340,
        scale: CGFloat = 3
    ) -> UIImage? {
        let renderer = ImageRenderer(content: view)
        renderer.scale = scale
        renderer.isOpaque = true
        // 宽度固定、高度自适应（卡片是竖版流式布局）
        renderer.proposedSize = ProposedViewSize(width: width, height: nil)
        return renderer.uiImage
    }
}

// MARK: - 系统分享面板

/// 包一层 Identifiable，方便用 .sheet(item:) 呈现
struct SharePayload: Identifiable {
    let id = UUID()
    let image: UIImage
}

struct ShareSheet: UIViewControllerRepresentable {
    let image: UIImage

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: [image], applicationActivities: nil)
    }

    func updateUIViewController(_ controller: UIActivityViewController, context: Context) {}
}
