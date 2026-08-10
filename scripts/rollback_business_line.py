#!/usr/bin/env python3
"""
回滚 v1.7.99.187 / v1.7.99.188 在 business-line.html 和 business-line-detail.html 的所有改动
"""

import re
from pathlib import Path

ROOT = Path("/Users/fuyu/.mavis/agents/mavis/workspace/yugangtong-prototype")

# ============================================================
# 1) business-line.html 回滚
# ============================================================
BL_FILE = ROOT / "pages" / "business-line.html"
content = BL_FILE.read_text(encoding="utf-8")
print(f"原 business-line.html: {len(content)} 字符")

# a) 删除 v1.7.99.188 列设置 CSS 块
css_block = '''    /* v1.7.99.188 表头列显示隐藏工具栏 */
    .bl-col-toggle-bar { display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; border-bottom: 1px solid var(--border-color); background: #fafbfc; }
    .bl-col-toggle-tip { font-size: 12px; color: var(--text-tertiary); }
    .bl-col-toggle-bar-right { position: relative; }
    .bl-col-toggle-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; border: 1px solid var(--border-color); border-radius: 4px; background: #fff; color: var(--text-primary); font-size: 13px; cursor: pointer; }
    .bl-col-toggle-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
    .bl-col-toggle-panel { position: absolute; top: calc(100% + 4px); right: 0; z-index: 100; min-width: 200px; background: #fff; border: 1px solid var(--border-color); border-radius: 6px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); padding: 12px 16px; }
    .bl-col-toggle-panel-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border-color); }
    .bl-col-toggle-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 13px; color: var(--text-primary); cursor: pointer; }
    .bl-col-toggle-item input[type="checkbox"] { cursor: pointer; }
    .bl-col-toggle-panel-footer { margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--border-color); text-align: right; }

'''
if css_block in content:
    content = content.replace(css_block, "")
    print("✅ 删 v1.7.99.188 CSS 块")

# b) 删除 5 个新筛选项
filter_block = '''              <!-- v1.7.99.188 新增：6 个字段筛选（项目编号/项目名称/采销框架合同/采销订单/上下游企业） -->
              <div class="cp-filter-item">
                <span class="cp-filter-label">项目编号</span>
                <input type="text" class="input" placeholder="请输入项目编号">
              </div>
              <div class="cp-filter-item">
                <span class="cp-filter-label">项目名称</span>
                <input type="text" class="input" placeholder="请输入项目名称">
              </div>
              <div class="cp-filter-item">
                <span class="cp-filter-label">采/销框架合同</span>
                <input type="text" class="input" placeholder="请输入采购/销售框架合同编号">
              </div>
              <div class="cp-filter-item">
                <span class="cp-filter-label">采/销订单</span>
                <input type="text" class="input" placeholder="请输入采购/销售订单/单批次合同编号">
              </div>
              <div class="cp-filter-item">
                <span class="cp-filter-label">上下游企业</span>
                <input type="text" class="input" placeholder="请输入上游/下游/业务主体企业名称">
              </div>
'''
if filter_block in content:
    content = content.replace(filter_block, "")
    print("✅ 删 5 个新筛选项")

# c) 删除列设置工具栏 HTML
toolbar_block = '''            <!-- v1.7.99.188 表头列显示隐藏工具栏 -->
            <div class="bl-col-toggle-bar">
              <div class="bl-col-toggle-bar-left">
                <span class="bl-col-toggle-tip">提示：点击右侧"列设置"可自定义显示/隐藏表头列</span>
              </div>
              <div class="bl-col-toggle-bar-right">
                <button type="button" class="bl-col-toggle-btn" id="colToggleBtn" onclick="toggleColPanel(event)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                  列设置
                </button>
                <div class="bl-col-toggle-panel" id="colTogglePanel" style="display: none;">
                  <div class="bl-col-toggle-panel-title">自定义列显示</div>
                  <label class="bl-col-toggle-item"><input type="checkbox" data-col-idx="1" checked onchange="toggleColumn(1, this.checked)"> 业务线信息</label>
                  <label class="bl-col-toggle-item"><input type="checkbox" data-col-idx="2" checked onchange="toggleColumn(2, this.checked)"> 货物进度</label>
                  <label class="bl-col-toggle-item"><input type="checkbox" data-col-idx="3" checked onchange="toggleColumn(3, this.checked)"> 资金进度</label>
                  <label class="bl-col-toggle-item"><input type="checkbox" data-col-idx="4" checked onchange="toggleColumn(4, this.checked)"> 结算进度</label>
                  <label class="bl-col-toggle-item"><input type="checkbox" data-col-idx="5" checked onchange="toggleColumn(5, this.checked)"> 发票进度</label>
                  <label class="bl-col-toggle-item"><input type="checkbox" data-col-idx="6" checked onchange="toggleColumn(6, this.checked)"> 操作</label>
                  <div class="bl-col-toggle-panel-footer">
                    <button type="button" class="btn btn-text btn-sm" onclick="resetColumnPref()">恢复默认</button>
                  </div>
                </div>
              </div>
            </div>
'''
if toolbar_block in content:
    content = content.replace(toolbar_block, "")
    print("✅ 删 列设置工具栏 HTML")

