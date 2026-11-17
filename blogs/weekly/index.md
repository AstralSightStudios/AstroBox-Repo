---
type: "公告"
title: "AstroBox 2.2.5 更新日志"
subtitle: "全新的模块安装方式，iOS 与 Linux 体验升级，创作者功能增强"
author: "AstroBox"
date: 2026-11-1
cover: "https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/cover1.jpg"
---

嗨喽各位！距离 2.2 的发布已经过了一些时日了，在此期间，我们接到了不少问题反馈，并持续积极推送热更新对它们进行修复。当然，2.2.5 的更新也带来了不少新功能与体验改进，接下来请让我为你介绍它们！

## 全新的模块、资源包安装方式

Canopus 与 Corona 已于近期完成了一次完整重构。自该版本起，在新版 Canopus 管理器的加持下，你可以直接使用 AstroBox 安装 `.canopus` 模块包文件，而无需通过表盘进行释放。我们还为插件提供了 `canopusconnect` 接口，允许插件通过 Canopus 专有的蓝牙通道进行通信，并提供极高的速度。

> **注意**：如果你曾安装过旧版的 Canopus 与模块，请先完全移除它们，再升级到新版。最快速的方法是在激活表盘按两次 `Clear Env` 然后重启设备删除表盘。

此外，Bluetooth Audio 模块与 Lyra Player 模块也得到了从 UI 到体验的全面改进，欢迎更新尝试！

## iOS 用户体验

自 AstroBox 上架 App Store 后，我们的 iOS 用户占比持续增长，目前已达近 50%，数量接近 100 万。同时，我们接到许多用户的反馈，称他们在资源安装过程中经常遇到“设备响应超时”的提示，即便已按照标准流程操作。经过我们的持续调查，发现该问题是“小米运动健康”与“AstroBox”抢夺设备连接导致。因此在该版本中，我们针对这种情况追加了一些可能的提示来引导用户关闭“小米运动健康”的蓝牙权限以解决该问题，你也可以直接按照下面的动图来操作：

![在 iOS/iPadOS 设置中关闭“小米运动健康”的蓝牙权限](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/mifit-bt-off.webp)

同时，为响应苹果号召，在该版本更新中，我们也提供了完整的 iPhone Duo 适配：

![iPhone Duo 适配演示](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/iphone-duo.webp)

此外，我们也将于近期通过热更新推送更多适用于 iOS/iPad OS 的前端体验改进，尽情期待。

## Linux 用户体验

我们深知 AstroBox 在 Linux 平台上的严重性能问题。简单地说，这是由于 Tauri V2 在 Linux 上仅使用 GTK WebView 渲染前端，而其基于的 WebKit 内核在 Linux 上性能表现过于糟糕，近乎处于不可用状态。临近 Tauri V3 的发布，我们先将其包含的新特性“Linux CEF WebView”移植到了 Tauri V2，并已于该版本实装。由 Chromium 内核驱动的前端现已能在 Linux 上得到十分优秀的性能表现。

## 创作者服务

众所周知，AstroBox 官方源并不允许上架测试类的资源，因为测试资源的频繁更新会给我们带来严重的审核压力，但广大创作者需要更合理便捷的测试资源分发渠道的需求切实存在。为此，受苹果 TestFlight 启发，我们在 CreatorConsole 中推出了“测试分发”功能。

只要你拥有 CreatorPlus 或 CreatorPro 会员，即可使用该功能，不同会员档次包含不同的用量限制。它的使用方法非常简单：

前往“测试分发”页面，创建一个测试资源，填写相关信息：

![创建测试资源](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/test-create.webp)

选择“添加版本”，输入版本信息，并添加包体与其对应的设备，然后将其发布：

![发布测试版本](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/test-publish-version.webp)

点击“成员”，在这里你有三种方法邀请你的用户加入测试：

**1. 使用邀请码**

![使用邀请码邀请](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/test-invite-code.webp)

**2. 使用邀请链接**

![使用邀请链接邀请](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/test-invite-link.webp)

**3. 根据账号 ID 邀请**

![根据账号 ID 邀请](https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/test-invite-id.webp)

三种方法均可达成相同的效果，各位创作者可以根据自己的需求选择合适的方式。

在“测试分发”中创建资源和发布资源版本不需要等待审核，一切操作都是实时的。你的资源文件也不会被上传到 GitHub 等三方平台，而是由 AstroBox 服务器本身承载存储服务。当然，这不意味着测试资源分发没有审核，我们仍会不定时检查测试资源的合法合规性，以防止有害内容的传播。

此外，我们注意到部分创作者会对资源审核的规范产生一些异议，因此我们推出了一套更完整的[资源内容规范](https://abox.run/docs/creator-tools/resource-std/content)。

如果你不知道将你的资源上传到 AstroBox 有什么意义，欢迎阅读 [Why AstroBox](https://abox.run/docs/creator-tools/why-astrobox)。
