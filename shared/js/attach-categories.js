/* ==========================================================================
 * 通用「附件分类」增强组件  attach-categories.js
 * --------------------------------------------------------------------------
 * 用途：给任意页面的附件区补齐三件事
 *   1. 每个材料类别行新增「上传无此附件说明」入口（说明材料缺失原因，非材料本体）
 *   2. 上传后**回显文件名称**（可预览 / 更换 / 删除）
 *   3. 附件区下方追加「自定义附件」分区（新增 / 改名 / 删除条目 + 各自上传）
 *
 * 与 project-apply.html 内联的「客户准入材料上传」保持同一套交互口径。
 *
 * --------------------------------------------------------------------------
 * 配置方式（由 scripts/inject_attach_feature.py 注入到页面）：
 *   window.__ATTACH_ZONES__ = [
 *     { zone: '<容器选择器>', row: '<类别行选择器>' },
 *     ...
 *   ]
 *   · zone —— 附件区容器（自定义附件分区追加到它之后）
 *   · row  —— 容器内的「材料类别行」选择器
 *   未显式配置时，组件会按约定自动识别：
 *     zone = 含 table.attach-table 的最近容器
 *     row  = 该容器内的 tbody > tr
 *
 * 零依赖、零构建、不引任何 CDN；所有样式由本组件注入 <style>。
 * ========================================================================== */
