#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数字供应链平台 PRD 汇编 → Word（python-docx，Word 排版规范）"""
import io, json, os, glob, re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")
SHOTS = "/Users/fuyu/.minimax/tmp/prd-modules/shots"
OUT_DOCX = os.path.join(REPO, "docs", "数字供应链平台-产品需求文档汇编.docx")

CN = "宋体"; CN_H = "黑体"; EN = "Times New Roman"
BRAND = "数字供应链"

# ---------------- 基础工具 ----------------

def set_run(run, size=12, bold=False, cn=CN, en=EN, color=None, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = en
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:ascii'), en); rf.set(qn('w:hAnsi'), en); rf.set(qn('w:eastAsia'), cn)
    if color: run.font.color.rgb = RGBColor(*color)


def para(doc, text="", size=12, bold=False, align=None, indent_chars=0, space_before=0,
         space_after=6, line=1.5, cn=CN, color=None, style=None):
    p = doc.add_paragraph(style=style)
    pf = p.paragraph_format
    pf.space_before = Pt(space_before); pf.space_after = Pt(space_after)
    pf.line_spacing = line; pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    if indent_chars: pf.first_line_indent = Pt(size * indent_chars)
    if align is not None: p.alignment = align
    if text:
        set_run(p.add_run(text), size=size, bold=bold, cn=cn, color=color)
    return p


def heading(doc, text, level=1, page_break=False):
    if page_break:
        doc.add_page_break()
    sizes = {1: 16, 2: 14, 3: 12, 4: 11}
    p = doc.add_heading(level=level)
    pf = p.paragraph_format
    pf.space_before = Pt({1: 18, 2: 12, 3: 8, 4: 6}[level])
    pf.space_after = Pt({1: 10, 2: 6, 3: 4, 4: 3}[level])
    pf.line_spacing = 1.3; pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.first_line_indent = Pt(0)
    pf.keep_with_next = True
    set_run(p.add_run(text), size=sizes[level], bold=True, cn=CN_H)
    return p


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexcolor)
    tcPr.append(sh)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement('w:tblHeader'); el.set(qn('w:val'), 'true'); trPr.append(el)


def add_table(doc, headers, rows, widths=None, size=10.5):
    """headers: list[str]; rows: list[list[str]]; widths: list[cm]"""
    ncol = len(headers)
    t = doc.add_table(rows=1, cols=ncol)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0]
    repeat_header(hdr)
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        set_run(p.add_run(str(h)), size=size, bold=True, cn=CN_H)
        shade(c, "DCE6F1")
    for r in rows:
        row = t.add_row()
        for i, v in enumerate(r):
            c = row.cells[i]
            c.text = ""
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.first_line_indent = Pt(0)
            txt = "" if v is None else str(v)
            for j, seg in enumerate(txt.split("\n")):
                if j: p.add_run().add_break()
                set_run(p.add_run(seg), size=size)
    if widths:
        if len(widths) != ncol:
            widths = (list(widths) + [1] * ncol)[:ncol]
        total = sum(widths)
        avail = 16.0
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(avail * w / total)
    para(doc, "", size=6, space_after=0, line=1.0)
    return t


def add_figure(doc, png, caption, width_cm=15.6):
    if not png or not os.path.exists(png):
        return False
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.first_line_indent = Pt(0)
    p.add_run().add_picture(png, width=Cm(width_cm))
    cp = doc.add_paragraph(); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(0); cp.paragraph_format.space_after = Pt(10)
    cp.paragraph_format.line_spacing = 1.0
    cp.paragraph_format.first_line_indent = Pt(0)
    set_run(cp.add_run(caption), size=10.5, cn=CN)
    return True


