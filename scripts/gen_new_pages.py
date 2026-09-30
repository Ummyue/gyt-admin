#!/usr/bin/env python3
"""
gen_new_pages.py — 批量生成 v1.2 新 HTML 占位页
根据用户图 1:1 菜单结构 + B 方案（独立 HTML）

每个新 HTML 模板：
- 顶 nav（v1.6 7 menu）
- 左 sidemenu（v1.2 JS 渲染）
- 面包屑
- 标题
- 简单 mock 列表（占位）
- drawer.js + left-sidemenu.js 引用
"""
import os

PAGES_DIR = '/Users/fuyu/.mavis/agents/mavis/workspace/yugangtong-prototype/pages'

# 7 menu 顺序（与 fix_topbar_nav.py MODULES 保持一致）
TOPBAR_HTML = '''    <div class="topbar-menu">
      <a class="topbar-menu-item" href="./workbench.html" data-menu-key="工作台">工作台</a>
      <a class="topbar-menu-item" href="./project-list.html" data-menu-key="准入管理">准入管理</a>
      <a class="topbar-menu-item" href="./contract-purchase.html" data-menu-key="数字供应链">数字供应链</a>
      <a class="topbar-menu-item" href="./warehouse-inbound.html" data-menu-key="仓储管理">仓储管理</a>
      <a class="topbar-menu-item" href="./risk-cockpit.html" data-menu-key="风险运营管理">风险运营管理</a>
      <a class="topbar-menu-item" href="./warning-list.html" data-menu-key="预警中心">预警中心</a>
      <a class="topbar-menu-item" href="./account-personal.html" data-menu-key="账户中心">账户中心</a>
    </div>'''

DRAWER_JS = '<script src="../shared/js/topnav-drawer.js"></script>'
LEFT_JS = '<script src="../shared/js/left-sidemenu.js"></script>'

