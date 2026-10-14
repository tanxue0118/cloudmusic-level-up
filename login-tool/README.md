# 登录工具

在**你自己的电脑**上登录网易云，并把登录态同步到你的服务器。

网页端扫码登录容易被网易云判定「设备环境异常」，因此登录在本地完成——
走你家的网络，不经过服务器，成功率更高。

## 准备工作

1. 安装 [Python 3](https://www.python.org/downloads/)（安装时勾选 "Add to PATH"）

2. 复制配置文件并填写：

   ```
   config.example.json  →  config.json
   ```

   用文本编辑器打开 `config.json`，填入你的服务器信息：

   ```json
   {
     "server_host": "你的服务器 IP",
     "api_port": 8080,
     "ssh_port": 22,
     "ssh_user": "root",
     "ssh_password": "你的 SSH 密码",
     "ssh_key_path": "",
     "remote_dir": "/opt/netease-autoplay"
   }
   ```

   - `ssh_password` 与 `ssh_key_path` 二选一：用密钥登录就填 `ssh_key_path`（私钥文件路径），密码登录就填 `ssh_password`
   - `remote_dir` 填你部署后端时的目录

## 使用

双击 **`登录网易云.bat`**（首次会自动安装依赖，稍等片刻）。

- 会弹出网易云登录窗口
- 用扫码 / 账号密码 / 短信任意方式登录
- 登录成功后工具自动验证并同步到服务器，看到「同步成功」即可关闭

之后回到控制台网页点「刷新状态」就能看到已登录。

## 手动运行

不想用 bat，也可以在命令行执行：

```bash
py -m pip install playwright paramiko requests
py -m playwright install msedge
py browser_login.py
```

## 常见问题

**提示找不到 config.json**
复制 `config.example.json` 为 `config.json` 再运行。

**无法启动浏览器**
确保系统已安装 Edge 浏览器；或执行 `py -m playwright install msedge` 安装内核。

**同步后校验未通过**
检查 `config.json` 里的 IP、端口、SSH 账号是否正确，以及服务器后端容器是否在运行。

**登录态多久失效**
通常可用数周到数月。失效后重新运行一次本工具即可。

## 注意

- `config.json` 含你的服务器密码，**不要提交到 Git**（`.gitignore` 已忽略）
- `.login-profile/` 目录保存浏览器登录态，同样不要提交
