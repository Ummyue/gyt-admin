#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建可公网部署的单页版 QA 问答页。

背景：
    完整交付（21 份 HTML）含全部模块规格，不宜整体公开。
    本脚本从导出目录中抽出「99-待确认清单.html」，把左侧跨文档导航换成
    页内模块跳转，产出单文件、可独立部署的问答页。

⚠️ 注意（踩过的坑）：
    替换 `<nav>...</nav>` 时**必须保留 `</nav>` 闭合标签**，
    否则整个 `<main>` 会变成 `<nav>` 的子节点，被塞进左侧 290px 宽、
    overflow-y:auto 的滚动容器里 —— 页面看起来一片空白，但 DOM 里内容其实都在。

用法：
    python3 scripts/build_qa_standalone.py --out <部署目录>
"""
import argparse
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(ROOT, '..', 'docs-v2-export')
SRC_PAGE = '99-待确认清单.html'

NAV_HEAD = (
    '<nav><div class="brand">豫港通 · 待确认问答</div>'
    '<div class="ver">单页版 · {date}</div>'
    '<div class="grp">本文档</div>'
    '<a href="#qa-top">📌 怎么答这份清单</a>'
    '<a href="#进度总览">📊 进度总览</a>'
    '<a href="#已裁决无需再问业务负责人-2026-10-08">✅ 已裁决，无需再问</a>'
    '<div class="grp">按模块跳转</div>'
)
TOC_RE = re.compile(r'<h3 id="([^"]+)">第\s*(\S+?)\s*部分 · ([^<]+?)\s*共 (\d+) 条</h3>')


def build(export_dir, out_dir):
    src = os.path.join(export_dir, SRC_PAGE)
    if not os.path.exists(src):
        print('❌ 找不到 %s，请先跑 export_docs.py + inject_qa_form.py' % src)
        return 1
    from datetime import date
    h = open(src, encoding='utf-8').read()

    # 1) 换导航（保留 </nav>）
    nav = NAV_HEAD.format(date=date.today().isoformat())
    h, n = re.subn(r'<nav>.*?</nav>', nav, h, flags=re.S)
    if n != 1:
        print('❌ 导航替换异常（匹配 %d 处）' % n)
        return 1

    # 2) 塞模块跳转
    toc = ['<a href="#%s">%s · %s（%s 条）</a>'
           % (m.group(1), m.group(2), m.group(3).strip(), m.group(4))
           for m in TOC_RE.finditer(h)]
    h = h.replace('<div class="grp">按模块跳转</div>',
                  '<div class="grp">按模块跳转</div>' + ''.join(toc) + '</nav>', 1)
    h = h.replace('<main>', '<main id="qa-top">', 1)

    # 3) 结构自检 —— 防止再犯 </nav> 丢失的坑
    for tag in ('<div class="wrap">', '<nav>', '</nav>', '<main', '</main>'):
        c = h.count(tag)
        if c != 1:
            print('❌ 结构自检失败：%s 出现 %d 次（应为 1）' % (tag, c))
            return 1
    if h.find('</nav>') > h.find('<main'):
        print('❌ 结构自检失败：</nav> 在 <main> 之后')
        return 1

    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, 'index.html')
    open(dst, 'w', encoding='utf-8').write(h)
    print('✅ 单页版已生成：%s（模块跳转 %d 条，%.0f KB）'
          % (dst, len(toc), os.path.getsize(dst) / 1024))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--export', default=os.path.abspath(EXPORT))
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    return build(os.path.abspath(a.export), os.path.abspath(a.out))


if __name__ == '__main__':
    sys.exit(main())
