---
type: "公告"
title: "AstroBox 2.2 正式发布"
subtitle: "全面优化性能，支持多设备连接与全新装扮"
author: "AstroBox"
date: 2026-10-03
cover: "https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/cover1.jpg"
---

也许你目前还没能收到该版本的更新推送——但别担心，它将于3天内在各个平台上陆续发布！

欢迎各位更新到 AstroBox 2.2 版本！如果说 2.0 是全新的起点，2.1 是交互逻辑的补足，那么 2.2 就是一个在此基础上进行大幅优化并加入数项重磅功能的版本。请允许我们为你介绍在该版本中带来的数十项显著改进：

## 性能

AstroBox 的应用内流畅度自 2.0 版本起便饱受诟病。这其中当然有一部分是使用 Tauri 框架基于 Web 技术栈开发的原因导致，但更多是由于我们在开发过程中对大众设备性能的欠考虑。在我们动辄 M5 Pro、A19 Pro、骁龙 8 Elite 的机器上进行测试，显然无法照顾到覆盖更广的中低端设备，导致实际上很多用户遭遇了极其严重的性能与发热问题。

因此在该版本中，我们以一台搭载 Tensor G2 处理器的 Google Pixel 7a 作为性能基准，从应用启动速度到页面切换流畅度进行了全面且彻底的优化。请看效果：

应用冷启动速度：

![应用启动速度](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/launch-speed.webp)

预见式返回动画：

![预见式返回动画](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/back-anim.webp)

抽屉手势与动画：

![抽屉动画](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/vaul-anim.webp)

卡片展开收起动画：

![卡片展开收起动画](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/card-anim.webp)

（运行环境：Google Pixel 7a, Android 17, Android System WebView 155.0.8059.16）

## 连接

我们注意到，很多小米穿戴设备用户都同时持有多台设备，并大概率正在同时使用它们，这些用户也许也希望能同时为这些设备安装资源、同步数据。因此在该版本中，我们支持了多设备连接：

![多设备连接演示](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/multi-device-connect.webp)

正如你所见，现在你可以连接理论无数个设备（取决于系统蓝牙限制），并通过在导航栏的设备区域滑动来切换它们。切换到对应设备后，从社区源下载的资源将安装到其中；当你向队列中添加项目时，将始终询问你要安装到哪个设备上。

同时，我们也听到了一些用户的反馈，目前我们的应用逻辑是在安卓系统上连接前自动移除配对，但这会破坏他们的就近解锁功能。因此在该版本中我们也提供了开关：

![连接前移除配对开关](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/pair-switch.PNG)

## 资源包
在2.2版本中，我们在Canopus的基础上扩充出了全新的资源类型“模块”，尽管确实有不少模仿者采用生成式AI仿照我们的思路批量生成同类产品，但这的确也反映出了社区对此类资源的认可与喜爱，包括每天只会敲打Prompt的AI Kiddies们。

当然，我们的探索不会停止。在Canopus的基础上，我们开发了全新的项目**Corona**，并带来了全新的资源类型“资源包”。Corona本质上是一个Canopus模块+快应用管理器的组合，它支持通过在AstroBox中安装 **.crpack** 文件向设备导入资源包，并按照资源包中包含的资源和映射规则入侵设备系统的资源读取流程，将设备本应被读取的自带资源“转接”到资源包提供的资源上，支持的资源包括所有图片资源和字体资源。前往资源列表搜索“Corona”即可安装相关组件，要寻找可用的Corona资源包，可在资源列表中筛选“资源包”类型。

同时，我们也没有忘记对资源包作者提供便利。通过AstroBox插件，我们制作了一个资源包制作工具，资源包创作者们可以通过该工具**完全免费**地制作资源包，并**完全免费**地将它发放到每个用户的手中，并且这一切都是**完全开源**的。

![资源包制作器插件](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/corona-plugin.png)

要了解更多（包括详细使用教程），欢迎到各大视频平台（如哔哩哔哩）上搜索相关视频！

