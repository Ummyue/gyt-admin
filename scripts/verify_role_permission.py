#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""角色权限管理页 v1.23.0 端到端验证。

用法: python3 scripts/verify_role_permission.py [BASE_URL]
默认 BASE_URL = http://127.0.0.1:8899
"""

import sys
import os
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
PAGE_URL = f"{BASE}/pages/account-role-permission.html"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    mark = "✅" if cond else "❌"
    print(f"{mark} {name}" + (f"  — {detail}" if detail and not cond else ""))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        ctx = browser.new_context(viewport={"width": 1600, "height": 950})
        page = ctx.new_page()
        errors = []
        missing = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append("PAGEERROR: " + str(e)))
        page.on("response", lambda r: missing.append(f"{r.status} {r.url}")
                if r.status >= 400 else None)

        page.goto(PAGE_URL, wait_until="networkidle")
        page.wait_for_timeout(500)

        # ---------- 1. 列表页 ----------
        check("页面标题正确", "角色权限管理" in page.title())
        check("面包屑含角色权限管理",
              "角色权限管理" in page.locator(".breadcrumb-inline").inner_text())
        rows = page.locator("#rpTbody tr")
        check("角色表格渲染出种子角色（5 条）",
              page.locator("#rpTbody tr").count() == 5,
              f"实际 {page.locator('#rpTbody tr').count()} 行")
        check("首屏有 4 张统计卡", page.locator(".rp-stat-card").count() == 4)
        body_txt = page.locator("#rpTbody").inner_text()
        check("含「系统管理员」角色", "系统管理员" in body_txt)
        check("含「仅本人创建的数据」数据权限标记", "仅本人创建的数据" in body_txt)
        check("数据权限徽标渲染", page.locator(".rp-scope-badge").count() >= 5)

        # 左侧菜单：账户中心 → 企业管理 → 角色权限管理
        sm = page.locator("#leftSidemenu").inner_text()
        check("左菜单挂上角色权限管理", "角色权限管理" in sm, sm[:120])
        check("左菜单含企业管理分组", "企业管理" in sm)

        # ---------- 2. 筛选 ----------
        page.fill("#fltName", "财务")
        page.wait_for_timeout(250)
        check("按名称筛选命中 1 条",
              page.locator("#rpTbody tr").count() == 1,
              f"实际 {page.locator('#rpTbody tr').count()}")
        check("筛选 chip 出现", page.locator(".filter-chip").count() >= 1)
        page.click("#rpClearAll")
        page.wait_for_timeout(200)
        check("清除筛选后恢复 5 条",
              page.locator("#rpTbody tr").count() == 5)

        # ---------- 3. 抽屉（查看权限） ----------
        page.locator(".rp-act-link", has_text="查看权限").first.click()
        page.wait_for_timeout(400)
        check("右侧抽屉打开", page.locator(".rp-drawer").is_visible())
        drawer_txt = page.locator("#drawerBody").inner_text()
        check("抽屉显示数据权限说明", "全部数据" in drawer_txt or "仅本人创建" in drawer_txt)
        check("抽屉显示权限概览统计", "菜单权限" in drawer_txt and "操作按钮" in drawer_txt)
        check("抽屉渲染权限树节点（7 一级 + 74 子节点）",
              page.locator("#drawerBody .rp-tnode").count() == 81,
              f"实际 {page.locator('#drawerBody .rp-tnode').count()}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        check("Esc 关闭抽屉", not page.locator(".rp-drawer").is_visible())

        # ---------- 4. 新增角色弹窗 ----------
        page.click("button.btn.btn-primary")
        page.wait_for_timeout(400)
        check("新增角色弹窗打开", page.locator(".rp-modal").is_visible())
        check("弹窗标题为新增角色",
              page.locator("#roleModalTitle").inner_text() == "新增角色")
        check("左树渲染 81 个菜单节点（7 一级 + 74 子节点）",
              page.locator("#permTree .rp-tnode").count() == 81,
              f"实际 {page.locator('#permTree .rp-tnode').count()}")
        check("左树一级菜单 7 个",
              page.locator('#permTree .rp-tnode[data-depth="0"]').count() == 7)
        check("新建时自动定位到第一个带操作的菜单（项目准入）",
              "新增立项申请" in page.locator("#opBody").inner_text(),
              page.locator("#opBody").inner_text()[:80])

        # 数据权限切换
        page.click('.rp-scope-opt[data-scope="own"]')
        page.wait_for_timeout(200)
        check("数据权限切到「仅本人创建的数据」",
              page.locator('.rp-scope-opt[data-scope="own"]').get_attribute("class").find("on") >= 0)
        check("数据权限提示文案同步更新",
              "只能看到自己创建的单据" in page.locator("#scopeTipText").inner_text())

        # 选菜单节点 → 看操作按钮
        page.click('.rp-tnode[data-label="项目准入"] .rp-tnode-label')
        page.wait_for_timeout(250)
        op_txt = page.locator("#opBody").inner_text()
        check("选中二级菜单后右侧显示操作按钮",
              "新增立项申请" in op_txt, op_txt[:100])
        check("操作按钮带权限编码",
              "#" in page.locator(".rp-op-code").first.inner_text())
        ops_before = page.locator(".rp-op-item").count()
        check("项目准入权限项收敛为 10 项（user 图1 审核结果）", ops_before == 10, f"实际 {ops_before}")
        op_labels = page.locator(".rp-op-label").all_inner_texts()
        for gone in ["确认上传", "全部标记已读", "查看", "替换", "删除"]:
            check(f"项目准入已剔除「{gone}」权限项", gone not in op_labels, str(op_labels))
        for keep in ["新增立项申请", "数据导出", "编辑", "提交", "作废", "撤回",
                     "重新提交", "上传客户准入报告", "上传决议文件", "发起完结"]:
            check(f"项目准入保留「{keep}」权限项", keep in op_labels, str(op_labels))

        # 勾选一个操作按钮 → 计数变化
        cnt_before = page.locator("#opCount").inner_text()
        page.locator(".rp-op-item input").first.click()
        page.wait_for_timeout(250)
        cnt_after = page.locator("#opCount").inner_text()
        check("勾选操作按钮后已选计数变化", cnt_before != cnt_after,
              f"{cnt_before} -> {cnt_after}")
        check("底部汇总提示出现", "已选" in page.locator("#roleFootTip").inner_text())

        # 树 checkbox 联动
        page.click('.rp-tnode[data-label="准入管理"] [data-check]')
        page.wait_for_timeout(300)
        foot = page.locator("#roleFootTip").inner_text()
        # 准入管理 = 1 个一级 + 3 个二级；操作按钮 10 + 6 + 4 = 20（user 审核收敛后）
        check("勾选一级菜单联动全部下级（4 菜单 / 20 按钮）",
              "已选 4 个菜单 · 20 个操作按钮" in foot, foot)

        # 客户准入 / 黑名单管理 也按 user 图2 / 图3 收敛
        page.click('.rp-tnode[data-label="客户准入"] .rp-tnode-label')
        page.wait_for_timeout(250)
        cl = page.locator(".rp-op-label").all_inner_texts()
        check("客户准入权限项收敛为 6 项（user 图2 审核结果）", len(cl) == 6, str(cl))
        for gone in ["查看状态机说明", "查看额度", "发起完结"]:
            check(f"客户准入已剔除「{gone}」权限项", gone not in cl, str(cl))
        page.click('.rp-tnode[data-label="黑名单管理"] .rp-tnode-label')
        page.wait_for_timeout(250)
        bl = page.locator(".rp-op-label").all_inner_texts()
        check("黑名单管理权限项收敛为 4 项（user 图3 审核结果）", len(bl) == 4, str(bl))
        for gone in ["批量删除", "下载模板", "开始导入"]:
            check(f"黑名单管理已剔除「{gone}」权限项", gone not in bl, str(bl))

        # 全选 / 清空操作按钮
        page.click('.rp-tnode[data-label="项目准入"] .rp-tnode-label')
        page.wait_for_timeout(200)
        page.click('.rp-perm-right-tools button:has-text("全选")')
        page.wait_for_timeout(200)
        check("全选后当前页操作全选中",
              page.locator('.rp-op-item input[checked]').count() == 10,
              f"实际 {page.locator('.rp-op-item input[checked]').count()}")
        page.click('.rp-perm-right-tools button:has-text("清空")')
        page.wait_for_timeout(200)
        check("清空后当前页操作全不选中",
              page.locator('.rp-op-item input[checked]').count() == 0)

        # 树搜索
        page.fill("#treeSearch", "保证金")
        page.wait_for_timeout(300)
        kept = page.locator("#permTree .rp-tnode").count()
        check("树搜索「保证金」过滤生效", 0 < kept < 72, f"实际 {kept}")
        page.fill("#treeSearch", "")
        page.wait_for_timeout(250)

        # 保存：先清空权限应被拦截
        page.click('.rp-perm-right-tools button:has-text("清空")')
        page.wait_for_timeout(150)
        page.locator(".rp-modal-foot button.btn-primary").click()
        page.wait_for_timeout(300)
        check("无权限时保存被拦截", page.locator(".rp-modal").is_visible())

        # 勾一个菜单 + 一个操作后保存
        page.click('.rp-tnode[data-label="项目准入"] .rp-tnode-label')
        page.wait_for_timeout(250)
        page.locator(".rp-op-item input").first.click()
        page.wait_for_timeout(200)
        page.fill("#inpName", "测试角色A")
        page.wait_for_timeout(200)
        code_val = page.input_value("#inpCode")
        check("角色名称自动生成编码", code_val.startswith("ROLE_"), code_val)
        page.locator(".rp-modal-foot button.btn-primary").click()
        page.wait_for_timeout(500)
        check("保存后弹窗关闭", not page.locator(".rp-modal").is_visible())
        check("新角色出现在列表",
              "测试角色A" in page.locator("#rpTbody").inner_text())
        check("新角色条数变 6",
              page.locator("#rpTbody tr").count() == 6,
              f"实际 {page.locator('#rpTbody tr').count()}")

        # ---------- 5. 编辑回显 ----------
        page.locator("tr", has_text="测试角色A").locator(".rp-act-link", has_text="编辑").click()
        page.wait_for_timeout(400)
        check("编辑弹窗回显角色名",
              page.input_value("#inpName") == "测试角色A")
        check("编辑弹窗回显数据权限为「仅本人创建的数据」",
              page.locator('.rp-scope-opt[data-scope="own"]').get_attribute("class").find("on") >= 0)
        checked_ops = page.locator('.rp-op-item input[checked]').count()
        check("编辑弹窗回显已勾选的操作按钮", checked_ops >= 1, f"实际 {checked_ops}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

        # ---------- 6. 删除确认 ----------
        page.locator("tr", has_text="测试角色A").locator(".rp-act-link", has_text="删除").click()
        page.wait_for_timeout(350)
        check("删除二次确认弹窗出现", page.locator(".rp-confirm").is_visible())
        check("确认文案提到不可撤销", "不可撤销" in page.locator("#confirmText").inner_text())
        page.click("#confirmOkBtn")
        page.wait_for_timeout(400)
        check("删除后角色消失",
              "测试角色A" not in page.locator("#rpTbody").inner_text())

        # ---------- 7. 控制台错误 / 404 ----------
        real_missing = [m for m in missing if "favicon.ico" not in m]
        check("无 404 资源请求", len(real_missing) == 0, "; ".join(real_missing[:5]))
        # 资源 404 已在上面单独检查（favicon.ico 属浏览器自动请求，不算缺陷）
        real_errors = [e for e in errors
                       if "favicon" not in e.lower() and "Failed to load resource" not in e]
        check("无 JS 控制台错误", len(real_errors) == 0, "; ".join(real_errors[:3]))

        page.screenshot(path="/tmp/rp-full.png", full_page=True)
        browser.close()

    print()
    print(f"通过 {len(PASS)}/{len(PASS) + len(FAIL)}")
    if FAIL:
        print("失败项:")
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
