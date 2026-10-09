#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA 清单可填写层注入器。

背景（2026-10-09 用户反馈）：
    交付的 99-待确认清单.html 是**静态导出产物**，业主在浏览器里改动刷新即丢，
    也不知道怎么把答案回传给开发。这里给 99 页注入一层原生 JS 填写能力：

    · 每张问答卡下方插入 textarea，可直接作答
    · 边填边存 localStorage（同源长期有效，换设备/重部署不丢）
    · 顶部工具条：填写进度 / 仅看待答 / 复制全部答复 / 下载 Markdown / 清空
    · 「复制全部答复」产出 `QA-012：xxx` 形式的 Markdown，直接粘回对话即可回写正文

约束：零 CDN、零框架、零构建 —— 离线双击打开也能用。
用法：python3 scripts/inject_qa_form.py --out <导出目录>
"""
import argparse
import html
import os
import re

QA_PAGE = '99-待确认清单.html'
STORE_KEY = 'ygt-qa-answers-v2'

CSS = """
<style id="qaform">
.qabar{position:sticky;top:0;z-index:40;margin:0 0 22px;padding:12px 14px;
 background:#fff;border:1px solid #E5E7EB;border-left:4px solid #1D4ED8;
 border-radius:8px;box-shadow:0 2px 10px rgba(15,23,42,.06);
 display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:13px}
.qabar b{font-size:15px}
.qabar .sp{flex:1}
.qabtn{border:1px solid #D1D5DB;background:#fff;color:#1F2937;border-radius:6px;
 padding:6px 12px;cursor:pointer;font:inherit;line-height:1.4}