- [资源包制作器插件开源仓库](https://github.com/leset0ng/Corona-editor)
- [资源包载入模块开源仓库](https://github.com/AstralSightStudios/Canopus-Module-Corona)
- [Canopus开源仓库](https://github.com/AstralSightStudios/Canopus)

⚠️ 要安装Corona资源包，你必须使用AstroBox v2.2版本

## 社区

AstroBox 的官方资源社区内现已有超过 300 款资源，但十分严峻的问题是，此前我们只提供一个完整的资源列表，并按更新时间排序，这让很多资源完全失去了露面的机会，也难以让用户找到自己喜欢的资源。

面对这个问题，我们从 9 月中旬起在服务端埋入了用户画像收集、资源推流标签的功能，在半个月的验证与调教下取得了令人满意的成果。自 AstroBox 2.2 版本起，你将在首页看到“为你推荐”栏目，并可在资源列表中切换为按“推荐”排序：

![排序方式切换](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/sort-change.PNG)

“推荐”排序将根据你对资源的浏览、下载情况，综合你已拥有的设备进行个性化的资源推送。同时，我们也额外添加了“按下载量排序”和“按浏览量排序”的选项。

此外，在该版本中，我们彻底移除了此前“发送评论必须绑定 GitHub 账号”的限制，现在任何用户都能够发送评论——当然，由《冈易我**界》同款屏蔽词列表驱动的内容审查系统依然存在，因此在发言前请三思。

说到评论，为了方便创作者收集用户反馈、为用户提供有效的解决方案，并尽可能丢弃无效信息，我们做出了如下调整与功能新增：

1. 为资源评分前必须先下载资源
2. 做出三星及以下的评分时，必须先做出评论
3. 创作者本人可在自己的资源下进行评论置顶
4. 创作者本人可在自己的资源下针对用户评论做出“开发者回复”并以最高优先级显示

![开发者回复](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/developer-reply.PNG)

同时，针对资源详情页，我们也做出了这些细节调整：

1. 未连接设备且未登录账号时针对付费资源不再直接显示下载按钮以造成错误引导
2. 针对付费资源即使未连接设备也可以跳转购买
3. 查看“更多设备下载”列表时不再需要先连接设备

现在，我们还支持直接使用创作者在 CreatorConsole 中生成的“激活码（CDK）”解锁资源：

![CDK解锁](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/cdk-redeem.PNG)

同时，付费资源的自动化购买解锁流程支持也不再局限于爱发电，我们构建了一套协议，现在创作者可以接入自有服务器，通过用户的 AstroBox UID 进行私有化的购买校验。详见文档：[自有网站与第三方订单系统授权](https://abox.run/docs/creator-tools/resource-management/external-authorization)

当然，我们也没忘记“通知”方面的改进——自 AstroBox 2.0 首个版本上线以来，其便支持通过 APNs 与 FCM 向用户推送通知，但仅局限于评论被回复、点赞等场景，较为鸡肋。在不久前我们通过服务端更新使推送内容也包含了 CreatorConsole 侧的提醒（如资源审核结果等），而在本次版本更新中，我们引入了“关注”作者的功能：

![作者关注](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/sub-creator.PNG)

关注作者后，每当作者发布新资源或是对已有资源进行更新时，都将向你推送通知以进行提醒。

同时，我们也引入了设备资源更新通知，每当你设备上有资源可进行更新时，我们会向你发送通知以进行提醒：

![设备资源更新通知](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/resource-update-notify.jpg)

![应用内设备资源更新通知](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/in-app-resource-update-notify.PNG)

当然，我们还允许创作者针对最新版本填写更新日志，用户在安装更新时也能对其进行浏览。

此外，我们还在不断增强“个人主页”功能的存在感。现在，“设置”页面上方的账号数据区域经过了彻底的重新设计，并引入了“历史记录”和“已购资源”等便捷功能：

![新设置页中的个人主页](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/settings-update.PNG)

现在，你也能通过首页的搜索框搜索作者，点击即可进入其个人主页：

![在探索页中搜索作者](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/creator-search.PNG)

## 界面装扮

开放和高度自定义性一直以来是 AstroBox 用户体验的基石，而从这个版本起，我们将允许用户对 AstroBox 的应用界面进行更深度的自定义，从探索页背景到导航栏图标，甚至是页面背景、设备页上每张卡片的背景、进度条的填充图，都可以被自定义调整。而这一切都可以被导出为 `.abtheme` 主题包，与你的朋友们尽情分享。

效果大致如下：

![界面装扮示例](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/theme-demo-device-detail.PNG)

同时，我们也加入了“装扮市场”，其中包含我们制作的一些装扮，你也可以通过给仓库提 PR 的方式上架你的装扮：[AstralSightStudios/AstroBox-NG-Theme-Repo](https://github.com/AstralSightStudios/AstroBox-NG-Theme-Repo)

![装扮市场](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/theme-store.PNG)

## 插件系统

在该版本中，我们也引入了插件 API Level 4，当然，它还不是一个稳定的 Level，其功能仍处于扩充阶段，但目前已制作完成的接口将不会有更改。Level 4 将 wasmtime 版本更新到了最新，并将 WASI 规范版本提升到了 v0.3，在性能、稳定性、安全性等各个方面都提供了显著的改善。同时自该 Level 起，AstroBox v2 插件也将正式支持使用 Python、JavaScript 开发（尽管因为它附带解释器会导致插件体积十分巨大）。

我们目前已开发完成并提供以下接口：

- **Browser**：其作用是拉起应用内浏览器，但支持脚本注入、Cookie 读取、URL 拦截等特性。该接口的制作初衷是，我们发现有许多开发者希望通过 AstroBox 重新实现某些软件的客户端，包括其账号系统的部分，但目标软件的登录也许强依赖 OAuth，此前该部分操作只能通过要求用户手动填写回调链接实现，而现在你可以通过拉起应用内浏览器，通过关键字实现对 OAuth Callback 的全自动化拦截，方便你通过 AstroBox 插件“强兼”其它软件。
- **HttpServer**：正如它的名字一样，现在你可以通过 AstroBox 插件架设一个 HTTP 服务器。该接口的制作初衷是，部分开发者反馈在某些设备上 fetch 的速度比 interconnect 快，既然如此相比费大心思实现 interconnect 传输协议，不如本地开个服务器用 fetch 去请求。此外，也许该接口也有助于插件扩充并响应来自外部的一些自动化请求；具体怎么使用，还得看大家发挥。
- **Notification**：依旧用途与名字对等，该接口的用途是向设备发送通知，也包括澎湃OS的“焦点通知”。
- **os.deviceId**：现在 os 接口下扩充了一个名为 deviceId 的函数，你可以通过调用它来获取该 AstroBox 客户端的唯一指纹，如果你在制作付费插件，这也许对反盗版有用。
- **Account**：该接口提供了获取当前 AstroBox 已登录的账号信息的能力，包括 AstroBox 账号 ID、名称、绑定的米坛/GitHub/爱发电账号 ID、名称。当然，在调用时会向用户申请授权。

## 体验提升

为了优化广大用户的体验，我们也做了十分多的体验改善，包括但不限于：

1. 队列里的添加按钮现在支持用于安装插件
2. 优化了深浅色自动识别的逻辑，不会再出现开屏吃闪的情况
3. 优化了热更新的获取逻辑，不再在启动时硬控用户
4. 重新设计了网络节点的测速逻辑，更容易选到合适的节点
5. 针对 macOS 从配对与连接速度到稳定性等全方面进行了优化

---

如果你有任何建议，欢迎大家通过填写下方的问卷向我们反馈各种问题、提出建议。我们会在后续持续更新、优化这个应用。

[点击填写：AstroBox 2.2 体验与建议反馈问卷](https://xykong-technology.feishu.cn/share/base/form/shrcnZScNiXcdtK7xhoDo4Fwysd)

期待 AstroBox 未来能与大家共同成长，持续构建一个优秀的第三方穿戴设备工具箱。
