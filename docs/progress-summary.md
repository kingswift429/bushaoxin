# 项目进度总结

> 最后更新：CI Run #20 通过后

---

## 一、现在处于什么状态

**一句话：App 本身已经完整，卡在「装到手机上」这一步。**

| 环节 | 状态 |
|---|---|
| 代码能编译 | ✅ CI 连续 20 次通过 |
| 12 种语言界面 | ✅ 137 条文案，100% 覆盖 |
| 12 种语言图标名 | ✅ 从产物里 `plutil` 实际读出验证 |
| 12 种语言商店页 | ✅ 名称/副标题/描述/关键词/隐私网址 |
| 品牌命名 | ✅ 海外 Wait A Day，中文不烧心 |
| 销售范围 | ✅ 174 个地区，**排除中国大陆** |
| 内购订阅 | ✅ 2 个产品 + 价格 + 12 语言本地化 |
| 年龄分级 | ✅ 4+ |
| 构建版本 | ✅ 已绑定到 1.0 |
| **装到真机** | ⏳ **等 UDID** |
| App Store 截屏 | ⏳ 等真机截图 |
| 订阅审核截图 | ⏳ 等真机截图 |

---

## 二、这一轮做完的事

### 1. 修掉一个会让付费墙完全失效的 bug

`Entitlements.swift` 里产品 ID 是模板遗留的占位符：

```swift
case .monthly: return "com.yourteam.bushaoxin.plus.monthly"   // ❌ yourteam
```

真实 Bundle ID 是 `com.kingswift429.bushaoxin`。

**为什么这个 bug 特别危险：**

`Product.products(for:)` 碰到不存在的 ID **不会抛错**，只返回空数组。结果是：

- 付费墙价格显示不出来
- 点「继续」没有任何反应
- 控制台不报错
- 只有真机跑起来、用真实账号测试才会发现

已改成正确 ID。

### 2. 修掉价格硬编码

原来 `displayPrice` 写死人民币符号。我们在 174 个地区上架，美元区用户看到人民币只会困惑。

改成 `fallbackPrice` 用美元占位，正常路径走 StoreKit 的 `product.displayPrice`（苹果按地区自动本地化）。

### 3. 销售范围配置成功

Apple 的 API 对这块限制很怪：`territoryAvailabilities` **只允许 UPDATE，不允许查询**。

绕过去的办法：直接 PATCH 并读返回值（PATCH 会回传当前状态）。

**ID 格式是坑**：不是 `CHN`，而是 base64 编码的 `{"s":"<appId>","t":"<地区码>"}`。

结果：

```
✗ CHN  中国大陆    available=false   CANNOT_SELL
✓ USA  美国        available=true
✓ JPN  日本        available=true
... 共 174 个地区
```

港澳台保留（不需要 ICP 备案，中文用户能下载）。

### 4. 订阅全部建好

| 项 | 值 |
|---|---|
| 订阅组 ID | `22496006` |
| 组名 | Plus（12 语言本地化）|
| 月订阅 | `com.kingswift429.bushaoxin.plus.monthly` — **$2.99** |
| 年订阅 | `com.kingswift429.bushaoxin.plus.yearly` — **$19.99** |
| 覆盖地区 | 174 个（排除中国大陆）|
| 本地化 | 12 种语言 |

**踩到的三个坑：**

1. **订阅描述限 55 字符** —— 不是 100，比 App 描述严格得多
2. **创建地区要 `availableTerritories`**（数组），不是 `territory`（单个）
3. **`subscriptionAvailabilities` 只允许 CREATE**，不能 UPDATE

### 5. Ad Hoc 打包流程

新建 `.github/workflows/adhoc-ipa.yml`，作用是绕开 TestFlight。

| | TestFlight | Ad Hoc |
|---|---|---|
| 大陆网络 | ❌ 不通 | ✅ 完全离线 |
| 需要审核 | 需要 | **不需要** |
| 需要 UDID | 不需要 | **必须** |
| 有效期 | 90 天 | 1 年 |

流程已经写好，只等 UDID。

---

## 三、我们有什么优势

### 1. 真实痛点，不是伪需求

「冲动消费」是高频行为。现有工具（记账 App）都是**事后记录**，我们做的是**事前拦截**。

这个差别很重要：记账 App 记录的是已经花掉的钱，改变不了什么。我们在用户点击「立即购买」和「确认支付」之间插了一个缓冲。

### 2. 24 小时冷静期是核心机制

不是靠意志力，是靠时间。心理学上这叫「热-冷 empathy gap」，冲动状态下的人无法预测冷静后的自己。

### 3. 社交监督

广场功能让用户看到「别人也在纠结」。这比任何说教都有效。

### 4. 截图自动识别

看到想买的东西，截个图，App 自动读出商品名和价格。把记录成本降到最低。

**这是竞品没有的。**

### 5. 零服务器成本

纯本地存储，不需要后端。这意味着：

- 边际成本接近 0
- 不会被服务器账单拖死
- 用户数据不上传，隐私故事好讲
- 审核容易过（没有 UGC 审核负担）

### 6. 12 种语言

覆盖全球主要市场。中文、英、日、韩、法、德、西、葡、俄、阿、意、荷。

**大多数同类 App 只做英文。**

### 7. 174 个地区上架

除中国大陆外全覆盖。

---

## 四、我们缺什么

### 严重

