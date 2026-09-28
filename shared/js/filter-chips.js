// filter-chips.js — 列表页筛选条件 chip 标签
// v1.7.99.16l：把已录入的筛选项作为 chip 标签显示在"当前搜索"位置
// 单个 chip 可点 × 单独删除，也可点"清除全部"清空所有
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

  function renderChips(panel) {
    var chipsContainer = panel.querySelector('[data-filter-chips]');
    var emptyHint = panel.querySelector('.filter-empty-hint');
    var clearBtn = panel.querySelector('.clear-all-btn');
    if (!chipsContainer) return;
    chipsContainer.innerHTML = '';
    var hasValue = false;
    panel.querySelectorAll('.cp-filter-item').forEach(function(item) {
      var input = item.querySelector('input, select');
      if (!input || isEmpty(input)) return;
      var labelText = getLabelText(item);
      var value = getDisplayValue(input);
      if (!value) return;
      hasValue = true;
      var chip = document.createElement('span');
      chip.className = 'filter-chip';
      chip.innerHTML = '<span class="filter-chip-key">' + labelText + '：</span>' +
        '<span class="filter-chip-val">' + value + '</span>' +
        '<span class="filter-chip-close" data-remove-target title="删除该筛选条件">×</span>';
      chip.querySelector('[data-remove-target]').addEventListener('click', function() {
        if (input.tagName === 'SELECT') input.selectedIndex = 0;
        else input.value = '';
        // 同时触发 input + change 事件（确保所有监听器都收到通知）
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        renderChips(panel);
      });
      chipsContainer.appendChild(chip);
    });
    if (emptyHint) emptyHint.style.display = hasValue ? 'none' : '';
    if (clearBtn) clearBtn.style.display = hasValue ? '' : 'none';
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
      panel.addEventListener('input', function(e) {
        if (e.target.matches('.cp-filter input, .cp-filter select')) renderChips(panel);
      });
      panel.addEventListener('change', function(e) {
        if (e.target.matches('.cp-filter input, .cp-filter select')) renderChips(panel);
      });
    });
  });
})();
