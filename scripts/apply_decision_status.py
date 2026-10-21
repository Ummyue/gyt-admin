#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把业务方 2026-10-21 裁决同步到各模块文档「待确认问题」表的状态列。

数据源（两级，权威性递增）：
  1. `docs-v2/BUSINESS-DECISIONS-2026-10-21.md` —— 全项目裁决台账
     · 「分类」列 = A 已裁决 / B 需重述 / C 不进 PRD，是分类的唯一权威来源
     · 「条目」列 = 该条裁决对应模块内的 C<n> / Q<n> 编号
  2. 各模块文档自己的「📋 业务方裁决记录（2026-10-21 · 线上填写页回填）」表
     · 「影响范围」列给出该裁决改动到本模块的哪几节，可补上台账没列出的条目
     · 「编号」列提供 D 编号，写进状态列便于回溯

状态列文案：`<标记>（<D 编号> / <QA 编号>）`
  ✅ 已裁决 / 🔁 待重述 / ⛔ 不进 PRD
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_V2 = ROOT / "docs-v2"
LEDGER = DOCS_V2 / "BUSINESS-DECISIONS-2026-10-21.md"

# 台账章节 → 模块文档
LEDGER_SECTIONS = {
    "1、总纲与全局口径": "00-产品概述与需求总纲.md",
    "2、项目管理（立项）": "02.01-项目管理.md",
    "3、客户管理": "02.02-客户管理.md",
    "4、合同管理": "02.03-合同管理.md",
    "5、收发货管理": "02.05-收发货管理.md",
    "6、业务线管理": "02.06-业务线管理.md",
    "7、货转管理": "02.07-货转管理.md",
}

# 文档 → 待确认小节号
TARGET_SECTIONS = {
    "00-产品概述与需求总纲.md": ("9.1", "9.2"),
}
DEFAULT_SECTIONS = ("7.1", "7.2")

# 特殊状态覆盖：条目 id → 完整状态文案
OVERRIDES = {
    ("02.03-合同管理.md", "C4"):
        "**部分已裁决**：✅ 枚举值已定（D1 / 2026-10-08：单签 = 待盖章、双签 = 已双签）；"
        "⛔ 落库字段名 / 类型 / 是否落库**不进 PRD**（D24 / QA-072）",
    ("02.05-收发货管理.md", "C6"):
        "**已裁决**：✅ 「已作废」是统一状态机，收发货各操作流均有（D14 / QA-083）；"
        "✅ 作废**角色权限**当前为全量权限（D19 / QA-088）",
    ("02.05-收发货管理.md", "C12"):
        "**已裁决**：✅ 收货作废后进入失效状态「已作废」，**不可再激活**（D9 / QA-078）",
    # 02.02：黑名单等级——10-09 定了业务枚举，10-21 判定 DB 映射不进 PRD（同一 C5 两侧面）
    ("02.02-客户管理.md", "C5"):
        "**部分已裁决**：✅ 黑名单只保留登记逻辑、不做自动拦截，**等级枚举 = 一般 / 中度 / 高度**"
        "（2026-10-09 对话补充）；⛔ 等级与 DB `level` 字段的映射、假央企国企落库字段"
        "**不进 PRD**（D13 / QA-042）",
    # 02.10：总纲 D7 跨模块裁决（保证金是资金管理子模块）
    ("02.10-保证金管理.md", "C1"):
        "✅ 已裁决（D7 / QA-002：保证金是**资金管理的子模块**，不独立一级菜单）",
    # 02.11：总纲 D8 跨模块裁决（运行态脱敏口径）
    ("02.11-预警中心.md", "C12"):
        "✅ 已裁决（D8 / QA-003：运行态**默认打码 + 可手动查看完整信息 + 查看行为留痕**；"
        "**交付物一律脱敏**，源文档「真实值例外」口径作废）",
}

CLASS_MARK = {"A": "✅ 已裁决", "B": "🔁 待重述", "C": "⛔ 不进 PRD"}

