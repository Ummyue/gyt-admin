// filter-chips.js — 列表页筛选条件 chip 标签
// v1.7.99.16l：把已录入的筛选项作为 chip 标签显示在"当前搜索"位置
// 单个 chip 可点 × 单独删除，也可点"清除全部"清空所有
//
// v1.17.0 修复（2026-10-26）：chip 的 × 点不动
//   现象：先在输入框里输内容 → chip 出现 → 点 chip 上的 ×，无反应。
//   根因：点 × 的 mousedown 会让输入框失焦 → 触发 change → renderChips() 用
//         `chipsContainer.innerHTML = ''` 整体重建 → 用户正要点的那个 × 节点
//         在 mouseup/click 之前已被摘除，click 落在已分离节点上不冒泡 → 事件丢失。
//   修复：改为**按筛选项下标做增量对齐**（键 = data-filter-idx）：
//         只删除多余的 chip、只新建缺失的 chip、已有 chip 只更新取值；
//         顺序用 appendChild 归位（appendChild 对已有节点是移动，不是克隆），
//         因此节点身份始终保留，正在点击的 × 不会被摘掉。
//   影响面：shared/js/filter-chips.js 被 51 个列表页引用，此 bug 是全站通用的。
(function() {
  function getLabelText(filterItem) {
    var labelEl = filterItem.querySelector('.cp-filter-label');
    return labelEl ? labelEl.textContent.replace(/\s*\*\s*$/, '').trim() : '';
  }

  function getDisplayValue(el) {
    if (el.tagName === 'SELECT') {
      var opt = el.options[el.selectedIndex];
      return opt ? opt.text : '';
    }
    return el.value || '';
  }

  function isEmpty(el) {
    if (el.tagName === 'SELECT') return el.selectedIndex <= 0;
    return !el.value || el.value.trim() === '';
  }

  // 收集当前有值的筛选项
  function collectActive(panel) {
    var active = [];
    var items = panel.querySelectorAll('.cp-filter-item');
    Array.prototype.forEach.call(items, function(item, idx) {
      var input = item.querySelector('input, select');
      if (!input || isEmpty(input)) return;
      var value = getDisplayValue(input);
      if (!value) return;
      active.push({ idx: idx, label: getLabelText(item), value: value });
    });
    return active;
  }

  function createChip(a) {
    var chip = document.createElement('span');
    chip.className = 'filter-chip';
    chip.setAttribute('data-filter-idx', String(a.idx));
    chip.innerHTML = '<span class="filter-chip-key"></span>' +
      '<span class="filter-chip-val"></span>' +
      '<span class="filter-chip-close" data-remove-target title="删除该筛选条件">×</span>';
    return chip;
  }

  function renderChips(panel) {
    var chipsContainer = panel.querySelector('[data-filter-chips]');
    var emptyHint = panel.querySelector('.filter-empty-hint');
    var clearBtn = panel.querySelector('.clear-all-btn');
    if (!chipsContainer) return;

    var active = collectActive(panel);

    // ===== 增量对齐：保留已有 chip 节点，只增删改，不整体重建 =====
    var existing = Array.prototype.slice.call(chipsContainer.querySelectorAll('.filter-chip'));
    var existingMap = {};
    existing.forEach(function(ch) {
      existingMap[ch.getAttribute('data-filter-idx')] = ch;
    });

    // 1) 删除已不再有值的 chip
    var keepKeys = active.map(function(a) { return String(a.idx); });
    existing.forEach(function(ch) {
      if (keepKeys.indexOf(ch.getAttribute('data-filter-idx')) === -1) {
        ch.parentNode.removeChild(ch);
      }
    });

    // 2) 新建缺失的 / 更新已有的
    active.forEach(function(a, i) {
      var key = String(a.idx);
      var chip = existingMap[key];
      if (!chip) {
        chip = createChip(a);
      }
      var keyEl = chip.querySelector('.filter-chip-key');
      if (keyEl && keyEl.textContent !== a.label + '：') keyEl.textContent = a.label + '：';
      var valEl = chip.querySelector('.filter-chip-val');
      if (valEl && valEl.textContent !== a.value) valEl.textContent = a.value;
      // ⚠️ 只有顺序真的不对时才移动节点。
      // appendChild / insertBefore 对已在容器里的节点等于「移除 + 重新插入」，
      // 而 mousedown 与 mouseup 之间移动节点会让浏览器判定 mousedown / mouseup
      // 目标不一致 → 不派发 click 事件（点击丢失）。
      // 常规路径（输入框失焦触发 change，筛选项集合未变）顺序本就正确 → 这里不动 DOM。
      if (chipsContainer.children[i] !== chip) {
        chipsContainer.insertBefore(chip, chipsContainer.children[i] || null);
      }
    });

    var hasValue = active.length > 0;
    if (emptyHint) emptyHint.style.display = hasValue ? 'none' : '';
    if (clearBtn) clearBtn.style.display = hasValue ? '' : 'none';
  }

  // ===== × 删除：事件委托到 chipsContainer =====
  // 委托的好处：chip 节点即使被重建，监听器也不会丢。
  function bindChipClicks(panel) {
    var chipsContainer = panel.querySelector('[data-filter-chips]');
    if (!chipsContainer || chipsContainer.getAttribute('data-chip-bound')) return;
    chipsContainer.setAttribute('data-chip-bound', '1');
    chipsContainer.addEventListener('click', function(e) {
      var closeEl = e.target.closest('[data-remove-target]');
      if (!closeEl) return;
      var chip = closeEl.closest('.filter-chip');
      if (!chip) return;
      var idx = parseInt(chip.getAttribute('data-filter-idx'), 10);
      var items = panel.querySelectorAll('.cp-filter-item');
      var item = items[idx];
      if (!item) return;
      var input = item.querySelector('input, select');
      if (!input) return;
      if (input.tagName === 'SELECT') input.selectedIndex = 0;
      else input.value = '';
      // 同时触发 input + change 事件（确保所有监听器都收到通知）
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      renderChips(panel);
    });
  }

  // 暴露全局清除函数（按钮 onclick 用）
  window.clearAllFilters = function(btn) {
    var panel = btn.closest('[data-filter-panel]');
    if (!panel) {
      // 兜底：找最近的 cp-block / cp-panel
      panel = btn.closest('.cp-block, .cp-panel') || document;
    }
    panel.querySelectorAll('.cp-filter input, .cp-filter select').forEach(function(el) {
      if (el.tagName === 'SELECT') el.selectedIndex = 0;
      else el.value = '';
      // 同时触发 input + change 事件（与单个 chip 的 × 一致），
      // 否则页面 oninput/onchange 驱动的实时过滤不会重绘表格，只清输入框不清结果
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
    renderChips(panel);
  };

  // 初始化
  document.addEventListener('DOMContentLoaded', function() {
    // 每个筛选面板独立渲染（支持双 tap 切换、详情页等）
    var panels = document.querySelectorAll('[data-filter-panel]');
    if (panels.length === 0) {
      // 兼容旧版：把整个 cp-panel 当作一个面板
      document.querySelectorAll('.cp-panel').forEach(function(p) { p.setAttribute('data-filter-panel', ''); });
      panels = document.querySelectorAll('[data-filter-panel]');
    }
    panels.forEach(function(panel) {
      renderChips(panel);
      bindChipClicks(panel);
      panel.addEventListener('input', function(e) {
        if (e.target.matches('.cp-filter input, .cp-filter select')) renderChips(panel);
      });
      panel.addEventListener('change', function(e) {
        if (e.target.matches('.cp-filter input, .cp-filter select')) renderChips(panel);
      });
    });
  });
})();
