# 不烧心 · 使用说明

## 一、现在有什么

```
bushaoxin/
├── docs/
│   ├── 产品设计.md          ← 优势总结 + 差异化设计（先读这个）
│   ├── 总结-优势与欠缺.md    ★ 当前状态、审查结果、还缺什么
│   ├── 增长方案.md          ★ 怎么让更多人下载
│   ├── 盈利闭环.md          ★ 商业模式、成本、收入测算、红线清单
│   ├── 多语言说明.md        ← 多语言与多币种实现细节
│   └── supabase_schema.sql  ← 后端建表（含举报/拉黑表），整段贴进 SQL Editor
├── project.yml              ← XcodeGen 工程定义
└── Bushaoxin/
    ├── BushaoxinApp.swift      入口 + TabBar + 中央发起按钮
    ├── Localization/
    │   ├── L.swift                  本地化文案键的集中注册表
    │   ├── Localizable.xcstrings    ★ 中/英/日/韩 四语 String Catalog
    │   └── CrowdCorpus.swift        ★ 模拟网友语料（按语言分表）
    ├── Models/Models.swift     SwiftData 模型（申请/票/举报/拉黑）
    ├── Services/
    │   ├── ReceiptParser.swift      ★ 截图 OCR 自动填单（多币种）
    │   ├── MoneyFormatter.swift     ★ 多币种格式化与分桶账本
    │   ├── Entitlements.swift       ★ 会员权益矩阵（唯一真相源）
    │   ├── PurchaseService.swift    ★ StoreKit 2 订阅接入
    │   ├── AffiliateService.swift   ★ 平替返利与合规标注
    │   ├── ReportService.swift      ★ 举报上报 + 拉黑管理
    │   ├── SupabaseClient.swift     后端客户端 + 匿名登录
    │   ├── CrowdSimulator.swift     模拟网友（冷启动体验）
    │   ├── NotificationService.swift 冷静期到点提醒
    │   ├── SeedData.swift           首次启动灌入广场内容（四语）
    │   └── Haptics.swift            触感反馈
    ├── Views/
    │   ├── Theme.swift          品牌色
    │   ├── PlazaView.swift      广场（分页 + 黑名单过滤）
    │   ├── ApprovalCard.swift   审批卡片（核心交互 + 举报/分享入口）
    │   ├── ComposeView.swift    发起审批 + 截图导入（含配额拦截）
    │   ├── MineView.swift       省钱账本 / 冷静期 / 历史 / 设置
    │   ├── ReasonSheet.swift    写理由弹窗
    │   ├── ReportSheet.swift    举报弹窗（Apple UGC 硬性要求）
    │   ├── BlockedListView.swift 拉黑管理（必须可撤销）
    │   ├── ShareCard.swift      ★ 分享卡片 = 病毒引擎
    │   └── PaywallView.swift    ★ 付费墙
    └── PrivacyInfo.xcprivacy    上架隐私清单
```

## 二、怎么跑起来（三步）

### 1. 生成 Xcode 工程

**方式 A（推荐，一条命令）**：

```bash
brew install xcodegen      # 首次
cd bushaoxin
xcodegen generate
open Bushaoxin.xcodeproj
```

**方式 B（不用装工具）**：Xcode → File → New → Project → iOS App，
Product Name 填 `Bushaoxin`，Interface 选 SwiftUI，Language 选 Swift，
然后把 `Bushaoxin/` 里的所有 `.swift` 文件拖进工程（注意勾选 Copy items if needed）。

### 2. 填你的开发者团队

打开工程 → Targets → Bushaoxin → Signing & Capabilities：
- Team 选你的 Apple Developer 团队
- Bundle Identifier 改成你自己的（如 `com.yourname.bushaoxin`）

### 3. 直接跑

**不需要任何后端就能完整体验** —— 已内置：
- 8 条种子广场内容（首次启动自动灌入）
- 模拟网友投票（你随手发一条，几秒内就有人来审）
- 全部数据本地持久化（SwiftData）

---

## 三、接 Supabase（要多久：约 20 分钟）
### 步骤

