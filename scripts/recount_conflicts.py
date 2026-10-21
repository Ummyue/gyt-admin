#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重算 docs-v2 各模块的源文档矛盾条数与裁决状态分布。

用途：业务方 2026-10-21 逐条裁决后，README §3 的矛盾统计必须按
「已裁决 / 待重述 / 不进 PRD / 未裁决」重新计数，且必须由实际文件内容统计得到，
不能人工估算、也不能沿用 v2.0 的旧数（v2.1 接入飞书手册后条目已增加）。

统计口径：
  - 矛盾条数 = 该模块 §3.4「版本冲突」中出现的 C 编号去重计数
    （两种载体都算：`**C1 — 标题` 独立块 / `| **C1** | ... |` 表格行）
  - 裁决状态 = 该模块 §7.1 待确认表对应行的最后一列（状态列）
"""
import re
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_V2 = ROOT / "docs-v2"

MODULES = [
    "02.01-项目管理.md", "02.02-客户管理.md", "02.03-合同管理.md",
    "02.05-收发货管理.md", "02.06-业务线管理.md", "02.07-货转管理.md",
    "02.08-盯市价格管理.md", "02.09-追保函管理.md", "02.10-保证金管理.md",
    "02.11-预警中心.md", "02.12-仓储管理.md", "02.13-结算单管理.md",
    "02.14-资金管理.md", "02.15-发票管理.md", "02.16-数据中心.md",
    "03-贸易风险合规-天眼查集成.md",
]

# 总纲的待确认章节是 §9.1 / §9.2，其余模块是 §7.1 / §7.2
SECTIONS = {"00-产品概述与需求总纲.md": ("9.1", "9.2")}

C_BLOCK = re.compile(r"^\*\*C(\d+)\s*[—–-]")
C_CELL = re.compile(r"^\|\s*\*?\*?C(\d+)\*?\*?\s*\|")
Q_CELL = re.compile(r"^\|\s*\*?\*?Q(\d+)\*?\*?\s*\|")


def is_separator(s):
    s = s.strip()
    if not s.startswith("|"):
        return False
    return bool(re.match(r"^\|[\s:\-\|]+\|$", s)) and "-" in s


def split_row(line):
    s = line.strip()
    if not s.startswith("|") or is_separator(s):
        return None
    return [c.strip() for c in s.split("|")[1:-1]]


def section_lines(lines, sec):
    pat = re.compile(rf"^###\s*{re.escape(sec)}\b")
    start = None
    for i, ln in enumerate(lines):
        if pat.match(ln):
            start = i
            break
    if start is None:
        return []
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^#{2,3}\s", lines[i]):
            end = i
            break
    return lines[start:end]


def table_rows(lines, sec):
    """返回该小节内所有表格数据行 [(行号, cells)]。"""
    sec_lines = section_lines(lines, sec)
    out = []
    i = 0
    while i < len(sec_lines):
        if split_row(sec_lines[i]) is not None and i + 1 < len(sec_lines) \
                and is_separator(sec_lines[i + 1]):
            j = i + 2
            while j < len(sec_lines) and split_row(sec_lines[j]) is not None:
                out.append((j, split_row(sec_lines[j])))
                j += 1
            i = j
        else:
            i += 1
    return out


def classify(status_text):
    t = status_text or ""
    if "⛔" in t or "不进 PRD" in t or "不进PRD" in t:
        return "不进PRD"
    if "🔁" in t or "待重述" in t:
        return "待重述"
    if "✅" in t or "已裁决" in t:
        return "已裁决"
    if "待裁决" in t or "待补充" in t or "待确认" in t or "待修订" in t:
        return "未裁决"
    return "未标注"


def analyze(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    # 1) 矛盾编号：§3.4（详情）与 §7.1（索引）取**并集**
    #    —— 被裁决为「不进 PRD / 已结案」的条目可能只在其中一处保留
    cids = set()
    for ln in section_lines(lines, "3.4"):
        m = C_BLOCK.match(ln)
        if m:
            cids.add(int(m.group(1)))
        m = C_CELL.match(ln)
        if m:
            cids.add(int(m.group(1)))
    # 2) §7.1 待确认表里的 C 行 + 状态
    secs = SECTIONS.get(path.name, ("7.1", "7.2"))
    state = {}
    for sec in secs:
        for _, cells in table_rows(lines, sec):
            if C_CELL.match("| " + cells[0] + " |"):
                cid = int(C_CELL.match("| " + cells[0] + " |").group(1))
                state[cid] = classify(cells[-1])
                cids.add(cid)
    counts = {"已裁决": 0, "待重述": 0, "未裁决": 0, "未标注": 0, "不进PRD": 0}
    for cid in cids:
        counts[state.get(cid, "未标注")] += 1
    # 3) 缺口 Q
    qids = set()
    qstate = {}
    for sec in secs:
        for _, cells in table_rows(lines, sec):
            if Q_CELL.match("| " + cells[0] + " |"):
                qid = int(Q_CELL.match("| " + cells[0] + " |").group(1))
                qids.add(qid)
                qstate[qid] = classify(cells[-1])
    qcounts = {"已裁决": 0, "待重述": 0, "未裁决": 0, "未标注": 0, "不进PRD": 0}
    for qid in qids:
        qcounts[qstate.get(qid, "未标注")] += 1
    return {
        "file": path.name,
        "conflicts": len(cids),
        "gaps": len(qids),
        **counts,
        "gaps_by_state": qcounts,
        "pending": [f"C{c}" for c in sorted(cids) if state.get(c, "未标注") in ("未裁决", "未标注")],
        "gap_pending": [f"Q{q}" for q in sorted(qids) if qstate.get(q, "未标注") in ("未裁决", "未标注")],
    }


def main():
    out = []
    total = {"conflicts": 0, "gaps": 0, "已裁决": 0, "待重述": 0, "未裁决": 0, "未标注": 0, "不进PRD": 0}
    print("=" * 104)
    print(f"{'模块':<30}{'矛盾':>5}{'已裁决':>7}{'待重述':>7}{'不进PRD':>8}{'未裁决':>7}{'未标注':>7}{'缺口':>6}")
    print("-" * 104)
    for name in MODULES:
        p = DOCS_V2 / name
        if not p.exists():
            print(f"[跳过] {name} 不存在")
            continue
        r = analyze(p)
        out.append(r)
        for k in total:
            total[k] += r.get(k, 0)
        print(f"{r['file']:<30}{r['conflicts']:>5}{r['已裁决']:>7}{r['待重述']:>7}"
              f"{r['不进PRD']:>8}{r['未裁决']:>7}{r['未标注']:>7}{r['gaps']:>6}")
    print("-" * 104)
    print(f"{'合计':<30}{total['conflicts']:>5}{total['已裁决']:>7}{total['待重述']:>7}"
          f"{total['不进PRD']:>8}{total['未裁决']:>7}{total['未标注']:>7}{total['gaps']:>6}")
    print("=" * 104)

    print("\n各模块仍待裁决条目：")
    for r in out:
        if r["pending"]:
            print(f"  {r['file']}: {', '.join(r['pending'])}")

    outfile = ROOT / ".work" / "conflict_recount.json"
    outfile.parent.mkdir(exist_ok=True)
    outfile.write_text(json.dumps({"modules": out, "total": total}, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(f"\n明细已写入 {outfile}")


if __name__ == "__main__":
    main()
