import SwiftUI
import SwiftData

/// 已拉黑列表。Apple UGC 审核要求屏蔽必须**可撤销**，
/// 只给拉黑不给解除同样会被拒。
struct BlockedListView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.modelContext) private var context
    @Query(sort: \BlockedAuthor.createdAt, order: .reverse) private var blocked: [BlockedAuthor]

    var body: some View {
        NavigationStack {
            Group {
                if blocked.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "hand.raised.slash")
                            .font(.system(size: 34))
                            .foregroundStyle(Theme.sub.opacity(0.45))
                        Text(L.blockEmpty)
                            .font(.system(size: 13))
                            .foregroundStyle(Theme.sub)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollView {
                        VStack(spacing: 10) {
                            ForEach(blocked) { author in
                                HStack(spacing: 11) {
                                    Circle()
                                        .fill(Theme.line.opacity(0.7))
                                        .frame(width: 28, height: 28)
                                        .overlay(
                                            Text(String(author.displayName.prefix(1)).uppercased())
                                                .font(.system(size: 12, weight: .semibold))
                                                .foregroundStyle(Theme.sub)
                                        )

                                    VStack(alignment: .leading, spacing: 1) {
                                        Text(author.displayName)
                                            .font(.system(size: 13.5, weight: .medium))
                                            .foregroundStyle(Theme.ink)
                                        Text(author.createdAt.formatted(date: .abbreviated, time: .omitted))
                                            .font(.system(size: 10.5))
                                            .foregroundStyle(Theme.sub)
                                    }

                                    Spacer()

                                    Button(L.blockUnblock) {
                                        ReportService.shared.unblock(
                                            authorKey: author.authorKey,
                                            context: context
                                        )
                                    }
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundStyle(Theme.reject)
                                    .buttonStyle(.plain)
                                }
                                .padding(13)
                                .background(RoundedRectangle(cornerRadius: 12).fill(.white))
                            }
                        }
                        .padding(16)
                    }
                }
            }
            .background(Theme.bg)
            .navigationTitle(L.blockManage)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(L.blockDone) { dismiss() }
                        .foregroundStyle(Theme.sub)
                }
            }
        }
    }
}
