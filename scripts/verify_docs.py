#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交付件结构校验。

检查项：
  1. 原 `docs/` 目录零改动（只读基线）
  2. 每份模块文档的 `## 0.`~`## 7.` 八章结构完整
  3. markdown 表格列数一致（无裸竖线破表）
  4. 粗体标记 `**` 成对
  5. §3.4 ↔ §7 编号双向对齐
  6. 脱敏五项扫描
  7. 导出产物完整性

用法：python3 scripts/verify_docs.py
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'docs-v2')
EXPORT = os.path.abspath(os.path.join(ROOT, '..', 'docs-v2-export'))

MODULES = [
    '00-产品概述与需求总纲.md', '01-通用交互与文案规范.md',
    '02.01-项目管理.md', '02.02-客户管理.md', '02.03-合同管理.md',
    '02.05-收发货管理.md', '02.06-业务线管理.md', '02.07-货转管理.md',
    '02.08-盯市价格管理.md', '02.09-追保函管理.md', '02.10-保证金管理.md',
    '02.11-预警中心.md', '02.12-仓储管理.md', '02.13-结算单管理.md',
    '02.14-资金管理.md', '02.15-发票管理.md', '02.16-数据中心.md',
    '03-贸易风险合规-天眼查集成.md',
]

fails, warns = [], []


def ok(msg):
    print('  ✅ %s' % msg)


def bad(msg):
    fails.append(msg)
    print('  ❌ %s' % msg)


def warn(msg):
    warns.append(msg)
    print('  ⚠️  %s' % msg)


def check_src_readonly():
    print('\n[1] 原 docs/ 只读基线')
    r = subprocess.run(['git', 'status', '--porcelain', 'docs/'],
                       cwd=ROOT, capture_output=True, text=True)
    n = len([x for x in r.stdout.strip().split('\n') if x.strip()])
    cnt = subprocess.run(['bash', '-c', 'ls docs/*.md 2>/dev/null | wc -l'],
                          cwd=ROOT, capture_output=True, text=True)
    if n == 0:
        ok('docs/ 改动 0 项（%s 份源文档）' % cnt.stdout.strip())
    else:
        bad('docs/ 有 %d 项改动：%s' % (n, r.stdout.strip()[:300]))


def check_chapters():
    print('\n[2] 模块文档八章结构')
    for fn in MODULES:
        p = os.path.join(SRC, fn)
        if not os.path.exists(p):
            bad('%s 缺失' % fn)
            continue
        txt = open(p, encoding='utf-8').read()
        if fn.startswith('00-'):
            need = ['## 9.']
            if '## 9. 待确认问题' not in txt:
                bad('%s 缺 §9 待确认问题' % fn)
            else:
                ok('%s §9 结构完整' % fn)
            continue
        if fn.startswith('01-') or fn.startswith('03-'):
            ok('%s 无固定八章要求（内容型文档）' % fn)
            continue
        heads = re.findall(r'\n## (\d)\.', txt)
        expect = [str(i) for i in range(0, 8)]
        missing = [h for h in expect if h not in heads]
        if missing:
            bad('%s 缺章节 §%s' % (fn, ','.join(missing)))
        else:
            ok('%s §0.~§7. 完整' % fn)


def _split_cells(row):
    """按未转义的竖线分列（与 export_docs.py / export_word.py 同口径）。"""
    return re.split(r'(?<!\\)\|', row.strip().strip('|'))


def check_tables():
    print('\n[3] markdown 表格列数一致')
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(SRC, fn)
        lines = open(p, encoding='utf-8').read().split('\n')
        i, bad_tables = 0, []
        while i < len(lines):
            if lines[i].strip().startswith('|') and i + 1 < len(lines) \
                    and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
                ncol = len(_split_cells(lines[i]))
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith('|'):
                    k = len(_split_cells(lines[j]))
                    if k != ncol:
                        bad_tables.append((j + 1, ncol, k))
                    j += 1
                i = j
            else:
                i += 1
        if bad_tables:
            bad('%s 表格列数不齐 %d 处，首处行 %d（表头 %d 列 / 该行 %d 列）'
                % (fn, len(bad_tables), bad_tables[0][0],
                   bad_tables[0][1], bad_tables[0][2]))
        else:
            ok('%s 表格列数一致' % fn)


