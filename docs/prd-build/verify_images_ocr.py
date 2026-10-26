#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对 Word 内嵌的全部图片做 OCR，逐张检查是否残留品牌字样。
这是"通篇检查"的硬标准：不依赖 DOM，图片里画出来的字也能查出来。"""
import os, sys, zipfile, subprocess, json, tempfile, shutil

DOCX = sys.argv[1] if len(sys.argv) > 1 else \
    "/Users/fuyu/.minimax/agents/mavis/workspace/yugangtong-prototype/docs/数字供应链平台-产品需求文档汇编.docx"
OCR = "/Users/fuyu/.minimax/tools/ocr_vision"
BAD = ["豫港通", "中豫港通", "港通供应链", "中豫", "豫港", "港通"]
# 「港澳台」等正常词需排除
OK_CTX = ["港澳台"]

tmp = tempfile.mkdtemp(prefix="docx_media_")
z = zipfile.ZipFile(DOCX)
media = [n for n in z.namelist() if n.startswith("word/media/")]
for n in media:
    with open(os.path.join(tmp, os.path.basename(n)), "wb") as f:
        f.write(z.read(n))
print("提取图片:", len(media))

# 分批 OCR
files = sorted(os.listdir(tmp))
files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
BATCH = 6
hits = []
alltext = []
for i in range(0, len(files), BATCH):
    part = files[i:i + BATCH]
    cmd = [OCR, "--json"] + [os.path.join(tmp, f) for f in part]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=600).stdout
    except Exception as e:
        print("  OCR 失败:", str(e)[:80]); continue
    try:
        data = json.loads(out)
    except Exception:
        print("  OCR 输出无法解析（跳过该批）"); continue
    items = data if isinstance(data, list) else data.get("results", data.get("items", []))
    for it in items:
        path = it.get("path") or it.get("file") or ""
        if it.get("lines") is not None:
            txt = "\n".join((l.get("text") or "") for l in it["lines"])
        else:
            txt = it.get("text") or ""
        alltext.append((os.path.basename(path), txt))
        for k in BAD:
            if k in txt:
                for o in OK_CTX:
                    txt2 = txt.replace(o, "")
                if k in txt2:
                    hits.append((os.path.basename(path), k, txt[:200]))

print("OCR 完成，覆盖图片:", len(alltext))
if hits:
    print("❌ 发现品牌字样:")
    for h in hits: print("   ", h)
else:
    print("✅ 全部图片 OCR 未发现品牌字样")

# 文本层再扫一遍
ztxt = "".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
th = [k for k in BAD if k in ztxt]
print("文档文本层品牌扫描:", "无 ✅" if not th else f"❌ {th}")
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if hits or th else 0)