def add_field(paragraph, instr):
    r = paragraph.add_run()
    fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'begin'); r._r.append(fc)
    r2 = paragraph.add_run()
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    r2._r.append(it)
    r3 = paragraph.add_run()
    fs = OxmlElement('w:fldChar'); fs.set(qn('w:fldCharType'), 'separate'); r3._r.append(fs)
    r4 = paragraph.add_run("（在 Word 中按 Ctrl+A 后按 F9 更新）")
    set_run(r4, size=10.5, color=(0x80, 0x80, 0x80))
    r5 = paragraph.add_run()
    fe = OxmlElement('w:fldChar'); fe.set(qn('w:fldCharType'), 'end'); r5._r.append(fe)


def bullet(doc, text, size=12, indent=0.6):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(indent); pf.first_line_indent = Pt(0)
    pf.space_before = Pt(0); pf.space_after = Pt(3); pf.line_spacing = 1.4
    set_run(p.add_run("· " + text), size=size)
    return p


def numbered(doc, idx, text, size=12):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.9); pf.first_line_indent = Cm(-0.9)
    pf.space_before = Pt(0); pf.space_after = Pt(3); pf.line_spacing = 1.4
    set_run(p.add_run(f"{idx}. {text}"), size=size)
    return p


def neutralize(s):
    """统一品牌口径"""
    if not s: return s
    for a, b in [("河南中豫港通供应链管理有限公司", "河南数字供应链管理有限公司"),
                 ("中豫港通供应链", "数字供应链"), ("河南港通供应链", "河南数字供应链"),
                 ("港通供应链", "数字供应链"), ("中豫港通", "数字供应链"),
                 ("豫港通", "数字供应链"), ("豫港", "数字供应链")]:
        s = s.replace(a, b)
    return s


# ---------------- 文档骨架 ----------------

def build_styles(doc):
    st = doc.styles['Normal']
    st.font.size = Pt(12); st.font.name = EN
    st.element.rPr.rFonts.set(qn('w:eastAsia'), CN)
    pf = st.paragraph_format
    pf.line_spacing = 1.5; pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.space_after = Pt(6); pf.first_line_indent = Pt(24)
    for i, sz in enumerate([16, 14, 12, 11], start=1):
        h = doc.styles[f'Heading {i}']
        h.font.size = Pt(sz); h.font.bold = True; h.font.name = CN_H
        h.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)
        h.element.rPr.rFonts.set(qn('w:eastAsia'), CN_H)
        h.paragraph_format.first_line_indent = Pt(0)


def setup_section(sec, header_text, footer=True):
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.54); sec.bottom_margin = Cm(2.54)
    sec.left_margin = Cm(2.6); sec.right_margin = Cm(2.6)
    sec.header_distance = Cm(1.5); sec.footer_distance = Cm(1.5)
    hp = sec.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.paragraph_format.first_line_indent = Pt(0)
    set_run(hp.add_run(header_text), size=9, color=(0x80, 0x80, 0x80))
    if footer:
        fp = sec.footer.paragraphs[0]
        fp.text = ""
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.paragraph_format.first_line_indent = Pt(0)
        set_run(fp.add_run("第 "), size=9, color=(0x80, 0x80, 0x80))
        add_field(fp, " PAGE ")
        set_run(fp.add_run(" 页 / 共 "), size=9, color=(0x80, 0x80, 0x80))
        add_field(fp, " NUMPAGES ")
        set_run(fp.add_run(" 页"), size=9, color=(0x80, 0x80, 0x80))


