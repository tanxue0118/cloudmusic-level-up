# 后端部署

这是 [ZainCheung/netease-cloud-api](https://github.com/ZainCheung/netease-cloud-api) 的容器化改进版，
增加了登录态文件管理、退出/状态接口与 CORS 支持，便于配合本项目的控制台使用。

基于上游项目修改，遵循其 MIT 许可（见 `LICENSE`）。感谢原作者。

## 环境要求

- 一台能上网的服务器（Linux 或 Windows 均可）
- Docker 与 Docker Compose v2
- 服务器能访问 `music.163.com`

## 部署步骤

1. 把 `server/` 目录整个上传到服务器，例如 `/opt/netease-autoplay/`

2. 进入目录并启动：

   ```bash
   cd /opt/netease-autoplay
   docker compose up -d --build
   ```

3. 确认状态：

   ```bash
   docker compose ps
   curl -s http://127.0.0.1:8080/?do=status
   ```

   返回 `{"code":200,"logged_in":false}` 即服务正常（尚未登录）。

## 端口

默认监听宿主机 `8080`。如需改动，在 `server/` 目录创建 `.env`：

```text
API_PORT=9000
```

然后 `docker compose up -d`。若要让外网访问，记得同时放行服务器防火墙与云厂商安全组端口。

## 登录态

后端把登录态存放在 `state/login.json`（通过 volume 挂载，重建容器不丢）。
该文件需要由登录工具写入——见仓库 `login-tool/` 说明。

`state/login.json` 内含账号 cookie，**不要提交到 Git**（`.gitignore` 已忽略）。

## 接口

| 路径 | 说明 |
|------|------|
| `/?do=status` | 查询是否已登录，返回 `{"code":200,"logged_in":true/false}` |
| `/?do=me` | 当前登录账号资料（昵称/头像/等级/听歌数/关注粉丝） |
| `/?do=level` | 等级进度：`level`、`nowPlayCount`、`nextPlayCount`、`remainPlayCount`、`progress` |
| `/?do=report&type=0\|1` | 听歌报告：0=全部，1=本周；返回总播放、歌曲数、歌手数、Top10 歌曲/歌手 |
| `/?do=logout` | 退出登录（删除登录态文件） |
| `/?do=detail&uid=UID` | 查询指定用户信息 |
| `/?do=daka` | 刷满 300 首 |
| `/?do=listen&id=歌单ID&time=次数` | 刷指定歌单 |

## 安全提示

- 后端接口**没有鉴权**。若暴露到公网，任何能访问该端口的人都能调用接口、退出登录。
  建议仅在**内网**使用，或在云安全组把端口限制为你的常用 IP。
- 登录态等同于账号权限，请勿泄露 `state/login.json`。

## 目录说明

```text
server/
├── Dockerfile        容器构建
├── compose.yaml      Compose 配置
├── index.php         接口实现（基于上游修改）
├── ui.html           控制台页面（与 web/index.html 相同）
├── help.html         兜底页面
├── LICENSE           上游 MIT 许可
└── state/            登录态（运行时生成，已被 .gitignore 忽略）
```
