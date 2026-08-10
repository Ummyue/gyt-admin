#!/usr/bin/env python3
"""report-project.html：客户 → 客户数量（tag 上下排列）"""

import re
from pathlib import Path

FILE = Path("/Users/fuyu/.mavis/agents/mavis/workspace/yugangtong-prototype/pages/report-project.html")

# (项目编号, 上游客户数, 下游客户数)
ROWS = [
    ("PRJ-2026-001", 1, 3),
    ("PRJ-2026-002", 2, 4),
    ("PRJ-2026-003", 1, 5),
    ("PRJ-2025-018", 1, 2),
    ("PRJ-2025-015", 3, 0),
    ("PRJ-2025-010", 1, 2),
    ("PRJ-2025-005", 1, 3),
    ("PRJ-2024-025", 1, 4),
]


def make_cell(up, down):
    return (
        '<div class="cust-cell">'
        f'<span class="tag tag-blue">上游 {up} 家</span>'
        f'<span class="tag tag-green">下游 {down} 家</span>'
        '</div>'
    )


def main():
    content = FILE.read_text(encoding="utf-8")
    print(f"原文件: {len(content)} 字符")

    # 1) 表头
    content = content.replace(
        '<th style="width: 11%;">客户</th>',
        '<th style="width: 12%;">客户数量</th>',
        1,
    )
    print("✅ 表头: 客户 → 客户数量")

    # 2) 描述
    content = content.replace(
        '（项目编号 / 客户 / 合同金额 / 累计回款 / 状态）',
        '（项目编号 / 客户数量 / 合同金额 / 累计回款 / 状态）',
        1,
    )
    print("✅ 描述: 客户 → 客户数量")

    # 3) 8 行数据 - 匹配每个项目行，用正则替换第 4 个 td
    for proj, up, down in ROWS:
        # 匹配：<tr ...><td col-num ...>项目编号</td><td>项目名</td><td><span class="tag tag-X">类型</span></td><td>客户</td>...
        pattern = re.compile(
            rf'(<tr class="cp-row-clickable"><td class="col-num" style="font-weight: 600;">{re.escape(proj)}</td>'
            r'<td>[^<]+</td>'                # 项目名称
            r'<td><span class="tag tag-\w+">[^<]+</span></td>)'  # 项目类型
            r'<td>[^<]+</td>'                 # ← 客户列
        )
        m = pattern.search(content)
        if not m:
            print(f"⚠️  跳过 {proj}: 正则没匹配到")
            continue
        # m.group(1) = 前 3 个 td 内容；m.group(0) = 完整 4 个 td
        new = m.group(1) + '<td>' + make_cell(up, down) + '</td>'
        content = content[:m.start()] + new + content[m.end():]
        print(f"✅ {proj}: 上游 {up} / 下游 {down}")

    FILE.write_text(content, encoding="utf-8")
    print(f"\n新文件: {len(content)} 字符")


if __name__ == "__main__":
    main()
