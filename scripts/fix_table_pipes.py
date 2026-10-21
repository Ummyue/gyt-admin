#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复表格行中「代码片段内的竖线」导致的表格劈列。

问题：Markdown 表格按 `|` 分列，**代码片段内部的 `|` 也会分列**（GFM 规定
代码片段内的竖线必须写成 `\|`）。docs-v2 的部分模块文档在 §3.4 / §5 等章节
引用了「以竖线分隔的字段定义」，这些代码片段在导出 HTML / Word 时会把一行
撑成 6 列、8 列，表格结构直接坏掉。

处理：把表格行内**代码片段中**的 `|` 转义为 `\|`（代码片段外的 `|` 是真正的
分列符，保持不动）。转义后单元格数量与表头一致，渲染与显示都正确。

只处理 docs-v2/ 下的交付文档；原 docs/ 目录全程只读，不触碰。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_V2 = ROOT / "docs-v2"


def is_separator(s):
    s = s.strip()
    if not s.startswith("|"):
        return False
    return bool(re.match(r"^\|[\s:\-\|]+\|$", s)) and "-" in s


def split_cells(row):
    """按未转义的竖线分列。"""
    return re.split(r"(?<!\\)\|", row.strip().strip("|"))


def escape_pipes_in_code(row):
    """把代码片段内部的 `|` 转义为 `\\|`，代码片段外的保持原样。"""
    out = []
    in_code = False
    for ch in row:
        if ch == "`":
            in_code = not in_code
            out.append(ch)
        elif ch == "|" and in_code:
            out.append("\\|")
        else:
            out.append(ch)
    return "".join(out)


def fix_file(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    changed = 0
    fixed_rows = 0
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            header_cells = len(split_cells(lines[i]))
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                if len(split_cells(lines[j])) != header_cells:
                    new = escape_pipes_in_code(lines[j])
                    if new != lines[j]:
                        lines[j] = new
                        changed += 1
                        fixed_rows += 1
                j += 1
            i = j
        else:
            i += 1
    if changed:
        path.write_text("\n".join(lines), encoding="utf-8")
    return changed, fixed_rows


def main():
    files = sorted(DOCS_V2.glob("*.md"))
    total_rows = 0
    for p in files:
        n, rows = fix_file(p)
        if n:
            total_rows += rows
            print(f"[修复] {p.name}：{rows} 行表格单元格数已对齐")
    print(f"\n共修复 {total_rows} 行")


if __name__ == "__main__":
    main()