def check_bold():
    print('\n[4] 粗体标记成对')
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(SRC, fn)
        bad_lines = []
        for i, ln in enumerate(open(p, encoding='utf-8'), 1):
            if ln.count('**') % 2:
                bad_lines.append(i)
        if bad_lines:
            bad('%s 有 %d 行 ** 不配对，首处行 %d' % (fn, len(bad_lines), bad_lines[0]))
        else:
            ok('%s ** 成对' % fn)


def check_numbering():
    print('\n[5] §3.4 ↔ §7 编号双向对齐')
    for fn in MODULES:
        if fn.startswith(('00-', '01-', '03-')):
            continue
        p = os.path.join(SRC, fn)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding='utf-8').read()
        m34 = re.search(r'\n### 3\.4', txt)
        m7 = re.search(r'\n## 7\.', txt)
        if not (m34 and m7):
            warn('%s 未找到 §3.4 或 §7' % fn)
            continue
        c = set('C' + n for n in re.findall(
            r'(?:\*\*|\|\s*\*\*)C(\d+)(?=[\s—*|])', txt[m34.start():m7.start()]))
        q = set('C' + n for n in re.findall(
            r'(?:\*\*|\|\s*\*\*)C(\d+)(?=[\s—*|])', txt[m7.start():]))
        if c == q:
            ok('%s C 编号双向一致（%d 条）' % (fn, len(c)))
        else:
            warn('%s C 编号不一致：§3.4 有 %s，§7 有 %s'
                 % (fn, sorted(c - q), sorted(q - c)))


def check_masking():
    print('\n[6] 脱敏五项扫描')
    pats = {
        '手机号': r'(13[0-9]|14[579]|15[0-35-9]|16[6]|17[0135678]|18[0-9]|19[89])[ -]?[0-9]{4}[ -]?[0-9]{4}',
        '银行卡': r'(?<![0-9A-Za-z])[0-9]{4}[ ]?[0-9]{4}[ ]?[0-9]{4}[ ]?[0-9]{4}(?![0-9A-Za-z])',
        '信用代码': r'91[0-9A-Z]{16,17}',
        '身份证': r'[1-9][0-9]{5}(19|20)[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx]',
    }
    for name, pat in pats.items():
        hits = 0
        for fn in os.listdir(SRC):
            if not fn.endswith('.md'):
                continue
            txt = open(os.path.join(SRC, fn), encoding='utf-8').read()
            for m in re.finditer(pat, txt):
                ctx = txt[max(0, m.start() - 40):m.end() + 20]
                if 'XXXX' in ctx or 'X' * 8 in ctx:
                    continue
                # 假阳性：整行是「接口 ID / 编号列表」（3 组以上 3~4 位数字）
                ls = txt.rfind('\n', 0, m.start()) + 1
                le = txt.find('\n', m.end())
                line = txt[ls:le if le > 0 else len(txt)]
                if re.search(r'(\d{3,4}[ ,、]+){3,}\d{3,4}', line):
                    continue
                hits += 1
        if hits:
            bad('%s 疑似真实值 %d 处' % (name, hits))
        else:
            ok('%s 无真实值' % name)
    em = 0
    for fn in os.listdir(SRC):
        if not fn.endswith('.md'):
            continue
        txt = open(os.path.join(SRC, fn), encoding='utf-8').read()
        for m in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', txt):
            if 'example' not in m.group(0):
                em += 1
    (ok if em == 0 else bad)('非保留域邮箱 %d 处' % em)


