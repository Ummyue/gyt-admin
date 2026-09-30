#!/usr/bin/env python3
"""
豫港通 prototype 增强版生成器
- 48 个缺失页面骨架（list/detail/form 三种类型）
- 1:1 路由：每个页面对应一个独立 MD
- 字段占位 + 待补充标识
"""
import re
from pathlib import Path

PAGES_DIR = Path(__file__).parent.parent / "pages"
PAGES_DIR.mkdir(exist_ok=True)

# ===== 通用顶 nav =====
TOPBAR = '''<div class="topbar">
  <div class="topbar-logo">
    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 16px;">豫</div>
    <span>豫港通</span>
  </div>
  <div class="topbar-menu">{MENU}</div>
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

MENU_ITEMS = [
    ("工作台", "work"), ("准入管理", "adm"), ("数字供应链", "scm"),
    ("仓储管理", "wh"), ("预警中心", "warn"), ("数据中心", "dc"), ("账户中心", "ac")
]
def get_topbar(active="scm"):
    items = "".join([
        f'<div class="topbar-menu-item{" active" if k==active else ""}">{n}</div>'
        for n, k in MENU_ITEMS
    ])
    return TOPBAR.replace("{MENU}", items)


# ===== 通用侧边菜单（按一级 group）=====
def get_sidemenu(active_group, active_page):
    """返回完整的左侧菜单 HTML（83 页 tree）"""
    groups = [
        ("准入管理", "adm", "📋", [
            ("project-list", "项目管理（列表）"),
            ("project-apply", "新增立项准入"),
            ("project-detail", "项目准入详情"),
            ("customer-list", "客户管理（列表）"),
            ("customer-apply", "新增客户申请"),
            ("customer-quota", "客户额度管理"),
            ("blacklist", "黑名单管理"),
        ]),
        ("数字供应链·合同", "scm", "📄", [
            ("contract-purchase", "采购合同"),
            ("contract-purchase-new", "新增/编辑采购框架合同"),
            ("contract-purchase-framework-detail", "采购框架合同详情"),
            ("contract-purchase-order-new", "新增/编辑采购订单/单批次合同"),
            ("contract-purchase-order-detail", "采购订单/单批次合同详情"),
            ("contract-sales", "销售合同"),
            ("contract-sales-new", "新增/编辑销售框架合同"),
            ("contract-sales-framework-detail", "销售框架合同详情"),
            ("contract-sales-order-new", "新增销售订单/单批次合同"),
            ("contract-sales-order-detail", "销售订单/单批次合同详情"),
            ("contract-supplement", "补充协议"),
            ("contract-supplement-new", "新增补协-框架合同"),
            ("contract-supplement-framework-detail", "补协详情页-框架合同"),
            ("contract-supplement-order-new", "新增补协-订单/单批次合同"),
            ("contract-supplement-order-detail", "补协详情页-订单/单批次合同"),
        ]),
        ("数字供应链·业务", "scm", "📦", [
            ("business-line", "业务线管理"),
            ("business-line-relate", "业务线关联"),
            ("business-line-detail", "业务线详情"),
            ("order-list", "订单管理"),
            ("shipment-out", "发货管理"),
            ("shipment-out-new", "新增发货申请"),
            ("shipment-out-detail", "发货申请详情"),
            ("shipment-in", "收货管理"),
            ("shipment-in-new", "新增收货数据"),
            ("shipment-in-detail", "收货信息详情"),
            ("goods-transfer", "货转管理"),
            ("goods-transfer-up", "已上传上游货转"),
            ("goods-transfer-up-detail", "已上传上游货转详情"),
            ("goods-transfer-down-new", "新增下游货转"),
            ("goods-transfer-down-detail", "下游货转详情"),
        ]),
        ("数字供应链·资金", "scm", "💰", [
            ("payment-list", "付款列表"),
            ("payment-new", "新增付款"),
            ("payment-detail", "付款详情"),
            ("refund-list", "退款列表"),
            ("refund-apply", "退款申请"),
            ("refund-detail", "退款详情"),
            ("receipt-list", "回款列表"),
            ("receipt-claim", "回款认领操作"),
            ("receipt-claim-detail", "回款认领详情"),
            ("margin-pool", "保证金管理"),
            ("margin-adjust", "保证金调整"),
            ("margin-record", "调整记录"),
        ]),
        ("数字供应链·结算", "scm", "🧾", [
            ("settlement-purchase", "采购结算"),
            ("settlement-purchase-new", "新增/编辑采购结算单"),
            ("settlement-purchase-detail", "采购结算单详情"),
            ("settlement-sales", "销售结算"),
            ("settlement-sales-new", "新增/编辑销售结算单"),
            ("settlement-sales-detail", "销售结算单详情"),
            ("invoice", "进项发票"),
        ]),
        ("数字供应链·风险", "scm", "📋", [
            ("market-price", "盯市价格管理"),
            ("market-price-detail", "指标详情"),
            ("bond-letter", "追保函管理"),
            ("bond-letter-new", "新增/编辑追保函"),
            ("bond-letter-detail", "追保函详情"),
        ]),
        ("仓储管理", "wh", "🏭", [
            ("warehouse-inbound", "入库记录"),
            ("warehouse-inbound-new", "新增入库"),
            ("warehouse-inbound-detail", "入库详情"),
            ("warehouse-outbound", "出库记录"),
            ("warehouse-outbound-new", "新增出库"),
            ("warehouse-outbound-detail", "出库详情"),
            ("warehouse-release", "放货管理"),
            ("warehouse-release-new", "新增放货指令"),
            ("warehouse-release-detail", "放货指令详情"),
        ]),
        ("预警中心", "warn", "🔔", [
            ("warning-list", "预警列表"),
            ("warning-detail", "预警详情"),
            ("warning-config", "预警规则配置"),
        ]),
        ("数据中心", "dc", "📊", [
            ("dashboard", "驾驶舱"),
            ("report-project", "项目台账表"),
            ("report-bizline", "业务线台账表"),
            ("report-fund", "资金占压表"),
            ("report-inventory", "库存明细表"),
            ("report-ar-ap", "应收应付表"),
            ("report-risk", "风控统计报表"),
            ("report-compliance", "合规验证报告列表"),
            ("report-compliance-detail", "合规报告详情"),
        ]),
    ]
    html = ""
    for gname, gkey, gicon, items in groups:
        is_open = (gkey == active_group)
        html += f'''<div class="sidemenu-group{" open" if is_open else ""}">
        <div class="sidemenu-group-title">
          <span class="icon">{gicon}</span>
          <span style="flex: 1;">{gname}</span>
          <span class="arrow">▾</span>
        </div>
        <div class="sidemenu-items">
          {''.join([
            f'<a href="./{f}.html" class="sidemenu-item{" active" if f==active_page else ""}">{n}</a>'
            for f, n in items
          ])}
        </div>
      </div>'''
    return html


def get_breadcrumb_html(breadcrumb):
    """breadcrumb: list of (name, href)"""
    parts = []
    for i, (n, h) in enumerate(breadcrumb):
        if h:
            parts.append(f'<a href="{h}">{n}</a>')
        else:
            parts.append(f'<span>{"current" if i==len(breadcrumb)-1 else ""}>{n}</span>'.replace("current", "current"))
    html = ""
    for i, (n, h) in enumerate(breadcrumb):
        if i == len(breadcrumb)-1:
            html += f'<span class="current">{n}</span>'
        else:
            html += f'<span>{n}</span><span class="separator">/</span>'
    return html


# ===== 公共样式块（每个页面复用）=====
COMMON_EXTRA_CSS = ""
# 已经有 design-system.css 了


# ===== 模板 1: 列表型 =====
def render_list_page(config):
    file = config["file"]
    name = config["name"]
    title = config["title"]
    breadcrumb = config["breadcrumb"]
    menu_group = config["menu_group"]
    active_top = config.get("active_top", "scm")
    filter_fields = config.get("filter_fields", [
        ("编号", "text", "请输入"),
        ("状态", "select", "请选择", ["待提交", "审核中", "执行中", "已完结"]),
    ])
    status_tabs = config.get("status_tabs", [
        ("全部", "100", True), ("待提交", "8", False), ("执行中", "78", False), ("已完结", "12", False),
    ])
    cards = config.get("cards", "")

    filter_html = "\n".join([
        f'''<div class="filter-item">
          <div class="filter-item-label">{l}</div>
          <input type="text" class="input" placeholder="{p}">
        </div>''' if t == "text" else
        f'''<div class="filter-item">
          <div class="filter-item-label">{l}</div>
          <select class="select"><option>{p or "请选择"}</option>{''.join([f'<option>{o}</option>' for o in (opts or [])])}</select>
        </div>'''
        for l, t, p, *opts in filter_fields
    ])
    status_tabs_html = "\n".join([
        f'<div class="status-tab{" active" if a else ""}">{n} <span class="count">{c}</span></div>'
        for n, c, a in status_tabs
    ])

    cards_section = cards if cards else '''
        <div class="empty">
          <div class="empty-icon">📋</div>
          <div class="empty-text">暂无数据</div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 豫港通</title>
  <link rel="stylesheet" href="../assets/css/design-system.css">
