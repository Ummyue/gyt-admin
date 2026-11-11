#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工作台门禁会话 cookie 获取（自动化回归用）。

背景：2026-11-10 起，原型工作台加了统一口令门禁（nginx `auth_request`），
**IP 直连和域名都要求登录**，未登录访问会被 302 到 /workbench/login.html。
所以 Playwright 直连拿到的会是登录页 → 断言全挂。

解决：服务器上 `sudo python3 /srv/git/_auth/mint_session.py <用户名>` 签发一个
会话 token（复用 auth_server 自身的签名算法，不改账号数据），用 `pb_session`
cookie 注入浏览器上下文，即可正常访问被门禁保护的页面。

用法：
    from pb_auth import add_gate_cookie
    ctx = br.new_context(...)
    add_gate_cookie(ctx, "192.144.175.203")
"""
import os
import subprocess

SSH = [
    "ssh", "-i", os.path.expanduser("~/.ssh/id_lighthouse"),
    "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
    "ubuntu@192.144.175.203",
]

COOKIE_NAME = "pb_session"


def get_session_token(user="yjj_user"):
    """到服务器上签发一个会话 token；失败返回空串。"""
    try:
        r = subprocess.run(
            SSH + ["sudo python3 /srv/git/_auth/mint_session.py " + user],
            capture_output=True, text=True, timeout=90,
        )
    except Exception:
        return ""
    lines = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
    return lines[-1] if lines else ""


def add_gate_cookie(ctx, host, user="yjj_user"):
    """给 Playwright context 注入门禁 cookie。成功返回 True。"""
    token = get_session_token(user)
    if not token:
        return False
    ctx.add_cookies([{
        "name": COOKIE_NAME,
        "value": token,
        "domain": host,
        "path": "/",
    }])
    return True


def host_of(url):
    """从 URL 里取 host（供 add_gate_cookie 用）。"""
    s = url.split("://", 1)[-1]
    return s.split("/", 1)[0].split(":", 1)[0]