# 2026-10-09 对话补充的 8 条（见 scripts/qa_answers_prior.py），与线上填写页来源分层
PRIOR_STATUS = {
    ("00-产品概述与需求总纲.md", "Q7"):
        "✅ 已裁决（2026-10-09 对话补充：合同状态机统一为 全部 / 待提交 / 审批中 / "
        "待上传双签合同 / 执行中 / 已完结 / 审批驳回 / 已作废，与 02.03 合同管理 D4 / QA-051 同口径）",
    ("02.01-项目管理.md", "C1"):
        "✅ 已裁决（2026-10-09 对话补充：字段中文名定为「业务周期」，语义为一个时间范围）",
    ("02.01-项目管理.md", "Q13"):
        "🔁 待重述（2026-10-09 对话补充：原问表述不清，已改写为「`flow_type` 一共有哪几种取值」）",
    ("02.02-客户管理.md", "C5"):
        "✅ 已裁决（2026-10-09 对话补充：客户黑名单只保留登记逻辑，不做自动拦截；"
        "等级枚举 = 一般 / 中度 / 高度）",
    ("02.05-收发货管理.md", "Q12"):
        "✅ 已裁决（2026-10-09 对话补充：收发货状态机统一为 全部 / 待收货 / 已收货 / 已作废，"
        "与 D15 / QA-084 同口径）",
    ("02.06-业务线管理.md", "C2"):
        "✅ 已裁决（2026-10-09 对话补充：业务线状态机统一为 全部 / 执行中 / 采购已完结 / "
        "销售已完结 / 全部已完结）",
    ("02.07-货转管理.md", "C8"):
        "✅ 已裁决（2026-10-09 对话补充：上下游货转状态机统一为 全部 / 审批中 / "
        "待上传已生效单据 / 已生效 / 驳回 / 已作废，与 QA-122 同口径）",
    ("02.08-盯市价格管理.md", "C4"):
        "✅ 已裁决（2026-10-09 对话补充：全平台品类统一为 淀粉制品 / 糖粉 / 谷物，"
        "与 QA-022 / QA-062 同口径）",
}


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


def load_ledger():
    """返回 (qa→分类, 模块→{条目 id → (QA编号, 分类)})"""
    qa_class = {}
    per_module = {}
    lines = LEDGER.read_text(encoding="utf-8").split("\n")
    cur_module = None
    in_table = False
    for ln in lines:
        m = re.match(r"^##\s*(\d+)、(.+?)\s*$", ln)
        if m:
            key = f"{m.group(1)}、{m.group(2)}"
            cur_module = None
            for sec_key, mod in LEDGER_SECTIONS.items():
                if key.startswith(sec_key):
                    cur_module = mod
                    break
            if cur_module:
                per_module.setdefault(cur_module, {})
            in_table = False
            continue
        if cur_module is None:
            continue
        if not in_table:
            cells = split_row(ln)
            if cells and cells[0] == "QA 编号":
                in_table = True
            continue
        if is_separator(ln):
            continue
        cells = split_row(ln)
        if cells is None:
            in_table = False
            continue
        if len(cells) < 4:
            continue
        qa = cells[0].replace("*", "").strip()
        item = cells[1].replace("*", "").strip()
        cls = cells[3].replace("*", "").strip().upper()[:1]
        if not re.match(r"^QA-\d+$", qa) or cls not in CLASS_MARK:
            continue
        qa_class[qa] = cls
        if re.match(r"^[CQ]\d+$", item):
            per_module[cur_module][item] = (qa, cls)
    return qa_class, per_module


def find_decision_table(lines):
    """定位模块内「业务方裁决记录（2026-10-21）」表，返回数据行列表 [(行号, cells)]。

    同一文档可能同时存在 2026-10-08 的旧裁决表，须取 2026-10-21 的那张。
    """
    headings = [i for i, ln in enumerate(lines)
                if "业务方裁决记录" in ln and ln.startswith("#")]
    if not headings:
        return []
    # 优先取标题里带 2026-10-21 的；否则取最后一个（一般是最新追加的）
    preferred = [i for i in headings if "2026-10-21" in lines[i]]
    candidates = preferred or headings
    for start in reversed(candidates):
        header = None
        for i in range(start, min(start + 120, len(lines))):
            cells = split_row(lines[i])
            if cells and any("QA" in c for c in cells) and any("影响范围" in c for c in cells):
                header = i
                break
        if header is None:
            continue
        rows = []
        for i in range(header + 2, len(lines)):
            cells = split_row(lines[i])
            if cells is None:
                break
            rows.append((i, cells))
        if rows:
            return rows
    return []


def module_id_map(lines):
    """从模块裁决记录表解析 {条目 id → (D编号, QA编号)}"""
    out = {}
    for _, cells in find_decision_table(lines):
        if len(cells) < 4:
            continue
        dno = cells[0].replace("*", "").strip()
        qa = cells[1].replace("*", "").strip()
        scope = cells[3]
        if not re.match(r"^D\d+$", dno):
            continue
        for item in re.findall(r"\b([CQ]\d+)\b", scope):
            out.setdefault(item, (dno, qa))
    return out