</head>
<body>
  {get_topbar(active_top)}
  <div style="display: flex;">
    {get_sidemenu(menu_group, file)}
    <div style="flex: 1; display: flex; flex-direction: column; min-width: 0;">
      <div class="page-header">
        <div class="breadcrumb">{get_breadcrumb_html(breadcrumb)}</div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <h1 class="page-title">{title}</h1>
          <button class="btn btn-primary">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            新增{title}
          </button>
        </div>
      </div>
      <div class="filter-bar">
        {filter_html}
        <div class="filter-actions">
          <button class="btn btn-primary btn-sm">查询</button>
          <button class="btn btn-secondary btn-sm">重置</button>
        </div>
      </div>
      <div class="status-tabs" style="padding: 0 24px; background: var(--bg-card);">
        {status_tabs_html}
      </div>
      <div style="flex: 1; padding: 16px 24px 24px; overflow-y: auto; background: var(--bg-page);">
        {cards_section}
        <div class="pagination">
          <div>共 100 条记录 · 第 1 / 5 页</div>
          <div class="pagination-pages">
            <div class="pagination-page">‹</div>
            <div class="pagination-page active">1</div>
            <div class="pagination-page">2</div>
            <div class="pagination-page">3</div>
            <div class="pagination-page">4</div>
            <div class="pagination-page">5</div>
            <div class="pagination-page">›</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>'''
    (PAGES_DIR / f"{file}.html").write_text(html, encoding="utf-8")
    print(f"  + {file}.html")


# ===== 模板 2: 详情型 =====
def render_detail_page(config):
    file = config["file"]
    name = config["name"]
    title = config["title"]
    breadcrumb = config["breadcrumb"]
    menu_group = config["menu_group"]
    active_top = config.get("active_top", "scm")
    status = config.get("status", ("执行中", "tag-blue"))
    info_rows = config.get("info_rows", [])  # list of (label, value, label, value, label, value)
    tabs = config.get("tabs", [])  # list of (name, active)
    bottom_actions = config.get("bottom_actions", [
        "导出详情", "复制为新", "查看审批记录", "推进到下一节点"
    ])

    status_label, status_color = status

    # 顶部信息卡（6 列）
    info_html = ""
    for i, row in enumerate(info_rows):
        cells = "".join([
            f'<div class="info-item"><span class="info-label">{l}</span><span class="info-value">{v}</span></div>'
            for l, v in row
        ])
        info_html += f'<div class="info-grid info-grid-3" style="margin-top: {8 if i else 12}px; row-gap: 8px;">{cells}</div>'

    tabs_html = "\n".join([
        f'<div class="tab{" active" if a else ""}">{n}</div>'
        for n, a in tabs
    ]) if tabs else ""

    actions_html = "\n".join([
        f'<button class="btn btn-secondary">{a}</button>' if i < len(bottom_actions)-1 else f'<button class="btn btn-primary">{a}</button>'
        for i, a in enumerate(bottom_actions)
    ])

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 豫港通</title>
  <link rel="stylesheet" href="../assets/css/design-system.css">
</head>
<body>
  {get_topbar(active_top)}
  <div style="display: flex;">
    {get_sidemenu(menu_group, file)}
    <div style="flex: 1; display: flex; flex-direction: column; min-width: 0;">
      <div class="page-header">
        <div class="breadcrumb">{get_breadcrumb_html(breadcrumb)}</div>
      </div>
      <div style="flex: 1; padding: 16px 24px 80px; overflow-y: auto;">
        <div class="card" style="margin-bottom: 16px; padding: 20px 24px;">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <span class="tag {status_color}">{status_label}</span>
            <h1 style="font-size: 18px; font-weight: 600; margin: 0;">{title}</h1>
            <a href="./{breadcrumb[-2][1] if len(breadcrumb)>=2 and breadcrumb[-2][1] else "javascript:history.back()"}" style="font-size: 13px; color: var(--color-primary);">&lt; 返回</a>
          </div>
          {info_html}
        </div>
        {f'<div class="tabs" style="margin-bottom: 16px;">{tabs_html}</div>' if tabs_html else ''}
        <div class="card">
          <div class="card-header"><div class="card-title">基本信息</div></div>
          <div class="card-body" style="padding: 0;">
            <table class="info-table">
              <tbody>
                <tr><td class="info-label">编号</td><td class="info-value">—</td><td class="info-label">名称</td><td class="info-value" colspan="3">待补充</td></tr>
                <tr><td class="info-label">创建人</td><td class="info-value">—</td><td class="info-label">创建时间</td><td class="info-value" colspan="3">—</td></tr>
                <tr><td class="info-label">备注</td><td class="info-value" colspan="5" style="color: var(--text-tertiary);">本页面字段待补充（基于原型图 02-83 抓取的内容）</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="footer-actions">
        {actions_html}
      </div>
    </div>
  </div>
</body>
</html>'''
    (PAGES_DIR / f"{file}.html").write_text(html, encoding="utf-8")
    print(f"  + {file}.html")


