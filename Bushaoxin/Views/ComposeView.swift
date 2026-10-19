import SwiftUI
import SwiftData
import PhotosUI
import UIKit

struct ComposeView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss

    @State private var goods = ""
    @State private var priceText = ""
    @State private var category: SpendCategory = .other
    @State private var reason = ""
    @State private var alternative = ""
    @State private var channel = "plaza"
    @State private var groupName = ""
    @State private var cooldownHours: Double = 24
    /// 币种：默认跟随系统地区，识别到外币符号时自动切换
    @State private var currencyCode: String = MoneyFormatter.deviceCurrencyCode

    // 截图识别
    @State private var photoItem: PhotosPickerItem?
    @State private var isParsing = false
    @State private var parseNote: String?

    // 会员
    @State private var membership = Membership.shared
    @State private var paywallTrigger: PaywallTrigger?

    @FocusState private var focused: Field?
    enum Field: Hashable { case goods, price, reason, alt }

    private var price: Decimal { MoneyFormatter.parse(priceText) ?? 0 }
    private var canSubmit: Bool {
        !goods.trimmingCharacters(in: .whitespaces).isEmpty
        && price > 0
        && !reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 14) {
                    importBanner
                    basicsCard
                    reasonCard
                    cooldownCard
                    channelCard
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 100)
            }
            .background(Theme.bg)
            .scrollDismissesKeyboard(.interactively)
            .navigationTitle(L.composeTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button(L.composeCancel) { dismiss() }.foregroundStyle(Theme.sub)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button(L.post) { submit() }
                        .font(.system(size: 15, weight: .semibold))
                        .disabled(!canSubmit)
                }
            }
            .safeAreaInset(edge: .bottom) { submitBar }
            .onChange(of: photoItem) { _, item in
                guard let item else { return }
                Task { await handlePicked(item) }
            }
        }
        // 付费墙必须挂在最外层。
        // ComposeView 本身是由 PostButton 的 sheet 呈现的，
        // 如果在子视图（importBanner）上再挂 .sheet，iOS 会静默丢弃 —— 表现为点按钮没反应。
        .sheet(item: $paywallTrigger) { t in
            PaywallView(trigger: t)
        }
    }

    // MARK: 截图导入（我们的核心差异化）

    private var importBanner: some View {
        VStack(spacing: 10) {
            HStack(spacing: 11) {
                ZStack {
                    Circle().fill(Theme.amber.opacity(0.15)).frame(width: 38, height: 38)
                    Image(systemName: "text.viewfinder")
                        .font(.system(size: 17, weight: .medium))
                        .foregroundStyle(Color(red: 0.78, green: 0.56, blue: 0.08))
                }

                VStack(alignment: .leading, spacing: 2) {
                    Text(L.importTitle)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundStyle(Theme.ink)
                    Text(L.importSubtitle)
                        .font(.system(size: 11.5))
                        .foregroundStyle(Theme.sub)
                }

                Spacer()

                if isParsing {
                    ProgressView().scaleEffect(0.85)
                } else if !membership.canUseOCR {
                    // 免费额度用完：不隐藏入口，而是引导到付费墙
                    Button {
                        paywallTrigger = .ocrQuotaExhausted
                    } label: {
                        Text(L.importPick)
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(.white)
                            .padding(.horizontal, 14).padding(.vertical, 7)
                            .background(Capsule().fill(Theme.sub.opacity(0.55)))
                    }
                    .buttonStyle(.plain)
                } else {
                    PhotosPicker(selection: $photoItem, matching: .images) {
                        Text(L.importPick)
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(.white)
                            .padding(.horizontal, 14).padding(.vertical, 7)
                            .background(Capsule().fill(Theme.ink))
                    }
                }
            }

            if let note = parseNote {
                HStack(spacing: 5) {
                    Image(systemName: "sparkles").font(.system(size: 10))
                    Text(note).font(.system(size: 11.5))
                    Spacer()
                }
                .foregroundStyle(Color(red: 0.78, green: 0.56, blue: 0.08))
            }

            // 免费用户显示剩余次数，制造自然的付费动机
            if let remaining = membership.ocrRemaining {
                HStack(spacing: 4) {
                    Image(systemName: "number").font(.system(size: 9))
                    Text("\(remaining) / \(Entitlement.freeOCRPerMonth)")
                        .font(.system(size: 10.5))
                    Spacer()
                }
                .foregroundStyle(Theme.sub.opacity(0.8))
            }
        }
        .cardStyle(padding: 13)
    }

    // MARK: 基本信息

    private var basicsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            fieldLabel(L.fieldGoods, required: true)
            TextField(L.fieldGoodsPlaceholder, text: $goods)
                .focused($focused, equals: .goods)
                .textFieldStyle(.plain)
                .padding(11)
                .background(RoundedRectangle(cornerRadius: 11).fill(Color(red: 0.988, green: 0.984, blue: 0.976)))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.2))
                .submitLabel(.next)
                .onSubmit { focused = .price }

            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 12) {
                    fieldLabel(L.fieldPrice, required: true)
                    HStack(spacing: 4) {
                        // 币种符号随地区变化：¥ / $ / € / 円 / ₩
                        Text(MoneyFormatter.symbol(for: currencyCode))
                            .font(.system(size: 15, weight: .medium))
                            .foregroundStyle(Theme.sub)
                        TextField(L.fieldPricePlaceholder, text: $priceText)
                            .keyboardType(.decimalPad)
                            .focused($focused, equals: .price)
                            .textFieldStyle(.plain)
                            .font(.system(size: 17, weight: .semibold, design: .rounded))
                    }
                    .padding(11)
                    .background(RoundedRectangle(cornerRadius: 11).fill(Color(red: 0.988, green: 0.984, blue: 0.976)))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.2))
                }

                VStack(alignment: .leading, spacing: 12) {
                    fieldLabel(L.fieldCategory, required: false)
                    Picker(L.fieldCategory, selection: $category) {
                        ForEach(SpendCategory.allCases) { c in
                            Text(c.localizedName).tag(c)
                        }
                    }
                    .pickerStyle(.menu)
                    .tint(Theme.ink)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 6).padding(.vertical, 8)
                    .background(RoundedRectangle(cornerRadius: 11).fill(Color(red: 0.988, green: 0.984, blue: 0.976)))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.2))
                }
            }
        }
        .cardStyle()
    }

    // MARK: 理由

    private var reasonCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            fieldLabel(L.fieldReason, required: true)
            TextViewPlaceholder(
                text: $reason,
                placeholder: L.fieldReasonPlaceholder,
                minHeight: 72
            )

            fieldLabel(L.fieldAlternative, required: false)
            TextViewPlaceholder(
                text: $alternative,
                placeholder: L.fieldAlternativePlaceholder,
                minHeight: 54
            )

            HStack(spacing: 5) {
                Image(systemName: "info.circle").font(.system(size: 10))
                Text(L.reasonHint)
                    .font(.system(size: 11))
                    .fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: 0)
            }
            .foregroundStyle(Theme.sub)
        }
        .cardStyle()
    }

    // MARK: 冷静期（原产品只有口号，我们做成机制）

    private var cooldownCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                fieldLabel(L.cooldownTitle, required: false)
                Spacer()
                Text(cooldownLabel)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(Theme.ink)
            }

            // 非会员只开放 24 小时，其余档位显示锁标并引导升级
            if membership.isPlus {
                Picker(L.cooldownTitle, selection: $cooldownHours) {
                    Text(L.cooldown2h).tag(2.0)
                    Text(L.cooldown12h).tag(12.0)
                    Text(L.cooldown24h).tag(24.0)
                    Text(L.cooldown3d).tag(72.0)
                }
                .pickerStyle(.segmented)
            } else {
                Button {
                    paywallTrigger = .cooldownOptionLocked
                } label: {
                    HStack(spacing: 6) {
                        Text(L.cooldown24h)
                            .font(.system(size: 13.5, weight: .semibold))
                            .foregroundStyle(Theme.ink)
                        Image(systemName: "lock.fill")
                            .font(.system(size: 10))
                            .foregroundStyle(Theme.sub)
                        Spacer()
                        Text("Plus")
                            .font(.system(size: 10.5, weight: .semibold))
                            .foregroundStyle(.white)
                            .padding(.horizontal, 7).padding(.vertical, 2.5)
                            .background(Capsule().fill(Theme.amber))
                    }
                    .padding(11)
                    .background(RoundedRectangle(cornerRadius: 11).fill(Color(red: 0.988, green: 0.984, blue: 0.976)))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.2))
                }
                .buttonStyle(.plain)
            }

            HStack(spacing: 5) {
                Image(systemName: "bell.badge").font(.system(size: 10))
                Text(L.cooldownHint)
                    .font(.system(size: 11))
                    .fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: 0)
            }
            .foregroundStyle(Theme.sub)
        }
        .cardStyle()
    }

    private var cooldownLabel: String {
        switch cooldownHours {
        case 2: return L.cooldownFlash
        case 12: return L.cooldownNormal
        case 24: return L.cooldownGolden
        default: return L.cooldownLong
        }
    }

    // MARK: 审批范围

    private var channelCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            fieldLabel(L.channelTitle, required: false)
            Picker(L.channelTitle, selection: $channel) {
                Text(L.channelPlaza).tag("plaza")
                Text(L.channelGroup).tag("group")
                Text(L.channelPrivate).tag("private_")
            }
            .pickerStyle(.segmented)

            if channel == "group" {
                TextField(L.channelGroupPlaceholder, text: $groupName)
                    .textFieldStyle(.plain)
                    .padding(11)
                    .background(RoundedRectangle(cornerRadius: 11).fill(Color(red: 0.988, green: 0.984, blue: 0.976)))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.2))
            }
        }
        .cardStyle()
    }

    private var submitBar: some View {
        Button { submit() } label: {
            Text(canSubmit ? L.composeSubmit : L.composeSubmitDisabled)
                .font(.system(size: 15.5, weight: .semibold))
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 15)
                .background(
                    RoundedRectangle(cornerRadius: 14)
                        .fill(canSubmit ? Theme.ink : Theme.sub.opacity(0.35))
                )
                .lineLimit(1)
                .minimumScaleFactor(0.85)
        }
        .buttonStyle(.plain)
        .disabled(!canSubmit)
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.ultraThinMaterial)
    }

    private func fieldLabel(_ s: String, required: Bool) -> some View {
        HStack(spacing: 2) {
            Text(s).font(.system(size: 12.5, weight: .semibold)).foregroundStyle(Color(red: 0.29, green: 0.28, blue: 0.25))
            if required {
                Text("*").font(.system(size: 12.5, weight: .semibold)).foregroundStyle(Theme.reject)
            }
        }
    }

    // MARK: 动作

    private func handlePicked(_ item: PhotosPickerItem) async {
        isParsing = true
        parseNote = nil
        defer { isParsing = false }

        // 额度检查放在真正执行前，避免用户点了才提示
        guard membership.canUseOCR else {
            paywallTrigger = .ocrQuotaExhausted
            return
        }

        guard let data = try? await item.loadTransferable(type: Data.self),
              let image = UIImage(data: data),
              let parsed = await ReceiptParser.parse(image: image) else {
            parseNote = L.importFailed
            return
        }

        if let g = parsed.goods, goods.isEmpty { goods = g }
        if let p = parsed.price {
            // 用 Decimal 精确转换，避免 1299.99 这类价格被浮点吃掉精度。
            // 写回输入框时必须按**当前地区**格式化：德语区要写 "9,99" 而不是 "9.99"，
            // 否则用户看到的小数点和 MoneyFormatter.parse 认的不一致，一编辑就变成 999。
            let dec = Decimal(string: String(p)) ?? 0
            priceText = MoneyFormatter.inputText(dec)
        }
        // 识别到外币符号时自动切换记账币种（原产品爆火后紧急补的功能）
        if let code = parsed.currencyCode {
            currencyCode = code
        }

        switch parsed.confidence {
        case 0..<0.45: parseNote = L.importLowConfidence
        case 0.45..<0.85: parseNote = L.importMediumConfidence
        default: parseNote = L.importHighConfidence
        }
        // 只有真正识别成功才扣额度，失败的尝试不消耗用户配额
        membership.consumeOCR()
        Haptics.light()
    }

    @MainActor
    private func submit() {
        guard canSubmit else { return }

        let app = Application(
            goods: goods.trimmingCharacters(in: .whitespaces),
            price: price,
            currencyCode: currencyCode,
            categoryKey: category.rawValue,
            reason: reason.trimmingCharacters(in: .whitespacesAndNewlines),
            alternative: alternative.trimmingCharacters(in: .whitespacesAndNewlines),
            channel: channel,
            groupName: channel == "group" ? groupName : nil,
            cooldownHours: cooldownHours
        )
        context.insert(app)

        // 模拟网友：让用户立刻感受到"有人审了"
        if channel == "plaza" {
            CrowdSimulator.apply(to: app, in: context, count: Int.random(in: 2...4))
        }
        try? context.save()

        if channel != "private_" {
            NotificationService.scheduleCooldownReminder(for: app)
        }
        if SupabaseConfig.isConfigured {
            let now = ISO8601DateFormatter().string(from: Date())
            Task {
                try? await SupabaseClient.shared.signInAnonymouslyIfNeeded()
                try? await SupabaseClient.shared.submit(
                    ApplicationDTO(id: app.id,
                                   author_id: SupabaseClient.shared.currentUserID,
                                   goods: app.goods,
                                   price: NSDecimalNumber(decimal: app.price).doubleValue,
                                   category: app.categoryKey, reason: app.reason,
                                   alternative: app.alternative, channel: app.channel,
                                   status: app.status, passCount: app.passCount,
                                   rejectCount: app.rejectCount, createdAt: now)
                )
            }
        }

        Haptics.success()
        dismiss()
    }
}

// MARK: - 带占位符的多行输入

struct TextViewPlaceholder: View {
    @Binding var text: String
    let placeholder: String
    var minHeight: CGFloat = 72

    var body: some View {
        ZStack(alignment: .topLeading) {
            if text.isEmpty {
                Text(placeholder)
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.sub.opacity(0.75))
                    .padding(.horizontal, 15).padding(.vertical, 12)
                    .allowsHitTesting(false)
            }
            TextEditor(text: $text)
                .font(.system(size: 14))
                .scrollContentBackground(.hidden)
                .padding(.horizontal, 11).padding(.vertical, 6)
                .frame(minHeight: minHeight)
        }
        .background(RoundedRectangle(cornerRadius: 11).fill(Color(red: 0.988, green: 0.984, blue: 0.976)))
        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1.2))
    }
}
