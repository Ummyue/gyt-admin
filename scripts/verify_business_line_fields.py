#!/usr/bin/env python3
"""截图验证：业务线台账表 + 详情页 6 个新字段的位置和排版"""

from playwright.sync_api import sync_playwright
from pathlib import Path

OUT = Path("/tmp/ygt-prototype-shots/v1.7.99.187-business-line-fields")
OUT.mkdir(parents=True, exist_ok=True)

BASE = "http://localhost:8765"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path="/Users/fuyu/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
    ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()

    # 1. 业务线台账表
    page.goto(f"{BASE}/pages/business-line.html", wait_until="networkidle")
    page.wait_for_timeout(500)
    page.screenshot(path=OUT / "01-business-line-list.png", full_page=True)

    # 验证：第 1 行 cell 字段顺序
    first_row_info_lines = page.locator(".col-bl-info").first.locator(".bl-info-line").all_text_contents()
    print("📋 第 1 行 业务线信息 cell 的字段顺序：")
    for i, line in enumerate(first_row_info_lines, 1):
        # 只取字段名前 30 字符
        print(f"  {i:2d}. {line.strip()[:60]}")

    # 验证 6 个新字段都在
    expected_new = ["采购订单/单批次合同编号", "销售订单/单批次合同编号", "项目编号", "项目名称", "采购框架合同编号", "销售框架合同编号"]
    for f in expected_new:
        count = page.locator(f".bl-info-line:has-text('{f}')").count()
        print(f"  ✅ '{f}': 出现 {count} 次 (期望 4 次)")

    # 2. 业务线详情页
    page.goto(f"{BASE}/pages/business-line-detail.html", wait_until="networkidle")
    page.wait_for_timeout(500)
    page.screenshot(path=OUT / "02-business-line-detail.png", full_page=False)

    # 验证：详情页头部 10 个字段
    meta_lines = page.locator(".bl-header-meta > div").all_text_contents()
    print("\n📋 详情页 头部 bl-header-meta 字段顺序：")
    for i, line in enumerate(meta_lines, 1):
        print(f"  {i:2d}. {line.strip()[:60]}")

    # 验证 6 个新字段都在
    for f in expected_new:
        count = page.locator(f".bl-header-meta div:has-text('{f}')").count()
        print(f"  ✅ '{f}': 出现 {count} 次 (期望 1 次)")

    browser.close()

print(f"\n✅ 截图保存到: {OUT}")
