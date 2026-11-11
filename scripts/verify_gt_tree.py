#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""角色权限详情抽屉 · 已授权权限树交互验证（v1.35.0）。

用法: python3 scripts/verify_gt_tree.py [BASE_URL]
"""
import sys
import os
import re

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pb_auth import add_gate_cookie, host_of  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail and not cond else ""))


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

        page.goto(f"{BASE}/pages/account-role-permission.html", wait_until="networkidle")
        page.wait_for_timeout(800)

        # 打开「系统管理员」的权限详情抽屉（权限项最多的角色）
        page.locator("tr", has_text="系统管理员").locator(".rp-act-link", has_text="查看权限").click()
        page.wait_for_timeout(700)
        check("权限详情抽屉打开", page.locator(".rp-drawer").is_visible())

        # 1) 统计胶囊 = 一级菜单数
        sums = page.locator(".rp-gt-sum-item")
        check("顶部按一级模块给出统计胶囊", sums.count() >= 5, f"实际 {sums.count()} 个")
        sum_text = sums.first.inner_text()
        check("统计胶囊含项数", "项" in sum_text, sum_text)

        # 2) 树结构：一级模块 + 二级菜单
        lv0 = page.locator(".rp-gt-node.lv0")
        lv1 = page.locator(".rp-gt-node.lv1")
        check("树含一级模块节点（仅显示有已授权项的模块）",
              lv0.count() == 6, f"实际 {lv0.count()}")
        check("树含二级菜单节点", lv1.count() >= 20, f"实际 {lv1.count()}")

        # 3) 默认态：一级展开、二级收起 → 首屏不是几百个 chip
        def visible_chips():
            return page.locator(".rp-gt-op").evaluate_all(
                "els => els.filter(e => e.offsetHeight > 0).length")
        check("默认二级菜单收起，首屏可见操作项数可控（< 60）",
              visible_chips() < 60, f"实际 {visible_chips()}")

        # 4) 展开二级 → 显示该菜单的操作 chip
        page.locator(".rp-gt-node.lv1 .rp-gt-head").first.click()
        page.wait_for_timeout(300)
        check("点击二级菜单展开后出现操作按钮 chip", page.locator(".rp-gt-op").count() > 0)

        # 5) 全部展开 / 全部收起
        page.click("#rpGtExpand")
        page.wait_for_timeout(400)
        expanded = visible_chips()
        check("「全部展开」后操作 chip 全部铺开（> 150）", expanded > 150, f"实际 {expanded}")
        page.click("#rpGtCollapse")
        page.wait_for_timeout(400)
        check("「全部收起」后回到模块级摘要",
              visible_chips() < 60, f"实际 {visible_chips()}")

        # 6) 统计胶囊点击 → 折叠/展开该模块
        before = page.locator(".rp-gt-node.lv0.open").count()
        sums.first.click()
        page.wait_for_timeout(300)
        after = page.locator(".rp-gt-node.lv0.open").count()
        check("点击统计胶囊可切换该模块展开状态", before != after, f"{before} → {after}")

        # 7) 搜索：过滤 + 高亮
        page.fill("#rpGtSearch", "导出")
        page.wait_for_timeout(500)
        hits = page.locator(".rp-gt-op.hit")
        check("搜索可跨层级过滤并高亮命中项", hits.count() > 0, f"实际 {hits.count()}")

        # ⚠️ 命中数必须**递归统计到子节点**且与统计胶囊之和一致
        #    （此前只遍历顶层节点，导致命中数恒为 0）
        def parse_hit(text):
            m = re.search(r"命中\s*(\d+)\s*项", text)
            return int(m.group(1)) if m else -1

        def pill_sum():
            # 胶囊文案形如 "3 项"
            total = 0
            for t in page.locator(".rp-gt-sum-item i").all_inner_texts():
                m = re.search(r"(\d+)", t)
                if m:
                    total += int(m.group(1))
            return total

        tool_txt = page.locator(".rp-gt-toolbar").inner_text()
        hit_n = parse_hit(tool_txt)
        check("搜索时提示命中数量且大于 0", hit_n > 0, f"工具条文本: {tool_txt!r}")
        check("命中数与统计胶囊项数之和一致", hit_n == pill_sum(),
              f"命中 {hit_n} vs 胶囊和 {pill_sum()}")
        note_txt = page.locator("#rpGtNote").inner_text()
        check("区块标题的命中数与工具条一致", f"命中 {hit_n} /" in note_txt,
              f"标题文本: {note_txt!r}")

        check("搜索后未命中模块被隐藏",
              page.locator(".rp-gt-sum-item").count() < 6,
              f"实际 {page.locator('.rp-gt-sum-item').count()}")

        # 无关键字时：总数应等于当前权限项总数，且胶囊之和 == 标题总数
        page.fill("#rpGtSearch", "")
        page.wait_for_timeout(400)
        check("清空搜索后恢复完整树", page.locator(".rp-gt-sum-item").count() >= 5)
        full_note = page.locator("#rpGtNote").inner_text()
        m = re.search(r"共\s*(\d+)\s*项操作权限", full_note)
        total_n = int(m.group(1)) if m else -1
        check("清空搜索后标题显示总项数", total_n > 0, f"标题文本: {full_note!r}")
        check("清空搜索后胶囊项数之和 == 标题总数", pill_sum() == total_n,
              f"胶囊和 {pill_sum()} vs 标题 {total_n}")
        check("清空搜索后总数 == 全部展开后的 chip 数",
              total_n == page.locator(".rp-gt-op").count(),
              f"标题 {total_n} vs chip {page.locator('.rp-gt-op').count()}")

        # 8) 旧版摊平 chip 列表已移除
        check("旧的摊平 chip 列表已移除", page.locator(".rp-granted-list").count() == 0)

        check("无 JS 错误", len(errs) == 0, "; ".join(errs[:3]))
        page.screenshot(path="/tmp/gt-tree.png")
        br.close()

    print()
    print(f"通过 {len(PASS)}/{len(PASS) + len(FAIL)}")
    if FAIL:
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
