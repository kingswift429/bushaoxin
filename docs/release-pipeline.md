# 发布流程总结

这份文档记录「不烧心」从 Windows 开发机到 TestFlight 的完整链路，
以及一路上踩过的每一个坑。下次发版只看这份就够。

---

## 结论先说

**在 Windows 上开发 iOS App，并且发布到 TestFlight —— 完全可行，且免费。**

不需要 Mac，不需要手动管理证书，不需要买 CI 额度（公开仓库免费）。

全流程：改代码 → `git push` → 点一次 GitHub Actions → 15 分钟后 TestFlight 出现新版本。

---

## 整个链路

```
Windows (无 Xcode)
    │
    │  git push
    ▼
GitHub 公开仓库  kingswift429/bushaoxin
    │
    │  Actions 触发
    ▼
macos-26 runner  (Xcode 26.6 / iOS 26.5 SDK)
    │
    ├─ xcodegen generate        生成 .xcodeproj
    ├─ xcodebuild archive       编译（不签名）
    ├─ xcodebuild -exportArchive 签名（Apple 现场签发 Distribution 描述文件）
    └─ xcrun altool --upload-app  上传
    │
    ▼
App Store Connect → TestFlight
    │
    ▼
iPhone 上装 TestFlight App → 安装「不烧心」
```

---

## 已配置的资产

| 项 | 值 | 说明 |
|---|---|---|
| Team ID | `GB6U7SA29H` | 写在 `project.yml` |
| Bundle ID | `com.kingswift429.bushaoxin` | **上传后不可改** |
| App Store Connect App ID | `6824727797` | 链接：appstoreconnect.apple.com/apps/6824727797 |
| SKU | `bushaoxin-001` | 内部编号，不可改 |
| 最低系统 | iOS 17.0 | `deploymentTarget` |
| 编译 SDK | iOS 26.5（Xcode 26.6） | Apple 强制要求 |
| 图标 | 冰购物车 1024×1024 RGB | 无 alpha |

---

## 三个 GitHub Secrets（已配置）

| Name | 内容 | 权限要求 |
|---|---|---|
| `ASC_KEY_ID` | API Key 的 ID（10 位） | — |
| `ASC_ISSUER_ID` | Issuer ID（UUID） | — |
| `ASC_KEY_P8` | `.p8` 文件全文 | **必须 Admin 权限** |

获取路径：https://appstoreconnect.apple.com/access/integrations/api → Team Keys → 「+」

**上传方式：** 用 GitHub 的 `crypto_box_seal` 加密后 PUT 到 API，密钥不出现在对话/日志里。

---

## 一路上踩的 9 个坑

按遇到顺序记录。每个都附了根因，不是只写"改了什么"。

### 1. `await` 写在 `??` 里 —— Swift 并发报错

```
error: 'async' call in a function that does not support concurrency
```

`PurchaseService.swift` 里 `let x = await foo() ?? bar` 这种写法，
`await` 的右操作数 `bar` 会掉出并发上下文。拆成两行即可。

**这个错误只有真正的 `xcodebuild` 能发现**，Windows 上的 swiftc 语法检查查不出来。

### 2. Vision 的 Sendable 警告

`ReceiptParser.swift` 里 `VNRecognizeTextRequest` 跨 actor 传递报警。
解法：`@preconcurrency import Vision`，并把 Vision 对象创建移到
`DispatchQueue.global(qos: .userInitiated).async` 的闭包**内部**。

### 3. PLA 协议未同意

```
Unable to process request - PLA Update available:
your team's Account Holder must agree to the latest Program License Agreement.
```

Apple 更新协议后，账号持有人必须去 developer.apple.com 勾选同意，
否则任何签名操作都失败。这个错误会伪装成 `No profiles found`，容易误判。

### 4. 账号没有绑定任何设备

```
Your team has no devices from which to generate a provisioning profile.
```

Xcode 默认 Automatic 签名会申请 **iOS App Development** 描述文件，
而 Development 描述文件强制要求至少一台设备 UDID。

**关键认知：TestFlight 根本不需要 Development 描述文件。**
它用的是 **iOS Distribution**，这类描述文件不需要设备。

### 5. Manual 签名又要求写死 profile

改 `CODE_SIGN_STYLE=Manual` 后变成：

```
"Bushaoxin" requires a provisioning profile.
```

因为 Manual 必须指定具体 profile 名，而 profile 每次签发都不一样。

**解法 —— 绕开这个循环：**

```bash
# 归档完全不签名
xcodebuild archive ... \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO

# 签名交给导出阶段，app-store-connect 强制走 Distribution
xcodebuild -exportArchive ... -allowProvisioningUpdates
```

未签名的 archive 装不到真机，但 TestFlight 不需要 ——
Apple 收到的是导出阶段签好名的 .ipa。

### 6. `exportArchive No Team Found in Archive`

