#!/usr/bin/env python3
"""
豫港通高保真原型 - 批量页面生成器 v2（基于模板替换，最快）
基于 3 个已完成的代表页：
  - contract-purchase.html  (列表型)
  - contract-purchase-framework-detail.html (详情型)
  - project-apply.html  (表单型)
通过字符串替换快速生成 60+ 页面。
"""
import os
import re
from pathlib import Path

PAGES_DIR = Path(__file__).parent.parent / "pages"
PAGES_DIR.mkdir(exist_ok=True)

# ============================================================
# 公共侧边菜单（按业务模块分类）
# ============================================================

MENU_ADM = '''<div class="sidemenu">
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">📋</span><span style="flex: 1;">项目管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items"><a href="./project-list.html" class="sidemenu-item">立项申请</a></div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">👥</span><span style="flex: 1;">客户管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./customer-list.html" class="sidemenu-item">客户管理</a>
          <a href="./customer-apply.html" class="sidemenu-item">新增客户申请</a>
          <a href="./customer-quota.html" class="sidemenu-item">额度管理</a>
        </div>
      </div>
      <div class="sidemenu-group">
        <div class="sidemenu-group-title"><span class="icon">🚫</span><span style="flex: 1;">黑名单管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items"><a href="./blacklist.html" class="sidemenu-item">黑名单管理</a></div>
      </div>
    </div>'''

MENU_SCM = '''<div class="sidemenu">
      <div class="sidemenu-group open">
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

MENU_WH = '''<div class="sidemenu">
      <div class="sidemenu-group open">
        <div class="sidemenu-group-title"><span class="icon">🏭</span><span style="flex: 1;">仓储管理</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./warehouse-inbound.html" class="sidemenu-item">入库记录</a>
          <a href="./warehouse-outbound.html" class="sidemenu-item">出库记录</a>
          <a href="./warehouse-release.html" class="sidemenu-item">放货管理</a>
        </div>
      </div>
    </div>'''

MENU_WARN = '''<div class="sidemenu">
      <div class="sidemenu-group open">
        <div class="sidemenu-group-title"><span class="icon">🔔</span><span style="flex: 1;">预警中心</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./warning-list.html" class="sidemenu-item">预警列表</a>
          <a href="./warning-config.html" class="sidemenu-item">预警规则配置</a>
        </div>
      </div>
    </div>'''

MENU_DC = '''<div class="sidemenu">
      <div class="sidemenu-group open">
        <div class="sidemenu-group-title"><span class="icon">📊</span><span style="flex: 1;">数据中心</span><span class="arrow">▾</span></div>
        <div class="sidemenu-items">
          <a href="./dashboard.html" class="sidemenu-item">驾驶舱</a>
          <a href="./report-project.html" class="sidemenu-item">项目台账表</a>
          <a href="./report-bizline.html" class="sidemenu-item">业务线台账表</a>
        </div>
      </div>
    </div>'''


# ============================================================
# 顶 nav active 切换
# ============================================================

TOPBAR_BASE = '''<div class="topbar">
    <div class="topbar-logo">
      <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 16px;">豫</div>
      <span>豫港通</span>
    </div>
    <div class="topbar-menu">
      <div class="topbar-menu-item{work}">工作台</div>
      <div class="topbar-menu-item{adm}">准入管理</div>
      <div class="topbar-menu-item{scm}">数字供应链</div>
      <div class="topbar-menu-item{wh}">仓储管理</div>
      <div class="topbar-menu-item{warn}">预警中心</div>
      <div class="topbar-menu-item{dc}">数据中心</div>
      <div class="topbar-menu-item{ac}">账户中心</div>
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

ACTIVE_KEYS = ["work", "adm", "scm", "wh", "warn", "dc", "ac"]
TOP_KEYS = {"work": "work", "adm": "adm", "scm": "scm", "wh": "wh", "warn": "warn", "dc": "dc", "ac": "ac"}

def get_topbar(active="adm"):
    out = TOPBAR_BASE
    for k in ACTIVE_KEYS:
        cls = " active" if TOP_KEYS.get(k) == active else ""
        out = out.replace("{" + k + "}", cls)
    return out


# ============================================================
# 通用"占位"列表页生成器
# ============================================================