# 新 HTML 配置：(filename, page_title, breadcrumb, filter_fields, table_columns, table_rows)
NEW_PAGES = [
    # ===== 数字供应链（2 个）=====
    {
        'file': 'collection-list.html',
        'title': '回款管理 - 豫港通',
        'breadcrumb': '数字供应链 / 资金管理 / 回款管理',
        'h1': '回款管理',
        'tabs': [('全部', 24, True), ('待回款', 8), ('已回款', 14), ('逾期', 2)],
        'filters': ['回款单号', '客户名称', '回款日期', '回款状态'],
        'columns': ['回款单号', '客户名称', '回款金额(元)', '回款日期', '回款方式', '关联合同', '状态', '操作'],
        'rows': [
            ('HK-20260127-001', '中粮贸易有限公司', '¥2,300,000.00', '2026-07-20', '银行转账', 'GTGYL-MSXS-20260127-001', '已回款', '详情/凭证'),
            ('HK-20260127-002', '河南诚泽运输有限公司', '¥1,850,000.00', '2026-07-18', '银行转账', 'GTGYL-XSXS-20260125-008', '已回款', '详情/凭证'),
            ('HK-20260127-003', '河北粮食产业集团', '¥3,600,000.00', '2026-07-25', '银行承兑', 'GTGYL-MSXS-20260120-005', '待回款', '详情/催收'),
            ('HK-20260127-004', '山东粮油集团', '¥1,200,000.00', '2026-07-15', '—', 'GTGYL-XSXS-20260110-003', '逾期', '详情/催收'),
        ]
    },
    {
        'file': 'margin-list.html',
        'title': '保证金管理 - 豫港通',
        'breadcrumb': '数字供应链 / 资金管理 / 保证金管理',
        'h1': '保证金管理',
        'tabs': [('全部', 18, True), ('缴存中', 4), ('已缴存', 11), ('已退还', 3)],
        'filters': ['保证金单号', '缴存方', '业务类型', '缴存日期'],
        'columns': ['保证金单号', '缴存方', '业务类型', '保证金额(元)', '缴存日期', '到期日期', '状态', '操作'],
        'rows': [
            ('BZJ-20260127-001', '中粮贸易有限公司', '预付融资', '¥1,200,000.00', '2026-07-15', '2026-12-15', '已缴存', '详情/退还'),
            ('BZJ-20260127-002', '河北粮食产业集团', '存货融资', '¥800,000.00', '2026-07-20', '2027-01-20', '已缴存', '详情/退还'),
            ('BZJ-20260127-003', '山东粮油集团', '购销融资', '¥500,000.00', '2026-07-25', '2026-10-25', '缴存中', '详情/确认'),
        ]
    },

    # ===== 仓储管理（9 个）=====
    {
        'file': 'warehouse-pickup.html',
        'title': '提货管理 - 豫港通',
        'breadcrumb': '仓储管理 / 提放货管理 / 提货管理',
        'h1': '提货管理',
        'tabs': [('全部', 32, True), ('待提货', 8), ('已提货', 21), ('已取消', 3)],
        'filters': ['提货单号', '提货方', '仓库名称', '提货日期'],
        'columns': ['提货单号', '提货方', '关联入库单', '品名', '提货数量(吨)', '提货日期', '状态', '操作'],
        'rows': [
            ('TH-20260127-001', '河南诚泽运输有限公司', 'RK-20260126-001', '玉米', '2,000', '2026-07-25', '已提货', '详情/凭证'),
            ('TH-20260127-002', '中粮贸易有限公司', 'RK-20260120-003', '木薯淀粉', '1,500', '2026-07-26', '待提货', '详情/确认'),
            ('TH-20260127-003', '河北粮食产业集团', 'RK-20260115-002', '大豆', '3,000', '2026-07-27', '待提货', '详情/确认'),
        ]
    },
    {
        'file': 'warehouse-inventory.html',
        'title': '库存台账 - 豫港通',
        'breadcrumb': '仓储管理 / 库存管理 / 库存台账',
        'h1': '库存台账',
        'tabs': [('全部', 156, True), ('正常', 132), ('临期', 18), ('已质押', 6)],
        'filters': ['存货编号', '品名', '仓库名称', '存货日期'],
        'columns': ['存货编号', '品名', '仓库', '库房-货位', '数量(吨)', '单价(元/吨)', '金额(元)', '状态'],
        'rows': [
            ('CH-20260120-001', '玉米', '新郑库A-01', 'A-01-12', '5,000', '2,800', '¥14,000,000', '已质押'),
            ('CH-20260120-002', '木薯淀粉', '中欧班列集结库', 'B-02-08', '3,500', '3,400', '¥11,900,000', '正常'),
            ('CH-20260120-003', '大豆', '新郑库A-02', 'A-02-15', '8,000', '4,200', '¥33,600,000', '正常'),
            ('CH-20260125-001', '进口木薯淀粉', '中欧班列集结库', 'B-01-05', '2,037', '3,400', '¥6,925,800', '临期'),
        ]
    },
    {
        'file': 'warehouse-market.html',
        'title': '库存盯市 - 豫港通',
        'breadcrumb': '仓储管理 / 库存管理 / 库存盯市',
        'h1': '库存盯市',
        'tabs': [('全部', 48, True), ('正常', 38), ('预警', 8), ('强平', 2)],
        'filters': ['盯市单号', '品名', '盯市日期', '盯市状态'],
        'columns': ['盯市单号', '品名', '数量(吨)', '盯市价格(元/吨)', '盯市总值(元)', '盯市日期', '盯市状态', '操作'],
        'rows': [
            ('DS-20260127-001', '玉米', '5,000', '2,820', '¥14,100,000', '2026-07-25', '正常', '详情/调整'),
            ('DS-20260127-002', '大豆', '8,000', '4,150', '¥33,200,000', '2026-07-25', '预警', '详情/补保'),
            ('DS-20260127-003', '木薯淀粉', '3,500', '3,380', '¥11,830,000', '2026-07-25', '正常', '详情/调整'),
        ]
    },
    {
        'file': 'warehouse-video.html',
        'title': '库点监控 - 豫港通',
        'breadcrumb': '仓储管理 / 视频监控 / 库点监控',
        'h1': '库点监控',
        'tabs': [('全部', 24, True), ('在线', 21), ('离线', 2), ('故障', 1)],
        'filters': ['摄像头编号', '库点名称', '摄像头位置', '在线状态'],
        'columns': ['摄像头编号', '库点', '位置', '在线状态', '最后心跳', '实时画面', '操作'],
        'rows': [
            ('CAM-001', '新郑库A区', 'A-01 入口', '在线', '2026-07-27 11:30', '查看', '详情/回放'),
            ('CAM-002', '新郑库A区', 'A-01 库内', '在线', '2026-07-27 11:30', '查看', '详情/回放'),
            ('CAM-003', '中欧班列集结库', 'B-02 卸货区', '在线', '2026-07-27 11:30', '查看', '详情/回放'),
            ('CAM-004', '中欧班列集结库', 'B-01 巡逻点', '离线', '2026-07-27 09:15', '—', '详情/报修'),
        ]
    },
    {
        'file': 'warehouse-patrol.html',
        'title': '巡库记录 - 豫港通',
        'breadcrumb': '仓储管理 / 巡库管理 / 巡库记录',
        'h1': '巡库记录',
        'tabs': [('全部', 86, True), ('已完成', 78), ('巡检中', 6), ('异常', 2)],
        'filters': ['巡检单号', '巡检员', '巡检日期', '巡检状态'],
        'columns': ['巡检单号', '库点', '巡检员', '巡检日期', '巡检项目', '巡检结果', '状态', '操作'],
        'rows': [
            ('XJ-20260127-001', '新郑库A区', '李建国', '2026-07-25', '库存盘点+安防检查', '正常', '已完成', '详情/凭证'),
            ('XJ-20260127-002', '中欧班列集结库', '王志强', '2026-07-26', '库存盘点+温湿度', '正常', '已完成', '详情/凭证'),
            ('XJ-20260127-003', '新郑库B区', '李建国', '2026-07-27', '库存盘点+安防检查', '巡检中', '巡检中', '详情/签到'),
        ]
    },
    {
        'file': 'warehouse-system.html',
        'title': '库点信息管理 - 豫港通',
        'breadcrumb': '仓储管理 / 系统管理 / 库点信息管理',
        'h1': '库点信息管理',
        'tabs': [('全部', 12, True), ('启用', 10), ('停用', 2)],
        'filters': ['库点编号', '库点名称', '所属区域', '库点状态'],
        'columns': ['库点编号', '库点名称', '所属区域', '库房数', '总面积(㎡)', '启用日期', '状态', '操作'],
        'rows': [
            ('KD-001', '新郑库A区', '郑州新郑', '8', '12,000', '2024-03-15', '启用', '详情/编辑'),
            ('KD-002', '中欧班列集结库', '郑州国际陆港', '12', '18,500', '2024-06-20', '启用', '详情/编辑'),
            ('KD-003', '新郑库B区', '郑州新郑', '6', '8,800', '2025-01-10', '启用', '详情/编辑'),
        ]
    },
    {
        'file': 'warehouse-point.html',
        'title': '库点信息管理 - 豫港通',
        'breadcrumb': '仓储管理 / 系统管理 / 库点信息管理',
        'h1': '库点信息管理',
        'tabs': [('全部', 12, True), ('启用', 10), ('停用', 2)],
        'filters': ['库点编号', '库点名称', '所属区域', '库点状态'],
        'columns': ['库点编号', '库点名称', '所属区域', '库房数', '总面积(㎡)', '启用日期', '状态', '操作'],
        'rows': [
            ('KD-001', '新郑库A区', '郑州新郑', '8', '12,000', '2024-03-15', '启用', '详情/编辑'),
            ('KD-002', '中欧班列集结库', '郑州国际陆港', '12', '18,500', '2024-06-20', '启用', '详情/编辑'),
        ]
    },
    {
        'file': 'warehouse-warehouse.html',
        'title': '仓库管理 - 豫港通',
        'breadcrumb': '仓储管理 / 系统管理 / 仓库管理',
        'h1': '仓库管理',
        'tabs': [('全部', 26, True), ('启用', 24), ('停用', 2)],
        'filters': ['仓库编号', '仓库名称', '所属库点', '仓库状态'],
        'columns': ['仓库编号', '仓库名称', '所属库点', '类型', '面积(㎡)', '启用日期', '状态', '操作'],
        'rows': [
            ('WH-001', 'A-01 库', '新郑库A区', '平房仓', '1,500', '2024-03-15', '启用', '详情/编辑'),
            ('WH-002', 'A-02 库', '新郑库A区', '平房仓', '1,500', '2024-03-15', '启用', '详情/编辑'),
            ('WH-003', 'B-01 库', '中欧班列集结库', '立体仓', '2,200', '2024-06-20', '启用', '详情/编辑'),
        ]
    },
    {
        'file': 'warehouse-category.html',
        'title': '品类配置 - 豫港通',
        'breadcrumb': '仓储管理 / 系统管理 / 品类配置',
        'h1': '品类配置',
        'tabs': [('全部', 18, True), ('启用', 16), ('停用', 2)],
        'filters': ['品类编号', '品类名称', '品类分类', '品类状态'],
        'columns': ['品类编号', '品类名称', '品类分类', '单位', '存储条件', '保质期(天)', '状态', '操作'],
        'rows': [
            ('PL-001', '玉米', '粮食类', '吨', '常温干燥', '720', '启用', '详情/编辑'),
            ('PL-002', '大豆', '粮食类', '吨', '常温干燥', '540', '启用', '详情/编辑'),
            ('PL-003', '木薯淀粉', '粮食加工类', '吨', '常温干燥', '365', '启用', '详情/编辑'),
        ]
    },

    # ===== 风险运营管理（3 个）=====
    {
        'file': 'risk-cockpit.html',
        'title': '驾驶舱 - 豫港通',
        'breadcrumb': '风险运营管理 / 驾驶舱',
        'h1': '风险运营驾驶舱',
        'tabs': [('总览', 1, True), ('业务概览', 1), ('风险概览', 1), ('预警概览', 1)],
        'filters': [],
        'columns': [],
        'rows': [],
        'is_cockpit': True
    },
    {
        'file': 'risk-report.html',
        'title': '业务报表 - 豫港通',
        'breadcrumb': '风险运营管理 / 业务报表',
        'h1': '业务报表',
        'tabs': [('项目台账', 0, True), ('业务线台账', 0), ('资金占压表', 0), ('库存明细表', 0), ('应收应付表', 0), ('风控统计报表', 0)],
        'filters': ['项目编号', '项目名称', '业务线', '报表日期'],
        'columns': ['项目编号', '项目名称', '业务线', '业务类型', '合同金额(元)', '在管金额(元)', '敞口金额(元)', '报表日期'],
        'rows': [
            ('LX20260120-001', '中粮贸易玉米存货融资', '粮食-玉米', '存货类', '¥50,000,000', '¥30,000,000', '¥20,000,000', '2026-07-25'),
            ('LX20260115-002', '河北粮食大豆存货融资', '粮食-大豆', '存货类', '¥80,000,000', '¥50,000,000', '¥30,000,000', '2026-07-25'),
        ]
    },
    {
        'file': 'risk-compliance.html',
        'title': '合规验证报告管理 - 豫港通',
        'breadcrumb': '风险运营管理 / 合规验证报告管理',
        'h1': '合规验证报告管理',
        'tabs': [('全部', 32, True), ('待验证', 8), ('验证中', 6), ('已完成', 18)],
        'filters': ['报告编号', '项目名称', '验证类型', '验证日期'],
        'columns': ['报告编号', '项目名称', '验证类型', '验证机构', '验证日期', '验证结果', '状态', '操作'],
        'rows': [
            ('HG-20260127-001', '中粮贸易玉米存货融资', '资金合规', '立信会计师事务所', '2026-07-20', '合规', '已完成', '详情/下载'),
            ('HG-20260127-002', '河北粮食大豆存货融资', '业务合规', '大华会计师事务所', '2026-07-25', '合规', '已完成', '详情/下载'),
            ('HG-20260127-003', '山东粮油玉米购销', '业务合规', '—', '2026-07-27', '—', '待验证', '详情/分配'),
        ]
    },

    # ===== 账户中心（2 个）=====
    {
        'file': 'account-personal.html',
        'title': '个人管理 - 豫港通',
        'breadcrumb': '账户中心 / 个人管理',
        'h1': '个人管理',
        'tabs': [('基本信息', 1, True), ('账号安全', 1), ('操作日志', 1)],
        'filters': [],
        'columns': [],
        'rows': [],
        'is_account': True
    },
    {
        'file': 'account-company.html',
        'title': '企业管理 - 豫港通',
        'breadcrumb': '账户中心 / 个人管理 / 企业管理',
        'h1': '企业管理',
        'tabs': [('基本信息', 1, True), ('组织架构', 1), ('权限管理', 1)],
        'filters': [],
        'columns': [],
        'rows': [],
        'is_account': True
    },
]


