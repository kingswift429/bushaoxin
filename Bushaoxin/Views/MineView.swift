import SwiftUI
import SwiftData
import Combine

struct MineView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Application.createdAt, order: .reverse) private var all: [Application]

    @State private var showBlocked = false
    /// 统一时钟：所有冷静期行共享一个 Timer，避免 N 行 = N 个定时器
    @State private var now = Date()

    private var votedApps: [Application] { all.filter { $0.castRealVote } }

    /// 只统计「我自己省下的钱」：
    /// 我驳回自己的单，或冷静期结束后主动放弃。
    /// 绝不能把「我驳回别人」算进来——那省的是别人的钱。
    private var savedApps: [Application] { all.filter { $0.savedForMe } }

    /// 分币种累加，绝不跨币种相加
    private var savedBucket: MoneyBucket {
        var b = MoneyBucket()
        for app in savedApps { b.add(app.price, code: app.currencyCode) }
        return b
    }

    /// 连续克制天数：从今天往前数，每天至少省下一笔。
    /// 用 verdictAt（我做判断的时间）而不是 createdAt（申请创建时间）。
    private var streak: Int {
        let cal = Calendar.current
        let days = Set(
            savedApps.compactMap { $0.verdictAt ?? $0.createdAt }
                .map { cal.startOfDay(for: $0) }
        )
        var n = 0
        var cursor = cal.startOfDay(for: Date())
        while days.contains(cursor) {
            n += 1
            guard let prev = cal.date(byAdding: .day, value: -1, to: cursor) else { break }
            cursor = prev
        }
        return n
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        savedCard
                        streakCard
                    }
                    .padding(.horizontal, 16)
                }
                .padding(.horizontal, -16)

                coolingSection
                breakdownCard
                historySection
                settingsSection
            }
            .padding(.horizontal, 16)
            .padding(.top, 10)
            .padding(.bottom, 30)
        }
        .background(Theme.bg)
        .scrollIndicators(.hidden)
        .onReceive(Timer.publish(every: 30, on: .main, in: .common).autoconnect()) { t in
            now = t
        }
        .sheet(isPresented: $showBlocked) {
            BlockedListView()
        }
    }

    // MARK: 设置与支持（Apple UGC 审核要求：客服联系 + 拉黑管理）

    private var settingsSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionTitle(L.supportTitle)

            VStack(spacing: 0) {
                Button {
                    showBlocked = true
                } label: {
                    settingsRow("hand.raised", L.blockManage)
                }
                .buttonStyle(.plain)

                Divider().opacity(0.5).padding(.leading, 44)

                // 用 AppLinks 统一取地址；URL 为 nil 时退化成一个不可点的行，
                // 而不是 `URL(string:)!` 崩溃。
                if let mail = AppLinks.supportMailURL {
                    Link(destination: mail) {
                        settingsRow("envelope", L.supportEmail)
                    }
                    .buttonStyle(.plain)
                }

                Divider().opacity(0.5).padding(.leading, 44)

                if let url = AppLinks.privacyURL {
                    Link(destination: url) {
                        settingsRow("lock.shield", L.privacyPolicy)
                    }
                    .buttonStyle(.plain)
                }

                Divider().opacity(0.5).padding(.leading, 44)

                if let url = AppLinks.termsURL {
                    Link(destination: url) {
                        settingsRow("doc.text", L.termsOfUse)
                    }
                    .buttonStyle(.plain)
                }
            }
            .cardStyle(padding: 0)

            Text(L.supportHint)
                .font(.system(size: 11))
                .foregroundStyle(Theme.sub.opacity(0.85))
                .padding(.leading, 2)
        }
    }

    private func settingsRow(_ icon: String, _ title: String) -> some View {
        HStack(spacing: 11) {
            Image(systemName: icon)
                .font(.system(size: 13))
                .foregroundStyle(Theme.sub)
                .frame(width: 22)
            Text(title)
                .font(.system(size: 13.5))
                .foregroundStyle(Theme.ink)
            Spacer()
            Image(systemName: "chevron.right")
                .font(.system(size: 11, weight: .semibold))
                .foregroundStyle(Theme.line)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 13)
        .contentShape(Rectangle())
    }

    // MARK: 省钱卡（产品的情感锚点）

    private var savedCard: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(L.savedTotalLabel)
                .font(.system(size: 11.5))
                .foregroundStyle(.white.opacity(0.62))
                .tracking(0.5)

            Spacer(minLength: 10)

            if let primary = savedBucket.primary {
                HStack(alignment: .firstTextBaseline, spacing: 3) {
                    Text(MoneyFormatter.plainNumber(primary.amount))
                        .font(.system(size: 40, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)
                        .contentTransition(.numericText())
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                    Text(MoneyFormatter.symbol(for: primary.code))
                        .font(.system(size: 15, weight: .medium))
                        .foregroundStyle(.white.opacity(0.7))
                }

                // 多币种时，把其余币种以小字列出来，绝不合并成一个假数字
                if savedBucket.sorted.count > 1 {
                    Text(savedBucket.sorted.dropFirst().map {
                        MoneyFormatter.string($0.amount, code: $0.code)
                    }.joined(separator: " + "))
                        .font(.system(size: 10.5))
                        .foregroundStyle(.white.opacity(0.45))
                        .lineLimit(1)
                }
            } else {
                HStack(alignment: .firstTextBaseline, spacing: 3) {
                    Text("0")
                        .font(.system(size: 40, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)
                }
            }

            Spacer(minLength: 10)

            HStack(spacing: 4) {
                Image(systemName: "leaf.fill").font(.system(size: 9))
                Text(L.tagline)
                    .font(.system(size: 10.5))
                    .lineLimit(1)
            }
            .foregroundStyle(Theme.amber)
        }
        .padding(18)
        .frame(width: 250, height: 150, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(LinearGradient(
                    colors: [Color(red: 0.11, green: 0.106, blue: 0.098),
                             Color(red: 0.20, green: 0.19, blue: 0.17)],
                    startPoint: .topLeading, endPoint: .bottomTrailing))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(.white.opacity(0.07), lineWidth: 1)
        )
    }

    private var streakCard: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(L.streakTitle)
                .font(.system(size: 11.5))
                .foregroundStyle(Theme.sub)

            Spacer(minLength: 10)

            HStack(alignment: .firstTextBaseline, spacing: 3) {
                Text("\(streak)")
                    .font(.system(size: 40, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.ink)
                    .contentTransition(.numericText())
                Text(L.streakUnit).font(.system(size: 15, weight: .medium)).foregroundStyle(Theme.sub)
            }

            Spacer(minLength: 10)

            Text(streak == 0 ? L.streakStart : L.streakHint)
                .font(.system(size: 10.5))
                .foregroundStyle(Theme.sub)
                .lineLimit(2)
        }
        .padding(18)
        .frame(width: 150, height: 150, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(.white)
                .shadow(color: Theme.shadow, radius: 10, y: 3)
        )
    }

    // MARK: 冷静期到点待确认

    @ViewBuilder
    private var coolingSection: some View {
        let cooling = all.filter { $0.isCoolingDown }
        if !cooling.isEmpty {
            VStack(alignment: .leading, spacing: 10) {
                sectionTitle(L.coolingSection)
                ForEach(cooling) { app in
                    CooldownRow(app: app, now: now)
                }
            }
        }
    }

    // MARK: 分类分布

    private var breakdownCard: some View {
        // 分币种统计会导致跨币种不可比，这里只统计主币种的分布
        let mainCode = savedBucket.primary?.code
        let mainRejected = savedApps.filter { $0.currencyCode == mainCode }

        // 先聚合成数组再排序：Dictionary 本身无序，不能直接 ForEach
        var totals: [String: Decimal] = [:]
        for app in mainRejected {
            totals[app.categoryKey, default: 0] += app.price
        }
        let groups = totals
            .map { (key: $0.key, value: $0.value) }
            .sorted { $0.value > $1.value }

        return Group {
            if !groups.isEmpty {
                VStack(alignment: .leading, spacing: 11) {
                    sectionTitle(L.whereSaved)
                    ForEach(groups, id: \.key) { item in
                        CategoryBarRow(
                            label: SpendCategory(key: item.key)?.localizedName ?? item.key,
                            amount: item.value,
                            maxAmount: groups.first?.value ?? 1,
                            code: mainCode ?? "CNY"
                        )
                    }
                }
                .cardStyle()
            }
        }
    }

    // MARK: 历史

    private var historySection: some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionTitle(L.historyTitle)

            if votedApps.isEmpty {
                VStack(spacing: 10) {
                    Image(systemName: "doc.text.magnifyingglass")
                        .font(.system(size: 30)).foregroundStyle(Theme.sub.opacity(0.45))
                    Text(L.historyEmpty)
                        .font(.system(size: 12.5)).foregroundStyle(Theme.sub)
                }
                .frame(maxWidth: .infinity).padding(.vertical, 36)
                .cardStyle()
            } else {
                VStack(spacing: 0) {
                    ForEach(Array(votedApps.prefix(20).enumerated()), id: \.element.id) { idx, app in
                        HStack(spacing: 10) {
                            Image(systemName: app.myVerdict == "pass" ? "checkmark.circle.fill" : "xmark.circle.fill")
                                .foregroundStyle(app.myVerdict == "pass" ? Theme.pass : Theme.reject)
                                .font(.system(size: 15))

                            VStack(alignment: .leading, spacing: 2) {
                                Text(app.goods)
                                    .font(.system(size: 13.5, weight: .medium))
                                    .foregroundStyle(Theme.ink)
                                    .lineLimit(1)
                                Text(app.createdAt.formatted(date: .abbreviated, time: .shortened))
                                    .font(.system(size: 10.5))
                                    .foregroundStyle(Theme.sub)
                            }
                            Spacer()
                            Text(app.priceText)
                                .font(.system(size: 13, weight: .semibold, design: .rounded))
                                .foregroundStyle(app.myVerdict == "reject" ? Theme.pass : Theme.sub)
                                .lineLimit(1)
                                .minimumScaleFactor(0.8)
                        }
                        .padding(.vertical, 11)

                        if idx < min(votedApps.count, 20) - 1 {
                            Divider().opacity(0.5)
                        }
                    }
                }
                .cardStyle(padding: 14)
            }
        }
    }

    private func sectionTitle(_ s: String) -> some View {
        Text(s)
            .font(.system(size: 13, weight: .semibold))
            .foregroundStyle(Theme.ink)
            .padding(.horizontal, 2)
    }
}

