#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓原型截图（品牌中性化 · 强化版）
三条防线：
 1) 响应级改写：所有 HTML / JS / CSS / JSON 响应体做字符串替换（含外部 BI iframe）
 2) canvas 绘制拦截：fillText / strokeText 传参替换（画布上的字）
 3) 严格自检：innerText + textContent + 伪元素 content + 全部属性值 + canvas 绘制串
"""
import os, sys, subprocess, time, json, re, functools
print = functools.partial(__builtins__.print, flush=True) if False else print
from playwright.sync_api import sync_playwright

REPO = "/Users/fuyu/.minimax/agents/mavis/workspace/yugangtong-prototype"
OUT = "/Users/fuyu/.minimax/tmp/prd-modules/shots"
PORT = 8805
os.makedirs(OUT, exist_ok=True)

# 品牌 → 中性 映射（长串优先）
MAP = [
    ("河南中豫港通供应链管理有限公司仓库", "河南数字供应链管理有限公司仓库"),
    ("河南中豫港通供应链管理有限公司", "河南数字供应链管理有限公司"),
    ("河南中豫港通供应链", "河南数字供应链"),
    ("中豫港通供应链", "数字供应链"),
    ("河南港通供应链", "河南数字供应链"),
    ("中豫港通", "数字供应链"),
    ("港通供应链", "数字供应链"),
    ("河南中豫产业投资集团", "河南数字产业投资集团"),
    ("河南中豫国际港务集团", "河南数字国际港务集团"),
    ("河南中豫粮食物流园", "河南数字粮食物流园"),
    ("河南中豫粮油集团", "河南数字粮油集团"),
    ("中豫豫投资控股集团", "数字产业投资控股集团"),
    ("河南中豫薯业", "河南数字薯业"),
    ("中豫", "数字"),
    ("豫港通", "数字供应链"),
    ("港通", "数字供应链"),
]
LOGO_OLD, LOGO_NEW = ">豫<", ">数<"
BAD = ["豫港通", "中豫港通", "港通供应链", "中豫", "豫港", "港通"]

TARGETS = [
    ("project-apply",   "project-list.html",        "项目准入-列表"),
    ("customer-apply",  "customer-list.html",       "客户准入-列表"),
    ("blacklist",       "blacklist.html",           "黑名单管理-列表"),
    ("workbench",       "workbench.html",           "工作台-首页"),
    ("account-personal","account-personal.html",    "账户中心-个人管理"),
    ("account-company", "account-company.html",     "账户中心-企业管理"),
    ("contract",        "contract-purchase.html",   "合同管理-采购合同列表"),
    ("business-line",   "business-line.html",       "业务线管理-列表"),
    ("shipment",        "shipment-out.html",        "收发货管理-发货列表"),
    ("goods-transfer",  "goods-transfer.html",      "货转管理-列表"),
    ("payment",         "payment-list.html",        "付款管理-列表"),
    ("refund",          "refund-list.html",         "退款管理-列表"),
    ("receipt",         "receipt-list.html",        "回款管理-列表"),
    ("margin",          "margin-pool.html",         "保证金管理-明细"),
    ("settlement",      "settlement-purchase.html", "结算单管理-采购结算"),
    ("invoice",         "invoice.html",             "发票管理-进项发票"),
    ("market-price",    "market-price.html",        "盯市管理-价格列表"),
    ("bond-letter",     "bond-letter.html",         "追保函管理-列表"),
    ("warning",         "warning-list.html",        "预警中心-预警列表"),
    ("warning-config",  "warning-config.html",      "预警中心-规则配置"),
    ("data-center",     "cockpit.html",             "数据中心-驾驶舱"),
    ("warehouse-inbound",  "warehouse-inbound.html",  "仓储管理-入库记录"),
    ("warehouse-outbound", "warehouse-outbound.html", "仓储管理-出库记录"),
    ("warehouse-pickup",   "warehouse-pickup.html",   "仓储管理-提货管理"),
    ("warehouse-inventory","warehouse-inventory.html","仓储管理-库存台账"),
    ("warehouse-video",    "warehouse-video.html",    "仓储管理-库点监控"),
    ("warehouse-patrol",   "warehouse-patrol.html",   "仓储管理-巡库记录"),
    ("warehouse-system",   "warehouse-system.html",   "仓储管理-系统管理"),
]
APPROVAL = [
    ("approval-01", "approval-flow-list.html",   "审批管理-流程配置"),
    ("approval-02", "approval-flow-editor.html?flowId=standard", "审批管理-编排步骤1"),
    ("approval-03", "approval-flow-editor.html?flowId=standard", "审批管理-编排画布"),
    ("approval-04", "approval-flow-editor.html?flowId=standard", "审批管理-节点属性"),
    ("approval-05", "approval-monitor.html",     "审批管理-流程监控"),
]

def replace_brand(txt):
    for a, b in MAP:
        txt = txt.replace(a, b)
    txt = txt.replace(LOGO_OLD, LOGO_NEW)
    return txt

MAP_JS = json.dumps(dict(MAP), ensure_ascii=False)

INIT_SCRIPT = """
(() => {
  const MAP = %s;
  const rep = (t) => {
    if (typeof t !== 'string') return t;
    for (const [a, b] of Object.entries(MAP)) { if (t.indexOf(a) >= 0) t = t.split(a).join(b); }
    if (t.indexOf('>豫<') >= 0) t = t.split('>豫<').join('>数<');
    return t;
  };
  window.__brandDraw = [];
  const of = CanvasRenderingContext2D.prototype.fillText;
  CanvasRenderingContext2D.prototype.fillText = function (t, ...a) {
    window.__brandDraw.push(String(t));
    return of.call(this, rep(t), ...a);
  };
  const os = CanvasRenderingContext2D.prototype.strokeText;
  CanvasRenderingContext2D.prototype.strokeText = function (t, ...a) {
    window.__brandDraw.push(String(t));
    return os.call(this, rep(t), ...a);
  };
  const ots = CanvasRenderingContext2D.prototype.measureText;
  CanvasRenderingContext2D.prototype.measureText = function (t) { return ots.call(this, rep(t)); };
  if (window.MutationObserver) {
    const mo = new MutationObserver((muts) => {
      muts.forEach(m => {
        if (m.type === 'characterData') { const nv = rep(m.target.nodeValue); if (nv !== m.target.nodeValue) m.target.nodeValue = nv; }
        m.addedNodes.forEach(n => {
          if (n.nodeType === 3) { const nv = rep(n.nodeValue); if (nv !== n.nodeValue) n.nodeValue = nv; }
          else if (n.nodeType === 1) {
            const w = document.createTreeWalker(n, NodeFilter.SHOW_TEXT);
            const ns = []; while (w.nextNode()) ns.push(w.currentNode);
            ns.forEach(x => { const nv = rep(x.nodeValue); if (nv !== x.nodeValue) x.nodeValue = nv; });
          }
        });
      });
    });
    document.addEventListener('DOMContentLoaded', () => {
      mo.observe(document.body, { subtree: true, childList: true, characterData: true });
    });
  }
})();
""" % MAP_JS

STRICT_JS = """
() => {
  const parts = [];
  parts.push(document.body ? (document.body.innerText || '') : '');
  parts.push(document.body ? (document.body.textContent || '') : '');
  document.querySelectorAll('*').forEach(el => {
    ['::before','::after'].forEach(ps => {
      const c = getComputedStyle(el, ps).content;
      if (c && c !== 'none' && c !== 'normal') parts.push(c);
    });
    for (const a of el.attributes || []) parts.push(a.value);
  });
  parts.push((window.__brandDraw || []).join('\\n'));
  let frames = [];
  document.querySelectorAll('iframe').forEach(f => {
    try {
      const d = f.contentDocument;
      if (d && d.body) {
        frames.push(d.body.innerText || '');
        frames.push(d.body.textContent || '');
        d.querySelectorAll('*').forEach(el => {
          ['::before','::after'].forEach(ps => {
            const c = getComputedStyle(el, ps).content;
            if (c && c !== 'none' && c !== 'normal') frames.push(c);
          });
          for (const a of el.attributes || []) frames.push(a.value);
        });
      }
    } catch (e) { frames.push('[cross-origin]'); }
  });
  parts.push(frames.join('\\n'));
  return parts.join('\\n');
}
"""

srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=REPO,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
BASE = f"http://127.0.0.1:{PORT}/pages"
manifest = {}
leaks = []

REWRITE_CT = ("text/html", "javascript", "text/css", "application/json", "text/plain")

def route_handler(route):
    req = route.request
    url = req.url
    if not any(url.endswith(x) for x in (".html", ".js", ".css", ".json")):
        route.continue_(); return
    try:
        resp = route.fetch()
    except Exception:
        route.continue_(); return
    rct = (resp.headers.get("content-type") or "").lower()
    try:
        body = resp.body()
    except Exception:
        route.fulfill(status=200, content_type="text/plain; charset=utf-8", body=b"")
        return
    if any(k in rct for k in ("text/html", "javascript", "text/css", "application/json")):
        txt = body.decode("utf-8", "ignore")
        new_txt = replace_brand(txt)
        if new_txt != txt:
            data = new_txt.encode("utf-8")
            try:
                route.fulfill(status=resp.status,
                              headers={"content-type": rct or "text/html; charset=utf-8"},
                              body=data)
                return
            except Exception as e:
                print("   fulfill 失败:", str(e)[:80])
    route.fulfill(status=resp.status, headers={"content-type": rct or "application/octet-stream"}, body=body)


srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=REPO,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
BASE = f"http://127.0.0.1:{PORT}/pages"
manifest = {}
leaks = []

REWRITE_CT = ("text/html", "javascript", "text/css", "application/json", "text/plain")

def route_handler(route):
    req = route.request
    url = req.url
    ct = (req.headers.get("accept") or "") + " " + url
    looks_text = any(k in ct for k in (".html", ".js", ".css", ".json", "text/html"))
    if not looks_text:
        route.continue_(); return
    try:
        resp = route.fetch()
    except Exception:
        route.continue_(); return
    rct = (resp.headers.get("content-type") or "").lower()
    try:
        body = resp.body()
    except Exception:
        route.fulfill(response=resp); return
    if any(k in rct for k in REWRITE_CT):
        txt = body.decode("utf-8", "ignore")
        new = replace_brand(txt)
        if new != txt:
            try:
                route.fulfill(response=resp, body=new.encode("utf-8"), headers={**resp.headers, "content-length": str(len(new.encode("utf-8")))})
                return
            except Exception:
                pass
    route.fulfill(response=resp, body=body)

try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(viewport={"width": 1600, "height": 950}, device_scale_factor=1.5)
        ctx.add_init_script(INIT_SCRIPT)
        ctx.route("**/*", route_handler)
        page = ctx.new_page()

        def grab(slug, fname, label, extra=None):
            page.goto(f"{BASE}/{fname}", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(14000 if fname == "cockpit.html" else 1600)
            if extra:
                try:
                    extra(page); page.wait_for_timeout(900)
                except Exception as e:
                    print(f"    交互失败 {slug}: {str(e)[:60]}")
            # 严格自检
            txt = page.evaluate(STRICT_JS)
            hit = [k for k in BAD if k in txt]
            if hit:
                leaks.append((slug, hit))
                i = min(txt.index(k) for k in hit)
                print(f"  ❌ {slug:22s} 命中{hit} … {txt[max(0,i-50):i+60]!r}")
            path = os.path.join(OUT, f"{slug}.png")
            page.screenshot(path=path, timeout=120000, animations="disabled")
            manifest[slug] = {"file": fname, "label": label, "png": path}
            print(f"[OK] {slug:22s} {label}{'  ⚠️泄漏' if hit else ''}")

        for slug, fname, label in TARGETS:
            try: grab(slug, fname, label)
            except Exception as e: print(f"[FAIL] {slug}: {str(e)[:90]}")

        def to_step2(pg): pg.click("#step2Btn"); pg.wait_for_timeout(900)
        def open_node(pg):
            nodes = pg.query_selector_all(".cv-node")
            if len(nodes) > 1: nodes[1].click()
            pg.wait_for_timeout(800)
        for slug, fname, label in APPROVAL:
            extra = to_step2 if slug == "approval-03" else (open_node if slug == "approval-04" else None)
            try: grab(slug, fname, label, extra)
            except Exception as e: print(f"[FAIL] {slug}: {str(e)[:90]}")
        b.close()
finally:
    srv.terminate()

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("=" * 50)
print("截图:", len(manifest), "张 | 泄漏页面:", len(leaks))
for s, h in leaks: print("   ⚠️", s, h)
