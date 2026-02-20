# AstroBox-NG适配流程
## 一、对于本仓库的修改
### 1.1 新的CSV文件结构
在最新的[index_v2.csv](../../index_v2.csv)中添加资源信息，最新的csv结构如下。
> 对于Visual Studio Code，可以安装[Rainbow CSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv)插件来更好地编辑csv文件。
```csv
id,name,restype,repo_owner,repo_name,repo_commit_hash,icon,cover,tags,device_vendors,devices,paid_type
com.searchstars.hyperbilibili,澎湃哔哩,quick_app,searchstars,Hyperbilibili_AstroBox_Release,650a7b4,icon.png,preview.png,客户端;实用工具;视频;社区;互动;在线;哔哩哔哩;B站;b站,xiaomi,xmws3;xmws4;xmrw5xring,
979808741600,endID,watchface,hrsthrt74,endID-for-astrobox,b3d1e51,icon.png,cover.png,表盘,xiaomi,xmrw6;xmrw5xring;xmrw5;xmws4;xmb9p;xmb10;xmb10nfc,
```
### 1.2 CSV字段说明
- id：唯一标识（快应用包名），若是表盘则以`<placeholder>`占位，我们会单独分配表盘ID，必填。`＜placeholder＞`大致结构如`979808741600`

| A(两位)           | B(两位)           | 作者名(四位)      | 系列(两位)      | 分支(两位)      |
|-------------------|-------------------|-------------------|-----------------|-----------------|
| 97                | 98                | 如h74为0874       | 如01            | 如01            |

> 前四位数字固定，分别为A(97)B(98)对应的ASCII编码，剩下八位由作者自己支配，建议结构为四位数字（字母要用ASCII转换），用于作者名字。后四位数字，两两一组分别代表表盘系列序号和分支序号。此为根据目前的表盘ID得到的惯例，正式版可能修改。

- name：名称，必填，且必须和你的仓库中manifest中的完全一致。
- restype：资源类型（quick_app / watchface / firmware），必填。
- repo_owner：资源仓库所有者GitHub名称(**非GitHub昵称**)，
- repo_name：资源仓库所有者名下的GitHub仓库名，必填。
- repo_commit_hash：资源仓库对应版本的提交短哈希，必填，更新后需要同步在此仓库更新此字段，此字段用于防止提交者滥改资源。
- icon/cover：展示用图在仓库中的文件名，必填，直接写对于根目录的路径。比如：如果放在根目录下，直接写`xxx.png`即可，如果在根目录的一个名为`xx`的子文件夹下，则写`./xx/icon.png`即可。
- tags：数组，用于分类和搜索，必填。
- device_vendor：数组，支持的设备的制造商 (xiaomi / vivo / ...)，必填。
- devices：数组，支持的设备 ID，可以从[这里](#设备对照列表)获取，必须和manifest中的完全一致，必填。
- paid_type：付费类型（paid / force_paid），免费则留空，自愿付费类资源属于免费。
## 二、对于自己仓库的修改
### 2.1 根目录的manifest_v2.json，必填
独立于v1版本的manifest.json，可以在同一仓库同时支持v1和v2。

```json
{
  "item": {
    "id": "com.searchstars.hyperbilibili",
    "restype": "quick_app",
    "name": "澎湃哔哩",
    "description": "为Xiaomi Vela穿戴设备打造的第三方哔哩哔哩客户端",
    "preview": ["preview.png", "preview2.png", "preview3.png"],
    "icon": "icon.png",
    "cover": "preview.png",
    "author": [
      {
        "name": "Searchstars",
        "bindABAccount": true
      }
    ]
  },
  "links": [
    {
      "icon": "",
      "title": "官方网站",
      "url": "https://hyperbili.astralsight.space"
    }
  ],
  "downloads": {
    "xmws3": {
      "version": "2.5",
      "file_name": "circle_com.searchstars.hyperbilibili.rpk"
    },
    "xmws4": {
      "version": "2.5",
      "file_name": "circle_com.searchstars.hyperbilibili.rpk"
    },
    "xmrw5xring": {
      "version": "2.5",
      "file_name": "rect_com.searchstars.hyperbilibili.rpk"
    },
    "xmb9p": {
      "version": "2.4",
      "file_name": "narrow_rect_com.searchstars.hyperbilibili.rpk"
    }
  },
  "ext": {}
}
```
### 2.2 字段说明
- **item**：资源基本信息。
   - **id**：唯一标识，必须与index_v2.csv中的id一致。
   - **restype**：资源类型（quick_app / watchface / firmware），必须与index_v2.csv中的restype一致。
   - **name**：显示名称，必须与index_v2.csv中的name一致。
   - **description**：对你资源的描述，可使用转义符来换行。
   - **preview**：进入详情页中展示的预览图片。若资源使用了知名 IP 素材，必须在 preview 中包含一张版权声明图
   - **icon**：资源图标.
   - **cover**：资源封面图。
   - **author**：作者信息，选填。`bindABAccount`为true根据`name`绑定到指定的AstroBox账号，选填。
- **links**：相关链接列表，选填。可填入官网、开源地址、QQ加群跳转等。
  - **icon**：AstroBox NextGen用了统一的图标库，为了保持风格统一，这里只能填[Phosphor](https://phosphoricons.com/)中的图标名称，比如`github-logo`、`house`、`telegram-logo`等等。
- **downloads**：下载资源，按设备ID划分。设备ID与index_v2.csv中的devices一致。
  - **version**：资源版本号。
  - **file_name**：资源文件名路径。
- **ext**：扩展字段，用于未来的拓展。

### 设备对照列表

| name                          | id           |
|------------------------------|--------------|
| Xiaomi Smart Band 9          | xmb9         |
| Xiaomi Smart Band 9 Pro      | xmb9p        |
| Xiaomi Smart Band 10         | xmb10        |
| Xiaomi Smart Band 10 NFC     | xmb10nfc     |
| Xiaomi Watch S3 系列         | xmws3        |
| Xiaomi Watch S4 系列         | xmws4        |
| Xiaomi Watch S4 15周年纪念版 | xmws4xring   |
| REDMI Watch 5                | xmrw5        |
| REDMI Watch 5 eSIM           | xmrw5xring   |
| REDMI Watch 6                | xmrw6        |
| vivo WATCH GT 2              | vivowgt2     |
