import SwiftUI
import SwiftData

struct ApprovalCard: View {
    @Bindable var app: Application
    @Environment(\.modelContext) private var context

    @State private var showReasonInput = false
    @State private var pendingVerdict: String?
    @State private var reasonDraft = ""
    @State private var showAllVotes = false
    @State private var showReport = false
    @State private var showBlockConfirm = false
    @State private var shareItem: SharePayload?

    @Query private var votes: [Vote]

    init(app: Application) {
        self.app = app
        let appID = app.id
        _votes = Query(
            filter: #Predicate<Vote> { $0.applicationID == appID },
            sort: \Vote.createdAt, order: .reverse
        )
    }

    /// 已表态（投票或围观）就收起按钮
    private var acted: Bool { app.hasActed || app.hasViewed }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {

            // ── 标题行 ──
            HStack(alignment: .top, spacing: 10) {
                Text(app.goods)
                    .font(.system(size: 16.5, weight: .semibold))
                    .foregroundStyle(Theme.ink)
                    .lineLimit(2)
                Spacer(minLength: 6)
                Text(app.priceText)
                    .font(.system(size: 17, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.reject)
                    .layoutPriority(1)

                // 举报 / 拉黑入口。Apple UGC 审核硬性要求，必须显眼可达。
                Menu {
                    Button {
                        showReport = true
                    } label: {
                        Label(L.reportAction, systemImage: "flag")
                    }
                    // 自己的内容不提供「拉黑自己」——那会把所有本地内容一起隐藏
                    if app.authorKey != "self" {
                        Button(role: .destructive) {
                            showBlockConfirm = true
                        } label: {
                            Label(L.blockAction, systemImage: "hand.raised")
                        }
                    }
                } label: {
                    Image(systemName: "ellipsis")
                        .font(.system(size: 14))
                        .foregroundStyle(Theme.sub)
                        .frame(width: 26, height: 26)
                        .contentShape(Rectangle())
                }
            }
            .padding(.bottom, 8)

            // ── 元信息 ──
            HStack(spacing: 6) {
                tag(app.categoryName)
                tag(L.voteCount(app.totalVotes))
                if app.channel == "group", let g = app.groupName {
                    tag(g)
                }
                Spacer(minLength: 0)
            }
            .padding(.bottom, 10)

            // ── 购买理由 ──
            (Text(L.reasonLabel + "  ").font(.system(size: 11.5)).foregroundColor(Theme.sub)
             + Text(app.reason).font(.system(size: 13.5)).foregroundColor(Color(red: 0.24, green: 0.23, blue: 0.20)))
                .lineSpacing(3)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.bottom, 8)

            // ── 替代方案 ──
            if !app.alternative.isEmpty {
                HStack(alignment: .top, spacing: 5) {
                    Text(L.alternativeLabel).font(.system(size: 11.5, weight: .semibold)).foregroundStyle(Theme.sub)
                    Text(app.alternative).font(.system(size: 12.5)).foregroundStyle(Theme.sub)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(9)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 9).fill(Color(red: 0.98, green: 0.976, blue: 0.965)))
            }