def check_decision_status():
    print('\n[7] 业务方裁决状态列 ↔ 全局台账一致性')
    ledger = os.path.join(SRC, 'BUSINESS-DECISIONS-2026-10-21.md')
    if not os.path.exists(ledger):
        bad('裁决台账缺失')
        return
    ltxt = open(ledger, encoding='utf-8').read()
    qa_in_ledger = set(re.findall(r'\|\s*(QA-\d+)\s*\|', ltxt))
    # 各模块状态列里出现的 QA 编号
    qa_in_docs = set()
    marked = 0
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.md') or fn.startswith('99-'):
            continue
        txt = open(os.path.join(SRC, fn), encoding='utf-8').read()
        # 只看「待确认问题」章（§7 / 总纲 §9），那里才有状态列
        m7 = re.search(r'\n## 7\. 本模块待确认问题|\n## 9\. 待确认问题', txt)
        if not m7:
            continue
        sec = txt[m7.start():]
        for m in re.finditer(r'QA-\d+', sec):
            qa_in_docs.add(m.group(0))
        marked += len(re.findall(r'QA-\d+', sec))
    missing = sorted(qa_in_ledger - qa_in_docs, key=lambda s: int(s[3:]))
    if missing:
        bad('台账 %d 条裁决未在正文状态列落地：%s'
            % (len(missing), ', '.join(missing)))
    else:
        ok('台账 %d 条裁决全部在正文状态列落地（状态标记 %d 处）'
           % (len(qa_in_ledger), marked))
    # 已裁决条目不应还残留「待裁决」
    # 只针对**本模块裁决记录表里点名要改的 C 条目**（其余 C 本轮本就未答）
    stale = []
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.md') or fn.startswith('99-'):
            continue
        txt = open(os.path.join(SRC, fn), encoding='utf-8').read()
        if '业务方裁决记录（2026-10-21' not in txt:
            continue
        # 从裁决记录表里取出「点名要改」的 C 编号
        decided_c = set()
        for m in re.finditer(r'^\|\s*\*?\*?D\d+\*?\*?\s*\|.*$', txt, re.M):
            for c in re.findall(r'\bC(\d+)\b', m.group(0)):
                decided_c.add('C' + c)
        m = re.search(r'\n### 7\.1', txt)
        if not m:
            continue
        sec = txt[m.start():]
        sec = sec[:sec.find('\n### 7.2')] if '\n### 7.2' in sec else sec
        for ln in sec.split('\n'):
            mm = re.match(r'^\|\s*\*?\*?(C\d+)\*?\*?\s*\|', ln)
            if mm and mm.group(1) in decided_c and '待裁决' in ln:
                stale.append('%s %s' % (fn, mm.group(1)))
    if stale:
        bad('已裁决条目仍残留「待裁决」：%s' % ', '.join(sorted(set(stale))))
    else:
        ok('已裁决条目无「已裁决却仍标待裁决」的残留行')


def check_export():
    print('\n[8] 导出产物')
    if not os.path.isdir(EXPORT):
        warn('导出目录不存在：%s' % EXPORT)
        return
    htmls = [f for f in os.listdir(EXPORT) if f.endswith('.html')]
    if len(htmls) >= 20:
        ok('HTML %d 份' % len(htmls))
    else:
        bad('HTML 只有 %d 份' % len(htmls))
    tbl_bad = 0
    for h in htmls:
        txt = open(os.path.join(EXPORT, h), encoding='utf-8').read()
        if txt.count('**'):
            warn('%s 有 %d 处裸 **' % (h, txt.count('**')))
        if txt.count('<table') != txt.count('</table>'):
            bad('%s table 标签不配对' % h)
        for m in re.finditer(r'<table>.*?</table>', txt, re.S):
            rows = re.findall(r'<tr>(.*?)</tr>', m.group(0), re.S)
            if not rows:
                continue
            n = len(re.findall(r'<t[hd]', rows[0]))
            for r in rows:
                if len(re.findall(r'<t[hd]', r)) != n:
                    tbl_bad += 1
    if tbl_bad:
        bad('HTML 表格列数不齐 %d 行' % tbl_bad)
    else:
        ok('HTML 表格列数全部一致')
    docx = [f for f in os.listdir(EXPORT) if f.endswith('.docx')]
    if docx:
        ok('Word：%s' % docx[0])
    else:
        warn('没有 docx')


def main():
    print('=' * 66)
    print('豫港通需求规格说明书 · 交付件校验')
    print('=' * 66)
    check_src_readonly()
    check_chapters()
    check_tables()
    check_bold()
    check_numbering()
    check_masking()
    check_decision_status()
    check_export()
    print('\n' + '=' * 66)
    if fails:
        print('❌ %d 项不通过：' % len(fails))
        for f in fails:
            print('   - %s' % f)
    else:
        print('✅ 全部检查项通过')
    if warns:
        print('⚠️  %d 项提醒：' % len(warns))
        for w in warns:
            print('   - %s' % w)
    print('=' * 66)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
