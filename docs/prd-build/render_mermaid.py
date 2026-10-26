#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把模块 JSON 里的 mermaid 代码本地渲染成 PNG（本地 Chrome，不外传内容）"""
import os, json, glob, sys
from playwright.sync_api import sync_playwright

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")
SHOTS = "/Users/fuyu/.minimax/tmp/prd-modules/shots"
os.makedirs(SHOTS, exist_ok=True)

CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
HTML = """<!doctype html><html><head><meta charset="utf-8">
<style>body{margin:0;background:#fff;font-family:"PingFang SC","Microsoft YaHei",sans-serif}
#box{padding:24px;display:inline-block;background:#fff}</style></head>
<body><div id="box"></div>
<script src="__CDN__"></script>
<script>
window.mermaid.initialize({startOnLoad:false, theme:'default', flowchart:{useMaxWidth:true}});
window.render = async (code) => {
  const box = document.getElementById('box');
  box.innerHTML = '';
  const {svg} = await mermaid.render('g'+Math.floor(Math.random()*1e6), code);
  box.innerHTML = svg;
  const s = box.querySelector('svg');
  if (s) { s.removeAttribute('style'); s.style.maxWidth='none'; }
  return true;
};
</script></body></html>"""

ok = fail = 0
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": 2000, "height": 1400}, device_scale_factor=2)
    page = ctx.new_page()
    page.set_content(HTML.replace("__CDN__", CDN))
    page.wait_for_function("typeof window.mermaid !== 'undefined'", timeout=30000)
    page.wait_for_timeout(500)

    for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        if os.path.basename(f) in ("manifest.json",):
            continue
        try:
            m = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        code = (m.get("mermaid") or "").strip()
        slug = m.get("slug")
        if not slug or not code:
            continue
        out = os.path.join(SHOTS, f"mermaid-{slug}.png")
        try:
            page.evaluate("async (c) => { await window.render(c); }", code)
            page.wait_for_timeout(600)
            el = page.query_selector("#box")
            el.screenshot(path=out)
            print(f"[OK] {slug:22s} {os.path.getsize(out)} bytes")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {slug:22s} {str(e)[:120]}")
            fail += 1
    b.close()
print(f"渲染完成：成功 {ok} / 失败 {fail}")