            // ── 投票按钮 / 已投结果 ──
            if acted {
                votedResult
                    .padding(.top, 12)
                    .transition(.opacity.combined(with: .move(edge: .bottom)))
            } else {
                actionButtons
                    .padding(.top, 13)
            }
        }
        .cardStyle()
        .onChange(of: showReasonInput) { _, showing in
            // 写理由时才解锁别人的观点（核心机制）
            if !showing { reasonDraft = "" }
        }
        .sheet(isPresented: $showReasonInput) {
            ReasonSheet(
                verdict: pendingVerdict ?? "reject",
                app: app,
                draft: $reasonDraft,
                onSubmit: { commit() }
            )
            .presentationDetents([.medium, .large])
            .presentationDragIndicator(.visible)
        }
        .sheet(isPresented: $showReport) {
            ReportSheet(target: app)
        }
        .confirmationDialog(
            L.blockTitle,
            isPresented: $showBlockConfirm,
            titleVisibility: .visible
        ) {
            Button(L.blockAction, role: .destructive) {
                guard app.authorKey != "self" else { return }
                ReportService.shared.block(
                    authorKey: app.authorKey,
                    displayName: app.authorKey,
                    context: context
                )
            }
            Button(L.reportCancel, role: .cancel) {}
        } message: {
            Text(L.blockConfirm)
        }
    }

    // MARK: 子视图

    private func tag(_ s: String) -> some View {
        Text(s)
            .font(.system(size: 11.5))
            .foregroundStyle(Theme.sub)
            .padding(.horizontal, 7).padding(.vertical, 2.5)
            .background(RoundedRectangle(cornerRadius: 6).fill(Color(red: 0.969, green: 0.965, blue: 0.953)))
    }

    private var actionButtons: some View {
        HStack(spacing: 8) {
            Button {
                pendingVerdict = "pass"; showReasonInput = true
            } label: {
                Text(L.pass).font(.system(size: 14.5, weight: .semibold))
                    .foregroundStyle(Theme.pass)
                    .frame(maxWidth: .infinity).padding(.vertical, 11)
                    .background(RoundedRectangle(cornerRadius: 11).fill(.white))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Color(red: 0.81, green: 0.91, blue: 0.855), lineWidth: 1.5))
            }
            .buttonStyle(.plain)

            Button {
                pendingVerdict = "reject"; showReasonInput = true
            } label: {
                Text(L.reject).font(.system(size: 14.5, weight: .semibold))
                    .foregroundStyle(Theme.reject)
                    .frame(maxWidth: .infinity).padding(.vertical, 11)
                    .background(RoundedRectangle(cornerRadius: 11).fill(.white))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Color(red: 0.949, green: 0.835, blue: 0.804), lineWidth: 1.5))
            }
            .buttonStyle(.plain)

            Button {
                // 围观：不解锁别人的观点，只把自己从"待投"里移出去
                app.hasViewed = true
                try? context.save()
                Haptics.light()
            } label: {
                Text(L.watch).font(.system(size: 14, weight: .medium))
                    .foregroundStyle(Theme.sub)
                    .frame(width: 68).padding(.vertical, 11)
                    .background(RoundedRectangle(cornerRadius: 11).fill(.white))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.5))
                    .lineLimit(1)
                    .minimumScaleFactor(0.85)
            }
            .buttonStyle(.plain)
        }
    }

    private var votedResult: some View {
        VStack(alignment: .leading, spacing: 9) {
            // 我的判断 + 结论
            if app.castRealVote {
                HStack(spacing: 6) {
                    Image(systemName: app.myVerdict == "pass" ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundStyle(app.myVerdict == "pass" ? Theme.pass : Theme.reject)
                        .font(.system(size: 13))
                    Text(app.myVerdict == "pass" ? L.youPassed : L.youRejected)
                        .font(.system(size: 12.5, weight: .medium))
                        .foregroundStyle(app.myVerdict == "pass" ? Theme.pass : Theme.reject)
                    Spacer()
                    if app.myVerdict == "reject" {
                        Text(L.savedAmount(app.priceText))
                            .font(.system(size: 12, weight: .semibold, design: .rounded))
                            .foregroundStyle(Theme.pass)
                    }
                }
            } else {
                // 只围观未表态：如实告知，并留一个反悔入口
                HStack(spacing: 6) {
                    Image(systemName: "eye")
                        .font(.system(size: 12)).foregroundStyle(Theme.sub)
                    Text(L.youWatched)
                        .font(.system(size: 12.5)).foregroundStyle(Theme.sub)
                        .lineLimit(2)
                    Spacer(minLength: 4)
                    Button(L.voteNow) {
                        app.hasViewed = false
                        try? context.save()
                    }
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(Theme.ink)
                    .fixedSize()
                }
            }

            // 票型进度条
            GeometryReader { geo in
                HStack(spacing: 0) {
                    Rectangle().fill(Theme.pass)
                        .frame(width: max(0, geo.size.width * app.passRatio))
                    Rectangle().fill(Theme.reject)
                }
                .clipShape(Capsule())
            }
            .frame(height: 7)

            HStack {
                Text(L.passCount(app.passCount)).font(.system(size: 11.5)).foregroundStyle(Theme.sub)
                Spacer()
                Text(L.rejectCount(app.rejectCount)).font(.system(size: 11.5)).foregroundStyle(Theme.sub)
            }

            // 别人的理由（投完之后才看得到）
            let shown = showAllVotes ? votes : Array(votes.prefix(2))
            if !shown.isEmpty {
                VStack(spacing: 6) { ForEach(shown) { CommentRow(vote: $0) } }
            }

            if votes.count > 2 && !showAllVotes {
                Button(L.viewAllReasons(votes.count)) { showAllVotes = true }
                    .font(.system(size: 12))
                    .foregroundStyle(Theme.sub)
            }

            // 分享 = 产品的病毒引擎。
            // 只有理由够扎心用户才想发，所以这里不催、不做弹窗诱导。
            if let best = topReason {
                Button {
                    prepareShare(reason: best)
                } label: {
                    HStack(spacing: 5) {
                        Image(systemName: "square.and.arrow.up")
                            .font(.system(size: 11))
                        Text(L.shareAction)
                            .font(.system(size: 12, weight: .medium))
                    }
                    .foregroundStyle(Theme.ink)
                    .padding(.horizontal, 12).padding(.vertical, 7)
                    .background(Capsule().fill(Theme.line.opacity(0.55)))
                }
                .buttonStyle(.plain)
                .padding(.top, 2)
            }
        }
        .sheet(item: $shareItem) { item in
            ShareSheet(image: item.image)
        }
    }

    /// 挑一条最扎心的理由作为分享卡正文：
    /// 优先被送花最多的，其次是最新的一条。
    private var topReason: String? {
        guard !votes.isEmpty else { return nil }
        return votes.max { a, b in
            if a.flowers != b.flowers { return a.flowers < b.flowers }
            return a.createdAt < b.createdAt
        }?.comment
    }

    private func prepareShare(reason: String) {
        let card = ShareCard(
            goods: app.goods,
            priceText: app.priceText,
            reason: reason,
            rejectCount: app.rejectCount,
            passCount: app.passCount
        )
        guard let image = ShareCardRenderer.render(card) else { return }
        Haptics.success()
        shareItem = SharePayload(image: image)
    }

    // MARK: 提交

    private func commit() {
        guard let verdict = pendingVerdict else { return }
        let text = reasonDraft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }

        app.myVerdict = verdict
        if verdict == "pass" { app.passCount += 1 } else { app.rejectCount += 1 }

        let v = Vote(applicationID: app.id, verdict: verdict, comment: text)
        context.insert(v)
        try? context.save()

        // 接后端时同步
        if SupabaseConfig.isConfigured {
            Task {
                try? await SupabaseClient.shared.signInAnonymouslyIfNeeded()
                try? await SupabaseClient.shared.castVote(
                    VoteDTO(id: v.id, applicationID: app.id,
                            voter_id: SupabaseClient.shared.currentUserID,
                            verdict: verdict, comment: text, flowers: 0,
                            createdAt: ISO8601DateFormatter().string(from: Date()))
                )
            }
        }

        if verdict == "reject" {
            Haptics.success()
            NotificationService.notifySaved(amount: app.price, code: app.currencyCode)
        } else {
            Haptics.light()
        }
    }
}