// MARK: - 冷静期行

struct CooldownRow: View {
    @Bindable var app: Application
    /// 由 MineView 统一驱动，不再每行各起一个 Timer
    let now: Date
    @Environment(\.modelContext) private var context

    private var remainingText: String {
        let s = max(0, app.cooldownUntil.timeIntervalSince(now))
        if s <= 0 { return L.coolingEnded }
        let h = Int(s) / 3600, m = (Int(s) % 3600) / 60
        return L.coolingLeft(h: h, m: m)
    }

    /// 冷却是否已结束。统一用 now，避免"文本用 now、按钮用 Date()"两个时钟打架。
    private var isFinished: Bool {
        app.cooldownUntil.timeIntervalSince(now) <= 0
    }

    var body: some View {
        VStack(spacing: 11) {
            HStack {
                VStack(alignment: .leading, spacing: 3) {
                    Text(app.goods)
                        .font(.system(size: 13.5, weight: .medium))
                        .foregroundStyle(Theme.ink)
                    Text(remainingText)
                        .font(.system(size: 11))
                        .foregroundStyle(isFinished ? Theme.pass : Theme.amber)
                }
                Spacer()
                Text(app.priceText)
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.sub)
                    .lineLimit(1)
            }

            if isFinished {
                HStack(spacing: 8) {
                    Button {
                        // 还是想买 → 正式批准
                        app.status = "passed"
                        app.confirmedAfterCooldown = true
                        app.verdictAt = Date()
                        try? context.save()
                        // 已经决定了，别再弹"现在还想买吗"
                        NotificationService.cancelCooldownReminder(for: app)
                        Haptics.light()
                    } label: {
                        Text(L.stillWant)
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(Theme.ink)
                            .frame(maxWidth: .infinity).padding(.vertical, 9)
                            .background(RoundedRectangle(cornerRadius: 10).fill(Theme.line.opacity(0.7)))
                            .lineLimit(1)
                            .minimumScaleFactor(0.85)
                    }
                    .buttonStyle(.plain)

                    Button {
                        // 算了 → 记一笔省下
                        app.status = "rejected"
                        app.verdictAt = Date()
                        try? context.save()
                        NotificationService.cancelCooldownReminder(for: app)
                        Haptics.success()
                        NotificationService.notifySaved(amount: app.price, code: app.currencyCode)
                    } label: {
                        Text(L.neverMind)
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity).padding(.vertical, 9)
                            .background(RoundedRectangle(cornerRadius: 10).fill(Theme.pass))
                            .lineLimit(1)
                            .minimumScaleFactor(0.85)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .cardStyle(padding: 14)
    }
}

// MARK: - 分类占比条

/// 单个分类的占比条。
///
/// 为什么单独抽出来：
/// 原来它内联在 MineView 的 body 第 9 层嵌套里（ForEach > HStack >
/// GeometryReader > ZStack），且三元表达式里混用 Double 与整数字面量。
/// 这种组合是 Swift 类型检查超时的典型触发点 —— 编译会卡几十秒甚至报
/// "unable to type-check this expression in reasonable time"。
/// 拆成独立 View 后每层类型都能单独推断，编译速度和稳定性都更好。
private struct CategoryBarRow: View {
    let label: String
    let amount: Decimal
    let maxAmount: Decimal
    let code: String

    /// 明确声明为 Double，避免三元表达式里 `: 0` 引发类型推断歧义
    private var ratio: Double {
        guard maxAmount > 0 else { return 0 }
        let r = NSDecimalNumber(decimal: amount / maxAmount).doubleValue
        return max(0, min(1, r))
    }

    var body: some View {
        HStack(spacing: 10) {
            Text(label)
                .font(.system(size: 12.5))
                .foregroundStyle(Theme.ink)
                .frame(width: 62, alignment: .leading)
                .lineLimit(1)

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule().fill(Theme.line.opacity(0.6))
                    Capsule()
                        .fill(Theme.pass.opacity(0.75))
                        .frame(width: max(6, geo.size.width * ratio))
                }
            }
            .frame(height: 8)

            Text(MoneyFormatter.string(amount, code: code))
                .font(.system(size: 12, weight: .medium, design: .rounded))
                .foregroundStyle(Theme.sub)
                .frame(width: 76, alignment: .trailing)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
    }
}
