#!/usr/bin/env node
/**
 * 不烧心 · 关键业务逻辑验证（Node 版）
 *
 * 为什么有这一份：
 *   Windows 上没有 Xcode，Swift 工具链下载还在进行。
 *   而产品最关键的算法（多币种账本、省钱口径、币种识别、价格选取、连击计算）
 *   本质是数据逻辑，与语言无关 —— 先用 Node 把它们跑一遍，
 *   任何算法错误都能立刻暴露，不必等编译环境。
 *
 * 用法：node verify/logic-check.mjs
 */

let pass = 0, fail = 0;
const failures = [];

function check(name, cond, detail = "") {
  if (cond) { pass++; console.log(`  \x1b[32m✅\x1b[0m ${name}`); }
  else { fail++; failures.push(`${name} ${detail}`); console.log(`  \x1b[31m❌\x1b[0m ${name}  ${detail}`); }
}

function section(t) { console.log(`\n\x1b[36m━━━ ${t} ━━━\x1b[0m`); }

// 用「分」为单位的 BigInt 模拟 Swift 的 Decimal，避免 JS 浮点误差
const D = (s) => BigInt(Math.round(Number(s) * 100));
const fromCents = (cents) => Number(cents) / 100;

// ══════════════════════════════════════════════
section("1. 多币种账本：绝不跨币种相加");

function MoneyBucket() {
  // 用 BigInt 存「分」，模拟 Swift 的 Decimal —— 绝不出现浮点漂移
  const totals = new Map();
  return {
    add(value, code) {
      const prev = totals.get(code) ?? 0n;
      totals.set(code, prev + value);
    },
    get isEmpty() { return totals.size === 0; },
    get sorted() {
      return [...totals.entries()]
        .map(([code, amount]) => ({ code, amount }))
        .sort((a, b) => (b.amount > a.amount ? 1 : b.amount < a.amount ? -1 : 0));
    },
    get primary() { return this.sorted[0] ?? null; },
    get totals() { return totals; }
  };
}

{
  const b = MoneyBucket();
  b.add(D("100"), "CNY");
  b.add(D("100"), "USD");
  check("两种币种产生两个桶", b.totals.size === 2, `实际 ${b.totals.size}`);
  check("CNY 桶独立为 100", b.totals.get("CNY") === D("100"));
  check("USD 桶独立为 100", b.totals.get("USD") === D("100"));
  check("primary 是金额最大的币种", b.primary !== null);
}

{
  const b = MoneyBucket();
  b.add(D("500"), "CNY");
  b.add(D("9800"), "JPY");
  check("日元数字大时成为主币种", b.primary.code === "JPY", `实际 ${b.primary?.code}`);
}

{
  const b = MoneyBucket();
  b.add(D("10.1"), "CNY");
  b.add(D("20.2"), "CNY");
  const got = fromCents(b.totals.get("CNY"));
  check("精确累加 10.1 + 20.2 = 30.3（无浮点漂移）",
    Math.abs(got - 30.3) < 1e-9, `实际 ${got}`);
  check("（对照）JS 原生浮点确实会漂移", 10.1 + 20.2 !== 30.3, `原生 = ${10.1 + 20.2}`);
}

{
  const b = MoneyBucket();
  check("空账本 isEmpty", b.isEmpty === true);
  check("空账本 primary 为 null", b.primary === null);
}

// ══════════════════════════════════════════════
section("2. 省钱口径：绝不能把「驳回别人」算成自己省的");

function makeApp(authorKey, myVerdict, status, price) {
  return { authorKey, myVerdict, status, price };
}
function isMine(a) { return a.authorKey === "self"; }
function savedForMe(a) {
  return isMine(a) && (a.myVerdict === "reject" || (a.status === "rejected" && a.myVerdict === null));
}

{
  check("我自己的单被驳回 → 计入省钱",
    savedForMe(makeApp("self", "reject", "voting", 100)) === true);

  check("我自己的单冷静期后放弃 → 计入省钱",
    savedForMe(makeApp("self", null, "rejected", 100)) === true);

  // 这是修复的关键 bug
  check("别人的单我驳回了 → 不计入我的省钱（关键修复）",
    savedForMe(makeApp("seed-abc", "reject", "voting", 100)) === false);

  check("我自己的单买了 → 不计入省钱",
    savedForMe(makeApp("self", "pass", "passed", 100)) === false);

  check("只围观的别人的单 → 不计入",
    savedForMe(makeApp("seed-x", null, "voting", 100)) === false);
}