def gen_filter_html(filters):
    if not filters:
        return ''
    items = ''.join(f'<input type="text" placeholder="请输入{f}" class="filter-input">\n        ' for f in filters)
    return f'''    <div class="filter-bar">
        {items}
        <button class="btn btn-primary btn-sm">查询</button>
        <button class="btn btn-default btn-sm">重置</button>
    </div>'''


def gen_tabs_html(tabs):
    if not tabs:
        return ''
    items = []
    for tab in tabs:
        if len(tab) == 2:
            label, count = tab
            active = False
        else:
            label, count, active = tab
        cls = 'tab-item active' if active else 'tab-item'
        items.append(f'<div class="{cls}">{label} <span class="tab-count">{count}</span></div>')
    return f'''    <div class="tab-bar">
        {chr(10).join(items)}
    </div>'''


def gen_table_html(columns, rows):
    if not columns:
        return ''
    th = ''.join(f'<th>{c}</th>' for c in columns)
    trs = []
    for r in rows:
        cells = ''.join(f'<td>{c}</td>' for c in r)
        trs.append(f'<tr>{cells}</tr>')
    return f'''    <table class="data-table">
      <thead><tr>{th}</tr></thead>
      <tbody>
        {chr(10).join(trs)}
      </tbody>
    </table>'''


