#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业风险扫描 · 主体风险 tab 改造验证（v1.38.0）。

需求：
1. 贸易风险 + 主体风险 合并，合并后新 tab 为主体风险
2. 第一列检查分类 = 4 类：主责主业合规 / 空壳企业风险 / 资质缺失风险 / 客户产业链定位
3. 各分类的校验项按业务清单落地
4. 「校验结果」→「系统诊断结论」，其后新增「备注」列
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
        "该企业为贸易类型企业，且我司目前合作客户中，贸易类企业占比超过80%",
    ]),
]
EXPECT_NAMES = [n for _, items in SPEC for n in items]
EXPECT_COUNT = Counter({cat: len(items) for cat, items in SPEC})


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail and not cond else ""))


def verify_page(page, label, tab_sel, panel_sel, warn_expr=None):
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
    check(f"{label}：表头第 6 列是「备注」",
          len(heads) >= 6 and heads[5] == "备注", f"实际 {heads}")
    check(f"{label}：表头前 3 列 = 检查分类 / 风险逻辑（对应合规要求）/ 校验项",
          heads[:3] == ["检查分类", "风险逻辑（对应合规要求）", "校验项"], f"实际 {heads[:3]}")

    rows = panel.locator("tbody tr")
    n = rows.count()
    check(f"{label}：主体风险共 16 项", n == 16, f"实际 {n} 项")

    # ===== v1.38.7 助手：按 rowspan 语义还原每行的列文本 =====
    # 合并单元格覆盖的行**没有**该 td → 逐行 locator 会超时；
    # 在 JS 侧一次性算好并按 rowspan 继承
    ROW_TEXTS = panel.evaluate(
        "(el) => {"
        "   const rows = [...el.querySelectorAll('tbody tr')];"
        "   function pick(cls) {"
        "   const out = []; let carry = null, remain = 0;"
        "   rows.forEach(r => {"
        "     const td = r.querySelector('td.' + cls);"
        "     if (td) { const txt = (td.textContent || '').trim().replace(/\\s+/g, ' ');"
        "              if (txt) { carry = txt; remain = parseInt(td.getAttribute('rowspan') || '1', 10) - 1; } }"
        "     else if (remain > 0) { remain--; }"
        "     else { carry = null; }"
        "     out.push(carry); });"
        "   return out; }"
        " return { cat: pick('risk-td-category'), rule: pick('risk-td-rule'), name: pick('risk-td-name') };"
        " }")

    # v1.38.8：内容合并 → 分类/风险逻辑只在组首行有内容，ROW_TEXTS 已按「空值继承」还原
    cats = list(ROW_TEXTS['cat'])
    names = list(ROW_TEXTS['name'])
    blanks = 0
    for i in range(n):
        r = rows.nth(i)
        desc = r.locator("td.risk-td-desc").inner_text().strip()
        if not desc:
            blanks += 1
        rule = ROW_TEXTS['rule'][i] or ''
        desc = r.locator("td.risk-td-desc").inner_text().strip()
        if not rule and not desc:
            blanks += 1
    check(f"{label}：检查分类只含 4 类", set(cats) <= set(EXPECT_COUNT), f"实际 {sorted(set(cats))}")
    check(f"{label}：4 类数量正确（4/6/5/2）",
          Counter(cats) == EXPECT_COUNT, f"实际 {dict(Counter(cats))}")
    # ---- v1.38.9：rowspan 合并（内容垂直居中）+ 合并区域内横线补绘 ----
    spans = panel.evaluate(
        "(el) => [...el.querySelectorAll('tbody td.risk-td-cat-merged')]"
        ".map(t => t.getAttribute('rowspan')).join(',')")
    check(f"{label}：分类列使用 rowspan 合并（内容跨行）", spans != "", f"实际 {spans!r}")
    if label == "项目详情":
        check(f"{label}：主体风险分类合并 rowspan=4/6/5/1", spans == "4,6,5,1", f"实际 {spans}")
    # 内容垂直居中
    valign = panel.evaluate(
        "(el) => { const t = el.querySelector('tbody td.risk-td-cat-merged');"
        " return t ? getComputedStyle(t).verticalAlign : ''; }")
    check(f"{label}：合并单元格内容垂直居中", valign == "middle", f"实际 {valign!r}")
    # 合并区域内部补画的横线数量 = rowspan - 1
    sep_info = panel.evaluate(
        "(el) => [...el.querySelectorAll('tbody td[data-rspan]')]"
        ".map(t => (t.getAttribute('rowspan') || '1') + ':' + t.querySelectorAll('.merged-row-sep').length).join(',')")
    bad = [x for x in sep_info.split(',') if x and x.split(':')[0] != str(int(x.split(':')[1]) + 1)]
    check(f"{label}：合并区域内横线已补回（数量=rowspan-1）", not bad,
          f"实际 {sep_info} / 不符 {bad}")

    # ---- v1.38.6：风险逻辑（对应合规要求）按检查分类给固定合规要求 ----
    LOGIC = {
        "主责主业合规": "违反「不准开展背离主业的贸易业务」，非主业贸易无审批，易形成无效资产",
        "空壳企业风险": "违反「不准与无实际经营能力的企业交易」，空壳企业易引发虚开发票、资金流失",
        "资质缺失风险": "违反「不准开展需特许资质但无资质的贸易」，无证经营易触发行政追责；"
                        "或违反「不准开展对交易标的没有控制权的空转、走单等贸易业务」，不具备资质的仓储企业无法保障货权清晰",
        "客户产业链定位": "违反「不准开展无商业实质的循环贸易」，交易对手生产型企业占比较低或变动频繁，"
                          "难以核实贸易背景，无法确定货物流转是否创造价值",
    }
    logic_by_cat = {}
    for i in range(n):
        r = rows.nth(i)
        ct = r.locator("td.risk-td-category")
        cat = ct.first.inner_text().strip() if ct.count() else (cats[i] if i < len(cats) else "")
        logic = ROW_TEXTS['rule'][i] or ''
        logic_by_cat.setdefault(cat, logic)
    for cat, expect in LOGIC.items():
        check(f"{label}：{cat} 的风险逻辑为对应合规要求",
              logic_by_cat.get(cat, "") == expect, f"实际 {logic_by_cat.get(cat)!r}")
    # 列顺序：风险逻辑必须在校验项之前
    order = panel.evaluate("(el) => { const r = el.querySelector('tbody tr');"
                    " if (!r) return '';"
                    " return [...r.children].map(c => { const m = c.className.match(/risk-td-([a-z]+)/);"
                    " return m ? m[1] : '?'; }).join(','); }")
    check(f"{label}：列顺序为 检查分类 │ 风险逻辑 │ 校验项 │ 检查过程 │ 系统诊断结论 │ 备注",
          order.startswith("category,rule,name,desc,result,remark"), f"实际 {order}")

    check(f"{label}：17 项校验项与需求清单逐条一致", names == EXPECT_NAMES,
          f"实际前 3 项 {names[:3]}")
    # v1.38.6：风险逻辑列改为按分类给固定合规要求（不再随匹配留空）
    # → 只有「检查过程」列对未匹配项留空
    desc_blanks = 0
    for i in range(n):
        d = rows.nth(i).locator("td.risk-td-desc").inner_text().strip()
        if not d:
            desc_blanks += 1
    check(f"{label}：未匹配到原型的检查过程留空（4 项）", desc_blanks == 4, f"实际留空 {desc_blanks} 项")
    # 检查规则列不得出现无意义的兜底占位文案
    ph = 0
    for i in range(n):
        rule = ROW_TEXTS['rule'][i] or ''
        if "按风险模型规则校验" in rule:
            ph += 1
    check(f"{label}：检查规则列无兜底占位文案", ph == 0, f"实际 {ph} 行含占位文案")

    # ---- v1.38.1：相同「检查分类」合并单元格 ----
    cat_tds = panel.locator("tbody td.risk-td-category")
    # v1.38.8 内容合并：同一分类只有组首行显示内容，其余行该单元格为空
    filled = sum(1 for t in cat_tds.all() if t.inner_text().strip())
    check(f"{label}：同一检查分类内容合并（只有组首行有内容）",
          filled == len(EXPECT_COUNT), f"实际有内容 {filled} 个 / 共 {cat_tds.count()} 格")
    firsts = panel.evaluate("(el) => [...el.querySelectorAll('tbody td.risk-td-cat-merged')]"
                            ".map(t => t.textContent.trim())")
    check(f"{label}：4 个分类各有 1 个合并格",
          firsts == [c for c, _ in SPEC], f"实际 {firsts}")
    # v1.38.9：rowspan 合并 → 分类名只出现在合并格（4 个）
    filled_cats = [t.inner_text().strip() for t in cat_tds.all() if t.inner_text().strip()]
    check(f"{label}：合并内容为 4 个分类名",
          filled_cats == [c for c, _ in SPEC], f"实际 {filled_cats}")

    # ---- v1.38.3：合并格之间的横向分隔线必须**看得见** ----
    # 坑：合并格背景曾与行分隔线同色(#F1F5F9) → 线画了但隐形，第一列像一整块
    m1 = panel.locator('tbody td.risk-td-category').first
    line_vis = m1.evaluate("e => { const c = getComputedStyle(e);"
                            ' return { w: c.borderBottomWidth, c: c.borderBottomColor, bg: c.backgroundColor }; }')
    check(f"{label}：分类列分组线可见（与背景不同色且有宽度）",
          line_vis['w'] != '0px' and line_vis['c'] != line_vis['bg'],
          f"实际 {line_vis}")
    sep2 = panel.evaluate("(el) => { const rows = [...el.querySelectorAll('tbody tr')];"
                " return rows.slice(0, -1).map(r => r.querySelector('td.risk-td-cat-merged'))"
                " .filter(Boolean).map(t => getComputedStyle(t).borderBottomWidth).join(','); }")
    check(f"{label}：分类合并格都有底边线（末行除外）",
          all(v == '1px' for v in sep2.split(',') if v), f"实际 {sep2}")

    # ---- v1.38.4：所有列块之间都要有竖向分隔线 ----
    # 用户标注：校验项↔检查规则、检查规则↔检查过程 两处缺线
    # ⚠️ 判定要按「列边界」而不是「本列两侧」：线可能画在左列的 border-right，
    #    也可能画在右列的 border-left（separate 模式下不合并，只画一侧）
    edges = panel.evaluate("""(el) => {
      const cols = ['category', 'name', 'rule', 'desc', 'result', 'remark'];
      const w = c => {
        const td = el.querySelector('tbody td.risk-td-' + c);
        const th = el.querySelector('thead th.risk-th-' + c);
        if (!td) return null;
        const c1 = getComputedStyle(td), c2 = th ? getComputedStyle(th) : null;
        return {
          right: [c1.borderRightWidth, c2 ? c2.borderRightWidth : '0px'],
          left:  [c1.borderLeftWidth,  c2 ? c2.borderLeftWidth  : '0px'],
        };
      };
      const data = {};
      cols.forEach(c => { data[c] = w(c); });
      // 每个边界（i 与 i+1 之间）是否有线
      const edges = [];
      for (let i = 0; i < cols.length - 1; i++) {
        const L = data[cols[i]], R = data[cols[i + 1]];
        const ok = (L && L.right.some(v => v === '1px')) || (R && R.left.some(v => v === '1px'));
        edges.push({ between: cols[i] + ' | ' + cols[i + 1], ok: !!ok,
                     leftRight: L ? L.right.join('/') : '-',
                     rightLeft: R ? R.left.join('/') : '-' });
      }
      return edges;
    }""")
    for e in edges:
        check(f"{label}：{e['between']} 之间有竖向分隔线", e["ok"],
              f"左列 border-right={e['leftRight']} 右列 border-left={e['rightLeft']}")

    # ---- v1.38.3：两模块的控件不能挤在一起 ----
    # v1.38.5：诊断结论已改为只读标签 → 间距度量对象改为「诊断结论标签 → 备注下拉」
    gap = panel.evaluate("(el) => {"
                    " const t = el.querySelector('td.risk-td-result .risk-result-tag');"
                    " const m = el.querySelector('td.risk-td-remark select');"
                    " if (!t || !m) return -1;"
                    " return Math.round(m.getBoundingClientRect().left - t.getBoundingClientRect().right);"
                    "}")
    check(f"{label}：两模块控件间距 ≥ 30px（箭头不粘连）", gap >= 30, f"实际 {gap}px")
    clipped = panel.evaluate("(el) => {"
                    " const t = el.querySelector('td.risk-td-result .risk-result-tag');"
                    " if (!t) return true;"
                    " return t.scrollWidth > t.clientWidth + 1;"
                    "}")
    check(f"{label}：系统诊断结论文案未被截断", not clipped)

    # ---- v1.38.2：列线框 + 两模块视觉区分 ----
    merged = panel.locator("tbody td.risk-td-category").first
    bl = merged.evaluate("e => getComputedStyle(e).borderLeftWidth + '/' + getComputedStyle(e).borderRightWidth")
    check(f"{label}：分类列左右有线框", bl == "1px/1px", f"实际 {bl}")
    div_color = merged.evaluate("e => getComputedStyle(e).borderRightColor")
    check(f"{label}：列分隔线为加深色（#CBD5E1）",
          div_color == "rgb(203, 213, 225)", f"实际 {div_color}")
    th_res = panel.locator("thead th.risk-th-result").first
    th_rem = panel.locator("thead th.risk-th-remark").first
    sep = th_rem.evaluate("e => getComputedStyle(e).borderLeftWidth")
    check(f"{label}：备注列与系统诊断结论列之间有竖向分隔", sep == "1px", f"实际 {sep}")
    bg1 = th_res.evaluate("e => getComputedStyle(e).backgroundColor")
    bg2 = th_rem.evaluate("e => getComputedStyle(e).backgroundColor")
    check(f"{label}：备注列表头底色与系统诊断结论列不同", bg1 != bg2, f"{bg1} vs {bg2}")

    # ---- 备注交互 ----
    sel = rows.first.locator(".risk-remark-select")
    check(f"{label}：每行都有「备注」控件",
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

    # ---- v1.38.1：排序后「系统诊断结论」写回与备注不错位 ----
    # 给第 5 行（空壳企业风险组内）打备注，再切走切回，确认仍落在同一行
    r5 = panel.locator("tbody tr").nth(5)
    r5.locator(".risk-remark-select").select_option("high")
    page.wait_for_timeout(300)
    page.locator(tab_sel).nth(1).click()
    page.wait_for_timeout(400)
    page.locator(tab_sel).nth(0).click()
    page.wait_for_timeout(500)
    v5 = panel.locator("tbody tr").nth(5).locator(".risk-remark-select").input_value()
    check(f"{label}：排序后备注不错位（仍在第 5 行）", v5 == "high", f"实际 {v5!r}")

    # v1.38.5：系统诊断结论 → 只读标签，不可手工修改
    n_sel = panel.locator("tbody td.risk-td-result select").count()
    check(f"{label}：系统诊断结论不再是可编辑下拉框", n_sel == 0, f"实际 {n_sel} 个 select")
    n_tag = panel.locator("tbody td.risk-td-result .risk-result-tag").count()
    n_rows = panel.locator("tbody tr").count()
    check(f"{label}：每行都有只读诊断结论标签", n_tag == n_rows, f"标签 {n_tag} / 行 {n_rows}")
    # 标签文本应为「✓ 无风险」或「⚠ 存在风险」，且无 onchange
    tag_info = panel.evaluate("""(el) => {
      const tags = [...el.querySelectorAll('tbody td.risk-td-result .risk-result-tag')];
      return {
        texts: [...new Set(tags.map(t => t.textContent.trim()))],
        withHandler: tags.filter(t => t.getAttribute('onchange') || t.onchange).length,
        cursor: tags.length ? getComputedStyle(tags[0]).cursor : '-',
      };
    }""")
    check(f"{label}：诊断结论文案正确",
          set(tag_info["texts"]) <= {"✓ 无风险", "⚠ 存在风险"}, f"实际 {tag_info['texts']}")
    check(f"{label}：诊断结论无修改事件", tag_info["withHandler"] == 0)
    check(f"{label}：诊断结论呈只读样式（cursor:default）",
          tag_info["cursor"] == "default", f"实际 {tag_info['cursor']}")
    # 备注列仍可编辑
    check(f"{label}：备注列仍可编辑",
          panel.locator("tbody td.risk-td-remark .risk-remark-select").count() == n_rows)


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
                    "#riskTabs .risk-tab", "#riskPanelSubject",
                    warn_expr="() => { const c = (window.COMPANIES||{})[window.currentCompanyId];"
                              " return c && c.internal ? c.internal.items.filter(x => x.status === 'warn').length : -1; }")

        # ---------- 项目准入 ----------
        page.goto(f"{BASE}/pages/project-apply.html", wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.locator("text=企业尽调报告").first.click()
        page.wait_for_timeout(1000)
        verify_page(page, "项目准入",
                    ".risk-tab[data-apply-risk-tab]",
                    ".apply-risk-panel[data-apply-tab='subject']")

        # ---------- v1.38.2：备注操作人回显 + 跨页回显 ----------
        page.goto(f"{BASE}/pages/project-detail.html", wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.click('.step-label[data-step="2"]')
        page.wait_for_timeout(800)
        # 在第 5 行填备注 → 应立即显示操作人
        r5 = page.locator("#riskPanelSubject tbody tr").nth(5)
        r5.locator(".risk-remark-select").select_option("custom")
        page.wait_for_timeout(300)
        r5.locator(".risk-remark-input").fill("社保人数异常需人工复核")
        page.wait_for_timeout(500)
        op_txt = r5.locator(".risk-remark-op").inner_text()
        user = page.evaluate("() => { const e = document.querySelector('.topbar-user-name');"
                             " return e ? e.textContent.trim() : ''; }")
        check("详情页：备注下方显示操作人姓名", user and user in op_txt,
              f"操作人={user!r} 显示={op_txt!r}")
        check("详情页：备注下方显示操作时间", "·" in op_txt and ":" in op_txt, f"实际 {op_txt!r}")

        # 切到申请页（同一企业）→ 备注应已持久化并回显
        page.goto(f"{BASE}/pages/project-apply.html", wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.locator("text=企业尽调报告").first.click()
        page.wait_for_timeout(1200)
        ap = page.locator(".apply-risk-panel[data-apply-tab='subject'] tbody tr").nth(5)
        check("申请页：回显详情页填写的备注", ap.locator(".risk-remark-input").input_value() == "社保人数异常需人工复核",
              f"实际 {ap.locator('.risk-remark-input').input_value()!r}")
        ap_op = ap.locator(".risk-remark-op").inner_text()
        check("申请页：回显操作人姓名", user and user in ap_op, f"实际 {ap_op!r}")

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
