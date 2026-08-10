#!/usr/bin/env python3
"""验证：业务线台账表（report-bizline.html）- 4 个新筛选项 + 列设置显隐功能"""

from playwright.sync_api import sync_playwright
from pathlib import Path

OUT = Path("/tmp/ygt-prototype-shots/v1.7.99.189-report-bizline")
OUT.mkdir(parents=True, exist_ok=True)

BASE = "http://localhost:8765"
EXEC = "/Users/fuyu/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=EXEC)
    ctx = browser.new_context(viewport={"width": 1920, "height": 1000})
    page = ctx.new_page()
    page.goto(f"{BASE}/pages/report-bizline.html", wait_until="networkidle")
    page.wait_for_timeout(800)

    # 1. 截图：默认状态
    page.screenshot(path=OUT / "01-default.png", full_page=False)

    # 2. 验证 4 个新筛选项
    new_filters = ["项目编号", "项目名称", "采/销框架合同", "采/销订单"]
    print("🅰️  4 个新筛选项：")
    for f in new_filters:
        cnt = page.locator(f".cp-filter-label:has-text('{f}')").count()
        print(f"  {'✅' if cnt > 0 else '❌'} '{f}': {cnt}")

    # 3. 原有 4 个筛选项还在
    old_filters = ["业务类型", "业务状态", "上游企业", "下游企业"]
    print("\n🅰️' 原有 4 个筛选项：")
    for f in old_filters:
        cnt = page.locator(f".cp-filter-label:has-text('{f}')").count()
        print(f"  {'✅' if cnt > 0 else '❌'} '{f}': {cnt}")

    # 4. 总筛选项数
    total_filters = page.locator(".cp-filter-label").count()
    print(f"\n🅱️  总筛选项: {total_filters} (期望 8)")

    # 5. 表头列数
    th_cnt = page.locator(".cp-table thead th").count()
    print(f"\n🅲  表格 th 数: {th_cnt} (期望 20)")

    # 6. 点击列设置按钮
    page.click("#colToggleBtn")
    page.wait_for_timeout(300)
    panel_visible = page.locator("#colTogglePanel").is_visible()
    print(f"\n🅳  列设置按钮 + 面板打开: {'✅' if panel_visible else '❌'}")
    page.screenshot(path=OUT / "02-col-panel-open.png", full_page=False)

    # 7. 列设置面板里 checkbox 数量
    cb_cnt = page.locator("#colTogglePanel input[type='checkbox']").count()
    print(f"  panel 里 checkbox 数: {cb_cnt} (期望 20)")

    # 8. 取消勾选第 6 列（上游货转）和第 18 列（状态）
    page.uncheck("input[data-col-idx='6']")
    page.uncheck("input[data-col-idx='18']")
    page.wait_for_timeout(300)

    # 验证：第 6、18 列所有单元格 display=none
    display_6 = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(6)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    display_18 = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(18)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    print(f"\n🅴  隐藏第 6 列（上游货转）: display 值 = {set(display_6)}")
    print(f"  隐藏第 18 列（状态）: display 值 = {set(display_18)}")
    page.screenshot(path=OUT / "03-col6-and-col18-hidden.png", full_page=False)

    # 9. 验证 localStorage
    ls = page.evaluate("() => localStorage.getItem('report-bizline-col-pref')")
    print(f"\n🅵  localStorage: {ls}")

    # 10. 恢复默认
    page.click("text=恢复默认")
    page.wait_for_timeout(300)
    display_after = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(6)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    print(f"\n🅶  恢复默认后第 6 列 display 值 = {set(display_after)} (期望全部为空)")

    # 11. 刷新后持久化
    page.uncheck("input[data-col-idx='7']")
    page.uncheck("input[data-col-idx='19']")
    page.wait_for_timeout(300)
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(800)
    display_7 = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(7)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    print(f"\n🅷  刷新后第 7 列 display = {set(display_7)}")
    page.screenshot(path=OUT / "04-after-reload-persist.png", full_page=False)

    # 12. 清理
    page.evaluate("() => localStorage.removeItem('report-bizline-col-pref')")
    browser.close()

print(f"\n✅ 截图保存到: {OUT}")
