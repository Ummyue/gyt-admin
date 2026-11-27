/* ================================================================
 * 风险扫描表格 · 合并单元格横向分割线补绘（v1.38.9）
 * ----------------------------------------------------------------
 * 背景：rowspan 合并单元格时，合并区域**内部的横向分割线会消失**
 *      （rowspan 跨多行，内部本就没有行分隔线）。
 *      但内容合并到首行又会让内容挤在顶部（用户反馈）。
 *
 * 方案：rowspan 合并（内容垂直居中于整个分组），
 *      再按各行**实际渲染高度**在合并单元格内绝对定位补回横线。
 *
 * 用法：渲染表格后调用 paintMergedSeparators(root)
 * ================================================================ */
(function (global) {
  'use strict';

  function paintMergedSeparators(root) {
    var scope = root || global.document;
    var tds = scope.querySelectorAll('.risk-table tbody td[data-rspan]');
    Array.prototype.forEach.call(tds, function (td) {
      var old = td.querySelector('.merged-row-seps');
      if (old) old.remove();
      var rs = parseInt(td.getAttribute('rowspan'), 10);
      if (!(rs > 1)) return;
      var table = td.closest('table');
      if (!table || !table.tBodies.length) return;
      var rows = Array.prototype.slice.call(table.tBodies[0].rows);
      var startIdx = rows.indexOf(td.parentNode);
      if (startIdx < 0) return;
      var tdRect = td.getBoundingClientRect();
      var box = document.createElement('div');
      box.className = 'merged-row-seps';
      for (var i = 0; i < rs - 1; i++) {
        var row = rows[startIdx + i];
        if (!row) break;
        var rr = row.getBoundingClientRect();
        if (!rr.height) continue;                 // 隐藏的 panel 跳过
        var line = document.createElement('div');
        line.className = 'merged-row-sep';
        line.style.top = (rr.bottom - tdRect.top - (td.clientTop || 0)) + 'px';
        box.appendChild(line);
      }
      td.appendChild(box);
    });
  }

  global.paintMergedSeparators = paintMergedSeparators;

  /**
   * 延迟重绘：渲染时 panel 可能还没显示（行高为 0 → 量不到），
   * 所以推到下一帧再画；tab 切换 / 窗口缩放后行高会变，也要重画。
   */
  function scheduleMergedSeparators(root) {
    var run = function () { paintMergedSeparators(root); };
    if (global.requestAnimationFrame) global.requestAnimationFrame(run);
    else setTimeout(run, 0);
  }
  global.scheduleMergedSeparators = scheduleMergedSeparators;

  // 窗口尺寸变化 → 行高变化 → 需重新计算补线位置
  global.addEventListener('resize', function () {
    document.querySelectorAll('.risk-table').forEach(function (t) {
      paintMergedSeparators(t);
    });
  });
})(window);
