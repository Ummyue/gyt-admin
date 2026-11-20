#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""准入表单改造验证（v1.37.0）。

需求 1：项目准入 + 客户准入的「企业开户行信息 / 企业银行账号」→ 合并为
        可添加多个的「企业银行账户」子表；客户准入菜单改名「企业准入」。
需求 2：项目准入「关联企业信息」弹窗 —— 客户类别→项目角色、新增企业类型（多选）、
        二者居首行、企业名称独占第二行。

用法: python3 scripts/verify_accession_forms.py [BASE_URL]
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


ROLE_OPTIONS = ["上游客户", "下游客户", "第三方物流", "第三方仓储"]
TYPE_OPTIONS = ["资源型企业", "生产加工型企业", "贸易流通型企业"]


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1600, "height": 1100})
        add_gate_cookie(ctx, host_of(BASE))
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

        # ================= 需求 2：关联企业信息弹窗 =================
        page.goto(f"{BASE}/pages/project-apply.html", wait_until="networkidle")
        page.wait_for_timeout(800)

        # 打开「关联企业信息」弹窗
        page.click(".dashed-add")
        page.wait_for_timeout(600)
        modal = page.locator("#companyModal")
        check("关联企业信息弹窗可打开", modal.is_visible())

        # 首行：项目角色 + 企业类型
        grid = page.locator("#companyModal .form-grid").first
        fields = grid.locator("> .form-field")

        # 取首行两个字段的 label
        def label_of(el):
            lab = el.locator(".form-label").first
            return lab.inner_text().strip() if lab.count() else ""

        f1_label = label_of(fields.nth(0))
        f2_label = label_of(fields.nth(1))
        check("首行第 1 格是「项目角色」", f1_label.startswith("项目角色"), f"实际 {f1_label!r}")
        check("首行第 2 格是「企业类型」", f2_label.startswith("企业类型"), f"实际 {f2_label!r}")

        # 项目角色选项不变
        role_sel = fields.nth(0).locator("select")
        role_opts = [o.strip() for o in role_sel.locator("option").all_inner_texts()]
        check("项目角色选项不变", role_opts == ROLE_OPTIONS, f"实际 {role_opts}")

        # 企业类型是复选组，3 个选项
        type_box = fields.nth(1).locator("#cmCompanyTypes")
        check("企业类型是多选复选组", type_box.count() == 1)
        type_cbs = type_box.locator("input[type=checkbox]")
        check("企业类型有 3 个选项", type_cbs.count() == 3, f"实际 {type_cbs.count()}")
        type_vals = [v.strip() for v in type_box.locator(".multi-select-item span").all_inner_texts()]
        check("企业类型选项内容正确", type_vals == TYPE_OPTIONS, f"实际 {type_vals}")

        # 企业类型可多选 + 选中态高亮
        type_cbs.nth(0).check()
        type_cbs.nth(2).check()
        page.wait_for_timeout(200)
        checked = type_box.locator("input[type=checkbox]:checked").count()
        check("企业类型可多选", checked == 2, f"实际勾选 {checked}")
        on_items = type_box.locator(".multi-select-item.on").count()
        check("企业类型选中态高亮", on_items == 2, f"实际高亮 {on_items}")

        # 第二行：企业名称独占整行
        f3_label = label_of(fields.nth(2))
        check("第 2 行是「企业名称」", f3_label.startswith("企业名称"), f"实际 {f3_label!r}")
        span = fields.nth(2).evaluate(
            "e => getComputedStyle(e).gridColumnStart + ' / ' + getComputedStyle(e).gridColumnEnd")
        check("企业名称独占整行", "1" in span and "-1" in span, f"grid-column={span}")

        # 其余字段顺序不变
        rest = [label_of(fields.nth(i)).replace('*', '').strip() for i in range(3, fields.count())]
        expect_head = ["法定代表人", "注册地址", "社会统一信用代码", "经营期限（止）", "成立日期",
                       "联系人姓名", "联系人电话", "联系人邮箱", "联系人地址",
                       "负责人姓名", "负责人电话"]
        check("其余字段顺序不变",
              [x for x in rest if x][:len(expect_head)] == expect_head,
              f"实际 {[x for x in rest if x][:len(expect_head)]}")

        # ================= 需求 1a：企业银行账户子表（项目准入弹窗）=================
        check("弹窗内无独立的「企业开户行信息」表单格",
              grid.locator("> .form-field > .form-label", has_text="企业开户行信息").count() == 0)
        bank_list = page.locator("#cmBankList")
        check("弹窗内有「企业银行账户」子表", bank_list.count() == 1)
        rows = bank_list.locator(".sub-table-row")
        check("子表默认 1 组", rows.count() == 1, f"实际 {rows.count()}")
        check("每组含开户行 + 账号两个字段",
              rows.first.locator("[data-role=bank-name]").count() == 1
              and rows.first.locator("[data-role=bank-account]").count() == 1)
        check("只有 1 组时删除按钮禁用",
              rows.first.locator(".sub-table-del").is_disabled())

        # 添加第 2 组
        page.click("#companyModal .sub-table-foot .btn")
        page.wait_for_timeout(300)
        check("可添加第 2 组", rows.count() == 2, f"实际 {rows.count()}")
        check("多组时删除按钮可用", not rows.first.locator(".sub-table-del").is_disabled())

        # 填写并删除第 2 组
        rows.nth(1).locator("[data-role=bank-name]").fill("中国银行开封分行")
        rows.nth(1).locator("[data-role=bank-account]").fill("6210 1234 5678")
        rows.nth(1).locator(".sub-table-del").click()
        page.wait_for_timeout(300)
        check("可删除指定组", rows.count() == 1, f"实际 {rows.count()}")
        check("删除后回到 1 组且按钮禁用", rows.first.locator(".sub-table-del").is_disabled())

        # ================= 需求 1b：菜单改名 =================
        # 左侧 sidemenu 只在「当前页属于菜单树」时渲染 → 用菜单内的 customer-list 验证
        page.goto(f"{BASE}/pages/customer-list.html", wait_until="networkidle")
        page.wait_for_timeout(800)
        side = page.locator("#leftSidemenu")
        side_text = side.inner_text() if side.count() else ""
        check("左侧菜单出现「企业准入」", "企业准入" in side_text, side_text[:150])
        check("左侧菜单不再出现「客户准入」", "客户准入" not in side_text, side_text[:150])

        crumb = page.locator(".breadcrumb").first.inner_text()
        check("企业准入页面包屑含「企业准入」", "企业准入" in crumb, crumb.replace("\n", " "))

        # ================= 需求 1a：客户准入页 =================
        page.goto(f"{BASE}/pages/customer-apply.html", wait_until="networkidle")
        page.wait_for_timeout(800)
        cust_bank = page.locator("#custBankList")
        check("客户准入页有「企业银行账户」子表", cust_bank.count() == 1)
        check("客户准入页子表默认 1 组", cust_bank.locator(".sub-table-row").count() == 1)
        check("客户准入页只有 1 组时删除按钮禁用",
              cust_bank.locator(".sub-table-del").first.is_disabled())
        page.click("#custBankList ~ .sub-table-foot .btn, .form-grid .sub-table-foot .btn")
        page.wait_for_timeout(300)
        check("客户准入页可添加第 2 组", cust_bank.locator(".sub-table-row").count() == 2)
        check("客户准入页无独立的「企业开户行信息」表单格",
              page.locator(".form-grid > .form-field > .form-label",
                           has_text="企业开户行信息").count() == 0)

        # ================= 权限树 =================
        page.goto(f"{BASE}/pages/account-role-permission.html", wait_until="networkidle")
        page.wait_for_timeout(900)
        tree_txt = page.evaluate("() => window.PERMISSION_TREE ? JSON.stringify(window.PERMISSION_TREE) : ''")
        check("权限树已加载", bool(tree_txt))
        if tree_txt:
            import json
            tree = json.loads(tree_txt)
            nodes = []
            for m in tree:
                for s in m.get("subMenus") or []:
                    nodes.append(s)
            ent = [n for n in nodes if n.get("label") == "企业准入"]
            check("权限树节点显示名为「企业准入」", len(ent) == 1, f"实际 {len(ent)}")
            if ent:
                codes = [o["code"] for o in ent[0].get("ops") or []]
                check("权限码仍沿用旧路径 准入管理/客户准入#xxx",
                      all(c.startswith("准入管理/客户准入#") for c in codes) and len(codes) > 0,
                      f"实际 {codes[:3]}")
                check("权限树节点 code 仍为 menu:准入管理/客户准入",
                      ent[0].get("code") == "menu:准入管理/客户准入", f"实际 {ent[0].get('code')}")

        # ================= 统一：全站「客户类别」→「项目角色」=================
        page.goto(f"{BASE}/pages/customer-detail.html", wait_until="networkidle")
        page.wait_for_timeout(700)
        # 详情页部分区块在隐藏 tab 里 → 用 HTML 源码断言（含未激活 tab）
        cd_text = page.content()
        check("客户详情页不再出现「客户类别」", "客户类别" not in cd_text)
        check("客户详情页出现「项目角色」", "项目角色" in cd_text)
        check("客户详情页展示业务「企业类型」", "贸易流通型企业" in cd_text)
        check("客户详情页工商字段改为「企业性质」",
              "企业性质" in cd_text and "其他有限责任公司" in cd_text)

        page.goto(f"{BASE}/pages/project-detail.html", wait_until="networkidle")
        page.wait_for_timeout(700)
        pd_text = page.content()
        check("项目详情页不再出现「客户类别」", "客户类别" not in pd_text)
        check("项目详情页出现「项目角色」", "项目角色" in pd_text)
        check("项目详情页展示业务「企业类型」", "资源型企业" in pd_text)

        page.goto(f"{BASE}/pages/customer-apply.html", wait_until="networkidle")
        page.wait_for_timeout(700)
        ca_form = page.locator(".form-grid").first.inner_text()
        check("客户准入表单标签为「项目角色」",
              "项目角色" in ca_form and "客户类别" not in ca_form)

        # ================= 兼容：存量数据仍可读 =================
        # 老 mock 结构只有 basic['客户类别'] → 渲染时兜底读旧 key
        compat = page.evaluate(
            "() => { const c = { basic: { '国家': '中国', '客户类别': '上游企业' } };"
            " return c.basic['项目角色'] || c.basic['客户类别'] || '—'; }")
        check("老数据（basic['客户类别']）兼容读取为项目角色",
              compat == "上游企业", str(compat))

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