def gen_cockpit_html(h1):
    """驾驶舱：4 个大卡片 + 简单图表占位"""
    return f'''    <div class="dashboard-grid">
      <div class="dashboard-card">
        <div class="dashboard-card-title">在管项目数</div>
        <div class="dashboard-card-value">28</div>
        <div class="dashboard-card-trend up">↑ 4 较上月</div>
      </div>
      <div class="dashboard-card">
        <div class="dashboard-card-title">在管金额(亿元)</div>
        <div class="dashboard-card-value">3.86</div>
        <div class="dashboard-card-trend up">↑ 12.5% 较上月</div>
      </div>
      <div class="dashboard-card">
        <div class="dashboard-card-title">风险预警数</div>
        <div class="dashboard-card-value">8</div>
        <div class="dashboard-card-trend down">↓ 2 较上周</div>
      </div>
      <div class="dashboard-card">
        <div class="dashboard-card-title">合规验证完成率</div>
        <div class="dashboard-card-value">96.5%</div>
        <div class="dashboard-card-trend up">↑ 1.2% 较上月</div>
      </div>
    </div>
    <div class="dashboard-charts" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;">
      <div class="dashboard-panel" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="margin: 0 0 12px 0; font-size: 14px; color: #475569;">在管金额趋势（近 6 个月）</h3>
        <div style="height: 240px; display: flex; align-items: center; justify-content: center; color: #94a3b8; background: #f8fafc; border-radius: 6px;">[折线图占位]</div>
      </div>
      <div class="dashboard-panel" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="margin: 0 0 12px 0; font-size: 14px; color: #475569;">业务类型分布</h3>
        <div style="height: 240px; display: flex; align-items: center; justify-content: center; color: #94a3b8; background: #f8fafc; border-radius: 6px;">[饼图占位]</div>
      </div>
    </div>'''


