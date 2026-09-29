# AstroBox-Repo
AstroBox的官方软件源仓库

## 相关公告
### 2026-8-18
自AstroBox v2.1版本起，现有“表盘 快应用”分类将被调整为“表盘 快应用 模块”。

表盘与快应用和传统定义别无二异
模块：由Canopus支撑的特殊资源类型，模块具有两种类型的能力：原生应用注册能力&系统拓展能力。模块可以只包含其一种能力，也可以两种能力同时拥有。这意味着你可以基于Canopus 拥有纯粹的原生应用能力的模块，制作一个功能更丰富的应用；也可以基于 Canopus 打造一个拥有系统拓展能力的模块，修改系统内的一些功能，期待大家的想象力。

同时，自该版本起，我们也将开放「模块资源类型」的上架。由于模块自身权限极高，出于对用户设备安全的考量，开发者除了进行合理分类外，还需向审核人员提交完整的模块源代码与编译流程，最终上架的模块文件须由审核人员在完成安全审计后自行编译，开发者自行提交的模块产物将不予采用。上架审核过程中，开发者有义务回答并协助审核人员解决在编译过程中遇到的任何问题。

### 2025-7-26
即日起，任何作者在 AstroBox 官方源上传的免费资源数量必须是付费资源的 2 倍以上。如果你并没有上传任何资源，则必须先提交两个免费资源，才能上传一个付费资源。
付费资源必须严格标注付费，我们将在 csv 中添加新的字段，对于存在任何应用内购买或类型为试用的资源，必须标注为付费，并且付费资源将在首页被明显标注，并允许被用户一键过滤。
已通过审核的资源不受该规定影响

## 举报与处罚
如果你认为有资源不应该出现在这里，或资源不符合我们的提交要求，欢迎在此仓库中开启Issue发起质询，我们会进行相应的处理。

同时也可阅读[资源下架清单](REMOVED.md)以获取下架过的资源的列表以及下架原因。

## 资源要求
可参考[资源提交规范](assets/docs/submission_standards.md)和[AstroBox-NG资源适配规范](assets/docs/ResAdptV2.md)

## 审核流程
可参见[《AstroBox 官方社区源资源审核标准》](assets/docs/review_standards.docx)

