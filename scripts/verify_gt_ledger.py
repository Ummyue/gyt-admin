#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发货管理「查看货转」货转台账弹窗验证（v1.30.0）。

用法: python3 scripts/verify_gt_ledger.py [BASE_URL]
默认 BASE_URL = http://127.0.0.1:8899
"""
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
URL = f"{BASE}/pages/shipment-out.html"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail and not cond else ""))


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        ctx = br.new_context(viewport={"width": 1600, "height": 950})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(600)

        # 弹窗默认不出现
        check("弹窗默认隐藏", not page.locator(".gt-modal").is_visible())

        # 列表里有「查看货转」按钮
        btns = page.locator(".col-action a", has_text="查看货转")
        check("列表存在「查看货转」按钮", btns.count() == 5, f"实际 {btns.count()}")

        # 点第一行（BN202607290009，2 条货转）→ 弹窗打开
        btns.first.click()
        page.wait_for_timeout(500)
        check("点击后弹窗打开", page.locator(".gt-modal").is_visible())
        check("弹窗标题为「查看货转台账」",
              page.locator(".gt-modal-title").inner_text() == "查看货转台账")
        info = page.locator("#gtLedgerInfo").inner_text()
        check("弹窗顶部展示发货摘要（批次号）", "BN202607290009" in info, info)
        check("弹窗顶部展示合同编号", "GTGYL-MSXS-20260127-s" in info, info)

        heads = page.locator(".gt-table thead th").all_inner_texts()
        expect_heads = ["合同编号", "货转编号", "买方企业", "卖方企业", "收货人",
                        "货转开具日", "货转数量(吨)", "发运方式", "状态"]
        check("弹窗表头与货转管理列表字段一致", heads == expect_heads, str(heads))

        rows = page.locator(".gt-table tbody tr")
        check("第一笔发货展示 2 条货转台账", rows.count() == 2, f"实际 {rows.count()}")
        check("底部统计为 2 条", "共 2 条货转台账" in page.locator("#gtLedgerCount").inner_text())
        r1 = rows.nth(0).inner_text()
        check("台账行含合同编号", "GTGYL-MSXS-20260127-s" in r1, r1)
        check("台账行含货转编号", "SKBT" in r1, r1)
        check("台账行含状态标签", "已生效" in r1, r1)
        r2 = rows.nth(1).inner_text()
        check("第 2 条为已作废状态", "已作废" in r2, r2)

        # 关闭
        page.click(".gt-modal-foot button")
        page.wait_for_timeout(350)
        check("点「关闭」弹窗关闭", not page.locator(".gt-modal").is_visible())

        # Esc 关闭
        btns.nth(1).click()
        page.wait_for_timeout(400)
        check("第 2 行打开弹窗（1 条货转）", page.locator(".gt-modal").is_visible())
        check("第 2 笔发货展示 1 条货转台账",
              page.locator(".gt-table tbody tr").count() == 1)
        page.keyboard.press("Escape")
        page.wait_for_timeout(350)
        check("Esc 关闭弹窗", not page.locator(".gt-modal").is_visible())

        # 空态（BN202607290003）
        btns.nth(4).click()
        page.wait_for_timeout(400)
        check("未开具货转的行弹出空态",
              "暂未开具货转台账" in page.locator("#gtLedgerBody").inner_text())
        check("空态时统计为 0 条", "共 0 条" in page.locator("#gtLedgerCount").inner_text())
        page.click(".gt-icon-btn")
        page.wait_for_timeout(300)
        check("点右上角 × 关闭弹窗", not page.locator(".gt-modal").is_visible())

        # 货转开具标识自洽：有货转的行 = 已开具
        rows_all = page.locator("tbody tr[data-status]")
        opened = page.locator("tbody tr td:nth-child(9)")
        vals = [opened.nth(i).inner_text().strip() for i in range(opened.count())]
        check("列表中「已开具」行数 = 4（与有台账的行数一致）",
              vals.count("已开具") == 4, str(vals))

        # favicon.ico 是浏览器自动请求，本地/线上都没这个文件 → 良性 404，排除
        real = [e for e in errs if "favicon" not in e.lower() and "Failed to load resource" not in e]
        check("无 JS 错误", len(real) == 0, "; ".join(real[:3]))
        page.screenshot(path="/tmp/gt-ledger.png")
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
