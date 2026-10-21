#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 QA 编号锁定表 `scripts/qa_numbering_pin.json`。

背景：
    线上填写页的 localStorage 以 **QA 编号** 为键，业主已填的 102 条答复绑定在
    **部署那一刻的编号**上。而 `build_qa.py` 原来的排序键含「是否已答复」——
    每回收一批新答复，编号就会全表洗牌，业主的答案、台账、模块正文引用的
    编号全部错位。

解决：
    把「部署那一刻」的编号固化成本文件（pin），`build_qa.py` 优先按 pin 分配
    编号；pin 里没有的条目才追加到末尾。编号从此**只增不改**。

输入：
    - 线上填写页源码（`yugangtong-qa-form/index.html`）——提供 QA 号 ↔ 问题原文
    - `build_qa.extract()`——提供 (模块, 条目号) ↔ 问题原文
输出：
    `scripts/qa_numbering_pin.json`  = { "<模块>|<条目号>": "QA-xxx", ... }
"""
import difflib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FORM = Path('/Users/fuyu/.minimax/sessions/mvs_641e5107c8b24c859321b703a3fec617'
            '/workspace/yugangtong-qa-form/index.html')
OUT = HERE / "qa_numbering_pin.json"

sys.path.insert(0, str(HERE))
import build_qa  # noqa: E402


def norm(s):
    s = re.sub(r'[`*_]', '', s or '')
    s = re.sub(r'\s+', '', s)
    s = s.replace('｜', '|')
    s = re.split(r'（\*\*裁决后|（裁决后', s)[0]
    return s[:70]


def form_cards():
    """从线上填写页源码取 (模块编号, QA号, 问题原文)。"""
    html = FORM.read_text(encoding="utf-8")
    sec_re = re.compile(r'<h3[^>]*>(第\s*\S+\s*部分\s*·[^<]*)</h3>')
    card_re = re.compile(
        r'data-qid="(QA-\d+)"\s+data-badge="([^"]*)"\s+data-question="([^"]*)"', re.S)
    out = []
    secs = list(sec_re.finditer(html))
    for i, m in enumerate(secs):
        codes = re.findall(r'（(\d{2}(?:\.\d{2})?)）', m.group(1))
        fn = codes[-1] if codes else m.group(1).strip()
        start = m.end()
        end = secs[i + 1].start() if i + 1 < len(secs) else len(html)
        for qa, badge, q in card_re.findall(html[start:end]):
            out.append((fn, qa, q))
    return out


# 题文在文档迭代中被改写、无法自动匹配的三条，人工核验填写页题文后固定
MANUAL = {
    '02.01-项目管理.md|C1': 'QA-028',   # 项目周期的字段中文名定哪个？
    '02.01-项目管理.md|Q13': 'QA-026',  # flow_type 枚举
    '02.02-客户管理.md|C5': 'QA-050',   # 客户黑名单要保留哪些能力、等级怎么分？
}


def main():
    if not FORM.exists():
        print("找不到线上填写页源码：%s" % FORM)
        return 1
    form = form_cards()
    print("线上填写页卡片：%d" % len(form))
    items = build_qa.extract()
    print("当前文档条目：%d" % len(items))

    form_by_mod = {}
    for fn, qa, q in form:
        form_by_mod.setdefault(fn, []).append((qa, q))

    # 条目 → 模块短码（02.01 之类）；MODULES 结构 = (key, 文件名, 显示名)
    mod_of = {}
    for entry in build_qa.MODULES:
        fn = entry[1]
        code = re.search(r'(\d{2}(?:\.\d{2})?)', fn)
        mod_of[fn] = code.group(1) if code else fn
    # 总纲在填写页里的分节没有编号，用「总纲」兜底
    form_by_mod.setdefault('总纲', form_by_mod.get('00-产品概述与需求总纲.md', []))

    pin, miss = {}, []
    for it in items:
        fn = it['file']
        code = mod_of.get(fn, fn)
        cands = form_by_mod.get(code, [])
        n = norm(it['q'])
        hit = None
        for i, (fqa, fq) in enumerate(cands):
            if fqa in pin.values():
                continue
            if norm(fq) == n:
                hit = i
                break
        if hit is None:
            best, bestr = None, 0.0
            for i, (fqa, fq) in enumerate(cands):
                if fqa in pin.values():
                    continue
                r = difflib.SequenceMatcher(None, n, norm(fq)).ratio()
                if r > bestr:
                    best, bestr = i, r
            if best is not None and bestr >= 0.45:
                hit = best
                print("  [模糊 %.2f] %s %s → %s" % (bestr, fn, it['id'], cands[hit][0]))
        if hit is None:
            miss.append((fn, it['id'], it['q'][:60]))
        else:
            pin[f"{fn}|{it['id']}"] = cands[hit][0]

    print("已锁定 %d 条" % len(pin))
    if miss:
        print("未锁定 %d 条：" % len(miss))
        for fn, cid, q in miss[:15]:
            print("   %s %s  %s" % (fn, cid, q))

    for k, v in MANUAL.items():
        if k not in pin:
            pin[k] = v
            print("  [人工指定] %s → %s" % (k, v))

    OUT.write_text(json.dumps(pin, ensure_ascii=False, indent=2, sort_keys=True),
                   encoding="utf-8")
    print("\n已写出 %s（%d 条）" % (OUT, len(pin)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
