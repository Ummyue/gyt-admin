#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""角色权限管理页 v1.23.0 端到端验证。

用法: python3 scripts/verify_role_permission.py [BASE_URL]
默认 BASE_URL = http://127.0.0.1:8899
"""

import sys
import os
from playwright.sync_api import sync_playwright
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from pb_auth import add_gate_cookie, host_of
        # 用 Playwright 自带 Chromium 而非系统 Chrome：
        # 系统 Chrome 会把 http:// 自动升级成 https://（HTTPS-First），
        # 而 192.144.175.203 没有 443 证书 → 直连 IP 报 ERR_BLOCKED_BY_CLIENT。
        # 真实用户请走正式入口 https://www.yf9.club。

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
PAGE_URL = f"{BASE}/pages/account-role-permission.html"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    mark = "✅" if cond else "❌"
    print(f"{mark} {name}" + (f"  — {detail}" if detail and not cond else ""))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1600, "height": 950})
        add_gate_cookie(ctx, host_of(BASE))
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
        check("抽屉渲染权限树节点（7 一级 + 67 子节点）",
              page.locator("#drawerBody .rp-tnode").count() == 74,
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
        check("左树渲染 74 个菜单节点（7 一级 + 67 子节点）",
              page.locator("#permTree .rp-tnode").count() == 74,
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
        # 准入管理 = 1 个一级 + 3 个二级；操作按钮 10 + 6 + 6 = 22（v1.32.0 黑名单 +2 后）
        check("勾选一级菜单联动全部下级（4 菜单 / 22 按钮）",
              "已选 4 个菜单 · 22 个操作按钮" in foot, foot)

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
        check("黑名单管理权限项收敛为 6 项（v1.24.0 4 项 + v1.32.0 增加 2 项）",
              len(bl) == 6, str(bl))
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

        # ===== 合同管理：新增/编辑页并入宿主菜单 =====
        page.click('.rp-tnode[data-label="合同管理"] .rp-tnode-label')
        page.wait_for_timeout(300)
        cm_dir = page.locator("#opBody .rp-jump-chip").all_inner_texts()
        check("合同管理 下只保留 采购合同/销售合同/补充协议",
              len(cm_dir) == 3 and "采购合同" in cm_dir[0], str(cm_dir))
        tree_labels = page.locator('#permTree .rp-tnode[data-depth="3"]').evaluate_all(
            "els => els.map(e => e.getAttribute('data-label'))")
        for gone in ["新增采购框架合同", "新增采购订单/单批次合同", "新增销售框架合同",
                     "新增销售订单/单批次合同", "新增补协-框架合同", "新增补协-订单/单批次合同"]:
            check(f"左树不再单列「{gone}」菜单节点", gone not in tree_labels, str(tree_labels))

        page.click('.rp-tnode[data-label="采购合同"] .rp-tnode-label')
        page.wait_for_timeout(300)
        cm_ops = page.locator(".rp-op-item").count()
        check("采购合同 操作权限 = 22 项（v1.32.0 user 全量替换）", cm_ops == 22, f"实际 {cm_ops}")
        codes = page.locator(".rp-op-code").all_inner_texts()
        check("采购合同 权限码改用语义 scope（create-framework 等）",
              any(c.endswith("#create-framework") for c in codes), str(codes[:3]))

        # ===== 回款管理 / 保证金管理：详情/编辑页并入列表页 =====
        page.click('.rp-tnode[data-label="回款管理"] .rp-tnode-label')
        page.wait_for_timeout(300)
        rc_dir = page.locator("#opBody .rp-jump-chip").all_inner_texts()
        check("回款管理 下只保留 回款列表",
              len(rc_dir) == 1 and "回款列表" in rc_dir[0], str(rc_dir))

        page.click('.rp-tnode[data-label="回款列表"] .rp-tnode-label')
        page.wait_for_timeout(300)
        rc_ops = page.locator(".rp-op-item").count()
        check("回款列表 操作权限 = 列表 5 + 审批详情 3 + 编辑回款 5 = 13 项",
              rc_ops == 13, f"实际 {rc_ops}")
        tip = page.locator(".rp-merged-tip").inner_text()
        check("回款列表 提示条列出已并入的子页面",
              "回款详情" in tip and "回款审批详情" in tip and "编辑回款" in tip, tip)
        check("并入页面的操作项数在提示条里标明",
              "3 项操作权限" in tip and "5 项操作权限" in tip, tip)
        check("并入页操作数已归入本菜单时提示「已并入本菜单的配置项」",
              "相关操作已并入本菜单的配置项" in tip, tip)

        page.click('.rp-tnode[data-label="保证金管理"] .rp-tnode-label')
        page.wait_for_timeout(300)
        mc_dir = page.locator("#opBody .rp-jump-chip").all_inner_texts()
        check("保证金管理 下只保留 保证金明细",
              len(mc_dir) == 1 and "保证金明细" in mc_dir[0], str(mc_dir))

        page.click('.rp-tnode[data-label="保证金明细"] .rp-tnode-label')
        page.wait_for_timeout(300)
        mc_ops = page.locator(".rp-op-item").count()
        check("保证金明细 操作权限 = 明细 3 + 调整 3 + 调整记录 4 = 10 项",
              mc_ops == 10, f"实际 {mc_ops}")
        mt = page.locator(".rp-merged-tip").inner_text()
        check("保证金明细 提示条列出已并入的子页面",
              "保证金调整" in mt and "保证金调整记录" in mt, mt)

        tree_labels2 = page.locator('#permTree .rp-tnode').evaluate_all(
            "els => els.map(e => e.getAttribute('data-label'))")
        for gone in ["回款详情", "回款审批详情", "编辑回款", "保证金调整", "保证金调整记录"]:
            check(f"左树不再单列「{gone}」菜单节点", gone not in tree_labels2, str(tree_labels2))

        # ===== 审批管理：编排画布并入审批流程配置 =====
        page.click('.rp-tnode[data-label="审批管理"] .rp-tnode-label')
        page.wait_for_timeout(300)
        ap_dir = page.locator("#opBody .rp-jump-chip").all_inner_texts()
        check("审批管理 下只保留 审批流程配置 / 审批流程监控",
              len(ap_dir) == 2 and "审批流程配置" in ap_dir[0] and "审批流程监控" in ap_dir[1],
              str(ap_dir))
        page.click('.rp-tnode[data-label="审批流程配置"] .rp-tnode-label')
        page.wait_for_timeout(300)
        ap_ops = page.locator(".rp-op-item").count()
        check("审批流程配置 操作权限 = 配置页 2 + 编排画布 5 = 7 项",
              ap_ops == 7, f"实际 {ap_ops}")
        at = page.locator(".rp-merged-tip").inner_text()
        check("审批流程配置 提示条列出已并入的流程编排画布（5 项）",
              "流程编排画布" in at and "5 项操作权限" in at, at)
        tree_labels3 = page.locator('#permTree .rp-tnode').evaluate_all(
            "els => els.map(e => e.getAttribute('data-label'))")
        check("左树不再单列「流程编排画布」菜单节点",
              "流程编排画布" not in tree_labels3, str(tree_labels3))

        # ===== v1.32.0 权限配置项调整（9 项）=====
        def ops_of(label):
            page.click('.rp-tnode[data-label="%s"] .rp-tnode-label' % label)
            page.wait_for_timeout(220)
            return page.locator(".rp-op-label").all_inner_texts()

        # 1) 黑名单管理：+ 修改 / 移入-解除
        bl = ops_of("黑名单管理")
        check("黑名单管理 6 项且含 修改 / 移入-解除",
              len(bl) == 6 and "修改" in bl and "移入/解除" in bl, str(bl))
        # 2) 采购合同 / 销售合同：全量替换为 22 项
        expect_contract = [
            "新增框架合同", "新增单批次或订单合同", "数据导出（框架合同）", "数据导出（单批次或订单合同）",
            "合同详情（框架合同）", "合同详情（单批次或订单合同）",
            "新增补充协议（框架合同）", "新增补充协议（单批次或订单合同）",
            "发起合同完结（框架合同）", "发起合同完结（单批次或订单合同）",
            "合同修改（框架合同）", "合同修改（单批次或订单合同）",
            "合同作废（框架合同）", "合同作废（单批次或订单合同）",
            "撤回审批（框架合同）", "撤回审批（单批次或订单合同）",
            "上传双签合同（框架合同）", "上传双签合同（单批次或订单合同）",
            "关联合同（订单或单批次）", "开票申请（单批次或订单合同）",
            "发起结算（单批次或订单合同）", "开具货转（单批次或订单合同）",
        ]
        for node_label in ("采购合同", "销售合同"):
            got = ops_of(node_label)
            check(f"{node_label} 权限项全量替换为 22 项", got == expect_contract, str(got))
        # 3) 补充协议：全量替换为 12 项
        expect_supp = [
            "新增补充协议（框架合同补充协议）", "新增补充协议（订单或单批次合同补充协议）",
            "补协详情（框架合同补充协议）", "补协详情（订单或单批次合同补充协议）",
            "修改补协（框架合同补充协议）", "修改补协（订单或单批次合同补充协议）",
            "上传双签协议（框架合同补充协议）", "上传双签协议（订单或单批次合同补充协议）",
            "作废补协（框架合同补充协议）", "作废补协（订单或单批次合同补充协议）",
            "数据导出（框架合同补充协议）", "数据导出（订单或单批次合同补充协议）",
        ]
        got = ops_of("补充协议")
        check("补充协议 权限项全量替换为 12 项", got == expect_supp, str(got))
        # 4) 业务线管理：+ 解除业务线 / 申请业务完结 / 一键下载附件 / 监控查看
        got = ops_of("业务线管理")
        check("业务线管理 5 项且含 4 个新增项",
              len(got) == 5 and "解除业务线" in got and "申请业务完结" in got
              and "一键下载附件" in got and "监控查看" in got, str(got))
        # 5)(6) 发货管理：删 登记订单发货数据 / 删除 / 确认删除
        got = ops_of("发货管理")
        check("发货管理 7 项，已去掉 登记订单发货数据 / 删除 / 确认删除",
              len(got) == 7 and "登记订单发货数据" not in got
              and "删除" not in got and "确认删除" not in got, str(got))
        check("发货管理 保留 登记采购/销售订单发运数据",
              "登记采购订单发运数据" in got and "登记销售订单发运数据" in got, str(got))
        # 6b) 收货管理：去掉 删除 / 确认删除
        got = ops_of("收货管理")
        check("收货管理 4 项，已去掉 删除 / 确认删除",
              len(got) == 4 and "删除" not in got and "确认删除" not in got, str(got))
        # 7) 货转管理：删 5 项 + 新增 上传货权转让协议
        got = ops_of("货转管理")
        check("货转管理 7 项，新增 上传货权转让协议",
              len(got) == 7 and "上传货权转让协议" in got, str(got))
        for gone in ("开具货转", "批量下载", "+ 上传", "确认上传", "下载"):
            check(f"货转管理 已去掉「{gone}」", gone not in got, str(got))
        check("货转管理 保留 上传上游货转 / 上传已生效单据",
              "↑ 上传上游货转" in got and "上传已生效单据" in got, str(got))
        # 8) 付款管理 / 9) 退款管理：+ 修改 / 作废 / 撤回审批
        got = ops_of("付款管理")
        check("付款管理 6 项且含 修改 / 作废 / 撤回审批",
              len(got) == 6 and "修改" in got and "作废" in got and "撤回审批" in got, str(got))
        got = ops_of("退款管理")
        check("退款管理 5 项且含 修改 / 作废 / 撤回审批",
              len(got) == 5 and "修改" in got and "作废" in got and "撤回审批" in got, str(got))

        # ===== 预警中心改名 + 账户中心按真实系统结构重建 =====
        warn = page.locator('#permTree .rp-tnode[data-depth="1"]').evaluate_all(
            "els => els.map(e => e.getAttribute('data-label'))")
        check("预警中心 二级改为 预警查询 / 预警设置",
              "预警查询" in warn and "预警设置" in warn and "预警管理" not in warn, str(warn))
        check("旧名 预警规则配置 已不再出现", "预警规则配置" not in warn, str(warn))

        acct = page.locator('#permTree .rp-tnode[data-label="账户中心"]').count()
        check("账户中心 一级节点存在", acct == 1)
        pmg = page.locator('#permTree .rp-tnode[data-label="个人管理"]').count()
        emg = page.locator('#permTree .rp-tnode[data-label="企业管理"]').count()
        check("账户中心 下有 个人管理 / 企业管理 两个二级", pmg == 1 and emg == 1)
        for leaf in ["个人信息", "安全设置", "我的企业", "企业账号管理",
                     "企业资料管理", "密码管理", "角色权限管理"]:
            n = page.locator('#permTree .rp-tnode[data-label="%s"]' % leaf).count()
            check(f"账户中心 下有「{leaf}」节点", n == 1, f"实际 {n}")

        # 右侧操作项同步构建
        page.click('.rp-tnode[data-label="企业账号管理"] .rp-tnode-label')
        page.wait_for_timeout(300)
        ea = page.locator(".rp-op-label").all_inner_texts()
        check("企业账号管理 操作权限 10 项",
              len(ea) == 10, str(ea))
        for keep in ["新增账号", "编辑账号", "删除账号", "重置密码", "分配角色",
                     "审核入职申请", "审批邀请", "导出账号列表"]:
            check(f"企业账号管理 含「{keep}」权限项", keep in ea, str(ea))

        page.click('.rp-tnode[data-label="安全设置"] .rp-tnode-label')
        page.wait_for_timeout(300)
        ss = page.locator(".rp-op-label").all_inner_texts()
        check("安全设置 操作权限 5 项", len(ss) == 5, str(ss))

        page.click('.rp-tnode[data-label="角色权限管理"] .rp-tnode-label')
        page.wait_for_timeout(300)
        rp = page.locator(".rp-op-label").all_inner_texts()
        check("角色权限管理 操作权限 4 项", len(rp) == 4, str(rp))
        rp_codes = page.locator(".rp-op-code").all_inner_texts()
        check("角色权限管理「确认删除」权限码为 delete",
              any(c.endswith("#delete") for c in rp_codes), str(rp_codes))

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
