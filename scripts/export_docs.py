#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docs-v2 → 离线 HTML + Word 导出器

用法:
    python3 scripts/export_docs.py --out ../docs-v2-export

产出:
    <out>/index.html            索引页（含优先级 + 已知问题摘要）
    <out>/<doc>.html            每份文档一份独立 HTML
    <out>/99-待确认清单.html     收敛后的待确认问题清单
    <out>/assets/               本地 marked/mermaid/样式（离线可用）
    <out>/豫港通需求规格说明书.docx
"""
import argparse
import html
import json
import os
import re
import shutil
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'docs-v2')
VENDOR = '/tmp/ygt-vendor'

# 文档顺序 / 元信息（与 docs-v2/README.md §2 保持一致）
DOCS = [
    ('00-产品概述与需求总纲.md', '产品概述与需求总纲', '顶层架构', '🔴'),
    ('01-通用交互与文案规范.md', '通用交互与文案规范', '顶层架构', '🔴'),
    ('02.01-项目管理.md', '02.01 项目管理', '功能规格', '🔴'),
    ('02.02-客户管理.md', '02.02 客户管理', '功能规格', '🔴'),
    ('02.03-合同管理.md', '02.03 合同管理', '功能规格', '🔴'),
    ('02.05-收发货管理.md', '02.05 收发货管理', '功能规格', '🟡'),
    ('02.06-业务线管理.md', '02.06 业务线管理', '功能规格', '🟡'),
    ('02.07-货转管理.md', '02.07 货转管理', '功能规格', '🟡'),
    ('02.08-盯市价格管理.md', '02.08 盯市价格管理', '功能规格', '🟡'),
    ('02.09-追保函管理.md', '02.09 追保函管理', '功能规格', '🟡'),
    ('02.10-保证金管理.md', '02.10 保证金管理', '功能规格', '🔴'),
    ('02.11-预警中心.md', '02.11 预警中心', '功能规格', '🔴'),
    ('02.12-仓储管理.md', '02.12 仓储管理', '功能规格', '🔴'),
    ('02.13-结算单管理.md', '02.13 结算单管理', '功能规格', '🔴'),
    ('02.14-资金管理.md', '02.14 资金管理', '功能规格', '🔴'),
    ('02.15-发票管理.md', '02.15 发票管理', '功能规格', '🟡'),
    ('02.16-数据中心.md', '02.16 数据中心', '功能规格', '🟡'),
    ('03-贸易风险合规-天眼查集成.md', '03 贸易风险合规 · 天眼查集成', '外部集成', '🟡'),
    ('README.md', '交付说明与索引', '交付说明', '⚪'),
    ('99-待确认清单.md', '待确认问题清单', '交付说明', '⚪'),
]

CSS = """
:root{--bd:#e5e7eb;--tx:#1f2937;--tx2:#4b5563;--tx3:#6b7280;--bg:#f9fafb;
--pri:#2563eb;--core:#dc2626;--imp:#d97706;--fwd:#64748b}
*{box-sizing:border-box}
body{margin:0;font:15px/1.75 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
color:var(--tx);background:var(--bg)}
.wrap{display:flex;min-height:100vh}
nav{width:290px;flex:0 0 290px;background:#fff;border-right:1px solid var(--bd);
padding:20px 0;position:sticky;top:0;height:100vh;overflow-y:auto}
nav .brand{font-size:17px;font-weight:700;padding:0 20px 4px}
nav .ver{font-size:12px;color:var(--tx3);padding:0 20px 14px;border-bottom:1px solid var(--bd);margin-bottom:10px}
nav a{display:block;padding:7px 20px;color:var(--tx2);text-decoration:none;font-size:13.5px;border-left:3px solid transparent}
nav a:hover{background:var(--bg);color:var(--pri)}
nav a.on{color:var(--pri);border-left-color:var(--pri);background:#eff6ff;font-weight:600}
nav .grp{font-size:11px;color:var(--tx3);padding:14px 20px 5px;letter-spacing:.5px;font-weight:600}
main{flex:1;min-width:0;padding:34px 46px 90px;max-width:1200px}
h1{font-size:27px;margin:0 0 18px;padding-bottom:12px;border-bottom:2px solid var(--bd)}
h2{font-size:21px;margin:36px 0 14px;padding-top:6px;border-top:1px solid var(--bd)}
h3{font-size:17px;margin:26px 0 10px;color:#111827}
h4{font-size:15px;margin:20px 0 8px;color:var(--tx2)}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px;display:block;overflow-x:auto}
th,td{border:1px solid var(--bd);padding:8px 11px;text-align:left;vertical-align:top}
th{background:#f3f4f6;font-weight:600;white-space:nowrap}
tr:nth-child(even) td{background:#fcfcfd}
code{background:#f3f4f6;padding:1.5px 5px;border-radius:3px;font-size:12.5px;
font-family:"SF Mono",Menlo,Consolas,monospace;color:#b91c1c}
pre{background:#1e293b;color:#e2e8f0;padding:15px 17px;border-radius:7px;overflow-x:auto;font-size:12.5px;line-height:1.6}
pre code{background:none;color:inherit;padding:0}
blockquote{border-left:4px solid var(--pri);background:#eff6ff;margin:14px 0;padding:11px 17px;color:var(--tx2);border-radius:0 5px 5px 0}
blockquote p{margin:5px 0}
hr{border:0;border-top:1px solid var(--bd);margin:28px 0}
ul,ol{padding-left:26px}
li{margin:5px 0}
a{color:var(--pri)}
.mermaid{background:#fff;border:1px solid var(--bd);border-radius:7px;padding:18px;margin:16px 0;text-align:center;overflow-x:auto}
.mermaid svg{max-width:100%;height:auto}
.badge{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11.5px;margin-left:7px;vertical-align:middle}
.b-ok{background:#dcfce7;color:#15803d}
.b-imp{background:#dbeafe;color:#1d4ed8}
.b-fwd{background:#f1f5f9;color:#475569}
.hero{background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#fff;padding:38px 44px;border-radius:12px;margin-bottom:30px}
.hero h1{color:#fff;border:0;margin:0 0 6px;padding:0;font-size:31px}
.hero .sub{font-size:20px;font-weight:500;margin:0 0 14px;opacity:.97}
.hero p{margin:5px 0;opacity:.93;font-size:14.5px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:14px;margin:22px 0}
.card{background:#fff;border:1px solid var(--bd);border-radius:9px;padding:15px 18px}
.card .n{font-size:27px;font-weight:700;color:var(--pri)}
.card .l{font-size:12.5px;color:var(--tx3);margin-top:3px}
.foot{margin-top:56px;padding-top:18px;border-top:1px solid var(--bd);font-size:12.5px;color:var(--tx3)}
@media print{nav{display:none}main{padding:0;max-width:100%}.wrap{display:block}
.hero{background:#1e3a8a!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
@media(max-width:900px){nav{display:none}main{padding:20px}}
"""

NAV_JS = """
document.querySelectorAll('nav a[data-d]').forEach(a=>a.addEventListener('click',e=>{
  e.preventDefault();location.href=a.getAttribute('href');
}));
function hl(){
  var p=decodeURIComponent(location.search.slice(1));
  if(!p)return;
  var h=document.getElementById(p);
  if(h){h.scrollIntoView({behavior:'smooth',block:'start'});h.style.background='#fef9c3';
    setTimeout(()=>h.style.background='',2400);}
  document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.dataset.d===p));
}
document.addEventListener('DOMContentLoaded',()=>{hl();
  if(window.mermaid)mermaid.initialize({startOnLoad:true,theme:'default',
    flowchart:{useMaxWidth:true,htmlLabels:true},securityLevel:'loose'});});
"""


def esc(s):
    return html.escape(s, quote=False)


def md_to_html(md):
    """最小 Markdown → HTML（不依赖 marked，导出时静态化，保证离线零依赖）。"""
    out, i, n = [], 0, len(md)
    in_fence = False
    fence_lang, buf = False, []
    para, lst, lst_ol = [], None, False

    def flush_p():
        nonlocal para
        if para:
            out.append('<p>%s</p>' % inline(' '.join(para)))
            para = []

    def flush_l():
        nonlocal lst, lst_ol
        if lst:
            out.append('<%s>%s</%s>' % ('ol' if lst_ol else 'ul',
                       ''.join('<li>%s</li>' % x for x in lst), 'ol' if lst_ol else 'ul'))
            lst, lst_ol = None, False

    def flush_all():
        flush_p(); flush_l()

    # 已导出文档集合，用于把 .md 链接改写成同目录的 .html（离线版可点）
    EXPORTED = {d[0] for d in DOCS} | {'README.md', '99-待确认清单.md'}

    def fix_link(href):
        """把指向已导出文档的 .md 链接改写为 .html。
        ./xx.md 与 ../docs/xx.md 都指向本导出集合内的文件 → 统一改成 ./xx.html；
        p-*.md 等未导出的源文档链接保持原样。"""
        base = os.path.basename(href.split('#')[0])
        if not base.endswith('.md') or base not in EXPORTED:
            return href
        frag = '#' + href.split('#')[1] if '#' in href else ''
        return './' + base[:-3] + '.html' + frag

    def inline(t):
        t = esc(t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)
        t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
        t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                   lambda m: '<a href="%s">%s</a>' % (fix_link(m.group(2)), m.group(1)), t)
        t = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', t)
        return t

    lines = md.split('\n')
    while i < len(lines):
        ln = lines[i]
        # 代码块
        if ln.strip().startswith('```'):
            flush_all()
            if not in_fence:
                in_fence, fence_lang, buf = True, ln.strip()[3:].strip(), []
            else:
                cls = ' class="mermaid"' if fence_lang == 'mermaid' else ''
                if cls:
                    out.append('<div class="mermaid">%s</div>' % esc('\n'.join(buf)))
                else:
                    out.append('<pre><code>%s</code></pre>' % esc('\n'.join(buf)))
                in_fence, buf = False, []
            i += 1; continue
        if in_fence:
            buf.append(ln); i += 1; continue
        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)', ln)
        if m:
            flush_all()
            lv = min(len(m.group(1)) + 1, 6)
            tid = re.sub(r'[^\w\u4e00-\u9fff-]', '', m.group(2))[:40]
            out.append('<h%d id="%s">%s</h%d>' % (lv, tid, inline(m.group(2)), lv))
            i += 1; continue
        # 分割线
        if re.match(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$', ln):
            flush_all(); out.append('<hr/>'); i += 1; continue
        # 表格
        if ln.strip().startswith('|') and i + 1 < len(lines) and \
           re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            flush_all()
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i += 1
            cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows]
            hd, body = cells[0], cells[2:]
            o = ['<table><thead><tr>']
            o += ['<th>%s</th>' % inline(c) for c in hd]
            o.append('</tr></thead><tbody>')
            for r in body:
                o.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
            o.append('</tbody></table>')
            out.append(''.join(o)); continue
        # 引用
        if ln.strip().startswith('>'):
            flush_all()
            bq = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                bq.append(lines[i].strip().lstrip('>').strip()); i += 1
            out.append('<blockquote>%s</blockquote>' %
                       ''.join('<p>%s</p>' % inline(x) for x in bq if x))
            continue
        # 列表
        m = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)', ln)
        if m:
            flush_p()
            ol = bool(re.match(r'\d+\.', m.group(2)))
            if lst is None:
                lst, lst_ol = [], ol
            elif lst_ol != ol:
                flush_l(); lst, lst_ol = [], ol
            lst.append(inline(m.group(3))); i += 1; continue
        # 空行
        if not ln.strip():
            flush_all(); i += 1; continue
        # 表格分隔行误判兜底
        if re.match(r'^\s*\|[\s:|-]+\|\s*$', ln):
            i += 1; continue
        para.append(ln.strip()); i += 1
    flush_all()
    return '\n'.join(out)


def page(title, body, cur, depth=1):
    nav = ['<div class="brand">豫港通需求规格说明书</div>',
           '<div class="ver">交付版 v2.0 · %s</div>' % date.today().isoformat()]
    last_grp = None
    for fn, disp, grp, pri in DOCS:
        fp = os.path.join(SRC, fn)
        if not os.path.exists(fp):
            continue
        if grp != last_grp:
            nav.append('<div class="grp">%s</div>' % grp); last_grp = grp
        b = {'🔴': 'b-imp', '🟡': 'b-ok', '⚪': 'b-fwd'}.get(pri, '')
        on = ' class="on"' if fn == cur else ''
        nav.append('<a href="%s.html" data-d="%s"%s>%s <span class="badge %s">%s</span></a>'
                   % (fn[:-3], fn[:-3], on, esc(disp), b, pri))
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · 豫港通需求规格说明书</title>
<style>%s</style></head><body><div class="wrap">
<nav>%s</nav>
<main>%s
<div class="foot">豫港通数字供应链管理平台 · 需求规格说明书（交付版）<br>
源文档：项目需求文档库（只读）｜范式：PRD Writer 落地需求文档｜生成日期：%s</div>
</main></div>
<script>%s</script></body></html>""" % (esc(title), CSS, ''.join(nav), body, date.today().isoformat(), NAV_JS)


def index_html():
    cards, rows = [], []
    tot_todo = tot_c = 0
    for fn, disp, grp, pri in DOCS:
        fp = os.path.join(SRC, fn)
        if not os.path.exists(fp):
            continue
        txt = open(fp, encoding='utf-8').read()
        lines = txt.count('\n') + 1
        todo = txt.count('待补充')
        cs = len(set(re.findall(r'\*\*C(\d+)\s+—', txt)))
        if fn != 'README.md' and fn != '99-待确认清单.md':
            tot_todo += todo; tot_c += cs
        b = {'🔴': 'b-imp', '🟡': 'b-ok', '⚪': 'b-fwd'}.get(pri, '')
        rows.append('<tr><td><a href="%s.html">%s</a></td><td>%s</td>'
                    '<td><span class="badge %s">%s</span></td><td>%s</td>'
                    '<td>%d</td><td>%d</td></tr>'
                    % (fn[:-3], esc(disp), grp, b, pri, cs, lines, todo))
    hero = """
<div class="hero">
  <h1>豫港通数字供应链管理平台</h1>
  <p class="sub">需求规格说明书 · 交付版</p>
  <p>按 PRD Writer 范式重组 · 8 个一级菜单 / 16 个业务模块 / 外部系统集成规格</p>
  <p>生成日期：%s</p>
</div>

<div class="cards">
  <div class="card"><div class="n">%d</div><div class="l">文档份数</div></div>
  <div class="card"><div class="n">16</div><div class="l">业务模块</div></div>
  <div class="card"><div class="n">3</div><div class="l">已裁决冲突</div></div>
  <div class="card"><div class="n">%d</div><div class="l">待确认问题</div></div>
</div>
""" % (date.today().isoformat(), len(DOCS), tot_todo)

    md = """
## 本文档的定位

本文档是**项目交付物**，由项目原始需求文档（133 份，含 112 份页面级 PRD）按
PRD Writer 范式重组而成，全部内容可追溯至源文档与飞书用户手册。

三条编制原则：

1. **不编造** —— 信息不足处显式标注，不靠猜测填充
2. **不掩盖** —— 源文档自身矛盾如实并列，不静默选边
3. **有裁决** —— 业务方已确认的口径优先于历史版本

## 文档清单

| 文档 | 分类 | 优先级 | 已裁决冲突 | 行数 | 待确认项 |
|---|---|---|---|---|---|
%s

## 阅读指引

| 角色 | 建议读法 |
|---|---|
| 项目负责人 / 业主 | 本索引页 → 产品概述与需求总纲 |
| 产品经理 | 总纲 §4 功能清单 → 各模块 §1 功能描述 |
| 前端开发 | 总纲 §5 线框图 + §7 文案规范 → 通用交互与文案规范 |
| 后端开发 | 各模块 §5 数据规范（**先看该模块 §7 的字段类待确认项**） |
| 测试 | 各模块 §3 状态清单 + §4 边界条件 |

> ⚠️ **已知遗留**：本交付物中标注「待确认」的条目为源文档或手册未覆盖的业务口径，
> 需业主/业务方后续确认。完整清单见 [《待确认问题清单》](99-待确认清单.html)。
""" % ''.join(rows)

    return page('交付说明与索引', hero + md_to_html(md), 'README.md')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, '..', 'docs-v2-export'))
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(os.path.join(out, 'assets'), exist_ok=True)
    for f in ('marked.min.js', 'mermaid.min.js'):
        s = os.path.join(VENDOR, f)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(out, 'assets', f))
        else:
            print('  ⚠️ 缺少 vendor %s（离线渲染仍可用，仅 JS 增强失效）' % f)
    n = 0
    for fn, disp, grp, pri in DOCS:
        fp = os.path.join(SRC, fn)
        if not os.path.exists(fp):
            print('  ⚠️ 跳过缺失源文档：%s' % fn); continue
        md = open(fp, encoding='utf-8').read()
        body = '<h1>%s</h1>%s' % (esc(disp), md_to_html(md)) if fn != 'README.md' \
            else md_to_html(md)
        with open(os.path.join(out, fn[:-3] + '.html'), 'w', encoding='utf-8') as f:
            f.write(page(disp, body, fn))
        n += 1
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html())
    print('✅ HTML 导出完成：%d 份文档 → %s' % (n + 1, out))
    return out


if __name__ == '__main__':
    main()
