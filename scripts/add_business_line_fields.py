#!/usr/bin/env python3
"""
业务线台账表新增 6 个字段
- 1-4 加到 业务线号 前
- 5-6 加到 业务线名称 后，类型 前
"""

import re
from pathlib import Path

FILE = Path("/Users/fuyu/.mavis/agents/mavis/workspace/yugangtong-prototype/pages/business-line.html")

# 4 行 mock 数据
ROWS = [
    {
        "no": "YWX202309050001",
        "purchase_no": "JYX-DPC-20230905001",
        "sales_no": "XS-DPC-20230905001",
        "proj_no": "PRJ202309050001",
        "proj_name": "2023年度煤炭采购供应链项目（一期）",
        "purchase_fw": "CG-KJ-202309-001",
        "sales_fw": "XS-KJ-202309-001",
    },
    {
        "no": "YWX202309050002",
        "purchase_no": "JYX-DPC-20230905002",
        "sales_no": "XS-DPC-20230905002",
        "proj_no": "PRJ202309050002",
        "proj_name": "2023年度木薯淀粉账期业务",
        "purchase_fw": "CG-KJ-202309-002",
        "sales_fw": "XS-KJ-202309-002",
    },
    {
        "no": "YWX202309050003",
        "purchase_no": "JYX-DPC-20230905003",
        "sales_no": "XS-DPC-20230905003",
        "proj_no": "PRJ202309050003",
        "proj_name": "2023年度钢材预付业务",
        "purchase_fw": "CG-KJ-202309-003",
        "sales_fw": "XS-KJ-202309-003",
    },
    {
        "no": "YWX202309050004",
        "purchase_no": "JYX-DPC-20230905004",
        "sales_no": "XS-DPC-20230905004",
        "proj_no": "PRJ202309050004",
        "proj_name": "2023年度电解铜存货业务",
        "purchase_fw": "CG-KJ-202309-004",
        "sales_fw": "XS-KJ-202309-004",
    },
]


def make_new_fields(row: dict) -> str:
    """生成 6 个新字段的 HTML"""
    return (
        f'<div class="bl-info-line">采购订单/单批次合同编号：<a class="bl-link" href="./contract-purchase-order-detail.html">{row["purchase_no"]}</a></div>\n                    '
        f'<div class="bl-info-line">销售订单/单批次合同编号：<a class="bl-link" href="./contract-sales-order-detail.html">{row["sales_no"]}</a></div>\n                    '
        f'<div class="bl-info-line">项目编号：<span class="bl-co">{row["proj_no"]}</span></div>\n                    '
        f'<div class="bl-info-line">项目名称：<span class="bl-co">{row["proj_name"]}</span></div>\n                    '
        f'<div class="bl-info-line">采购框架合同编号：<a class="bl-link" href="./contract-purchase-framework-detail.html">{row["purchase_fw"]}</a></div>\n                    '
        f'<div class="bl-info-line">销售框架合同编号：<a class="bl-link" href="./contract-sales-framework-detail.html">{row["sales_fw"]}</a></div>\n                    '
    )


def main():
    content = FILE.read_text(encoding="utf-8")
    print(f"原文件长度: {len(content)} 字符")

    changes = 0
    for row in ROWS:
        no = row["no"]
        # 锚点：业务线号那行（每行唯一）
        # 缩进 20 空格 + <div class="bl-info-line">业务线号：<span class="bl-co">YWX20230905000X</span>
        old = f'<div class="bl-info-line">业务线号：<span class="bl-co">{no}</span>　业务类型'
        if old not in content:
            print(f"❌ 找不到锚点: {no}")
            continue

        new_fields = make_new_fields(row).rstrip()  # 去尾部空格
        new = new_fields + old

        content = content.replace(old, new, 1)
        changes += 1
        print(f"✅ 改 {no}: 插入 6 个新字段")

    FILE.write_text(content, encoding="utf-8")
    print(f"\n总改动: {changes} / {len(ROWS)} 行")
    print(f"新文件长度: {len(content)} 字符（增加 {len(content) - len(FILE.read_text(encoding='utf-8')) + len(content)} 字符）" if False else f"新文件长度: {len(content)} 字符")


if __name__ == "__main__":
    main()
