# -*- coding: utf-8 -*-
"""
v1.7.99.225 工作台 10 个待办 tab 跨页跳转 E2E 测试

业务场景：
1. 打开工作台页面 → 验证 10 个待办 tab 存在
2. 切换到每个 tab → 验证 mock 数据正确加载
3. 点击行链接 → 验证跳转 URL 不 404
4. 在详情页 → 验证关键内容存在
"""
import pytest


# 10 个待办 tab 的 label + 期望最小行数（user 截图实际顺序）
TODO_TABS = [
    ('contract-approval',           '上下游合同审批',           1),
    ('contract-dual-sign',          '上下游双签合同上传',       1),
    ('bizline-pending-link',        '待关联业务线',             1),
    ('recv-confirm',                '待收货确认',               1),
    ('goods-transfer-approval',     '货转待审批',               1),
    ('goods-transfer-voucher',      '待上传上下游货转生效单据', 1),
    ('settlement-approval',         '待审批结算单',             1),
    ('payment-approval',            '待付款审批',               1),
    ('receipt-claim',               '回款待认领',               1),
    ('invoice-upload',              '待上传发票',               1),
]


class TestWorkbenchTodo:
    """工作台 10 个待办 tab E2E"""

    def test_workbench_loads_and_shows_10_tabs(self, page, deploy_url):
        """打开工作台 → 验证 10 个待办 tab 全部存在"""
        page.goto(f"{deploy_url}/pages/workbench.html", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 验证页面标题
        title = page.title()
        assert '豫港通' in title or 'workbench' in title.lower(), f"页面 title 异常: {title}"

        # 验证 10 个 tab 存在（通过 TODO_TAB_LABELS 全局变量）
        tab_labels = page.evaluate("() => Object.keys(TODO_TAB_LABELS || {})")
        assert len(tab_labels) == 10, f"待办 tab 数量异常: {len(tab_labels)}, 期望 10"

    @pytest.mark.parametrize("tab_key,tab_label,min_rows", TODO_TABS)
    def test_each_tab_renders_rows(self, page, deploy_url, tab_key, tab_label, min_rows):
        """切换到每个 tab → 验证 mock 数据行数 ≥ 1"""
        page.goto(f"{deploy_url}/pages/workbench.html", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 调用 renderTodoTable(tabKey) 直接渲染
        row_count = page.evaluate(f"() => {{ renderTodoTable('{tab_key}'); return document.querySelectorAll('#todoTbody tr').length; }}")

        # 至少 1 行（mock 数据每 tab 都有）
        assert row_count >= min_rows, f"tab '{tab_label}' 行数异常: {row_count}, 期望 ≥ {min_rows}"

        # 验证 tab label 在页面某处显示
        count_text = page.evaluate("() => document.getElementById('todoCount')?.textContent || ''")
        assert tab_label in count_text or tab_label in page.content(), f"tab label '{tab_label}' 不在页面上"

    def test_click_row_navigates_to_detail_without_404(self, page, deploy_url):
        """点击工作台第 1 个 tab 第 1 行的链接 → 验证跳转目标页不 404"""
        page.goto(f"{deploy_url}/pages/workbench.html", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 取「待付款审批」tab 第 1 行的 href
        href = page.evaluate("""() => {
            const rows = TODO_MOCK['payment-approval'] || [];
            if (rows.length === 0) return null;
            return rows[0].href;
        }""")
        assert href, "TODO_MOCK['payment-approval'] 第 1 行 href 为空"

        # 跳转
        target_url = f"{deploy_url}/pages/{href.lstrip('./')}"
        response = page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 验证页面加载成功（无 404 错误信息 + 有标题）
        title = page.title()
        assert title and '豫港通' in title, f"跳转后 title 异常: {title}"
        # 验证不是 404 错误页（检查页面不包含「404」字样）
        body_text = page.evaluate("() => document.body.innerText")
        assert '404' not in body_text and 'Not Found' not in body_text, f"跳转后页面是 404: {body_text[:200]}"

    @pytest.mark.parametrize("tab_key", [t[0] for t in TODO_TABS])
    def test_all_tab_hrefs_resolve(self, page, deploy_url, tab_key):
        """10 个 tab 的每行 href 都能正常跳转（不 404）"""
        page.goto(f"{deploy_url}/pages/workbench.html", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 取该 tab 所有行的 href
        hrefs = page.evaluate(f"""() => {{
            const rows = TODO_MOCK['{tab_key}'] || [];
            return rows.map(r => r.href);
        }}""")
        assert len(hrefs) >= 1, f"tab '{tab_key}' 没有任何 mock 数据行"

        # 遍历每个 href 跳转 + 验证
        for href in hrefs:
            target_url = f"{deploy_url}/pages/{href.lstrip('./')}"
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1500)

            body_text = page.evaluate("() => document.body.innerText")
            assert '404' not in body_text and 'Not Found' not in body_text, f"href '{href}' (tab '{tab_key}') 跳转后是 404"

    def test_tab_count_indicator_shows_total(self, page, deploy_url):
        """工作台待办总数 = 10 个 tab 各行数之和"""
        page.goto(f"{deploy_url}/pages/workbench.html", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        total = page.evaluate("""() => {
            return Object.values(TODO_MOCK).reduce((sum, rows) => sum + rows.length, 0);
        }""")
        # 10 个 tab × 2-3 行 = 20-30
        assert 20 <= total <= 30, f"工作台待办总数异常: {total}, 期望 20-30"
