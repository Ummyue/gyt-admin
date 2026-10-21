#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把表格行里「贴字竖线」转义为 `\\|`。

背景：Markdown 表格按 `|` 分列，GFM 规定单元格内的竖线必须写成 `\\|`。
docs-v2 里有一批「`……）| 下一列`」形态的行——竖线前紧贴中文右括号、后跟空格，
看起来像分列符，实际是上一格内容的收尾，属于典型的误伤点。

判定规则（仅作用于表格数据行）：
  竖线前一个字符是「非空白且非竖线」，且竖线后紧跟空白或行尾 → 判定为格内竖线，转义。
  真正的分列符在 docs-v2 中一律是 ` | `（前后都有空格），不会被误伤。

只处理 docs-v2/；原 docs/ 目录只读。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_V2 = ROOT / "docs-v2"

# 不在代码片段内时，判定为格内竖线
CELL_PIPE = re.compile(r"(?<![\s|\\])\|(?=\s|$)")


def is_separator(s):
    s = s.strip()
    if not s.startswith("|"):
        return False
    return bool(re.match(r"^\|[\s:\-\|]+\|$", s)) and "-" in s


def split_cells(row):
    return re.split(r"(?<!\\)\|", row.strip().strip("|"))


def escape_row(row):
    """按 backtick 状态分段，代码片段内的竖线不动，片段外贴字竖线转义。"""
    out = []
    in_code = False
    i = 0
    while i < len(row):
        ch = row[i]
        if ch == "`":
            in_code = not in_code
            out.append(ch)
            i += 1
            continue
        if ch == "|" and not in_code and i > 0:
            prev = row[i - 1]
            nxt = row[i + 1] if i + 1 < len(row) else " "
            if prev not in (" ", "\t", "|") and (nxt in (" ", "\t", "")):
                out.append("\\|")
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def fix_file(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    changed = 0
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            ncol = len(split_cells(lines[i]))
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                if len(split_cells(lines[j])) != ncol:
                    new = escape_row(lines[j])
                    if new != lines[j] and len(split_cells(new)) == ncol:
                        lines[j] = new
                        changed += 1
                j += 1
            i = j
        else:
            i += 1
    if changed:
        path.write_text("\n".join(lines), encoding="utf-8")
    return changed


def main():
    only = sys.argv[1:]
    files = [DOCS_V2 / f for f in only] if only else sorted(DOCS_V2.glob("*.md"))
    total = 0
    for p in files:
        if not p.exists():
            continue
        n = fix_file(p)
        if n:
            total += n
            print(f"[修复] {p.name}：{n} 行")
    print(f"\n共修复 {total} 行")


if __name__ == "__main__":
    main()
