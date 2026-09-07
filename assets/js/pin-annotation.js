/* v1.7.99.262 全局页面标记点（pin annotation）核心逻辑
   数据结构（localStorage 'ygt_pin_data'）：
   {
     password: '3905',         // 简单明文（mock，正式用 hash）
     pins: [
       { id, page, x, y, note, createdAt, updatedAt }
     ]
   }
*/
(function() {
  'use strict';
  var LS_KEY = 'ygt_pin_data';
  var DEFAULT_PWD = '3905';
  var MAX_TRY = 3;
  var LOCK_MIN = 5;

  // ===== Utils fallback（v1.7.99.262.2 修复：pages/*.html 无 window.Utils） =====
  // pin-annotation.js 会被注入到所有 112 个 pages/*.html，但 pages/*.html 本身
  // 不一定有 window.Utils（仅 app.html 顶层有）。如果不兜底，保存/删除 handler
  // 调 Utils.toast 会抛 ReferenceError，closeEditor 不执行 → 编辑器卡住。
  if (!window.Utils) {
    window.Utils = {
      toast: function(msg, type) {
        // 简单 DOM toast：底部弹出 2 秒
        try {
          var t = document.createElement('div');
          t.textContent = msg || '';
          t.style.cssText = 'position:fixed;bottom:60px;left:50%;transform:translateX(-50%);'
            + 'background:rgba(31,41,55,0.92);color:#fff;padding:8px 16px;border-radius:4px;'
            + 'font-size:13px;z-index:99999;box-shadow:0 4px 12px rgba(0,0,0,0.15);'
            + 'pointer-events:none;opacity:0;transition:opacity 0.2s';
          document.body.appendChild(t);
          setTimeout(function() { t.style.opacity = '1'; }, 10);
          setTimeout(function() { t.style.opacity = '0'; setTimeout(function() { t.remove(); }, 200); }, 2000);
        } catch(e) { /* DOM 异常时静默 */ }
        // 同时 console 输出便于调试
        if (window.console) console.log('[pin-toast]', type || 'info', msg);
      }
    };
  }

  // 状态
  var state = {
    authorized: false,
    pinMode: false,
    lockedUntil: 0,
    failCount: 0,
    pins: [],
    currentPage: location.pathname,
    selectedPin: null
  };

  // ===== 持久化 =====
  function loadData() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (!raw) {
        return { password: DEFAULT_PWD, pins: [] };
      }
      var data = JSON.parse(raw);
      if (!data.pins) data.pins = [];
      if (!data.password) data.password = DEFAULT_PWD;
      return data;
    } catch(e) {
      return { password: DEFAULT_PWD, pins: [] };
    }
  }
  function saveData(data) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(data)); } catch(e) {}
  }
  function getPwd() {
    return loadData().password;
  }
  function setPwd(newPwd) {
    var d = loadData();
    d.password = newPwd;
    saveData(d);
    // 顶层 app.html：通知 iframe 同步新密码
    if (!IN_IFRAME) notifyIframe('change-pwd', { newPwd: newPwd });
  }
  function getPins() {
    return loadData().pins;
  }
  function savePins(pins) {
    var d = loadData();
    d.pins = pins;
    saveData(d);
  }

  // ===== 工具 =====
  function genId() {
    return 'pin_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  }
  function nowStr() {
    var d = new Date();
    var p = function(n) { return n < 10 ? '0' + n : '' + n; };
    return d.getFullYear() + '-' + p(d.getMonth()+1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
  }
  function getPageKey() {
    return location.pathname;
  }
  function isLocked() {
    return Date.now() < state.lockedUntil;
  }
  function getLockRemainMin() {
    return Math.ceil((state.lockedUntil - Date.now()) / 60000);
  }

  // ===== iframe 桥接（app.html 用 iframe 加载 pages/*.html 时） =====
  // 顶层 (app.html) 和 iframe 内 (pages/*.html) 共享 pin 模式状态
  var IN_IFRAME = (function() {
    try { return window.parent && window.parent !== window; } catch(e) { return false; }
  })();
  function notifyIframe(action, data) {
    // 顶层 → iframe：通知 pin 模式状态变化
    try {
      var frame = document.getElementById('prototypeFrame');
      if (frame && frame.contentWindow && frame.contentWindow !== window) {
        frame.contentWindow.postMessage({ type: 'pin-bridge', action: action, data: data || {} }, '*');
      }
    } catch(e) { /* 跨域或 iframe 未就绪 */ }
  }
  function bindMessageBridge() {
    if (IN_IFRAME) {
      // ===== iframe 内（pages/*.html）监听父窗口消息 =====
      window.addEventListener('message', function(e) {
        if (!e.data || e.data.type !== 'pin-bridge') return;
        if (e.data.action === 'enter') {
          // 父窗口已验证密码，直接进入 pin 模式（不弹密码弹窗）
          state.authorized = true;
          enterPinMode();
        } else if (e.data.action === 'exit') {
          state.authorized = false;
          exitPinMode();
        } else if (e.data.action === 'change-pwd' && e.data.data && e.data.data.newPwd) {
          setPwd(e.data.data.newPwd);
        }
      });
      // pages/*.html 加载完成后主动询问父窗口当前状态
      if (window.parent) {
        try { window.parent.postMessage({ type: 'pin-bridge', action: 'ready' }, '*'); } catch(e) {}
      }
    } else {
      // ===== 顶层 app.html 监听 iframe 的 ready 消息 =====
      window.addEventListener('message', function(e) {
        if (!e.data || e.data.type !== 'pin-bridge') return;
        if (e.data.action === 'ready') {
          // iframe 加载完成，同步当前 pin 模式状态
          if (state.pinMode) notifyIframe('enter');
        }
      });
    }
  }

  // ===== 密码弹窗 =====
  function showPasswordDialog(mode) {
    // mode: 'unlock' 解锁 | 'change' 修改密码
    if (state.authorized && mode === 'unlock') {
      // 已解锁，直接进入标记模式
      enterPinMode();
      return;
    }
    if (isLocked()) {
      alert('密码输入已被锁定，请 ' + getLockRemainMin() + ' 分钟后重试');
      return;
    }
    var mask = document.createElement('div');
    mask.className = 'pin-password-mask';
    mask.id = 'pinPwdMask';
    var isChange = mode === 'change';
    mask.innerHTML = ''
      + '<div class="pin-password-box">'
      + '  <div class="pin-password-title">'
      + '    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
      + '    ' + (isChange ? '修改标记密码' : '标记功能解锁')
      + '  </div>'
      + '  <div class="pin-password-hint">' + (isChange ? '请输入新密码（4 位数字）：' : '请输入 4 位数字密码（默认 3905）') + '</div>'
      + '  <div class="pin-password-input-row">'
      + '    <input type="password" class="pin-password-input" id="pinPwdInput" maxlength="4" inputmode="numeric" pattern="[0-9]*" placeholder="••••" autocomplete="off">'
      + '  </div>'
      + '  <div class="pin-password-error" id="pinPwdError"></div>'
      + '  <div class="pin-password-actions">'
      + '    <button class="pin-password-btn" id="pinPwdCancel">取消</button>'
      + '    <button class="pin-password-btn primary" id="pinPwdOk">确定</button>'
      + '  </div>'
      + '</div>';
    document.body.appendChild(mask);
    var input = document.getElementById('pinPwdInput');
    var errEl = document.getElementById('pinPwdError');
    input.focus();
    function close() {
      document.body.removeChild(mask);
    }
    function trySubmit() {
      var v = input.value.trim();
      if (!/^\d{4}$/.test(v)) {
        errEl.textContent = '请输入 4 位数字';
        input.classList.add('error');
        setTimeout(function() { input.classList.remove('error'); }, 300);
        return;
      }
      var correctPwd = isChange ? getPwd() : getPwd();
      if (v === correctPwd) {
        if (isChange) {
          var newPwd = prompt('请输入新密码（4 位数字）：', '');
          if (newPwd && /^\d{4}$/.test(newPwd)) {
            setPwd(newPwd);
            alert('密码已修改');
            close();
          } else if (newPwd) {
            alert('新密码必须是 4 位数字');
          }
        } else {
          state.authorized = true;
          state.failCount = 0;
          updateTriggerBtn();
          close();
          enterPinMode();
        }
      } else {
        state.failCount++;
        errEl.textContent = '密码错误（' + (MAX_TRY - state.failCount) + ' 次机会剩余）';
        input.classList.add('error');
        setTimeout(function() { input.classList.remove('error'); }, 300);
        input.select();
        if (state.failCount >= MAX_TRY) {
          state.lockedUntil = Date.now() + LOCK_MIN * 60000;
          close();
          alert('密码错误次数过多，已锁定 ' + LOCK_MIN + ' 分钟');
        }
      }
    }
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') trySubmit();
      else if (e.key === 'Escape') close();
    });
    document.getElementById('pinPwdOk').addEventListener('click', trySubmit);
    document.getElementById('pinPwdCancel').addEventListener('click', close);
    mask.addEventListener('click', function(e) {
      if (e.target === mask) close();
    });
  }

  // ===== 触发按钮更新 =====
  function updateTriggerBtn() {
    var btn = document.getElementById('pinTriggerBtn');
    if (!btn) return;
    if (state.authorized && state.pinMode) {
      btn.classList.add('active');
      btn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M2 12h20"/></svg>退出标记';
    } else if (state.authorized) {
      btn.classList.remove('active');
      btn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>标记（已解锁）';
    } else {
      btn.classList.remove('active');
      btn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>标记';
    }
  }

  // ===== 标记模式 =====
  function enterPinMode() {
    if (!state.authorized) return;
    state.pinMode = true;
    document.body.classList.add('pin-mode-active');
    showBanner();
    updateTriggerBtn();
    // 顶层 app.html：通知 iframe 进入 pin 模式
    if (!IN_IFRAME) notifyIframe('enter');
  }
  function exitPinMode() {
    state.pinMode = false;
    document.body.classList.remove('pin-mode-active');
    hideBanner();
    updateTriggerBtn();
    // 顶层 app.html：通知 iframe 退出 pin 模式
    if (!IN_IFRAME) notifyIframe('exit');
  }
  function showBanner() {
    hideBanner();
    var b = document.createElement('div');
    b.className = 'pin-mode-banner';
    b.id = 'pinModeBanner';
    b.innerHTML = '📌 标记模式已激活 — 点击任意位置标记 <button id="pinExitBtn">退出</button> <button id="pinChangePwdBtn">修改密码</button>';
    document.body.appendChild(b);
    document.getElementById('pinExitBtn').addEventListener('click', exitPinMode);
    document.getElementById('pinChangePwdBtn').addEventListener('click', function() {
      exitPinMode();
      showPasswordDialog('change');
    });
  }
  function hideBanner() {
    var old = document.getElementById('pinModeBanner');
    if (old) document.body.removeChild(old);
  }

  // ===== 点击页面创建 pin =====
  document.addEventListener('click', function(e) {
    if (!state.pinMode) return;
    // 忽略触发按钮、密码框、编辑器、已有 pin 上的点击
    if (e.target.closest('.pin-trigger-btn, .pin-password-mask, .pin-editor, .pin-marker, .pin-tooltip, .pin-mode-banner, .pin-toggle-btn')) {
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    // 转为相对 body 的坐标（fixed 定位用 viewport 坐标）
    var x = e.clientX;
    var y = e.clientY + window.scrollY;
    createPin(x, y);
  }, true);

  function createPin(x, y) {
    var pin = {
      id: genId(),
      page: getPageKey(),
      x: x,
      y: y,
      note: '',
      createdAt: nowStr(),
      updatedAt: nowStr()
    };
    var pins = getPins();
    pins.push(pin);
    savePins(pins);
    state.pins = pins;
    renderPin(pin);
    openEditor(pin);
  }

  // ===== 渲染 pin =====
  function renderPin(pin) {
    if (pin.page !== getPageKey()) return;
    var el = document.createElement('div');
    el.className = 'pin-marker';
    el.id = 'pin_' + pin.id;
    el.style.left = (pin.x - 14) + 'px';  // 28/2 居中
    el.style.top = (pin.y - 28) + 'px';   // 28 是高度，让圆心在 click 点
    var num = state.pins.filter(function(p) { return p.page === getPageKey(); })
                       .findIndex(function(p) { return p.id === pin.id; }) + 1;
    el.innerHTML = '<span>' + num + '</span>';
    el.title = pin.note || '(空)';
    el.addEventListener('click', function(e) {
      e.stopPropagation();
      if (state.pinMode || state.authorized) {
        openEditor(pin);
      } else {
        // 只读模式：显示 tooltip
        showTooltip(el, pin);
      }
    });
    el.addEventListener('mouseenter', function() {
      if (!state.pinMode && !state.authorized && pin.note) {
        showTooltip(el, pin);
      }
    });
    el.addEventListener('mouseleave', hideTooltip);
    document.body.appendChild(el);
  }

  function showTooltip(el, pin) {
    hideTooltip();
    if (!pin.note) return;
    var t = document.createElement('div');
    t.className = 'pin-tooltip show';
    t.id = 'pinTooltip';
    t.textContent = pin.note;
    document.body.appendChild(t);
    var rect = el.getBoundingClientRect();
    var tipRect = t.getBoundingClientRect();
    var left = rect.left + rect.width / 2 - tipRect.width / 2;
    var top = rect.bottom + 8 + window.scrollY;
    if (left < 8) left = 8;
    if (left + tipRect.width > window.innerWidth - 8) left = window.innerWidth - tipRect.width - 8;
    t.style.left = left + 'px';
    t.style.top = top + 'px';
  }
  function hideTooltip() {
    var t = document.getElementById('pinTooltip');
    if (t) document.body.removeChild(t);
  }

  function renderAllPins() {
    // 清除已有
    document.querySelectorAll('.pin-marker').forEach(function(el) { el.remove(); });
    var pins = getPins();
    state.pins = pins;
    pins.filter(function(p) { return p.page === getPageKey(); }).forEach(renderPin);
  }

  // ===== 编辑器 =====
  function openEditor(pin) {
    hideTooltip();
    closeEditor();
    state.selectedPin = pin;
    var mask = document.createElement('div');
    mask.className = 'pin-editor-mask show';
    mask.id = 'pinEditorMask';
    var isNew = !pin.note;
    mask.innerHTML = ''
      + '<div class="pin-editor" onclick="event.stopPropagation()">'
      + '  <div class="pin-editor-header">'
      + '    <div class="pin-editor-title">'
      + '      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
      + '      标记点 #' + (state.pins.filter(function(p) { return p.page === getPageKey(); }).findIndex(function(p) { return p.id === pin.id; }) + 1)
      + '    </div>'
      + '    <button class="pin-editor-close" id="pinEditorClose">'
      + '      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
      + '    </button>'
      + '  </div>'
      + '  <div class="pin-editor-meta">'
      + '    页面: ' + pin.page + '<br>位置: (' + Math.round(pin.x) + ', ' + Math.round(pin.y) + ')<br>创建: ' + pin.createdAt + (pin.updatedAt !== pin.createdAt ? '<br>更新: ' + pin.updatedAt : '')
      + '  </div>'
      + '  <div class="pin-editor-body">'
      + '    <textarea class="pin-editor-textarea" id="pinEditorText" placeholder="请输入标记描述（如：需要修改的字段、未尽事宜、问题点...）">' + (pin.note || '') + '</textarea>'
      + '  </div>'
      + '  <div class="pin-editor-footer">'
      + '    <button class="pin-editor-btn danger" id="pinEditorDelete">删除</button>'
      + '    <button class="pin-editor-btn" id="pinEditorCancel">取消</button>'
      + '    <button class="pin-editor-btn primary" id="pinEditorSave">保存</button>'
      + '  </div>'
      + '</div>';
    document.body.appendChild(mask);
    var text = document.getElementById('pinEditorText');
    text.focus();
    text.setSelectionRange(text.value.length, text.value.length);
    document.getElementById('pinEditorClose').addEventListener('click', closeEditor);
    document.getElementById('pinEditorCancel').addEventListener('click', closeEditor);
    document.getElementById('pinEditorSave').addEventListener('click', function() {
      var note = text.value.trim();
      var pins = getPins();
      var idx = pins.findIndex(function(p) { return p.id === pin.id; });
      if (idx >= 0) {
        pins[idx].note = note;
        pins[idx].updatedAt = nowStr();
        savePins(pins);
        state.pins = pins;
        var el = document.getElementById('pin_' + pin.id);
        if (el) el.title = note || '(空)';
      }
      Utils.toast('标记点已保存', 'success');
      closeEditor();
    });
    document.getElementById('pinEditorDelete').addEventListener('click', function() {
      if (!confirm('确定删除这个标记点？')) return;
      var pins = getPins();
      var idx = pins.findIndex(function(p) { return p.id === pin.id; });
      if (idx >= 0) {
        pins.splice(idx, 1);
        savePins(pins);
        state.pins = pins;
        var el = document.getElementById('pin_' + pin.id);
        if (el) el.remove();
      }
      Utils.toast('标记点已删除', 'success');
      closeEditor();
    });
  }
  function closeEditor() {
    var m = document.getElementById('pinEditorMask');
    if (m) document.body.removeChild(m);
    state.selectedPin = null;
  }

  // ===== 全局开关按钮（右下角访客可隐藏所有 pin） =====
  function ensureToggleBtn() {
    if (document.getElementById('pinToggleBtn')) return;
    var b = document.createElement('button');
    b.className = 'pin-toggle-btn';
    b.id = 'pinToggleBtn';
    b.title = '显示/隐藏所有标记点';
    b.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>';
    var hidden = localStorage.getItem('ygt_pin_hidden') === '1';
    if (hidden) {
      document.body.classList.add('pin-hidden');
      b.classList.add('hidden');
    }
    b.addEventListener('click', function() {
      document.body.classList.toggle('pin-hidden');
      b.classList.toggle('hidden');
      localStorage.setItem('ygt_pin_hidden', document.body.classList.contains('pin-hidden') ? '1' : '0');
    });
    document.body.appendChild(b);
  }

  // ===== 触发按钮创建（仅 app.html 顶部工具栏） =====
  function ensureTriggerBtn() {
    var btn = document.getElementById('pinTriggerBtn');
    if (btn) {
      btn.addEventListener('click', function() {
        if (!state.authorized) {
          showPasswordDialog('unlock');
        } else if (state.pinMode) {
          exitPinMode();
        } else {
          enterPinMode();
        }
      });
      return;
    }
    // 找"窗口化"按钮前面插入
    var target = document.getElementById('btnCenter');
    if (!target) return;
    btn = document.createElement('button');
    btn.className = 'pin-trigger-btn';
    btn.id = 'pinTriggerBtn';
    btn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>标记';
    target.parentNode.insertBefore(btn, target);
    btn.addEventListener('click', function() {
      if (!state.authorized) {
        showPasswordDialog('unlock');
      } else if (state.pinMode) {
        exitPinMode();
      } else {
        enterPinMode();
      }
    });
  }

  // ===== 初始化 =====
  function init() {
    renderAllPins();
    ensureToggleBtn();
    if (document.getElementById('btnCenter')) {
      // 顶层 app.html：创建 trigger 按钮
      ensureTriggerBtn();
      updateTriggerBtn();
      // 顶层 app.html：监听 prototypeFrame iframe 加载，新页面加载完同步 pin 模式
      var frame = document.getElementById('prototypeFrame');
      if (frame) {
        frame.addEventListener('load', function() {
          if (state.pinMode) notifyIframe('enter');
        });
      }
    }
    // 双向桥接（iframe 内监听父窗口消息 + 顶层发消息）
    bindMessageBridge();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
