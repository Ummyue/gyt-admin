#!/usr/bin/env python3
"""
豫港通高保真原型 - 批量页面生成器
- list_page: 标准列表页（顶 nav + 左菜单 + 面包屑 + 筛选 + 状态 Tab + 卡片列表 + 分页）
- detail_page: 标准详情页（顶 nav + 左菜单 + 面包屑 + 顶部信息 + Tab + info-table + 底部操作栏）
- form_page: 标准表单页（顶 nav + 左菜单 + 面包屑 + 4 步骤条 + 卡片表单 + 底部操作栏）
"""
import os
import sys
from pathlib import Path

PAGES_DIR = Path(__file__).parent.parent / "pages"
PAGES_DIR.mkdir(exist_ok=True)

# ============================================================
# 通用模板
# ============================================================

TOPBAR = '''<div class="topbar">
  <div class="topbar-logo">
    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 16px;">豫</div>
    <span>豫港通</span>
  </div>
  <div class="topbar-menu">
    <div class="topbar-menu-item{active_work}">工作台</div>
    <div class="topbar-menu-item{active_adm}">准入管理</div>
    <div class="topbar-menu-item{active_scm}">数字供应链</div>
    <div class="topbar-menu-item{active_wh}">仓储管理</div>
    <div class="topbar-menu-item{active_warn}">预警中心</div>
    <div class="topbar-menu-item{active_dc}">数据中心</div>
    <div class="topbar-menu-item{active_ac}">账户中心</div>
  </div>
  <div class="topbar-right">
    <div class="topbar-icon-btn">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
      <span class="badge"></span>
    </div>
    <div class="topbar-user">
      <div class="topbar-user-avatar">张</div>
      <div>
        <div class="topbar-user-name">张爽</div>
        <div class="topbar-user-org">港通供应链</div>
      </div>
    </div>
  </div>
</div>'''

def topbar(active_top="adm"):
    keys = {"work":"work","adm":"adm","scm":"scm","wh":"wh","warn":"warn","dc":"dc","ac":"ac"}
    return TOPBAR.format(
        active_work=" active" if active_top=="work" else "",
        active_adm=" active" if active_top=="adm" else "",
        active_scm=" active" if active_top=="scm" else "",
        active_wh=" active" if active_top=="wh" else "",
        active_warn=" active" if active_top=="warn" else "",
        active_dc=" active" if active_top=="dc" else "",
        active_ac=" active" if active_top=="ac" else "",
    )

# ============================================================
# 标准列表页生成器
# ============================================================

def gen_list_page(
    filename,           # 输出文件名，如 "shipment-out.html"
    page_title,         # 页面标题
    breadcrumb,         # 面包屑，list of strings
    menu_svg,           # 菜单图标 emoji
    menu_group,         # 菜单组名
    menu_items,         # [(text, link, active_bool)]
    active_top,         # 工作台/准入/数字供应链 etc
    filter_fields,      # [(label, type, placeholder, options)]  type: text/select/dateRange
    status_tabs,        # [(name, count, active_bool)]
    show_content_tab,   # 是否显示子 tab（如基础信息/额度信息）
    content_tabs,       # [(name, active_bool)]
    show_new_btn,       # 右上角是否显示新增按钮
    new_btn_text,       # 新增按钮文本
    cards,              # 列表卡片 HTML 字符串（多张卡片拼接）
):
    """生成标准列表页 HTML"""
    sidemenu_items_html = "\n".join([
        f'<a href="{link}" class="sidemenu-item{" active" if active else ""}">{text}</a>'
        for text, link, active in menu_items
    ])
    filter_html = "\n".join([
        _render_filter_field(label, ftype, placeholder, options)
        for label, ftype, placeholder, options in filter_fields
    ])
    status_tabs_html = "\n".join([
        f'<div class="status-tab{" active" if active else ""}">{name} <span class="count">{count}</span></div>'
        for name, count, active in status_tabs
    ])
    content_tabs_html = ""
    if show_content_tab:
        content_tabs_html = '<div class="tabs" style="padding: 0 24px; background: var(--bg-card);">\n'
        content_tabs_html += "\n".join([
            f'<div class="tab{" active" if active else ""}">{name}</div>'
            for name, active in content_tabs
        ])
        content_tabs_html += "\n</div>"
    new_btn_html = ""
    if show_new_btn:
        new_btn_html = f'''<button class="btn btn-primary">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            {new_btn_text}
          </button>'''
    breadcrumb_html = ""
    for i, item in enumerate(breadcrumb):
        if i == len(breadcrumb) - 1:
            breadcrumb_html += f'<span class="current">{item}</span>'
        else:
            breadcrumb_html += f'<span>{item}</span><span class="separator">/</span>'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title} - 豫港通</title>
  <link rel="stylesheet" href="../assets/css/design-system.css">
