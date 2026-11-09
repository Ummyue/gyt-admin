#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站回归 v1.23.0：所有页面可达 + 菜单结构 + 无 JS 错误。

用法: python3 scripts/regress_site.py [BASE_URL]
默认 BASE_URL = http://127.0.0.1:8899
"""

import sys
import os
import glob
import urllib.request
import urllib.error

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))
    print(f"{'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail and not cond else ""))


def http_status(url):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return 0, str(e).encode()


def main():
    # ---------- 1. 静态页全部可达 ----------
    pages = sorted(glob.glob(os.path.join(ROOT, "pages", "*.html")))
    bad = []
    for p in pages:
        rel = os.path.relpath(p, ROOT)
        st, _ = http_status(f"{BASE}/{rel}")
        if st != 200:
            bad.append(f"{rel}={st}")
    check(f"pages/ 下 {len(pages)} 个页面全部 200", not bad, "; ".join(bad[:5]))

    # 根页面 / app.html / 共享资源
    for rel in ["index.html", "app.html", "login.html",
                "shared/js/topnav-drawer.js", "shared/js/left-sidemenu.js",
                "shared/js/permission-tree.js", "assets/css/design-system.css",
                "assets/css/list-page.css"]:
        st, _ = http_status(f"{BASE}/{rel}")
        check(f"{rel} 可达", st == 200, f"HTTP {st}")

    # ---------- 2. 权限树数据完整性 ----------
    st, body = http_status(f"{BASE}/shared/js/permission-tree.js")
    txt = body.decode("utf-8")
    check("permission-tree.js 声明 PERMISSION_TREE", "window.PERMISSION_TREE" in txt)
    check("权限树含 7 个一级菜单", txt.count('"icon":') == 7, str(txt.count('"icon":')))
    check("权限树含操作权限项", txt.count('"ops": [') >= 60, str(txt.count('"ops": [')))
    # 合同管理：新增/编辑页并入宿主菜单后，下级只保留 3 个可配置菜单
    import json as _json
    _d = _json.loads(txt[txt.index("["):txt.rindex(";")])
    _cm = None
    for _m in _d:
        for _sm in _m["subMenus"]:
            if _sm["label"] == "合同管理":
                _cm = _sm
    check("合同管理 下级只保留 采购合同/销售合同/补充协议",
          _cm is not None and [c["label"] for c in _cm["children"]]
          == ["采购合同", "销售合同", "补充协议"],
          str([c["label"] for c in _cm["children"]] if _cm else None))
    _pc = [c for c in _cm["children"] if c["label"] == "采购合同"][0]
    check("采购合同 操作权限已并入新增页 5 项（合计 9 项）",
          len(_pc["ops"]) == 9, str(len(_pc["ops"])))
    check("并入的菜单码记在 mergedMenus",
          [m["label"] for m in _pc["mergedMenus"]]
          == ["新增采购框架合同", "新增采购订单/单批次合同"],
          str([m["label"] for m in _pc["mergedMenus"]]))

    # ---------- 3. 浏览器端回归 ----------
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        ctx = br.new_context(viewport={"width": 1560, "height": 950})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" and "favicon" not in m.text.lower()
                and "Failed to load resource" not in m.text else None)

        # 3.1 账户中心三页：左菜单都应出现
        for f in ["account-role-permission.html", "account-company.html", "account-personal.html"]:
            page.goto(f"{BASE}/pages/{f}", wait_until="networkidle")
            page.wait_for_timeout(350)
            sm = page.locator("#leftSidemenu").inner_text()
            # 「企业管理」是目录项，未命中当前页时默认折叠 → 子项在 DOM 里但不可见，
            # 所以查 DOM 存在性而不是可见文本
            in_dom = page.locator('#leftSidemenu a[href*="account-role-permission.html"]').count()
            check(f"{f} 左菜单 DOM 含「角色权限管理」链接", in_dom >= 1, sm[:80])
            check(f"{f} 左菜单出现「企业管理」", "企业管理" in sm)
            if f == "account-company.html":
                # 企业管理 现在是目录项，企业中心仍要可达
                hrefs = page.locator("#leftSidemenu a.sidemenu-item").evaluate_all(
                    "els => els.map(e => e.getAttribute('href'))")
                check("企业中心仍可从左菜单直达",
                      any("account-company.html" in (h or "") for h in hrefs), str(hrefs))
                check("角色权限管理从左菜单直达",
                      any("account-role-permission.html" in (h or "") for h in hrefs), str(hrefs))

        # 3.2 其它模块页面左菜单未被破坏（抽样）
        for f, kw in [("project-list.html", "项目准入"), ("contract-purchase.html", "合同管理"),
                      ("warehouse-inbound.html", "入库管理"), ("cockpit.html", "驾驶舱"),
                      ("warning-list.html", "预警管理")]:
            page.goto(f"{BASE}/pages/{f}", wait_until="networkidle")
            page.wait_for_timeout(300)
            sm = page.locator("#leftSidemenu").inner_text()
            check(f"{f} 左菜单正常渲染（{kw}）", kw in sm, sm[:80])

        # 3.3 app.html 工作台导航出现新页
        page.goto(f"{BASE}/app.html", wait_until="networkidle")
        page.wait_for_timeout(700)
        tree = page.locator("#sidemenuTree").inner_text()
        check("app.html 左侧树出现「角色权限管理」", "角色权限管理" in tree, tree[:150])
        check("app.html 左侧树出现「企业中心」", "企业中心" in tree)

        # 3.4 点击新页 → iframe 载入 + 右侧文档渲染
        clicked = page.locator(".tree-item", has_text="角色权限管理").count()
        check("app.html 树里有可点击的「角色权限管理」条目", clicked >= 1)
        if clicked:
            page.locator(".tree-item", has_text="角色权限管理").first.click()
            page.wait_for_timeout(1800)
            frame_ok = False
            for fr in page.frames:
                if "account-role-permission" in (fr.url or ""):
                    frame_ok = True
                    break
            check("点击后 iframe 载入角色权限管理页", frame_ok)
            doc = page.locator("#docBody").inner_text()
            check("右侧文档渲染出角色权限管理说明", "角色权限管理" in doc, doc[:120])

        check("全站回归无 JS 错误", len(errs) == 0, "; ".join(errs[:3]))
        br.close()

    print()
    print(f"通过 {len(PASS)}/{len(PASS) + len(FAIL)}")
    if FAIL:
        print("失败项:")
        for n, d in FAIL:
            print(f"  - {n}  {d}")
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