(function () {
  'use strict';

  var STYLE_ID = 'ac-style';
  var CSS = [
    /* 行内文件 chip */
    '.ac-files{display:inline-flex;flex-wrap:wrap;gap:6px;align-items:center;vertical-align:middle;margin-right:8px;}',
    '.ac-chip{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border:1px solid var(--border-light,rgba(15,23,42,.1));border-radius:10px;background:#fff;font-size:11px;color:var(--text-primary,#1f2937);max-width:220px;}',
    '.ac-chip:hover{border-color:var(--color-primary,#1E40AF);}',
    '.ac-chip .ac-chip-ico{font-size:12px;}',
    '.ac-chip .ac-chip-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:pointer;}',
    '.ac-chip .ac-chip-x{cursor:pointer;color:var(--text-tertiary,#94a3b8);font-size:12px;line-height:1;}',
    '.ac-chip .ac-chip-x:hover{color:#DC2626;}',
    '.ac-chip.ac-nosuch{border-color:rgba(180,83,9,.35);background:#FFFBEB;}',
    '.ac-chip .ac-chip-badge{padding:0 5px;border-radius:3px;background:rgba(180,83,9,.14);color:#B45309;font-size:10px;font-weight:600;}',
    /* 自动补建的「↑ 上传」按钮（该类别行原本没有上传入口时） */
    '.ac-btn-upload{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border:1px solid var(--border-light,rgba(15,23,42,.1));border-radius:4px;background:#fff;color:var(--color-primary,#1E40AF);font-size:11px;cursor:pointer;transition:all .15s;white-space:nowrap;}',
    '.ac-btn-upload:hover{background:rgba(30,64,175,.08);border-color:var(--color-primary,#1E40AF);}',
    /* 「上传无此附件说明」按钮 */
    '.ac-btn-nosuch{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border:1px dashed rgba(180,83,9,.4);border-radius:4px;background:#FFFBEB;color:#B45309;font-size:11px;cursor:pointer;transition:all .15s;white-space:nowrap;}',
    '.ac-btn-nosuch:hover{border-color:#B45309;background:#FEF3C7;color:#92400E;}',
    /* 自定义附件分区 */
    '.ac-custom{margin-top:12px;border:1px solid var(--border-light,rgba(15,23,42,.1));border-radius:6px;overflow:hidden;}',
    '.ac-custom-head{display:flex;align-items:center;gap:8px;padding:10px 14px;background:#F8FAFC;border-bottom:1px solid var(--border-light,rgba(15,23,42,.1));}',
    '.ac-custom-head .ac-custom-title{font-size:13px;font-weight:600;color:var(--text-primary,#1f2937);}',
    '.ac-custom-head .ac-custom-count{font-size:12px;color:var(--text-secondary,#64748b);}',
    '.ac-custom-head .ac-custom-progress{margin-left:auto;font-size:12px;color:var(--text-secondary,#64748b);}',
    '.ac-custom-add-btn{padding:3px 10px;border:1px dashed var(--color-primary,#1E40AF);border-radius:4px;background:rgba(30,64,175,.04);color:var(--color-primary,#1E40AF);font-size:11px;cursor:pointer;}',
    '.ac-custom-add-btn:hover{background:rgba(30,64,175,.12);}',
    '.ac-custom-row{display:flex;align-items:center;gap:10px;padding:8px 14px;border-top:1px solid var(--border-light,rgba(15,23,42,.1));}',
    '.ac-custom-row:first-of-type{border-top:none;}',
    '.ac-custom-row .ac-custom-name{font-size:13px;font-weight:500;color:#6D28D9;cursor:pointer;}',
    '.ac-custom-row .ac-custom-name:hover{text-decoration:underline;}',
    '.ac-custom-row .ac-custom-tag{padding:1px 6px;border-radius:3px;font-size:10px;font-weight:500;background:rgba(100,116,139,.1);color:#64748B;}',
    '.ac-custom-row .ac-custom-del{padding:3px 10px;border:1px solid var(--border-light,rgba(15,23,42,.1));border-radius:3px;background:#fff;font-size:11px;color:var(--text-secondary,#64748b);cursor:pointer;}',
    '.ac-custom-row .ac-custom-del:hover{color:#DC2626;border-color:#DC2626;background:#FEF2F2;}',
    '.ac-custom-row .ac-custom-input{font-size:13px;font-weight:500;color:var(--text-primary,#1f2937);border:1px solid var(--color-primary,#1E40AF);border-radius:3px;padding:2px 8px;width:240px;}',
    '.ac-custom-addrow{display:flex;align-items:center;gap:8px;padding:10px 14px;border-top:1px dashed var(--border-light,rgba(15,23,42,.1));background:#FFFBEB;}',
    '.ac-custom-addrow input{flex:1;font-size:13px;padding:5px 10px;border:1px solid var(--border-light,rgba(15,23,42,.1));border-radius:4px;}',
    '.ac-custom-addrow input:focus{outline:none;border-color:var(--color-primary,#1E40AF);}',
    '.ac-custom-addrow .ac-hint{font-size:11px;color:var(--text-tertiary,#94a3b8);}',
    '.ac-empty{padding:10px 14px;font-size:12px;color:var(--text-tertiary,#94a3b8);}',
    /* ===== 客户准入材料区（.cm-*，与 project-apply 的材料清单视觉一致） ===== */
    '.cm-material-section{margin-top:20px;padding-top:18px;border-top:1px dashed var(--border-light,rgba(15,23,42,.1));}',
    '.cm-material-section-title{font-size:14px;font-weight:600;color:var(--text-primary,#1f2937);margin-bottom:6px;}',
    '.cm-material-section-hint{font-size:12px;color:var(--text-tertiary,#94a3b8);line-height:1.7;margin-bottom:12px;}',
    '.cm-mats-summary{display:flex;align-items:center;gap:8px;margin-bottom:10px;}',
    '.cm-mats-summary .sum-chip{padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;}',
    '.cm-mats-summary .sum-chip.req-pending{background:rgba(220,38,38,.1);color:#B91C1C;}',
    '.cm-mats-summary .sum-chip.req-done{background:rgba(4,120,87,.12);color:#047857;}',
    '.cm-mats-summary .sum-chip.opt{background:rgba(100,116,139,.1);color:#64748B;}',
    '.cm-mat-row{display:flex;align-items:center;gap:10px;padding:8px 12px;border:1px solid var(--border-light,rgba(15,23,42,.1));border-radius:6px;margin-bottom:6px;background:#fff;}',
    '.cm-mat-row:hover{border-color:var(--color-primary,#1E40AF);}',
    '.cm-mat-row .row-left{display:flex;align-items:center;gap:8px;flex:1;min-width:0;}',
    '.cm-mat-row .row-num{color:var(--text-tertiary,#94a3b8);font-size:12px;min-width:20px;}',
    '.cm-mat-row .row-name{font-size:13px;color:var(--text-primary,#1f2937);font-weight:500;}',
    '.cm-mat-row .req-star{color:#DC2626;font-weight:700;font-size:13px;}',
    '.cm-mat-row .req-tag-mini{padding:1px 6px;border-radius:3px;font-size:10px;font-weight:500;}',
    '.cm-mat-row .req-tag-mini.req{background:rgba(220,38,38,.1);color:#B91C1C;}',
    '.cm-mat-row .req-tag-mini.opt{background:rgba(100,116,139,.1);color:#64748B;}',
    '.cm-mat-row.req-required{box-shadow:inset 3px 0 0 0 #DC2626;}',
    '.cm-mat-row.req-required .row-num{color:#DC2626;font-weight:600;}',
    '.cm-mat-row .row-right{display:flex;align-items:center;gap:8px;flex-shrink:0;}',
    '.cm-mat-row .upload-btn{padding:4px 12px;border:1px solid var(--color-primary,#1E40AF);border-radius:4px;background:#fff;color:var(--color-primary,#1E40AF);font-size:12px;cursor:pointer;}',
    '.cm-mat-row .upload-btn:hover{background:rgba(30,64,175,.08);}'
  ].join('\n');

  /* ---------------- 状态 ---------------- */
  var ZONES = {};       // zoneId → { rows:{key:{label,files:[]}}, customs:[{id,label,files:[]}] }
  var SEQ = 0;
  var CONFIRM = null;    // 待确认删除的自定义条目

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function toast(msg, type) {
    if (window.Utils && Utils.toast) { Utils.toast(msg, type || 'info'); return; }
    console.log('[attach]', msg);
  }
  function injectStyle() {
    if (document.getElementById(STYLE_ID)) return;
    var st = document.createElement('style');
    st.id = STYLE_ID;
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  /* ---------------- 定位 ---------------- */
  function resolveZone(cfg) {
    // 方式 1：按「区标题文本」定位（标题元素的父容器里再取 zoneSel）
    if (cfg.titleSel && cfg.titleText) {
      var titles = Array.from(document.querySelectorAll(cfg.titleSel));
      var hit = titles.filter(function (t) {
        return t.textContent && t.textContent.indexOf(cfg.titleText) >= 0;
      });
      if (hit.length) {
        // 标题的父级可能只是「标题条」，不一定包含区内容 → 向上逐级找
        var up = hit[0].parentElement;
        for (var d = 0; up && d < 6; d++, up = up.parentElement) {
          if (cfg.zoneSel) {
            var zs = up.querySelectorAll(cfg.zoneSel);
            if (zs.length) return zs[0];
          } else {
            return up;
          }
        }
        // 兜底：标题的最近祖先里若直接带 zoneSel 类
        up = hit[0].parentElement;
        for (var d2 = 0; up && d2 < 6; d2++, up = up.parentElement) {
          if (cfg.zoneSel && up.matches && up.matches(cfg.zoneSel)) return up;
        }
        return hit[0].parentElement;
      }
    }
    if (cfg.zone) {
      var list = Array.from(document.querySelectorAll(cfg.zone));
      if (cfg.filter) {
        // 按「区标题文本」筛选：标题通常是容器的上一个兄弟
        var h2 = list.filter(function (z) {
          var t = z.previousElementSibling;
          return t && t.textContent && t.textContent.indexOf(cfg.filter) >= 0;
        });
        if (h2.length) return h2[0];
        h2 = list.filter(function (z) {
          return z.textContent && z.textContent.indexOf(cfg.filter) >= 0;
        });
        if (h2.length) return h2[0];
      }
      if (list.length) return list[0];
    }
    // 自动：含 attach-table 的最近容器
    var t = document.querySelector('table.attach-table');
    if (!t) return null;
    return t.closest('.info-section-body, .form-section-body, .card-body, .block, .info-section, .form-section, .block-body') || t.parentElement;
  }
  function resolveRows(zone, cfg) {
    var sel = cfg.row || 'tbody > tr';
    var rows = Array.from(zone.querySelectorAll(sel));
    if (!rows.length && cfg.row) rows = Array.from(zone.querySelectorAll('tbody > tr'));
    return rows;
  }
  function rowLabel(row) {
    var el = row.querySelector('.attach-label, .bl-up-label, .row-name, .ac-label');
    if (el) return el.textContent.replace(/\s+/g, ' ').trim();
    var td = row.querySelector('td');
    if (td) return td.textContent.replace(/\s+/g, ' ').replace(/^\*\s*/, '').trim();
    return '';
  }
  function findUploadBtn(row) {
    return row.querySelector(
      'button.upload-btn, a.upload-btn, button.attach-btn, button.attach-upload-btn, ' +
      '.bl-up-btn button, button[class*="upload"], a[class*="upload"]'
    );
  }
  function rowAnchor(row, btn) {
    return btn ? btn.parentElement : row;
  }

  /* ---------------- 文件操作 ---------------- */
  function pickFile(zoneId, key, kind, row) {
    var inp = document.createElement('input');
    inp.type = 'file';
    inp.multiple = true;
    inp.style.display = 'none';
    inp.addEventListener('change', function () {
      var files = Array.from(inp.files || []);
      files.forEach(function (f) { addFile(zoneId, key, kind, f); });
      inp.remove();
    });
    document.body.appendChild(inp);
    inp.click();
  }
  function addFile(zoneId, key, kind, file) {
    var st = ZONES[zoneId];
    if (!st) return;
    if (file.size > 100 * 1024 * 1024) { toast(file.name + ' 超过 100MB，请压缩后再上传', 'warn'); return; }
    var reader = new FileReader();
    reader.onload = function (e) {
      var target = st.rows[key] ? st.rows[key].files : null;
      if (!target) {
        st.customs.forEach(function (c) { if (c.id === key) target = c.files; });
      }
      if (!target) return;
      target.push({
        name: file.name, size: file.size, type: file.type, dataUrl: e.target.result,
        noSuch: kind === 'no-such',
        uploadedAt: new Date().toLocaleString('zh-CN', { hour12: false })
      });
      renderZone(zoneId);
      toast((kind === 'no-such' ? '无此附件说明' : '附件') + '上传成功：' + file.name, 'success');
    };
    reader.readAsDataURL(file);
  }
  function sizeText(b) {
    if (!b && b !== 0) return '';
    if (b < 1024) return b + ' B';
    if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1024 / 1024).toFixed(2) + ' MB';
  }
  function fileChipHtml(f, idx, zoneId, key) {
    return '<span class="ac-chip' + (f.noSuch ? ' ac-nosuch' : '') + '" title="' + esc(f.name + ' · ' + sizeText(f.size) + ' · ' + f.uploadedAt) + '">'
      + '<span class="ac-chip-ico">' + (f.type && f.type.indexOf('image/') === 0 ? '🖼️' : '📄') + '</span>'
      + (f.noSuch ? '<span class="ac-chip-badge">非本附件本体</span>' : '')
      + '<span class="ac-chip-name" data-ac-preview="' + zoneId + '|' + key + '|' + idx + '">' + esc(f.name) + '</span>'
      + '<span class="ac-chip-x" data-ac-del="' + zoneId + '|' + key + '|' + idx + '" title="删除">×</span>'
      + '</span>';
  }
  function filesHtml(files, zoneId, key) {
    if (!files || !files.length) return '';
    return files.map(function (f, i) { return fileChipHtml(f, i, zoneId, key); }).join('');
  }

  /* ---------------- 渲染：类别行 ---------------- */
  function renderRow(zoneId, row, key) {
    var st = ZONES[zoneId];
    var rec = st.rows[key];
    if (!rec) return;
    var btn = findUploadBtn(row);
    var anchor = rowAnchor(row, btn);
    var holder = anchor.querySelector('[data-ac-files]');
    if (!holder) {
      holder = document.createElement('span');
      holder.className = 'ac-files';
      holder.setAttribute('data-ac-files', key);
      if (btn) anchor.insertBefore(holder, btn);
      else anchor.appendChild(holder);
    }
    holder.innerHTML = filesHtml(rec.files, zoneId, key);

    // 「上传无此附件说明」按钮（放在上传按钮之后）
    var nb = row.querySelector('.ac-btn-nosuch');
    if (!nb) {
      nb = document.createElement('button');
      nb.type = 'button';
      nb.className = 'ac-btn-nosuch';
      nb.textContent = '📄 上传无此附件说明';
      nb.title = '上传无此附件说明（说明该材料缺失原因，非本材料本体）';
      nb.setAttribute('data-ac-nosuch', zoneId + '|' + key);
      if (btn) btn.parentNode.insertBefore(nb, btn.nextSibling);
      else anchor.appendChild(nb);
    }
  }

  /* ---------------- 渲染：自定义附件分区 ---------------- */
  function customRowHtml(zoneId, c) {
    var editing = ZONES[zoneId].editing === c.id;
    var nameHtml = editing
      ? '<input class="ac-custom-input" id="ac-name-input" value="' + esc(c.label) + '"'
        + ' onkeydown="if(event.key===\'Enter\'){acCommitRename(this.value);}if(event.key===\'Escape\'){acCancelRename();}">'
      : '<span class="ac-custom-name" data-ac-rename="' + c.id + '" title="点击可修改附件名称">' + esc(c.label) + '</span>';
    return '<div class="ac-custom-row" data-ac-custom="' + c.id + '">'
      + nameHtml
      + '<span class="ac-custom-tag">自定义</span>'
      + '<span class="ac-files" data-ac-cfiles="' + c.id + '">' + filesHtml(c.files, zoneId, c.id) + '</span>'
      + '<button type="button" class="btn btn-default btn-sm" data-ac-cupload="' + zoneId + '|' + c.id + '">↑ 上传</button>'
      + '<button type="button" class="ac-btn-nosuch" data-ac-cnosuch="' + zoneId + '|' + c.id + '">📄 上传无此附件说明</button>'
      + '<button type="button" class="ac-custom-del" data-ac-cdel="' + zoneId + '|' + c.id + '">删除条目</button>'
      + '</div>';
  }
  function customZoneHtml(zoneId) {
    var st = ZONES[zoneId];
    var done = st.customs.filter(function (c) { return c.files.length > 0; }).length;
    var addRow = st.adding
      ? '<div class="ac-custom-addrow"><input type="text" id="ac-add-input" placeholder="请输入自定义附件名称，如「股东会决议书」"'
        + ' onkeydown="if(event.key===\'Enter\'){acCommitAdd();}if(event.key===\'Escape\'){acCancelAdd();}">'
        + '<span class="ac-hint">回车确认 · Esc 取消</span>'
        + '<button type="button" class="btn btn-primary btn-sm" data-ac-add-ok>确定</button>'
        + '<button type="button" class="btn btn-default btn-sm" data-ac-add-cancel>取消</button></div>'
      : '';
    return '<div class="ac-custom" data-ac-zone="' + zoneId + '">'
      + '<div class="ac-custom-head">'
      + '<span class="ac-custom-title">自定义附件</span>'
      + '<span class="ac-custom-count">（' + st.customs.length + ' 项）</span>'
      + '<span class="ac-custom-progress">' + done + ' / ' + st.customs.length + ' 已上传</span>'
      + '<button type="button" class="ac-custom-add-btn" data-ac-add>+ 新增附件</button>'
      + '</div>'
      + (st.customs.length
          ? st.customs.map(function (c) { return customRowHtml(zoneId, c); }).join('')
          : '<div class="ac-empty">暂无自定义附件条目，点击「+ 新增附件」手动添加</div>')
      + addRow
      + '</div>';
  }

  /* ---------------- 渲染整个 zone ---------------- */
  function renderZone(zoneId) {
    var st = ZONES[zoneId];
    if (!st) return;
    Object.keys(st.rowEls).forEach(function (key) { renderRow(zoneId, st.rowEls[key], key); });
    var holder = st.holder;
    if (!holder) return;
    var html = customZoneHtml(zoneId);
    if (st.customHost) { st.customHost.innerHTML = html; }
    else {
      if (!st.customEl) {
        st.customEl = document.createElement('div');
        st.customEl.setAttribute('data-ac-custom-host', zoneId);
        holder.parentNode.insertBefore(st.customEl, holder.nextSibling);
      }
      st.customEl.innerHTML = html;
      st.customHost = st.customEl;
    }
    // 通知页面：zone 已重渲（页面可用它刷新自己的摘要计数）
    document.dispatchEvent(new CustomEvent('ac:zone-rendered', { detail: { zoneId: zoneId } }));
  }

  // 供页面查询 zone 内各行的文件状态（必填校验 / 摘要计数用）
  function getZoneState(zoneId) {
    var st = ZONES[zoneId];
    if (!st) return null;
    var rows = Object.keys(st.rows).map(function (k) {
      var r = st.rows[k];
      return { key: k, label: r.label, files: r.files.slice() };
    });
    return {
      zoneId: zoneId,
      rows: rows,
      customs: st.customs.map(function (c) {
        return { id: c.id, label: c.label, files: c.files.slice() };
      })
    };
  }

  /* ---------------- 自定义附件操作 ---------------- */
  function acAdd() {
    var zid = currentZone();
    if (!zid) return;
    ZONES[zid].adding = true;
    renderZone(zid);
    var i = document.getElementById('ac-add-input');
    if (i) i.focus();
  }
  function acCancelAdd() {
    var zid = currentZone();
    if (!zid) return;
    ZONES[zid].adding = false;
    renderZone(zid);
  }
  function acCommitAdd() {
    var zid = currentZone();
    if (!zid) return;
    var st = ZONES[zid];
    var i = document.getElementById('ac-add-input');
    var name = i ? i.value.trim() : '';
    if (!name) { toast('请输入附件名称', 'warn'); return; }
    if (st.customs.some(function (c) { return c.label === name; })) { toast('已存在同名附件「' + name + '」', 'warn'); return; }
    SEQ += 1;
    st.customs.push({ id: 'ac_c' + SEQ + '_' + Date.now(), label: name, files: [] });
    st.adding = false;
    renderZone(zid);
    toast('已新增自定义附件「' + name + '」', 'success');
  }
  function acStartRename(id) {
    var zid = currentZone();
    if (!zid) return;
    ZONES[zid].editing = id;
    renderZone(zid);
    var i = document.getElementById('ac-name-input');
    if (i) { i.focus(); i.select(); }
  }
  function acCancelRename() {
    var zid = currentZone();
    if (!zid) return;
    ZONES[zid].editing = null;
    renderZone(zid);
  }
  function acCommitRename(val) {
    var zid = currentZone();
    if (!zid) return;
    var st = ZONES[zid];
    if (!st.editing) return;
    var id = st.editing;
    var name = (val || '').trim();
    if (!name) { toast('附件名称不能为空', 'warn'); st.editing = null; renderZone(zid); return; }
    if (st.customs.some(function (c) { return c.id !== id && c.label === name; })) { toast('已存在同名附件「' + name + '」', 'warn'); return; }
    st.customs.forEach(function (c) { if (c.id === id) c.label = name; });
    st.editing = null;
    renderZone(zid);
  }
  function acDelete(zid, id) {
    if (!zid) return;
    var st = ZONES[zid];
    var c = st.customs.filter(function (x) { return x.id === id; })[0];
    if (!c) return;
    if (c.files.length > 0) {
      if (!window.confirm('自定义附件「' + c.label + '」已上传 ' + c.files.length
        + ' 个附件。\n删除该条目后，已上传的附件将一并删除且无法恢复。\n\n确定要删除吗？')) return;
    }
    st.customs = st.customs.filter(function (x) { return x.id !== id; });
    renderZone(zid);
    toast('已删除自定义附件「' + c.label + '」', 'success');
  }
  function currentZone() {
    // 事件发生时找最近的 zone
    var el = document.querySelector('[data-ac-zone]');
    return el ? el.getAttribute('data-ac-zone') : null;
  }

  /* ---------------- 预览 ---------------- */
  function acPreview(zoneId, key, idx) {
    var st = ZONES[zoneId];
    if (!st) return;
    var files = null;
    if (st.rows[key]) files = st.rows[key].files;
    else st.customs.forEach(function (c) { if (c.id === key) files = c.files; });
    var f = files && files[idx];
    if (!f || !f.dataUrl) return;
    var w = window.open();
    if (!w) return;
    var html = (f.type && f.type.indexOf('image/') === 0)
      ? '<img src="' + f.dataUrl + '" style="max-width:100%;height:auto">'
      : '<iframe src="' + f.dataUrl + '" style="width:100%;height:100%;border:none"></iframe>';
    w.document.write('<html><head><title>' + esc(f.name) + '</title></head><body style="margin:0;padding:8px">' + html + '</body></html>');
    w.document.close();
  }

  /* ---------------- 事件委托 ---------------- */
  function onClick(e) {
    var t = e.target;

    // 「上传无此附件说明」（类别行）
    var nos = t.closest('[data-ac-nosuch]');
    if (nos) {
      var p = nos.getAttribute('data-ac-nosuch').split('|');
      pickFile(p[0], p[1], 'no-such');
      return;
    }
    // 自定义条目 · 上传
    var cu = t.closest('[data-ac-cupload]');
    if (cu) { var cp = cu.getAttribute('data-ac-cupload').split('|'); pickFile(cp[0], cp[1], 'material'); return; }
    // 自定义条目 · 上传无此附件说明
    var cn = t.closest('[data-ac-cnosuch]');
    if (cn) { var cnp = cn.getAttribute('data-ac-cnosuch').split('|'); pickFile(cnp[0], cnp[1], 'no-such'); return; }
    // 自定义条目 · 删除条目
    var cd = t.closest('[data-ac-cdel]');
    if (cd) { var cdp = cd.getAttribute('data-ac-cdel').split('|'); acDelete(cdp[0], cdp[1]); return; }
    // 自定义条目 · 改名
    var rn = t.closest('[data-ac-rename]');
    if (rn) { acStartRename(rn.getAttribute('data-ac-rename')); return; }
    // 新增
    if (t.closest('[data-ac-add]')) { acAdd(); return; }
    if (t.closest('[data-ac-add-ok]')) { acCommitAdd(); return; }
    if (t.closest('[data-ac-add-cancel]')) { acCancelAdd(); return; }
    // 预览
    var pv = t.closest('[data-ac-preview]');
    if (pv) {
      var pp = pv.getAttribute('data-ac-preview').split('|');
      acPreview(pp[0], pp[1], parseInt(pp[2], 10));
      return;
    }
    // 删除文件
    var dl = t.closest('[data-ac-del]');
    if (dl) {
      var dp = dl.getAttribute('data-ac-del').split('|');
      var st2 = ZONES[dp[0]];
      if (!st2) return;
      var arr = st2.rows[dp[1]] ? st2.rows[dp[1]].files : null;
      if (!arr) st2.customs.forEach(function (c) { if (c.id === dp[1]) arr = c.files; });
      if (!arr) return;
      arr.splice(parseInt(dp[2], 10), 1);
      renderZone(dp[0]);
      return;
    }
  }

  /* ---------------- 初始化 ---------------- */
  function init() {
    injectStyle();
    var cfgs = window.__ATTACH_ZONES__ || [];
    cfgs.forEach(function (cfg, ci) {
      var zone = resolveZone(cfg);
      if (!zone) return;
      var zoneId = 'z' + ci + '_' + (zone.id || '');
      // 把 zoneId 写到容器上，页面可据此查状态（避免硬编码）
      zone.setAttribute('data-ac-zone-id', zoneId);
      var st = { rows: {}, rowEls: {}, customs: [], holder: zone, adding: false, editing: null };
      ZONES[zoneId] = st;
      var rows = resolveRows(zone, cfg);
      rows.forEach(function (row, ri) {
        var label = rowLabel(row);
        if (!label) return;
        var key = 'r' + ri;
        st.rows[key] = { label: label, files: [] };
        st.rowEls[key] = row;
        // 接管行内上传按钮 → 真实文件选择 + 文件名回显
        var btn = findUploadBtn(row);
        if (!btn) {
          // 该类别行原本**没有上传入口**（多为「已上传文件清单」型页面：
          // 操作列只有「下载」）→ 在行内补一个「↑ 上传」
          btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'ac-btn-upload';
          btn.textContent = '↑ 上传';
          btn.title = '上传该附件';
          var cell = row.querySelector('td:last-child') || row;
          cell.appendChild(btn);
        }
        if (!btn.getAttribute('data-ac-bound')) {
          btn.setAttribute('data-ac-bound', zoneId + '|' + key);
          btn.addEventListener('click', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            pickFile(zoneId, key, 'material');
          });
        }
      });
      renderZone(zoneId);
    });
    document.addEventListener('click', onClick, true);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        var zid = currentZone();
        if (zid) { ZONES[zid].adding = false; ZONES[zid].editing = null; renderZone(zid); }
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  // 暴露给页面内联 onkeydown 调用的全局函数
  // （组件本体在 IIFE 内，但自定义附件的内联输入框要用 onkeydown="acCommitAdd()"，
  //   这些函数必须挂到 window 上，否则内联处理器报 undefined）
  window.acCommitAdd = acCommitAdd;
  window.acCancelAdd = acCancelAdd;
  window.acCommitRename = acCommitRename;
  window.acCancelRename = acCancelRename;
  window.acStartRename = acStartRename;

  // 暴露给页面内联脚本调用
  window.AttachCategories = {
    init: init,
    renderZone: renderZone,
    state: getZoneState,
    add: acAdd,
    commitAdd: acCommitAdd,
    cancelAdd: acCancelAdd,
    startRename: acStartRename,
    commitRename: acCommitRename,
    cancelRename: acCancelRename,
    del: acDelete
  };
})();