# d) 删除 v1.7.99.188 JS 块
js_block = '''
    // v1.7.99.188 表头列显示隐藏
    const COL_PREF_KEY = 'business-line-col-pref';

    function toggleColPanel(e) {
      if (e) e.stopPropagation();
      const panel = document.getElementById('colTogglePanel');
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }

    // 点击页面其他位置关闭列设置面板
    document.addEventListener('click', function(e) {
      const panel = document.getElementById('colTogglePanel');
      const btn = document.getElementById('colToggleBtn');
      if (!panel || !btn) return;
      if (panel.contains(e.target) || btn.contains(e.target)) return;
      panel.style.display = 'none';
    });

    function toggleColumn(colIdx, show) {
      // 通过 nth-child 控制 th + 所有 td
      const display = show ? '' : 'none';
      document.querySelectorAll('.cp-table tr > *:nth-child(' + colIdx + ')').forEach(function(el) {
        el.style.display = display;
      });
      saveColumnPref();
    }

    function saveColumnPref() {
      const checks = document.querySelectorAll('#colTogglePanel input[type="checkbox"]');
      const pref = {};
      checks.forEach(function(c) {
        pref[c.getAttribute('data-col-idx')] = c.checked;
      });
      try { localStorage.setItem(COL_PREF_KEY, JSON.stringify(pref)); } catch (e) {}
    }

    function loadColumnPref() {
      let pref = null;
      try { pref = JSON.parse(localStorage.getItem(COL_PREF_KEY) || 'null'); } catch (e) {}
      if (!pref) return;
      Object.keys(pref).forEach(function(idx) {
        const show = pref[idx];
        const checkbox = document.querySelector('#colTogglePanel input[data-col-idx="' + idx + '"]');
        if (checkbox) {
          checkbox.checked = show;
          toggleColumn(parseInt(idx, 10), show);
        }
      });
    }

    function resetColumnPref() {
      try { localStorage.removeItem(COL_PREF_KEY); } catch (e) {}
      document.querySelectorAll('#colTogglePanel input[type="checkbox"]').forEach(function(c) {
        c.checked = true;
        toggleColumn(parseInt(c.getAttribute('data-col-idx'), 10), true);
      });
    }

    // 页面加载时应用用户偏好
    loadColumnPref();
'''
if js_block in content:
    content = content.replace(js_block, "")
    print("✅ 删 v1.7.99.188 JS 块")

