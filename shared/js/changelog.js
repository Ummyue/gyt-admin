// ===== 版本变更记录（v2） =====
// 入口：高保真顶部"版本变更记录"按钮 → window.open('../pages/changelog.html')
// 存储：localStorage（key = ygt_changelog_v1）
// 数据结构：
//   ts        = 时间戳（ISO 字符串）
//   version   = 版本号（如 v1.7.99.168）
//   module    = 功能模块归属（如「业务线管理」/「货转管理」/「合同管理」）
//   summary   = 文字总结（一句话）
//   changes   = 结构化新旧改动列表 [ { type, location, before, after } ]
//     type     = 'add' | 'remove' | 'modify'
//     location = 改动位置
//     before   = 改动前（null 表示新增）
//     after    = 改动后（null 表示删除）
//   prevSnapshot = 变更前截图（dataURL 或 URL，可选）
//   newSnapshot  = 变更后截图（dataURL 或 URL，可选）
//   rules    = 文字变更规则描述（兼容旧版，等价于 summary）
//
// 用法：
//   window.YGTChangelog.add({
//     version: 'v1.7.99.168',
//     module: '业务线管理',
//     summary: '...',
//     changes: [
//       { type: 'remove', location: '状态 tab 栏', before: '已终止 tab', after: null }
//     ]
//   })

(function () {
  'use strict';

  const STORAGE_KEY = 'ygt_changelog_v1';

  function loadAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveAll(list) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (e) {
      console.error('changelog save failed:', e);
    }
  }

  // 公开 API：添加一条变更记录
  window.YGTChangelog = {
    add: function (entry) {
      const list = loadAll();
      list.unshift(Object.assign({
        ts: new Date().toISOString(),
        version: 'v1.7.99.0',
        module: '未指定模块',
        summary: '',
        changes: []
      }, entry || {}));
      saveAll(list);
      return list.length;
    },
    list: loadAll,
    clear: function () {
      localStorage.removeItem(STORAGE_KEY);
    },
    STORAGE_KEY: STORAGE_KEY
  };
})();
