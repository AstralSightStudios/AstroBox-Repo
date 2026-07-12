---
type: "Weekly"
title: "V2.0.2 版本更新"
subtitle: "本周优化版本已发布"
author: "AstroBox"
date: 2026-07-13
cover: "https://raw.githubusercontent.com/AstralSightStudios/AstroBox-Repo/refs/heads/main/blogs/weekly/cover.png"
---

所有喜爱、关注与支持 AstroBox 的用户大家好！感谢你参与 AstroBox 2.0 的公测！

自 AstroBox 正式发布以来，我们收到了非常多反馈，感谢所有小伙伴填写的问卷！v2.0.2 是一个以移动端体验补全与基础设施加固为主的维护版本，我们为App Store上架调整了一些内容，同时显著改善了网络错误提示、固件校验容错和构建脚本稳定性。

iOS 版现已上架 App Store，若你在使用 iOS/iPadOS，请前往 App Store 搜索 AstroBox 下载并更新。

## 新增

- 系统通知推送集成 — 信箱中的内容（如收到点赞、回复）现在支持通过苹果APNs或谷歌FCM进行推送
- 应用内购买 (IAP) — iOS 端捐赠计划改为默认通过 App Store 应用内购买。
- iOS 内置登录 — 支持在 iOS 端直接完成账户登录，无需跳转外部浏览器。
- 音乐元数据自动提取 — 上传音乐文件时自动从文件字节中解析并提取元数据信息。
- 文件类型自动检测 — 向队列添加资源时移除手动下拉选择，改为根据文件内容自动识别类型。

## 修复

- 网络错误提示 — 网络请求失败时现在展示具体错误原因，不再只显示通用文案。
- 固件校验容错 — 当固件验证无效时增加“继续安装”选项，避免完全阻断用户操作。

## 改进

- OTA 固件检测 — core 模块改用标准 ZIP 解析来识别 OTA 固件包，提升检测准确性。
- Provider 下载策略 — 当使用 Raw CDN 且用户已登录时，自动回退至 GitHub API 获取资源，提升下载稳定性。
- 账户安全 — privaccount 模块为刷新令牌 (refresh token) 轮换增加互斥锁，防止并发下的令牌竞争问题。
- UI 细节 — 优化了一些样式细节
- i18n — 补全多语言翻译词条。

## 写在最后

以上是这个版本的更新内容，如果你有更多的建议、又或是发现了更多的问题，欢迎点击填写 [这份反馈问卷](https://xykong-technology.feishu.cn/share/base/form/shrcnZScNiXcdtK7xhoDo4Fwysd)，我们会进行评估，针对有效的建议进行逐一优化实现，感谢你的参与！

期待 AstroBox 未来能与大家共同成长，持续构建一个优秀的第三方穿戴设备工具箱。