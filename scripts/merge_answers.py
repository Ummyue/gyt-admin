#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把业务方答复（2026-10-21 回收的 102 条）合并进 QA 生成器的数据源。

输入：
    ygt-answers-raw.md          线上填写页导出的答复原文
    ygt-answer-classification.json  Mavis 对每条答复的分类（A/B/C）与正文影响指引
输出：
    scripts/qa_answers.py       ANSWERS 数据源（build_qa.py 引用）
    docs-v2/BUSINESS-DECISIONS-2026-10-21.md  业务方裁决记录（交付件）

用法：
    python3 scripts/merge_answers.py --raw <raw.md> --cls <cls.json>
"""
import argparse
import collections
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

DUMP_RE = re.compile(r'\*\*(QA-\d+)\*\*\s*([^\n]*)\n\n((?:> [^\n]*\n?)+)')


def parse_raw(path):
    raw = io.open(path, encoding='utf-8').read()
    out = {}
    for m in DUMP_RE.finditer(raw):
        body = '\n'.join(l[2:] if l.startswith('> ') else l[1:]
                         for l in m.group(3).strip('\n').split('\n'))
        out[m.group(1)] = body.strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', required=True)
    ap.add_argument('--cls', required=True)
    a = ap.parse_args()

    import build_qa

    raw = parse_raw(a.raw)
    cls = json.load(io.open(a.cls, encoding='utf-8'))
    cats = dict(cls.get('_cats') or {})
    cats.update({k: v for k, v in cls.items() if not k.startswith('_')})

    # QA 编号 → (file, id)
    items = build_qa.extract()
    for it in items:
        pr, icon = build_qa.classify(it)
        it['prio'], it['icon'] = pr, icon
    by = collections.OrderedDict()
    for it in items:
        by.setdefault(it['key'], []).append(it)
    for k in by:
        by[k].sort(key=lambda x: (1 if build_qa.ans_of((x['file'], x['id'])) else 0,
                                  x['prio'], x['id']))
    seq, mapping = 0, {}
    for k, lst in by.items():
        for it in lst:
            seq += 1
            mapping['QA-%03d' % seq] = (it['file'], it['id'], it['q'], it['disp'])

    ANSWERS, RECORDS = {}, []
    for qid, (cat, body) in sorted(cats.items()):
        if qid not in raw:
            print('⚠️ %s 分类存在但答复原文缺失，跳过' % qid)
            continue
        if qid not in mapping:
            print('⚠️ %s 在当前清单中找不到对应条目，跳过' % qid)
            continue
        f, cid, q, disp = mapping[qid]
        ANSWERS[(f, cid)] = {
            'cat': cat,
            'ans': raw[qid],
            'body': body,
            'qa': qid,
        }
        RECORDS.append((qid, disp, cid, q, raw[qid], cat, body))

    # 生成 Python 数据源
    lines = ['# -*- coding: utf-8 -*-',
             '"""业务方答复数据源（2026-10-21 回收 · 102 条）。',
             '',
             '由 scripts/merge_answers.py 生成，请勿手工编辑。',
             '每条：cat = A 已裁决 / B 需重述 / C 不进 PRD',
             '"""',
             'ANSWERS = {']
    for (f, cid), v in sorted(ANSWERS.items()):
        lines.append('    (%r, %r): {' % (f, cid))
        lines.append('        %r: %r,' % ('cat', v['cat']))
        lines.append('        %r: %r,' % ('ans', v['ans']))
        lines.append('        %r: %r,' % ('body', v['body']))
        lines.append('        %r: %r,' % ('qa', v['qa']))
        lines.append('    },')
    lines.append('}')
    lines.append('')
    io.open(os.path.join(ROOT, 'scripts', 'qa_answers.py'), 'w',
            encoding='utf-8').write('\n'.join(lines))

    # 生成裁决记录（交付件）
    cc = collections.Counter(r[5] for r in RECORDS)
    L = ['# 业务方裁决记录（2026-10-21）', '',
         '> **来源**：业主在《待确认问题清单》线上填写页逐条回填，回收 102 条。',
         '> **记录日期**：2026-10-21',
         '> **口径**：本记录与业务方答复原文一一对应；正文已按 A 类裁决同步更新。', '',
         '## 统计', '',
         '| 分类 | 条数 | 含义 |', '|---|---|---|',
         '| A 已裁决 | %d | 答复明确，已写入正文 |' % cc['A'],
         '| B 需重述 | %d | 业主反馈问题表述不清，已改写问题待再答 |' % cc['B'],
         '| C 不进 PRD | %d | 属技术实现细节或已废弃，需求文档不体现 |' % cc['C'],
         '| **合计** | **%d** | |' % len(RECORDS), '']
    by_mod = collections.OrderedDict()
    for r in RECORDS:
        by_mod.setdefault(r[1], []).append(r)
    for mi, (disp, rs) in enumerate(by_mod.items(), 1):
        L += ['---', '', '## %d、%s（%d 条）' % (mi, disp, len(rs)), '',
              '| QA 编号 | 条目 | 业主答复原文 | 分类 | 正文处理 |',
              '|---|---|---|---|---|']
        for qid, _d, cid, q, ans, cat, body in rs:
            ans_s = ans.replace('\n', ' ').replace('|', '／')
            body_s = body.replace('\n', ' ').replace('|', '／')
            L.append('| %s | %s | %s | %s | %s |'
                     % (qid, cid, ans_s[:180], cat, body_s[:220]))
        L.append('')
    io.open(os.path.join(ROOT, 'docs-v2', 'BUSINESS-DECISIONS-2026-10-21.md'), 'w',
            encoding='utf-8').write('\n'.join(L))

    print('✅ 已生成 scripts/qa_answers.py（%d 条）' % len(ANSWERS))
    print('   A 已裁决 %d ｜ B 需重述 %d ｜ C 不进 PRD %d'
          % (cc['A'], cc['B'], cc['C']))
    print('✅ 已生成 docs-v2/BUSINESS-DECISIONS-2026-10-21.md')


if __name__ == '__main__':
    main()