</head>
<body>
  {topbar(active_top)}

  <div style="display: flex;">
    <div class="sidemenu">
      <div class="sidemenu-group open">
        <div class="sidemenu-group-title">
          <span class="icon">{menu_svg}</span>
          <span style="flex: 1;">{menu_group}</span>
          <span class="arrow">▾</span>
        </div>
        <div class="sidemenu-items">
          {sidemenu_items_html}
        </div>
      </div>
    </div>

    <div style="flex: 1; display: flex; flex-direction: column; min-width: 0;">
      <div class="page-header">
        <div class="breadcrumb">
          {breadcrumb_html}
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <h1 class="page-title">{page_title}</h1>
          {new_btn_html}
        </div>
      </div>

      <div class="filter-bar">
        {filter_html}
        <div class="filter-actions">
          <button class="btn btn-primary btn-sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            查询
          </button>
          <button class="btn btn-secondary btn-sm">重置</button>
        </div>
      </div>

      <div class="status-tabs" style="padding: 0 24px; background: var(--bg-card);">
        {status_tabs_html}
      </div>

      {content_tabs_html}

      <div style="flex: 1; padding: 16px 24px 24px; overflow-y: auto; background: var(--bg-page);">
        {cards}
        <div class="pagination">
          <div>共 36 条记录 · 第 1 / 4 页</div>
          <div class="pagination-pages">
            <div class="pagination-page">‹</div>
            <div class="pagination-page active">1</div>
            <div class="pagination-page">2</div>
            <div class="pagination-page">3</div>
            <div class="pagination-page">4</div>
            <div class="pagination-page">›</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>'''
    (PAGES_DIR / filename).write_text(html, encoding="utf-8")
    print(f"✓ {filename}")


def _render_filter_field(label, ftype, placeholder, options=None):
    if ftype == "select":
        opts = "\n".join([f'<option>{o}</option>' for o in (options or ["全部"])])
        return f'''<div class="filter-item">
          <div class="filter-item-label">{label}</div>
          <select class="select"><option>{placeholder or "请选择"}</option>{opts}</select>
        </div>'''
    if ftype == "dateRange":
        return f'''<div class="filter-item">
          <div class="filter-item-label">{label}</div>
          <input type="text" class="input" placeholder="{placeholder or "开始时间 ~ 结束时间"}">
        </div>'''
    # text
    return f'''<div class="filter-item">
      <div class="filter-item-label">{label}</div>
      <input type="text" class="input" placeholder="{placeholder}">
    </div>'''


def sample_card(corner_label, corner_color, title_no, status_tag, status_color, meta_lines, grid_cells, actions):
    """生成一张标准列表卡片"""
    meta_html = "".join([
        f'<div><span style="color: var(--text-tertiary);">{k}</span> {v}</div>'
        for k, v in meta_lines
    ])
    cells_html = ""
    for col in grid_cells:
        if col.get("type") == "progress":
            cells_html += f'''<div>
              <div style="font-size: 11px; color: var(--text-tertiary); margin-bottom: 4px;">{col["label"]}</div>
              <div class="progress"><div class="progress-bar"><div class="progress-fill{col.get("fill_cls","")}" style="width: {col["pct"]}%"></div></div><span class="progress-text">{col["pct"]}%</span></div>
            </div>'''
        else:
            cells_html += f'''<div>
              <div style="font-size: 11px; color: var(--text-tertiary); margin-bottom: 4px;">{col.get("label","")}</div>
              <div style="font-size: 16px; font-weight: 600;{col.get("extra_style","")}">{col["value"]}</div>
              {f'<div style="font-size: 11px; color: var(--text-tertiary);">{col["sub"]}</div>' if col.get("sub") else ''}
            </div>'''
    actions_html = "".join([f'<a href="{a.get("href","#")}" class="btn-text">{a["text"]}</a>' for a in actions])
    return f'''<div class="list-card-item">
      <div class="list-card-item-corner" style="background: {corner_color};">{corner_label}</div>
      <div style="display: grid; grid-template-columns: 2.2fr 1fr 1fr 1fr 1fr 1fr 120px; gap: 16px; align-items: center;">
        <div>
          <div class="contract-card-title">
            <span style="font-family: var(--font-mono);">{title_no}</span>
            <span class="tag {status_color}">{status_tag}</span>
          </div>
          <div class="contract-card-meta">{meta_html}</div>
        </div>
        {cells_html}
        <div class="contract-card-actions">{actions_html}</div>
      </div>
    </div>'''


# ============================================================
# 公共侧边菜单
# ============================================================

SCM_MENU = '''<div class="sidemenu">
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">📄</span><span style="flex: 1;">合同管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./contract-purchase.html" class="sidemenu-item">采购合同</a>
          <a href="./contract-sales.html" class="sidemenu-item">销售合同</a>
          <a href="./contract-shipping.html" class="sidemenu-item">运输合同</a>
          <a href="./contract-supplement.html" class="sidemenu-item">补充协议</a>
        </div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">📦</span><span style="flex: 1;">业务线管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items"><a href="./business-line.html" class="sidemenu-item">业务线管理</a></div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">🚚</span><span style="flex: 1;">收发货管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./shipment-out.html" class="sidemenu-item">发货管理</a>
          <a href="./shipment-in.html" class="sidemenu-item">收货管理</a>
        </div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">🔄</span><span style="flex: 1;">货转管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items"><a href="./goods-transfer.html" class="sidemenu-item">货转管理</a></div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">💰</span><span style="flex: 1;">资金管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./payment-list.html" class="sidemenu-item">付款列表</a>
          <a href="./receipt-list.html" class="sidemenu-item">回款管理</a>
          <a href="./margin-pool.html" class="sidemenu-item">保证金管理</a>
        </div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">📋</span><span style="flex: 1;">盯市/追保</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./market-price.html" class="sidemenu-item">盯市价格管理</a>
          <a href="./bond-letter.html" class="sidemenu-item">追保函管理</a>
        </div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">🧾</span><span style="flex: 1;">结算/发票</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./settlement-purchase.html" class="sidemenu-item">采购结算</a>
          <a href="./settlement-sales.html" class="sidemenu-item">销售结算</a>
          <a href="./invoice.html" class="sidemenu-item">进项发票</a>
        </div>
      </div>
    </div>'''


if __name__ == "__main__":
    # 02.03 合同管理 - 销售合同
    cards = "\n".join([
        sample_card(
            "执行中", "var(--color-info)",
            "XS-MSXS-20260125-s", "执行中", "tag-blue",
            [("卖方", "河南中豫港通供应链"), ("运输方式", "中欧班列-东线"), ("业务类型", "存货类"), ("交货期", "2026-01-25 至 2026-12-31")],
            [
                {"label": "品名", "value": "进口木薯淀粉", "sub": "3,800元/吨 × 18000吨"},
                {"type": "progress", "label": "回款进度", "pct": 65, "fill_cls": ""},
                {"type": "progress", "label": "结算进度", "pct": 50, "fill_cls": ""},
                {"type": "progress", "label": "开票进度", "pct": 40, "fill_cls": ""},
                {"label": "已回款", "value": "¥ 44,460,000", "sub": "11,700 吨"},
            ],
            [{"text": "合同详情"}, {"text": "编辑合同"}, {"text": "发起收款"}, {"text": "更多"}],
        ),
    ])
    gen_list_page(
        filename="contract-sales.html",
        page_title="销售合同",
        breadcrumb=["数字供应链", "合同管理", "销售合同"],
        menu_svg="📄", menu_group="合同管理",
        menu_items=[("采购合同", "./contract-purchase.html", False),
                    ("销售合同", "./contract-sales.html", True),
                    ("运输合同", "./contract-shipping.html", False),
                    ("补充协议", "./contract-supplement.html", False)],
        active_top="scm",
        filter_fields=[
            ("合同编号", "text", "请输入"),
            ("企业名称", "text", "请输入"),
            ("业务类型", "select", "请选择", ["存货业务", "预付业务", "账期业务", "购销业务", "总代业务"]),
            ("签订日期", "dateRange", ""),
        ],
        status_tabs=[("全部", "100", True), ("待确认", "4", False), ("执行中", "82", False), ("已完结", "12", False), ("无效", "2", False)],
        show_content_tab=False, content_tabs=[],
        show_new_btn=True, new_btn_text="新增销售合同",
        cards=cards,
    )
    print("Sales page done")
