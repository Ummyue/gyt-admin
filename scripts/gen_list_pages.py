#!/usr/bin/env python3
"""
列表页批量生成器 v1.7.99
所有 30+ 列表页统一按 v1.7.99 规范生成
"""

import os
from pathlib import Path

PAGES_DIR = Path("/Users/fuyu/.mavis/agents/mavis/workspace/yugangtong-prototype/pages")

# ============================================
# 模板
# ============================================

HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 豫港通</title>
  <link rel="stylesheet" href="../assets/css/design-system.css">
  <link rel="stylesheet" href="../assets/css/list-page.css">
  <style>
    .page-body {
      padding: 20px 24px;
    }
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-logo">
      <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 16px;">豫</div>
      <span>豫港通</span>
    </div>
    <div class="topbar-menu">
      <a class="topbar-menu-item" href="./workbench.html" data-menu-key="工作台">工作台</a>
      <a class="topbar-menu-item" href="./project-list.html" data-menu-key="准入管理">准入管理</a>
      <a class="topbar-menu-item active" href="./contract-purchase.html" data-menu-key="数字供应链">数字供应链</a>
      <a class="topbar-menu-item" href="./warehouse-inbound.html" data-menu-key="仓储管理">仓储管理</a>
      <a class="topbar-menu-item" href="./risk-operations.html" data-menu-key="风险运营管理">风险运营管理</a>
      <a class="topbar-menu-item" href="./cockpit.html" data-menu-key="数据中心">数据中心</a>
      <a class="topbar-menu-item" href="./warning-list.html" data-menu-key="预警中心">预警中心</a>
      <a class="topbar-menu-item" href="./account-personal.html" data-menu-key="账户中心">账户中心</a>
      <button class="topbar-changelog-btn" onclick="window.open('./changelog.html', '_blank')" title="查看高保真原型版本变更记录">📋 版本变更记录</button>
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
  </div>

  <div style="display: flex;">
    <div class="sidemenu" id="leftSidemenu"></div>

    <div class="main-content" style="flex: 1; min-width: 0; display: flex; flex-direction: column;">
      <div class="page-body" style="flex: 1; overflow-y: auto; background: var(--bg-page);">

        <!-- 面包屑 -->
        <div class="breadcrumb-inline">
          <a href="#">{bc1}</a>
          <span class="sep">/</span>
          <a href="#">{bc2}</a>
          <span class="sep">/</span>
          <span class="current">{title}</span>
        </div>

        <!-- 标题 + 新增 -->
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
          <h1 class="page-h1" style="margin: 0;">{title}</h1>
          {add_btn_block}
        </div>

        <!-- 顶部子菜单 tap（v1.7.99.13：只在有 sub_tabs 时输出，否则不渲染空容器） -->
        {sub_tabs_block}

        <!-- 合并 panel：筛选 / 状态 tab / 表格 / 分页 -->
        <div class="cp-panel">

          <!-- 区块 1：筛选区 -->
          <div class="cp-block">
            <div class="cp-filter-summary">
              <div class="cp-filter-summary-left">
                当前搜索：<span data-filter-chips class="filter-chips"></span><span class="filter-empty-hint">（无筛选条件）</span>
                <button type="button" class="clear-all-btn" style="display: none;" onclick="clearAllFilters(this)">清除全部</button>
              </div>
              <button class="btn btn-text btn-sm">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                数据导出
              </button>
            </div>
            <div class="cp-filter">
              {filter_fields_html}
            </div>
          </div>

          <!-- 区块 2：状态 tab（带背景色 + 收紧高度） -->
          <div class="cp-block cp-block-tab">
            <div class="cp-tab-bar">
              <div class="cp-tab-bar-tabs">
                {status_tabs_html}
              </div>
              <div class="cp-tab-bar-actions">
                <!-- 状态 tab 右侧空，预留扩展位 -->
              </div>
            </div>
          </div>

          <!-- 区块 3：表格 -->
          <div class="cp-block" style="padding: 0;">
            <div class="cp-table-wrap">
              <table class="cp-table">
                <thead>
                  <tr>
                    {columns_html}
                  </tr>
                </thead>
                <tbody>
                  {mock_rows_html}
                </tbody>
              </table>
            </div>
          </div>

          <!-- 区块 4：分页 -->
          <div class="cp-block">
            <div class="cp-pagination">
              <div>共 {total} 条记录 · 第 1 / {total_pages} 页</div>
              <div style="display: flex; align-items: center; gap: 14px;">
                <div class="cp-pagination-pages">
                  <div class="cp-pagination-page">‹</div>
                  <div class="cp-pagination-page active">1</div>
                  <div class="cp-pagination-page">2</div>
                  <div class="cp-pagination-page">3</div>
                  <div class="cp-pagination-page">4</div>
                  <div class="cp-pagination-page">›</div>
                </div>
                <select class="cp-pagination-size">
                  <option>10 条/页</option>
                  <option>20 条/页</option>
                  <option>50 条/页</option>
                </select>
                <span class="cp-pagination-jump">跳至 <input type="number" min="1" value="1"> 页</span>
              </div>
            </div>
          </div>

        </div>
        <!-- /cp-panel -->

      </div>
    </div>
  </div>
  <script src="../shared/js/topnav-drawer.js"></script>
  <script src="../shared/js/left-sidemenu.js"></script>
  <script src="../shared/js/filter-chips.js"></script>
  <script>
    // 「新增」按钮下拉（v1.7.99.7 起，采购/销售合同用）
    function toggleAddDropdown(e) {
      if (e) e.stopPropagation();
      var dd = document.getElementById('addBtnDropdown');
      if (dd) dd.classList.toggle('open');
    }
    document.addEventListener('click', function(e) {
      var dd = document.getElementById('addBtnDropdown');
      if (dd && !dd.contains(e.target)) dd.classList.remove('open');
    });

    // 行点击进入详情页（v1.7.99.11 起，project-list 等列表页用）
    // 规则：点击行任意位置（除操作区 .col-action）→ 跳 data-detail-href + ?status=xxx
    (function() {
      var rows = document.querySelectorAll('.cp-row-clickable');
      rows.forEach(function(row) {
        row.addEventListener('click', function(e) {
          // 排除操作区
          if (e.target.closest('.col-action')) return;
          // 排除按钮/链接
          if (e.target.closest('button, a')) return;
          var status = row.getAttribute('data-status') || '';
          var detailHref = row.getAttribute('data-detail-href');
          if (!detailHref) return;
          var url = detailHref + (status ? '?status=' + encodeURIComponent(status) : '');
          window.location.href = url;
        });
      });
    })();
  </script>
  </div>
  <!-- /main-content -->
