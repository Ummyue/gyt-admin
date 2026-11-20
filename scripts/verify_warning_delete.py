#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""预警规则配置页 · 列表操作列「删除」交互验证（v1.36.0）。

用法: python3 scripts/verify_warning_delete.py [BASE_URL]
"""
import sys
import os

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pb_auth import add_gate_cookie, host_of  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail and not cond else ""))


TABS = [
    ("enterprise", "企业监控"),
    ("transaction", "交易监控"),
    ("price", "价格波动"),
]


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1600, "height": 1000})
        add_gate_cookie(ctx, host_of(BASE))
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

        page.goto(f"{BASE}/pages/warning-config.html", wait_until="networkidle")
        page.wait_for_timeout(700)

        # ---------- 1) 三个 tab 的列表操作列都有「删除」 ----------
        for key, label in TABS:
            scope = f"#wc-tab-{key}"
            del_links = page.locator(f"{scope} tbody .wc-del")
            n = del_links.count()
            check(f"{label} tab：列表每行都有「删除」入口", n >= 10, f"实际 {n} 个")

            # 表头有「操作」列
            heads = page.locator(f"{scope} thead th").all_inner_texts()
            check(f"{label} tab：表头含「操作」列", "操作" in heads, f"表头 {heads}")

            # 列数一致（colgroup / th / td）
            ncol = page.locator(f"{scope} colgroup col").count()
            nth = page.locator(f"{scope} thead th").count()
            ntd = page.locator(f"{scope} tbody tr").first.locator("td").count()
            check(f"{label} tab：列数一致", ncol == nth == ntd, f"col {ncol} / th {nth} / td {ntd}")

        # ---------- 2) 点击删除 → 居中二次确认弹窗 ----------
        page.click(".wc-tab[data-wc-tab='transaction']")
        page.wait_for_timeout(400)
        page.locator("#wc-tab-transaction tbody .wc-del").first.click()
        page.wait_for_timeout(400)
        mask = page.locator("#wcConfirmMask")
        check("点击「删除」弹出二次确认弹窗", mask.is_visible())
        box = page.locator(".wc-confirm").bounding_box()
        vw = page.viewport_size
        centered = abs((box["x"] + box["width"] / 2) - vw["width"] / 2) < 40
        check("确认弹窗居中显示", centered, f"box={box}")

        rule_name = page.locator("#wc-tab-transaction tbody tr").first.locator("td").nth(1).inner_text().strip()
        ctext = page.locator("#wcConfirmText").inner_text()
        check("确认文案含规则名称", rule_name in ctext, f"文案={ctext!r}")
        check("确认文案含不可恢复提示", "不可恢复" in ctext, f"文案={ctext!r}")

        # ---------- 3) 取消 → 行保留 ----------
        rows_before = page.locator("#wc-tab-transaction tbody tr").count()
        page.locator(".wc-confirm-foot .btn-secondary").click()
        page.wait_for_timeout(300)
        check("点「取消」关闭弹窗", not mask.is_visible())
        check("点「取消」行未被删除",
              page.locator("#wc-tab-transaction tbody tr").count() == rows_before)

        # ---------- 4) Esc 关闭 ----------
        page.locator("#wc-tab-transaction tbody .wc-del").first.click()
        page.wait_for_timeout(300)
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        check("Esc 可关闭确认弹窗", not mask.is_visible())
        check("Esc 关闭后行未被删除",
              page.locator("#wc-tab-transaction tbody tr").count() == rows_before)

        # ---------- 5) 确定 → 行被删除 + toast ----------
        page.locator("#wc-tab-transaction tbody .wc-del").first.click()
        page.wait_for_timeout(300)
        page.locator(".wc-confirm-foot .btn-danger").click()
        page.wait_for_timeout(500)
        check("点「确认删除」后该行被移除",
              page.locator("#wc-tab-transaction tbody tr").count() == rows_before - 1,
              f"{rows_before} → {page.locator('#wc-tab-transaction tbody tr').count()}")
        toast_visible = page.locator("#wcToast").evaluate(
            "e => e.classList.contains('show') && e.textContent.includes('已删除')")
        check("删除后出现 toast 反馈", toast_visible,
              page.locator("#wcToast").inner_text())
        check("删除后确认弹窗已关闭", not mask.is_visible())

        # ---------- 6) 三个 tab 的删除都生效 ----------
        for key, label in TABS[::2]:
            page.click(f".wc-tab[data-wc-tab='{key}']")
            page.wait_for_timeout(400)
            before = page.locator(f"#wc-tab-{key} tbody tr").count()
            page.locator(f"#wc-tab-{key} tbody .wc-del").first.click()
            page.wait_for_timeout(300)
            ok = page.locator(".wc-confirm-foot .btn-danger")
            check(f"{label} tab：删除流程可走通", ok.is_visible())
            ok.click()
            page.wait_for_timeout(400)
            check(f"{label} tab：行数减 1",
                  page.locator(f"#wc-tab-{key} tbody tr").count() == before - 1)

        # ---------- 7) 权限树含「删除」权限项（去角色权限页校验，该页才加载权限树）----------
        page.goto(f"{BASE}/pages/account-role-permission.html", wait_until="networkidle")
        page.wait_for_timeout(900)
        tree_txt = page.evaluate("() => window.PERMISSION_TREE ? JSON.stringify(window.PERMISSION_TREE) : ''")
        check("权限树已加载", bool(tree_txt))
        if tree_txt:
            import json
            tree = json.loads(tree_txt)

            def find(nodes):
                for n in nodes:
                    if n.get("label") == "预警设置":
                        return n
                    r = find(n.get("children") or [])
                    if r:
                        return r
                return None

            # 权限树结构：一级菜单 → subMenus（二级）→ children（三级）
            flat_nodes = []
            for mod in tree:
                for sub in mod.get("subMenus") or []:
                    flat_nodes.append(sub)
            node = find(flat_nodes)
            check("权限树含「预警设置」节点", node is not None)
            if node:
                labels = [o["label"] for o in node.get("ops") or []]
                check("「预警设置」权限项含「删除」", "删除" in labels, f"当前 {labels}")
                codes = [o["code"] for o in node.get("ops") or []]
                check("「添加规则」权限码保持 op1 未漂移",
                      "预警中心/预警设置#op1" in codes, f"当前 {codes}")
                check("「编辑」权限码保持 edit 未漂移",
                      "预警中心/预警设置#edit" in codes, f"当前 {codes}")
                check("「删除」权限码为 delete",
                      "预警中心/预警设置#delete" in codes, f"当前 {codes}")

        check("无 JS 错误", not errs, "; ".join(errs[:3]))
        br.close()

    print(f"\n通过 {len(PASS)}/{len(PASS) + len(FAIL)}")
    if FAIL:
        print("未通过：")
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