def cover(doc):
    for _ in range(4):
        para(doc, "", size=12)
    para(doc, "数字供应链平台", size=30, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=10, line=1.2, cn=CN_H)
    para(doc, "产品需求文档（PRD）汇编", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=30, line=1.2, cn=CN_H)
    para(doc, "准入 · 合同 · 履约 · 仓储 · 结算 · 资金 · 风控 · 数据",
         size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=60, color=(0x59, 0x59, 0x59))
    rows = [
        ["文档名称", "数字供应链平台 · 产品需求文档（PRD）汇编"],
        ["文档版本", "v1.0.0"],
        ["编制日期", "2026-10-26"],
        ["文档性质", "全模块需求说明（需求基线稿）"],
        ["覆盖范围", "8 个一级菜单 / 29 个业务模块 / 118 个原型页面"],
        ["阅读对象", "业务负责人、产品、研发、测试、UI 设计"],
        ["密级", "内部使用"],
    ]
    t = doc.add_table(rows=0, cols=2); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, v in rows:
        r = t.add_row()
        for i, txt in enumerate([k, v]):
            c = r.cells[i]; c.text = ""
            p = c.paragraphs[0]; p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(3)
            set_run(p.add_run(txt), size=11, bold=(i == 0), cn=(CN_H if i == 0 else CN))
            r.cells[0].width = Cm(3.6); r.cells[1].width = Cm(11.4)
        shade(r.cells[0], "F2F2F2")
    for _ in range(2):
        para(doc, "", size=12)
    para(doc, "本文件为需求基线。文中业务规则以业务方已确认口径为准；标记为「待业务方确认」的条目，"
               "需在需求评审会上逐条闭环后再进入开发排期。",
         size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x59, 0x59, 0x59), indent_chars=0)


def toc(doc):
    doc.add_page_break()
    heading(doc, "目　录", 1)
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Pt(0)
    add_field(p, ' TOC \\o "1-3" \\h \\z \\u ')