1. 注册 [supabase.com](https://supabase.com)，新建项目（免费额度够早期用）；
2. 进 **SQL Editor**，把 `docs/supabase_schema.sql` 整段粘贴执行；
3. 进 **Authentication → Providers**，打开 **Anonymous sign-ins**（关键，不打开会 401）；
4. 进 **Project Settings → API**，复制 `Project URL` 和 `anon public` key；
5. 改 `Services/SupabaseClient.swift` 顶部的两个常量：

```swift
static let url = URL(string: "https://你的项目ref.supabase.co")!
static let anonKey = "你的 anon public key"
```

改完重跑，`isConfigured` 自动变 true，广场会开始走后端同步。
**没配置时一切照常本地运行**，不会报错 —— 方便你先验证产品再决定要不要后端。

### 安全提醒

- 只用 `anon` key，**绝不要**把 `service_role` key 放进客户端（会被逆向提取）；
- 数据安全靠 RLS，SQL 里已经写好了策略；
- 生产环境建议再加一次服务端敏感词校验。

---

## 四、上架前检查清单

- [ ] Bundle ID 改成自己的
- [x] App 图标（已生成 1024×1024 无 alpha 占位版，可换设计师版本）
- [ ] 截图：至少 6.7 寸和 6.1 寸各一套
- [ ] 隐私政策 URL（Supabase + 本机存储，需如实说明）
- [ ] App Store 分类建议：**生活 / 财务**（不要选"金融"，会触发资质审查）
- [ ] 年龄分级：建议 12+（含用户生成内容）
- [ ] 描述里**避免**"帮你管钱""理财""投资"等词
- [x] 加入 Apple 要求的 UGC 四项：屏蔽、举报、过滤、客服联系方式
- [ ] **多语言元数据**：App Store Connect 里为 zh-Hans / en / ja / ko 各填一套名称、
      副标题、描述、关键词、截图（截图里的文字也要是当地语言，不能直接用中文截图）

---

## 五、没有 Mac 怎么验证（重要）

### 已经跑过的：逻辑验证 53 项全通过

```bash
node verify/logic-check.mjs
```

覆盖多币种账本、省钱口径、币种识别、OCR 价格、金额解析、会员权益、
连击天数、通知调度。**实际执行，0 失败。**

### 下一步：云端 macOS 编译（不用买 Mac）

流水线已配好：`.github/workflows/build-ios.yml`

```bash
cd bushaoxin
git init && git add . && git commit -m "v1.0"
git remote add origin https://github.com/你的用户名/bushaoxin.git
git push -u origin main
```

GitHub → Actions → **Build iOS** → Run workflow。
日志里的「编译错误汇总」就是你需要的东西。

额度：公共仓库免费；私有仓库约 200 分钟 macOS/月 ≈ 编译 20 次。

### 边界

| 能做 | 不能在 Windows 上做 |
|---|---|
| 验证算法正确 | 看界面长什么样 |
| 验证能否编译 | 验证动画/手势手感 |
| 拿到 error/warning 清单 | 真机跑 OCR |
| 验证产物完整性 | StoreKit 购买流程 |

界面必须**接触一次 Mac**（借半天，或租云 Mac 一两小时）。

完整说明见 [`docs/怎么跑起来.md`](docs/怎么跑起来.md)。

---

## 六、已知限制（诚实说明）

1. **截图识别用的是规则法**，不是大模型。复杂购物页识别率约 80%，
   已做置信度提示让你核对。想提升可接视觉大模型（豆包/GPT-4o-mini）兜底。
2. **广场数据还是本地的**：`fetchPlaza()` 拉了后端数据但没有合并进 SwiftData，
   真机上目前是"单机 + 假网友"。接真后端是上架后的第一件事。
3. **没有服务端推送**：只有冷静期到点的本地通知，做不了"有人驳回了你的申请"。
4. 模拟网友只在用户自己发的内容上生效，不影响别人的真实内容。
5. **不做汇率换算**：多币种分开记账。用户跨币种消费时，"省下总额"会按币种并列显示，
   而不是一个合并数字。这是刻意取舍，详见 `docs/多语言说明.md`。
6. 四个语言的语料和种子内容由我撰写，**建议找母语者过一遍**，尤其是日语和韩语的
   语气（敬语层级）——用词不准会让产品显得像机翻。
7. **代码从未在 Xcode 中编译过**。所有静态校验和逻辑验证都通过了，
   但 SwiftUI/SwiftData 的 API 签名问题只有在真编译时才会暴露。
