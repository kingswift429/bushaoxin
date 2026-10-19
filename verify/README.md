# 验证工具

开发机是 Windows，没有 Xcode。这个目录记录**在没有 Mac 的情况下，实际验证到了什么程度**。

---

## 已经跑的：逻辑验证 53 项全通过

```bash
node verify/logic-check.mjs
```

实际执行结果：**53 项断言，0 失败。**

| 模块 | 验证内容 | 为什么必须验 |
|---|---|---|
| 多币种账本 | 分币种累加，绝不跨币种相加 | ¥100 + $100 被显示成 ¥200 是最尴尬的本地化 bug |
| 省钱口径 | 只有「自己的单 + 最终没买」计入 | 算错会虚报用户的省钱金额 |
| 币种识别 | `HK$` 早于 `$`，`円` 早于 `元` | 顺序错了香港价变美元、日本价变人民币 |
| OCR 价格 | 有优惠标记时取实付价 | 取原价会夸大会省下的金额 |
| 金额解析 | 欧式 `9,99` = 9.99 而非 999 | 无脑删逗号放大 100 倍 |
| 会员权益 | 免费/会员的额度与权限边界 | 越权或额度算错直接影响收入 |
| 连击天数 | 断签、跨天、空记录 | 断一天还显示连击，用户觉得被骗 |
| 通知调度 | 已决策/已过期不提醒 | 刚建单就响铃会被骂 |

其中 5 项专门验证**这次修复的 bug**，并且带「反例断言」确认修复前后行为确实不同：

- 驳回别人的单**不**计入自己的省钱（驳回 10 条 + 自己省 1 条，账本只算 50 而不是 1050）
- 德语 `9,99` 解析为 9.99（旧逻辑得到 999）
- 日文「元値 1200円」识别为 JPY（旧逻辑得到 CNY）
- 「原价299 到手199」取 199（旧逻辑取 299）
- 通知在已决策状态下不调度

---

## 第二层：iOS 17 API 兼容性检查

```bash
python verify/ios17_check.py
```

扫描 26 个 Swift 文件，专门查**会让 xcodebuild 失败但人眼看不出**的问题：

| 检查项 | 为什么重要 |
|---|---|
| `#Predicate` 对可选属性做 `nil` 比较 | SwiftData 已知缺陷，会编译失败或运行时报错 |
| `#Predicate` 里用 `.count` | 不支持，必定失败 |
| 用了 iOS 18+ API（如新的 `Tab` 类型） | 部署目标 iOS 17 会直接编译失败 |
| `ForEach` 直接吃 `prefix()` 返回的 Slice | 需要 `Array()` 包一层 |
| **import 缺失**（用了 `@Model` 但没 `import SwiftData` 等） | 必定编译失败 |
| 强制解包 `!` / `try!` / `as!` | 运行期崩溃 |
| `onChange` 单参数闭包 | iOS 17 已废弃，会报警告 |
| `Task.sleep(nanoseconds:)` | iOS 16 起废弃 |
| `String(localized:)` 里含插值 | 查不到译文 |

结果（本次运行）：**E 级 0 个，W 级 7 个（均已人工确认为安全）**。

### 这个检查器已经办到的事

它抓出的问题中，有 3 个是真实缺陷，已修：

1. **`SupabaseClient.url.host!`** —— URL 解析异常时崩溃。已改成 `guard let host`
2. **`#Predicate { $0.syncedAt == nil }`** —— SwiftData 已知缺陷。已改成取回后内存过滤
3. **`Task.sleep(nanoseconds:)`** —— 已废弃 API。已改成 `Task.sleep(for: .seconds(2))`

### 误报的处理

第一版检查器报了 8 个 E，其中 5 个是误报。我没有直接"全改"，
而是**修正规则本身**——把注释里的示例代码、常量字面量 `URL(...)!`、
正确的两参数 `onChange` 都排除掉。

一个会误报的检查器比没有更糟：它会训练你忽略真正的错误。

---