# ===== 模板 3: 表单型 =====
def render_form_page(config):
    file = config["file"]
    name = config["name"]
    title = config["title"]
    breadcrumb = config["breadcrumb"]
    menu_group = config["menu_group"]
    active_top = config.get("active_top", "scm")
    fields = config.get("fields", [])  # list of (label, required, type, placeholder, options)
    show_steps = config.get("show_steps", False)
    step_count = config.get("step_count", 0)
    current_step = config.get("current_step", 1)

    steps_html = ""
    if show_steps and step_count:
        items = "".join([
            f'''<div class="step">
              <div class="step-circle{' completed' if i+1 < current_step else ' current' if i+1==current_step else ''}">{i+1 if i+1 != current_step else i+1}</div>
              <div class="step-label">第 {i+1} 步</div>
            </div>{'<div class="step-line' + (' completed' if i+1 < current_step else '') + '"></div>' if i < step_count-1 else ''}'''
            for i in range(step_count)
        ])
        steps_html = f'''<div class="card" style="margin-bottom: 16px; padding: 16px 32px;">
          <div class="steps">{items}</div>
        </div>'''

    # 字段 HTML
    fields_html = ""
    for i, (label, required, ftype, ph, *opts) in enumerate(fields):
        req_html = ' <span class="required">*</span>' if required else ''
        if ftype == "textarea":
            fields_html += f'''<div class="form-field" style="grid-column: 1 / -1;">
                <label class="form-label">{label}{req_html}</label>
                <textarea class="textarea" rows="3" placeholder="{ph}"></textarea>
              </div>'''
        elif ftype == "select":
            options_html = "\n".join([f'<option>{o}</option>' for o in (opts or [])])
            fields_html += f'''<div class="form-field">
                <label class="form-label">{label}{req_html}</label>
                <select class="select"><option>{ph or "请选择"}</option>{options_html}</select>
              </div>'''
        else:
            fields_html += f'''<div class="form-field">
                <label class="form-label">{label}{req_html}</label>
                <input type="text" class="input" placeholder="{ph}">
              </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 豫港通</title>
  <link rel="stylesheet" href="../assets/css/design-system.css">
</head>
<body>
  {get_topbar(active_top)}
  <div style="display: flex;">
    {get_sidemenu(menu_group, file)}
    <div style="flex: 1; display: flex; flex-direction: column; min-width: 0;">
      <div class="page-header">
        <div class="breadcrumb">{get_breadcrumb_html(breadcrumb)}</div>
        <h1 class="page-title">{title}</h1>
      </div>
      <div style="flex: 1; padding: 16px 24px 80px; overflow-y: auto;">
        {steps_html}
        <div class="card" style="margin-bottom: 16px;">
          <div class="card-header">
            <div class="card-title">基本信息</div>
            <div style="font-size: 12px; color: var(--text-tertiary);">带 <span style="color: var(--color-danger);">*</span> 为必填项</div>
          </div>
          <div class="card-body">
            <div class="form-grid form-grid-3">
              {fields_html if fields_html else '<div class="form-field" style="grid-column: 1/-1;"><div style="color: var(--text-tertiary);">字段待补充</div></div>'}
            </div>
          </div>
        </div>
      </div>
      <div class="footer-actions">
        <button class="btn btn-secondary">保存草稿</button>
        <div style="flex: 1;"></div>
        <button class="btn btn-secondary">上一步</button>
        <button class="btn btn-primary">下一步</button>
      </div>
    </div>
  </div>
</body>
</html>'''
    (PAGES_DIR / f"{file}.html").write_text(html, encoding="utf-8")
    print(f"  + {file}.html")


