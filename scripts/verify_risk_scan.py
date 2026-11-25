#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业风险扫描 · 主体风险 tab 改造验证（v1.38.0）。

需求：
1. 贸易风险 + 主体风险 合并，合并后新 tab 为主体风险
2. 第一列检查分类 = 4 类：主责主业合规 / 空壳企业风险 / 资质缺失风险 / 客户产业链定位
3. 各分类的校验项按业务清单落地
4. 「校验结果」→「系统诊断结论」，其后新增「自动结论备注」列
   （低风险 / 中风险 / 高风险 / 自定义描述，自定义 ≤24 字）
5. 检查过程沿用原型现有规则，匹配不到的留空

用法: python3 scripts/verify_risk_scan.py [BASE_URL]
"""
import sys
import os
from collections import Counter

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pb_auth import add_gate_cookie, host_of  # noqa: E402

PASS, FAIL = [], []

# ===== 需求给定的 4 分类 × 校验项清单 =====
SPEC = [
    ("主责主业合规", [
        "经营范围中无贸易、供应链管理",
        "业务品类是否属于流通性强、易变现产品",
        "企业具有清晰的供应链业务方向与模式",
        "服务集团主业",
    ]),
    ("空壳企业风险", [
        "成立时间＜6 个月且拟开展单笔＞500 万大额贸易",
        "社保人数≤1 人、无工资个税记录、无水电消耗数据",
        "注册地址为虚拟/集群/托管地址、一址多企≥5 家",
        "长期零申报、非正常户、走逃失联、欠税≥3 次",
        "无实缴资本、经营范围宽泛无具体品类",
        "与该无历史业务记录且突然开展大额新增品类贸易",
    ]),
    ("资质缺失风险", [
        "拟交易商品品类不在其工商经营范围内",
        "企业是否有与本次贸易相关的资质临期或已过期",
        "与下游客户无仓库、仓储协议",
        "企业无实际经营场地或使用虚拟/托管地址",
        "特定货品无有效专项存储设备",
    ]),
    ("客户产业链定位", [
        "上下游双方是否均为贸易类型企业且过往合作项目中对手为贸易企业占比超过 80%",
        "该企业连续三个月客户变动率>50%",
    ]),
]
EXPECT_NAMES = [n for _, items in SPEC for n in items]
EXPECT_COUNT = Counter({cat: len(items) for cat, items in SPEC})


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail and not cond else ""))


def verify_page(page, label, tab_sel, panel_sel):
    """在已切到风险扫描所在 step 的页面上校验主体风险 tab。"""
    all_tabs = [t.split()[0] for t in page.locator(tab_sel).all_inner_texts()]
    # apply 页每个企业一套 tab（多套）→ 按 5 个一组切分，逐组校验
    tab_sets = [all_tabs[i:i + 5] for i in range(0, len(all_tabs), 5)]
    tabs = tab_sets[0] if tab_sets else []
    check(f"{label}：每套风险分类 tab 均为 5 个",
          all(len(t) == 5 for t in tab_sets), f"实际各套长度 {[len(t) for t in tab_sets]}")
    check(f"{label}：风险分类 tab 为 5 个", len(tabs) == 5, f"实际 {tabs}")
    check(f"{label}：第一个 tab 是「主体风险」", tabs and tabs[0] == "主体风险", f"实际 {tabs}")
    check(f"{label}：不再有「贸易风险」tab", "贸易风险" not in tabs, f"实际 {tabs}")

    panel = page.locator(panel_sel).first
    heads = panel.locator("thead th").all_inner_texts()
    check(f"{label}：表头第 5 列是「系统诊断结论」",
          len(heads) >= 5 and heads[4] == "系统诊断结论", f"实际 {heads}")
    check(f"{label}：表头第 6 列是「自动结论备注」",
          len(heads) >= 6 and heads[5] == "自动结论备注", f"实际 {heads}")
    check(f"{label}：表头前 3 列未变",
          heads[:3] == ["检查分类", "校验项", "检查规则（负面清单）"], f"实际 {heads[:3]}")

    rows = panel.locator("tbody tr")
    n = rows.count()
    check(f"{label}：主体风险共 17 项", n == 17, f"实际 {n} 项")

    cats, names, blanks = [], [], 0
    for i in range(n):
        r = rows.nth(i)
        cats.append(r.locator("td.risk-td-category").inner_text().strip())
        names.append(r.locator("td.risk-td-name").inner_text().strip())
        rule = r.locator("td.risk-td-rule").inner_text().strip()
        desc = r.locator("td.risk-td-desc").inner_text().strip()
        if not rule and not desc:
            blanks += 1
    check(f"{label}：检查分类只含 4 类", set(cats) <= set(EXPECT_COUNT), f"实际 {sorted(set(cats))}")
    check(f"{label}：4 类数量正确（4/6/5/2）",
          Counter(cats) == EXPECT_COUNT, f"实际 {dict(Counter(cats))}")
    check(f"{label}：17 项校验项与需求清单逐条一致", names == EXPECT_NAMES,
          f"实际前 3 项 {names[:3]}")
    check(f"{label}：未匹配到原型的检查过程留空（4 项）", blanks == 4, f"实际留空 {blanks} 项")
    # 检查规则列不得出现无意义的兜底占位文案
    ph = 0
    for i in range(n):
        rule = rows.nth(i).locator("td.risk-td-rule").inner_text().strip()
        if "按风险模型规则校验" in rule:
            ph += 1
    check(f"{label}：检查规则列无兜底占位文案", ph == 0, f"实际 {ph} 行含占位文案")

    # ---- 自动结论备注交互 ----
    sel = rows.first.locator(".risk-remark-select")
    check(f"{label}：每行都有「自动结论备注」控件",
          panel.locator("tbody tr td.risk-td-remark .risk-remark-select").count() == n)
    opts = [o.strip() for o in sel.locator("option").all_inner_texts()]
    check(f"{label}：备注选项为 低风险/中风险/高风险/自定义描述",
          all(o in opts for o in ["低风险", "中风险", "高风险", "自定义描述"]), f"实际 {opts}")

    sel.select_option("low")
    page.wait_for_timeout(250)
    check(f"{label}：选「低风险」后不显示自定义输入框",
          rows.first.locator(".risk-remark-input").is_hidden())

    sel.select_option("custom")
    page.wait_for_timeout(250)
    inp = rows.first.locator(".risk-remark-input")
    check(f"{label}：选「自定义描述」后出现输入框", inp.is_visible())
    check(f"{label}：自定义输入框限制 24 字",
          inp.get_attribute("maxlength") == "24", f"maxlength={inp.get_attribute('maxlength')}")
    inp.fill("一二三四五六七八九十" * 3)
    page.wait_for_timeout(250)
    val = inp.input_value()
    check(f"{label}：超长输入被截断到 24 字", len(val) == 24, f"实际 {len(val)} 字")
    count_txt = rows.first.locator(".risk-remark-count").inner_text()
    check(f"{label}：显示字数计数", "/24" in count_txt, f"实际 {count_txt!r}")

    # 备注在切换 tab 后保留
    page.locator(tab_sel).nth(1).click()
    page.wait_for_timeout(400)
    page.locator(tab_sel).nth(0).click()
    page.wait_for_timeout(500)
    sel2 = panel.locator("tbody tr").first.locator(".risk-remark-select")
    check(f"{label}：切换 tab 后备注保留", sel2.input_value() == "custom",
          f"实际 {sel2.input_value()!r}")


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1800, "height": 1100})
        add_gate_cookie(ctx, host_of(BASE))
        page = ctx.new_page()
        errs = []
        neterrs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.on("requestfailed", lambda r: neterrs.append(r.url + " → " + str(r.failure)))

        # ---------- 项目详情 ----------
        page.goto(f"{BASE}/pages/project-detail.html", wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.click('.step-label[data-step="2"]')
        page.wait_for_timeout(800)
        verify_page(page, "项目详情",
                    "#riskTabs .risk-tab", "#riskPanelSubject")

        # ---------- 项目准入 ----------
        page.goto(f"{BASE}/pages/project-apply.html", wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.locator("text=企业尽调报告").first.click()
        page.wait_for_timeout(1000)
        verify_page(page, "项目准入",
                    ".risk-tab[data-apply-risk-tab]",
                    ".apply-risk-panel[data-apply-tab='subject']")

        # ---------- 共享清单 ----------
        page.goto(f"{BASE}/pages/project-detail.html", wait_until="networkidle")
        page.wait_for_timeout(900)
        spec = page.evaluate("() => window.RISK_SCAN_SUBJECT ? "
                              "JSON.stringify(window.RISK_SCAN_SUBJECT.categories) : ''")
        check("共享清单已加载", bool(spec))

        check("无 JS 错误", not errs, "; ".join(errs[:3]))
        check("无资源加载失败", not neterrs, "; ".join(neterrs[:3]))
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
