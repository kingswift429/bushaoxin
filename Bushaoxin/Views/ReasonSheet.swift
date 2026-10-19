import SwiftUI

/// 写理由弹窗。
///
/// 强制写理由不是为了流程完整，而是产品灵魂：
/// 只投票会退化成玩梗，写了理由评审才真的在思考。
struct ReasonSheet: View {
    let verdict: String
    let app: Application
    @Binding var draft: String
    let onSubmit: () -> Void

    @Environment(\.dismiss) private var dismiss
    @FocusState private var focused: Bool

    private var isPass: Bool { verdict == "pass" }

    private var accent: Color { isPass ? Theme.pass : Theme.reject }

    private var suggestions: [String] {
        // 直接用当前语言的语料——快速选项和广场里的"网友口吻"保持一致
        let corpus = CrowdCorpus.current()
        let pool = isPass ? corpus.pass : corpus.reject
        return Array(pool.prefix(4))
    }

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 14) {
                HStack(spacing: 8) {
                    Image(systemName: isPass ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundStyle(accent)
                    Text(isPass ? L.sheetPassHeadline : L.sheetRejectHeadline)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundStyle(Theme.ink)
                        .lineLimit(2)
                    Spacer(minLength: 4)
                    Text(app.priceText)
                        .font(.system(size: 15, weight: .bold, design: .rounded))
                        .foregroundStyle(accent)
                        .fixedSize()
                }

                Text(app.goods)
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.sub)
                    .lineLimit(1)

                ZStack(alignment: .topLeading) {
                    if draft.isEmpty {
                        Text(isPass ? L.sheetPassPlaceholder : L.sheetRejectPlaceholder)
                            .font(.system(size: 13.5))
                            .foregroundStyle(Theme.sub.opacity(0.7))
                            .padding(.horizontal, 13).padding(.vertical, 12)
                            .allowsHitTesting(false)
                    }
                    TextEditor(text: $draft)
                        .font(.system(size: 13.5))
                        .focused($focused)
                        .scrollContentBackground(.hidden)
                        .padding(.horizontal, 9).padding(.vertical, 6)
                        .frame(minHeight: 88, maxHeight: 140)
                }
                .background(RoundedRectangle(cornerRadius: 11).fill(Color(red: 0.988, green: 0.984, blue: 0.976)))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.2))

                // 快速选项：降低写理由的成本，但不替代思考
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 7) {
                        ForEach(suggestions, id: \.self) { s in
                            Button { draft = s } label: {
                                Text(s)
                                    .font(.system(size: 11.5))
                                    .foregroundStyle(Theme.sub)
                                    .padding(.horizontal, 10).padding(.vertical, 6)
                                    .background(Capsule().stroke(Theme.line, lineWidth: 1))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }

                Spacer(minLength: 0)

                Button {
                    onSubmit()
                    dismiss()
                } label: {
                    Text(L.sheetSubmit)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundStyle(.white)
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(RoundedRectangle(cornerRadius: 13)
                            .fill(draft.trimmingCharacters(in: .whitespaces).isEmpty ? Theme.sub.opacity(0.35) : accent))
                }
                .buttonStyle(.plain)
                .disabled(draft.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            .padding(18)
            .background(Theme.bg)
            .navigationTitle(L.sheetTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(L.sheetClose) { dismiss() }.foregroundStyle(Theme.sub)
                }
            }
            .onAppear { focused = true }
        }
    }
}
