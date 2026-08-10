#!/usr/bin/env python3
"""验证：业务线台账表 - 5 个新筛选项 + 列设置显隐功能"""

from playwright.sync_api import sync_playwright
from pathlib import Path

OUT = Path("/tmp/ygt-prototype-shots/v1.7.99.188-filter-and-col-toggle")
OUT.mkdir(parents=True, exist_ok=True)

BASE = "http://localhost:8765"
EXEC = "/Users/fuyu/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=EXEC)
    ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    page.goto(f"{BASE}/pages/business-line.html", wait_until="networkidle")
    page.wait_for_timeout(800)

    # 1. 截图：默认状态
    page.screenshot(path=OUT / "01-default.png", full_page=False)

    # 2. 验证 5 个新筛选项存在
    new_filters = ["项目编号", "项目名称", "采/销框架合同", "采/销订单", "上下游企业"]
    print("🅰️  5 个新筛选项检查：")
    for f in new_filters:
        cnt = page.locator(f".cp-filter-label:has-text('{f}')").count()
        print(f"  {'✅' if cnt > 0 else '❌'} '{f}': {cnt}")

    # 3. 验证列设置按钮存在
    btn_cnt = page.locator("#colToggleBtn").count()
    print(f"\n🅱️  列设置按钮: {'✅ 存在' if btn_cnt else '❌ 不存在'}")

    # 4. 点击列设置按钮
    page.click("#colToggleBtn")
    page.wait_for_timeout(300)
    panel_visible = page.locator("#colTogglePanel").is_visible()
    print(f"  面板打开: {'✅' if panel_visible else '❌'}")
    page.screenshot(path=OUT / "02-col-panel-open.png", full_page=False)

    # 5. 取消勾选"货物进度"列（第 2 列）
    page.uncheck("input[data-col-idx='2']")
    page.wait_for_timeout(300)
    # 验证：所有第 2 列单元格 display = none
    display_2 = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(2)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    print(f"\n🅲 隐藏第 2 列（货物进度）: display 值 = {set(display_2)}")
    page.screenshot(path=OUT / "03-col2-hidden.png", full_page=False)

    # 6. 再取消勾选"发票进度"列（第 5 列）
    page.uncheck("input[data-col-idx='5']")
    page.wait_for_timeout(300)
    display_5 = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(5)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    print(f"🅳 隐藏第 5 列（发票进度）: display 值 = {set(display_5)}")
    page.screenshot(path=OUT / "04-col2-and-col5-hidden.png", full_page=False)

    # 7. 验证 localStorage
    ls = page.evaluate("() => localStorage.getItem('business-line-col-pref')")
    print(f"\n🅴 localStorage: {ls}")

    # 8. 点击恢复默认
    page.click("text=恢复默认")
    page.wait_for_timeout(300)
    display_after_reset = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(2)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    print(f"🅵 恢复默认后第 2 列 display 值 = {set(display_after_reset)} (期望全部为空)")
    page.screenshot(path=OUT / "05-reset-default.png", full_page=False)

    # 9. 重新隐藏 2 列后刷新页面，验证 localStorage 持久化
    page.uncheck("input[data-col-idx='3']")
    page.uncheck("input[data-col-idx='4']")
    page.wait_for_timeout(300)
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(800)
    print("\n🅶 刷新后，验证 localStorage 持久化：")
    display_3 = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(3)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    display_4 = page.evaluate("""() => {
        const cells = document.querySelectorAll('.cp-table tr > *:nth-child(4)');
        return Array.from(cells).map(c => c.style.display);
    }""")
    print(f"  第 3 列（资金进度）display = {set(display_3)}")
    print(f"  第 4 列（结算进度）display = {set(display_4)}")
    page.screenshot(path=OUT / "06-after-reload-persist.png", full_page=False)

    # 10. 清理 localStorage 避免污染下次测试
    page.evaluate("() => localStorage.removeItem('business-line-col-pref')")

    browser.close()

print(f"\n✅ 截图保存到: {OUT}")
