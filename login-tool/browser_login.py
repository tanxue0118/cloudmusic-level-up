# -*- coding: utf-8 -*-
"""网易云登录工具（通用版）。

在你自己的电脑上打开网易云官方登录窗口，登录成功后自动把登录态
同步到你的服务器，供 netease-autoplay 后端使用。

准备：
1. 复制 config.example.json 为 config.json，填好自己的服务器信息
2. 安装依赖：py -m pip install playwright paramiko requests
3. 首次运行需要下载浏览器内核：py -m playwright install msedge
   （或已安装 Edge 浏览器可跳过）

用法：双击「登录网易云.bat」，或运行 py browser_login.py
"""
import json
import sys
import time
from pathlib import Path

import paramiko
import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config.json"
PROFILE = ROOT / ".login-profile"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def load_config():
    """读取 config.json；不存在时给出明确指引。"""
    if not CONFIG.exists():
        print("未找到 config.json。")
        print(f"请复制 {ROOT / 'config.example.json'} 为 config.json，并填入你的服务器信息。")
        sys.exit(1)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    required = ("server_host", "api_port", "ssh_user", "remote_dir")
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        print("config.json 缺少字段：" + ", ".join(missing))
        sys.exit(1)
    if not cfg.get("ssh_password") and not cfg.get("ssh_key_path"):
        print("config.json 需要填写 ssh_password 或 ssh_key_path 之一。")
        sys.exit(1)
    return cfg


def verify_cookie(cookies):
    """调用网易云接口验证登录态，返回昵称；无效返回 None。"""
    try:
        resp = requests.get(
            "http://music.163.com/api/nuser/account/get",
            cookies=cookies, headers={"User-Agent": UA}, timeout=15,
        )
        data = resp.json()
        if data.get("code") == 200 and data.get("profile"):
            return data["profile"].get("nickname") or "已登录"
    except Exception as exc:  # noqa: BLE001
        print(f"  验证请求失败：{exc}")
    return None


def connect_ssh(cfg):
    """按配置建立 SSH 连接（支持密码或密钥）。"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs = {
        "hostname": cfg["server_host"],
        "port": int(cfg.get("ssh_port", 22)),
        "username": cfg["ssh_user"],
        "timeout": 15,
    }
    if cfg.get("ssh_key_path"):
        kwargs["key_filename"] = cfg["ssh_key_path"]
        kwargs["look_for_keys"] = False
    else:
        kwargs["password"] = cfg["ssh_password"]
        kwargs["look_for_keys"] = False
        kwargs["allow_agent"] = False
    client.connect(**kwargs)
    return client


def push_to_server(cfg, cookies):
    """把登录态写入服务器 state/login.json，并通过服务端接口确认。"""
    remote = cfg["remote_dir"].rstrip("/")
    body = json.dumps({"MUSIC_U": cookies["MUSIC_U"],
                       "__csrf": cookies.get("__csrf", "")})
    client = connect_ssh(cfg)
    try:
        client.exec_command(f"mkdir -p {remote}/state")[1].read()
        sftp = client.open_sftp()
        try:
            with sftp.open(f"{remote}/state/login.json", "w") as handle:
                handle.write(body)
        finally:
            sftp.close()
        # 容器以 www-data(uid 33) 运行，需要让它可读
        client.exec_command(
            f"chown 33:33 {remote}/state/login.json 2>/dev/null; "
            f"chmod 644 {remote}/state/login.json")[1].read()
    finally:
        client.close()
    try:
        url = f"http://{cfg['server_host']}:{cfg['api_port']}/?do=status"
        check = requests.get(url, timeout=15).json()
        return check.get("logged_in") is True
    except Exception as exc:  # noqa: BLE001
        print(f"  服务端校验失败：{exc}")
        return False


def main():
    cfg = load_config()
    PROFILE.mkdir(exist_ok=True)
    print("=" * 52)
    print(" 网易云登录工具（登录后自动同步到服务器）")
    print("=" * 52)
    print(f"目标服务器：{cfg['server_host']}:{cfg['api_port']}")
    print("正在打开登录窗口，请稍候…")
    sys.stdout.flush()

    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE),
                channel="msedge",
                headless=False,
                viewport={"width": 1100, "height": 800},
                args=["--no-first-run", "--no-default-browser-check"],
            )
        except Exception as exc:  # noqa: BLE001
            print("无法启动浏览器：" + str(exc))
            print("请确认已安装 Edge，或先运行：py -m playwright install msedge")
            sys.exit(1)

        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto("https://music.163.com/#/login",
                      wait_until="domcontentloaded", timeout=60000)
        except Exception as exc:  # noqa: BLE001
            print("页面加载提示：", exc)
        print("请在窗口里登录（扫码 / 账号密码 / 短信均可）。")
        print("登录成功后会自动同步到服务器，请勿手动关闭窗口。")
        sys.stdout.flush()

        deadline = time.time() + 600
        done = False
        while time.time() < deadline:
            try:
                cookies = {c["name"]: c["value"]
                           for c in ctx.cookies("https://music.163.com")}
            except Exception:  # 窗口被手动关闭
                print("窗口已关闭，未完成同步。可重新运行本工具。")
                ctx.close()
                sys.exit(1)
            music_u = cookies.get("MUSIC_U")
            if music_u:
                print("检测到登录 cookie，正在验证…")
                sys.stdout.flush()
                nickname = verify_cookie({"MUSIC_U": music_u,
                                          "__csrf": cookies.get("__csrf", "")})
                if nickname:
                    print(f"登录有效：{nickname}")
                    print("正在同步到服务器…")
                    sys.stdout.flush()
                    if push_to_server(cfg, cookies):
                        print("同步成功，服务器登录态已更新。")
                    else:
                        print("同步后校验未通过，请检查 config.json 与服务器状态。")
                    done = True
                    break
                else:
                    print("检测到 cookie 但尚未生效，继续等待登录完成…")
                    sys.stdout.flush()
            time.sleep(3)
        if not done:
            print("等待超时（10 分钟）。可以重新运行本工具。")
        ctx.close()

    print("完成，可以关闭本窗口了。")


if __name__ == "__main__":
    main()