def gen_account_html(h1):
    """账户中心：3 个 info card"""
    return f'''    <div class="account-cards" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
      <div class="account-card" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="margin: 0 0 16px 0; font-size: 14px; color: #475569;">基本信息</h3>
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, #1E40AF, #3B82F6); color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700;">张</div>
          <div>
            <div style="font-size: 16px; font-weight: 500; color: #1e293b;">张爽</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">港通供应链 / 业务部</div>
          </div>
        </div>
        <div style="font-size: 13px; color: #475569; line-height: 2;">
          <div>手机：138-XXXX-XXXX</div>
          <div>邮箱：xxx@example.com</div>
          <div>岗位：业务经理</div>
          <div>入职日期：2024-05-15</div>
        </div>
      </div>
      <div class="account-card" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="margin: 0 0 16px 0; font-size: 14px; color: #475569;">账号安全</h3>
        <div style="font-size: 13px; color: #475569; line-height: 2;">
          <div>登录密码：已设置（90 天前修改）<a href="#" style="margin-left: 8px; color: #2563eb;">修改</a></div>
          <div>手机绑定：138-XXXX-XXXX <span style="color: #16a34a;">[已绑定]</span></div>
          <div>邮箱绑定：xxx@example.com <span style="color: #16a34a;">[已绑定]</span></div>
          <div>上次登录：2026-07-27 09:15:23 (郑州市)</div>
          <div>登录设备：3 台</div>
        </div>
      </div>
    </div>'''