def gen_simple_list_page(
    filename, page_title, breadcrumb, active_top, menu_html, body_html, doc_title="页面"
):
    """最简化列表页：完整 HTML 框架 + body_html（自定义内容）"""
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
  {get_topbar(active_top)}

  <div style="display: flex;">
    {menu_html}

    <div style="flex: 1; display: flex; flex-direction: column; min-width: 0;">
      <div class="page-header">
        <div class="breadcrumb">{breadcrumb_html}</div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <h1 class="page-title">{page_title}</h1>
        </div>
      </div>
      {body_html}
    </div>
  </div>
</body>
</html>'''
    (PAGES_DIR / filename).write_text(html, encoding="utf-8")
    print(f"  + {filename}")


def gen_simple_detail_page(
    filename, page_title, breadcrumb, active_top, menu_html, body_html, status_label="审核中", status_color="tag-yellow", doc_title="页面"
):
    """最简化详情页"""
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
  {get_topbar(active_top)}

  <div style="display: flex;">
    {menu_html}

    <div style="flex: 1; display: flex; flex-direction: column; min-width: 0;">
      <div class="page-header">
        <div class="breadcrumb">{breadcrumb_html}</div>
      </div>
      {body_html}
    </div>
  </div>
</body>
</html>'''
    (PAGES_DIR / filename).write_text(html, encoding="utf-8")
    print(f"  + {filename}")


# ============================================================
# 标准列表卡片
# ============================================================

def list_body(filter_html, status_tabs, cards, sub_tabs_html=""):
    """构造标准列表页 body（不含 page-header 之外的内容）"""
    status_html = "\n".join([
        f'<div class="status-tab{" active" if active else ""}">{name} <span class="count">{count}</span></div>'
        for name, count, active in status_tabs
    ])
    return f'''
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
        {status_html}
      </div>

      {sub_tabs_html}

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
      </div>'''


def filter_field(label, ftype="text", placeholder="", options=None):
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
    return f'''<div class="filter-item">
      <div class="filter-item-label">{label}</div>
      <input type="text" class="input" placeholder="{placeholder}">
    </div>'''


def card(corner, corner_color, code, status_tag, status_color, meta, cells, actions):
    """构造一张标准列表卡片"""
    meta_html = "".join([f'<div><span style="color: var(--text-tertiary);">{k}</span> {v}</div>' for k, v in meta])
    cells_html = ""
    for c in cells:
        if c.get("type") == "progress":
            cls = c.get("fill_cls", "")
            cells_html += f'''<div>
              <div style="font-size: 11px; color: var(--text-tertiary); margin-bottom: 4px;">{c["label"]}</div>
              <div class="progress"><div class="progress-bar"><div class="progress-fill{cls}" style="width: {c["pct"]}%"></div></div><span class="progress-text">{c["pct"]}%</span></div>
            </div>'''
        else:
            sub = f'<div style="font-size: 11px; color: var(--text-tertiary);">{c["sub"]}</div>' if c.get("sub") else ''
            extra = c.get("extra_style", "")
            cells_html += f'''<div>
              <div style="font-size: 11px; color: var(--text-tertiary); margin-bottom: 4px;">{c["label"]}</div>
              <div style="font-size: 16px; font-weight: 600;{extra}">{c["value"]}</div>
              {sub}
            </div>'''
    actions_html = "".join([f'<a href="{a.get("href","#")}" class="btn-text">{a["text"]}</a>' for a in actions])
    return f'''<div class="list-card-item">
      <div class="list-card-item-corner" style="background: {corner_color};">{corner}</div>
      <div style="display: grid; grid-template-columns: 2.2fr 1fr 1fr 1fr 1fr 1fr 120px; gap: 16px; align-items: center;">
        <div>
          <div class="contract-card-title">
            <span style="font-family: var(--font-mono);">{code}</span>
            <span class="tag {status_color}">{status_tag}</span>
          </div>
          <div class="contract-card-meta">{meta_html}</div>
        </div>
        {cells_html}
        <div class="contract-card-actions">{actions_html}</div>
      </div>
    </div>'''


# ============================================================
# 批量生成 02.04 - 02.16
# ============================================================

