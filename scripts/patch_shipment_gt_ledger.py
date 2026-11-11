#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 发货管理列表页 加「查看货转」货转台账弹窗（v1.30.0）。

改动 pages/shipment-out.html：
1. 样式：居中弹窗（gt-modal-*）
2. 弹窗 DOM
3. JS：GT_LEDGER 货转台账数据 + openGtLedger / renderGtLedger / closeGtLedger
4. 5 处「查看货转」按钮的 onclick：alert(mock) → openGtLedger(this)
5. 货转开具标识：已开具货转的行由「未开具」改「已开具」（保证 mock 内部自洽）
"""
import re
import sys

P = "pages/shipment-out.html"
s = open(P, encoding="utf-8").read()
orig = s

# ---------------------------------------------------------------- 1. 样式
CSS = """
    /* ===== 查看货转 · 货转台账弹窗（v1.30.0）===== */
    .gt-modal-mask {
      position: fixed; inset: 0; background: rgba(15, 23, 42, 0.45);
      display: none; align-items: center; justify-content: center;
      z-index: 9998; padding: 24px;
    }
    .gt-modal-mask.show { display: flex; }
    .gt-modal {
      background: #fff; border-radius: var(--radius-lg);
      width: 1240px; max-width: 100%; max-height: 88vh;
      display: flex; flex-direction: column; overflow: hidden;
      box-shadow: 0 20px 50px rgba(15, 23, 42, 0.22);
    }
    .gt-modal-head {
      padding: 16px 22px; border-bottom: 1px solid var(--border-default);
      display: flex; align-items: flex-start; justify-content: space-between;
      gap: 16px; flex-shrink: 0;
    }
    .gt-modal-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
    .gt-modal-sub { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; }
    .gt-modal-info { display: flex; flex-wrap: wrap; gap: 6px 22px; margin-top: 12px; }
    .gt-info-item { font-size: 12px; color: var(--text-tertiary); }
    .gt-info-item b { color: var(--text-primary); font-weight: 500; margin-left: 4px; }
    .gt-icon-btn {
      width: 28px; height: 28px; border-radius: var(--radius-default);
      border: none; background: none; cursor: pointer; color: var(--text-tertiary);
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .gt-icon-btn:hover { background: var(--bg-page); color: var(--text-primary); }
    .gt-modal-body { flex: 1; overflow: auto; }
    .gt-modal-foot {
      padding: 12px 22px; border-top: 1px solid var(--border-default);
      background: var(--bg-page); display: flex; align-items: center;
      justify-content: space-between; flex-shrink: 0;
    }
    .gt-foot-count { font-size: 12px; color: var(--text-tertiary); }
    .gt-table-wrap { overflow-x: auto; }
    .gt-table { width: 100%; border-collapse: collapse; min-width: 1080px; }
    .gt-table th {
      background: var(--bg-page); font-size: 12px; font-weight: 500;
      color: var(--text-secondary); text-align: left;
      padding: 10px 12px; border-bottom: 1px solid var(--border-default);
      white-space: nowrap;
    }
    .gt-table td {
      font-size: 13px; color: var(--text-primary);
      padding: 11px 12px; border-bottom: 1px solid var(--border-light);
      vertical-align: middle;
    }
    .gt-table tbody tr:hover { background: var(--bg-hover); }
    .gt-table .col-num { font-variant-numeric: tabular-nums; }
    .gt-table .txt-right { text-align: right; }
    .gt-empty { padding: 64px 20px; text-align: center; color: var(--text-tertiary); }
    .gt-empty-ico { font-size: 40px; opacity: .35; margin-bottom: 12px; }
    .gt-empty-title { font-size: 14px; color: var(--text-secondary); margin-bottom: 6px; }
    .gt-empty-hint { font-size: 12px; color: var(--text-tertiary); line-height: 1.7; }
    .tag-orange { background: #FFEDD5; color: #C2410C; }
"""

anchor = "    .cp-drawer-filter-buttons button { height: 30px; }\n  </style>"
assert anchor in s, "未找到 style 块尾部锚点"
s = s.replace(anchor, "    .cp-drawer-filter-buttons button { height: 30px; }\n" + CSS + "  </style>", 1)

# ---------------------------------------------------------------- 2. 弹窗 DOM
MODAL = """
  <!-- ===== 查看货转 · 货转台账弹窗（v1.30.0）===== -->
  <div class="gt-modal-mask" id="gtLedgerMask" onclick="if(event.target===this)closeGtLedger()">
    <div class="gt-modal" onclick="event.stopPropagation()">
      <div class="gt-modal-head">
        <div>
          <div class="gt-modal-title">查看货转台账</div>
          <div class="gt-modal-sub">展示该发货数据对应的货转台账信息，字段与货转管理列表一致</div>
          <div class="gt-modal-info" id="gtLedgerInfo"></div>
        </div>
        <button class="gt-icon-btn" onclick="closeGtLedger()" title="关闭">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="gt-modal-body" id="gtLedgerBody"></div>
      <div class="gt-modal-foot">
        <div class="gt-foot-count" id="gtLedgerCount"></div>
        <button class="btn btn-secondary" onclick="closeGtLedger()">关闭</button>
      </div>
    </div>
  </div>
"""

anchor = '<script src="../assets/js/pin-annotation.js"></script>'
assert anchor in s, "未找到 pin-annotation 锚点"
s = s.replace(anchor, MODAL + anchor, 1)

# ---------------------------------------------------------------- 3. JS
JS = r"""
    // ===== 查看货转 · 货转台账弹窗（v1.30.0）=====
    // 货转状态标签与 goods-transfer.html 的 GT_STATUS 保持一致
    var GT_STATUS_MAP = {
      'approving':                   { tag: '●平台运营审核中',   color: 'tag-yellow' },
      'awaiting-effect-voucher':     { tag: '●待上传已生效单据', color: 'tag-orange' },
      'effective':                   { tag: '●已生效',           color: 'tag-green' },
      'rejected':                    { tag: '●平台审批驳回',     color: 'tag-red' },
      'voided':                      { tag: '已作废',            color: 'tag-gray' }
    };

    // 货转台账 MOCK：key = 发货批次号，value = 该发货对应的货转记录（可 0 / 1 / 多条）
    // 字段与货转管理列表一致：货转编号 / 买方 / 卖方 / 收货人 / 货转开具日 / 数量 / 发运方式 / 状态
    // 合同编号 / 买方 / 卖方 / 收货人 取自发货行本身，保证与该笔发货对得上
    var GT_LEDGER = {
      // 一笔发货拆成两笔货转（其中一笔已作废）
      'BN202607290009': [
        { gtNo: 'SKBT202607040003-202607300001', date: '2026-04-22', qty: '50',     transport: '火运', status: 'effective' },
        { gtNo: 'SKBT202607040004-202607300002', date: '2026-04-25', qty: '872.25', transport: '火运', status: 'voided' }
      ],
      // 一笔发货对应一笔货转
      'BN202607290008': [
        { gtNo: 'SKBT202607040005-202607300003', date: '2026-04-15', qty: '922.25', transport: '火运', status: 'effective' }
      ],
      'BN202607290007': [
        { gtNo: 'SKBT202607040006-202607300004', date: '2026-04-05', qty: '474.9',  transport: '火运', status: 'effective' }
      ],
      // 货转审批中
      'BN202607290006': [
        { gtNo: 'SKBT202607040007-202607300005', date: '2026-03-27', qty: '973.25', transport: '火运', status: 'approving' }
      ],
      // 该批次尚未开具货转 → 空态
      'BN202607290003': []
    };

    function openGtLedger(el) {
      var tr = el && el.closest ? el.closest('tr') : null;
      if (!tr) return;
      var cells = tr.querySelectorAll('td');
      var info = {
        contract: cells[0] ? cells[0].textContent.trim() : '',
        batchNo:  cells[1] ? cells[1].textContent.trim() : '',
        seller:   cells[2] ? cells[2].textContent.trim() : '',
        buyer:    cells[3] ? cells[3].textContent.trim() : '',
        receiver: cells[4] ? cells[4].textContent.trim() : ''
      };
      renderGtLedger(info);
      document.getElementById('gtLedgerMask').classList.add('show');
    }

    function renderGtLedger(info) {
      // 顶部：当前发货数据摘要
      document.getElementById('gtLedgerInfo').innerHTML =
        '<span class="gt-info-item">合同编号<b>' + esc(info.contract) + '</b></span>' +
        '<span class="gt-info-item">发货批次号<b>' + esc(info.batchNo) + '</b></span>' +
        '<span class="gt-info-item">卖方企业<b>' + esc(info.seller) + '</b></span>' +
        '<span class="gt-info-item">买方企业<b>' + esc(info.buyer) + '</b></span>';

      var rows = GT_LEDGER[info.batchNo] || [];
      var body = document.getElementById('gtLedgerBody');

      if (!rows.length) {
        body.innerHTML = '<div class="gt-empty">'
          + '<div class="gt-empty-ico">📄</div>'
          + '<div class="gt-empty-title">该发货数据暂未开具货转台账</div>'
          + '<div class="gt-empty-hint">发货批次号 ' + esc(info.batchNo) + ' 尚未关联货转记录<br>'
          + '可在「数字供应链 → 货转管理」中查看全部货转台账</div>'
          + '</div>';
        document.getElementById('gtLedgerCount').textContent = '共 0 条货转台账';
        return;
      }

      body.innerHTML = '<div class="gt-table-wrap"><table class="gt-table">'
        + '<thead><tr>'
        + '<th style="width: 150px;">合同编号</th>'
        + '<th style="width: 175px;">货转编号</th>'
        + '<th style="width: 180px;">买方企业</th>'
        + '<th style="width: 180px;">卖方企业</th>'
        + '<th style="width: 180px;">收货人</th>'
        + '<th style="width: 100px;">货转开具日</th>'
        + '<th style="width: 105px; text-align: right;">货转数量(吨)</th>'
        + '<th style="width: 110px;">发运方式</th>'
        + '<th style="width: 130px;">状态</th>'
        + '</tr></thead><tbody>'
        + rows.map(function (r) {
            var st = GT_STATUS_MAP[r.status] || GT_STATUS_MAP['effective'];
            return '<tr>'
              + '<td class="col-num">' + esc(info.contract) + '</td>'
              + '<td class="col-num">' + esc(r.gtNo) + '</td>'
              + '<td>' + esc(info.buyer) + '</td>'
              + '<td>' + esc(info.seller) + '</td>'
              + '<td>' + esc(info.receiver) + '</td>'
              + '<td class="col-num">' + esc(r.date) + '</td>'
              + '<td class="col-num txt-right">' + esc(r.qty) + '</td>'
              + '<td>' + esc(r.transport) + '</td>'
              + '<td><span class="tag ' + st.color + '">' + st.tag + '</span></td>'
              + '</tr>';
          }).join('')
        + '</tbody></table></div>';
      document.getElementById('gtLedgerCount').textContent = '共 ' + rows.length + ' 条货转台账';
    }

    function closeGtLedger() {
      document.getElementById('gtLedgerMask').classList.remove('show');
    }

    // 文本转义（台账里拼接了公司名/编号，统一走一次转义）
    function esc(str) {
      return String(str == null ? '' : str).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
      });
    }

    // Esc 关闭货转台账弹窗
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        var mask = document.getElementById('gtLedgerMask');
        if (mask && mask.classList.contains('show')) closeGtLedger();
      }
    });