不签名的 archive 里没有记录团队信息。解法：
- `ExportOptions.plist` 加 `teamID`
- `archive` 命令也传 `DEVELOPMENT_TEAM`

### 7. API Key 权限不足（最费时的一个）

```
error: exportArchive Cloud signing permission error
error: exportArchive No profiles for 'com.kingswift429.bushaoxin' were found
```

| 权限 | 上传 .ipa | 签发证书 |
|---|---|---|
| Developer | ❌ | ❌ |
| App Manager | ✅ | ❌ |
| **Admin** | ✅ | ✅ |

**自动签名要现场创建 Distribution 证书，必须有 Admin。**
而且 Key 的权限**创建后不可修改**，只能新建。

### 8. Bundle ID 未注册

`Cloud signing permission` 还有一个成因：Bundle ID 没在
developer.apple.com 的 Identifiers 里注册。

注意这是**两件事**：
- 注册 Bundle ID（developer.apple.com/account/resources/identifiers）
- 创建 App 记录（appstoreconnect.apple.com/apps）

**必须先注册 Bundle ID，App Store Connect 的下拉框里才会出现。**

### 9. iOS 26 SDK 强制要求

```
This app was built with the iOS 18.5 SDK. All iOS and iPadOS apps must be
built with the iOS 26 SDK or later, included in Xcode 26 or later.
```

`macos-15` runner 只有 Xcode 16.4（iOS 18.5 SDK），已被拒收。
改用 `macos-26`（Xcode 26.6 / iOS 26.5 SDK）。

**注意：** `deploymentTarget` 仍是 iOS 17.0，支持老设备不变。
"用什么 SDK 编译" 和 "最低支持什么系统" 是两件事。

### 10. 90474 方向声明

```
Invalid bundle. The "UIInterfaceOrientationPortrait" orientations were provided
for the UISupportedInterfaceOrientations Info.plist key, but you need to include
all of Portrait, PortraitUpsideDown, LandscapeLeft, LandscapeRight to support
iPad multitasking. (90474)
```

即使 `TARGETED_DEVICE_FAMILY=1`（只 iPhone），Xcode 26 上传校验
仍会按 iPad 多任务规则检查方向。

**解法：** `Info.plist` 加 `UIRequiresFullScreen: true`，
明确声明不做 iPad 多任务。这个键只对 iPad 生效，不影响 iPhone。

---

## 一次发版怎么做

### 普通更新

```bash
# 1. 改 project.yml 的构建号（必须递增）
#    CURRENT_PROJECT_VERSION: "1"  ->  "2"

# 2. 提交推送
git add -A && git commit -m "feat: xxx" && git push

# 3. 打开这个页面点 Run workflow
#    https://github.com/kingswift429/bushaoxin/actions/workflows/release-testflight.yml
```

### 大版本更新

`MARKETING_VERSION` 也改（`1.0.0` → `1.1.0`）。

---

## 常见错误速查

| 报错 | 原因 | 解法 |
|---|---|---|
| `No signing certificate` | Team ID 错或 Key 非 Admin | 检查 `project.yml` 和 Key 权限 |
| `Unable to find matching private key` | `.p8` 内容不完整 | 重新复制全文，含首尾两行 |
| `Cloud signing permission error` | Key 是 App Manager | 新建 Admin Key |
| `No profiles ... were found` + `Cloud signing` | Bundle ID 未注册 | 去 Identifiers 注册 |
| `already been used` | 构建号重复 | `CURRENT_PROJECT_VERSION` +1 |
| `can't have an alpha channel` | 图标带透明 | 转 RGB（`verify/make_icon_final.py` 强制 RGB） |
| `iOS 26 SDK` | runner 太旧 | 用 `macos-26` |
| `90474` 方向 | 缺 UIRequiresFullScreen | `Info.plist` 加该键 |

---

## 相关文件

| 文件 | 作用 |
|---|---|
| `.github/workflows/release-testflight.yml` | 发布 workflow（11 步） |
| `.github/workflows/build-ios.yml` | 日常编译检查 |
| `project.yml` | 工程配置（Team ID、Bundle ID、版本号、Info.plist） |
| `docs/testflight-setup.md` | 首次配置三个 Secret 的步骤 |
| `docs/privacy.html` / `terms.html` | 四语隐私政策与条款 |
| `verify/make_icon_final.py` | 图标生成（1024 RGB 无 alpha） |

---

## 隐私政策地址

上线在 GitHub Pages：

- 主页：https://kingswift429.github.io/bushaoxin/
- 隐私政策：https://kingswift429.github.io/bushaoxin/privacy.html
- 服务条款：https://kingswift429.github.io/bushaoxin/terms.html

`Bushaoxin/Services/AppLinks.swift` 里已指向这三个地址。
审核会真的点开链接，不能是 404。

**如果以后换自定义域名**，只需改 `AppLinks.swift` 里三个常量。