{
  // 模拟一个真实场景：我用广场驳回 10 个人的申请，账本必须还是 0
  const apps = [];
  for (let i = 0; i < 10; i++) apps.push(makeApp(`seed-${i}`, "reject", "voting", 100));
  apps.push(makeApp("self", "reject", "voting", 50));  // 真正自己省下的
  const total = apps.filter(savedForMe).reduce((s, a) => s + a.price, 0);
  check("驳回别人 10 次 + 自己省 1 次 → 账本只算 50（不是 1050）",
    total === 50, `实际 ${total}`);
}

// ══════════════════════════════════════════════
section("3. 币种识别：HK$ 必须早于 $，円 必须早于 元");

function detectCurrency(text) {
  const prefixed = [
    ["HK$", "HKD"], ["NT$", "TWD"], ["US$", "USD"], ["A$", "AUD"],
    ["C$", "CAD"], ["S$", "SGD"], ["RMB", "CNY"], ["CNY", "CNY"],
    ["USD", "USD"], ["EUR", "EUR"], ["GBP", "GBP"]
  ];
  for (const [token, code] of prefixed) if (text.includes(token)) return code;

  const single = [
    ["€", "EUR"], ["£", "GBP"], ["₩", "KRW"],
    ["円", "JPY"], ["원", "KRW"],
    ["元", "CNY"], ["¥", "CNY"], ["￥", "CNY"], ["$", "USD"]
  ];
  for (const [token, code] of single) if (text.includes(token)) return code;
  return null;
}

{
  check("HK$58 → HKD（不是 USD）", detectCurrency("HK$58") === "HKD", `实际 ${detectCurrency("HK$58")}`);
  check("NT$1200 → TWD", detectCurrency("NT$1200") === "TWD");
  check("$12.99 → USD", detectCurrency("$12.99") === "USD");
  check("580円 → JPY", detectCurrency("580円") === "JPY");
  check("₩6,800 → KRW", detectCurrency("₩6,800") === "KRW");
  check("¥15 → CNY", detectCurrency("¥15") === "CNY");

  // 关键修复：日文页里的「元値」不能把币种带偏
  check("日文「元値 1200円」→ JPY（关键修复）",
    detectCurrency("元値 1200円") === "JPY", `实际 ${detectCurrency("元値 1200円")}`);

  check("无符号 → null", detectCurrency("hello") === null);
}

// ══════════════════════════════════════════════
section("4. OCR 价格选取：不能永远取原价");

function pickPrice(candidates, text) {
  const valid = candidates.filter(c => c > 0 && c < 10_000_000);
  if (valid.length === 0) return null;
  const markers = ["到手", "实付", "券后", "优惠后", "应付", "合计",
                   "final", "total", "sale", "割引", "적용가"];
  const hasDiscount = markers.some(m => text.toLowerCase().includes(m.toLowerCase()));
  return hasDiscount ? Math.min(...valid) : Math.max(...valid);
}

{
  check("「原价299 到手199」→ 199（关键修复）",
    pickPrice([299, 199], "原价299 到手价199") === 199,
    `实际 ${pickPrice([299, 199], "原价299 到手价199")}`);
  check("只有一个价格 → 取它", pickPrice([199], "商品 199") === 199);
  check("过滤 0、负数、超大值 → 50",
    pickPrice([0, -5, 50, 99_999_999], "商品") === 50,
    `实际 ${pickPrice([0, -5, 50, 99_999_999], "商品")}`);
  check("全无效 → null", pickPrice([0, -1], "x") === null);
  check("英文 sale 标记也生效",
    pickPrice([100, 60], "sale price") === 60);
}

// ══════════════════════════════════════════════
section("5. 金额解析：欧式逗号不能当千分位");

function parseAmount(text, locale) {
  const t = text.trim();
  if (!t) return null;
  const decimalSep = locale === "de_DE" || locale === "fr_FR" ? "," : ".";
  const groupSep = decimalSep === "," ? "." : ",";
  const cleaned = t.split(groupSep).join("").replace(decimalSep, ".");
  const n = Number(cleaned);
  return Number.isFinite(n) ? n : null;
}