# ===== 48 个缺失页面配置 =====
def gen_all():
    print("==> 生成 48 个缺失页面")

    # === 合同管理 (9 个缺) ===
    scm_bc = ("合同管理", "scm")
    breadcrumb_contract = [("数字供应链", None), ("合同管理", None), ("采购合同", "./contract-purchase.html")]

    # 09 新增/编辑采购框架合同
    render_form_page({
        "file": "contract-purchase-new", "name": "新增/编辑采购框架合同",
        "title": "新增/编辑采购框架合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("采购合同", "./contract-purchase.html"), ("新增/编辑采购框架合同", None)],
        "fields": [
            ("合同编号", False, "text", "GTGYL-MSXS-20260127-s"),
            ("卖方企业", True, "select", "请选择", ["河南诚泽运输", "中粮贸易", "其他"]),
            ("运输方式", True, "select", "请选择", ["中欧班列-东线", "中欧班列-西线", "海运", "公路", "铁路"]),
            ("业务类型", True, "select", "请选择", ["存货业务", "预付业务", "账期业务", "购销业务", "总代业务"]),
            ("合同单价", True, "text", "3,400 元/吨"),
            ("合同数量", True, "text", "20,000 吨"),
            ("合同总价", False, "text", "¥ 68,000,000"),
            ("合同签订日期", True, "text", "选择日期"),
            ("交货期限", True, "text", "起 ~ 止"),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
        ],
    })

    # 11 新增/编辑采购订单/单批次合同
    render_form_page({
        "file": "contract-purchase-order-new", "name": "新增/编辑采购订单/单批次合同",
        "title": "新增/编辑采购订单/单批次合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("采购合同", "./contract-purchase.html"), ("新增/编辑采购订单/单批次合同", None)],
        "fields": [
            ("所属框架合同", True, "select", "请选择", ["GTGYL-MSXS-20260127-s"]),
            ("订单编号", False, "text", "DD-20260127-001"),
            ("本批次数量", True, "text", "5,000 吨"),
            ("本批次单价", True, "text", "3,400 元/吨"),
            ("本批次金额", False, "text", "¥ 17,000,000"),
            ("交付日期", True, "text", "选择日期"),
            ("收货仓库", True, "select", "请选择", ["新郑库 A-01", "郑州库 B-02", "洛阳库 C-03"]),
            ("收货人", True, "select", "请选择", ["河南中豫港通供应链管理有限公司"]),
            ("备注", False, "textarea", "请输入备注"),
        ],
    })

    # 销售合同新增/编辑
    render_form_page({
        "file": "contract-sales-new", "name": "新增/编辑销售框架合同",
        "title": "新增/编辑销售框架合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("销售合同", "./contract-sales.html"), ("新增/编辑销售框架合同", None)],
        "fields": [
            ("合同编号", False, "text", "XS-MSXS-20260125-s"),
            ("买方企业", True, "select", "请选择", ["河南双汇集团", "思念食品", "其他"]),
            ("运输方式", True, "select", "请选择", ["中欧班列-东线", "海运", "公路"]),
            ("业务类型", True, "select", "请选择", ["存货业务", "预付业务", "账期业务", "购销业务", "总代业务"]),
            ("合同单价", True, "text", "3,800 元/吨"),
            ("合同数量", True, "text", "18,000 吨"),
            ("合同总价", False, "text", "¥ 68,400,000"),
            ("合同签订日期", True, "text", "选择日期"),
            ("交货期限", True, "text", "起 ~ 止"),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
        ],
    })

    # 13 销售框架合同详情
    render_detail_page({
        "file": "contract-sales-framework-detail", "name": "销售框架合同详情",
        "title": "销售框架合同详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("销售合同", "./contract-sales.html"), ("销售框架合同详情", None)],
        "status": ("执行中", "tag-blue"),
        "info_rows": [
            [("卖方企业", "河南中豫港通供应链管理有限公司"), ("买方企业", "河南双汇集团有限责任公司"), ("业务类型", "存货类")],
            [("合同编号", "XS-MSXS-20260125-s"), ("业务实际负责人", "宋美玲"), ("创建时间", "2026-01-25 10:30:24")],
        ],
        "tabs": [("合同信息", True), ("回款信息(8)", False), ("结算信息(4)", False), ("发票信息(4)", False), ("合同操作记录", False)],
    })

    # 14 销售订单/单批次新增
    render_form_page({
        "file": "contract-sales-order-new", "name": "新增销售订单/单批次合同",
        "title": "新增销售订单/单批次合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("销售合同", "./contract-sales.html"), ("新增销售订单/单批次合同", None)],
        "fields": [
            ("所属框架合同", True, "select", "请选择", ["XS-MSXS-20260125-s"]),
            ("订单编号", False, "text", "DD-20260125-001"),
            ("本批次数量", True, "text", "1,200 吨"),
            ("本批次单价", True, "text", "3,800 元/吨"),
            ("本批次金额", False, "text", "¥ 4,560,000"),
            ("交付日期", True, "text", "选择日期"),
            ("收货方", True, "select", "请选择", ["河南双汇集团有限责任公司"]),
            ("运输方式", True, "select", "请选择", ["公路", "铁路"]),
        ],
    })

    # 17 补协-框架合同新增
    render_form_page({
        "file": "contract-supplement-new", "name": "新增补协-框架合同",
        "title": "新增补协-框架合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("补充协议", "./contract-supplement.html"), ("新增补协-框架合同", None)],
        "fields": [
            ("协议编号", False, "text", "BC-20260120-003"),
            ("主合同编号", True, "select", "请选择", ["GTGYL-MSXS-20260127-s", "XS-MSXS-20260125-s"]),
            ("协议类型", True, "select", "请选择", ["价格调整", "数量调整", "期限延长", "条款变更"]),
            ("变更内容", True, "textarea", "详细描述变更内容"),
            ("生效日期", True, "text", "选择日期"),
            ("到期日期", False, "text", "选择日期"),
        ],
    })

    # 18 补协详情页-框架合同
    render_detail_page({
        "file": "contract-supplement-framework-detail", "name": "补协详情页-框架合同",
        "title": "补协详情页-框架合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("补充协议", "./contract-supplement.html"), ("补协详情页-框架合同", None)],
        "status": ("双签完成", "tag-green"),
        "info_rows": [
            [("协议编号", "BC-20260120-001"), ("主合同编号", "GTGYL-MSXS-20260127-s"), ("协议类型", "价格调整")],
            [("生效日期", "2026-02-01"), ("签订日期", "2026-01-20"), ("签章状态", "双签完成")],
        ],
        "tabs": [("协议信息", True), ("变更详情", False), ("操作记录", False)],
    })

    # 19 补协-订单/单批次合同新增
    render_form_page({
        "file": "contract-supplement-order-new", "name": "新增补协-订单/单批次合同",
        "title": "新增补协-订单/单批次合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("补充协议", "./contract-supplement.html"), ("新增补协-订单/单批次合同", None)],
        "fields": [
            ("协议编号", False, "text", "BC-20260120-004"),
            ("所属补协-框架协议", True, "select", "请选择", ["BC-20260120-001"]),
            ("订单合同", True, "select", "请选择", ["DD-20260127-001"]),
            ("变更类型", True, "select", "请选择", ["价格调整", "数量调整", "期限延长"]),
            ("变更内容", True, "textarea", "详细描述"),
            ("生效日期", True, "text", "选择日期"),
        ],
    })

    # 20 补协详情页-订单/单批次
    render_detail_page({
        "file": "contract-supplement-order-detail", "name": "补协详情页-订单/单批次合同",
        "title": "补协详情页-订单/单批次合同", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("合同管理", None), ("补充协议", "./contract-supplement.html"), ("补协详情页-订单/单批次合同", None)],
        "status": ("待签章", "tag-yellow"),
        "info_rows": [
            [("协议编号", "BC-20260120-002"), ("订单合同", "DD-20260115-002"), ("变更类型", "期限延长")],
        ],
        "tabs": [("协议信息", True), ("变更详情", False), ("操作记录", False)],
    })

    # === 业务线 2 个缺 ===
    render_list_page({
        "file": "business-line-relate", "name": "业务线关联",
        "title": "业务线关联", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("业务线管理", "./business-line.html"), ("业务线关联", None)],
        "filter_fields": [("业务线号", "text", "请输入"), ("上游/下游", "select", "请选择", ["上游", "下游"])],
        "status_tabs": [("全部", "100", True), ("已关联", "82", False), ("待关联", "18", False)],
    })
    render_detail_page({
        "file": "business-line-detail", "name": "业务线详情",
        "title": "业务线详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("业务线管理", "./business-line.html"), ("业务线详情", None)],
        "status": ("执行中", "tag-blue"),
        "info_rows": [
            [("业务线号", "SKYWX202601050001"), ("业务线名称", "河南中粮 - 河南中豫港通"), ("业务类型", "存货类")],
            [("起始日", "2026-01-05"), ("业务负责人", "张爽"), ("业务线金额", "¥ 68,000,000")],
        ],
        "tabs": [("基本信息", True), ("关联合同", False), ("货物进度", False), ("资金进度", False), ("操作记录", False)],
    })

    # === 收发货 4 个缺 ===
    render_form_page({
        "file": "shipment-out-new", "name": "新增发货申请",
        "title": "新增发货申请", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("收发货管理", None), ("发货管理", "./shipment-out.html"), ("新增发货申请", None)],
        "fields": [
            ("发货单号", False, "text", "FH-20260126-001"),
            ("对应销售合同", True, "select", "请选择", ["XS-MSXS-20260125-s"]),
            ("客户名称", True, "select", "请选择", ["河南双汇集团"]),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
            ("发货数量", True, "text", "1,200 吨"),
            ("发货仓库", True, "select", "请选择", ["新郑库 A-01", "郑州库 B-02"]),
            ("货位", False, "text", "A-01-12"),
            ("运输方式", True, "select", "请选择", ["中欧班列", "海运", "公路", "铁路"]),
            ("承运商", True, "select", "请选择", ["郑州铁龙物流", "中远海运物流"]),
            ("发运日期", True, "text", "选择日期"),
            ("到货日期", False, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "shipment-out-detail", "name": "发货申请详情",
        "title": "发货申请详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("收发货管理", None), ("发货管理", "./shipment-out.html"), ("发货申请详情", None)],
        "status": ("运输中", "tag-blue"),
        "info_rows": [
            [("发货单号", "FH-20260126-001"), ("客户名称", "河南双汇集团"), ("品名", "玉米")],
            [("发货数量", "1,200 吨"), ("发货仓库", "新郑库 A-01"), ("货位", "A-01-12")],
            [("运输方式", "中欧班列"), ("承运商", "郑州铁龙物流"), ("运单号", "YD20260126001")],
        ],
        "tabs": [("发货信息", True), ("运输跟踪", False), ("签收记录", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "shipment-in-new", "name": "新增收货数据",
        "title": "新增收货数据", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("收发货管理", None), ("收货管理", "./shipment-in.html"), ("新增收货数据", None)],
        "fields": [
            ("收货单号", False, "text", "SH-20260126-001"),
            ("对应采购合同", True, "select", "请选择", ["GTGYL-MSXS-20260127-s"]),
            ("供应商", True, "select", "请选择", ["中粮贸易"]),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
            ("收货数量", True, "text", "2,000 吨"),
            ("收货仓库", True, "select", "请选择", ["新郑库 A-01", "郑州库 B-02", "洛阳库 C-03"]),
            ("货位", False, "text", "A-01-12"),
            ("运单号", True, "text", "请输入"),
            ("收货日期", True, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "shipment-in-detail", "name": "收货信息详情",
        "title": "收货信息详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("收发货管理", None), ("收货管理", "./shipment-in.html"), ("收货信息详情", None)],
        "status": ("已验收", "tag-green"),
        "info_rows": [
            [("收货单号", "SH-20260126-001"), ("供应商", "中粮贸易"), ("品名", "玉米")],
            [("收货数量", "2,000 吨"), ("收货仓库", "新郑库 A-01"), ("货位", "A-01-12")],
            [("运单号", "YD20260125001"), ("收货日期", "2026-01-26"), ("验收状态", "已验收")],
        ],
        "tabs": [("收货信息", True), ("验收记录", False), ("入库记录", False), ("操作记录", False)],
    })

    # === 货转 4 个缺 ===
    render_detail_page({
        "file": "goods-transfer-up", "name": "已上传上游货转",
        "title": "已上传上游货转", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("货转管理", "./goods-transfer.html"), ("已上传上游货转", None)],
        "status": ("待确认", "tag-yellow"),
        "info_rows": [
            [("货转单号", "HZ-20260126-002"), ("业务线", "SKYWX202601050001"), ("来源", "上游货转")],
        ],
        "tabs": [("货转信息", True), ("OCR识别结果", False), ("所有权确认", False), ("操作记录", False)],
    })
    render_detail_page({
        "file": "goods-transfer-up-detail", "name": "已上传上游货转详情",
        "title": "已上传上游货转详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("货转管理", "./goods-transfer.html"), ("已上传上游货转详情", None)],
        "status": ("已确认", "tag-green"),
        "info_rows": [
            [("货转单号", "HZ-20260120-001"), ("业务线", "SKYWX202601050001"), ("品名", "进口木薯淀粉")],
            [("数量", "1,000 吨"), ("转出库", "新郑库 A-01"), ("转入库", "郑州库 B-02")],
            [("运输方式", "中欧班列"), ("运单号", "YD20260120001"), ("确认时间", "2026-01-21")],
        ],
        "tabs": [("货转信息", True), ("OCR识别结果", False), ("所有权确认", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "goods-transfer-down-new", "name": "新增下游货转",
        "title": "新增下游货转", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("货转管理", "./goods-transfer.html"), ("新增下游货转", None)],
        "fields": [
            ("货转单号", False, "text", "HZ-20260126-003"),
            ("业务线", True, "select", "请选择", ["SKYWX202601050001"]),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
            ("数量", True, "text", "1,000 吨"),
            ("转出库", True, "select", "请选择", ["新郑库 A-01", "郑州库 B-02"]),
            ("转入库", True, "select", "请选择", ["郑州库 B-02", "洛阳库 C-03"]),
            ("运输方式", True, "select", "请选择", ["中欧班列", "铁路", "海运", "公路"]),
            ("运单号", True, "text", "请输入"),
            ("货转日期", True, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "goods-transfer-down-detail", "name": "下游货转详情",
        "title": "下游货转详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("货转管理", "./goods-transfer.html"), ("下游货转详情", None)],
        "status": ("运输中", "tag-blue"),
        "info_rows": [
            [("货转单号", "HZ-20260125-001"), ("业务线", "SKYWX202601050002"), ("品名", "玉米")],
            [("数量", "1,500 吨"), ("转出库", "郑州库 B-02"), ("转入库", "洛阳库 C-03")],
            [("运输方式", "铁路"), ("运单号", "YD20260125001"), ("发运日期", "2026-01-25")],
        ],
        "tabs": [("货转信息", True), ("运输跟踪", False), ("签收记录", False), ("操作记录", False)],
    })

    # === 资金管理 6 个缺 ===
    render_form_page({
        "file": "payment-new", "name": "新增付款",
        "title": "新增付款", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("付款列表", "./payment-list.html"), ("新增付款", None)],
        "fields": [
            ("付款单号", False, "text", "FK-20260126-001"),
            ("收款方", True, "select", "请选择", ["中粮贸易", "河南诚泽运输"]),
            ("付款类型", True, "select", "请选择", ["货款", "运费", "保证金", "其他"]),
            ("对应合同", True, "select", "请选择", ["GTGYL-MSXS-20260127-s"]),
            ("付款金额", True, "text", "¥ 3,400,000"),
            ("付款方式", True, "select", "请选择", ["线下转账", "银行承兑", "商业汇票"]),
            ("计划付款日期", True, "text", "选择日期"),
            ("付款用途", True, "textarea", "详细说明付款用途"),
            ("凭证上传", False, "text", "点击上传凭证"),
        ],
    })
    render_detail_page({
        "file": "payment-detail", "name": "付款详情",
        "title": "付款详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("付款列表", "./payment-list.html"), ("付款详情", None)],
        "status": ("待审批", "tag-yellow"),
        "info_rows": [
            [("付款单号", "FK-20260126-001"), ("收款方", "中粮贸易"), ("付款类型", "货款")],
            [("对应合同", "GTGYL-MSXS-20260127-s"), ("付款金额", "¥ 3,400,000"), ("付款方式", "线下转账")],
        ],
        "tabs": [("付款信息", True), ("审批记录", False), ("凭证", False), ("操作记录", False)],
    })
    render_list_page({
        "file": "refund-list", "name": "退款列表",
        "title": "退款列表", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("退款列表", None)],
        "filter_fields": [("退款单号", "text", "请输入"), ("退款方", "text", "请输入"), ("退款类型", "select", "请选择", ["货款退款", "保证金退款"])],
        "status_tabs": [("全部", "12", True), ("待审批", "3", False), ("已退款", "8", False), ("已驳回", "1", False)],
    })
    render_form_page({
        "file": "refund-apply", "name": "退款申请",
        "title": "退款申请", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("退款列表", "./refund-list.html"), ("退款申请", None)],
        "fields": [
            ("退款单号", False, "text", "TK-20260126-001"),
            ("退款方", True, "select", "请选择", ["河南某客户", "其他"]),
            ("退款类型", True, "select", "请选择", ["货款退款", "保证金退款", "其他"]),
            ("原付款单", True, "select", "请选择", ["FK-20260120-001"]),
            ("退款金额", True, "text", "¥ 500,000"),
            ("退款原因", True, "textarea", "详细说明退款原因"),
        ],
    })
    render_detail_page({
        "file": "refund-detail", "name": "退款详情",
        "title": "退款详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("退款列表", "./refund-list.html"), ("退款详情", None)],
        "status": ("已退款", "tag-green"),
        "info_rows": [
            [("退款单号", "TK-20260125-001"), ("退款方", "河南某客户"), ("退款类型", "货款退款")],
            [("原付款单", "FK-20260120-001"), ("退款金额", "¥ 500,000"), ("退款日期", "2026-01-25")],
        ],
        "tabs": [("退款信息", True), ("审批记录", False), ("凭证", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "receipt-claim", "name": "回款认领操作",
        "title": "回款认领操作", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("回款列表", "./receipt-list.html"), ("回款认领操作", None)],
        "fields": [
            ("付款方", True, "select", "请选择", ["河南双汇集团"]),
            ("到账金额", True, "text", "¥ 4,560,000"),
            ("到账日期", True, "text", "选择日期"),
            ("对应销售合同", True, "select", "请选择", ["XS-MSXS-20260125-s"]),
            ("匹配方式", True, "select", "请选择", ["订单号自动匹配", "金额匹配", "手动匹配"]),
            ("匹配分", True, "text", "98/100"),
            ("凭证上传", False, "text", "点击上传凭证"),
        ],
    })
    render_detail_page({
        "file": "receipt-claim-detail", "name": "回款认领详情",
        "title": "回款认领详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("回款列表", "./receipt-list.html"), ("回款认领详情", None)],
        "status": ("已认领", "tag-green"),
        "info_rows": [
            [("付款方", "河南双汇集团"), ("到账金额", "¥ 4,560,000"), ("到账日期", "2026-01-26")],
            [("对应销售合同", "XS-MSXS-20260125-s"), ("匹配方式", "订单号自动匹配"), ("匹配分", "98/100")],
        ],
        "tabs": [("回款信息", True), ("认领详情", False), ("匹配记录", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "margin-adjust", "name": "保证金调整",
        "title": "保证金调整", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("保证金管理", "./margin-pool.html"), ("保证金调整", None)],
        "fields": [
            ("客户", True, "select", "请选择", ["河南军牧原国际贸易", "河南双汇集团"]),
            ("调整类型", True, "select", "请选择", ["追加", "减少", "全额释放"]),
            ("调整金额", True, "text", "¥ 1,000,000"),
            ("调整原因", True, "textarea", "详细说明调整原因"),
            ("生效日期", True, "text", "选择日期"),
            ("附件上传", False, "text", "点击上传"),
        ],
    })
    render_list_page({
        "file": "margin-record", "name": "调整记录",
        "title": "保证金调整记录", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("资金管理", None), ("保证金管理", "./margin-pool.html"), ("调整记录", None)],
        "filter_fields": [("客户", "text", "请输入"), ("调整类型", "select", "请选择", ["追加", "减少", "全额释放"])],
        "status_tabs": [("全部", "32", True), ("已生效", "28", False), ("已驳回", "4", False)],
    })

    # === 结算单 4 个缺 ===
    render_form_page({
        "file": "settlement-purchase-new", "name": "新增/编辑采购结算单",
        "title": "新增/编辑采购结算单", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("结算单管理", None), ("采购结算", "./settlement-purchase.html"), ("新增/编辑采购结算单", None)],
        "fields": [
            ("结算单号", False, "text", "JS-20260126-001"),
            ("供应商", True, "select", "请选择", ["中粮贸易"]),
            ("对应采购合同", True, "select", "请选择", ["GTGYL-MSXS-20260127-s"]),
            ("结算数量", True, "text", "1,000 吨"),
            ("结算单价", True, "text", "3,400 元/吨"),
            ("结算金额", False, "text", "¥ 3,400,000"),
            ("结算日期", True, "text", "选择日期"),
            ("结算类型", True, "select", "请选择", ["线下结算", "线上结算"]),
        ],
    })
    render_detail_page({
        "file": "settlement-purchase-detail", "name": "采购结算单详情",
        "title": "采购结算单详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("结算单管理", None), ("采购结算", "./settlement-purchase.html"), ("采购结算单详情", None)],
        "status": ("已结算", "tag-green"),
        "info_rows": [
            [("结算单号", "JS-20260120-001"), ("供应商", "中粮贸易"), ("对应合同", "GTGYL-MSXS-20260127-s")],
            [("结算数量", "1,000 吨"), ("结算金额", "¥ 3,400,000"), ("结算日期", "2026-01-20")],
        ],
        "tabs": [("结算信息", True), ("付款记录", False), ("发票", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "settlement-sales-new", "name": "新增/编辑销售结算单",
        "title": "新增/编辑销售结算单", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("结算单管理", None), ("销售结算", "./settlement-sales.html"), ("新增/编辑销售结算单", None)],
        "fields": [
            ("结算单号", False, "text", "JS-20260126-002"),
            ("客户", True, "select", "请选择", ["河南双汇集团"]),
            ("对应销售合同", True, "select", "请选择", ["XS-MSXS-20260125-s"]),
            ("结算数量", True, "text", "1,200 吨"),
            ("结算单价", True, "text", "3,800 元/吨"),
            ("结算金额", False, "text", "¥ 4,560,000"),
            ("结算日期", True, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "settlement-sales-detail", "name": "销售结算单详情",
        "title": "销售结算单详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("结算单管理", None), ("销售结算", "./settlement-sales.html"), ("销售结算单详情", None)],
        "status": ("已结算", "tag-green"),
        "info_rows": [
            [("结算单号", "JS-20260125-001"), ("客户", "河南双汇集团"), ("对应合同", "XS-MSXS-20260125-s")],
            [("结算数量", "1,200 吨"), ("结算金额", "¥ 4,560,000"), ("结算日期", "2026-01-25")],
        ],
        "tabs": [("结算信息", True), ("回款记录", False), ("发票", False), ("操作记录", False)],
    })

    # === 风险 4 个缺 ===
    render_detail_page({
        "file": "market-price-detail", "name": "指标详情",
        "title": "指标详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("盯市价格管理", "./market-price.html"), ("指标详情", None)],
        "status": ("监控中", "tag-blue"),
        "info_rows": [
            [("指标名称", "玉米价格"), ("监控来源", "Wind 大商所"), ("预警阈值", "±5%")],
            [("当前价格", "¥ 2,780/吨"), ("昨日收盘", "¥ 2,750/吨"), ("涨跌幅", "+1.09%")],
        ],
        "tabs": [("实时价格", True), ("历史趋势", False), ("预警记录", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "bond-letter-new", "name": "新增/编辑追保函",
        "title": "新增/编辑追保函", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("追保函管理", "./bond-letter.html"), ("新增/编辑追保函", None)],
        "fields": [
            ("追保函号", False, "text", "ZB-20260126-001"),
            ("客户", True, "select", "请选择", ["中粮贸易"]),
            ("追保类型", True, "select", "请选择", ["电子追保函", "线下追保函"]),
            ("触发原因", True, "select", "请选择", ["盯市预警", "额度不足", "其他"]),
            ("追保金额", True, "text", "¥ 5,000,000"),
            ("生效日期", True, "text", "选择日期"),
            ("到期日期", True, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "bond-letter-detail", "name": "追保函详情",
        "title": "追保函详情", "menu_group": "scm",
        "active_top": "scm",
        "breadcrumb": [("数字供应链", None), ("追保函管理", "./bond-letter.html"), ("追保函详情", None)],
        "status": ("生效中", "tag-green"),
        "info_rows": [
            [("追保函号", "ZB-20260125-001"), ("客户", "中粮贸易"), ("追保类型", "电子追保函")],
            [("追保金额", "¥ 5,000,000"), ("触发原因", "盯市预警"), ("签发日期", "2026-01-25")],
            [("生效日期", "2026-01-26"), ("到期日期", "2026-04-25"), ("状态", "已签收")],
        ],
        "tabs": [("追保信息", True), ("函件内容", False), ("签收记录", False), ("操作记录", False)],
    })

    # === 仓储 6 个缺 ===
    render_form_page({
        "file": "warehouse-inbound-new", "name": "新增入库",
        "title": "新增入库", "menu_group": "wh",
        "active_top": "wh",
        "breadcrumb": [("仓储管理", None), ("入库记录", "./warehouse-inbound.html"), ("新增入库", None)],
        "fields": [
            ("入库单号", False, "text", "RK-20260126-001"),
            ("对应采购合同", True, "select", "请选择", ["GTGYL-MSXS-20260127-s"]),
            ("供应商", True, "select", "请选择", ["中粮贸易"]),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
            ("入库数量", True, "text", "2,000 吨"),
            ("入库仓库", True, "select", "请选择", ["新郑库 A-01", "郑州库 B-02", "洛阳库 C-03"]),
            ("货位", True, "text", "A-01-12"),
            ("入库日期", True, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "warehouse-inbound-detail", "name": "入库详情",
        "title": "入库详情", "menu_group": "wh",
        "active_top": "wh",
        "breadcrumb": [("仓储管理", None), ("入库记录", "./warehouse-inbound.html"), ("入库详情", None)],
        "status": ("已入库", "tag-green"),
        "info_rows": [
            [("入库单号", "RK-20260126-001"), ("供应商", "中粮贸易"), ("品名", "玉米")],
            [("入库数量", "2,000 吨"), ("入库仓库", "新郑库 A-01"), ("货位", "A-01-12")],
            [("入库日期", "2026-01-26"), ("对应合同", "GTGYL-MSXS-20260127-s"), ("状态", "已入库")],
        ],
        "tabs": [("入库信息", True), ("货位详情", False), ("质检记录", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "warehouse-outbound-new", "name": "新增出库",
        "title": "新增出库", "menu_group": "wh",
        "active_top": "wh",
        "breadcrumb": [("仓储管理", None), ("出库记录", "./warehouse-outbound.html"), ("新增出库", None)],
        "fields": [
            ("出库单号", False, "text", "CK-20260126-001"),
            ("对应销售合同", True, "select", "请选择", ["XS-MSXS-20260125-s"]),
            ("客户", True, "select", "请选择", ["河南双汇集团"]),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
            ("出库数量", True, "text", "1,200 吨"),
            ("出库仓库", True, "select", "请选择", ["新郑库 A-01", "郑州库 B-02"]),
            ("货位", True, "text", "A-01-12"),
            ("出库日期", True, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "warehouse-outbound-detail", "name": "出库详情",
        "title": "出库详情", "menu_group": "wh",
        "active_top": "wh",
        "breadcrumb": [("仓储管理", None), ("出库记录", "./warehouse-outbound.html"), ("出库详情", None)],
        "status": ("已出库", "tag-green"),
        "info_rows": [
            [("出库单号", "CK-20260126-001"), ("客户", "河南双汇集团"), ("品名", "玉米")],
            [("出库数量", "1,200 吨"), ("出库仓库", "新郑库 A-01"), ("货位", "A-01-12")],
            [("出库日期", "2026-01-26"), ("对应合同", "XS-MSXS-20260125-s"), ("运单号", "YD20260126001")],
        ],
        "tabs": [("出库信息", True), ("货位详情", False), ("运输跟踪", False), ("操作记录", False)],
    })
    render_form_page({
        "file": "warehouse-release-new", "name": "新增放货指令",
        "title": "新增放货指令", "menu_group": "wh",
        "active_top": "wh",
        "breadcrumb": [("仓储管理", None), ("放货管理", "./warehouse-release.html"), ("新增放货指令", None)],
        "fields": [
            ("指令单号", False, "text", "FH-20260126-002"),
            ("客户", True, "select", "请选择", ["河南双汇集团"]),
            ("品名", True, "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]),
            ("放货数量", True, "text", "1,200 吨"),
            ("对应销售合同", True, "select", "请选择", ["XS-MSXS-20260125-s"]),
            ("货位", True, "text", "A-01-12"),
            ("申请人", True, "select", "请选择", ["张爽", "王浩", "宋美玲"]),
            ("申请日期", True, "text", "选择日期"),
        ],
    })
    render_detail_page({
        "file": "warehouse-release-detail", "name": "放货指令详情",
        "title": "放货指令详情", "menu_group": "wh",
        "active_top": "wh",
        "breadcrumb": [("仓储管理", None), ("放货管理", "./warehouse-release.html"), ("放货指令详情", None)],
        "status": ("已放货", "tag-green"),
        "info_rows": [
            [("指令单号", "FH-20260126-001"), ("客户", "河南双汇集团"), ("品名", "玉米")],
            [("放货数量", "1,200 吨"), ("对应销售合同", "XS-MSXS-20260125-s"), ("货位", "A-01-12")],
            [("申请人", "张爽"), ("申请日期", "2026-01-26"), ("审批人", "王浩")],
        ],
        "tabs": [("指令信息", True), ("审批记录", False), ("出库记录", False), ("操作记录", False)],
    })

    # === 预警 1 个缺 ===
    render_detail_page({
        "file": "warning-detail", "name": "预警详情",
        "title": "预警详情", "menu_group": "warn",
        "active_top": "warn",
        "breadcrumb": [("预警中心", None), ("预警列表", "./warning-list.html"), ("预警详情", None)],
        "status": ("未处理", "tag-red"),
        "info_rows": [
            [("预警编号", "WJ-20260126-001"), ("预警类型", "价格波动"), ("触发规则", "玉米价格下跌 ≥ 3%")],
            [("当前值", "¥ 2,650/吨"), ("基准值", "¥ 2,750/吨"), ("波动幅度", "96%")],
            [("触发时间", "2026-01-26 14:30"), ("紧急程度", "高"), ("涉及业务线", "SKYWX202601050001")],
        ],
        "tabs": [("预警信息", True), ("触发详情", False), ("处理记录", False), ("操作记录", False)],
    })

    # === 数据中心 6 个缺 ===
    render_list_page({
        "file": "report-fund", "name": "资金占压表",
        "title": "资金占压表", "menu_group": "dc",
        "active_top": "dc",
        "breadcrumb": [("数据中心", None), ("资金占压表", None)],
        "filter_fields": [("统计周期", "text", "开始 ~ 结束"), ("客户", "text", "请输入"), ("业务类型", "select", "请选择", ["全部", "存货业务", "预付业务"])],
        "status_tabs": [("按月", "12", True), ("按季", "4", False), ("按年", "1", False)],
    })
    render_list_page({
        "file": "report-inventory", "name": "库存明细表",
        "title": "库存明细表", "menu_group": "dc",
        "active_top": "dc",
        "breadcrumb": [("数据中心", None), ("库存明细表", None)],
        "filter_fields": [("仓库", "select", "请选择", ["新郑库", "郑州库", "洛阳库"]), ("品名", "select", "请选择", ["玉米", "糖粉", "木薯淀粉"]), ("货位", "text", "请输入")],
        "status_tabs": [("全部", "1,236", True), ("在库", "1,180", False), ("锁定", "56", False)],
    })
    render_list_page({
        "file": "report-ar-ap", "name": "应收应付表",
        "title": "应收应付表", "menu_group": "dc",
        "active_top": "dc",
        "breadcrumb": [("数据中心", None), ("应收应付表", None)],
        "filter_fields": [("客户", "text", "请输入"), ("类型", "select", "请选择", ["应收", "应付"]), ("账期", "select", "请选择", ["30天内", "30-60天", "60-90天", "90天以上"])],
        "status_tabs": [("全部", "256", True), ("应收", "128", False), ("应付", "128", False)],
    })
    render_list_page({
        "file": "report-risk", "name": "风控统计报表",
        "title": "风控统计报表", "menu_group": "dc",
        "active_top": "dc",
        "breadcrumb": [("数据中心", None), ("风控统计报表", None)],
        "filter_fields": [("统计周期", "text", "开始 ~ 结束"), ("风险类型", "select", "请选择", ["全部", "价格波动", "企业监控", "交易监控"])],
        "status_tabs": [("按月", "12", True), ("按季", "4", False), ("按年", "1", False)],
    })
    render_list_page({
        "file": "report-compliance", "name": "合规验证报告列表",
        "title": "合规验证报告列表", "menu_group": "dc",
        "active_top": "dc",
        "breadcrumb": [("数据中心", None), ("合规验证报告列表", None)],
        "filter_fields": [("报告编号", "text", "请输入"), ("客户", "text", "请输入"), ("验证状态", "select", "请选择", ["全部", "通过", "不通过", "待验证"])],
        "status_tabs": [("全部", "186", True), ("通过", "162", False), ("不通过", "12", False), ("待验证", "12", False)],
    })
    render_detail_page({
        "file": "report-compliance-detail", "name": "合规报告详情",
        "title": "合规报告详情", "menu_group": "dc",
        "active_top": "dc",
        "breadcrumb": [("数据中心", None), ("合规验证报告列表", "./report-compliance.html"), ("合规报告详情", None)],
        "status": ("通过", "tag-green"),
        "info_rows": [
            [("报告编号", "BG-20260126-001"), ("客户", "河南军牧原国际贸易"), ("验证日期", "2026-01-26")],
            [("验证人", "王芳（风控）"), ("验证结论", "通过"), ("合规率", "98.5%")],
        ],
        "tabs": [("报告概览", True), ("合规明细", False), ("附件", False), ("操作记录", False)],
    })


if __name__ == "__main__":
    gen_all()
    print("\n✅ Done.")
