// ===== 左侧 sidemenu 动态渲染（v1.2：无 group 标题 + 三级菜单） =====
// 根据当前 page 所属 module 自动渲染左 sidemenu
// - 不显示 group 标题（按用户动图：直接列出二级菜单）
// - 二级有 children 时显示 ▸/▾ 箭头 + 可点击展开
// - 三级菜单缩进灰色
// - 当前 page 所属二级自动展开 + 三级项 active 高亮
// - 手动展开状态记 localStorage（用户记忆）
// 数据：window.TOPNAV_MENU（与 topnav-drawer.js 共用）
// workbench.html 不渲染（首页简洁，按用户决策）

(function () {
  'use strict';

  function getCurrentPage() {
    return (window.location.pathname.split('/').pop() || '').replace(/\.html$/, '');
  }

  function getCurrentModule() {
    const path = getCurrentPage();
    // 菜单最多 4 层（二级 subMenus → 三级 children → 四级 children.children），
    // 递归查找，避免四层页面（如回款详情/编辑回款、保证金明细）匹配不到而渲染空菜单
    function findIn(list) {
      if (!list || !list.length) return null;
      for (const item of list) {
        if (!item) continue;
        if (item.file && item.file.replace(/\.html$/, '') === path) return true;
        if (item.children && findIn(item.children)) return true;
      }
      return null;
    }
    for (const menuKey in window.TOPNAV_MENU) {
      const m = window.TOPNAV_MENU[menuKey];
      if (findIn(m.subMenus)) return menuKey;
    }
    return null;
  }

  // 读取 localStorage 中的展开状态
  function getExpandState(menuKey) {
    try {
      const stored = localStorage.getItem(`sidemenuExpand_${menuKey}`);
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      return {};
    }
  }

  function setExpandState(menuKey, label, isOpen) {
    try {
      const state = getExpandState(menuKey);
      state[label] = isOpen;
      localStorage.setItem(`sidemenuExpand_${menuKey}`, JSON.stringify(state));
    } catch (e) {}
  }

  /** 递归判断某个节点树里是否包含当前页（用于自动展开父级） */
  function containsCurrent(children, currentPath) {
    if (!children || !children.length) return false;
    return children.some(c => {
      if (!c) return false;
      if (c.file && c.file.replace(/\.html$/, '') === currentPath) return true;
      return containsCurrent(c.children, currentPath);
    });
  }

  /**
   * 渲染某个节点的下级列表。
   * 三级项若还有下级（如「回款管理」下的 回款详情 / 回款审批详情 / 编辑回款），
   * 渲染成可展开的嵌套组 —— 否则这层页面在左侧菜单里完全不可达。
   */
  function renderChildItems(children, currentPath, menuKey, isGrand) {
    if (!children || !children.length) return '';
    return children.map(c => {
      if (!c) return '';
      const cFile = c.file.replace(/\.html$/, '');
      const cActive = cFile === currentPath;
      const grand = c.children && c.children.length;
      if (!grand) {
        const cls = isGrand ? 'sidemenu-item sidemenu-child sidemenu-grandchild' : 'sidemenu-item sidemenu-child';
        return `<a href="./${c.file}" class="${cls}${cActive ? ' active' : ''}">${c.label}</a>`;
      }
      const gActive = containsCurrent(c.children, currentPath);
      const expandState = getExpandState(menuKey);
      const userExpanded = expandState[c.label];
      const isOpen = gActive ? true : (userExpanded === undefined ? false : userExpanded);
      const grandHtml = renderChildItems(c.children, currentPath, menuKey, true);
      return `
        <div class="sidemenu-group" data-sub="${c.label}">
          <div class="sidemenu-item sidemenu-parent${gActive ? ' active-parent' : ''}" data-toggle-parent="${c.label}" title="点击展开/收起子菜单">
            <span class="sidemenu-parent-label">${c.label}</span>
            <span class="arrow" data-toggle="${c.label}">${isOpen ? '▾' : '▸'}</span>
          </div>
          <div class="sidemenu-children ${isOpen ? 'show' : ''}">${grandHtml}</div>
        </div>
      `;
    }).join('');
  }

  function renderSubMenuItem(sm, currentPath, menuKey) {
    const smFile = sm.file.replace(/\.html$/, '');
    const isActive = smFile === currentPath;
    const hasChildren = sm.children && sm.children.length > 0;

    if (!hasChildren) {
      // 无 children：保持跳转（sub 本身就是页面）
      return `<a href="./${sm.file}" class="sidemenu-item${isActive ? ' active' : ''}">${sm.label}</a>`;
    }

    // 有 children：父项仅作展开/收起（点击不跳转）
    const childActive = containsCurrent(sm.children, currentPath);
    const expandState = getExpandState(menuKey);
    const userExpanded = expandState[sm.label];
    // 当前 page 在 children 中 → 自动展开；否则用用户记忆
    const isOpen = childActive ? true : (userExpanded === undefined ? false : userExpanded);

    const childrenHtml = renderChildItems(sm.children, currentPath, menuKey, false);

    return `
      <div class="sidemenu-group" data-sub="${sm.label}">
        <div class="sidemenu-item sidemenu-parent${childActive ? ' active-parent' : ''}" data-toggle-parent="${sm.label}" title="点击展开/收起子菜单">
          <span class="sidemenu-parent-label">${sm.label}</span>
          <span class="arrow" data-toggle="${sm.label}">${isOpen ? '▾' : '▸'}</span>
        </div>
        <div class="sidemenu-children ${isOpen ? 'show' : ''}">${childrenHtml}</div>
      </div>
    `;
  }

  function renderLeftSidemenu() {
    const container = document.getElementById('leftSidemenu');
    if (!container) return;
    const currentModule = getCurrentModule();
    if (!currentModule || currentModule === '工作台') {
      container.innerHTML = '';
      container.style.display = 'none';
      return;
    }
    container.style.display = '';
    const menu = window.TOPNAV_MENU[currentModule];
    const currentPath = getCurrentPage();
    // 空 subMenus（风险运营管理暂无可用页面）→ 显示占位
    if (!menu.subMenus || menu.subMenus.length === 0) {
      container.innerHTML = `<div class="sidemenu-empty">暂无可用页面</div>`;
      return;
    }
    const html = menu.subMenus.map(sm => renderSubMenuItem(sm, currentPath, currentModule)).join('');
    container.innerHTML = html;

    // v1.7.99.351：点击子菜单链接时通知父窗口（app.html）联动右侧 doc（不影响 iframe 内 navigate）
    container.addEventListener('click', e => {
      const a = e.target.closest('a.sidemenu-item');
      if (!a) return;
      const rawHref = a.getAttribute('href');
      if (!rawHref || rawHref.startsWith('#')) return;
      // v1.7.99.351.1：去掉 ./ 前缀（避免 app.html allPages.findIndex 不匹配）
      const href = rawHref.replace(/^\.\//, '');
      try {
        if (window.parent && window.parent !== window) {
          window.parent.postMessage({ type: 'PROTOTYPE_NAV', file: href, source: 'sidemenu' }, '*');
        }
      } catch (err) { /* cross-origin silently fail */ }
    });

    // 绑定父项点击事件：v1.7.95 改为"点击整个父项 = 切换展开/收起"，不跳转
    container.querySelectorAll('[data-toggle-parent]').forEach(parentEl => {
      parentEl.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();
        const label = parentEl.dataset.toggleParent;
        const group = parentEl.closest('.sidemenu-group');
        const childrenEl = group.querySelector('.sidemenu-children');
        const arrow = group.querySelector('.arrow');
        const isOpen = childrenEl.classList.contains('show');
        if (isOpen) {
          childrenEl.classList.remove('show');
          if (arrow) arrow.textContent = '▸';
        } else {
          childrenEl.classList.add('show');
          if (arrow) arrow.textContent = '▾';
        }
        setExpandState(currentModule, label, !isOpen);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderLeftSidemenu);
  } else {
    renderLeftSidemenu();
  }
})();