def gen_html(page):
    """生成单页 HTML"""
    is_cockpit = page.get('is_cockpit', False)
    is_account = page.get('is_account', False)
    body_content = ''
    if is_cockpit:
        body_content = gen_cockpit_html(page['h1'])
    elif is_account:
        body_content = gen_account_html(page['h1'])
    else:
        body_content = (
            gen_filter_html(page.get('filters', [])) + '\n'
            + gen_tabs_html(page.get('tabs', [])) + '\n'
            + gen_table_html(page.get('columns', []), page.get('rows', []))
        )

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page['title']}</title>
  <link rel="stylesheet" href="../assets/css/design-system.css">
</head>
<body>
  <div class="topbar">
  <div class="topbar-logo">
    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 16px;">豫</div>
    <span>豫港通</span>
  </div>
{TOPBAR_HTML}
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
    <div class="page-header">
      <div class="breadcrumb">{page['breadcrumb']}</div>
      <h1 class="page-title">{page['h1']}</h1>
    </div>
    <div class="page-body">
{body_content}
    </div>
  </div>
  <!-- /main-content -->
  <script src="../shared/js/topnav-drawer.js"></script>
  <script src="../shared/js/left-sidemenu.js"></script>
</body>
</html>
'''


def main():
    created = 0
    skipped = 0
    for page in NEW_PAGES:
        path = os.path.join(PAGES_DIR, page['file'])
        if os.path.exists(path):
            skipped += 1
            print(f'  ⏭ {page["file"]} (exists)')
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(gen_html(page))
        created += 1
        print(f'  ✓ {page["file"]}')
    print(f'\n✓ Created {created}, Skipped {skipped}')


if __name__ == '__main__':
    main()
