# TestFlight 配置指南

把 App 传到 TestFlight，需要在 App Store Connect 拿到三个值，存进 GitHub Secrets。
做完这一步之后，以后每次发版只需点一次按钮。

---

## 为什么需要这三个值

GitHub Actions 的 macOS runner 是一台**干净的机器** —— 上面没有任何证书、没有登录 Apple 账号。
所以要让 xcodebuild 能签名并上传，必须给它一把「钥匙」。

Apple 提供两种钥匙：

| 方式 | 做法 | 缺点 |
|---|---|---|
| 上传 `.p12` 证书 | 本地导出证书 + 私钥，转 base64 存 Secret | 证书一年过期；私钥要存仓库；换机器要重做 |
| **App Store Connect API Key** | Apple 托管，只给 Key ID + Issuer ID + `.p8` | 几乎无 |

本项目用 **API Key**。`-allowProvisioningUpdates` 会让 xcodebuild 拿着这把钥匙
自己去 Apple 申请证书和描述文件，用完即弃。

---

## 第一步：创建 API Key

1. 打开 https://appstoreconnect.apple.com/access/integrations/api
2. 点左侧 **「Team Keys」**（团队密钥）标签
3. 点 **「+」** 生成新密钥
4. **Name** 填 `GitHub Actions`（随便起，自己能认出来即可）
5. **Access** 选 **「App Manager」**
   - 不要选 Admin：权限过大
   - 不要选 Developer：没有上传 App 的权限
6. 点 **「Generate」**
7. **立刻点「Download API Key」** —— 这个 `.p8` 文件**只能下载一次**，关掉页面就再也拿不到了
8. 记下这一页上显示的两个值：

```
Key ID      : 2X9ABCD3EF          <- 10 位，存在页面上的 "Key ID" 一栏
Issuer ID   : 57246542-96fe-1a63-e053-0824d011072a
```

Issuer ID 在页面**上方**，是给整个团队用的，所有 Key 共用同一个。

---

## 第二步：存进 GitHub Secrets

1. 打开 https://github.com/kingswift429/bushaoxin/settings/secrets/actions
2. 依次点 **「New repository secret」**，添加三个：

| Name | Value |
|---|---|
| `ASC_KEY_ID` | 上一步的 **Key ID**（10 位） |
| `ASC_ISSUER_ID` | 上一步的 **Issuer ID**（UUID 带连字符） |
| `ASC_KEY_P8` | 用文本编辑器打开 `.p8` 文件，**全文复制**，包括开头 `-----BEGIN PRIVATE KEY-----` 和结尾 `-----END PRIVATE KEY-----` 两行 |

**关于 `ASC_KEY_P8` 的注意事项：**

- 必须**完整复制**，少一行都签名失败
- 结尾的 `-----END PRIVATE KEY-----` 后面有没有换行都可以，脚本会处理
- 粘贴到 Secret 输入框时，多行内容直接粘贴即可，不要转义

---

## 第三步：在 App Store Connect 创建 App

API Key 只能操作**已经存在**的 App，不能创建。

1. 打开 https://appstoreconnect.apple.com/apps
2. 点 **「+」** → **「新建 App」**
3. 填写：

| 字段 | 值 |
|---|---|
| 平台 | iOS |
| 名称 | 不烧心 |
| 主要语言 | 简体中文 |
| 套装 ID (Bundle ID) | `com.kingswift429.bushaoxin` |
| SKU | `bushaoxin-001`（内部用，随便填但别重复） |
| 用户访问权限 | 完全访问权限 |

4. 点「创建」

**如果「套装 ID」下拉框里没有 `com.kingswift429.bushaoxin`：**
说明这个 Bundle ID 还没在开发者账号里注册。两个办法：

- 办法 A：先在 https://developer.apple.com/account/resources/identifiers/list 手动创建
- 办法 B：本地跑一次 `xcodebuild -allowProvisioningUpdates` 会自动注册（需要 Mac）

---

## 第四步：跑 workflow

1. 打开 https://github.com/kingswift429/bushaoxin/actions/workflows/release-testflight.yml
2. 点右侧 **「Run workflow」**
3. 第一次建议把 **「只打包不上传」** 勾上 —— 先验证签名能不能通过，不上传到 App Store
4. 点绿色的 **「Run workflow」**

跑完后看日志。如果 `Archive` 和 `Export IPA` 都绿了，说明签名配置正确，
取消勾选再跑一次就会真正上传。

---

## 常见错误对照表

| 日志里的错误 | 原因 | 解决 |
|---|---|---|
| `No signing certificate "iOS Distribution" found` | Team ID 错，或 API Key 没有 App Manager 权限 | 检查 `project.yml` 的 `DEVELOPMENT_TEAM`；检查 Key 的 Access 级别 |
| `Unable to find matching private key` | `.p8` 内容不完整 | 重新复制 `.p8` 全文，确认首尾两行都在 |
| `The provided entity includes an attribute with a value that has already been used` | 同一个 build number 传了两次 | 改 `project.yml` 的 `CURRENT_PROJECT_VERSION` |
| `Invalid Image Path - No image found at the path referenced under key CFBundleIcons` | 图标缺失 | 确认 `icon-1024.png` 在 `Assets.xcassets/AppIcon.appiconset/` 里 |
| `Invalid app icon - The app icon can't have an alpha channel` | 图标带透明通道 | 用 `verify/make_icon.py` 重新生成（它强制 RGB 无 alpha） |
| `Missing compliance` | 没声明出口合规 | 已在 `project.yml` 声明 `ITSAppUsesNonExemptEncryption: false` |
| `This bundle is invalid. New apps ... must be built with the latest SDK` | Xcode 版本太旧 | workflow 用的是 `macos-15` + Xcode 16.4，一般不会遇到 |

---

## 上传之后

1. 等 5~15 分钟，Apple 处理完包（会发邮件）
2. 打开 https://appstoreconnect.apple.com/apps → 你的 App → **TestFlight**
3. 在「内部测试」下添加测试员（你自己）
4. 手机上装 **TestFlight** App，用同一个 Apple ID 登录，就能看到并安装

**内部测试**不需要审核，上传后立即可用，最多 100 人。
**外部测试**需要 Apple 审核第一版，但之后更新大多免审。

---

## 版本号规则

在 `project.yml` 里：

```yaml
MARKETING_VERSION: "1.0.0"        # 给用户看的版本号，改这个发新版本
CURRENT_PROJECT_VERSION: "1"      # 构建号，每次上传必须递增
```

**同一个 `CURRENT_PROJECT_VERSION` 不能上传两次。** 每次改代码要发版，就把这个数字 +1。