def main():
    # 读取模块数据
    mods = []
    for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        if os.path.basename(f) == "manifest.json": continue
        try:
            m = json.load(open(f, encoding="utf-8"))
            if m.get("slug"): mods.append(m)
        except Exception as e:
            print("跳过坏文件", f, e)
    order = ["project-apply","customer-apply","blacklist","workbench","account-personal","account-company",
             "contract","business-line","shipment","goods-transfer","payment","refund","receipt","margin",
             "settlement","invoice","market-price","bond-letter","approval","warehouse-inbound",
             "warehouse-outbound","warehouse-pickup","warehouse-inventory","warehouse-video",
             "warehouse-patrol","warehouse-system","warning","warning-config","data-center"]
    by = {m["slug"]: m for m in mods}
    ordered = [by[s] for s in order if s in by] + [m for m in mods if m["slug"] not in order]
    print("模块数:", len(ordered), "| 缺失:", [s for s in order if s not in by])

    doc = Document()
    build_styles(doc)
    sec0 = doc.sections[0]
    sec0.page_width = Cm(21.0); sec0.page_height = Cm(29.7)
    sec0.top_margin = Cm(2.54); sec0.bottom_margin = Cm(2.54)
    sec0.left_margin = Cm(2.6); sec0.right_margin = Cm(2.6)
    cover(doc)

    # 单一节 + 首页不同：封面（第 1 页）无页眉页脚，正文页起才有
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    setup_section(sec, f"{BRAND}平台 · 产品需求文档（PRD）汇编")

    toc(doc)

    # 第 1 章 文档说明
    heading(doc, "1　文档说明", 1)
    heading(doc, "1.1　文档目的", 2)
    para(doc, "本文件把数字供应链平台全部业务模块的需求，统一整理为一套可评审、可交付、可追溯的需求基线，"
              "用于业务确认、开发实现、测试验收与后续变更管理。每个模块采用同一套章节骨架，"
              "保证不同模块之间的描述口径、颗粒度与阅读方式一致。")
    heading(doc, "1.2　适用范围", 2)
    add_table(doc, ["项", "内容"], [
        ["产品形态", "B 端网页应用（PC 端优先，1440–1600px 基准）"],
        ["终端范围", "本期仅网页端，不含移动端与现场作业端"],
        ["覆盖范围", "8 个一级菜单、29 个业务模块、118 个原型页面"],
        ["不含范围", "平台化开放接口、第三方系统直连、移动端、线下作业系统"],
    ], widths=[3, 13])
    heading(doc, "1.3　阅读对象与读法", 2)
    add_table(doc, ["读者", "建议读法"], [
        ["业务负责人", "第 2 章产品概述 → 各模块「背景与目标」→ 第 5 章待确认问题"],
        ["产品经理", "全文，重点看各模块功能结构、流程与验收标准"],
        ["研发", "第 3 章全局规范 → 各模块数据关系、权限、流程、页面说明"],
        ["测试", "各模块验收标准与异常分支清单"],
        ["UI 设计", "各模块页面说明表与原型截图"],
    ], widths=[3, 13])
    heading(doc, "1.4　编写原则", 2)
    for i, t in enumerate([
        "只写需求，不写实现：数据关系只到字段口径与对象关系，不写表结构与接口报文",
        "每条规则必须可判断、可测试，不使用「适当」「尽快」等模糊表述",
        "业务方已确认的裁决口径优先于历史文档中的存疑口径，未裁决项一律进入第 5 章待确认清单",
        "资金流转按「线下操作 + 凭证上传 + 系统内确认」建模，系统内不存在线上扣款与打款",
        "权限以业务方当前裁决为准（本期未划分角色权限、系统全量权限），文档中出现的角色仅表示典型使用角色",
    ], 1):
        numbered(doc, i, t)
    heading(doc, "1.5　文档结构", 2)
    add_table(doc, ["章节", "内容"], [
        ["第 1 章", "文档说明：目的、范围、读法、编写原则"],
        ["第 2 章", "产品概述：定位、角色总表、模块地图、核心业务链路"],
        ["第 3 章", "全局规范：权限口径、通用交互与文案、通用异常与空状态、脱敏与合规、资金流转口径"],
        ["第 4 章", "各模块需求说明（29 个模块，每模块 8 节）"],
        ["第 5 章", "跨模块待确认问题清单"],
        ["附录 A", "页面索引（118 个页面 → 所属模块）"],
        ["附录 B", "术语与缩写"],
    ], widths=[3, 13])

    # 第 2 章 产品概述
    heading(doc, "2　产品概述", 1, page_break=True)
    heading(doc, "2.1　产品定位", 2)
    para(doc, "面向大宗商品供应链业务全角色（业务员、业务主管、风控、财务、总经办、仓储）的 B 端网页应用，"
              "把「准入—合同—履约—仓储—结算—资金—风控」全链路业务，从线下表格与即时通讯群的登记方式，"
              "搬进系统内流程化登记、单据可追溯、风险可核查。")
    heading(doc, "2.2　产品形态与阶段", 2)
    add_table(doc, ["项", "内容"], [
        ["当前选型", "网页 B 端应用（PC 端优先）"],
        ["选择理由", "功能复杂、多列表对比操作密集、使用者为企业内多部门角色，桌面端优于移动端，且免客户端发版"],
        ["终端范围", "本期仅网页端"],
        ["阶段策略", "一期：全链路主流程跑通；二期范围以业务方后续确认为准"],
    ], widths=[3, 13])
    heading(doc, "2.3　角色总表", 2)
    add_table(doc, ["角色", "所属部门", "核心诉求", "主要使用模块"], [
        ["业务员", "业务部", "快速发起立项、合同、收发货、货转、付款，把单据录进去不丢", "准入、合同、收发货、货转、仓储"],
        ["业务主管", "业务部", "审批下属单据，查看团队待办与业务线进度", "各业务模块审批节点"],
        ["风控人员", "风控部", "尽调审查、风险扫描结果复核、盯市监控、预警处置", "客户准入、预警中心、盯市、保证金、追保函"],
        ["财务人员", "财务部", "付款、退款、回款、保证金、结算、发票的凭证与金额核对", "结算单、资金、发票"],
        ["总经办", "总经办", "高风险事项终审（串行审批链的最终节点）", "各模块审批链终审节点"],
        ["仓储人员", "仓储部", "出入库、提放货、库存与巡库作业的现场登记", "仓储管理"],
        ["平台管理员", "运营管理部", "配置审批流程与预警规则，维护主数据与权限", "审批管理、预警规则配置、账户中心"],
    ], widths=[2.2, 1.8, 6.5, 5.5])
    heading(doc, "2.4　模块地图", 2)
    menu_rows = [
        ["准入管理", "项目准入、客户准入、黑名单管理"],
        ["数字供应链", "合同管理、业务线管理、收发货管理、货转管理、付款管理、退款管理、回款管理、保证金管理、结算单管理、发票管理、盯市管理、追保函管理、审批管理"],
        ["仓储管理", "入库管理、出库管理、提放货管理、库存管理、视频监控、巡库管理、系统管理"],
        ["数据中心", "驾驶舱、项目台账、业务线台账、资金占压、库存明细、应收应付、合规验证报告"],
        ["预警中心", "预警管理、预警规则配置"],
        ["账户中心", "个人管理、企业管理"],
        ["工作台", "工作台（待办与经营概览）"],
    ]
    add_table(doc, ["一级菜单", "二级模块"], menu_rows, widths=[3, 13])
    heading(doc, "2.5　核心业务链路", 2)
    para(doc, "平台的主链路以单据流转为主线：")
    for i, t in enumerate([
        "准入：立项（关联客户、风险扫描、黑灰名单校验）→ 客户准入审批 → 准入通过后方可发起合同",
        "合同：采购/销售/补充协议签订，合同与业务线关联，作为履约与资金计提的依据",
        "履约：收发货登记实际货物流转 → 货转管理完成货权转移 → 仓储出入库、提放货完成实物作业",
        "结算与资金：结算单生成 → 付款/退款/回款线下操作后上传凭证并在系统内确认 → 发票与保证金处理",
        "风控与监控：盯市价格监控 → 预警触发与处置 → 审批链路串起各节点待办与终审",
        "数据：驾驶舱与台账报表汇总项目、业务线、资金占压、库存、应收应付与合规验证结果",
    ], 1):
        numbered(doc, i, t)

    # 第 3 章 全局规范
    heading(doc, "3　全局规范与共性约定", 1, page_break=True)
    heading(doc, "3.1　权限口径（当前状态）", 2)
    para(doc, "业务方已明确：本期未划分角色权限，所有角色均为系统全量权限。本章及各模块中的角色，仅表示"
              "典型使用角色与业务分工，不构成权限分级。权限模型与数据权限划分待后续版本明确。")
    add_table(doc, ["事项", "当前口径", "后续"], [
        ["功能权限", "系统全量权限，所有登录用户可见全部已上线菜单与功能", "待业务方明确角色-功能矩阵"],
        ["数据权限", "不做数据行级隔离，按单据归属与业务筛选查看", "待明确组织维度的数据隔离规则"],
        ["敏感字段", "运行态可查看真实值，默认打码展示，手动点击查看并留痕", "保留留痕机制"],
        ["操作留痕", "关键操作（查看敏感信息、提交、撤回、审批）记录操作人与时间", "持续"],
    ], widths=[2.4, 8.6, 5])
    heading(doc, "3.2　通用交互约定", 2)
    add_table(doc, ["约定项", "规则"], [
        ["列表页", "左标题区 + 筛选区 + 表格区 + 分页；筛选实时生效，不设「查询 / 重置」按钮；已选条件以标签展示并支持单独删除与一键清除"],
        ["表单页", "字段分组、必填校验、金额与日期格式统一；提交前二次确认关键操作"],
        ["详情页", "概览区 + 标签页 + 关联单据；审批类单据统一提供审批时间线区块"],
        ["操作反馈", "成功/失败均给出明确反馈；空状态给出引导动作"],
        ["危险操作", "删除、撤回、终止、作废等操作必须二次确认，并提示影响范围"],
        ["导出", "全站详情页与报表页不支持打印；仅准入管理模块的整体报告支持导出 PDF"],
    ], widths=[2.6, 13.4])
    heading(doc, "3.3　通用异常与空状态", 2)
    add_table(doc, ["场景", "系统表现"], [
        ["无数据", "展示空状态文案与引导动作，不显示空白表格"],
        ["无权限", "菜单不展示该入口；直接访问时提示无权限并返回可访问页面"],
        ["加载失败", "展示失败提示与「重试」入口，不展示半截数据"],
        ["重复提交", "提交中禁用主按钮并保持处理中状态，不产生重复单据"],
        ["状态冲突", "提示当前单据状态已变更，请刷新后重试"],
        ["字段越界", "在字段下方给出具体原因与修正建议（格式、范围、依赖）"],
        ["凭证缺失", "单据进入待补充状态并提示所需材料，不阻断流程记录"],
    ], widths=[3, 13])
    heading(doc, "3.4　脱敏与合规", 2)
    add_table(doc, ["对象", "口径"], [
        ["交付物脱敏", "文档与演示数据中的手机号、证件号、信用代码、银行卡号一律按格式打码"],
        ["运行态脱敏", "真实手机号、信用代码等前端默认打码，用户手动点击查看完整值，查看行为被记录留痕"],
        ["贸易风险合规", "客户准入引入外部风险数据源做风险扫描，扫描结论与证据留档并可追溯"],
    ], widths=[3, 13])
    heading(doc, "3.5　资金流转口径（全平台统一）", 2)
    para(doc, "平台内所有资金类动作（放款、还款、追保还款、解押还款、受托支付等）一律按以下模型实现：")
    for i, t in enumerate([
        "实际资金操作在系统外完成（银行转账、票据或其他方式）",
        "发起方在系统内上传凭证：实际金额 + 凭证图片或 PDF",
        "收款方在系统内确认，系统据凭证更新单据状态与台账",
        "系统内的试算金额仅作参考，不等于实际发生金额，也不驱动线上资金动作",
    ], 1):
        numbered(doc, i, t)

    # 第 4 章 各模块
    heading(doc, "4　各模块需求说明", 1, page_break=True)
    para(doc, "以下 29 个模块采用统一骨架：4.x.1 一页结论 → 4.x.2 背景与目标 → 4.x.3 角色与用户需求 → "
              "4.x.4 功能结构与范围 → 4.x.5 数据关系 → 4.x.6 角色权限与数据权限 → 4.x.7 业务流程与页面 → "
              "4.x.8 验收标准与待确认项。")
    all_open = []
    page_index = []
    for i, m in enumerate(ordered, 1):
        heading(doc, f"4.{i}　{m.get('name','未命名')}", 2, page_break=True)
        path = m.get("menu_path", "")
        if path:
            para(doc, f"菜单路径：{path}", size=10.5, indent_chars=0, color=(0x59, 0x59, 0x59), space_after=8)
        # 4.x.1
        heading(doc, f"4.{i}.1　一页结论", 3)
        para(doc, neutralize(m.get("purpose", "")))
        pp = m.get("pain_points") or []
        if pp:
            add_table(doc, ["问题", "当前做法", "本模块解法"],
                      [[neutralize(x.get("problem","")), neutralize(x.get("current","")), neutralize(x.get("solution",""))] for x in pp],
                      widths=[3.4, 6.3, 6.3])
        # 4.x.2
        heading(doc, f"4.{i}.2　背景与目标", 3)
        gs = m.get("goals") or []
        if gs:
            add_table(doc, ["目标 / 衡量口径"], [[neutralize(g)] for g in gs], widths=[16])
        nis = m.get("not_in_scope") or m.get("out_of_scope") or []
        if nis:
            para(doc, "本期不做：", bold=True, space_after=3)
            for x in nis: bullet(doc, neutralize(x))
        para(doc, "说明：文中口径以业务方已确认结论为准；未确认项集中列于本章末与第 5 章。",
             size=10.5, indent_chars=0, color=(0x59, 0x59, 0x59), space_before=4)
        # 4.x.3
        heading(doc, f"4.{i}.3　角色与用户需求", 3)
        rs = m.get("roles") or []
        if rs:
            add_table(doc, ["角色", "所属部门", "用户需求（我要…以便…）"],
                      [[neutralize(x.get("role","")), neutralize(x.get("dept","") or "—"), neutralize(x.get("need",""))] for x in rs],
                      widths=[2.4, 2.2, 11.4])
        else:
            para(doc, "本模块的使用角色见全局角色总表（2.3）。")
        # 4.x.4
        heading(doc, f"4.{i}.4　功能结构与范围", 3)
        fs = m.get("functions") or []
        if fs:
            add_table(doc, ["功能", "功能说明", "关键规则"],
                      [[neutralize(x.get("name","")), neutralize(x.get("desc","")), neutralize(x.get("rule",""))] for x in fs],
                      widths=[2.6, 5.6, 7.8])
        pgs = m.get("pages") or []
        if pgs:
            add_table(doc, ["页面", "文件", "入口", "主要区块", "主要操作", "跳转"],
                      [[neutralize(x.get("name","")), x.get("file",""), neutralize(x.get("entry","")),
                        neutralize(x.get("blocks","")), neutralize(x.get("buttons","")), neutralize(x.get("jump",""))] for x in pgs],
                      widths=[2.2, 2.6, 2.0, 3.6, 3.0, 2.6], size=9.5)
        # 4.x.5
        heading(doc, f"4.{i}.5　数据关系", 3)
        es = m.get("entities") or []
        if es:
            add_table(doc, ["业务对象", "关键字段与口径", "与其他对象的关系"],
                      [[neutralize(x.get("name","")), "\n".join(neutralize(f) for f in (x.get("key_fields") or [])),
                        neutralize(x.get("relation",""))] for x in es],
                      widths=[2.6, 7.4, 6.0])
        else:
            para(doc, "本模块的数据对象与字段口径随单据结构确定，未单独列出。")
        # 4.x.6
        heading(doc, f"4.{i}.6　角色权限与数据权限", 3)
        para(doc, neutralize(m.get("permissions_note", "")) or
                   "本期为系统全量权限（业务方已确认未划分角色权限）；下表角色为典型使用角色，非权限分级。")
        para(doc, "数据可见性：按单据归属与业务筛选查看；手机号、统一社会信用代码等敏感字段默认打码，"
                  "手动点击查看完整值且查看行为留痕。", space_after=4)
        # 4.x.7
        heading(doc, f"4.{i}.7　业务流程与页面", 3)
        mm = m.get("mermaid") or ""
        if mm.strip():
            mp = os.path.join(SHOTS, f"mermaid-{m['slug']}.png")
            if os.path.exists(mp):
                add_figure(doc, mp, f"图 4-{i}-1　{m.get('name','')} 主业务流程")
            else:
                para(doc, "（流程图见原型页面）", indent_chars=0)
        fn = m.get("flow_nodes") or []
        if fn:
            para(doc, "主流程步骤：", bold=True, space_after=3)
            for k, s in enumerate(fn, 1): numbered(doc, k, neutralize(s))
        exs = m.get("exceptions") or []
        if exs:
            para(doc, "异常分支：", bold=True, space_before=6, space_after=3)
            add_table(doc, ["异常场景", "系统处理"],
                      [[neutralize(x.get("scene","")), neutralize(x.get("handling",""))] for x in exs],
                      widths=[5, 11])
        shot = os.path.join(SHOTS, f"{m['slug']}.png")
        multi = sorted(glob.glob(os.path.join(SHOTS, f"{m['slug']}-*.png")))
        lbl = m.get("name", "")
        if multi:
            for k, sp in enumerate(multi, 1):
                tag = os.path.basename(sp).rsplit("-", 1)[-1].replace(".png", "")
                add_figure(doc, sp, f"图 4-{i}-2.{k}　{lbl}（{tag}）")
        elif os.path.exists(shot):
            add_figure(doc, shot, f"图 4-{i}-2　{lbl} 原型页面")
        if pgs:
            para(doc, "页面级说明：", bold=True, space_before=4, space_after=3)
            add_table(doc, ["页面", "原型文件", "进入方式", "关键区块", "主要按钮与行为", "跳转去向"],
                      [[neutralize(x.get("name","")), x.get("file",""), neutralize(x.get("entry","")),
                        neutralize(x.get("blocks","")), neutralize(x.get("buttons","")), neutralize(x.get("jump",""))] for x in pgs],
                      widths=[2.0, 2.6, 1.9, 3.5, 3.0, 2.4], size=9.5)
        # 4.x.8
        heading(doc, f"4.{i}.8　验收标准与待确认项", 3)
        if fs:
            add_table(doc, ["功能", "验收要点（由关键规则转写）"],
                      [[neutralize(x.get("name","")), neutralize(x.get("rule",""))] for x in fs],
                      widths=[3, 13])
        oqs = m.get("open_questions") or []
        if oqs:
            para(doc, "待业务方确认：", bold=True, space_before=6, space_after=3)
            for x in oqs:
                bullet(doc, neutralize(x))
                all_open.append([m.get("name", ""), neutralize(x)])
        for x in pgs:
            page_index.append([m.get("name", ""), neutralize(x.get("name", "")), x.get("file", "")])

    # 第 5 章 待确认问题
    heading(doc, "5　跨模块待确认问题清单", 1, page_break=True)
    para(doc, "以下条目需在需求评审会上逐条闭环，闭环前不进入开发排期。")
    if all_open:
        add_table(doc, ["模块", "待确认问题"], [[a, b] for a, b in all_open], widths=[3, 13], size=10.5)
    else:
        para(doc, "各模块未列出待确认项。")

    # 附录 A
    heading(doc, "附录 A　页面索引", 1, page_break=True)
    para(doc, f"共 {len(page_index)} 个需求条目页面，文件均位于原型目录 pages/ 下。")
    add_table(doc, ["所属模块", "页面名称", "原型文件"], page_index, widths=[3, 6, 7], size=9.5)

    # 附录 B
    heading(doc, "附录 B　术语与缩写", 1)
    add_table(doc, ["术语", "说明"], [
        ["单据", "业务动作的书面凭证，如合同、发货单、结算单、付款单；是系统内流转的基本单位"],
        ["业务线", "业务归属维度，用于把合同、货转、仓储等单据归到同一条业务线并统计账面库存"],
        ["货转", "货权转移业务，记录货物所有权在不同主体间的流转"],
        ["提放货", "仓储侧的实物作业动作：提货与放货"],
        ["盯市", "对约定货物的市场价格持续监控并触发预警"],
        ["追保函", "为业务提供担保责任的函件凭证"],
        ["在途", "单据已发起但流程尚未结束的状态"],
        ["待办", "当前登录人需要处理的单据集合"],
        ["串行审批", "节点按顺序逐级流转，前一级通过后才进入下一级"],
        ["并行会签", "同一节点内多人同时收到待办，需全部通过才进入下一节点"],
        ["凭证", "线下资金动作发生后上传系统的证明材料（图片或 PDF）"],
        ["打码", "敏感字段在界面上以掩码展示，需手动点击查看完整值"],
    ], widths=[3, 13])

    doc.save(OUT_DOCX)
    print("已生成:", OUT_DOCX, os.path.getsize(OUT_DOCX), "bytes")
    print("模块数:", len(ordered), "| 待确认条目:", len(all_open), "| 页面条目:", len(page_index))


if __name__ == "__main__":
    main()
