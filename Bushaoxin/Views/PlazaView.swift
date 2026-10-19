import SwiftUI
import SwiftData

struct PlazaView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Application.createdAt, order: .reverse) private var all: [Application]
    /// 用 @Query 拿黑名单，而不是每次 body 求值都去 context.fetch
    @Query private var blockedAuthors: [BlockedAuthor]

    /// 分页：一次显示 20 条，滚动到底部再加载。
    /// 不分页的话，社区内容一多首屏就会卡。
    @State private var visibleCount = 20
    private let pageSize = 20

    /// 未投的排前面，已投的沉底 —— 让用户总有东西可审
    /// 同时过滤掉被举报隐藏的、以及被拉黑作者的内容
    private var sorted: [Application] {
        let blocked = Set(blockedAuthors.map(\.authorKey))
        return all
            .filter { $0.status == "voting" && !$0.isHidden && !blocked.contains($0.authorKey) }
            .sorted { a, b in
                if a.hasActed != b.hasActed { return !a.hasActed }   // 未投的在前
                return a.createdAt > b.createdAt                      // 同组内新的在前
            }
    }

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                header
                slogan

                // sorted 是 computed property，每次访问都会重新过滤排序。
                // 在 ForEach 里反复访问会重复计算，所以这里用 Group 包一层，
                // 保持单表达式 body（@ViewBuilder 下最稳），避免类型推断问题。
                content
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 24)
        }
        .scrollIndicators(.hidden)
        .background(Theme.bg)
        .refreshable { await refresh() }
    }

    /// 列表主体。抽成独立的 @ViewBuilder 属性，
    /// 这样 body 保持单表达式，深层嵌套也不会让类型推断超时。
    @ViewBuilder
    private var content: some View {
        let list = sorted
        if list.isEmpty {
            emptyState
        } else {
            ForEach(Array(list.prefix(visibleCount))) { app in
                ApprovalCard(app: app)
            }

            if visibleCount < list.count {
                loadMoreButton
            }
        }
    }

    private var loadMoreButton: some View {
        Button {
            withAnimation(.snappy(duration: 0.2)) {
                visibleCount += pageSize
            }
            Haptics.light()
        } label: {
            HStack(spacing: 6) {
                Image(systemName: "arrow.down")
                    .font(.system(size: 11, weight: .semibold))
                Text(L.loadMore)
                    .font(.system(size: 13, weight: .medium))
            }
            .foregroundStyle(Theme.sub)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 13)
            .background(RoundedRectangle(cornerRadius: 12).fill(.white))
        }
        .buttonStyle(.plain)
        .padding(.top, 2)
    }

    private var header: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text(L.appName)
                .font(.system(size: 26, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.ink)
            Text(L.tagline)
                .font(.system(size: 11))
                .foregroundStyle(Theme.sub)
                .padding(.horizontal, 8).padding(.vertical, 3)
                .background(Capsule().fill(.white))
                .overlay(Capsule().stroke(Theme.line, lineWidth: 1))
                .lineLimit(1)
                .minimumScaleFactor(0.8)
            Spacer()
        }
        .padding(.top, 8)
    }

    private var slogan: some View {
        HStack(spacing: 9) {
            Image(systemName: "hourglass")
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(Theme.amber)
            Text(L.slogan)
                .font(.system(size: 12.5))
                .foregroundStyle(Color(red: 0.54, green: 0.42, blue: 0.12))
                .fixedSize(horizontal: false, vertical: true)
            Spacer(minLength: 0)
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .background(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(LinearGradient(
                    colors: [Color(red: 1.0, green: 0.965, blue: 0.878),
                             Color(red: 0.992, green: 0.925, blue: 0.812)],
                    startPoint: .topLeading, endPoint: .bottomTrailing))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(Color(red: 0.965, green: 0.89, blue: 0.72), lineWidth: 1)
        )
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "tray")
                .font(.system(size: 34))
                .foregroundStyle(Theme.sub.opacity(0.5))
            Text(L.plazaEmpty)
                .font(.system(size: 13))
                .multilineTextAlignment(.center)
                .foregroundStyle(Theme.sub)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 60)
    }

    private func refresh() async {
        guard SupabaseConfig.isConfigured else { return }
        // 接后端时在此拉取远端广场并合并；未配置则静默跳过
        _ = try? await SupabaseClient.shared.fetchPlaza()
    }
}
