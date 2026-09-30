/**
 * Global Utils（v1.7.99.158 补建）
 * 提供 toast / nav / filterChips 等工具函数，供各页面调用
 */
(function(global) {
  const Utils = {
    toast: function(msg, type) {
      // 简化版 toast：创建/复用 .utils-toast div
      let toast = document.querySelector('.utils-toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.className = 'utils-toast';
        toast.style.cssText = 'position: fixed; top: 80px; left: 50%; transform: translateX(-50%); padding: 10px 20px; background: rgba(15, 23, 42, 0.92); color: #fff; border-radius: 6px; font-size: 13px; z-index: 99999; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: opacity 0.3s;';
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      toast.style.opacity = '1';
      clearTimeout(toast._timer);
      toast._timer = setTimeout(function() { toast.style.opacity = '0'; }, 2000);
    },
    nav: function(path) {
      window.location.href = path;
    },
    filterChips: {
      init: function() {}
    }
  };
  global.Utils = Utils;
})(window);
