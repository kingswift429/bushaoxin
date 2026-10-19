import SwiftUI
import SwiftData

/// 举报弹窗。
///
/// App Store 审核指南 1.2 明确要求 UGC 产品具备举报入口与 24 小时内处理承诺。
/// 没有这个，第一次提审几乎必被拒。
struct ReportSheet: View {
    let target: Application

    @Environment(\.dismiss) private var dismiss
    @Environment(\.modelContext) private var context

    @State private var reason: ReportReason = .spam
    @State private var detail = ""
    @State private var submitted = false

    var body: some View {
        NavigationStack {
            Group {
                if submitted {
                    thanksView
                } else {
                    form
                }
            }
            .background(Theme.bg)
            .navigationTitle(L.reportTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button(L.reportCancel) { dismiss() }
                        .foregroundStyle(Theme.sub)
                }
            }
        }
    }

    private var form: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(L.reportSubtitle)
                    .font(.system(size: 12.5))
                    .foregroundStyle(Theme.sub)

                // 展示被举报内容，避免误报
                VStack(alignment: .leading, spacing: 4) {
                    Text(target.goods)
                        .font(.system(size: 13.5, weight: .medium))
                        .foregroundStyle(Theme.ink)
                        .lineLimit(2)
                    Text(target.reason)
                        .font(.system(size: 12))
                        .foregroundStyle(Theme.sub)
                        .lineLimit(2)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(12)
                .background(RoundedRectangle(cornerRadius: 11).fill(.white))

                VStack(spacing: 0) {
                    ForEach(ReportReason.allCases) { r in
                        Button {
                            reason = r
                        } label: {
                            HStack {
                                Text(r.displayName)
                                    .font(.system(size: 13.5))
                                    .foregroundStyle(Theme.ink)
                                Spacer()
                                Image(systemName: reason == r ? "largecircle.fill.circle" : "circle")
                                    .foregroundStyle(reason == r ? Theme.ink : Theme.line)
                            }
                            .padding(.horizontal, 13)
                            .padding(.vertical, 13)
                        }
                        .buttonStyle(.plain)

                        if r != ReportReason.allCases.last {
                            Divider().opacity(0.5).padding(.leading, 13)
                        }
                    }
                }
                .background(RoundedRectangle(cornerRadius: 12).fill(.white))

                TextField(L.reportDetailPlaceholder, text: $detail, axis: .vertical)
                    .lineLimit(3...5)
                    .font(.system(size: 13))
                    .padding(12)
                    .background(RoundedRectangle(cornerRadius: 11).fill(.white))

                Button {
                    submit()
                } label: {
                    Text(L.reportSubmit)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundStyle(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(RoundedRectangle(cornerRadius: 13).fill(Theme.reject))
                }
                .buttonStyle(.plain)
            }
            .padding(18)
        }
    }

    private var thanksView: some View {
        VStack(spacing: 14) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 44))
                .foregroundStyle(Theme.pass)
            Text(L.reportThanks)
                .font(.system(size: 14))
                .foregroundStyle(Theme.ink)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .task {
            // 用 .task 而不是 DispatchQueue.asyncAfter：
            // 用户若在这 2 秒内手动关掉弹窗，.task 会被取消，
            // 不会对一个已销毁的 presentation 调 dismiss()。
            // Task.sleep(nanoseconds:) 在 iOS 16 起已废弃，用 for: .seconds 写法。
            try? await Task.sleep(for: .seconds(2))
            if !Task.isCancelled { dismiss() }
        }
    }

    private func submit() {
        let report = Report(
            targetID: target.id,
            reasonKey: reason.rawValue,
            detail: detail.trimmingCharacters(in: .whitespacesAndNewlines)
        )
        context.insert(report)
        try? context.save()

        // 本地先隐藏，不等服务端——用户举报后不该再看到这条
        target.isHidden = true
        try? context.save()

        Haptics.success()
        submitted = true

        // 联网时异步上报（失败保留在本地待重试）
        Task { await ReportService.shared.flush(context: context) }
    }
}
