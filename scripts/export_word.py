#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
待确认清单生成器 + Word 导出器

用法:
    python3 scripts/export_word.py --out ../docs-v2-export
"""
import argparse
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'docs-v2')

ORDER = [
    '00-产品概述与需求总纲.md', '01-通用交互与文案规范.md',
    '02.01-项目管理.md', '02.02-客户管理.md', '02.03-合同管理.md',
    '02.05-收发货管理.md', '02.06-业务线管理.md', '02.07-货转管理.md',
    '02.08-盯市价格管理.md', '02.09-追保函管理.md', '02.10-保证金管理.md',
    '02.11-预警中心.md', '02.12-仓储管理.md', '02.13-结算单管理.md',
    '02.14-资金管理.md', '02.15-发票管理.md', '02.16-数据中心.md',
    '03-贸易风险合规-天眼查集成.md',
]
PRIO = {
    '02.01': '🔴核心', '02.02': '🔴核心', '02.03': '🔴核心', '02.10': '🔴核心',
    '02.11': '🔴核心', '02.12': '🔴核心', '02.13': '🔴核心', '02.14': '🔴核心',
    '02.05': '🟡重要', '02.06': '🟡重要', '02.07': '🟡重要', '02.08': '🟡重要',
    '02.09': '🟡重要', '02.15': '🟡重要', '02.16': '🟡重要',
    '03': '🟡重要', '00': '顶层', '01': '顶层',
}


def collect():
    """从各文档 §7 抽取待确认条目。"""
    out = []
    for fn in ORDER:
        fp = os.path.join(SRC, fn)
        if not os.path.exists(fp):
            continue
        txt = open(fp, encoding='utf-8').read()
        # 只取 §7 之后的内容（待确认问题章节）
        m = re.search(r'\n## 7\.\s*', txt)
        sec = txt[m.start():] if m else ''
        rows = re.findall(r'^\|\s*\*\*(C\d+(?:-\S+)?)\*\*\s*\|(.+)$', sec, re.M)
        qs = re.findall(r'^\|\s*\*\*(Q\d+)\*\*\s*\|(.+)$', sec, re.M)
        key = fn[:-3].split('-')[0]
        for cid, rest in rows:
            cells = [c.strip() for c in rest.split('|')]
            title = cells[0] if cells else ''
            status = cells[-1] if cells else ''
            if re.search(r'已裁决|已解除|已确认', status):
                continue
            out.append((fn, key, cid, re.sub(r'\*\*|`', '', title), status))
        for qid, rest in qs:
            cells = [c.strip() for c in rest.split('|')]
            title = cells[0] if cells else ''
            if not title:
                continue
            out.append((fn, key, qid, re.sub(r'\*\*|`', '', title), '待确认'))
    return out


CAT = [
    ('枚举与状态值', r'枚举|状态值|状态名|中文名|取值'),
    ('字段与数据规范', r'字段|DDL|落库|类型|长度|必填|默认值|表结构|字段名'),
    ('权限与角色', r'权限|角色|谁能|矩阵'),
    ('交互与文案', r'文案|提示|Toast|空状态|交互|按钮|弹窗|校验'),
    ('计算公式与口径', r'公式|计算|口径|取值范围|统计|汇总|加总|口径'),
    ('外部系统与接口', r'接口|API|天眼查|外部|同步|ERP|银行'),
    ('流程与状态机', r'流程|状态机|流转|节点|审批|终态'),
]


def cat_of(t):
    for name, pat in CAT:
        if re.search(pat, t):
            return name
    return '其他业务口径'


def build_todo_md(items):
    by = {}
    for it in items:
        by.setdefault(cat_of(it[3]), []).append(it)
    total = len(items)
    L = []
    L.append('# 待确认问题清单')
    L.append('')
    L.append('> **文档类型**：PRD Writer 范式 · 交付附件')
    L.append('> **用途**：本清单汇总《豫港通需求规格说明书》正文各模块中**仍需业主 / 业务方确认**的业务口径问题。')
    L.append('> **说明**：正文已按「可确认的已确认、不可编造的不编造」原则编制；本清单是**正文无法自行解决、需要业务判断**的遗留项，不含研发可自行决定的技术实现细节。')
    L.append('> **生成日期**：%s' % date.today().isoformat())
    L.append('')
    L.append('## 统计')
    L.append('')
    L.append('| 分类 | 条数 |')
    L.append('|---|---|')
    for name, _ in CAT + [('其他业务口径', None)]:
        n = len(by.get(name, []))
        if n:
            L.append('| %s | %d |' % (name, n))
    L.append('| **合计** | **%d** |' % total)
    L.append('')
    L.append('> 📌 **已裁决无需再问的问题**（业务负责人 2026-10-08 确认，已写入正文）：')
    L.append('> 1. 立项/合同/货转审批 = **串行审批流**（非 OR 会签）')
    L.append('> 2. 合同签署状态 = **单签/双签**，界面文案为「待盖章/已双签」（已获线上录屏实证）')
    L.append('> 3. 保证金调整方式 = **3 种**（冲抵最后一笔货款 / 转移为另一笔业务的保证金 / 保证金退款）')
    L.append('> 4. 资金链路 = **系统仅作为登记方**，不涉及真实付款')
    L.append('> 5. 货转上下游 = 货权从供应商转给核心企业（上游）/ 核心企业转下游客户（下游）')
    L.append('')
    for name, _ in CAT + [('其他业务口径', None)]:
        rows = by.get(name, [])
        if not rows:
            continue
        L.append('## %s（%d 条）' % (name, len(rows)))
        L.append('')
        L.append('| # | 模块 | 优先级 | 编号 | 待确认问题 | 现有状态 |')
        L.append('|---|---|---|---|---|---|')
        for i, (fn, key, cid, title, status) in enumerate(rows, 1):
            st = re.sub(r'\*\*|`|<br>', ' ', status or '').strip()
            st = re.sub(r'\s+', ' ', st)[:60] or '待确认'
            disp = fn[:-3].replace('02.', '0').replace('-', ' ') if False else fn[:-3]
            L.append('| %d | [%s](%s) | %s | %s | %s | %s |'
                     % (i, disp, './' + fn, PRIO.get(key, '—'), cid,
                        title.replace('|', '／')[:150], st))
        L.append('')
    L.append('---')
    L.append('')
    L.append('## 建议处理顺序')
    L.append('')
    L.append('1. **枚举与状态值** —— 直接决定数据库枚举与前端状态 Tag，不定无法开发')
    L.append('2. **字段与数据规范** —— 决定 DDL 与接口契约')
    L.append('3. **流程与状态机** —— 决定业务流转与审批实现')
    L.append('4. **计算公式与口径** —— 决定报表数字正确性')
    L.append('5. 其余（交互文案 / 权限 / 外部接口）可与开发联调时并行确认')
    return '\n'.join(L) + '\n', total


# ---------------- Word 导出 ----------------
def md_to_docx(md, path, title=None):
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()
    # 中文字体
    st = doc.styles['Normal']
    st.font.name = 'Microsoft YaHei'
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    for s in ('Heading 1', 'Heading 2', 'Heading 3', 'Heading 4'):
        h = doc.styles[s]
        h.font.name = 'Microsoft YaHei'
        h._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
        h.font.color.rgb = RGBColor(0x1f, 0x29, 0x37)

    lines = md.split('\n')
    i, n = 0, len(lines)
    in_fence = False; buf = []; fence_lang = ''

    def shade(c, hexc):
        el = OxmlElement('w:shd'); el.set(qn('w:fill'), hexc)
        c._tc.get_or_add_tcPr().append(el)

    def add_table(rows):
        cols = max(len(r) for r in rows)
        t = doc.add_table(rows=len(rows), cols=cols)
        t.style = 'Table Grid'
        for ri, r in enumerate(rows):
            for ci in range(cols):
                cell = t.cell(ri, ci)
                cell.text = ''
                p = cell.paragraphs[0]
                txt = re.sub(r'[*`>#]', '', r[ci]) if ci < len(r) else ''
                run = p.add_run(txt.strip())
                run.font.size = Pt(8.5)
                run.font.name = 'Microsoft YaHei'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
                if ri == 0:
                    run.bold = True
                    shade(cell, 'eef2f7')
        doc.add_paragraph()

    while i < n:
        ln = lines[i]
        if ln.strip().startswith('```'):
            if not in_fence:
                in_fence, fence_lang, buf = True, ln.strip()[3:].strip(), []
            else:
                txt = '\n'.join(buf)
                if fence_lang == 'mermaid':
                    p = doc.add_paragraph()
                    r = p.add_run('[Mermaid 流程图：%d 行源码，离线版 HTML 中为可视化渲染]' % (len(buf) + 1))
                    r.font.size = Pt(8.5); r.italic = True
                    r.font.color.rgb = RGBColor(0x6b, 0x72, 0x80)
                else:
                    p = doc.add_paragraph()
                    r = p.add_run(txt)
                    r.font.size = Pt(8.5); r.font.name = 'Consolas'
                    r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
                in_fence, buf = False, []
            i += 1; continue
        if in_fence:
            buf.append(ln); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)', ln)
        if m:
            lv = min(len(m.group(1)), 4)
            doc.add_heading(re.sub(r'[*`]', '', m.group(2)), level=lv)
            i += 1; continue
        if re.match(r'^\s*(-{3,}|\*{3,})\s*$', ln):
            doc.add_paragraph('─' * 40); i += 1; continue
        if ln.strip().startswith('|') and i + 1 < n and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            add_table(rows); continue
        if ln.strip().startswith('>'):
            bq = []
            while i < n and lines[i].strip().startswith('>'):
                bq.append(lines[i].strip().lstrip('>').strip()); i += 1
            p = doc.add_paragraph()
            r = p.add_run(' '.join(x for x in bq if x))
            r.italic = True; r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0x1d, 0x4e, 0xd8)
            continue
        m = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)', ln)
        if m:
            p = doc.add_paragraph(style='List Bullet' if not re.match(r'\d+\.', m.group(2)) else 'List Number')
            p.add_run(re.sub(r'[*`]', '', m.group(3)))
            p.paragraph_format.space_after = Pt(2)
            i += 1; continue
        if not ln.strip():
            i += 1; continue
        p = doc.add_paragraph(re.sub(r'\*\*(.+?)\*\*', r'\1', re.sub(r'`([^`]+)`', r'\1', ln.strip())))
        p.paragraph_format.space_after = Pt(4)
        i += 1
    doc.save(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, '..', 'docs-v2-export'))
    ap.add_argument('--no-docx', action='store_true')
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    # 待确认清单统一由 build_qa.py 生成（QA 问答表格式），
    # 本脚本只负责读它来出 Word，不再重复生成，避免两种口径互相覆盖。
    import subprocess
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_qa
    md, total = build_qa.build(build_qa.extract())
    with open(os.path.join(SRC, '99-待确认清单.md'), 'w', encoding='utf-8') as f:
        f.write(md)
    print('✅ 待确认清单：%d 条（QA 问答表） → %s'
          % (total, os.path.join(SRC, '99-待确认清单.md')))

    if a.no_docx:
        return
    parts = ['# 豫港通数字供应链管理平台', '', '## 需求规格说明书（交付版）', '',
             '> 生成日期：%s' % date.today().isoformat(),
             '> 本文档由项目需求文档库（133 份源文档）按 PRD Writer 范式重组编制。', '',
             '> **阅读提示**：正文中标注「待确认」的条目需业主/业务方后续确认，'
             '完整清单见本文件末尾的《待确认问题清单》章节。', '', '---', '']
    for fn in ORDER + ['99-待确认清单.md']:
        fp = os.path.join(SRC, fn)
        if not os.path.exists(fp):
            print('  ⚠️ 跳过缺失：%s' % fn); continue
        parts.append(open(fp, encoding='utf-8').read())
        parts.append('\n\n---\n\n')
    full = '\n'.join(parts)
    dpath = os.path.join(out, '豫港通需求规格说明书.docx')
    try:
        md_to_docx(full, dpath)
        print('✅ Word 导出：%s（%.1f MB）'
              % (dpath, os.path.getsize(dpath) / 1048576))
    except ImportError:
        print('❌ 缺 python-docx，请先 pip3 install python-docx')
        return
    print('   正文 %d 份 + 待确认清单，合计 %d 条待确认问题' % (len(ORDER), total))


if __name__ == '__main__':
    main()