</body>
</html>
"""

def sub_tabs_html(tabs, active_index=0):
    return "\n            ".join(
        f'<div class="tab-action-tab{" active" if i==active_index else ""}">{tab}</div>'
        for i, tab in enumerate(tabs)
    )

def add_btn_html(cfg):
    """新增按钮：单按钮 或 点击下拉（v1.7.99.7 起，采购/销售合同用下拉）"""
    label = cfg.get("add_btn", f"新增{cfg['title']}")
    href = cfg.get("add_btn_href")
    dropdown = cfg.get("add_btn_dropdown")
    if not dropdown:
        # 单按钮
        # v1.7.99.10 起：如果指定了 add_btn_href，渲染为 <a> 链接（用于跳 app.html 等）
        if href:
            return f'''<a class="btn btn-primary" href="{href}">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            {label}
          </a>'''
        return f'''<button class="btn btn-primary">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            {label}
          </button>'''
    # 按钮下拉
    items = "".join(
        f'<a href="{item.get("href", "#")}"><span class="ico">+</span>{item["label"]}<span class="desc">{item.get("desc", "")}</span></a>'
        for item in dropdown
    )
    return f'''<div class="btn-dropdown" id="addBtnDropdown">
          <button class="btn btn-primary btn-dropdown-toggle" onclick="toggleAddDropdown(event)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            {label}
            <svg class="caret" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div class="btn-dropdown-menu">
            {items}
          </div>
        </div>'''

def filter_fields_html(fields):
    """fields: list of (label, input_html)"""
    return "\n              ".join(
        f'''<div class="cp-filter-item">
                <span class="cp-filter-label">{label}</span>
                {inp}
              </div>'''
        for label, inp in fields
    )

def status_tabs_color(label):
    """v1.7.99.14 状态机颜色编码（5 大类）"""
    # 默认
    if label in ['全部'] or any(x in label for x in ['供应商', '客户分类', '运输方', '批发', '油脂', '粮食', '饲料', '期货', '现货', '基本信息', '资质证书', '认证信息', '操作记录', '周报', '日报', '月报']):
        return None  # 默认色
    # 等待态 = 蓝
    if label.startswith('待') or '待提交' in label or '待审核' in label or '待确认' in label or '待签署' in label or '待入库' in label or '待出库' in label or '待发运' in label or '待提货' in label or '待付款' in label or '待收款' in label or '待退款' in label or '待认领' in label or '待结算' in label or '待缴纳' in label or '待开具' in label or '待开票' in label or '待巡检' in label:
        return '#1e40af'
    # 审批/审核中 = 黄（特殊）
    if '审批中' in label or '审核中' in label:
        return '#a16207'
    # 进行态 = 绿
    if '中' in label and ('执行中' in label or '运输中' in label or '回款中' in label or '运营中' in label or '建设中' in label):
        return '#15803d'
    # 完成态 = 绿
    if label.startswith('已') and any(x in label for x in ['完成', '完结', '结算', '签署', '签收', '入库', '出库', '提货', '付款', '收款', '退款', '回款', '认领', '缴纳', '开具', '开票', '退还', '释放', '审核', '到货', '发运']):
        return '#15803d'
    # 异常态 = 红
    if any(x in label for x in ['驳回', '已拒绝', '已作废', '已取消', '已撤销', '无效', '异常', '故障', '高风险']):
        return '#dc2626'
    # 风险预警 = 黄/橙
    if any(x in label for x in ['中风险', '预警', '价格预警', '库存预警', '合规预警', '回款预警']):
        return '#a16207'
    # 低风险 / 正常 = 绿
    if any(x in label for x in ['低风险', '正常', '启用', '空闲', '已停用', '停用', '占用', '锁定', '冻结', '离线', '在线', '个人黑名单', '企业黑名单']):
        return '#64748b'  # 灰
    return None  # 默认色

def status_tabs_html(tabs):
    """tabs: list of (label, count)
    v1.7.99.14: 状态机完整 — count badge 颜色编码（active tab 强制蓝色保持品牌色）"""
    out = []
    for i, (label, count) in enumerate(tabs):
        is_active = (i == 0)
        color = status_tabs_color(label)
        # active tab 强制蓝色下划线（品牌色）；inactive tab 染色
        if is_active:
            count_style = ''
            tab_style = ''
        elif color:
            count_style = f'color: {color}; font-weight: 600;'
            tab_style = f'color: {color};'
        else:
            count_style = ''
            tab_style = ''
        out.append(
            f'<div class="cp-tab{" active" if i==0 else ""}" style="{tab_style}">{label} <span class="count" style="{count_style}">{count}</span></div>'
        )
    return "\n                ".join(out)

def columns_html(columns):
    """columns: list of column dicts: {name, width, align, action}"""
    out = []
    for col in columns:
        attrs = []
        if col.get("width"):
            attrs.append(f'width: {col["width"]};')
        align = col.get("align", "left")
        if align != "left":
            attrs.append(f"text-align: {align};")
        cls = ""
        if col.get("action"):
            cls = ' class="col-action"'
        # v1.7.99.16k：根据列名"状态"自动加 col-status 类
        elif col.get("name") == "状态" or col.get("name") == "流程状态":
            cls = ' class="col-status"'
        attr_str = f' style="{"".join(attrs)}"' if attrs else ""
        out.append(f"<th{cls}{attr_str}>{col['name']}</th>")
    return "\n                    ".join(out)

def cell_html(value, col):
    """value: 字符串 或 dict (自定义 cell)
    col: 列定义
    """
    align = col.get("align", "left")
    style = f"text-align: {align};" if align != "left" else ""

    # 如果 value 是 dict，自定义 cell
    if isinstance(value, dict):
        ctype = value.get("type")
        v = value.get("v", "")
        if ctype == "progress":
            num = int(v.replace("%", ""))
            warn = " warning" if value.get("warning") and num < 50 else ""
            return f'<td><div class="progress"><div class="progress-bar"><div class="progress-fill{warn}" style="width: {num}%;"></div></div><span class="progress-text">{v}</span></div></td>'
        if ctype == "tag":
            color = value.get("tag_color", "blue")
            return f'<td><span class="tag tag-{color}">{v}</span></td>'
        if ctype == "action":
            links = "".join(value.get("v", []))
            return f'<td class="col-action" style="text-align: right;">{links}</td>'
        if ctype == "status":
            # v1.7.99.12：流程状态（圆点 + 文字，5 状态固定颜色：待提交/审批中/执行中/已完结/驳回）
            # v1.7.99.14：加 col-status 类（让该列 sticky 在操作列左侧）
            color_map = {
                '待提交': '#1e40af',  # blue
                '审批中': '#a16207',  # yellow
                '执行中': '#15803d',  # green
                '已完结': '#15803d',  # green
                '驳回':   '#64748b',  # gray
                '已拒绝': '#64748b',
                '已撤回': '#64748b',
                '已作废': '#64748b',
            }
            color = color_map.get(v, '#64748b')
            return f'<td class="col-status"><span style="display: inline-flex; align-items: center; gap: 6px; color: {color}; font-size: 13px; font-weight: 500;"><span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: {color};"></span>{v}</span></td>'
        if ctype == "actions_by_status":
            # v1.7.99.11：按"流程状态"动态生成操作项
            # v 是状态文字（"待提交"/"审核中"/"执行中"/"驳回"/"已完结"）
            # 默认规则：待提交=查看/编辑/作废；其他=查看
            status = v
            if status == "待提交":
                links = f'<a href="#" data-status="{status}">查看</a><a href="#" data-status="{status}">编辑</a><a href="#" data-status="{status}">作废</a>'
            else:
                links = f'<a href="#" data-status="{status}">查看</a>'
            return f'<td class="col-action" style="text-align: right;">{links}</td>'

    # 普通列
    extra_cls = ""
    if col.get("mono"):
        extra_cls = " col-num"
    style_attr = f' style="{style}"' if style else ""
    cls_attr = f' class="{extra_cls.strip()}"' if extra_cls.strip() else ""
    return f'<td{style_attr}{cls_attr}>{value}</td>'

def row_html(row, columns, detail_file=None):
    cells = []
    for col, val in zip(columns, row):
        cells.append(cell_html(val, col))
    # v1.7.99.11：行支持 data-status 标记 + data-detail-href + cp-row-clickable（CSS 鼠标手势）
    # 行点击 → 跳详情页（由 cp-row-click JS 处理）
    status = None
    for col, val in zip(columns, row):
        if col.get("name") == "操作" and isinstance(val, dict) and val.get("type") == "actions_by_status":
            status = val.get("v")
    data_attrs = []
    if status:
        data_attrs.append(f'data-status="{status}"')
    if detail_file:
        data_attrs.append(f'data-detail-href="./{detail_file}"')
    data_str = (' ' + ' '.join(data_attrs)) if data_attrs else ''
    return f'<tr class="cp-row-clickable"{data_str}>{"".join(cells)}</tr>'

def render_page(cfg):
    """cfg: 配置字典"""
    html = HTML_HEAD
    html = html.replace("{title}", cfg["title"])
    html = html.replace("{bc1}", cfg["bc1"])
    html = html.replace("{bc2}", cfg["bc2"])
    html = html.replace("{add_btn_block}", add_btn_html(cfg))
    # v1.7.99.13：sub_tabs 块只在有内容时输出
    sub_tabs = cfg.get("sub_tabs", [])
    if sub_tabs:
        sub_tabs_block = f'''<div class="tab-action-bar" style="margin-bottom: 0;">
          <div class="tab-action-bar-tabs">
            {sub_tabs_html(sub_tabs, cfg.get("sub_tabs_active", 0))}
          </div>
        </div>'''
    else:
        sub_tabs_block = ''
    html = html.replace("{sub_tabs_block}", sub_tabs_block)
    html = html.replace("{filter_fields_html}", filter_fields_html(cfg["filter_fields"]))
    html = html.replace("{status_tabs_html}", status_tabs_html(cfg["status_tabs"]))
    html = html.replace("{columns_html}", columns_html(cfg["columns"]))
    html = html.replace("{total}", str(cfg.get("total", 36)))
    html = html.replace("{total_pages}", str(cfg.get("total_pages", 4)))

    rows_html = "\n                  ".join(
        row_html(row, cfg["columns"], cfg.get("detail_file")) for row in cfg["mock_rows"]
    )
    html = html.replace("{mock_rows_html}", rows_html)
    return html

# ============================================
# 5 个页面配置
# ============================================

PAGES_CONFIG = {
    "contract-sales.html": {
        "title": "销售合同",
        "bc1": "数字供应链", "bc2": "合同管理",
        "sub_tabs": ["销售框架合同", "销售订单/单批次合同"],
        "sub_tabs_active": 0,
        "add_btn_dropdown": [
            {"label": "新增销售框架合同", "desc": "框架", "href": "./contract-sales-frame-new.html"},
            {"label": "新增销售订单/单批次合同", "desc": "订单/单批次", "href": "./contract-sales-order-new.html"},
        ],
        "filter_fields": [
            ("合同编号", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("客户名称", '<input type="text" class="input" placeholder="请输入客户名称">'),
            ("运输方式", '<select class="select"><option>请选择</option><option>中欧班列-东线</option><option>海运</option><option>公路</option><option>铁路</option></select>'),
            ("业务类型", '<select class="select"><option>请选择</option><option>存货业务</option><option>预付业务</option><option>账期业务</option><option>购销业务</option></select>'),
            ("签订日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("交货起始日", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 28), ("待确认", 3), ("执行中", 21), ("已完结", 3), ("无效", 1)],
        "total": 28, "total_pages": 3,
        "columns": [
            {"name": "合同编号", "width": "18%", "mono": True},
            {"name": "买方", "width": "16%"},
            {"name": "业务类型", "width": "8%"},
            {"name": "运输方式", "width": "10%"},
            {"name": "品名", "width": "8%"},
            {"name": "单价(元/吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "数量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "合同金额(元)", "width": "10%", "align": "right", "mono": True},
            {"name": "回款进度", "width": "8%"},
            {"name": "结算进度", "width": "8%"},
            {"name": "开票进度", "width": "8%"},
            {"name": "已结算金额", "width": "10%", "align": "right", "mono": True},
            {"name": "签订日期", "width": "8%"},
            {"name": "交货期限", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["GTGYL-XSXS-20260127-001", "郑州粮食批发市场", "存货类", "中欧班列-东线", "进口木薯淀粉", "3,500.00", "20,000", "¥ 70,000,000",
             {"v": "60%", "type": "progress", "warning": False},
             {"v": "45%", "type": "progress", "warning": False},
             {"v": "30%", "type": "progress", "warning": True},
             "¥ 31,500,000", "2026-01-27", "2026-12-31",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="./contract-sales-order-detail.html">详情</a>', '<a href="#">编辑</a>']}],
            ["GTGYL-XSXS-20260125-002", "中粮贸易有限公司", "购销类", "海运", "大豆", "4,300.00", "12,000", "¥ 51,600,000",
             {"v": "0%", "type": "progress"}, {"v": "0%", "type": "progress"}, {"v": "0%", "type": "progress"},
             "¥ 0", "2026-01-25", "2026-06-30",
             {"v": "待确认", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">确认</a>']}],
            ["GTGYL-XSXS-20260122-003", "山东金粮农业有限公司", "存货类", "铁路", "玉米", "2,600.00", "15,000", "¥ 39,000,000",
             {"v": "100%", "type": "progress"}, {"v": "100%", "type": "progress"}, {"v": "90%", "type": "progress", "warning": True},
             "¥ 39,000,000", "2025-12-20", "2026-03-31",
             {"v": "已完结", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">查看</a>']}],
            ["GTGYL-XSXS-20260120-004", "河北粮食产业集团", "账期类", "公路", "小麦", "2,550.00", "18,000", "¥ 45,900,000",
             {"v": "80%", "type": "progress"}, {"v": "60%", "type": "progress"}, {"v": "40%", "type": "progress", "warning": True},
             "¥ 27,540,000", "2026-01-20", "2026-09-30",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["GTGYL-XSXS-20260118-005", "河南诚泽运输有限公司", "预付类", "中欧班列-西线", "进口木薯淀粉", "3,450.00", "10,000", "¥ 34,500,000",
             {"v": "20%", "type": "progress", "warning": True}, {"v": "10%", "type": "progress", "warning": True}, {"v": "0%", "type": "progress"},
             "¥ 3,450,000", "2026-01-18", "2026-08-15",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
        ],
    },
    "contract-supplement.html": {
        "title": "补充协议",
        "bc1": "数字供应链", "bc2": "合同管理",
        "sub_tabs": ["采购补充", "销售补充", "运输补充"],
        "filter_fields": [
            ("协议编号", '<input type="text" class="input" placeholder="请输入协议编号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入关联合同编号">'),
            ("协议类型", '<select class="select"><option>请选择</option><option>价格调整</option><option>数量调整</option><option>期限延期</option><option>其他</option></select>'),
            ("对方企业", '<input type="text" class="input" placeholder="请输入企业名称">'),
            ("签订日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("状态", '<select class="select"><option>请选择</option><option>待签</option><option>已签</option><option>执行中</option><option>已完结</option></select>'),
        ],
        "status_tabs": [("全部", 18), ("待签署", 3), ("已签署", 12), ("执行中", 2), ("已完结", 1)],
        "total": 18, "total_pages": 2,
        "columns": [
            {"name": "协议编号", "width": "16%", "mono": True},
            {"name": "关联合同编号", "width": "18%", "mono": True},
            {"name": "协议类型", "width": "10%"},
            {"name": "对方企业", "width": "16%"},
            {"name": "调整内容", "width": "20%"},
            {"name": "原值", "width": "10%", "align": "right", "mono": True},
            {"name": "新值", "width": "10%", "align": "right", "mono": True},
            {"name": "签订日期", "width": "10%"},
            {"name": "生效日期", "width": "10%"},
            {"name": "状态", "width": "8%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["BCXY-20260127-001", "GTGYL-MSXS-20260127-001", "价格调整", "河南诚泽运输有限公司", "单价由 ¥3,400 上调至 ¥3,450",
             "¥ 3,400.00", "¥ 3,450.00", "2026-01-27", "2026-02-01",
             {"v": "已签署", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="./contract-supplement-order-detail.html">详情</a>', '<a href="#">下载</a>']}],
            ["BCXY-20260125-002", "GTGYL-XSXS-20260125-001", "数量调整", "中粮贸易有限公司", "数量由 12,000 吨调整为 15,000 吨",
             "12,000 吨", "15,000 吨", "2026-01-25", "2026-02-05",
             {"v": "已签署", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["BCXY-20260120-003", "GTGYL-MSXS-20260120-001", "期限延期", "河北粮食产业集团", "交货期限延期 30 天",
             "2026-03-31", "2026-04-30", "2026-01-20", "2026-01-22",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["BCXY-20260118-004", "GTGYL-XSXS-20260118-002", "其他", "山东金粮农业有限公司", "增加质量验收条款",
             "—", "见协议", "2026-01-18", "2026-01-20",
             {"v": "已签署", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "contract-shipping.html": {
        "title": "运输合同",
        "bc1": "数字供应链", "bc2": "合同管理",
        "sub_tabs": ["干线运输", "支线运输", "末端配送"],
        "filter_fields": [
            ("合同编号", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("承运商", '<input type="text" class="input" placeholder="请输入承运商名称">'),
            ("运输方式", '<select class="select"><option>请选择</option><option>中欧班列</option><option>海运</option><option>公路</option><option>铁路</option><option>多式联运</option></select>'),
            ("起运地", '<input type="text" class="input" placeholder="请输入起运地">'),
            ("目的地", '<input type="text" class="input" placeholder="请输入目的地">'),
            ("签订日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 12), ("待确认", 2), ("执行中", 8), ("已完结", 1), ("无效", 1)],
        "total": 12, "total_pages": 2,
        "columns": [
            {"name": "合同编号", "width": "16%", "mono": True},
            {"name": "承运商", "width": "16%"},
            {"name": "运输方式", "width": "10%"},
            {"name": "起运地", "width": "10%"},
            {"name": "目的地", "width": "10%"},
            {"name": "运量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "运费(元)", "width": "10%", "align": "right", "mono": True},
            {"name": "已发车次数", "width": "8%", "align": "right", "mono": True},
            {"name": "完成进度", "width": "10%"},
            {"name": "签订日期", "width": "8%"},
            {"name": "有效期至", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["YSHT-20260127-001", "中远海运物流有限公司", "中欧班列", "郑州", "汉堡", "20,000", "¥ 1,200,000", "8",
             {"v": "80%", "type": "progress"}, "2026-01-27", "2026-12-31",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["YSHT-20260125-002", "中国铁路货运公司", "铁路", "郑州北站", "成都", "15,000", "¥ 450,000", "12",
             {"v": "100%", "type": "progress"}, "2026-01-25", "2026-12-31",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["YSHT-20260122-003", "顺丰大件运输", "公路", "郑州", "西安", "8,000", "¥ 280,000", "5",
             {"v": "50%", "type": "progress", "warning": True}, "2026-01-22", "2026-12-31",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["YSHT-20260120-004", "中外运国际物流", "多式联运", "天津港", "郑州", "12,000", "¥ 580,000", "3",
             {"v": "30%", "type": "progress", "warning": True}, "2026-01-20", "2026-12-31",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["YSHT-20260118-005", "德邦物流", "公路", "郑州", "武汉", "5,000", "¥ 150,000", "8",
             {"v": "100%", "type": "progress"}, "2026-01-18", "2026-06-30",
             {"v": "已完结", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">查看</a>']}],
        ],
    },
    "shipment-in.html": {
        "title": "收货管理",
        "bc1": "数字供应链", "bc2": "收发货管理",
        "filter_fields": [
            ("收货单号", '<input type="text" class="input" placeholder="请输入收货单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("供应商", '<input type="text" class="input" placeholder="请输入供应商">'),
            ("收货仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("预计到货日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("运输方式", '<select class="select"><option>请选择</option><option>中欧班列</option><option>海运</option><option>铁路</option><option>公路</option></select>'),
        ],
        "status_tabs": [("全部", 24), ("待确认", 2), ("运输中", 8), ("已到货", 5), ("已入库", 9)],
        "total": 24, "total_pages": 3,
        "columns": [
            {"name": "收货单号", "width": "14%", "mono": True},
            {"name": "关联合同", "width": "14%", "mono": True},
            {"name": "供应商", "width": "14%"},
            {"name": "品名", "width": "8%"},
            {"name": "数量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "收货仓库", "width": "10%"},
            {"name": "运输方式", "width": "8%"},
            {"name": "发车日期", "width": "8%"},
            {"name": "预计到货", "width": "8%"},
            {"name": "实际到货", "width": "8%"},
            {"name": "收货进度", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["SHR-20260127-001", "GTGYL-MSXS-20260127-001", "河南诚泽运输有限公司", "进口木薯淀粉", "20,000", "郑州主仓", "中欧班列-东线", "2026-01-28", "2026-02-15", "2026-02-14",
             {"v": "100%", "type": "progress"},
             {"v": "已入库", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="./shipment-in-detail.html">详情</a>', '<a href="#">收货确认</a>']}],
            ["SHR-20260125-002", "GTGYL-MSXS-20260125-001", "中粮贸易有限公司", "玉米", "15,000", "郑州主仓", "铁路", "2026-01-26", "2026-02-10", "—",
             {"v": "40%", "type": "progress", "warning": True},
             {"v": "运输中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">跟踪</a>']}],
            ["SHR-20260122-003", "GTGYL-MSXS-20260122-001", "河北粮食产业集团", "大豆", "8,000", "青岛前置仓", "海运", "2025-12-20", "2026-02-05", "2026-02-03",
             {"v": "100%", "type": "progress"},
             {"v": "已入库", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">查看</a>']}],
            ["SHR-20260120-004", "GTGYL-XSXS-20260120-001", "山东金粮农业有限公司", "小麦", "12,000", "西安中转仓", "公路", "2026-01-22", "2026-02-01", "2026-01-31",
             {"v": "100%", "type": "progress"},
             {"v": "已到货", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">入库</a>']}],
            ["SHR-20260118-005", "GTGYL-MSXS-20260118-002", "郑州粮食批发市场", "进口木薯淀粉", "10,000", "郑州主仓", "中欧班列-西线", "2026-01-19", "2026-02-08", "—",
             {"v": "60%", "type": "progress"},
             {"v": "运输中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">跟踪</a>']}],
        ],
    },
    "shipment-out.html": {
        "title": "发货管理",
        "bc1": "数字供应链", "bc2": "收发货管理",
        "filter_fields": [
            ("发货单号", '<input type="text" class="input" placeholder="请输入发货单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("客户名称", '<input type="text" class="input" placeholder="请输入客户名称">'),
            ("出库仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("发运日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("运输方式", '<select class="select"><option>请选择</option><option>中欧班列</option><option>海运</option><option>铁路</option><option>公路</option></select>'),
        ],
        "status_tabs": [("全部", 22), ("待发运", 3), ("运输中", 7), ("已签收", 11), ("异常", 1)],
        "total": 22, "total_pages": 3,
        "columns": [
            {"name": "发货单号", "width": "14%", "mono": True},
            {"name": "关联合同", "width": "14%", "mono": True},
            {"name": "客户名称", "width": "12%"},
            {"name": "品名", "width": "8%"},
            {"name": "数量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "出库仓库", "width": "10%"},
            {"name": "运输方式", "width": "8%"},
            {"name": "发运日期", "width": "8%"},
            {"name": "预计签收", "width": "8%"},
            {"name": "实际签收", "width": "8%"},
            {"name": "签收进度", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["SHF-20260127-001", "GTGYL-XSXS-20260127-001", "郑州粮食批发市场", "进口木薯淀粉", "20,000", "郑州主仓", "中欧班列-东线", "2026-01-28", "2026-02-20", "—",
             {"v": "60%", "type": "progress"},
             {"v": "运输中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="./shipment-out-detail.html">详情</a>', '<a href="#">跟踪</a>']}],
            ["SHF-20260125-002", "GTGYL-XSXS-20260125-001", "中粮贸易有限公司", "大豆", "12,000", "青岛前置仓", "海运", "2026-01-26", "2026-02-15", "2026-02-13",
             {"v": "100%", "type": "progress"},
             {"v": "已签收", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">查看</a>']}],
            ["SHF-20260122-003", "GTGYL-XSXS-20260122-001", "山东金粮农业有限公司", "小麦", "15,000", "西安中转仓", "公路", "2026-01-23", "2026-02-01", "2026-01-30",
             {"v": "100%", "type": "progress"},
             {"v": "已签收", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">查看</a>']}],
            ["SHF-20260120-004", "GTGYL-XSXS-20260120-001", "河北粮食产业集团", "玉米", "18,000", "郑州主仓", "铁路", "2026-01-21", "2026-02-05", "—",
             {"v": "70%", "type": "progress"},
             {"v": "运输中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">跟踪</a>']}],
            ["SHF-20260118-005", "GTGYL-XSXS-20260118-002", "河南诚泽运输有限公司", "进口木薯淀粉", "10,000", "郑州主仓", "中欧班列-西线", "2026-01-19", "2026-02-08", "—",
             {"v": "30%", "type": "progress", "warning": True},
             {"v": "待发运", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">发运</a>']}],
        ],
    },
}

# ============================================
# Batch 2 — 货款管理 5 个 + 资金管理 2 个 = 7 个
# ============================================

BATCH2_CONFIG = {
    "payment-list.html": {
        "title": "付款管理",
        "bc1": "数字供应链", "bc2": "货款管理",
        "filter_fields": [
            ("付款单号", '<input type="text" class="input" placeholder="请输入付款单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("收款方", '<input type="text" class="input" placeholder="请输入收款方">'),
            ("付款方式", '<select class="select"><option>请选择</option><option>银行转账</option><option>商业汇票</option><option>信用证</option></select>'),
            ("申请日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("付款类型", '<select class="select"><option>请选择</option><option>货款</option><option>订金</option><option>尾款</option><option>保证金</option></select>'),
        ],
        "status_tabs": [("全部", 18), ("待付款", 4), ("已付款", 13), ("已撤回", 1)],
        "total": 18, "total_pages": 2,
        "columns": [
            {"name": "付款单号", "width": "16%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "收款方", "width": "14%"},
            {"name": "付款金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "付款方式", "width": "8%"},
            {"name": "付款类型", "width": "8%"},
            {"name": "申请日期", "width": "9%"},
            {"name": "付款日期", "width": "9%"},
            {"name": "凭证", "width": "6%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["PAY-20260127-001", "GTGYL-MSXS-20260127-001", "河南诚泽运输有限公司", "¥ 13,600,000", "银行转账", "货款", "2026-01-27", "2026-01-30", "已上传",
             {"v": "已付款", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="./payment-detail.html">详情</a>', '<a href="#">凭证</a>']}],
            ["PAY-20260125-002", "GTGYL-MSXS-20260125-001", "中粮贸易有限公司", "¥ 8,400,000", "商业汇票", "订金", "2026-01-25", "—", "未上传",
             {"v": "待付款", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">付款</a>']}],
            ["PAY-20260122-003", "GTGYL-MSXS-20260122-001", "河北粮食产业集团", "¥ 6,720,000", "银行转账", "尾款", "2026-01-22", "2026-01-25", "已上传",
             {"v": "已付款", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["PAY-20260120-004", "GTGYL-MSXS-20260120-001", "山东金粮农业有限公司", "¥ 9,540,000", "银行转账", "货款", "2026-01-20", "—", "未上传",
             {"v": "待付款", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">付款</a>']}],
        ],
    },
    "refund-list.html": {
        "title": "退款管理",
        "bc1": "数字供应链", "bc2": "货款管理",
        "filter_fields": [
            ("退款单号", '<input type="text" class="input" placeholder="请输入退款单号">'),
            ("原付款单号", '<input type="text" class="input" placeholder="请输入原付款单号">'),
            ("退款方", '<input type="text" class="input" placeholder="请输入退款方">'),
            ("退款原因", '<select class="select"><option>请选择</option><option>数量差异</option><option>质量异议</option><option>合同变更</option><option>其他</option></select>'),
            ("申请日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 6), ("待审核", 2), ("已退款", 3), ("已拒绝", 1)],
        "total": 6, "total_pages": 1,
        "columns": [
            {"name": "退款单号", "width": "16%", "mono": True},
            {"name": "原付款单号", "width": "16%", "mono": True},
            {"name": "退款方", "width": "16%"},
            {"name": "退款金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "退款原因", "width": "12%"},
            {"name": "申请日期", "width": "10%"},
            {"name": "退款日期", "width": "10%"},
            {"name": "状态", "width": "8%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["REF-20260125-001", "PAY-20260120-001", "山东金粮农业有限公司", "¥ 1,500,000", "数量差异", "2026-01-25", "—",
             {"v": "待审核", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="./refund-detail.html">详情</a>', '<a href="#">审核</a>']}],
            ["REF-20260120-002", "PAY-20260118-001", "郑州粮食批发市场", "¥ 800,000", "质量异议", "2026-01-20", "2026-01-23",
             {"v": "已退款", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["REF-20260118-003", "PAY-20260115-001", "河北粮食产业集团", "¥ 350,000", "合同变更", "2026-01-18", "—",
             {"v": "待审核", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">审核</a>']}],
        ],
    },
    "collection-list.html": {
        "title": "收款管理",
        "bc1": "数字供应链", "bc2": "货款管理",
        "filter_fields": [
            ("收款单号", '<input type="text" class="input" placeholder="请输入收款单号">'),
            ("关联销售合同", '<input type="text" class="input" placeholder="请输入销售合同编号">'),
            ("付款方", '<input type="text" class="input" placeholder="请输入付款方">'),
            ("收款方式", '<select class="select"><option>请选择</option><option>银行转账</option><option>商业汇票</option><option>信用证</option></select>'),
            ("应收日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 16), ("待收款", 5), ("已收款", 9), ("已逾期", 2)],
        "total": 16, "total_pages": 2,
        "columns": [
            {"name": "收款单号", "width": "16%", "mono": True},
            {"name": "关联销售合同", "width": "16%", "mono": True},
            {"name": "付款方", "width": "14%"},
            {"name": "应收金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "已收金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "收款方式", "width": "8%"},
            {"name": "应收日期", "width": "9%"},
            {"name": "实收日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["COL-20260127-001", "GTGYL-XSXS-20260127-001", "郑州粮食批发市场", "¥ 14,000,000", "¥ 14,000,000", "银行转账", "2026-01-27", "2026-01-30",
             {"v": "已收款", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["COL-20260125-002", "GTGYL-XSXS-20260125-001", "中粮贸易有限公司", "¥ 10,320,000", "¥ 0", "商业汇票", "2026-01-25", "—",
             {"v": "待收款", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">催收</a>']}],
            ["COL-20260122-003", "GTGYL-XSXS-20260122-001", "山东金粮农业有限公司", "¥ 7,800,000", "¥ 7,800,000", "银行转账", "2026-01-22", "2026-01-25",
             {"v": "已收款", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["COL-20260118-004", "GTGYL-XSXS-20260118-001", "河南诚泽运输有限公司", "¥ 6,900,000", "¥ 0", "银行转账", "2026-01-18", "—",
             {"v": "已逾期", "type": "tag", "tag_color": "red"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">催收</a>']}],
        ],
    },
    "receipt-claim.html": {
        "title": "回款认领",
        "bc1": "数字供应链", "bc2": "货款管理",
        "filter_fields": [
            ("认领单号", '<input type="text" class="input" placeholder="请输入认领单号">'),
            ("到账流水号", '<input type="text" class="input" placeholder="请输入银行流水号">'),
            ("付款方", '<input type="text" class="input" placeholder="请输入付款方名称">'),
            ("到账日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
        ],
        "status_tabs": [("全部", 8), ("待认领", 3), ("已认领", 4), ("已驳回", 1)],
        "total": 8, "total_pages": 1,
        "columns": [
            {"name": "认领单号", "width": "16%", "mono": True},
            {"name": "到账流水号", "width": "16%", "mono": True},
            {"name": "付款方", "width": "14%"},
            {"name": "到账金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "认领金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "到账日期", "width": "10%"},
            {"name": "关联合同", "width": "12%", "mono": True},
            {"name": "状态", "width": "8%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RCL-20260127-001", "BNK-20260127-001", "郑州粮食批发市场", "¥ 14,000,000", "¥ 14,000,000", "2026-01-27", "GTGYL-XSXS-20260127-001",
             {"v": "已认领", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["RCL-20260125-002", "BNK-20260125-001", "中粮贸易有限公司", "¥ 10,320,000", "—", "2026-01-25", "—",
             {"v": "待认领", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">认领</a>']}],
            ["RCL-20260122-003", "BNK-20260122-001", "山东金粮农业有限公司", "¥ 7,800,000", "¥ 7,800,000", "2026-01-22", "GTGYL-XSXS-20260122-001",
             {"v": "已认领", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
        ],
    },
    "receipt-list.html": {
        "title": "回款管理",
        "bc1": "数字供应链", "bc2": "货款管理",
        "filter_fields": [
            ("回款单号", '<input type="text" class="input" placeholder="请输入回款单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("客户名称", '<input type="text" class="input" placeholder="请输入客户名称">'),
            ("回款类型", '<select class="select"><option>请选择</option><option>货款</option><option>订金</option><option>尾款</option></select>'),
            ("应回日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 20), ("回款中", 5), ("已回款", 13), ("已逾期", 2)],
        "total": 20, "total_pages": 2,
        "columns": [
            {"name": "回款单号", "width": "14%", "mono": True},
            {"name": "关联合同", "width": "14%", "mono": True},
            {"name": "客户名称", "width": "12%"},
            {"name": "应回金额(元)", "width": "11%", "align": "right", "mono": True},
            {"name": "已回金额(元)", "width": "11%", "align": "right", "mono": True},
            {"name": "回款进度", "width": "10%"},
            {"name": "应回日期", "width": "8%"},
            {"name": "实回日期", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RCP-20260127-001", "GTGYL-XSXS-20260127-001", "郑州粮食批发市场", "¥ 14,000,000", "¥ 14,000,000",
             {"v": "100%", "type": "progress"}, "2026-01-27", "2026-01-27",
             {"v": "已回款", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["RCP-20260125-002", "GTGYL-XSXS-20260125-001", "中粮贸易有限公司", "¥ 10,320,000", "¥ 0",
             {"v": "0%", "type": "progress"}, "2026-01-25", "—",
             {"v": "回款中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">催收</a>']}],
            ["RCP-20260122-003", "GTGYL-XSXS-20260122-001", "山东金粮农业有限公司", "¥ 7,800,000", "¥ 7,800,000",
             {"v": "100%", "type": "progress"}, "2026-01-22", "2026-01-22",
             {"v": "已回款", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["RCP-20260118-004", "GTGYL-XSXS-20260118-001", "河南诚泽运输有限公司", "¥ 6,900,000", "¥ 0",
             {"v": "20%", "type": "progress", "warning": True}, "2026-01-18", "—",
             {"v": "已逾期", "type": "tag", "tag_color": "red"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">催收</a>']}],
        ],
    },
    "margin-list.html": {
        "title": "保证金管理",
        "bc1": "数字供应链", "bc2": "资金管理",
        "filter_fields": [
            ("保证金单号", '<input type="text" class="input" placeholder="请输入保证金单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("缴纳方", '<input type="text" class="input" placeholder="请输入缴纳方">'),
            ("保证金类型", '<select class="select"><option>请选择</option><option>履约保证金</option><option>质量保证金</option><option>投标保证金</option></select>'),
            ("缴纳日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 12), ("待缴纳", 2), ("已缴纳", 8), ("已退还", 2)],
        "total": 12, "total_pages": 2,
        "columns": [
            {"name": "保证金单号", "width": "16%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "缴纳方", "width": "14%"},
            {"name": "保证金类型", "width": "10%"},
            {"name": "应缴金额(元)", "width": "11%", "align": "right", "mono": True},
            {"name": "已缴金额(元)", "width": "11%", "align": "right", "mono": True},
            {"name": "缴纳日期", "width": "9%"},
            {"name": "退还日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["MRG-20260127-001", "GTGYL-MSXS-20260127-001", "河南诚泽运输有限公司", "履约保证金", "¥ 1,360,000", "¥ 1,360,000", "2026-01-27", "—",
             {"v": "已缴纳", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["MRG-20260125-002", "GTGYL-XSXS-20260125-001", "中粮贸易有限公司", "质量保证金", "¥ 1,032,000", "¥ 0", "—", "—",
             {"v": "待缴纳", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">缴纳</a>']}],
            ["MRG-20260120-003", "GTGYL-MSXS-20260120-001", "河北粮食产业集团", "履约保证金", "¥ 672,000", "¥ 672,000", "2026-01-20", "—",
             {"v": "已缴纳", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
        ],
    },
    "settlement-purchase.html": {
        "title": "采购结算",
        "bc1": "数字供应链", "bc2": "资金管理",
        "filter_fields": [
            ("结算单号", '<input type="text" class="input" placeholder="请输入结算单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("供应商", '<input type="text" class="input" placeholder="请输入供应商">'),
            ("结算方式", '<select class="select"><option>请选择</option><option>按合同结算</option><option>按到货结算</option><option>按入库结算</option></select>'),
            ("结算日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 15), ("待结算", 4), ("已结算", 10), ("已撤回", 1)],
        "total": 15, "total_pages": 2,
        "columns": [
            {"name": "结算单号", "width": "16%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "供应商", "width": "14%"},
            {"name": "结算金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "已付金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "结算方式", "width": "8%"},
            {"name": "申请日期", "width": "9%"},
            {"name": "结算日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["STL-20260127-001", "GTGYL-MSXS-20260127-001", "河南诚泽运输有限公司", "¥ 30,325,800", "¥ 13,600,000", "按入库结算", "2026-01-27", "—",
             {"v": "待结算", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="./settlement-purchase-detail.html">详情</a>', '<a href="#">结算</a>']}],
            ["STL-20260125-002", "GTGYL-MSXS-20260125-001", "中粮贸易有限公司", "¥ 8,400,000", "¥ 8,400,000", "按合同结算", "2026-01-25", "2026-01-28",
             {"v": "已结算", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["STL-20260122-003", "GTGYL-MSXS-20260122-001", "河北粮食产业集团", "¥ 21,000,000", "¥ 6,720,000", "按到货结算", "2026-01-22", "—",
             {"v": "待结算", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">结算</a>']}],
            ["STL-20260120-004", "GTGYL-MSXS-20260120-001", "山东金粮农业有限公司", "¥ 9,540,000", "¥ 9,540,000", "按合同结算", "2026-01-20", "2026-01-23",
             {"v": "已结算", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
        ],
    },
}

# 合并所有 batch 配置
PAGES_CONFIG.update(BATCH2_CONFIG)


# ============================================
# Batch 3 — 仓储管理 12 个
# ============================================

BATCH3_CONFIG = {
    "warehouse-pickup.html": {
        "title": "提货管理", "bc1": "仓储管理", "bc2": "入库管理",
        "filter_fields": [
            ("提货单号", '<input type="text" class="input" placeholder="请输入提货单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("提货方", '<input type="text" class="input" placeholder="请输入提货方">'),
            ("仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option></select>'),
            ("提货日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("运输方式", '<select class="select"><option>请选择</option><option>公路</option><option>铁路</option><option>海运</option></select>'),
        ],
        "status_tabs": [("全部", 14), ("待提货", 3), ("已提货", 9), ("已取消", 2)],
        "total": 14, "total_pages": 2,
        "columns": [
            {"name": "提货单号", "width": "14%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "提货方", "width": "12%"},
            {"name": "品名", "width": "8%"},
            {"name": "数量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "仓库", "width": "10%"},
            {"name": "运输方式", "width": "8%"},
            {"name": "申请日期", "width": "8%"},
            {"name": "提货日期", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["TH-20260127-001", "GTGYL-MSXS-20260127-001", "河南诚泽运输有限公司", "进口木薯淀粉", "20,000", "郑州主仓", "中欧班列-东线", "2026-01-27", "2026-02-01",
             {"v": "已提货", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["TH-20260125-002", "GTGYL-MSXS-20260125-001", "中粮贸易有限公司", "玉米", "15,000", "郑州主仓", "铁路", "2026-01-25", "—",
             {"v": "待提货", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">提货</a>']}],
            ["TH-20260122-003", "GTGYL-MSXS-20260122-001", "河北粮食产业集团", "大豆", "8,000", "青岛前置仓", "海运", "2026-01-22", "2026-01-30",
             {"v": "已提货", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
        ],
    },
    "warehouse-inbound.html": {
        "title": "入库管理", "bc1": "仓储管理", "bc2": "入库管理",
        "filter_fields": [
            ("入库单号", '<input type="text" class="input" placeholder="请输入入库单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("供应商", '<input type="text" class="input" placeholder="请输入供应商">'),
            ("仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option></select>'),
            ("入库日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("品名", '<input type="text" class="input" placeholder="请输入品名">'),
        ],
        "status_tabs": [("全部", 18), ("待入库", 4), ("已入库", 13), ("已取消", 1)],
        "total": 18, "total_pages": 2,
        "columns": [
            {"name": "入库单号", "width": "14%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "供应商", "width": "12%"},
            {"name": "品名", "width": "8%"},
            {"name": "数量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "仓库", "width": "10%"},
            {"name": "货位", "width": "8%"},
            {"name": "申请日期", "width": "8%"},
            {"name": "入库日期", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RK-20260127-001", "GTGYL-MSXS-20260127-001", "河南诚泽运输有限公司", "进口木薯淀粉", "20,000", "郑州主仓", "A-01-03", "2026-01-27", "2026-02-01",
             {"v": "已入库", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="./warehouse-inbound-detail.html">详情</a>', '<a href="#">货位</a>']}],
            ["RK-20260125-002", "GTGYL-MSXS-20260125-001", "中粮贸易有限公司", "玉米", "15,000", "郑州主仓", "B-02-01", "2026-01-25", "—",
             {"v": "待入库", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">入库</a>']}],
            ["RK-20260122-003", "GTGYL-MSXS-20260122-001", "河北粮食产业集团", "大豆", "8,000", "青岛前置仓", "C-01-02", "2026-01-22", "2026-01-30",
             {"v": "已入库", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">货位</a>']}],
        ],
    },
    "warehouse-inventory.html": {
        "title": "库存管理", "bc1": "仓储管理", "bc2": "库存管理",
        "filter_fields": [
            ("库存编号", '<input type="text" class="input" placeholder="请输入库存编号">'),
            ("品名", '<input type="text" class="input" placeholder="请输入品名">'),
            ("仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("货位", '<input type="text" class="input" placeholder="请输入货位">'),
            ("库存数量", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
            ("最近变动", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 32), ("正常", 24), ("预警", 6), ("冻结", 2)],
        "total": 32, "total_pages": 3,
        "columns": [
            {"name": "库存编号", "width": "14%", "mono": True},
            {"name": "品名", "width": "10%"},
            {"name": "仓库", "width": "10%"},
            {"name": "货位", "width": "8%"},
            {"name": "批次号", "width": "12%", "mono": True},
            {"name": "库存数量(吨)", "width": "10%", "align": "right", "mono": True},
            {"name": "锁定数量", "width": "8%", "align": "right", "mono": True},
            {"name": "可用数量", "width": "8%", "align": "right", "mono": True},
            {"name": "入库时间", "width": "8%"},
            {"name": "最近变动", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["KC-20260127-001", "进口木薯淀粉", "郑州主仓", "A-01-03", "BT20260127-001", "20,000", "5,000", "15,000", "2026-02-01", "2026-02-15",
             {"v": "正常", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">锁定</a>']}],
            ["KC-20260125-002", "玉米", "郑州主仓", "B-02-01", "BT20260125-001", "15,000", "0", "15,000", "2026-01-28", "2026-01-28",
             {"v": "正常", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">锁定</a>']}],
            ["KC-20260122-003", "大豆", "青岛前置仓", "C-01-02", "BT20260122-001", "8,000", "2,000", "6,000", "2026-01-30", "2026-02-12",
             {"v": "正常", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">锁定</a>']}],
            ["KC-20260120-004", "小麦", "西安中转仓", "D-03-01", "BT20260120-001", "12,000", "0", "12,000", "2026-01-22", "2026-02-10",
             {"v": "预警", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">补货</a>']}],
        ],
    },
    "warehouse-outbound.html": {
        "title": "出库管理", "bc1": "仓储管理", "bc2": "出库管理",
        "filter_fields": [
            ("出库单号", '<input type="text" class="input" placeholder="请输入出库单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("客户名称", '<input type="text" class="input" placeholder="请输入客户名称">'),
            ("仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option></select>'),
            ("出库日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("运输方式", '<select class="select"><option>请选择</option><option>公路</option><option>铁路</option><option>海运</option></select>'),
        ],
        "status_tabs": [("全部", 14), ("待出库", 3), ("已出库", 10), ("已取消", 1)],
        "total": 14, "total_pages": 2,
        "columns": [
            {"name": "出库单号", "width": "14%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "客户名称", "width": "12%"},
            {"name": "品名", "width": "8%"},
            {"name": "数量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "仓库", "width": "10%"},
            {"name": "货位", "width": "8%"},
            {"name": "申请日期", "width": "8%"},
            {"name": "出库日期", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["CK-20260127-001", "GTGYL-XSXS-20260127-001", "郑州粮食批发市场", "进口木薯淀粉", "20,000", "郑州主仓", "A-01-03", "2026-01-27", "2026-01-28",
             {"v": "已出库", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="./warehouse-outbound-detail.html">详情</a>', '<a href="#">凭证</a>']}],
            ["CK-20260125-002", "GTGYL-XSXS-20260125-001", "中粮贸易有限公司", "大豆", "12,000", "青岛前置仓", "C-01-02", "2026-01-25", "2026-01-26",
             {"v": "已出库", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
        ],
    },
    "warehouse-release.html": {
        "title": "释放管理", "bc1": "仓储管理", "bc2": "库存管理",
        "filter_fields": [
            ("释放单号", '<input type="text" class="input" placeholder="请输入释放单号">'),
            ("关联库存", '<input type="text" class="input" placeholder="请输入库存编号">'),
            ("申请方", '<input type="text" class="input" placeholder="请输入申请方">'),
            ("仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option></select>'),
            ("申请日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("释放类型", '<select class="select"><option>请选择</option><option>质押释放</option><option>锁定释放</option><option>冻结解除</option></select>'),
        ],
        "status_tabs": [("全部", 6), ("待审核", 2), ("已释放", 3), ("已拒绝", 1)],
        "total": 6, "total_pages": 1,
        "columns": [
            {"name": "释放单号", "width": "16%", "mono": True},
            {"name": "关联库存", "width": "16%", "mono": True},
            {"name": "申请方", "width": "12%"},
            {"name": "释放类型", "width": "10%"},
            {"name": "释放数量(吨)", "width": "10%", "align": "right", "mono": True},
            {"name": "仓库", "width": "10%"},
            {"name": "申请日期", "width": "10%"},
            {"name": "释放日期", "width": "10%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["SF-20260127-001", "KC-20260127-001", "河南诚泽运输有限公司", "质押释放", "5,000", "郑州主仓", "2026-01-27", "2026-01-30",
             {"v": "已释放", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["SF-20260125-002", "KC-20260122-001", "中粮贸易有限公司", "锁定释放", "2,000", "青岛前置仓", "2026-01-25", "—",
             {"v": "待审核", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">审核</a>']}],
        ],
    },
    "warehouse-category.html": {
        "title": "品类管理", "bc1": "仓储管理", "bc2": "基础数据",
        "filter_fields": [
            ("品类编号", '<input type="text" class="input" placeholder="请输入品类编号">'),
            ("品类名称", '<input type="text" class="input" placeholder="请输入品类名称">'),
            ("上级品类", '<input type="text" class="input" placeholder="请输入上级品类">'),
            ("品类类型", '<select class="select"><option>请选择</option><option>粮食类</option><option>油脂类</option><option>饲料类</option><option>其他</option></select>'),
            ("更新时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("状态", '<select class="select"><option>请选择</option><option>启用</option><option>停用</option></select>'),
        ],
        "status_tabs": [("全部", 18), ("启用", 15), ("停用", 3)],
        "total": 18, "total_pages": 2,
        "columns": [
            {"name": "品类编号", "width": "14%", "mono": True},
            {"name": "品类名称", "width": "14%"},
            {"name": "品类类型", "width": "10%"},
            {"name": "上级品类", "width": "12%"},
            {"name": "品类描述", "width": "16%"},
            {"name": "关联仓库", "width": "8%"},
            {"name": "更新时间", "width": "10%"},
            {"name": "创建人", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["CAT-001", "进口木薯淀粉", "粮食类", "—", "东南亚进口优质木薯淀粉", "郑州主仓", "2026-01-15", "管理员", "启用",
             {"v": "启用", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["CAT-002", "玉米", "粮食类", "—", "国产优质玉米", "郑州主仓", "2026-01-15", "管理员", "启用",
             {"v": "启用", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["CAT-003", "大豆", "粮食类", "—", "东北非转基因大豆", "青岛前置仓", "2026-01-15", "管理员", "启用",
             {"v": "启用", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["CAT-004", "小麦", "粮食类", "—", "河南优质小麦", "西安中转仓", "2025-12-20", "管理员", "停用",
             {"v": "停用", "type": "tag", "tag_color": "gray"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
        ],
    },
    "warehouse-market.html": {
        "title": "行情管理", "bc1": "仓储管理", "bc2": "基础数据",
        "filter_fields": [
            ("行情编号", '<input type="text" class="input" placeholder="请输入行情编号">'),
            ("品名", '<input type="text" class="input" placeholder="请输入品名">'),
            ("行情类型", '<select class="select"><option>请选择</option><option>现货</option><option>期货</option><option>批发</option></select>'),
            ("价格区间", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
            ("更新日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("数据来源", '<select class="select"><option>请选择</option><option>系统采集</option><option>人工录入</option><option>第三方接口</option></select>'),
        ],
        "status_tabs": [("全部", 26), ("粮食", 14), ("油脂", 6), ("饲料", 6)],
        "total": 26, "total_pages": 3,
        "columns": [
            {"name": "行情编号", "width": "12%", "mono": True},
            {"name": "品名", "width": "10%"},
            {"name": "行情类型", "width": "8%"},
            {"name": "现价(元/吨)", "width": "10%", "align": "right", "mono": True},
            {"name": "开盘价", "width": "10%", "align": "right", "mono": True},
            {"name": "最高价", "width": "10%", "align": "right", "mono": True},
            {"name": "最低价", "width": "10%", "align": "right", "mono": True},
            {"name": "涨跌幅", "width": "8%", "align": "right", "mono": True},
            {"name": "数据来源", "width": "10%"},
            {"name": "更新时间", "width": "10%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["HQ-20260127-001", "进口木薯淀粉", "现货", "3,450", "3,420", "3,480", "3,400", "+0.88%", "系统采集", "2026-01-27 14:30",
             {"type": "action", "v": ['<a href="./market-price-detail.html">详情</a>', '<a href="#">走势</a>']}],
            ["HQ-20260127-002", "玉米", "现货", "2,650", "2,620", "2,680", "2,600", "+1.15%", "系统采集", "2026-01-27 14:30",
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">走势</a>']}],
            ["HQ-20260127-003", "大豆", "现货", "4,300", "4,250", "4,350", "4,200", "+1.18%", "系统采集", "2026-01-27 14:30",
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">走势</a>']}],
        ],
    },
    "warehouse-video.html": {
        "title": "视频监控", "bc1": "仓储管理", "bc2": "智能监控",
        "filter_fields": [
            ("摄像头编号", '<input type="text" class="input" placeholder="请输入摄像头编号">'),
            ("所属仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("安装位置", '<input type="text" class="input" placeholder="请输入位置">'),
            ("摄像头类型", '<select class="select"><option>请选择</option><option>枪机</option><option>球机</option><option>半球</option></select>'),
            ("在线状态", '<select class="select"><option>请选择</option><option>在线</option><option>离线</option><option>故障</option></select>'),
            ("更新时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 24), ("在线", 20), ("离线", 3), ("故障", 1)],
        "total": 24, "total_pages": 3,
        "columns": [
            {"name": "摄像头编号", "width": "12%", "mono": True},
            {"name": "所属仓库", "width": "10%"},
            {"name": "安装位置", "width": "14%"},
            {"name": "摄像头类型", "width": "8%"},
            {"name": "分辨率", "width": "8%"},
            {"name": "在线状态", "width": "8%"},
            {"name": "存储天数", "width": "8%"},
            {"name": "最近心跳", "width": "12%"},
            {"name": "IP地址", "width": "12%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["CAM-001", "郑州主仓", "A 区入口", "枪机", "1080P", "在线", "30 天", "2026-01-27 15:20:15", "192.168.1.101",
             {"v": "在线", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">直播</a>']}],
            ["CAM-002", "郑州主仓", "B 区货架", "球机", "4K", "在线", "30 天", "2026-01-27 15:20:18", "192.168.1.102",
             {"v": "在线", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">直播</a>']}],
            ["CAM-003", "青岛前置仓", "C 区出口", "半球", "1080P", "离线", "30 天", "2026-01-25 10:15:32", "192.168.2.101",
             {"v": "离线", "type": "tag", "tag_color": "gray"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">诊断</a>']}],
        ],
    },
    "warehouse-patrol.html": {
        "title": "巡检管理", "bc1": "仓储管理", "bc2": "智能监控",
        "filter_fields": [
            ("巡检单号", '<input type="text" class="input" placeholder="请输入巡检单号">'),
            ("所属仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("巡检人员", '<input type="text" class="input" placeholder="请输入人员">'),
            ("巡检类型", '<select class="select"><option>请选择</option><option>日常巡检</option><option>定期巡检</option><option>专项巡检</option></select>'),
            ("巡检日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("巡检结果", '<select class="select"><option>请选择</option><option>正常</option><option>异常</option></select>'),
        ],
        "status_tabs": [("全部", 16), ("待巡检", 4), ("已完成", 10), ("异常", 2)],
        "total": 16, "total_pages": 2,
        "columns": [
            {"name": "巡检单号", "width": "14%", "mono": True},
            {"name": "所属仓库", "width": "10%"},
            {"name": "巡检类型", "width": "10%"},
            {"name": "巡检人员", "width": "10%"},
            {"name": "巡检点位", "width": "8%"},
            {"name": "巡检项目", "width": "14%"},
            {"name": "计划日期", "width": "8%"},
            {"name": "完成日期", "width": "8%"},
            {"name": "巡检结果", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["XJ-20260127-001", "郑州主仓", "日常巡检", "张安全", "12 个", "温湿度/消防/货位", "2026-01-27", "2026-01-27 10:30", "正常", "已完成",
             {"v": "已完成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">报告</a>']}],
            ["XJ-20260126-002", "青岛前置仓", "专项巡检", "李安全", "8 个", "冷链/密封", "2026-01-26", "2026-01-26 14:20", "正常", "已完成",
             {"v": "已完成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">报告</a>']}],
            ["XJ-20260125-003", "西安中转仓", "定期巡检", "王安全", "10 个", "消防/安全", "2026-01-25", "2026-01-25 16:00", "异常", "异常",
             {"v": "异常", "type": "tag", "tag_color": "red"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">整改</a>']}],
        ],
    },
    "warehouse-system.html": {
        "title": "系统监控", "bc1": "仓储管理", "bc2": "智能监控",
        "filter_fields": [
            ("设备编号", '<input type="text" class="input" placeholder="请输入设备编号">'),
            ("所属仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("设备类型", '<select class="select"><option>请选择</option><option>温湿度传感器</option><option>烟雾报警器</option><option>门禁</option><option>PLC 控制器</option></select>'),
            ("运行状态", '<select class="select"><option>请选择</option><option>正常</option><option>预警</option><option>故障</option><option>离线</option></select>'),
            ("安装位置", '<input type="text" class="input" placeholder="请输入位置">'),
            ("更新时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 32), ("正常", 26), ("预警", 4), ("故障", 2)],
        "total": 32, "total_pages": 3,
        "columns": [
            {"name": "设备编号", "width": "12%", "mono": True},
            {"name": "所属仓库", "width": "10%"},
            {"name": "设备类型", "width": "10%"},
            {"name": "安装位置", "width": "14%"},
            {"name": "实时数据", "width": "10%"},
            {"name": "运行状态", "width": "8%"},
            {"name": "最后心跳", "width": "12%"},
            {"name": "固件版本", "width": "8%"},
            {"name": "IP地址", "width": "12%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["DEV-001", "郑州主仓", "温湿度传感器", "A 区 01", "23.5°C / 65%RH", "正常", "2026-01-27 15:25:30", "v2.1.5", "192.168.1.50",
             {"v": "正常", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">日志</a>']}],
            ["DEV-002", "郑州主仓", "烟雾报警器", "B 区 02", "正常", "正常", "2026-01-27 15:25:25", "v1.8.2", "192.168.1.51",
             {"v": "正常", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">日志</a>']}],
            ["DEV-003", "青岛前置仓", "门禁", "正门", "常闭", "预警", "2026-01-26 12:10:05", "v3.0.1", "192.168.2.50",
             {"v": "预警", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">处理</a>']}],
        ],
    },
    "warehouse-point.html": {
        "title": "货位管理", "bc1": "仓储管理", "bc2": "基础数据",
        "filter_fields": [
            ("货位编号", '<input type="text" class="input" placeholder="请输入货位编号">'),
            ("所属仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("区域", '<select class="select"><option>请选择</option><option>A 区</option><option>B 区</option><option>C 区</option><option>D 区</option></select>'),
            ("货架", '<input type="text" class="input" placeholder="请输入货架号">'),
            ("状态", '<select class="select"><option>请选择</option><option>空闲</option><option>占用</option><option>锁定</option></select>'),
            ("更新日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 86), ("空闲", 52), ("占用", 30), ("锁定", 4)],
        "total": 86, "total_pages": 9,
        "columns": [
            {"name": "货位编号", "width": "12%", "mono": True},
            {"name": "所属仓库", "width": "10%"},
            {"name": "区域", "width": "8%"},
            {"name": "货架", "width": "8%"},
            {"name": "层数", "width": "6%"},
            {"name": "货位类型", "width": "10%"},
            {"name": "容量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "当前库存", "width": "10%", "align": "right", "mono": True},
            {"name": "更新时间", "width": "10%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["HW-A01-03", "郑州主仓", "A 区", "A-01", "3", "标准", "100", "20", "2026-01-27", "占用",
             {"v": "占用", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["HW-A02-01", "郑州主仓", "A 区", "A-02", "1", "标准", "100", "0", "2026-01-27", "空闲",
             {"v": "空闲", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["HW-B01-05", "郑州主仓", "B 区", "B-01", "5", "重型", "200", "150", "2026-01-26", "占用",
             {"v": "占用", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
        ],
    },
    "warehouse-warehouse.html": {
        "title": "仓库管理", "bc1": "仓储管理", "bc2": "基础数据",
        "filter_fields": [
            ("仓库编号", '<input type="text" class="input" placeholder="请输入仓库编号">'),
            ("仓库名称", '<input type="text" class="input" placeholder="请输入仓库名称">'),
            ("仓库类型", '<select class="select"><option>请选择</option><option>主仓</option><option>前置仓</option><option>中转仓</option><option>监管仓</option></select>'),
            ("所在地区", '<input type="text" class="input" placeholder="请输入地区">'),
            ("仓库状态", '<select class="select"><option>请选择</option><option>运营中</option><option>建设中</option><option>已停用</option></select>'),
            ("启用日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 8), ("运营中", 5), ("建设中", 2), ("已停用", 1)],
        "total": 8, "total_pages": 1,
        "columns": [
            {"name": "仓库编号", "width": "14%", "mono": True},
            {"name": "仓库名称", "width": "14%"},
            {"name": "仓库类型", "width": "10%"},
            {"name": "所在地区", "width": "12%"},
            {"name": "仓库面积(㎡)", "width": "12%", "align": "right", "mono": True},
            {"name": "货位数", "width": "8%", "align": "right", "mono": True},
            {"name": "负责人", "width": "10%"},
            {"name": "启用日期", "width": "10%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["WH-001", "郑州主仓", "主仓", "河南郑州", "50,000", "120", "王经理", "2025-06-01", "运营中",
             {"v": "运营中", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["WH-002", "青岛前置仓", "前置仓", "山东青岛", "20,000", "60", "李经理", "2025-08-15", "运营中",
             {"v": "运营中", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["WH-003", "西安中转仓", "中转仓", "陕西西安", "15,000", "40", "张经理", "2025-10-20", "运营中",
             {"v": "运营中", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["WH-004", "天津北仓", "主仓", "天津", "—", "—", "—", "2026-03-01", "建设中",
             {"v": "建设中", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
        ],
    },
}

PAGES_CONFIG.update(BATCH3_CONFIG)


# ============================================
# Batch 4 — 数字供应链结算剩余 4 + 货转 1 + 准入 2 + 预警 3 + 业务线 1 + 账户 2 + 报表 7 = 20 个
# ============================================

BATCH4_CONFIG = {
    # 数字供应链 — 资金结算
    "settlement-sales.html": {
        "title": "销售结算", "bc1": "数字供应链", "bc2": "资金管理",
        "filter_fields": [
            ("结算单号", '<input type="text" class="input" placeholder="请输入结算单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("客户名称", '<input type="text" class="input" placeholder="请输入客户名称">'),
            ("结算方式", '<select class="select"><option>请选择</option><option>按合同结算</option><option>按到货结算</option><option>按签收结算</option></select>'),
            ("结算日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 14), ("待结算", 3), ("已结算", 10), ("已撤回", 1)],
        "total": 14, "total_pages": 2,
        "columns": [
            {"name": "结算单号", "width": "16%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "客户名称", "width": "14%"},
            {"name": "结算金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "已收金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "结算方式", "width": "8%"},
            {"name": "申请日期", "width": "9%"},
            {"name": "结算日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["STS-20260127-001", "GTGYL-XSXS-20260127-001", "郑州粮食批发市场", "¥ 70,000,000", "¥ 14,000,000", "按签收结算", "2026-01-27", "—",
             {"v": "待结算", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">结算</a>']}],
            ["STS-20260125-002", "GTGYL-XSXS-20260125-001", "中粮贸易有限公司", "¥ 51,600,000", "¥ 10,320,000", "按合同结算", "2026-01-25", "2026-01-28",
             {"v": "已结算", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
            ["STS-20260122-003", "GTGYL-XSXS-20260122-001", "山东金粮农业有限公司", "¥ 39,000,000", "¥ 7,800,000", "按到货结算", "2026-01-22", "—",
             {"v": "待结算", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">结算</a>']}],
        ],
    },
    "invoice.html": {
        "title": "发票管理", "bc1": "数字供应链", "bc2": "资金管理",
        "filter_fields": [
            ("发票号", '<input type="text" class="input" placeholder="请输入发票号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("开票方", '<input type="text" class="input" placeholder="请输入开票方">'),
            ("发票类型", '<select class="select"><option>请选择</option><option>增值税专用</option><option>增值税普通</option></select>'),
            ("开票日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 18), ("待开票", 4), ("已开票", 13), ("已作废", 1)],
        "total": 18, "total_pages": 2,
        "columns": [
            {"name": "发票号", "width": "16%", "mono": True},
            {"name": "关联合同", "width": "16%", "mono": True},
            {"name": "开票方", "width": "14%"},
            {"name": "发票类型", "width": "10%"},
            {"name": "开票金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "税额(元)", "width": "10%", "align": "right", "mono": True},
            {"name": "申请日期", "width": "9%"},
            {"name": "开票日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["FP-20260127-001", "GTGYL-XSXS-20260127-001", "郑州粮食批发市场", "增值税专用", "¥ 70,000,000", "¥ 9,100,000", "2026-01-27", "2026-01-28",
             {"v": "已开票", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["FP-20260125-002", "GTGYL-XSXS-20260125-001", "中粮贸易有限公司", "增值税专用", "¥ 51,600,000", "¥ 6,708,000", "2026-01-25", "2026-01-27",
             {"v": "已开票", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "market-price.html": {
        "title": "行情管理", "bc1": "数字供应链", "bc2": "市场行情",
        "filter_fields": [
            ("行情编号", '<input type="text" class="input" placeholder="请输入行情编号">'),
            ("品名", '<input type="text" class="input" placeholder="请输入品名">'),
            ("行情类型", '<select class="select"><option>请选择</option><option>现货</option><option>期货</option><option>批发</option></select>'),
            ("价格区间", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
            ("更新日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("数据来源", '<select class="select"><option>请选择</option><option>系统采集</option><option>人工录入</option><option>第三方接口</option></select>'),
        ],
        "status_tabs": [("全部", 32), ("现货", 18), ("期货", 8), ("批发", 6)],
        "total": 32, "total_pages": 3,
        "columns": [
            {"name": "行情编号", "width": "12%", "mono": True},
            {"name": "品名", "width": "10%"},
            {"name": "行情类型", "width": "8%"},
            {"name": "现价(元/吨)", "width": "10%", "align": "right", "mono": True},
            {"name": "开盘价", "width": "10%", "align": "right", "mono": True},
            {"name": "最高价", "width": "10%", "align": "right", "mono": True},
            {"name": "最低价", "width": "10%", "align": "right", "mono": True},
            {"name": "涨跌幅", "width": "8%", "align": "right", "mono": True},
            {"name": "数据来源", "width": "10%"},
            {"name": "更新时间", "width": "10%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["HQ-20260127-001", "进口木薯淀粉", "现货", "3,450", "3,420", "3,480", "3,400", "+0.88%", "系统采集", "2026-01-27 14:30",
             {"type": "action", "v": ['<a href="./market-price-detail.html">详情</a>', '<a href="#">走势</a>']}],
            ["HQ-20260127-002", "玉米", "现货", "2,650", "2,620", "2,680", "2,600", "+1.15%", "系统采集", "2026-01-27 14:30",
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">走势</a>']}],
            ["HQ-20260127-003", "大豆", "期货", "4,300", "4,250", "4,350", "4,200", "+1.18%", "第三方接口", "2026-01-27 14:30",
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">走势</a>']}],
        ],
    },
    "bond-letter.html": {
        "title": "保函管理", "bc1": "数字供应链", "bc2": "资金管理",
        "filter_fields": [
            ("保函编号", '<input type="text" class="input" placeholder="请输入保函编号">'),
            ("申请方", '<input type="text" class="input" placeholder="请输入申请方">'),
            ("受益人", '<input type="text" class="input" placeholder="请输入受益人">'),
            ("保函类型", '<select class="select"><option>请选择</option><option>履约保函</option><option>投标保函</option><option>预付款保函</option><option>质量保函</option></select>'),
            ("申请日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("金额范围", '<input type="text" class="input" placeholder="最小 ~ 最大">'),
        ],
        "status_tabs": [("全部", 8), ("待开具", 2), ("已开具", 5), ("已撤销", 1)],
        "total": 8, "total_pages": 1,
        "columns": [
            {"name": "保函编号", "width": "16%", "mono": True},
            {"name": "申请方", "width": "14%"},
            {"name": "受益人", "width": "14%"},
            {"name": "保函类型", "width": "10%"},
            {"name": "保函金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "生效日期", "width": "9%"},
            {"name": "到期日期", "width": "9%"},
            {"name": "申请日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["BH-20260127-001", "河南诚泽运输有限公司", "中粮贸易有限公司", "履约保函", "¥ 5,000,000", "2026-01-27", "2027-01-26", "2026-01-27",
             {"v": "已开具", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="./bond-letter-detail.html">详情</a>', '<a href="#">下载</a>']}],
            ["BH-20260125-002", "河北粮食产业集团", "山东金粮农业有限公司", "投标保函", "¥ 1,500,000", "2026-01-25", "2026-04-25", "2026-01-25",
             {"v": "已开具", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    # 数字供应链 — 货转
    "goods-transfer.html": {
        "title": "货转管理", "bc1": "数字供应链", "bc2": "收发货管理",
        "filter_fields": [
            ("货转单号", '<input type="text" class="input" placeholder="请输入货转单号">'),
            ("关联合同", '<input type="text" class="input" placeholder="请输入合同编号">'),
            ("转出方", '<input type="text" class="input" placeholder="请输入转出方">'),
            ("转入方", '<input type="text" class="input" placeholder="请输入转入方">'),
            ("货转日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("货转原因", '<select class="select"><option>请选择</option><option>调配</option><option>应急</option><option>退货</option><option>其他</option></select>'),
        ],
        "status_tabs": [("全部", 10), ("待审核", 2), ("已审核", 7), ("已拒绝", 1)],
        "total": 10, "total_pages": 1,
        "columns": [
            {"name": "货转单号", "width": "14%", "mono": True},
            {"name": "关联合同", "width": "14%", "mono": True},
            {"name": "转出方", "width": "12%"},
            {"name": "转入方", "width": "12%"},
            {"name": "品名", "width": "8%"},
            {"name": "数量(吨)", "width": "8%", "align": "right", "mono": True},
            {"name": "货转原因", "width": "8%"},
            {"name": "申请日期", "width": "8%"},
            {"name": "货转日期", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["HZ-20260127-001", "GTGYL-MSXS-20260127-001", "河南诚泽运输有限公司", "中粮贸易有限公司", "进口木薯淀粉", "5,000", "调配", "2026-01-27", "2026-01-30",
             {"v": "已审核", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="./goods-transfer-up-detail.html">详情</a>', '<a href="#">凭证</a>']}],
            ["HZ-20260125-002", "GTGYL-MSXS-20260125-001", "河北粮食产业集团", "山东金粮农业有限公司", "玉米", "3,000", "应急", "2026-01-25", "2026-01-28",
             {"v": "已审核", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">凭证</a>']}],
        ],
    },
    # 准入管理
    "project-list.html": {
        "title": "项目列表", "bc1": "准入管理", "bc2": "项目准入",
        "add_btn": "新增立项申请",
        "add_btn_href": "./project-apply.html",
        "filter_fields": [
            ("立项申请编号", '<input type="text" class="input" placeholder="请输入立项申请编号">'),
            ("项目名称", '<input type="text" class="input" placeholder="请输入项目名称">'),
            ("业务类型", '<select class="select"><option>请选择</option><option>存货业务</option><option>预付业务</option><option>账期业务</option><option>购销业务</option></select>'),
            ("货物品类", '<select class="select"><option>请选择</option><option>玉米</option><option>糖粉</option><option>木薯淀粉</option><option>谷物</option><option>淀粉制品</option></select>'),
            ("业务结束日期", '<input type="text" class="input" placeholder="业务结束日期">'),
            ("申请时间", '<input type="text" class="input" placeholder="请选择申请时间">'),
            ("业务负责人", '<select class="select"><option>请选择业务负责人</option><option>张三</option><option>李四</option><option>王五</option></select>'),
        ],
        "status_tabs": [("全部", 100), ("待提交", 12), ("审批中", 8), ("执行中", 76), ("已完结", 3), ("驳回", 1)],
        "total": 400, "total_pages": 80,
        "detail_file": "project-detail.html",
        "columns": [
            {"name": "立项申请编号", "width": "10%", "mono": True},
            {"name": "项目名称", "width": "13%"},
            {"name": "上游企业", "width": "9%"},
            {"name": "下游企业", "width": "9%"},
            {"name": "业务类型", "width": "7%"},
            {"name": "货物品类", "width": "8%"},
            {"name": "总投资金额(万元)", "width": "10%", "align": "right", "mono": True},
            {"name": "业务周期", "width": "11%"},
            {"name": "立项日期", "width": "8%"},
            {"name": "业务负责人", "width": "6%"},
            {"name": "申请时间", "width": "10%", "mono": True},
            {"name": "流程状态", "width": "8%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["LX20260122001", "木薯淀粉存货类供应链项目", "XXXXX-A", "DDDDD-B", "存货业务", "淀粉制品", "10,000.00", "2026-01-01 ~ 2026-12-31", "2023-09-17", "张三", "2023-09-17 20:11:22", {"type": "status", "v": "审批中"}, {"type": "actions_by_status", "v": "审批中"}],
            ["LX20260122002", "玉米预付业务供应链项目", "YYYYY-C", "EEEEE-D", "预付业务", "玉米", "8,500.00", "2026-02-15 ~ 2026-12-31", "2023-09-20", "李四", "2023-09-20 14:32:11", {"type": "status", "v": "执行中"}, {"type": "actions_by_status", "v": "执行中"}],
            ["LX20260122003", "糖粉账期业务项目", "ZZZZZ-E", "FFFFF-F", "账期业务", "糖粉", "12,000.00", "2026-03-01 ~ 2027-02-28", "2023-10-05", "王五", "2023-10-05 09:15:48", {"type": "status", "v": "待提交"}, {"type": "actions_by_status", "v": "待提交"}],
            ["LX20260122004", "谷物购销业务项目", "AAAAA-G", "BBBBB-H", "购销业务", "谷物", "15,500.00", "2026-03-10 ~ 2026-12-31", "2023-10-12", "张三", "2023-10-12 16:42:33", {"type": "status", "v": "审批中"}, {"type": "actions_by_status", "v": "审批中"}],
            ["LX20260122005", "淀粉制品存货类项目", "CCCCC-I", "DDDDD-J", "存货业务", "淀粉制品", "9,800.00", "2026-04-01 ~ 2026-12-31", "2023-10-25", "李四", "2023-10-25 11:23:09", {"type": "status", "v": "执行中"}, {"type": "actions_by_status", "v": "执行中"}],
            ["LX20260122006", "玉米预付业务项目", "EEEEE-K", "FFFFF-L", "预付业务", "玉米", "11,200.00", "2026-04-15 ~ 2027-04-14", "2023-11-02", "王五", "2023-11-02 13:55:27", {"type": "status", "v": "驳回"}, {"type": "actions_by_status", "v": "驳回"}],
            ["LX20260122007", "木薯淀粉存货类项目", "GGGGG-M", "HHHHH-N", "存货业务", "淀粉制品", "13,400.00", "2026-05-01 ~ 2027-04-30", "2023-11-15", "张三", "2023-11-15 10:08:51", {"type": "status", "v": "执行中"}, {"type": "actions_by_status", "v": "执行中"}],
            ["LX20260122008", "糖粉账期业务项目", "IIIII-O", "JJJJJ-P", "账期业务", "糖粉", "7,600.00", "2026-05-20 ~ 2027-05-19", "2023-12-01", "李四", "2023-12-01 15:36:42", {"type": "status", "v": "审批中"}, {"type": "actions_by_status", "v": "审批中"}],
            ["LX20260122009", "谷物购销业务项目", "KKKKK-Q", "LLLLL-R", "购销业务", "谷物", "16,800.00", "2026-06-01 ~ 2027-05-31", "2023-12-18", "王五", "2023-12-18 09:42:15", {"type": "status", "v": "已完结"}, {"type": "actions_by_status", "v": "已完结"}],
            ["LX20260122010", "淀粉制品存货类项目", "MMMMM-S", "NNNNN-T", "存货业务", "淀粉制品", "10,500.00", "2026-06-15 ~ 2027-06-14", "2024-01-05", "张三", "2024-01-05 14:21:38", {"type": "status", "v": "待提交"}, {"type": "actions_by_status", "v": "待提交"}],
        ],
    },
    # 预警中心
    "warning-list.html": {
        "title": "预警列表", "bc1": "预警中心", "bc2": "预警管理",
        "filter_fields": [
            ("预警编号", '<input type="text" class="input" placeholder="请输入预警编号">'),
            ("预警类型", '<select class="select"><option>请选择</option><option>价格预警</option><option>库存预警</option><option>回款预警</option><option>合规预警</option></select>'),
            ("预警对象", '<input type="text" class="input" placeholder="请输入对象">'),
            ("风险等级", '<select class="select"><option>请选择</option><option>高</option><option>中</option><option>低</option></select>'),
            ("预警时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("处理状态", '<select class="select"><option>请选择</option><option>待处理</option><option>处理中</option><option>已处理</option></select>'),
        ],
        "status_tabs": [("全部", 18), ("高风险", 3), ("中风险", 8), ("低风险", 7)],
        "total": 18, "total_pages": 2,
        "columns": [
            {"name": "预警编号", "width": "14%", "mono": True},
            {"name": "预警类型", "width": "10%"},
            {"name": "预警对象", "width": "18%"},
            {"name": "预警内容", "width": "20%"},
            {"name": "风险等级", "width": "8%"},
            {"name": "预警时间", "width": "10%"},
            {"name": "处理人", "width": "8%"},
            {"name": "处理状态", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["YJ-20260127-001", "回款预警", "GTGYL-XSXS-20260118-001", "逾期 7 天未回款 ¥6,900,000", "高", "2026-01-27 10:00", "—", "待处理",
             {"v": "待处理", "type": "tag", "tag_color": "red"},
             {"type": "action", "v": ['<a href="./warning-detail.html">详情</a>', '<a href="#">处理</a>']}],
            ["YJ-20260125-002", "库存预警", "小麦 (西安中转仓)", "库存量低于安全阈值 12 吨", "中", "2026-01-25 14:30", "—", "待处理",
             {"v": "待处理", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">处理</a>']}],
            ["YJ-20260122-003", "合规预警", "中粮贸易有限公司", "客户证照即将过期", "低", "2026-01-22 09:15", "张风控", "已处理",
             {"v": "已处理", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">查看</a>']}],
        ],
    },
    "warning-config.html": {
        "title": "预警配置", "bc1": "预警中心", "bc2": "预警管理",
        "filter_fields": [
            ("规则编号", '<input type="text" class="input" placeholder="请输入规则编号">'),
            ("规则名称", '<input type="text" class="input" placeholder="请输入规则名称">'),
            ("预警类型", '<select class="select"><option>请选择</option><option>价格预警</option><option>库存预警</option><option>回款预警</option><option>合规预警</option></select>'),
            ("风险等级", '<select class="select"><option>请选择</option><option>高</option><option>中</option><option>低</option></select>'),
            ("状态", '<select class="select"><option>请选择</option><option>启用</option><option>停用</option></select>'),
            ("更新时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
        ],
        "status_tabs": [("全部", 14), ("价格预警", 4), ("库存预警", 3), ("回款预警", 4), ("合规预警", 3)],
        "total": 14, "total_pages": 2,
        "columns": [
            {"name": "规则编号", "width": "14%", "mono": True},
            {"name": "规则名称", "width": "18%"},
            {"name": "预警类型", "width": "10%"},
            {"name": "触发条件", "width": "20%"},
            {"name": "风险等级", "width": "8%"},
            {"name": "通知方式", "width": "10%"},
            {"name": "更新时间", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["GZ-001", "玉米价格波动预警", "价格预警", "单日涨跌幅 > 5%", "中", "站内消息", "2026-01-15", "启用",
             {"v": "启用", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["GZ-002", "库存安全预警", "库存预警", "库存量 < 安全阈值", "高", "站内+短信", "2026-01-15", "启用",
             {"v": "启用", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
            ["GZ-003", "逾期回款预警", "回款预警", "应收日期 < 当前日期 -3 天", "高", "站内+短信+邮件", "2026-01-15", "启用",
             {"v": "启用", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">编辑</a>']}],
        ],
    },
    "blacklist.html": {
        "title": "黑名单管理", "bc1": "预警中心", "bc2": "预警管理",
        "filter_fields": [
            ("名单编号", '<input type="text" class="input" placeholder="请输入名单编号">'),
            ("对象名称", '<input type="text" class="input" placeholder="请输入对象名称">'),
            ("对象类型", '<select class="select"><option>请选择</option><option>企业</option><option>个人</option></select>'),
            ("加入原因", '<select class="select"><option>请选择</option><option>失信被执行</option><option>重大违约</option><option>欺诈</option><option>其他</option></select>'),
            ("加入日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("状态", '<select class="select"><option>请选择</option><option>生效中</option><option>已解除</option></select>'),
        ],
        "status_tabs": [("全部", 8), ("企业黑名单", 5), ("个人黑名单", 3)],
        "total": 8, "total_pages": 1,
        "columns": [
            {"name": "名单编号", "width": "14%", "mono": True},
            {"name": "对象名称", "width": "18%"},
            {"name": "对象类型", "width": "10%"},
            {"name": "证件号", "width": "20%", "mono": True},
            {"name": "加入原因", "width": "12%"},
            {"name": "加入日期", "width": "9%"},
            {"name": "解除日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["HMD-001", "某失信公司", "企业", "91110000MAXXXXXXXX", "失信被执行人", "2025-12-01", "—",
             {"v": "生效中", "type": "tag", "tag_color": "red"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">解除</a>']}],
            ["HMD-002", "某违约企业", "企业", "91370000MAXXXXXXXX", "重大合同违约", "2025-11-15", "—",
             {"v": "生效中", "type": "tag", "tag_color": "red"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">解除</a>']}],
        ],
    },
    # 业务线
    "business-line.html": {
        "title": "业务线管理", "bc1": "业务线管理", "bc2": "业务线",
        "filter_fields": [
            ("业务线编号", '<input type="text" class="input" placeholder="请输入业务线编号">'),
            ("业务线名称", '<input type="text" class="input" placeholder="请输入业务线名称">'),
            ("关联项目", '<input type="text" class="input" placeholder="请输入项目编号">'),
            ("业务类型", '<select class="select"><option>请选择</option><option>存货业务</option><option>预付业务</option><option>账期业务</option><option>购销业务</option></select>'),
            ("创建日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("状态", '<select class="select"><option>请选择</option><option>执行中</option><option>已暂停</option><option>已完结</option></select>'),
        ],
        "status_tabs": [("全部", 12), ("执行中", 8), ("已暂停", 2), ("已完结", 2)],
        "total": 12, "total_pages": 2,
        "columns": [
            {"name": "业务线编号", "width": "14%", "mono": True},
            {"name": "业务线名称", "width": "18%"},
            {"name": "关联项目", "width": "12%", "mono": True},
            {"name": "业务类型", "width": "10%"},
            {"name": "融资金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "已用额度", "width": "12%", "align": "right", "mono": True},
            {"name": "开始日期", "width": "8%"},
            {"name": "结束日期", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["YWX-20260127-001", "中粮贸易预付业务线", "XM-20260127-001", "预付业务", "¥ 80,000,000", "¥ 30,000,000", "2026-01-30", "2026-12-31",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="./business-line-detail.html">详情</a>', '<a href="#">额度</a>']}],
            ["YWX-20260125-002", "山东金粮存货业务线", "XM-20260125-002", "存货业务", "¥ 50,000,000", "¥ 15,000,000", "2026-01-28", "2026-12-31",
             {"v": "执行中", "type": "tag", "tag_color": "blue"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">额度</a>']}],
        ],
    },
    # 账户中心（特殊：不是标准列表页，但套用模板）
    "account-personal.html": {
        "title": "个人中心", "bc1": "账户中心", "bc2": "个人账户",
        "filter_fields": [
            ("记录编号", '<input type="text" class="input" placeholder="请输入记录编号">'),
            ("操作类型", '<select class="select"><option>请选择</option><option>登录</option><option>修改资料</option><option>密码修改</option><option>权限变更</option></select>'),
            ("操作人", '<input type="text" class="input" placeholder="请输入操作人">'),
            ("操作时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("IP 地址", '<input type="text" class="input" placeholder="请输入 IP">'),
            ("结果", '<select class="select"><option>请选择</option><option>成功</option><option>失败</option></select>'),
        ],
        "status_tabs": [("全部", 48), ("基本信息", 0), ("认证信息", 0), ("操作记录", 48)],
        "total": 48, "total_pages": 5,
        "columns": [
            {"name": "记录编号", "width": "16%", "mono": True},
            {"name": "操作类型", "width": "12%"},
            {"name": "操作人", "width": "10%"},
            {"name": "操作对象", "width": "18%"},
            {"name": "操作详情", "width": "20%"},
            {"name": "操作时间", "width": "12%"},
            {"name": "IP 地址", "width": "8%"},
            {"name": "结果", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["LOG-20260127-001", "登录", "张爽", "—", "账号登录成功", "2026-01-27 09:15:30", "192.168.1.50", "成功",
             {"v": "成功", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>']}],
            ["LOG-20260126-002", "修改资料", "王经理", "客户资料", "修改客户联系电话", "2026-01-26 14:20:15", "192.168.1.51", "成功",
             {"v": "成功", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>']}],
            ["LOG-20260125-003", "密码修改", "李安全", "—", "用户密码修改", "2026-01-25 16:45:00", "192.168.1.52", "成功",
             {"v": "成功", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>']}],
        ],
    },
    "account-company.html": {
        "title": "企业中心", "bc1": "账户中心", "bc2": "企业账户",
        "filter_fields": [
            ("证书编号", '<input type="text" class="input" placeholder="请输入证书编号">'),
            ("证书类型", '<select class="select"><option>请选择</option><option>营业执照</option><option>开户许可证</option><option>行业资质</option><option>其他</option></select>'),
            ("上传人", '<input type="text" class="input" placeholder="请输入上传人">'),
            ("上传时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("到期时间", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("状态", '<select class="select"><option>请选择</option><option>有效</option><option>已过期</option><option>即将过期</option></select>'),
        ],
        "status_tabs": [("全部", 8), ("基本信息", 0), ("资质证书", 6), ("操作记录", 2)],
        "total": 8, "total_pages": 1,
        "columns": [
            {"name": "证书编号", "width": "16%", "mono": True},
            {"name": "证书类型", "width": "12%"},
            {"name": "证书名称", "width": "20%"},
            {"name": "发证机构", "width": "14%"},
            {"name": "发证日期", "width": "10%"},
            {"name": "到期日期", "width": "10%"},
            {"name": "上传人", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["ZS-20260127-001", "营业执照", "河南中豫港通供应链管理有限公司", "郑州市市场监督管理局", "2023-05-15", "2026-05-14", "管理员",
             {"v": "即将过期", "type": "tag", "tag_color": "yellow"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">续期</a>']}],
            ["ZS-20260125-002", "开户许可证", "河南中豫港通供应链管理有限公司", "中国人民银行郑州中心支行", "2023-06-20", "长期有效", "管理员",
             {"v": "有效", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">查看</a>']}],
        ],
    },
    # 数据中心 — 报表
    "report-bizline.html": {
        "title": "业务线报表", "bc1": "数据中心", "bc2": "业务报表",
        "filter_fields": [
            ("报表编号", '<input type="text" class="input" placeholder="请输入报表编号">'),
            ("业务线", '<input type="text" class="input" placeholder="请输入业务线">'),
            ("报表周期", '<select class="select"><option>请选择</option><option>日报</option><option>周报</option><option>月报</option></select>'),
            ("生成日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("生成人", '<input type="text" class="input" placeholder="请输入生成人">'),
            ("状态", '<select class="select"><option>请选择</option><option>已生成</option><option>已归档</option></select>'),
        ],
        "status_tabs": [("全部", 26), ("日报", 18), ("周报", 6), ("月报", 2)],
        "total": 26, "total_pages": 3,
        "columns": [
            {"name": "报表编号", "width": "14%", "mono": True},
            {"name": "业务线", "width": "16%"},
            {"name": "报表周期", "width": "8%"},
            {"name": "放款金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "还款金额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "生成日期", "width": "9%"},
            {"name": "生成人", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RPT-BIZ-001", "中粮贸易预付业务线", "月报", "¥ 30,000,000", "¥ 10,000,000", "2026-01-31", "系统",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["RPT-BIZ-002", "山东金粮存货业务线", "月报", "¥ 15,000,000", "¥ 5,000,000", "2026-01-31", "系统",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "report-fund.html": {
        "title": "资金报表", "bc1": "数据中心", "bc2": "资金报表",
        "filter_fields": [
            ("报表编号", '<input type="text" class="input" placeholder="请输入报表编号">'),
            ("资金类型", '<select class="select"><option>请选择</option><option>自有资金</option><option>融资资金</option><option>保证金</option></select>'),
            ("报表周期", '<select class="select"><option>请选择</option><option>日报</option><option>周报</option><option>月报</option></select>'),
            ("生成日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("生成人", '<input type="text" class="input" placeholder="请输入生成人">'),
            ("状态", '<select class="select"><option>请选择</option><option>已生成</option><option>已归档</option></select>'),
        ],
        "status_tabs": [("全部", 30), ("日报", 20), ("周报", 8), ("月报", 2)],
        "total": 30, "total_pages": 3,
        "columns": [
            {"name": "报表编号", "width": "14%", "mono": True},
            {"name": "资金类型", "width": "10%"},
            {"name": "报表周期", "width": "8%"},
            {"name": "期初余额(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "本期收入", "width": "12%", "align": "right", "mono": True},
            {"name": "本期支出", "width": "12%", "align": "right", "mono": True},
            {"name": "期末余额", "width": "12%", "align": "right", "mono": True},
            {"name": "生成日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RPT-FUND-001", "自有资金", "月报", "¥ 5,000,000", "¥ 1,054,140", "¥ 1,032,580", "¥ 5,021,560", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["RPT-FUND-002", "融资资金", "月报", "¥ 50,000,000", "¥ 30,000,000", "¥ 10,000,000", "¥ 70,000,000", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "report-ar-ap.html": {
        "title": "应收应付报表", "bc1": "数据中心", "bc2": "财务报表",
        "filter_fields": [
            ("报表编号", '<input type="text" class="input" placeholder="请输入报表编号">'),
            ("报表类型", '<select class="select"><option>请选择</option><option>应收账款</option><option>应付账款</option><option>总账</option></select>'),
            ("报表周期", '<select class="select"><option>请选择</option><option>日报</option><option>周报</option><option>月报</option></select>'),
            ("生成日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("客户/供应商", '<input type="text" class="input" placeholder="请输入名称">'),
            ("状态", '<select class="select"><option>请选择</option><option>已生成</option><option>已归档</option></select>'),
        ],
        "status_tabs": [("全部", 22), ("日报", 14), ("周报", 6), ("月报", 2)],
        "total": 22, "total_pages": 3,
        "columns": [
            {"name": "报表编号", "width": "14%", "mono": True},
            {"name": "报表类型", "width": "10%"},
            {"name": "对方单位", "width": "16%"},
            {"name": "应收(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "已收(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "应付(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "已付(元)", "width": "12%", "align": "right", "mono": True},
            {"name": "生成日期", "width": "8%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RPT-AR-001", "应收账款", "中粮贸易有限公司", "¥ 14,000,000", "¥ 14,000,000", "—", "—", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["RPT-AP-002", "应付账款", "河南诚泽运输有限公司", "—", "—", "¥ 13,600,000", "¥ 13,600,000", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "report-inventory.html": {
        "title": "库存报表", "bc1": "数据中心", "bc2": "仓储报表",
        "filter_fields": [
            ("报表编号", '<input type="text" class="input" placeholder="请输入报表编号">'),
            ("仓库", '<select class="select"><option>请选择</option><option>郑州主仓</option><option>青岛前置仓</option><option>西安中转仓</option></select>'),
            ("品名", '<input type="text" class="input" placeholder="请输入品名">'),
            ("报表周期", '<select class="select"><option>请选择</option><option>日报</option><option>周报</option><option>月报</option></select>'),
            ("生成日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("状态", '<select class="select"><option>请选择</option><option>已生成</option><option>已归档</option></select>'),
        ],
        "status_tabs": [("全部", 28), ("日报", 18), ("周报", 8), ("月报", 2)],
        "total": 28, "total_pages": 3,
        "columns": [
            {"name": "报表编号", "width": "14%", "mono": True},
            {"name": "仓库", "width": "10%"},
            {"name": "品名", "width": "10%"},
            {"name": "期初库存(吨)", "width": "12%", "align": "right", "mono": True},
            {"name": "本期入库", "width": "10%", "align": "right", "mono": True},
            {"name": "本期出库", "width": "10%", "align": "right", "mono": True},
            {"name": "期末库存", "width": "10%", "align": "right", "mono": True},
            {"name": "生成日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RPT-INV-001", "郑州主仓", "进口木薯淀粉", "20,000", "0", "0", "20,000", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["RPT-INV-002", "青岛前置仓", "大豆", "8,000", "0", "0", "8,000", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "report-project.html": {
        "title": "项目报表", "bc1": "数据中心", "bc2": "项目报表",
        "filter_fields": [
            ("报表编号", '<input type="text" class="input" placeholder="请输入报表编号">'),
            ("项目类型", '<select class="select"><option>请选择</option><option>存货业务</option><option>预付业务</option><option>账期业务</option><option>购销业务</option></select>'),
            ("报表周期", '<select class="select"><option>请选择</option><option>日报</option><option>周报</option><option>月报</option></select>'),
            ("生成日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("生成人", '<input type="text" class="input" placeholder="请输入生成人">'),
            ("状态", '<select class="select"><option>请选择</option><option>已生成</option><option>已归档</option></select>'),
        ],
        "status_tabs": [("全部", 18), ("日报", 12), ("周报", 4), ("月报", 2)],
        "total": 18, "total_pages": 2,
        "columns": [
            {"name": "报表编号", "width": "14%", "mono": True},
            {"name": "项目类型", "width": "10%"},
            {"name": "项目数量", "width": "10%", "align": "right", "mono": True},
            {"name": "拟融资金额(元)", "width": "14%", "align": "right", "mono": True},
            {"name": "已用金额(元)", "width": "14%", "align": "right", "mono": True},
            {"name": "放款笔数", "width": "8%", "align": "right", "mono": True},
            {"name": "还款笔数", "width": "8%", "align": "right", "mono": True},
            {"name": "生成日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RPT-PRJ-001", "预付业务", "5", "¥ 250,000,000", "¥ 80,000,000", "12", "3", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["RPT-PRJ-002", "存货业务", "8", "¥ 380,000,000", "¥ 150,000,000", "25", "8", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "report-risk.html": {
        "title": "风险报表", "bc1": "数据中心", "bc2": "风险报表",
        "filter_fields": [
            ("报表编号", '<input type="text" class="input" placeholder="请输入报表编号">'),
            ("风险类型", '<select class="select"><option>请选择</option><option>客户风险</option><option>市场风险</option><option>操作风险</option><option>合规风险</option></select>'),
            ("报表周期", '<select class="select"><option>请选择</option><option>日报</option><option>周报</option><option>月报</option></select>'),
            ("生成日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("生成人", '<input type="text" class="input" placeholder="请输入生成人">'),
            ("状态", '<select class="select"><option>请选择</option><option>已生成</option><option>已归档</option></select>'),
        ],
        "status_tabs": [("全部", 16), ("日报", 10), ("周报", 4), ("月报", 2)],
        "total": 16, "total_pages": 2,
        "columns": [
            {"name": "报表编号", "width": "14%", "mono": True},
            {"name": "风险类型", "width": "10%"},
            {"name": "高风险数", "width": "10%", "align": "right", "mono": True},
            {"name": "中风险数", "width": "10%", "align": "right", "mono": True},
            {"name": "低风险数", "width": "10%", "align": "right", "mono": True},
            {"name": "已处理", "width": "10%", "align": "right", "mono": True},
            {"name": "未处理", "width": "10%", "align": "right", "mono": True},
            {"name": "生成日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RPT-RISK-001", "客户风险", "3", "8", "7", "16", "2", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
            ["RPT-RISK-002", "市场风险", "1", "3", "5", "8", "1", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
    "report-compliance.html": {
        "title": "合规报表", "bc1": "数据中心", "bc2": "合规报表",
        "filter_fields": [
            ("报表编号", '<input type="text" class="input" placeholder="请输入报表编号">'),
            ("合规类型", '<select class="select"><option>请选择</option><option>监管报送</option><option>内控检查</option><option>审计</option><option>其他</option></select>'),
            ("报表周期", '<select class="select"><option>请选择</option><option>日报</option><option>周报</option><option>月报</option></select>'),
            ("生成日期", '<input type="text" class="input" placeholder="开始 ~ 结束">'),
            ("生成人", '<input type="text" class="input" placeholder="请输入生成人">'),
            ("状态", '<select class="select"><option>请选择</option><option>已生成</option><option>已归档</option></select>'),
        ],
        "status_tabs": [("全部", 12), ("日报", 8), ("周报", 2), ("月报", 2)],
        "total": 12, "total_pages": 2,
        "columns": [
            {"name": "报表编号", "width": "14%", "mono": True},
            {"name": "合规类型", "width": "10%"},
            {"name": "检查项数", "width": "10%", "align": "right", "mono": True},
            {"name": "合规项数", "width": "10%", "align": "right", "mono": True},
            {"name": "不合规项数", "width": "12%", "align": "right", "mono": True},
            {"name": "已整改", "width": "10%", "align": "right", "mono": True},
            {"name": "待整改", "width": "10%", "align": "right", "mono": True},
            {"name": "生成日期", "width": "9%"},
            {"name": "状态", "width": "6%"},
            {"name": "操作", "width": "auto", "min_width": 140, "action": True, "align": "right"},
        ],
        "mock_rows": [
            ["RPT-COMP-001", "内控检查", "30", "28", "2", "1", "1", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="./report-compliance-detail.html">详情</a>', '<a href="#">下载</a>']}],
            ["RPT-COMP-002", "监管报送", "12", "12", "0", "0", "0", "2026-01-31",
             {"v": "已生成", "type": "tag", "tag_color": "green"},
             {"type": "action", "v": ['<a href="#">详情</a>', '<a href="#">下载</a>']}],
        ],
    },
}

PAGES_CONFIG.update(BATCH4_CONFIG)

# ============================================
# 主流程
# ============================================

if __name__ == "__main__":
    for filename, cfg in PAGES_CONFIG.items():
        filepath = PAGES_DIR / filename
        html = render_page(cfg)
        filepath.write_text(html, encoding="utf-8")
        print(f"✅ 生成: {filename}  ({len(html)} bytes)")
    print(f"\n📦 Batch 1 完成：{len(PAGES_CONFIG)} 个列表页")
