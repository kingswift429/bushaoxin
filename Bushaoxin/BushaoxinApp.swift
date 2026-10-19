import SwiftUI
import SwiftData

@main
struct BushaoxinApp: App {
    let container: ModelContainer

    init() {
        do {
            let schema = Schema([Application.self, Vote.self, Report.self, BlockedAuthor.self])
            let config = ModelConfiguration(schema: schema, isStoredInMemoryOnly: false)
            container = try ModelContainer(for: schema, configurations: config)

            // 在第一次 body 求值之前灌种子数据。
            // 放在 .onAppear 里会和 @Query 的首次查询赛跑：
            // PlazaView 可能先拿到空数组渲染一帧，或 onAppear 多次调用导致重复灌入。
            let ctx = ModelContext(container)
            SeedData.seedIfNeeded(ctx)
        } catch {
            fatalError("SwiftData 初始化失败：\(error)")
        }
    }

    var body: some Scene {
        WindowGroup {
            RootView()
        }
        .modelContainer(container)
    }
}

struct RootView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.scenePhase) private var scenePhase
    @State private var tab: Tab = .plaza

    enum Tab: Hashable { case plaza, mine }

    var body: some View {
        ZStack {
            Theme.bg.ignoresSafeArea()

            VStack(spacing: 0) {
                switch tab {
                case .plaza: PlazaView()
                case .mine:  MineView()
                }

                TabBar(selection: $tab)
            }
        }
        .preferredColorScheme(.light)
        .task {
            NotificationService.requestAuthorization()
            // 未配置 Supabase 时静默跳过，纯本地也能完整使用
            if SupabaseConfig.isConfigured {
                try? await SupabaseClient.shared.signInAnonymouslyIfNeeded()
            }
            // 校正会员状态：用户可能在别的设备上买过
            await PurchaseService.shared.refreshEntitlement()
        }
        .onChange(of: scenePhase) { _, phase in
            // 回前台时重新校验：用户可能刚在系统设置里取消或续订
            if phase == .active {
                Task { await PurchaseService.shared.refreshEntitlement() }
            }
        }
    }
}

// MARK: - 自定义 TabBar

struct TabBar: View {
    @Binding var selection: RootView.Tab
    var body: some View {
        HStack {
            item(.plaza, L.tabPlaza, "square.grid.2x2")
            item(.plaza, "", "")   // 占位，中间留给发起按钮
            item(.mine, L.tabMine, "person")
        }
        .overlay(alignment: .center) {
            PostButton()
        }
        .padding(.top, 10)
        .padding(.horizontal, 30)
        .background(.ultraThinMaterial)
        .overlay(alignment: .top) { Divider().opacity(0.4) }
    }

    private func item(_ t: RootView.Tab, _ title: String, _ icon: String) -> some View {
        Button {
            withAnimation(.snappy(duration: 0.18)) { selection = t }
        } label: {
            VStack(spacing: 3) {
                Image(systemName: icon).font(.system(size: 19))
                if !title.isEmpty {
                    Text(title).font(.system(size: 11, weight: selection == t ? .semibold : .regular))
                }
            }
            .foregroundStyle(selection == t && !title.isEmpty ? Theme.ink : Theme.sub)
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.plain)
        .disabled(title.isEmpty)
        .opacity(title.isEmpty ? 0 : 1)
    }
}

/// 中央发起按钮 —— 产品最重要的动作，做成最显眼的位置
struct PostButton: View {
    @State private var showSheet = false

    var body: some View {
        Button { showSheet = true } label: {
            ZStack {
                Circle()
                    .fill(Theme.ink)
                    .frame(width: 56, height: 56)
                    .shadow(color: Theme.ink.opacity(0.25), radius: 10, y: 4)
                Image(systemName: "plus")
                    .font(.system(size: 22, weight: .semibold))
                    .foregroundStyle(.white)
            }
        }
        .buttonStyle(.plain)
        .sheet(isPresented: $showSheet) {
            ComposeView()
        }
    }
}