## 第三层：编译期类型审查（人工 + agent）

`.py` 检查器只能查模式，查不了「这个函数的参数类型对不对」。
所以又请了一个 agent 做逐文件深度审查，专找：

- 类型不匹配、成员不存在、可选值误用
- `@MainActor` 隔离违规
- 初始化器参数标签错误
- ViewBuilder 单块超过 10 个子视图
- `Decimal` 与 `Int`/`Double` 混用

已据此修复的问题：

| 问题 | 文件 | 修法 |
|---|---|---|
| `var body` 里用 `let` + `return`，@ViewBuilder 类型推断不稳 | PlazaView | 抽成独立的 `@ViewBuilder private var content` |
| 第 9 层嵌套 `ForEach > HStack > GeometryReader > ZStack`，三元表达式混用 Double 和整数字面量 | MineView | 抽出 `CategoryBarRow` 独立 View，`ratio` 显式声明 `Double` |
| `URL(string:)!` 硬编码三处，域名还是占位符 | MineView | 集中到 `AppLinks`，URL 为 nil 时退化为不显示 |

---

## 试过但放弃的：Windows Swift 工具链

我尝试安装 Swift 工具链（`winget install Swift.Toolchain`，下载 2 GB），
想在 Windows 上直接编译验证。**放弃了**，原因如实说明：

1. **`winget` 安装器挂起**：msiexec 启动后 CPU 停在 6.17 不再变化，等待交互无法静默完成
2. **更根本的原因**：即使装上，Windows 版 Swift **不包含 SwiftUI 和 SwiftData**
   （[官方说明](https://www.swift.org/install/windows/) 里 Windows 支持的是服务端/跨平台场景）。
   项目里 19 个文件依赖 SwiftUI/SwiftData，装上也编译不了

已删除不完整的下载，不留半成品。

---

## 现在真正该做的：云端 macOS 编译

**不用买 Mac。** GitHub Actions 提供免费 macOS 机器，
配置已经写好：`.github/workflows/build-ios.yml`

**本地仓库已建好**（47 个文件已 commit），只差推送到 GitHub：

```bash
cd bushaoxin
git remote add origin https://github.com/你的用户名/bushaoxin.git
git branch -M main
git push -u origin main
```

> 推送需要你的 GitHub 凭据。本机有一把 SSH key 但**尚未绑定到 GitHub 账号**，
> 所以这一步只能你来做（或把 key 加到 GitHub 设置里）。

然后 GitHub → Actions → Build iOS → Run workflow。
日志里那段「编译错误汇总」贴回来即可。

**额度**：公共仓库免费；私有仓库 2000 分钟/月，macOS 按 10 倍计 ≈ 200 分钟 ≈ 编译 20 次。

详见 [`../docs/怎么跑起来.md`](../docs/怎么跑起来.md)。

---

## Windows 上永远验证不了的部分

| 内容 | 原因 |
|---|---|
| SwiftUI 视图能否编译 | 仅 Apple 平台 |
| `@Model` / `@Query` 运行时行为 | SwiftData 仅 Apple 平台 |
| Vision OCR 实际识别效果 | 仅 Apple 平台 |
| StoreKit 购买流程 | 仅 Apple 平台 |
| 布局、动画、手势手感 | 需要真实渲染 |
| App 真正在手机上运行 | 需要 iOS 运行时 |

**一句话**：Windows 上能确定"算法是对的"，确定不了"界面能不能编译、长什么样"。

---

## 附：图标生成

```bash
python verify/make_icon.py
```

生成 `Bushaoxin/Assets.xcassets/AppIcon.appiconset/icon-1024.png`。

- 1024×1024，**RGB 模式无 alpha**（苹果硬性要求，带透明通道会被自动拒）
- 这是**占位图标**，上架前建议换设计师版本
- 有必要生成是因为：`ASSETCATALOG_COMPILER_APPICON_NAME: AppIcon` 已设置，
  但图标文件缺失会导致编译告警甚至失败
