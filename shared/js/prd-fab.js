// ===== 浮动"查看 PRD"按钮（v1.7.99.350 新增） =====
// 触发：每个 HTML 页面 body 末尾加载，自动注入右上角浮动按钮
// 行为：点击 → 跳 docs-renderer.html?page=<当前页面>&section=业务定位
// 设计：详情页不加业务变更按钮规则 — PRD 按钮是辅助跳转（类似"复制/附件下载"），允许

(function () {
  'use strict';

  // 当前页面文件名（去掉 .html）
  var fileName = window.location.pathname.split('/').pop() || '';
  var pageName = fileName.replace(/\.html$/i, '');

  // 工具页/非业务页不显示
  var NON_BUSINESS = ['index', 'login', 'app', 'docs-renderer', '_clear-pins', 'changelog'];
  if (NON_BUSINESS.indexOf(pageName) >= 0) return;

  // 映射：HTML 页面名 → 锚点 section（默认"业务定位"）
  // 注意：section 名要跟 docs-renderer 自动生成的 id 一致（marked.slug）
  var SECTION_MAP = {
    // 列表页：默认"业务定位"（或"页面清单"）
    // 详情/新建页：默认"字段规则"
    // 特殊情况：dashboard/cockpit → "业务定位"
    _default: '业务定位',
    _detail: '字段规则'
  };

  // 默认 section：列表页用 _default，其他用 _detail
  var defaultSection = SECTION_MAP._default;
  // 简单判定：含 detail 或 new → 字段规则
  if (pageName.indexOf('detail') >= 0 || pageName.indexOf('-new') >= 0) {
    defaultSection = SECTION_MAP._detail;
  }

  // 创建按钮
  var btn = document.createElement('a');
  btn.href = './docs-renderer.html?page=' + pageName + '#' + defaultSection;
  btn.target = '_blank';
  btn.rel = 'noopener';
  btn.title = '查看本页面需求文档';
  btn.setAttribute('aria-label', '查看本页面需求文档');
  btn.style.cssText = [
    'position: fixed',
    'right: 24px',
    'bottom: 24px',
    'z-index: 9999',
    'display: inline-flex',
    'align-items: center',
    'justify-content: center',
    'gap: 6px',
    'padding: 10px 16px',
    'background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%)',
    'color: #fff',
    'border: none',
    'border-radius: 24px',
    'font-size: 13px',
    'font-weight: 500',
    'box-shadow: 0 4px 12px rgba(124, 58, 237, 0.35)',
    'text-decoration: none',
    'cursor: pointer',
    'transition: all 0.2s ease',
    'font-family: var(--font-family, -apple-system, BlinkMacSystemFont, sans-serif)'
  ].join(';');

  // 鼠标悬停效果
  btn.onmouseenter = function () {
    btn.style.transform = 'translateY(-2px)';
    btn.style.boxShadow = '0 6px 16px rgba(124, 58, 237, 0.5)';
  };
  btn.onmouseleave = function () {
    btn.style.transform = 'translateY(0)';
    btn.style.boxShadow = '0 4px 12px rgba(124, 58, 237, 0.35)';
  };

  // SVG 图标 + 文字
  btn.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
      <line x1="8" y1="7" x2="16" y2="7"/>
      <line x1="8" y1="11" x2="14" y2="11"/>
      <line x1="8" y1="15" x2="12" y2="15"/>
    </svg>
    <span>查看 PRD</span>
  `;

  // 注入到 body
  document.body.appendChild(btn);

  console.log('[prd-fab] 注入"查看 PRD"按钮：' + pageName + ' → docs-renderer.html?page=' + pageName + '#' + defaultSection);
})();