.qabtn:hover{background:#F3F4F6;border-color:#9CA3AF}
.qabtn.pri{background:#1D4ED8;border-color:#1D4ED8;color:#fff}
.qabtn.pri:hover{background:#1e40af}
.qabtn.on{background:#FEF3C7;border-color:#F59E0B}
.qaprog{color:#6B7280}
.qaprog em{font-style:normal;color:#1D4ED8;font-weight:700;font-size:15px}
.qabar .hint{color:#9CA3AF;font-size:12px}
.qacard{position:relative;padding-left:10px;border-left:3px solid #E5E7EB;margin:0 0 6px}
.qacard.answered{border-left-color:#16A34A;background:#F0FDF4}
.qacard.p0{border-left-color:#DC2626}
.qap{font-weight:700;font-size:14.5px;line-height:1.65;margin:14px 0 6px;color:#111827}
.qameta{margin:0 0 4px;font-size:12.5px;color:#4B5563}
.qameta li{margin:2px 0}
.qata{width:100%;box-sizing:border-box;font:inherit;font-size:13.5px;line-height:1.6;
 padding:9px 11px;border:1px dashed #CBD5E1;border-radius:6px;background:#F8FAFC;
 resize:vertical;min-height:42px;color:#111827}
.qata:focus{outline:none;border-color:#1D4ED8;border-style:solid;background:#fff}
.qata::placeholder{color:#B0B7C3}
.qasaved{font-size:11.5px;color:#16A34A;margin-left:6px;opacity:0;transition:opacity .25s}
.qasaved.show{opacity:1}
body.qahide .qacard.answered{display:none}
body.qahideonly .qacard:not(.filled){display:none}
.qatotop{position:fixed;right:22px;bottom:22px;width:42px;height:42px;border-radius:50%;
 border:none;background:#1D4ED8;color:#fff;font-size:19px;cursor:pointer;display:none;
 box-shadow:0 4px 14px rgba(29,78,216,.4);z-index:50}
.qatotop.show{display:block}
</style>
"""

JS = """
<script id="qaform-js">
(function(){
  var KEY = '%s';
  var store = {};
  try { store = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e) { store = {}; }

  var cards = [].slice.call(document.querySelectorAll('p.qap'));
  var save = function(id, v){
    if (v && v.trim()) store[id] = v; else delete store[id];
    try { localStorage.setItem(KEY, JSON.stringify(store)); } catch(e) {}
  };
  var count = function(){ return Object.keys(store).length; };

  // ---- 工具条 ----
  var bar = document.createElement('div');
  bar.className = 'qabar';
  bar.innerHTML =
    '<b>答复填写区</b>' +
    '<span class="qaprog">已填 <em id="qaN">0</em> / %d 条</span>' +
    '<button class="qabtn" id="qaToggle">仅看待答</button>' +
    '<span class="sp"></span>' +
    '<button class="qabtn pri" id="qaCopy">复制全部答复</button>' +
    '<button class="qabtn" id="qaDl">下载 Markdown</button>' +
    '<button class="qabtn" id="qaClr">清空</button>' +
    '<span class="hint">答案自动存在本浏览器，换设备请用「复制/下载」带走</span>';
  var main = document.querySelector('main');
  main.insertBefore(bar, main.firstChild);

  // ---- 逐条注入 ----
  var qs = function(el, sel){ var m = el.nextElementSibling;
    while (m && !(m.tagName === 'UL' && m.classList.contains('qameta'))) m = m.nextElementSibling;
    return m; };

  cards.forEach(function(p){
    var id = p.getAttribute('data-qid');
    var badge = p.getAttribute('data-badge') || '';
    var done = p.getAttribute('data-answered') === '1';
    p.classList.add('qacard');
    if (done) p.classList.add('answered');
    if (badge.indexOf('🔴') === 0) p.classList.add('p0');

    var meta = qs(p);
    if (done) return;                       // 已裁决的条目不再给输入框
    var ta = document.createElement('textarea');
    ta.className = 'qata'; ta.dataset.qid = id; ta.rows = 1;
    ta.placeholder = badge.indexOf('🔴') === 0 ? '🔴 必答 —— 请在此填写你的裁决…'
                  : badge.indexOf('🟡') === 0 ? '🟡 请在此填写…' : '⚪ 研发自决，留空即可';
    ta.value = store[id] || '';
    var wrap = document.createElement('div');
    wrap.className = 'qawrap';
    wrap.style.margin = '2px 0 16px 10px';
    wrap.appendChild(ta);
    var ok = document.createElement('span');
    ok.className = 'qasaved'; ok.textContent = '已保存';
    wrap.appendChild(ok);
    meta.parentNode.insertBefore(wrap, meta.nextSibling);

    var autosize = function(){ ta.style.height = 'auto';
      ta.style.height = Math.max(42, ta.scrollHeight + 2) + 'px'; };
    autosize();
    var t = null;
    ta.addEventListener('input', function(){
      autosize();
      clearTimeout(t);
      t = setTimeout(function(){
        save(id, ta.value);
        p.classList.toggle('filled', !!ta.value.trim());
        document.getElementById('qaN').textContent = count();
        ok.classList.add('show'); setTimeout(function(){ ok.classList.remove('show'); }, 900);
      }, 350);
    });
    p.classList.toggle('filled', !!ta.value.trim());
  });
  document.getElementById('qaN').textContent = count();

  // ---- 工具条行为 ----
  var build = function(){
    var out = ['# 豫港通需求规格说明书 · 待确认问题答复',
               '', '> 由业主在离线 HTML 填写页回填，生成时间 ' + new Date().toLocaleString('zh-CN'), ''];
    [].slice.call(document.querySelectorAll('textarea.qata')).forEach(function(ta){
      var v = ta.value.trim(); if (!v) return;
      var p = ta.closest('.qacard');
      out.push('**' + ta.dataset.qid + '** ' + p.getAttribute('data-badge').replace(/^[^\\s]+\\s*/, '') +
               '　' + p.getAttribute('data-question').trim());
      out.push('');
      out.push('> ' + v.replace(/\\n/g, '\\n> '));
      out.push('');
    });
    if (out.length <= 5) out.push('（尚未填写任何答复）');
    return out.join('\\n');
  };
  document.getElementById('qaCopy').onclick = function(){
    var t = build(), btn = this;
    var done = function(){ btn.textContent = '已复制 ✓';
      setTimeout(function(){ btn.textContent = '复制全部答复'; }, 1600); };
    if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function(){ fallback(t); done(); });
    else fallback(t);
    function fallback(t){
      var ta = document.createElement('textarea');
      ta.value = t; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch(e) {}
      document.body.removeChild(ta);
    }
  };
  document.getElementById('qaDl').onclick = function(){
    var b = new Blob([build()], {type:'text/markdown;charset=utf-8'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(b);
    a.download = '待确认答复-豫港通.md'; a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); }, 3000);
  };
  document.getElementById('qaClr').onclick = function(){
    if (!confirm('确定清空本浏览器已填写的全部答复？此操作不可撤销。')) return;
    store = {}; try { localStorage.removeItem(KEY); } catch(e) {}
    location.reload();
  };
  var tg = document.getElementById('qaToggle');
  tg.onclick = function(){
    document.body.classList.toggle('qahideonly');
    tg.classList.toggle('on', document.body.classList.contains('qahideonly'));
  };
  var top = document.createElement('button');
  top.className = 'qatotop'; top.textContent = '↑'; top.title = '回到顶部';
  top.onclick = function(){ window.scrollTo({top:0, behavior:'smooth'}); };
  document.body.appendChild(top);
  window.addEventListener('scroll', function(){
    top.classList.toggle('show', window.scrollY > 600);
  });
})();
</script>
""" % (STORE_KEY, 0)   # 占位，总数在注入时替换


CARD_RE = re.compile(
    r'<p><strong>(QA-\d+)</strong>\s*｜\s*([^｜]+?)｜\s*(.*?)</p>\s*'
    r'<ul>(.*?)</ul>', re.S)


def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def inject(path):
    src = open(path, encoding='utf-8').read()
    total = [0]

    def repl(m):
        qid, badge, question, inner = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
        total[0] += 1
        answered = '🟢' in badge
        # 把卡片首行改成带 data 属性的标题；meta 列表加 class 供脚本定位
        new_head = ('<p class="qap" data-qid="%s" data-badge="%s" data-question="%s">'
                    '<strong>%s</strong> ｜ %s ｜ %s</p>'
                    % (qid, html.escape(badge, quote=True),
                       html.escape(strip_tags(question), quote=True),
                       qid, html.escape(badge), question))
        # 未答条目：移除静态的「你的答复：」空行（改用 textarea）
        inner2 = re.sub(r'<li><strong>你的答复</strong>：</li>', '', inner)
        return '%s <ul class="qameta">%s</ul>' % (new_head, inner2)

    body, n = CARD_RE.subn(repl, src)
    if n == 0:
        print('  ⚠️ 未匹配到任何 QA 卡片，填写层未注入')
        return path

    js = JS.replace("'%s'" % STORE_KEY, "'%s'" % STORE_KEY, 1)
    js = js.replace('<em id="qaN">0</em> / %d 条' % 0,
                    '<em id="qaN">0</em> / %d 条' % n)
    body = body.replace('</head>', CSS + '</head>', 1)
    body = body.replace('</body>', js + '</body>', 1)
    open(path, 'w', encoding='utf-8').write(body)
    print('✅ 填写层已注入：%s（%d 张卡片）' % (os.path.basename(path), n))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '..', 'docs-v2-export'))
    a = ap.parse_args()
    p = os.path.join(os.path.abspath(a.out), QA_PAGE)
    if not os.path.exists(p):
        print('❌ 找不到 %s，请先跑 export_docs.py' % p)
        return
    inject(p)


if __name__ == '__main__':
    main()