# e) 删除 4 行 mock 数据中的 6 个新字段（v1.7.99.187）
# 4 行的字段格式一致，每行 6 个 bl-info-line
# 通用模式：6 个 bl-info-line + 1 个原有的 bl-info-line
for no in ["YWX202309050001", "YWX202309050002", "YWX202309050003", "YWX202309050004"]:
    idx = int(no[-1])
    new_fields = (
        f'<div class="bl-info-line">采购订单/单批次合同编号：<a class="bl-link" href="./contract-purchase-order-detail.html">JYX-DPC-2023090500{idx}</a></div>\n                    '
        f'<div class="bl-info-line">销售订单/单批次合同编号：<a class="bl-link" href="./contract-sales-order-detail.html">XS-DPC-2023090500{idx}</a></div>\n                    '
        f'<div class="bl-info-line">项目编号：<span class="bl-co">PRJ20230905000{idx}</span></div>\n                    '
        f'<div class="bl-info-line">项目名称：<span class="bl-co">'  # 注意项目名称不同行不同
    )
    # 用正则匹配更稳
    pattern = re.compile(
        r'<div class="bl-info-line">采购订单/单批次合同编号：.*?</div>\s*'
        r'<div class="bl-info-line">销售订单/单批次合同编号：.*?</div>\s*'
        r'<div class="bl-info-line">项目编号：<span class="bl-co">PRJ20230905000\d</span></div>\s*'
        r'<div class="bl-info-line">项目名称：<span class="bl-co">[^<]+</span></div>\s*'
        r'<div class="bl-info-line">采购框架合同编号：<a class="bl-link" href="./contract-purchase-framework-detail\.html">CG-KJ-202309-00\d</a></div>\s*'
        r'<div class="bl-info-line">销售框架合同编号：<a class="bl-link" href="./contract-sales-framework-detail\.html">XS-KJ-202309-00\d</a></div>'
    )
    m = pattern.search(content)
    if m:
        content = content[:m.start()] + content[m.end():]
        print(f"✅ 删 {no} 的 6 个新字段")
    else:
        print(f"⚠️  找不到 {no} 的 6 个新字段")

BL_FILE.write_text(content, encoding="utf-8")
print(f"\n新 business-line.html: {len(content)} 字符 (减少 {len(content) - len(BL_FILE.read_text(encoding='utf-8')) + len(content)} 字符)")

# ============================================================
# 2) business-line-detail.html 回滚
# ============================================================
BLD_FILE = ROOT / "pages" / "business-line-detail.html"
content = BLD_FILE.read_text(encoding="utf-8")
print(f"\n原 business-line-detail.html: {len(content)} 字符")

new_meta = '''          <!-- 业务线信息行 v1.7.99.187：业务线名称后/类型前 + 业务线号前共 6 字段（v1.7.99.187 新增台账字段） -->
          <div class="bl-header-meta">
            <div>采购订单/单批次合同编号：<a class="meta-link" href="./contract-purchase-order-detail.html">JYX-DPC-20260705001</a></div>
            <div>销售订单/单批次合同编号：<a class="meta-link" href="./contract-sales-order-detail.html">XS-DPC-20260705001</a></div>
            <div>项目编号：<span class="meta-value">PRJ202607050001</span></div>
            <div>项目名称：<span class="meta-value">2026年度木薯淀粉供应链项目</span></div>
            <div>采购框架合同编号：<a class="meta-link" href="./contract-purchase-framework-detail.html">CG-KJ-202601-001</a></div>
            <div>销售框架合同编号：<a class="meta-link" href="./contract-sales-framework-detail.html">XS-KJ-202601-001</a></div>
            <div>业务线号：<span class="meta-value">SKYWX202607050001</span></div>
            <div>采购合同：<span class="meta-link">GTGYL-MSXS-20260127-s</span></div>
            <div>销售合同：<span class="meta-link">YL-MSXS-20260127-s</span></div>
            <div>创建时间：<span class="meta-value">2026-07-05 09:50:24</span></div>
          </div>'''
old_meta = '''          <!-- 业务线信息行 v1.7.99.87：业务线号 + 采购合同 + 销售合同 + 创建时间（合同号 -s 后缀） -->
          <div class="bl-header-meta">
            <div>业务线号：<span class="meta-value">SKYWX202607050001</span></div>
            <div>采购合同：<span class="meta-link">GTGYL-MSXS-20260127-s</span></div>
            <div>销售合同：<span class="meta-link">YL-MSXS-20260127-s</span></div>
            <div>创建时间：<span class="meta-value">2026-07-05 09:50:24</span></div>
          </div>'''
if new_meta in content:
    content = content.replace(new_meta, old_meta)
    print("✅ 回滚 business-line-detail.html 头部 meta")
    BLD_FILE.write_text(content, encoding="utf-8")
    print(f"新 business-line-detail.html: {len(content)} 字符")
else:
    print("⚠️  找不到新 meta 块，无需回滚")

print("\n回滚完成")