def main():
    """批量生成剩余 60+ 页面"""
    print("==> 02.04 订单管理")
    # 订单管理 - 列表型
    cards = card(
        "执行中", "var(--color-info)",
        "DD-20260126-001", "执行中", "tag-blue",
        [("客户", "河南双汇集团"), ("业务线", "SKYWX202601050002"), ("订单类型", "销售出库"), ("创建时间", "2026-01-26")],
        [
            {"label": "品名", "value": "玉米", "sub": "1,200吨 × 2,800元/吨"},
            {"type": "progress", "label": "发货进度", "pct": 75, "fill_cls": ""},
            {"type": "progress", "label": "结算进度", "pct": 60, "fill_cls": ""},
            {"type": "progress", "label": "回款进度", "pct": 50, "fill_cls": "warning"},
            {"label": "订单金额", "value": "¥ 3,360,000", "sub": "已发货 900吨"},
        ],
        [{"text": "订单详情"}, {"text": "编辑"}, {"text": "发货"}],
    ) + card(
        "已完结", "var(--color-success)",
        "DD-20260115-002", "已完结", "tag-green",
        [("客户", "中粮贸易"), ("业务线", "SKYWX202512100001"), ("订单类型", "采购入库"), ("创建时间", "2026-01-15")],
        [
            {"label": "品名", "value": "玉米", "sub": "2,000吨 × 2,750元/吨"},
            {"type": "progress", "label": "发货进度", "pct": 100, "fill_cls": "success"},
            {"type": "progress", "label": "结算进度", "pct": 100, "fill_cls": "success"},
            {"type": "progress", "label": "回款进度", "pct": 100, "fill_cls": "success"},
            {"label": "订单金额", "value": "¥ 5,500,000", "sub": "已结清"},
        ],
        [{"text": "订单详情"}, {"text": "下载凭证"}],
    )
    gen_simple_list_page(
        "order-list.html", "订单管理",
        ["数字供应链", "合同管理", "订单管理"],
        "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("订单编号"), filter_field("客户名称"), filter_field("订单类型", "select", "请选择", ["采购入库", "销售出库", "内部调拨"])]),
            [("全部", "100", True), ("待提交", "8", False), ("执行中", "78", False), ("已完结", "12", False), ("已取消", "2", False)],
            cards,
        ),
    )

    print("==> 02.05 收发货管理")
    # 发货管理
    cards = card(
        "执行中", "var(--color-info)", "FH-20260126-001", "执行中", "tag-blue",
        [("客户", "河南双汇集团"), ("品名", "玉米"), ("数量", "1,200 吨")],
        [{"label": "发货日期", "value": "2026-01-26"}, {"type":"progress","label":"出库进度","pct":75}, {"type":"progress","label":"签收进度","pct":60}, {"label":"运输方式", "value": "中欧班列"}, {"label":"运单号", "value": "YD20260126001", "extra_style": "font-family: var(--font-mono); font-size: 13px;"}],
        [{"text": "发货详情"}, {"text": "编辑"}, {"text": "签收"}],
    )
    gen_simple_list_page(
        "shipment-out.html", "发货管理",
        ["数字供应链", "收发货管理", "发货管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("发货单号"), filter_field("客户名称"), filter_field("运输方式", "select", "请选择", ["中欧班列", "海运", "铁路", "公路"])]),
            [("全部", "100", True), ("待发货", "8", False), ("运输中", "78", False), ("已签收", "12", False)],
            cards,
        ),
    )
    # 收货管理
    cards = card(
        "执行中", "var(--color-info)", "SH-20260126-001", "执行中", "tag-blue",
        [("供应商", "中粮贸易"), ("品名", "玉米"), ("数量", "2,000 吨")],
        [{"label": "收货日期", "value": "2026-01-26"}, {"type":"progress","label":"入库进度","pct":85}, {"type":"progress","label":"验收进度","pct":70}, {"label":"仓库", "value": "新郑库 A-01"}, {"label":"运单号", "value": "YD20260125001", "extra_style": "font-family: var(--font-mono); font-size: 13px;"}],
        [{"text": "收货详情"}, {"text": "验收"}],
    )
    gen_simple_list_page(
        "shipment-in.html", "收货管理",
        ["数字供应链", "收发货管理", "收货管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("收货单号"), filter_field("供应商"), filter_field("仓库", "select", "请选择", ["新郑库", "郑州库", "洛阳库"])]),
            [("全部", "100", True), ("待收货", "6", False), ("已到货", "82", False), ("已验收", "12", False)],
            cards,
        ),
    )

    print("==> 02.06 业务线管理")
    cards = card(
        "执行中", "var(--color-info)", "SKYWX202607050001", "执行中", "tag-blue",
        [("业务线名称", "河南诚泽运输 - 河南中豫港通"), ("起始日", "2026-01-05"), ("业务类型", "存货类")],
        [{"label": "采购合同", "value": "GTGYL-MSXS-20260127-s", "extra_style": "font-family: var(--font-mono); font-size: 13px;"}, {"type":"progress","label":"货物进度","pct":45}, {"type":"progress","label":"资金进度","pct":35}, {"label":"业务负责人", "value": "张爽"}, {"label":"业务线金额", "value": "¥ 68,000,000", "extra_style": "color: var(--color-primary);"}],
        [{"text": "业务线详情"}, {"text": "更多"}],
    )
    gen_simple_list_page(
        "business-line.html", "业务线管理",
        ["数字供应链", "业务线管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("业务线号"), filter_field("业务类型", "select", "请选择", ["存货业务", "预付业务", "账期业务", "购销业务", "总代业务"]), filter_field("创建时间", "dateRange")]),
            [("全部", "100", True), ("执行中", "82", False), ("已完结", "15", False), ("已终止", "3", False)],
            cards,
        ),
    )

    print("==> 02.07 货转管理")
    cards = card(
        "执行中", "var(--color-info)", "HZ-20260126-001", "执行中", "tag-blue",
        [("业务线", "SKYWX202601050001"), ("转出库", "新郑库 A-01"), ("转入库", "郑州库 B-02")],
        [{"label": "品名", "value": "进口木薯淀粉", "sub": "1,000 吨"}, {"type":"progress","label":"装车进度","pct":80}, {"type":"progress","label":"运输进度","pct":50}, {"label":"运输方式", "value": "中欧班列"}, {"label":"运单号", "value": "YD20260126002", "extra_style": "font-family: var(--font-mono); font-size: 13px;"}],
        [{"text": "货转详情"}, {"text": "OCR识别"}, {"text": "所有权确认"}],
    )
    gen_simple_list_page(
        "goods-transfer.html", "货转管理",
        ["数字供应链", "货转管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("货转单号"), filter_field("业务线号"), filter_field("运输方式", "select", "请选择", ["中欧班列", "铁路", "海运", "公路"])]),
            [("全部", "100", True), ("待装车", "8", False), ("运输中", "62", False), ("已签收", "28", False), ("已确认", "2", False)],
            cards,
        ),
    )

    print("==> 02.08 盯市价格管理")
    cards = card(
        "监控中", "var(--color-info)", "PR-20260126-001", "监控中", "tag-blue",
        [("品名", "玉米"), ("监控来源", "Wind 大商所"), ("预警阈值", "±5%")],
        [{"label": "当前价格", "value": "¥ 2,780/吨", "extra_style": "color: var(--color-success); font-size: 18px;"}, {"label": "昨日收盘", "value": "¥ 2,750/吨"}, {"label": "涨跌幅", "value": "+1.09%", "extra_style": "color: var(--color-success); font-weight: 600;"}, {"label": "更新时间", "value": "15:30:00"}, {"label": "操作", "value": "自动监控"}],
        [{"text": "查看趋势"}, {"text": "调整阈值"}],
    )
    gen_simple_list_page(
        "market-price.html", "盯市价格管理",
        ["数字供应链", "盯市价格管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("品名", "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]), filter_field("监控状态", "select", "请选择", ["监控中", "已暂停", "触发预警"])]),
            [("全部", "12", True), ("监控中", "8", False), ("触发预警", "2", False), ("已暂停", "2", False)],
            cards,
        ),
    )

    print("==> 02.09 追保函管理")
    cards = card(
        "生效中", "var(--color-success)", "ZB-20260126-001", "生效中", "tag-green",
        [("客户", "中粮贸易"), ("追保类型", "电子追保函"), ("追保金额", "¥ 5,000,000")],
        [{"label": "触发原因", "value": "盯市预警 - 价格下跌"}, {"label": "签发日期", "value": "2026-01-25"}, {"label": "生效日期", "value": "2026-01-26"}, {"label": "到期日期", "value": "2026-04-25"}, {"label": "追保状态", "value": "已签收", "extra_style": "color: var(--color-success);"}],
        [{"text": "查看详情"}, {"text": "下载函件"}],
    )
    gen_simple_list_page(
        "bond-letter.html", "追保函管理",
        ["数字供应链", "追保函管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("追保函号"), filter_field("客户名称"), filter_field("追保类型", "select", "请选择", ["电子追保函", "线下追保函"])]),
            [("全部", "32", True), ("待签发", "3", False), ("已签发", "5", False), ("生效中", "18", False), ("已到期", "6", False)],
            cards,
        ),
    )

    print("==> 02.10 保证金管理")
    cards = card(
        "正常", "var(--color-success)", "MR-20260126-001", "正常", "tag-green",
        [("客户", "河南军牧原国际贸易"), ("保证金类型", "履约保证金")],
        [{"label": "保证金余额", "value": "¥ 3,200,000", "extra_style": "color: var(--color-success); font-size: 18px;"}, {"label": "占用金额", "value": "¥ 800,000"}, {"label": "可用余额", "value": "¥ 2,400,000"}, {"label": "保证金率", "value": "8.5%"}, {"label": "上次变动", "value": "2026-01-15"}],
        [{"text": "查看流水"}, {"text": "补充保证金"}],
    )
    gen_simple_list_page(
        "margin-pool.html", "保证金管理",
        ["数字供应链", "资金管理", "保证金管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("保证金号"), filter_field("客户名称"), filter_field("保证金类型", "select", "请选择", ["履约保证金", "风险保证金", "结算保证金"])]),
            [("全部", "100", True), ("正常", "82", False), ("预警", "12", False), ("不足", "6", False)],
            cards,
        ),
    )

    print("==> 02.11 预警中心")
    # 预警列表
    cards = card(
        "未处理", "var(--color-danger)", "WJ-20260126-001", "未处理", "tag-red",
        [("预警类型", "价格波动"), ("触发规则", "玉米价格下跌 ≥ 3%"), ("涉及业务线", "SKYWX202601050001")],
        [{"label": "当前值", "value": "¥ 2,650/吨"}, {"label": "基准值", "value": "¥ 2,750/吨"}, {"type":"progress","label":"波动幅度","pct":96, "fill_cls": "danger" if False else ""}, {"label": "触发时间", "value": "2026-01-26 14:30"}, {"label": "紧急程度", "value": "高", "extra_style": "color: var(--color-danger); font-weight: 600;"}],
        [{"text": "查看详情"}, {"text": "立即处理"}],
    )
    gen_simple_list_page(
        "warning-list.html", "预警列表",
        ["预警中心", "预警列表"], "warn", MENU_WARN,
        list_body(
            "\n".join([filter_field("预警编号"), filter_field("预警类型", "select", "请选择", ["价格波动", "企业监控", "交易监控", "额度预警"]), filter_field("紧急程度", "select", "请选择", ["高", "中", "低"])]),
            [("全部", "100", True), ("未处理", "8", False), ("处理中", "12", False), ("已处理", "78", False), ("已忽略", "2", False)],
            cards,
        ),
    )
    # 预警规则配置
    cards = card(
        "启用中", "var(--color-success)", "RULE-001", "启用中", "tag-green",
        [("规则名称", "玉米价格下跌预警"), ("规则类型", "价格波动"), ("监控对象", "玉米 / Wind大商所")],
        [{"label": "触发条件", "value": "日跌幅 ≥ 3%"}, {"label": "预警级别", "value": "高", "extra_style": "color: var(--color-danger);"}, {"label": "通知方式", "value": "短信 + 邮件 + 站内信"}, {"label": "通知对象", "value": "风控 + 业务 + 总经办"}, {"label": "触发次数", "value": "本月 3 次", "extra_style": "color: var(--color-warning); font-weight: 600;"}],
        [{"text": "编辑规则"}, {"text": "禁用"}, {"text": "查看触发记录"}],
    )
    gen_simple_list_page(
        "warning-config.html", "预警规则配置",
        ["预警中心", "预警规则配置"], "warn", MENU_WARN,
        list_body(
            "\n".join([filter_field("规则名称"), filter_field("规则类型", "select", "请选择", ["价格波动", "企业监控", "交易监控"])]),
            [("全部", "18", True), ("启用中", "12", False), ("已禁用", "6", False)],
            cards,
        ),
    )

    print("==> 02.12 仓储管理")
    # 入库记录
    cards = card(
        "已入库", "var(--color-success)", "RK-20260126-001", "已入库", "tag-green",
        [("仓库", "新郑库 A-01"), ("品名", "玉米"), ("供应商", "中粮贸易")],
        [{"label": "入库数量", "value": "2,000 吨", "extra_style": "color: var(--color-primary); font-size: 18px;"}, {"label": "入库日期", "value": "2026-01-26"}, {"type":"progress","label":"入库进度","pct":100, "fill_cls": "success"}, {"label": "货位", "value": "A-01-12", "extra_style": "font-family: var(--font-mono);"}, {"label": "操作", "value": "系统自动"}],
        [{"text": "入库详情"}, {"text": "查看货位"}],
    )
    gen_simple_list_page(
        "warehouse-inbound.html", "入库记录",
        ["仓储管理", "入库记录"], "wh", MENU_WH,
        list_body(
            "\n".join([filter_field("入库单号"), filter_field("仓库", "select", "请选择", ["新郑库", "郑州库", "洛阳库"]), filter_field("品名", "select", "请选择", ["玉米", "糖粉", "木薯淀粉"])]),
            [("全部", "100", True), ("待入库", "6", False), ("入库中", "12", False), ("已入库", "82", False)],
            cards,
        ),
    )
    # 出库记录
    cards = card(
        "已出库", "var(--color-success)", "CK-20260126-001", "已出库", "tag-green",
        [("仓库", "新郑库 A-01"), ("品名", "玉米"), ("客户", "河南双汇集团")],
        [{"label": "出库数量", "value": "1,200 吨", "extra_style": "color: var(--color-primary); font-size: 18px;"}, {"label": "出库日期", "value": "2026-01-26"}, {"type":"progress","label":"出库进度","pct":100, "fill_cls": "success"}, {"label": "货位", "value": "A-01-12", "extra_style": "font-family: var(--font-mono);"}, {"label": "运单号", "value": "YD20260126001", "extra_style": "font-family: var(--font-mono); font-size: 13px;"}],
        [{"text": "出库详情"}, {"text": "查看货位"}],
    )
    gen_simple_list_page(
        "warehouse-outbound.html", "出库记录",
        ["仓储管理", "出库记录"], "wh", MENU_WH,
        list_body(
            "\n".join([filter_field("出库单号"), filter_field("仓库", "select", "请选择", ["新郑库", "郑州库", "洛阳库"]), filter_field("品名", "select", "请选择", ["玉米", "糖粉", "木薯淀粉"])]),
            [("全部", "100", True), ("待出库", "8", False), ("出库中", "12", False), ("已出库", "80", False)],
            cards,
        ),
    )
    # 放货管理
    cards = card(
        "待放货", "var(--color-warning)", "FH-20260126-001", "待放货", "tag-yellow",
        [("客户", "河南双汇集团"), ("品名", "玉米"), ("对应合同", "XS-MSXS-20260125-s")],
        [{"label": "申请数量", "value": "1,200 吨"}, {"label": "申请日期", "value": "2026-01-26"}, {"type":"progress","label":"审批进度","pct":50}, {"label": "货位", "value": "A-01-12", "extra_style": "font-family: var(--font-mono);"}, {"label": "申请人", "value": "张爽"}],
        [{"text": "审批"}, {"text": "驳回"}],
    )
    gen_simple_list_page(
        "warehouse-release.html", "放货管理",
        ["仓储管理", "放货管理"], "wh", MENU_WH,
        list_body(
            "\n".join([filter_field("放货申请号"), filter_field("客户名称"), filter_field("品名", "select", "请选择", ["玉米", "糖粉", "木薯淀粉"])]),
            [("全部", "32", True), ("待放货", "8", False), ("放货中", "12", False), ("已放货", "10", False), ("已驳回", "2", False)],
            cards,
        ),
    )

    print("==> 02.13 结算单管理")
    # 采购结算
    cards = card(
        "待结算", "var(--color-warning)", "JS-20260126-001", "待结算", "tag-yellow",
        [("供应商", "中粮贸易"), ("采购合同", "GTGYL-MSXS-20260127-s"), ("业务线", "SKYWX202601050001")],
        [{"label": "结算数量", "value": "1,000 吨"}, {"label": "结算金额", "value": "¥ 3,400,000", "extra_style": "color: var(--color-primary); font-size: 18px;"}, {"type":"progress","label":"付款进度","pct":50}, {"label": "结算日期", "value": "2026-01-26"}, {"label": "结算类型", "value": "线下"}],
        [{"text": "结算详情"}, {"text": "确认结算"}],
    )
    gen_simple_list_page(
        "settlement-purchase.html", "采购结算",
        ["数字供应链", "结算/发票", "采购结算"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("结算单号"), filter_field("供应商"), filter_field("结算日期", "dateRange")]),
            [("全部", "100", True), ("待结算", "12", False), ("已结算", "82", False), ("已驳回", "6", False)],
            cards,
        ),
    )
    # 销售结算
    cards = card(
        "已结算", "var(--color-success)", "JS-20260126-002", "已结算", "tag-green",
        [("客户", "河南双汇集团"), ("销售合同", "XS-MSXS-20260125-s"), ("业务线", "SKYWX202601050002")],
        [{"label": "结算数量", "value": "1,200 吨"}, {"label": "结算金额", "value": "¥ 4,560,000", "extra_style": "color: var(--color-success); font-size: 18px;"}, {"type":"progress","label":"回款进度","pct":80}, {"label": "结算日期", "value": "2026-01-26"}, {"label": "结算类型", "value": "线下"}],
        [{"text": "结算详情"}, {"text": "查看回款"}],
    )
    gen_simple_list_page(
        "settlement-sales.html", "销售结算",
        ["数字供应链", "结算/发票", "销售结算"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("结算单号"), filter_field("客户"), filter_field("结算日期", "dateRange")]),
            [("全部", "100", True), ("待结算", "12", False), ("已结算", "82", False), ("已驳回", "6", False)],
            cards,
        ),
    )

    print("==> 02.14 资金管理")
    # 付款列表
    cards = card(
        "待付款", "var(--color-warning)", "FK-20260126-001", "待付款", "tag-yellow",
        [("收款方", "中粮贸易"), ("付款类型", "货款"), ("对应合同", "GTGYL-MSXS-20260127-s")],
        [{"label": "付款金额", "value": "¥ 3,400,000", "extra_style": "color: var(--color-primary); font-size: 18px;"}, {"type":"progress","label":"审批进度","pct":60}, {"label": "付款方式", "value": "线下转账"}, {"label": "计划付款日期", "value": "2026-01-28"}, {"label": "付款状态", "value": "待审批", "extra_style": "color: var(--color-warning);"}],
        [{"text": "付款详情"}, {"text": "上传凭证"}],
    )
    gen_simple_list_page(
        "payment-list.html", "付款列表",
        ["数字供应链", "资金管理", "付款列表"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("付款单号"), filter_field("收款方"), filter_field("付款类型", "select", "请选择", ["货款", "运费", "保证金", "其他"]), filter_field("付款日期", "dateRange")]),
            [("全部", "100", True), ("待付款", "12", False), ("已付款", "82", False), ("已驳回", "6", False)],
            cards,
        ),
    )
    # 回款管理
    cards = card(
        "已认领", "var(--color-success)", "HK-20260126-001", "已认领", "tag-green",
        [("付款方", "河南双汇集团"), ("回款类型", "货款"), ("对应合同", "XS-MSXS-20260125-s")],
        [{"label": "回款金额", "value": "¥ 4,560,000", "extra_style": "color: var(--color-success); font-size: 18px;"}, {"type":"progress","label":"认领进度","pct":100, "fill_cls": "success"}, {"label": "匹配方式", "value": "订单号自动匹配"}, {"label": "到账日期", "value": "2026-01-26"}, {"label": "凭证", "value": "已上传", "extra_style": "color: var(--color-success);"}],
        [{"text": "回款详情"}, {"text": "查看凭证"}],
    )
    gen_simple_list_page(
        "receipt-list.html", "回款管理",
        ["数字供应链", "资金管理", "回款管理"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("回款单号"), filter_field("付款方"), filter_field("回款类型", "select", "请选择", ["货款", "运费", "保证金", "其他"]), filter_field("到账日期", "dateRange")]),
            [("全部", "100", True), ("待认领", "8", False), ("已认领", "82", False), ("异常", "10", False)],
            cards,
        ),
    )

    print("==> 02.15 发票管理")
    cards = card(
        "已开具", "var(--color-success)", "FP-20260126-001", "已开具", "tag-green",
        [("供应商", "中粮贸易"), ("发票类型", "增值税专用发票"), ("对应合同", "GTGYL-MSXS-20260127-s")],
        [{"label": "发票金额", "value": "¥ 3,400,000", "extra_style": "color: var(--color-primary); font-size: 18px;"}, {"label": "税率", "value": "13%"}, {"label": "税额", "value": "¥ 442,000"}, {"label": "开票日期", "value": "2026-01-26"}, {"label": "发票号", "value": "FP20260126001", "extra_style": "font-family: var(--font-mono); font-size: 13px;"}],
        [{"text": "查看详情"}, {"text": "下载发票"}],
    )
    gen_simple_list_page(
        "invoice.html", "进项发票",
        ["数字供应链", "结算/发票", "进项发票"], "scm", MENU_SCM,
        list_body(
            "\n".join([filter_field("发票号"), filter_field("供应商"), filter_field("发票类型", "select", "请选择", ["增值税专用发票", "增值税普通发票"]), filter_field("开票日期", "dateRange")]),
            [("全部", "100", True), ("待开具", "8", False), ("已开具", "82", False), ("已认证", "10", False)],
            cards,
        ),
    )

    print("==> 02.16 数据中心")
    # 驾驶舱
    cards = card(
        "概览", "var(--color-primary)", "DASHBOARD-202601", "概览", "tag-blue",
        [("统计周期", "2026-01"), ("数据来源", "全模块")],
        [{"label": "项目总数", "value": "118", "extra_style": "color: var(--color-primary); font-size: 24px;"}, {"label": "执行中项目", "value": "92"}, {"label": "本月新增", "value": "12", "extra_style": "color: var(--color-success);"}, {"label": "本月完结", "value": "8"}, {"label": "本月 GMV", "value": "¥ 580,000,000", "extra_style": "color: var(--color-primary); font-size: 18px;"}],
        [{"text": "查看明细"}],
    )
    gen_simple_list_page(
        "dashboard.html", "驾驶舱",
        ["数据中心", "驾驶舱"], "dc", MENU_DC,
        list_body(
            "\n".join([filter_field("统计周期", "dateRange"), filter_field("业务类型", "select", "请选择", ["全部", "存货业务", "预付业务", "账期业务", "购销业务", "总代业务"])]),
            [("概览", "1", True), ("项目", "118", False), ("合同", "236", False), ("客户", "182", False)],
            cards,
        ),
    )
    # 项目台账表
    cards = card(
        "汇总", "var(--color-info)", "RPT-PROJ-202601", "汇总", "tag-blue",
        [("统计周期", "2026-01"), ("项目数", "118")],
        [{"label": "立项金额", "value": "¥ 1,200,000,000", "extra_style": "color: var(--color-primary);"}, {"label": "执行中", "value": "92"}, {"label": "完结", "value": "18"}, {"label": "驳回", "value": "3"}, {"label": "违约", "value": "5"}],
        [{"text": "导出 Excel"}, {"text": "打印"}],
    )
    gen_simple_list_page(
        "report-project.html", "项目台账表",
        ["数据中心", "项目台账表"], "dc", MENU_DC,
        list_body(
            "\n".join([filter_field("统计周期", "dateRange"), filter_field("项目状态", "select", "请选择", ["全部", "执行中", "已完结", "驳回"])]),
            [("按月", "12", True), ("按季", "4", False), ("按年", "1", False)],
            cards,
        ),
    )
    # 业务线台账表
    cards = card(
        "汇总", "var(--color-info)", "RPT-BIZ-202601", "汇总", "tag-blue",
        [("统计周期", "2026-01"), ("业务线数", "82")],
        [{"label": "业务线金额", "value": "¥ 980,000,000", "extra_style": "color: var(--color-primary);"}, {"label": "执行中", "value": "68"}, {"label": "完结", "value": "12"}, {"label": "终止", "value": "2"}, {"label": "异常", "value": "0"}],
        [{"text": "导出 Excel"}],
    )
    gen_simple_list_page(
        "report-bizline.html", "业务线台账表",
        ["数据中心", "业务线台账表"], "dc", MENU_DC,
        list_body(
            "\n".join([filter_field("统计周期", "dateRange"), filter_field("业务类型", "select", "请选择", ["全部", "存货业务", "预付业务", "账期业务", "购销业务", "总代业务"])]),
            [("按月", "12", True), ("按季", "4", False), ("按年", "1", False)],
            cards,
        ),
    )

    print("\n✅ Done. Pages in:", PAGES_DIR)


if __name__ == "__main__":
    main()
