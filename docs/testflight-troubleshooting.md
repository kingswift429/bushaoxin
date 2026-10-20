# TestFlight 分发排查记录

记录「构建版本上传成功但测试员装不上」的完整排查过程。
这类问题的难点在于：**服务端一切正常，没有任何报错**。

---

## 结论

三个隐藏的必填项导致 App 无法进入「可分发」状态：

| 缺失项 | 位置 | 后果 |
|---|---|---|
| App 隐私声明未填写/未发布 | App 隐私 | App 无法分发 |
| 隐私政策网址为空 | App 隐私 → 编辑 | 同上 |
| 年龄分级未设置 | App 信息 → 设置年龄分级 | 同上 |

以及第四个更根本的问题：**内部测试邀请从未被真正接受**
（API 显示 `state: "INVITED"`、`appDevices: []`）。

最终走 **外部测试公开链接** 绕开了邀请机制。

---

## 判断方法：用 API 而不是看页面

App Store Connect 的网页有很多状态不直观，
改用 API 直查最可靠。

### 核心接口

```
GET /v1/builds?filter[app]=<APP_ID>
GET /v1/betaTesters?filter[apps]=<APP_ID>
GET /v1/betaGroups?filter[app]=<APP_ID>
GET /v1/betaAppReviewSubmissions?filter[build]=<BUILD_ID>
GET /v1/apps/<APP_ID>/betaAppLocalizations
GET /v1/apps/<APP_ID>/betaAppReviewDetail
GET /v1/apps/<APP_ID>/appInfos
```

### 关键字段怎么读

| 字段 | 正常值 | 异常含义 |
|---|---|---|
| `builds.processingState` | `VALID` | `PROCESSING`/`FAILED` = 还在处理或出错 |
| `builds.iconAssetToken` | 有对象 | `null` = 图标没进包 |
| `betaTesters.state` | `INSTALLED` | 停在 `INVITED` = 从未接受邀请 |
| `betaTesters.appDevices` | 非空数组 | 空 = 该账号没在设备上接受过 |
| `betaGroups.publicLink` | `https://testflight.apple.com/join/xxx` | 无 = 未开启公开链接 |
| `appInfos.appStoreAgeRating` | `FOUR_PLUS` 等 | `null` = 年龄分级未设置 |
| `betaAppReviewSubmissions` | 有记录 | 空 = 外部测试未提交审核 |

### 脚本

- `asc-check.js` —— 一次性查出所有状态
- `asc-external.js` —— 创建外部测试组 + 公开链接
- `asc-submit-beta.js` —— 提交 Beta 审核

运行方式：

```powershell
$env:ASC_KEY_ID = "3F6MS38C2R"
$env:ASC_ISSUER_ID = "03728b7d-2ebc-41f9-9efb-673b5c74b5c0"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
node asc-check.js "F:\Administrator\AuthKey_3F6MS38C2R.p8"
```

---

## 踩过的坑

### 1. JWT 的 iat 不能超前

第一个请求成功、后续全部 401。原因是本地时钟比苹果快几十秒，
苹果认为令牌「签发于未来」。

**修复**：`iat` 用 `now - 60`。

### 2. 内部测试的邀请没有「邀请码」

内部测试组只能邮件邀请，没有兑换码。
邮件链接失效时几乎没有备用方案 —— 这是设计缺陷。

### 3. 外部测试才提供公开链接

`betaGroups` 上 `publicLinkEnabled: true` 时才会生成 `publicLink`。
内部组（`isInternalGroup: true`）永远是 `null`。

### 4. 外部测试的第一个版本必须过 Beta 审核

创建外部组并加入构建版本后，
`betaAppReviewSubmissions` 仍然是空的 —— 必须显式 POST 提交。
审核通过前，公开链接打开后也是空的。

### 5. 网页上填 React 受控输入框不能用 setter

App Store Connect 用 React。直接设 `el.value` + `dispatchEvent('input')`
不会让「保存」按钮变亮，因为 React 的受控状态没更新。

**唯一可靠的办法**：用 CDP 的真实鼠标点击 + `Input.insertText`。

```javascript
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left' });
await send('Input.insertText', { text: value });
```

### 6. 页面全文里看不到的值，可能其实已经保存了

React 只渲染可见区域的输入框。
`document.body.innerText` 显示「–」不代表没值 —— 要用
`document.getElementById(id).value` 读。

---

## 隐私声明的正确答案

不烧心是纯本地 App（SwiftData，无服务器、无分析、无广告），
所以：

- 问题「你或第三方是否从此 App 收集数据？」→ **否**
- 数据类型 → **一个都不勾**
- 结果：产品页显示「未收集数据」

这个声明必须点「发布」才生效。

---

## 年龄分级

不烧心是工具类，所有内容项选「无」：

| 步骤 | 内容 | 选择 |
|---|---|---|
| 1 | App 内控件（家长控制/网页/社交/广告） | 全部「否」 |
| 2 | 成人主题（低俗笑话/恐怖/烟酒） | 全部「无」 |
| 3 | 医疗或保健 | 全部「无」 |
| 4 | 性或裸体 | 全部「无」 |
| 5 | 暴力 | 全部「无」 |
| 6 | 基于概率的活动（赌博/竞赛） | 全部「无」 |
| 7 | 其他信息 | 直接保存 |

结果：**4+**，覆盖 172 个国家或地区。

---

## 最终可用的安装方式

**公开测试链接**（外部测试，审核通过后长期有效）：

```
https://testflight.apple.com/join/Ed8HXmmp
```

打开后：
1. 自动跳转 TestFlight
2. 点「接受」
3. 点「安装」

不需要邀请邮件，不需要账号匹配，不需要兑换码。
后续版本推送后自动可更新，不再需要审核（只有第一个版本要）。
