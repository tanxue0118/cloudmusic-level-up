# 网易云自动刷歌

一个自托管的网易云音乐自动刷歌方案：极简的控制台界面 + 容器化后端 + 本地登录工具。

把后端部署到自己的服务器，用控制台一键刷满每日 300 首、刷新指定歌单。

> ⚠️ 仅供个人学习与自建研究使用。请勿用于商业或非法用途，使用风险自负。
> 本项目会调用网易云非公开接口，可能违反其服务条款。

## 特性

- **极简控制台**：总览 / 登录 / 刷满 300 首 / 刷指定歌单 / 听歌报告 / 设置
- **等级进度**：显示当前等级、本等级已听/需听、距下一级还差多少首
- **听歌报告**：本周 / 全部时间的总播放、歌曲数、歌手数，以及 Top10 歌曲与歌手
- **容器化后端**：一条 `docker compose up -d` 即可跑起来
- **本地登录**：登录在你自己的电脑完成，绕开服务器环境的网易云风控
- **登录态持久化**：存服务器文件，重建容器不丢失
- **零前端依赖**：单文件 HTML，可本地打开也可托管

## 架构

```
┌─────────────────┐        HTTP        ┌──────────────────────┐
│  控制台网页      │  ───────────────▶ │  后端 (Docker/PHP)    │
│  web/index.html │                     │  server/  :8080      │
└─────────────────┘                     └──────────┬───────────┘
                                                    │ 读写
                                         ┌──────────▼───────────┐
                                         │  state/login.json    │
                                         │  （登录态）           │
                                         └──────────▲───────────┘
                                                    │ SSH 同步
                                         ┌──────────┴───────────┐
                                         │  本地登录工具         │
                                         │  login-tool/         │
                                         │  （在你电脑上运行）    │
                                         └──────────────────────┘
```

## 快速开始

### 1. 部署后端

把 `server/` 上传到服务器，运行：

```bash
cd server
docker compose up -d --build
curl -s http://127.0.0.1:8080/?do=status
```

详见 [`server/DEPLOY.md`](server/DEPLOY.md)。

### 2. 登录网易云

在**自己电脑**上，进入 `login-tool/`：

1. 复制 `config.example.json` 为 `config.json`，填入你的服务器信息
2. 双击 `登录网易云.bat`，在弹出窗口登录
3. 工具自动把登录态同步到服务器

详见 [`login-tool/README.md`](login-tool/README.md)。

### 3. 打开控制台

浏览器打开 `http://你的服务器:8080/`，即可使用。

也可以直接打开 `web/index.html`，在「设置」里填后端地址。

## 目录结构

```text
netease-autoplay/
├── web/
│   └── index.html          控制台界面（单文件，可独立托管）
├── server/                 后端（Docker）
│   ├── Dockerfile
│   ├── compose.yaml
│   ├── index.php
│   ├── ui.html
│   ├── DEPLOY.md
│   └── LICENSE             上游 MIT 许可
├── login-tool/             本地登录工具
│   ├── browser_login.py
│   ├── 登录网易云.bat
│   ├── config.example.json
│   └── README.md
└── .gitignore
```

## 设计

控制台参考 Vercel / Linear 一类的极简设计：

- 中性色为主，唯一强调色用网易云红 `#e23b2e`
- 字体：标题 Sora、正文 Noto Sans SC、代码 JetBrains Mono（Google Fonts）
- 桌面侧栏 + 移动端顶栏自适应

## 安全提示

- 后端接口**无鉴权**，请勿直接暴露到公网，建议限制来源 IP 或仅内网使用
- `config.json`、`state/login.json`、`.login-profile/` 均含敏感信息，切勿提交
- 登录态等价于账号权限，泄露后果自负

## 致谢

后端基于 [ZainCheung/netease-cloud-api](https://github.com/ZainCheung/netease-cloud-api) 修改，
遵循其 MIT 许可。灵感来自 [Binaryify/NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)。

## 声明

本项目的所有脚本以及软件仅用于个人学习开发测试，所有网易云相关字样版权属于网易公司，勿用于商业及非法用途，如产生法律纠纷与本人无关。

## 许可

本项目遵循 MIT 许可。上游相关版权归原作者所有。
