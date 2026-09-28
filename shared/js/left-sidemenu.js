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
    for (const menuKey in window.TOPNAV_MENU) {
      const m = window.TOPNAV_MENU[menuKey];
      for (const sm of m.subMenus) {
        const smFile = sm.file.replace(/\.html$/, '');
        if (smFile === path) return menuKey;
        if (sm.children) {
          for (const c of sm.children) {
            if (c.file.replace(/\.html$/, '') === path) return menuKey;
          }
        }
      }
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

  function renderSubMenuItem(sm, currentPath, menuKey) {
    const smFile = sm.file.replace(/\.html$/, '');
    const isActive = smFile === currentPath;
    const hasChildren = sm.children && sm.children.length > 0;

    if (!hasChildren) {
      // 无 children：保持跳转（sub 本身就是页面）
      return `<a href="./${sm.file}" class="sidemenu-item${isActive ? ' active' : ''}">${sm.label}</a>`;
    }

    // 有 children：父项仅作展开/收起（点击不跳转）
    const childActiveIdx = sm.children.findIndex(c => c.file.replace(/\.html$/, '') === currentPath);
    const childActive = childActiveIdx >= 0;
    const expandState = getExpandState(menuKey);
    const userExpanded = expandState[sm.label];
    // 当前 page 在 children 中 → 自动展开；否则用用户记忆
    const isOpen = childActive ? true : (userExpanded === undefined ? false : userExpanded);

    const childrenHtml = sm.children.map(c => {
      const cFile = c.file.replace(/\.html$/, '');
      const cActive = cFile === currentPath;
      return `<a href="./${c.file}" class="sidemenu-item sidemenu-child${cActive ? ' active' : ''}">${c.label}</a>`;
    }).join('');

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
      const href = a.getAttribute('href');
      if (!href || href.startsWith('#')) return;
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
