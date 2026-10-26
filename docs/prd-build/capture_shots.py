import os, sys, subprocess, time, json
from playwright.sync_api import sync_playwright

REPO = "/Users/fuyu/.minimax/agents/mavis/workspace/yugangtong-prototype"
OUT = "/Users/fuyu/.minimax/tmp/prd-modules/shots"
PORT = 8801
os.makedirs(OUT, exist_ok=True)

# slug -> (页面文件, 中文名)
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

# 审批管理：多张关键状态
APPROVAL = [
    ("approval-01", "approval-flow-list.html",   "审批管理-流程配置"),
    ("approval-02", "approval-flow-editor.html?flowId=standard", "审批管理-编排步骤1"),
    ("approval-03", "approval-flow-editor.html?flowId=standard", "审批管理-编排画布"),
    ("approval-04", "approval-flow-editor.html?flowId=standard", "审批管理-节点属性"),
    ("approval-05", "approval-monitor.html",     "审批管理-流程监控"),
]

NEUTRALIZE_JS = r"""
(() => {
  const MAP = [
    ['河南中豫港通供应链管理有限公司', '河南数字供应链管理有限公司'],
    ['中豫港通供应链', '数字供应链'],
    ['河南港通供应链', '河南数字供应链'],
    ['港通供应链', '数字供应链'],
    ['中豫港通', '数字供应链'],
    ['豫港通', '数字供应链'],
  ];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walk.nextNode()) nodes.push(walk.currentNode);
  nodes.forEach(n => {
    let v = n.nodeValue;
    if (!v) return;
    MAP.forEach(([a, b]) => { v = v.split(a).join(b); });
    n.nodeValue = v;
  });
  // 品牌 logo 单字
  document.querySelectorAll('span,div,a').forEach(el => {
    if (el.children.length === 0 && el.textContent.trim() === '豫') el.textContent = '数';
  });
  document.title = document.title.replace(/豫港通|中豫港通|港通/g, '数字供应链');
  return true;
})()
"""

srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=REPO,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
BASE = f"http://127.0.0.1:{PORT}/pages"
manifest = {}

def grab(page, slug, fname, label, extra=None):
    page.goto(f"{BASE}/{fname}", wait_until="networkidle")
    page.wait_for_timeout(1100)
    page.evaluate(NEUTRALIZE_JS)
    page.wait_for_timeout(250)
    if extra:
        try:
            extra(page)
            page.wait_for_timeout(800)
            page.evaluate(NEUTRALIZE_JS)
            page.wait_for_timeout(150)
        except Exception as e:
            print(f"    交互失败 {slug}: {str(e)[:70]}")
    path = os.path.join(OUT, f"{slug}.png")
    page.screenshot(path=path)
    manifest[slug] = {"file": fname, "label": label, "png": path}
    print(f"[OK] {slug:22s} {label}")

try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(viewport={"width": 1600, "height": 950}, device_scale_factor=1.5)
        page = ctx.new_page()

        for slug, fname, label in TARGETS:
            try:
                grab(page, slug, fname, label)
            except Exception as e:
                print(f"[FAIL] {slug}: {str(e)[:90]}")

        # 审批管理多状态
        def to_step2(pg):
            pg.click("#step2Btn"); pg.wait_for_timeout(900)
        def open_node(pg):
            nodes = pg.query_selector_all(".cv-node")
            if len(nodes) > 1: nodes[1].click()
            pg.wait_for_timeout(800)
        for slug, fname, label in APPROVAL:
            extra = None
            if slug == "approval-03": extra = to_step2
            if slug == "approval-04": extra = open_node
            try:
                grab(page, slug, fname, label, extra)
            except Exception as e:
                print(f"[FAIL] {slug}: {str(e)[:90]}")

        b.close()
finally:
    srv.terminate()

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("共", len(manifest), "张")