## 资源创作者社区
可加入此[QQ群](https://qm.qq.com/q/XVnT5deGiW)

## 徽标链接
我们提供了多种"Get it on AstroBox"徽标以便您放置在您的资源发布页、帖子中，用户点击该徽标后能快速跳转至AstroBox应用内下载资源：

![](https://astrobox.online/goab/en/white.svg)

请在合适的地方插入以下html以添加该徽标：
```html
<a href="https://astrobox.online/open?source=res&res=资源名称&provider=official" target="_blank" rel="noopener noreferrer">
  <img src="https://astrobox.online/goab/en/white.svg">
</a>
```

<table>
  <thead>
    <tr>
      <th>语言</th>
      <th>样式</th>
      <th>配色</th>
      <th>图片</th>
      <th>链接</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="9">简体中文</td>
      <td rowspan="3">标准</td>
      <td>黑色</td>
      <td><img src="https://astrobox.online/goab/zhcn/black.svg" alt="黑色" style="min-width: 234px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/black.svg">https://astrobox.online/goab/zhcn/black.svg</a></code></td>
    </tr>
    <tr>
      <td>灰色</td>
      <td><img src="https://astrobox.online/goab/zhcn/gray.svg" alt="灰色" style="min-width: 234px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/gray.svg">https://astrobox.online/goab/zhcn/gray.svg</a></code></td>
    </tr>
    <tr>
      <td>亮色</td>
      <td><img src="https://astrobox.online/goab/zhcn/white.svg" alt="亮色" style="min-width: 234px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/white.svg">https://astrobox.online/goab/zhcn/white.svg</a></code></td>
    </tr>
    <tr>
      <td rowspan="3">胶囊</td>
      <td>黑色</td>
      <td><img src="https://astrobox.online/goab/zhcn/rounded/black.svg" alt="胶囊黑色" style="min-width: 228px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/rounded/black.svg">https://astrobox.online/goab/zhcn/rounded/black.svg</a></code></td>
    </tr>
    <tr>
      <td>灰色</td>
      <td><img src="https://astrobox.online/goab/zhcn/rounded/gray.svg" alt="胶囊灰色" style="min-width: 228px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/rounded/gray.svg">https://astrobox.online/goab/zhcn/rounded/gray.svg</a></code></td>
    </tr>
    <tr>
      <td>亮色</td>
      <td><img src="https://astrobox.online/goab/zhcn/rounded/white.svg" alt="胶囊亮色" style="min-width: 228px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/rounded/white.svg">https://astrobox.online/goab/zhcn/rounded/white.svg</a></code></td>
    </tr>
    <tr>
      <td rowspan="3">链接</td>
      <td>黑色</td>
      <td><img src="https://astrobox.online/goab/zhcn/linked/black.svg" alt="链接黑色" style="min-width: 256px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/linked/black.svg">https://astrobox.online/goab/zhcn/linked/black.svg</a></code></td>
    </tr>
    <tr>
      <td>灰色</td>
      <td><img src="https://astrobox.online/goab/zhcn/linked/gray.svg" alt="链接灰色" style="min-width: 256px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/linked/gray.svg">https://astrobox.online/goab/zhcn/linked/gray.svg</a></code></td>
    </tr>
    <tr>
      <td>亮色</td>
      <td><img src="https://astrobox.online/goab/zhcn/linked/white.svg" alt="链接亮色" style="min-width: 256px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/zhcn/linked/white.svg">https://astrobox.online/goab/zhcn/linked/white.svg</a></code></td>
    </tr>
    <tr>
      <td rowspan="9">英文</td>
      <td rowspan="3">标准</td>
      <td>黑色</td>
      <td><img src="https://astrobox.online/goab/en/black.svg" alt="黑色" style="min-width: 234px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/black.svg">https://astrobox.online/goab/en/black.svg</a></code></td>
    </tr>
    <tr>
      <td>灰色</td>
      <td><img src="https://astrobox.online/goab/en/gray.svg" alt="灰色" style="min-width: 234px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/gray.svg">https://astrobox.online/goab/en/gray.svg</a></code></td>
    </tr>
    <tr>
      <td>亮色</td>
      <td><img src="https://astrobox.online/goab/en/white.svg" alt="亮色" style="min-width: 234px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/white.svg">https://astrobox.online/goab/en/white.svg</a></code></td>
    </tr>
    <tr>
      <td rowspan="3">胶囊</td>
      <td>黑色</td>
      <td><img src="https://astrobox.online/goab/en/rounded/black.svg" alt="胶囊黑色" style="min-width: 228px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/rounded/black.svg">https://astrobox.online/goab/en/rounded/black.svg</a></code></td>
    </tr>
    <tr>
      <td>灰色</td>
      <td><img src="https://astrobox.online/goab/en/rounded/gray.svg" alt="胶囊灰色" style="min-width: 228px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/rounded/gray.svg">https://astrobox.online/goab/en/rounded/gray.svg</a></code></td>
    </tr>
    <tr>
      <td>亮色</td>
      <td><img src="https://astrobox.online/goab/en/rounded/white.svg" alt="胶囊亮色" style="min-width: 228px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/rounded/white.svg">https://astrobox.online/goab/en/rounded/white.svg</a></code></td>
    </tr>
    <tr>
      <td rowspan="3">链接</td>
      <td>黑色</td>
      <td><img src="https://astrobox.online/goab/en/linked/black.svg" alt="链接黑色" style="min-width: 256px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/linked/black.svg">https://astrobox.online/goab/en/linked/black.svg</a></code></td>
    </tr>
    <tr>
      <td>灰色</td>
      <td><img src="https://astrobox.online/goab/en/linked/gray.svg" alt="链接灰色" style="min-width: 256px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/linked/gray.svg">https://astrobox.online/goab/en/linked/gray.svg</a></code></td>
    </tr>
    <tr>
      <td>亮色</td>
      <td><img src="https://astrobox.online/goab/en/linked/white.svg" alt="链接亮色" style="min-width: 256px; min-height: 46px; height: 46px;" /></td>
      <td><code><a href="https://astrobox.online/goab/en/linked/white.svg">https://astrobox.online/goab/en/linked/white.svg</a></code></td>
    </tr>
  </tbody>
</table>


### 规范化使用
为保证在页面上的可读性，我们建议您在使用徽标时将其高度设为 46px，最小不应低于 40px

<img height="93" alt="高度展示图" src="https://github.com/user-attachments/assets/bc87f41b-a020-4799-8d20-b4b285196d29" />

当高度为 46px 时，字号为 16px；当高度为 40px 时，字号为 14px

徽标的外边距建议应为高度的 1.25 倍 (125%)，在等比缩放后还需四舍五入以使得数不保留小数点，如 46px 高边距即为 12px，40px 高边距即为 5px
