#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 mermaid flowchart 源码解析成结构化泳道数据，供 Word 生成流程表。
输出 JSON：{swimlanes:[{role, nodes:[{id,label,kind}]}], edges:[{from,to,label,kind}]}"""
import re, json, sys, glob, os

NODE_RE = re.compile(r'([A-Za-z_][\w]*)\s*(\[\"[^\"]*\"\]|\(\"[^\"]*\"\)|\{[^\}]*\})')
EDGE_RE = re.compile(r'([A-Za-z_][\w]*)\s*(-->|-\.->|===>|-\.-)\s*(?:\|([^|]*)\|)?\s*([A-Za-z_][\w]*)')

def clean(lbl):
    lbl = lbl.strip()
    m = re.match(r'^[\[\("]\s*"?(.*?)"?\s*[\]\)]$', lbl, re.S)
    if m: lbl = m.group(1)
    return lbl.replace("<br/>", "；").replace("<br>", "；").strip()

def parse(code):
    lines = code.splitlines()
    swimlanes = []           # [{role, nodes:[{id,label}]}]
    edges = []
    cur = None
    stack = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        # subgraph
        sm = re.match(r'subgraph\s+([A-Za-z_][\w]*)\s*\[?"?([^"\]]*)"?\]?\s*$', line)
        if sm:
            cur = {"role": sm.group(2).strip() or sm.group(1), "nodes": []}
            swimlanes.append(cur)
            stack.append(cur)
            continue
        if line == "end":
            if stack: stack.pop()
            cur = stack[-1] if stack else None
            continue
        # 节点定义
        for m in NODE_RE.finditer(line):
            nid, lbl = m.group(1), clean(m.group(2))
            tgt = cur
            if tgt is None:
                tgt = {"role": "流程", "nodes": []}
                swimlanes.append(tgt)
            if not any(n["id"] == nid for n in tgt["nodes"]):
                tgt["nodes"].append({"id": nid, "label": lbl})
        # 边
        for m in EDGE_RE.finditer(line):
            _lbl = (m.group(3) or "").strip().strip('"').strip("'")
            edges.append({"from": m.group(1), "to": m.group(4),
                          "label": _lbl,
                          "kind": "实线" if m.group(2) == "-->" else ("虚线" if ".-" in m.group(2) else "粗线")})
    # 节点索引
    idx = {}
    for sl in swimlanes:
        for n in sl["nodes"]:
            idx.setdefault(n["id"], {"label": n["label"], "role": sl["role"]})
    # 补全只在边里出现、未在节点定义中的 id
    for e in edges:
        for k in ("from", "to"):
            if e[k] not in idx:
                idx[e[k]] = {"label": e[k], "role": "流程"}
    return {"swimlanes": swimlanes, "edges": edges, "index": idx}

if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    SRC = os.path.join(HERE, "modules")
    OUT = os.path.join(HERE, "flow_tables.json")
    result = {}
    for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        code = (d.get("mermaid") or "").strip()
        if not code or not code.startswith("flowchart"):
            continue
        result[d["slug"]] = parse(code)
    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("解析模块数:", len(result))
    for slug, r in list(result.items())[:3]:
        print(f"\n--- {slug}: 泳道 {len(r['swimlanes'])} 条 / 边 {len(r['edges'])} 条")
        for sl in r["swimlanes"]:
            print("   ", sl["role"], "→", " | ".join(n["label"][:18] for n in sl["nodes"][:6]))
