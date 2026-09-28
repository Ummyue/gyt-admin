// ===== 顶 nav 抽屉组件（v1.2：7 module + 三级菜单 children 字段） =====
// 触发：mouseenter 顶 nav 7 menu → 显示该 menu 的子菜单抽屉
// 关闭：mouseleave menu + drawer 区域（200ms 延迟）
// 数据：window.TOPNAV_MENU（与 left-sidemenu.js 共用）
// 子菜单跳转：a href + 当前 page 高亮
// v1.2 升级（2026-07-27）：
//   - 7 module（去掉"数据中心"）按用户图 1:1
//   - 每个 sub 加 children: [] 字段（三级菜单）
//   - "驾驶舱" 改为"风险运营管理"下的 sub
//   - 抽屉列表同时展示 sub 和 child（child 缩进）

(function () {
  'use strict';

  // ===== 7 menu 数据（按用户图 1:1：子菜单 + 三级菜单） =====
  window.TOPNAV_MENU = {
    '工作台': {
      label: '工作台',
      icon: '🏠',
      subMenus: [
        { label: '工作台', file: 'workbench.html' }
      ]
    },
    '准入管理': {
      label: '准入管理',
      icon: '📋',
      subMenus: [
        { label: '项目准入', file: 'project-list.html' },
        { label: '客户准入', file: 'customer-list.html' },
        { label: '黑名单管理', file: 'blacklist.html' }
      ]
    },
    '数字供应链': {
      label: '数字供应链',
      icon: '📦',
      subMenus: [
        {
          label: '合同管理', file: 'contract-purchase.html',
          children: [
            { label: '采购合同', file: 'contract-purchase.html' },
            { label: '新增采购框架合同', file: 'contract-purchase-new.html' },
            { label: '新增采购订单/单批次合同', file: 'contract-purchase-order-new.html' },
            { label: '销售合同', file: 'contract-sales.html' },
            { label: '新增销售框架合同', file: 'contract-sales-new.html' },
            { label: '新增销售订单/单批次合同', file: 'contract-sales-order-new.html' },
            { label: '补充协议', file: 'contract-supplement.html' },
            { label: '新增补协-框架合同', file: 'contract-supplement-new.html' },
            { label: '新增补协-订单/单批次合同', file: 'contract-supplement-order-new.html' }
          ]
        },
        { label: '业务线管理', file: 'business-line.html' },
        {
          label: '收发货管理', file: 'shipment-out.html',
          children: [
            { label: '发货管理', file: 'shipment-out.html' },
            { label: '收货管理', file: 'shipment-in.html' }
          ]
        },
        { label: '货转管理', file: 'goods-transfer.html' },
        {
          label: '资金管理', file: 'payment-list.html',
          children: [
            { label: '付款管理', file: 'payment-list.html' },
            { label: '退款管理', file: 'refund-list.html' },
            {
              label: '回款管理', file: 'receipt-list.html',
              children: [
                { label: '回款详情', file: 'receipt-detail.html' },
                { label: '编辑回款', file: 'receipt-edit.html' },
              ]
            },
            {
              label: '保证金管理', file: 'margin-pool.html',
              children: [
                { label: '保证金明细', file: 'margin-pool.html' },
                { label: '保证金调整', file: 'margin-adjust.html' },
                { label: '保证金调整记录', file: 'margin-adjust-detail.html' }
              ]
            }
          ]
        },
        {
          label: '结算单管理', file: 'settlement-purchase.html',
          children: [
            { label: '采购结算', file: 'settlement-purchase.html' },
            { label: '销售结算', file: 'settlement-sales.html' }
          ]
        },
        {
          label: '发票管理', file: 'invoice.html',
          children: [
            { label: '进项发票', file: 'invoice.html' },
            { label: '销项发票', file: 'invoice-out.html' }
          ]
        },
        {
          label: '盯市管理', file: 'market-price.html',
          children: [
            { label: '盯市价格管理', file: 'market-price.html' }
          ]
        },
        { label: '追保函管理', file: 'bond-letter.html' }
      ]
    },
    '仓储管理': {
      label: '仓储管理',
      icon: '🏭',
      subMenus: [
        {
          label: '入库管理', file: 'warehouse-inbound.html',
          children: [
            { label: '入库记录', file: 'warehouse-inbound.html' }
          ]
        },
        {
          label: '出库管理', file: 'warehouse-outbound.html',
          children: [
            { label: '出库记录', file: 'warehouse-outbound.html' }
          ]
        },
        {
          label: '提放货管理', file: 'warehouse-pickup.html',
          children: [
            { label: '提货管理', file: 'warehouse-pickup.html' },
            { label: '放货管理', file: 'warehouse-release.html' }
          ]
        },
        {
          label: '库存管理', file: 'warehouse-inventory.html',
          children: [
            { label: '库存台账', file: 'warehouse-inventory.html' }
          ]
        },
        {
          label: '视频监控', file: 'warehouse-video.html',
          children: [
            { label: '库点监控', file: 'warehouse-video.html' }
          ]
        },
        {
          label: '巡库管理', file: 'warehouse-patrol.html',
          children: [
            { label: '巡库记录', file: 'warehouse-patrol.html' }
          ]
        },
        {
          label: '系统管理', file: 'warehouse-system.html',
          children: [
            { label: '库点信息管理', file: 'warehouse-point.html' },
            { label: '仓房管理', file: 'warehouse-warehouse.html' },
            { label: '品类配置', file: 'warehouse-category.html' }
          ]
        }
      ]
    },
    '数据中心': {
      label: '数据中心',
      icon: '📊',
      subMenus: [
        { label: '驾驶舱', file: 'cockpit.html' },
        { label: '项目台账表', file: 'report-project.html' },
        { label: '业务线台账表', file: 'report-bizline.html' },
        { label: '资金占压表', file: 'report-fund.html' },
        { label: '库存明细表', file: 'report-inventory.html' },
        { label: '应收应付表', file: 'report-ar-ap.html' },
        { label: '合规验证报告管理', file: 'report-compliance.html' }
      ]
    },
    '预警中心': {
      label: '预警中心',
      icon: '🔔',
      subMenus: [
        { label: '预警管理', file: 'warning-list.html' },
        { label: '预警规则配置', file: 'warning-config.html' }
      ]
    },
    '账户中心': {
      label: '账户中心',
      icon: '👤',
      subMenus: [
        { label: '个人管理', file: 'account-personal.html' },
        { label: '企业管理', file: 'account-company.html' }
      ]
    }
  };

  // ===== 当前 page → menu/sub 映射（用于高亮抽屉内 active 项） =====
  function getCurrentNav() {
    const path = (window.location.pathname.split('/').pop() || '').replace(/\.html$/, '');
    for (const menuKey in window.TOPNAV_MENU) {
      const m = window.TOPNAV_MENU[menuKey];
      for (const sm of m.subMenus) {
        const smFile = sm.file.replace(/\.html$/, '');
        if (smFile === path) return { menuKey, subLabel: sm.label, subFile: sm.file, childLabel: null };
        if (sm.children) {
          for (const c of sm.children) {
            if (c.file.replace(/\.html$/, '') === path) {
              return { menuKey, subLabel: sm.label, subFile: sm.file, childLabel: c.label, childFile: c.file };
            }
          }
        }
      }
    }
    return null;
  }

  // ===== Drawer 渲染（v1.3：仅显示二级菜单，三级交给左 sidemenu） =====
  // v1.3 简化：抽屉只列 sub，不展开 child
  // 原因：抽屉是快捷入口，三级展开让左 sidemenu 负责（自动展开 + 高亮）
  function renderDrawer(menuKey) {
    const menu = window.TOPNAV_MENU[menuKey];
    if (!menu) return '';
    const current = getCurrentNav();
    const items = menu.subMenus.map(sm => {
      const isActive = current && current.subFile === sm.file;
      const isChildActive = current && current.subLabel === sm.label && current.childLabel;
      const activeClass = isActive ? ' active' : '';
      const parentActive = isChildActive ? ' active-parent' : '';
      return `<a href="./${sm.file}" class="drawer-sub-item${activeClass}${parentActive}">${sm.label}</a>`;
    }).join('');
    return `<div class="drawer-sub-list">${items}</div>`;
  }

  // ===== Drawer 创建（单例） =====
  let drawerEl = null;
  let hideTimer = null;

  function ensureDrawer() {
    if (drawerEl) return drawerEl;
    drawerEl = document.createElement('div');
    drawerEl.id = 'topnavDrawer';
    drawerEl.className = 'topnav-drawer';
    drawerEl.hidden = true;
    document.body.appendChild(drawerEl);
    drawerEl.addEventListener('mouseenter', () => clearTimeout(hideTimer));
    drawerEl.addEventListener('mouseleave', () => scheduleHide());
    // v1.7.99.351：点击抽屉子菜单时通知父窗口（app.html）联动右侧 doc
    drawerEl.addEventListener('click', e => {
      const a = e.target.closest('a.drawer-sub-item');
      if (!a) return;
      const rawHref = a.getAttribute('href');
      if (!rawHref || rawHref.startsWith('#')) return;
      // v1.7.99.351.1：去掉 ./ 前缀（避免 app.html allPages.findIndex 不匹配）
      const file = rawHref.replace(/^\.\//, '');
      // 通知父窗口（app.html）联动右侧 doc（不影响 iframe 内 navigate）
      try {
        if (window.parent && window.parent !== window) {
          window.parent.postMessage({ type: 'PROTOTYPE_NAV', file: file, source: 'topnav' }, '*');
        }
      } catch (err) { /* cross-origin silently fail */ }
    });
    return drawerEl;
  }

  function showDrawer(menuKey, anchorEl) {
    clearTimeout(hideTimer);
    const el = ensureDrawer();
    el.innerHTML = renderDrawer(menuKey);
    const rect = anchorEl.getBoundingClientRect();
    el.style.left = rect.left + 'px';
    el.hidden = false;
  }

  function scheduleHide() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      if (drawerEl) drawerEl.hidden = true;
    }, 200);
  }

  // ===== 初始化（顶 nav 7 menu 绑定 hover） =====
  function init() {
    const topbarMenus = document.querySelectorAll('.topbar-menu-item[data-menu-key]');
    if (topbarMenus.length === 0) return;
    topbarMenus.forEach(item => {
      const menuKey = item.dataset.menuKey;
      if (!window.TOPNAV_MENU[menuKey]) return;
      item.addEventListener('mouseenter', () => showDrawer(menuKey, item));
      item.addEventListener('mouseleave', () => scheduleHide());
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && drawerEl) drawerEl.hidden = true;
    });
    // Debug hook
    const dm = location.search.match(/[?&]_drawer=([^&]+)/);
    if (dm) {
      const key = decodeURIComponent(dm[1]);
      const target = Array.from(topbarMenus).find(m => m.dataset.menuKey === key);
      if (target) setTimeout(() => showDrawer(key, target), 200);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // ===== 全局铃铛通知（v1.7.99.174：所有有 .topbar-right 的页面自动注入） =====
  // 之前 v1.7.99.170 只在 project-list.html 加了铃铛，导致其他页面找不到。
  // 现在把铃铛 + 弹窗 + JS 函数 全部从 project-list.html 提到这里，全站共享。
  function renderNotifBell() {
    if (document.getElementById('notifBell')) return; // 已存在（如有页面手写过）则不重复
    var topbarRight = document.querySelector('.topbar-right');
    if (!topbarRight) return; // 没有 topbar 的页面（如 changelog 独立窗口）不注入

    // 1. 注入 CSS（铃铛 + 弹窗 + 消息项 + 标签 + 元信息 + 底部）
    if (!document.getElementById('notifBellCss')) {
      var css = document.createElement('style');
      css.id = 'notifBellCss';
      css.textContent = ''
        + '.notif-dropdown { position: fixed; top: 60px; right: 80px; width: 400px; max-height: 580px; background: #fff; border: 1px solid var(--border-default); border-radius: 8px; box-shadow: 0 6px 24px rgba(0,0,0,0.12); z-index: 999; display: none; flex-direction: column; overflow: hidden; }'
        + '.notif-dropdown.open { display: flex; }'
        + '.notif-header { padding: 12px 16px; border-bottom: 1px solid var(--border-light); display: flex; align-items: center; justify-content: space-between; }'
        + '.notif-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }'
        + '.notif-tabs { display: flex; padding: 0 16px; border-bottom: 1px solid var(--border-light); background: #fafbfc; }'
        + '.notif-tab { padding: 10px 14px; font-size: 13px; color: var(--text-secondary); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }'
        + '.notif-tab.active { color: var(--color-primary); border-bottom-color: var(--color-primary); font-weight: 500; }'
        + '.notif-tab .num { background: var(--color-danger); color: #fff; font-size: 11px; padding: 0 6px; border-radius: 8px; margin-left: 4px; line-height: 16px; display: inline-block; }'
        + '.notif-list { flex: 1; overflow-y: auto; max-height: 420px; }'
        + '.notif-empty { padding: 60px 20px; text-align: center; color: var(--text-tertiary); font-size: 13px; }'
        + '.notif-item { padding: 12px 16px; border-bottom: 1px solid var(--border-light); cursor: pointer; display: flex; gap: 10px; align-items: flex-start; transition: background 0.15s; }'
        + '.notif-item:hover { background: #f8fafc; }'
        + '.notif-item:last-child { border-bottom: 0; }'
        + '.notif-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-danger); margin-top: 6px; flex-shrink: 0; }'
        + '.notif-item.read .notif-dot { background: transparent; }'
        + '.notif-body { flex: 1; min-width: 0; }'
        + '.notif-row1 { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }'
        + '.notif-row1 .type { font-size: 11px; padding: 1px 6px; border-radius: 3px; flex-shrink: 0; }'
        + '.notif-row1 .type.contract { background: #dbeafe; color: #1e40af; }'
        + '.notif-row1 .type.project { background: #ffedd5; color: #9a3412; }'
        + '.notif-row1 .type.fund { background: #f3e8ff; color: #6b21a8; }'
        + '.notif-row1 .no { font-size: 12px; color: var(--text-tertiary); font-family: "SF Mono", Menlo, monospace; }'
        + '.notif-title2 { font-size: 13px; color: var(--text-primary); font-weight: 500; margin-bottom: 4px; line-height: 1.5; }'
        + '.notif-meta { font-size: 12px; color: var(--text-tertiary); display: flex; gap: 10px; }'
        + '.notif-foot { padding: 10px 16px; border-top: 1px solid var(--border-light); display: flex; align-items: center; justify-content: space-between; background: #fafbfc; }'
        + '.notif-foot a { font-size: 12px; color: var(--color-primary); text-decoration: none; cursor: pointer; }'
        + '.notif-foot a:hover { text-decoration: underline; }';
      document.head.appendChild(css);
    }

    // 2. 注入铃铛 HTML（插入到 .topbar-user 之前）
    var bell = document.createElement('div');
    bell.className = 'topbar-icon-btn';
    bell.id = 'notifBell';
    bell.style.position = 'relative';
    bell.setAttribute('onclick', 'toggleNotifDropdown(event)');
    bell.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg><span class="badge" id="notifBadge">6</span>';
    var user = topbarRight.querySelector('.topbar-user');
    if (user) topbarRight.insertBefore(bell, user);
    else topbarRight.appendChild(bell);

    // 3. 注入弹窗 HTML
    var dd = document.createElement('div');
    dd.className = 'notif-dropdown';
    dd.id = 'notifDropdown';
    dd.innerHTML = ''
      + '<div class="notif-header"><div class="notif-title">🔔 消息通知</div>'
      +   '<a onclick="markAllNotifRead(event)" style="font-size: 12px; color: var(--color-primary); cursor: pointer;">全部标记已读</a></div>'
      + '<div class="notif-tabs">'
      +   '<div class="notif-tab active" data-notif-tab="contract" onclick="switchNotifTab(event, \'contract\')">合同 <span class="num" id="numContract">3</span></div>'
      +   '<div class="notif-tab" data-notif-tab="project" onclick="switchNotifTab(event, \'project\')">项目准入 <span class="num" id="numProject">3</span></div>'
      +   '<div class="notif-tab" data-notif-tab="fund" onclick="switchNotifTab(event, \'fund\')">资金审批 <span class="num" id="numFund">4</span></div>'
      + '</div>'
      + '<div class="notif-list" id="notifList"></div>'
      + '<div class="notif-foot">'
      +   '<a onclick="closeNotifDropdown()">关闭</a>'
      +   '<a onclick="alert(\'查看全部消息（mock）\')">查看全部 →</a>'
      + '</div>';
    document.body.appendChild(dd);

    // 4. 注册全局 NOTIF_MOCK + 函数（只在第一次注入时注册）
    if (!window.NOTIF_MOCK) {
      window.NOTIF_MOCK = {
        contract: [
          { id: 'c1', type: 'contract', no: 'CGHT202607040003', title: '河南中豫港通供应链管理有限公司 → 河南诚泽运输有限公司', submitter: '张爽', time: '5 分钟前', href: './contract-purchase-order-detail.html' },
          { id: 'c2', type: 'contract', no: 'XSDD-2026-001-002', title: '中原粮食集团有限公司 → 河南中豫港通供应链管理有限公司', submitter: '李四', time: '30 分钟前', href: './contract-sales-order-detail.html' },
          { id: 'c3', type: 'contract', no: 'BC-2026-0801-001', title: '河南诚泽运输有限公司 - 补充协议（订单）', submitter: '王五', time: '1 小时前', href: './contract-supplement-order-detail.html' }
        ],
        project: [
          { id: 'p1', type: 'project', no: 'LX-2026-0722-001', title: '木薯淀粉存货类供应链项目 - 上游企业：菏泽德坤煤炭有限公司', submitter: '张爽', time: '10 分钟前', href: './project-detail.html' },
          { id: 'p2', type: 'project', no: 'LX-2026-0805-001', title: '玉米预付业务供应链项目 - 上游企业：山西省金能物资贸易', submitter: '李四', time: '2 小时前', href: './project-detail.html' },
          { id: 'p3', type: 'project', no: 'LX-2026-0810-001', title: '谷物购销业务项目 - 上游企业：山东金岭粮油有限公司', submitter: '王五', time: '昨天 18:32', href: './project-detail.html' }
        ],
        fund: [
          { id: 'f1', type: 'fund', subtype: '付款', no: 'SKJZ202507071619010', title: '河南中豫港通供应链管理有限公司 → 河南诚泽运输有限公司 ¥486,000', submitter: '张爽', time: '8 分钟前', href: './payment-detail.html' },
          { id: 'f2', type: 'fund', subtype: '付款', no: 'SKJZ20250620000022', title: '中原粮食集团有限公司 → 国能河南燃料有限公司 ¥328,500', submitter: '李娜', time: '45 分钟前', href: './payment-detail.html' },
          { id: 'f3', type: 'fund', subtype: '退款', no: 'TK20251219003', title: '天宇豪国际贸易集团有限公司 → 陕西魏煤供应链管理有限公司 ¥123', submitter: '李娜', time: '2 小时前', href: './refund-detail.html' },
          { id: 'f4', type: 'fund', subtype: '退款', no: 'TK20251218001', title: '天宇豪国际贸易集团有限公司 → 陕西魏煤供应链管理有限公司 ¥45,800', submitter: '王强', time: '昨天 16:20', href: './refund-detail.html' }
        ]
      };
    }
    if (!window.toggleNotifDropdown) {
      window.toggleNotifDropdown = function(e) {
        e.stopPropagation();
        var d = document.getElementById('notifDropdown');
        d.classList.toggle('open');
        if (d.classList.contains('open')) window.renderNotifList(window.currentNotifTab || 'contract');
      };
      window.closeNotifDropdown = function() {
        document.getElementById('notifDropdown').classList.remove('open');
      };
      window.currentNotifTab = window.currentNotifTab || 'contract';
      window.switchNotifTab = function(e, key) {
        e.stopPropagation();
        window.currentNotifTab = key;
        document.querySelectorAll('.notif-tab').forEach(function(t) { t.classList.remove('active'); });
        var t = document.querySelector('.notif-tab[data-notif-tab="' + key + '"]');
        if (t) t.classList.add('active');
        window.renderNotifList(key);
      };
      window.renderNotifList = function(key) {
        var list = (window.NOTIF_MOCK || {})[key] || [];
        var html = '';
        if (list.length === 0) {
          html = '<div class="notif-empty">暂无待审批消息 🎉</div>';
        } else {
          html = list.map(function(n) {
            return ''
              + '<div class="notif-item" onclick="notifItemClick(event, \'' + n.href + '\')">'
              +   '<div class="notif-dot"></div>'
              +   '<div class="notif-body">'
              +     '<div class="notif-row1"><span class="type ' + n.type + '">' + (n.type === 'contract' ? '合同' : n.type === 'project' ? '项目准入' : n.subtype || '资金') + '</span><span class="no">' + n.no + '</span></div>'
              +     '<div class="notif-title2">' + n.title + '</div>'
              +     '<div class="notif-meta"><span>👤 ' + n.submitter + '</span><span>🕐 ' + n.time + '</span></div>'
              +   '</div>'
              + '</div>';
          }).join('');
        }
        document.getElementById('notifList').innerHTML = html;
      };
      window.notifItemClick = function(e, href) {
        e.stopPropagation();
        window.location.href = href;
      };
      window.markAllNotifRead = function(e) {
        e.stopPropagation();
        document.querySelectorAll('.notif-item .notif-dot').forEach(function(d) { d.style.background = 'transparent'; });
        var b = document.getElementById('notifBadge');
        if (b) b.style.display = 'none';
      };
      // 点击外部关闭（只注册一次）
      document.addEventListener('click', function(e) {
        var d = document.getElementById('notifDropdown');
        if (!d) return;
        if (d.classList.contains('open') && !d.contains(e.target) && e.target.id !== 'notifBell' && !e.target.closest('#notifBell')) {
          d.classList.remove('open');
        }
      });
    }
  }

  // 启动时检查并注入铃铛
  function initNotif() {
    if (document.querySelector('.topbar-right')) renderNotifBell();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNotif);
  } else {
    initNotif();
  }
})();