| 问题 | 影响 | 怎么解决 |
|---|---|---|
| **界面从未被人眼看过** | 可能有布局错、文字截断 | 装到手机上自己看 |
| **App Store 截屏为零** | 无法提交审核 | 真机截图 |
| **订阅审核截图缺失** | 内购无法上架 | 真机截图 |
| **订阅状态 `MISSING_METADATA`** | 内购不能卖 | 上传审核截图 |

### 中等

| 问题 | 影响 |
|---|---|
| 广场数据是内置语料，不是真实用户 | 冷启动没有真实内容 |
| `support@bushaoxin.app` 邮箱 MX 记录不存在 | 用户反馈邮件收不到 |
| 没有崩溃监控 | 出问题不知道 |
| 没有推送服务 | 冷静期到点无法提醒 |

### 轻微

| 问题 | 影响 |
|---|---|
| `AffiliateService` 是死代码（`isEnabled = false`）| 无功能影响 |
| 没有 A/B 测试框架 | 无法优化转化 |
| 没有年度报告 | 少一个留存点 |

---

## 五、怎么让更多人下载

### 第一波：先把地基打对（现在）

- ✅ 174 个地区上架
- ✅ 12 种语言
- ✅ 名字好记（Wait A Day）
- ⏳ 截图要好看（这是转化率第一因素）

### 第二波：商店优化（ASO）

**关键词策略：**

| 语言 | 核心词 |
|---|---|
| 英 | impulse buying, spending tracker, self control |
| 日 | 衝動買い, 節約, 家計簿 |
| 韩 | 충동구매, 절약, 가계부 |
| 德 | Impulskauf, Sparen, Haushaltsbuch |

**竞品分析：** 名字最接近的两个是 `Sleep On It: Decide Later` 和 `Sleep On It: Buy Later`。它们的名字被困在 Sleep On It 上，我们的 `Wait A Day` 在搜索里能见度更高（因为不是它们的关键词）。

### 第三波：内容营销

**最容易起量的渠道：**

1. **Reddit** — r/personalfinance, r/frugal, r/shoppingaddiction, r/ADHD
2. **TikTok** — 「我用这个 App 一个月省了 XXX」这类内容
3. **小红书 / 抖音** — 中文市场（虽然大陆不上架，但可以导流到港澳台/海外）
4. **Product Hunt** — 一次发布能带来几千下载

### 第四波：付费推广

先不要。等自然量跑起来，看清楚哪个语言的转化率最高，再定向投放。

---

## 六、明天要做的三件事

### 1. 拿 UDID（最关键）

**借一根数据线**，电脑上：

1. 打开爱思助手（`i4.cn`）
2. 连 iPhone，手机上点「信任」
3. 首页会显示 UDID，复制

**UDID 长这样：**

```
00008110-001A2B3C4D5E6F70
```

或

```
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
```

### 2. 我注册设备并打包

拿到 UDID 后我做：

1. API 注册设备到账号
2. 跑 Ad Hoc 打包
3. 给你下载链接

**预计 20 分钟。**

### 3. 装机后截 6 张图

| # | 截什么 |
|---|---|
| 1 | 发起审批页（想买什么/多少钱/为什么买）|
| 2 | 冷静期倒计时 |
| 3 | 广场 |
| 4 | 我的页（省下多少钱 + 连续天数）|
| 5 | 省钱报告 |
| 6 | 截图自动识别 |

**再加 1 张给订阅审核用** —— 就是付费墙页面。

**iPhone 14 Pro Max 截图正好是 1290×2796，直接符合 App Store 6.7 英寸要求，不用任何处理。**

---

## 七、安全提醒

### 需要撤销的凭证

| 凭证 | 说明 | 何时撤销 |
|---|---|---|
| GitHub 个人访问令牌 | 本次开发用于触发 CI，权限较大 | **全部完成后立即撤销** |
| ASC API Key（Admin 那把）| 本次开发主力，能删 App | 全部完成后撤销 |
| ASC API Key（App Manager 那把）| 仅能上传包 | 全部完成后撤销 |
| ASC API Key（Developer 那把）| 一直不可用 | 现在就可以删 |
| 早期下载的 `.p8` 私钥文件 | 已在开发机工作目录 | 删除 |

撤销入口：

- GitHub：Settings → Developer settings → Personal access tokens → Revoke
- App Store Connect：Users and Access → Integrations → App Store Connect API → 点 Key 右侧的 Revoke

**重要：** 你在对话里贴出过手机号。它已经被填进 App 审核联系信息（苹果要求必填）。如果不想公开这个信息，之后可以在 App Store Connect 里改。

---

## 八、关键配置速查

```
Team ID            GB6U7SA29H
Bundle ID          com.kingswift429.bushaoxin
Apple ID (App)     6824727797
SKU                bushaoxin-001
Issuer ID          03728b7d-2ebc-41f9-9efb-673b5c74b5c0
当前 API Key       3F6MS38C2R (Admin)
版本 ID            86dfde54-cd3c-49f0-b132-3c7140d0ce0d
构建 ID            4081de62-76ae-4ffb-9bea-ddc270da7fd4
订阅组 ID          22496006
月订阅 ID          6824841415
年订阅 ID          6824841550
GitHub 仓库        https://github.com/kingswift429/bushaoxin
ASC 后台          https://appstoreconnect.apple.com/apps/6824727797
```