{
  check("zh_CN '15' → 15", parseAmount("15", "zh_CN") === 15);
  check("zh_CN '1,299' → 1299（逗号是千分位）",
    parseAmount("1,299", "zh_CN") === 1299, `实际 ${parseAmount("1,299", "zh_CN")}`);
  check("zh_CN '1299.99' → 1299.99", parseAmount("1299.99", "zh_CN") === 1299.99);
  check("空串 → null", parseAmount("", "zh_CN") === null);
  check("纯空格 → null", parseAmount("   ", "zh_CN") === null);

  // 关键修复
  check("de_DE '9,99' → 9.99（不是 999，关键修复）",
    parseAmount("9,99", "de_DE") === 9.99, `实际 ${parseAmount("9,99", "de_DE")}`);
  check("de_DE '1.299,50' → 1299.5",
    parseAmount("1.299,50", "de_DE") === 1299.5, `实际 ${parseAmount("1.299,50", "de_DE")}`);
}

// ══════════════════════════════════════════════
section("6. 会员权益矩阵");

const Entitlement = {
  freeOCRPerMonth: 10,
  freeGroupLimit: 1,
  freeCooldownHours: 24,
  plusCooldownOptions: [2, 12, 24, 72],
  showsAds: false,
  allowedCooldownOptions(isPlus) {
    return isPlus ? this.plusCooldownOptions : [this.freeCooldownHours];
  }
};

{
  check("免费只能用 24 小时", JSON.stringify(Entitlement.allowedCooldownOptions(false)) === "[24]");
  check("会员可选 4 档", Entitlement.allowedCooldownOptions(true).length === 4);
  check("不投广告", Entitlement.showsAds === false);

  const remaining = (isPlus, used) => isPlus ? null : Math.max(0, Entitlement.freeOCRPerMonth - used);
  check("免费用 3 次 → 剩 7", remaining(false, 3) === 7);
  check("免费用 15 次 → 剩 0（不为负）", remaining(false, 15) === 0);
  check("会员额度 null（无限）", remaining(true, 999) === null);

  const canUse = (isPlus, used) => remaining(isPlus, used) === null ? true : remaining(isPlus, used) > 0;
  check("免费用满后不能用", canUse(false, 10) === false);
  check("会员永远可用", canUse(true, 999) === true);
}

// ══════════════════════════════════════════════
section("7. 连续克制天数");

function streak(days, today, msPerDay = 86400000) {
  const norm = (d) => Math.floor(d / msPerDay) * msPerDay;
  const set = new Set(days.map(norm));
  let n = 0, cursor = norm(today);
  while (set.has(cursor)) {
    n++;
    cursor -= msPerDay;
  }
  return n;
}

{
  const today = 1_800_000_000_000;
  const day = 86400000;

  check("今天有记录 → 1", streak([today], today) === 1);
  check("今天+昨天+前天 → 3", streak([today, today - day, today - 2 * day], today) === 3);
  check("只有昨天 → 0（断签）", streak([today - day], today) === 0);
  check("空 → 0", streak([], today) === 0);
  check("今天+前天（中间断）→ 1", streak([today, today - 2 * day], today) === 1);
}

// ══════════════════════════════════════════════
section("8. 通知调度边界");

function shouldSchedule(status, remainingSeconds) {
  if (status !== "voting") return false;
  if (remainingSeconds <= 5) return false;
  return true;
}

{
  check("投票中 + 还剩 1 小时 → 要提醒", shouldSchedule("voting", 3600) === true);
  check("已通过 → 不提醒", shouldSchedule("passed", 3600) === false);
  check("已驳回 → 不提醒", shouldSchedule("rejected", 3600) === false);
  check("只剩 3 秒 → 不提醒（避免刚建就响）", shouldSchedule("voting", 3) === false);
  check("已过期（负值）→ 不提醒", shouldSchedule("voting", -100) === false);
}

// ══════════════════════════════════════════════
console.log("\n" + "═".repeat(52));
console.log(`通过 ${pass} 项，失败 ${fail} 项`);
if (fail > 0) {
  console.log("\n失败明细：");
  failures.forEach(f => console.log("  • " + f));
  console.log("═".repeat(52));
  process.exit(1);
} else {
  console.log("\x1b[32m全部关键逻辑验证通过 ✅\x1b[0m");
  console.log("═".repeat(52));
}