def target_ranges(lines, doc_name):
    secs = TARGET_SECTIONS.get(doc_name, DEFAULT_SECTIONS)
    out = []
    for sec in secs:
        pat = re.compile(rf"^###\s*{re.escape(sec)}\b")
        start = None
        for i, ln in enumerate(lines):
            if pat.match(ln):
                start = i
                break
        if start is None:
            continue
        hdr = None
        for i in range(start + 1, min(start + 20, len(lines))):
            if split_row(lines[i]) is None:
                continue
            if i + 1 < len(lines) and is_separator(lines[i + 1]):
                hdr = i
                break
        if hdr is None:
            continue
        end = hdr + 1
        for i in range(hdr + 2, len(lines)):
            if split_row(lines[i]) is None:
                break
            end = i
        out.append((sec, hdr, end))
    return out


def apply_status(doc_name, lines, id_to_qa_cls, id_to_dqa):
    changed = 0
    touched = set()
    for sec, hdr, end in target_ranges(lines, doc_name):
        header_cells = split_row(lines[hdr])
        id_col = None
        status_col = None
        for ci, c in enumerate(header_cells):
            key = c.strip(" *")
            if key in ("#", "编号", "序号", "问题编号"):
                id_col = ci
            if key in ("状态", "裁决状态", "处理状态"):
                status_col = ci
        if id_col is None:
            continue
        if status_col is None:
            new_header = header_cells + ["状态"]
            lines[hdr] = "| " + " | ".join(new_header) + " |"
            lines[hdr + 1] = "| " + " | ".join(["---"] * len(new_header)) + " |"
            for i in range(hdr + 2, end + 1):
                cells = split_row(lines[i])
                if cells is None:
                    continue
                lines[i] = "| " + " | ".join(cells + [""]) + " |"
            status_col = len(new_header) - 1
            end += 1
        for i in range(hdr + 2, end + 1):
            cells = split_row(lines[i])
            if cells is None or len(cells) <= id_col:
                continue
            item = cells[id_col].replace("*", "").strip()
            if not re.match(r"^[CQ]\d+$", item):
                continue
            touched.add(item)
            key = (doc_name, item)
            existing = cells[status_col] if len(cells) > status_col else ""
            has_mark = ("✅" in existing or "🔁" in existing or "⛔" in existing)
            if key in OVERRIDES:
                text = OVERRIDES[key]
            elif key in PRIOR_STATUS:
                text = PRIOR_STATUS[key]
            elif has_mark:
                # 已有人工写好的状态文案（往往带 ⚠️ 遗留说明），**不覆盖**
                continue
            else:
                info = id_to_qa_cls.get(item)
                if info is None and item in id_to_dqa:
                    dno, qa = id_to_dqa[item]
                    info = (qa, None)
                if info is None:
                    continue
                qa, cls = info
                if cls is None:
                    continue
                dno = id_to_dqa.get(item, (None, qa))[0]
                text = f"{CLASS_MARK[cls]}（{dno} / {qa}）" if dno else f"{CLASS_MARK[cls]}（{qa}）"
            while len(cells) <= status_col:
                cells.append("")
            if cells[status_col] != text:
                cells[status_col] = text
                lines[i] = "| " + " | ".join(cells) + " |"
                changed += 1
    return changed, touched


def main():
    qa_class, per_module = load_ledger()
    default_docs = sorted(set(list(LEDGER_SECTIONS.values()) +
                              [f for f, _ in PRIOR_STATUS]))
    only = sys.argv[1:] or default_docs
    for name in only:
        p = DOCS_V2 / name
        if not p.exists():
            print(f"[跳过] {name} 不存在")
            continue
        lines = p.read_text(encoding="utf-8").split("\n")
        id_to_dqa = module_id_map(lines)
        # 台账条目 → (QA, 分类)；台账没有的用模块记录的 QA 再从全局 QA→分类 查
        id_to_qa_cls = {}
        for item, (qa, cls) in per_module.get(name, {}).items():
            id_to_qa_cls[item] = (qa, cls)
        for item, (dno, qa) in id_to_dqa.items():
            if item not in id_to_qa_cls and qa in qa_class:
                id_to_qa_cls[item] = (qa, qa_class[qa])
        if not id_to_qa_cls and not any(f == name for f, _ in PRIOR_STATUS):
            print(f"[跳过] {name}：未找到裁决记录表或台账条目")
            continue
        changed, touched = apply_status(name, lines, id_to_qa_cls, id_to_dqa)
        p.write_text("\n".join(lines), encoding="utf-8")
        missing = sorted(set(id_to_qa_cls) - touched, key=lambda s: (s[0], int(s[1:])))
        print(f"[完成] {name}：映射 {len(id_to_qa_cls)} 条，更新 {changed} 个状态列"
              + (f"；未在待确认表找到: {', '.join(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