"""

anchor = "    // v1.7.99.162 状态机切换：4 tab（全部/待收货/已收货/已作废）"
assert anchor in s, "未找到 JS 插入锚点"
s = s.replace(anchor, JS + "\n" + anchor, 1)

# ---------------------------------------------------------------- 4. 按钮 onclick
n = s.count("alert('操作：查看货转（mock）')")
s = s.replace("alert('操作：查看货转（mock）')", "openGtLedger(this)")
print("替换「查看货转」按钮 onclick：%d 处" % n)

# ---------------------------------------------------------------- 5. 货转开具标识自洽
# 有货转台账的行：未开具 → 已开具
rows_changed = 0
def fix_row(m):
    global rows_changed
    block = m.group(0)
    mm = re.search(r'<td class="col-num">(BN\d+)</td>', block)
    if not mm:
        return block
    batch = mm.group(1)
    if batch in ('BN202607290009', 'BN202607290008', 'BN202607290007', 'BN202607290006'):
        new = block.replace('<td>未开具</td>', '<td>已开具</td>', 1)
        if new != block:
            rows_changed += 1
        return new
    return block

s = re.sub(r'<tr data-status="received">.*?</tr>', fix_row, s, flags=re.S)
print("货转开具标识改为「已开具」的行：%d 行" % rows_changed)

assert s != orig
open(P, "w", encoding="utf-8").write(s)
print("✅ shipment-out.html 已更新")