// MARK: - 一条审批理由

struct CommentRow: View {
    @Bindable var vote: Vote
    @Environment(\.modelContext) private var context

    var body: some View {
        HStack(alignment: .top, spacing: 7) {
            Circle()
                .fill(vote.verdict == "pass" ? Theme.pass.opacity(0.14) : Theme.reject.opacity(0.12))
                .frame(width: 20, height: 20)
                .overlay(
                    Image(systemName: vote.verdict == "pass" ? "hand.thumbsup.fill" : "hand.thumbsdown.fill")
                        .font(.system(size: 9))
                        .foregroundStyle(vote.verdict == "pass" ? Theme.pass : Theme.reject)
                )

            Text(vote.comment)
                .font(.system(size: 12.5))
                .foregroundStyle(Color(red: 0.28, green: 0.27, blue: 0.24))
                .fixedSize(horizontal: false, vertical: true)

            Spacer(minLength: 4)

            // 送花替代评论区，避免对骂（原产品的折中，我们保留并强化）
            Button {
                vote.flowers += 1
                try? context.save()
                Haptics.light()
            } label: {
                HStack(spacing: 2) {
                    Image(systemName: vote.flowers > 0 ? "leaf.fill" : "leaf")
                        .font(.system(size: 10))
                    if vote.flowers > 0 {
                        Text("\(vote.flowers)").font(.system(size: 10))
                    }
                }
                .foregroundStyle(vote.flowers > 0 ? Theme.pass : Theme.sub.opacity(0.6))
            }
            .buttonStyle(.plain)
        }
    }
}
