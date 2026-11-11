#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""缓存新鲜度回归：验证「改了 js 后，浏览器普通刷新就能拿到新版本」。

为什么需要这个测试
------------------
2026-11-09 踩坑：nginx 给 .js 设了 `Cache-Control: public, max-age=604800`（7 天强缓存），
用户浏览器一直用旧版 permission-tree.js，而我用 Playwright 验证时**每次都是全新 profile
（无缓存）**，所以测出来全是绿的 —— 典型的假阴性。

本测试用**持久化 profile**（复用磁盘缓存）复现真实浏览器的缓存行为：
  1. 首次加载 → 浏览器缓存 js
  2. 在服务器上改 js 内容
  3. 普通 reload（不是硬刷新）→ 断言拿到的是新内容

用法: python3 scripts/verify_cache_freshness.py [BASE_URL]
默认 BASE_URL = http://192.144.175.203
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://192.144.175.203"
JS_PATH = "/var/www/yugangtong/shared/js/permission-tree.js"
SSH = ["ssh", "-i", os.path.expanduser("~/.ssh/id_lighthouse"),
       "-o", "ConnectTimeout=15", "ubuntu@192.144.175.203"]

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail and not cond else ""))


def sh(cmd, sudo=False):
    c = SSH + [cmd]
    if sudo:
        c = SSH + ["sudo " + cmd]
    r = subprocess.run(c, capture_output=True, text=True, timeout=90)
    return r.stdout + r.stderr


def tree_labels(page):
    return page.locator("#permTree .rp-tnode").evaluate_all(
        "els => els.map(e => e.getAttribute('data-label'))")


def main():
    from playwright.sync_api import sync_playwright
        # 用 Playwright 自带 Chromium 而非系统 Chrome：
        # 系统 Chrome 会把 http:// 自动升级成 https://（HTTPS-First），
        # 而 192.144.175.203 没有 443 证书 → 直连 IP 报 ERR_BLOCKED_BY_CLIENT。
        # 真实用户请走正式入口 https://www.yf9.club。

    profile = tempfile.mkdtemp(prefix="pb-cache-profile-")
    backup = "/tmp/permission-tree.js.bak-cache-test"
    try:
        # 备份服务器上的 js
        sh(f"sudo cp {JS_PATH} {backup}")

        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                profile, viewport={"width": 1500, "height": 950})
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(f"{BASE}/pages/account-role-permission.html", wait_until="networkidle")
            page.wait_for_timeout(800)
            page.click("button.btn.btn-primary")
            page.wait_for_timeout(600)

            first = tree_labels(page)
            check("首次加载渲染出权限树", len(first) > 50, str(len(first)))
            check("首次加载含最新菜单名「预警查询」", "预警查询" in first, str(first[:10]))

            # 记录 js 的缓存响应头
            js_hdr = {}
            def on_resp(r):
                if r.url.endswith("permission-tree.js") or "permission-tree.js?" in r.url:
                    js_hdr.update(r.headers)
            page.on("response", on_resp)
            page.reload(wait_until="networkidle")
            page.wait_for_timeout(600)
            cc = (js_hdr.get("cache-control") or "").lower()
            check("js 响应头为 no-cache（不再是 7 天强缓存）",
                  "no-cache" in cc or "must-revalidate" in cc, f"cache-control={js_hdr.get('cache-control')!r}")

            # --- 改服务器上的 js，普通 reload 应拿到新内容 ---
            marker = "预警查询CACHE探针"
            sh(f"sudo sed -i 's/预警查询/{marker}/g' {JS_PATH}")
            time.sleep(1.5)

            page.reload(wait_until="networkidle")
            page.wait_for_timeout(900)
            page.click("button.btn.btn-primary")
            page.wait_for_timeout(700)
            second = tree_labels(page)
            check("改文件后普通刷新即拿到新内容（无陈旧缓存）",
                  marker in second, f"未出现探针，实际前 10 项={second[:10]}")

            # 恢复
            sh(f"sudo cp {backup} {JS_PATH}")
            time.sleep(1.0)
            page.reload(wait_until="networkidle")
            page.wait_for_timeout(900)
            page.click("button.btn.btn-primary")
            page.wait_for_timeout(700)
            third = tree_labels(page)
            check("恢复文件后刷新也正确", marker not in third and "预警查询" in third,
                  str(third[:10]))
            ctx.close()
    finally:
        sh(f"sudo cp {backup} {JS_PATH}")
        sh(f"rm -f {backup}")
        shutil.rmtree(profile, ignore_errors=True)

    print()
    print(f"通过 {len(PASS)}/{len(PASS) + len(FAIL)}")
    if FAIL:
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
