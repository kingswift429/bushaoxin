import SwiftUI
import StoreKit

/// 付费墙。
///
/// 设计原则：只从用户"已经想要某个东西"的时刻进入，不做主动弹窗。
/// 默认选中**年费**（对照月费突出省 41%），并强调 7 天试用降低决策门槛。
struct PaywallView: View {
    let trigger: PaywallTrigger

    @Environment(\.dismiss) private var dismiss
    @State private var selected: Plan = .yearly
    @State private var purchase = PurchaseService.shared

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 18) {
                    header
                    benefits
                    planPicker
                    subscribeButton
                    footer
                }
                .padding(.horizontal, 20)
                .padding(.top, 12)
                .padding(.bottom, 30)
            }
            .background(Theme.bg)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(L.paywallLater) { dismiss() }
                        .foregroundStyle(Theme.sub)
                }
            }
            .task {
                // 只加载商品。权益校验交给 RootView 启动/回前台统一做，
                // 这里重复调用会在沙盒环境把刚买的会员误撤销。
                if purchase.products.isEmpty {
                    await purchase.loadProducts()
                }
            }
        }
    }

    // MARK: 头部

    private var header: some View {
        VStack(spacing: 10) {
            ZStack {
                Circle()
                    .fill(LinearGradient(
                        colors: [Theme.amber.opacity(0.22), Theme.amber.opacity(0.08)],
                        startPoint: .topLeading, endPoint: .bottomTrailing))
                    .frame(width: 62, height: 62)
                Image(systemName: "leaf.fill")
                    .font(.system(size: 25))
                    .foregroundStyle(Color(red: 0.78, green: 0.56, blue: 0.08))
            }

            Text(L.paywallTitle)
                .font(.system(size: 22, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.ink)

            Text(trigger.headline)
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(Theme.ink)
                .multilineTextAlignment(.center)

            Text(trigger.detail)
                .font(.system(size: 12.5))
                .foregroundStyle(Theme.sub)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.top, 6)
        .padding(.bottom, 4)
    }

    // MARK: 权益列表

    private var benefits: some View {
        VStack(spacing: 0) {
            benefitRow("text.viewfinder", L.importTitle)
            Divider().opacity(0.4)
            benefitRow("hourglass", L.cooldownTitle)
            Divider().opacity(0.4)
            benefitRow("person.3.fill", L.channelGroup)
            Divider().opacity(0.4)
            benefitRow("chart.pie.fill", L.whereSaved)
            Divider().opacity(0.4)
            benefitRow("square.and.arrow.up", L.historyTitle)
        }
        .cardStyle(padding: 4)
    }

    private func benefitRow(_ icon: String, _ title: String) -> some View {
        HStack(spacing: 11) {
            Image(systemName: icon)
                .font(.system(size: 14))
                .foregroundStyle(Theme.ink)
                .frame(width: 22)
            Text(title)
                .font(.system(size: 13.5))
                .foregroundStyle(Theme.ink)
            Spacer()
            Image(systemName: "checkmark")
                .font(.system(size: 12, weight: .bold))
                .foregroundStyle(Theme.pass)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 13)
    }

    // MARK: 套餐

    private var planPicker: some View {
        HStack(spacing: 10) {
            ForEach(Plan.allCases) { plan in
                planCard(plan)
            }
        }
    }

    private func planCard(_ plan: Plan) -> some View {
        let isOn = selected == plan
        return Button {
            withAnimation(.snappy(duration: 0.15)) { selected = plan }
        } label: {
            VStack(spacing: 5) {
                Text(plan.caption)
                    .font(.system(size: 11.5))
                    .foregroundStyle(isOn ? Theme.ink.opacity(0.7) : Theme.sub)

                Text(purchase.localizedPrice(for: plan) ?? plan.displayPrice)
                    .font(.system(size: 24, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.ink)

                if plan.savingsPercent > 0 {
                    Text(L.savePercent(plan.savingsPercent))
                        .font(.system(size: 10.5, weight: .semibold))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 8).padding(.vertical, 2.5)
                        .background(Capsule().fill(Theme.reject))
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: 15, style: .continuous)
                    .fill(isOn ? Theme.amber.opacity(0.10) : .white)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 15, style: .continuous)
                    .stroke(isOn ? Theme.amber : Theme.line, lineWidth: isOn ? 2 : 1.2)
            )
        }
        .buttonStyle(.plain)
    }

    // MARK: 订阅

    private var subscribeButton: some View {
        VStack(spacing: 9) {
            Button {
                Task {
                    let ok = await purchase.purchase(selected)
                    if ok { dismiss() }
                }
            } label: {
                HStack {
                    if purchase.isPurchasing {
                        ProgressView().tint(.white)
                    } else {
                        Text("\(L.paywallSubscribe) · \(purchase.localizedPrice(for: selected) ?? selected.displayPrice)")
                            .font(.system(size: 15.5, weight: .semibold))
                    }
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 15)
                .background(RoundedRectangle(cornerRadius: 14).fill(Theme.ink))
            }
            .buttonStyle(.plain)
            .disabled(purchase.isPurchasing)

            Text(L.paywallTrial)
                .font(.system(size: 11.5))
                .foregroundStyle(Theme.sub)

            if let err = purchase.lastError {
                Text(err)
                    .font(.system(size: 11))
                    .foregroundStyle(Theme.reject)
                    .multilineTextAlignment(.center)
            }
        }
    }

    private var footer: some View {
        VStack(spacing: 7) {
            Button(L.paywallRestore) {
                Task { await purchase.restore() }
            }
            .font(.system(size: 12))
            .foregroundStyle(Theme.sub)

            Text(L.paywallTerms)
                .font(.system(size: 10.5))
                .foregroundStyle(Theme.sub.opacity(0.8))
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.top, 4)
    }
}
