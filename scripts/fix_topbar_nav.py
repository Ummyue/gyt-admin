#!/usr/bin/env python3
"""
批量修复 prototype 顶 nav（v1.7）：
1. 8 menu 顺序按用户图：工作台 / 准入管理 / 数字供应链 / 仓储管理 / 风险运营管理 / 数据中心 / 预警中心 / 账户中心
2. <div> → <a href="..." data-menu-key="...">（hover 抽屉触发）
3. active 状态按文件名 regex 自动判断
4. 在 <body> 之前加 <script src="../shared/js/topnav-drawer.js"></script>

适用：yugangtong-prototype/pages/*.html
"""
import re
import os
import glob

PAGES_DIR = '/Users/fuyu/.mavis/agents/mavis/workspace/yugangtong-prototype/pages'

# 8 个 module 的路由 + 代表页（v1.7：恢复"数据中心"，风险运营管理暂无可用页面）
MODULES = [
    ('工作台',       'workbench',          None),
    ('准入管理',     'project-list',       r'^(project|customer|blacklist)(-|\\.)'),
    ('数字供应链',   'contract-purchase',  r'^(contract|shipment|goods-transfer|payment|refund|collection|margin|settlement|invoice|market-price|bond-letter|business-line)-'),
    ('仓储管理',     'warehouse-inbound',  r'^warehouse-'),
    ('风险运营管理', 'risk-operations',     None),  # v1.7 暂无 sub（sub 搬到了数据中心）
    ('数据中心',     'cockpit',             r'^(cockpit|risk-report|report|risk-compliance)'),  # 驾驶舱 + 业务报表 + 合规验证
    ('预警中心',     'warning-list',       r'^warning-'),
    ('账户中心',     'account-personal',   r'^account-'),
]

# 旧 topbar 菜单（v1.4 / v1.5 / v1.6 7 menu / 8 menu 各种顺序）
OLD_TOPBAR_RES = [
    # v1.7 7 menu 格式（无数据中心）— 数据模型升级前的页面
    re.compile(
        r'<div class="topbar-menu">\s*'
        r'<a class="topbar-menu-item(?P<a1> active)?"\s+href="\./workbench\.html"[^>]*>工作台</a>\s*'
        r'<a class="topbar-menu-item(?P<a2> active)?"\s+href="\./project-list\.html"[^>]*>准入管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a3> active)?"\s+href="\./contract-purchase\.html"[^>]*>数字供应链</a>\s*'
        r'<a class="topbar-menu-item(?P<a4> active)?"\s+href="\./warehouse-inbound\.html"[^>]*>仓储管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a5> active)?"\s+href="\./risk-cockpit\.html"[^>]*>风险运营管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a6> active)?"\s+href="\./warning-list\.html"[^>]*>预警中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a7> active)?"\s+href="[^"]*"[^>]*>账户中心</a>\s*'
        r'</div>',
        re.MULTILINE
    ),
    # v1.5 8 menu 格式（风险运营管理 → 预警中心 → 数据中心 → 账户中心）
    re.compile(
        r'<div class="topbar-menu">\s*'
        r'<a class="topbar-menu-item(?P<a1> active)?"\s+href="\./workbench\.html"[^>]*>工作台</a>\s*'
        r'<a class="topbar-menu-item(?P<a2> active)?"\s+href="\./project-list\.html"[^>]*>准入管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a3> active)?"\s+href="\./contract-purchase\.html"[^>]*>数字供应链</a>\s*'
        r'<a class="topbar-menu-item(?P<a4> active)?"\s+href="\./warehouse-inbound\.html"[^>]*>仓储管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a5> active)?"\s+href="[^"]*"[^>]*>风险运营管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a6> active)?"\s+href="\./warning-list\.html"[^>]*>预警中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a7> active)?"\s+href="\./dashboard\.html"[^>]*>数据中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a8> active)?"\s+href="[^"]*"[^>]*>账户中心</a>\s*'
        r'</div>',
        re.MULTILINE
    ),
    # v1.5 8 menu 格式（风险运营管理 → 数据中心 → 预警中心 → 账户中心）
    re.compile(
        r'<div class="topbar-menu">\s*'
        r'<a class="topbar-menu-item(?P<a1> active)?"\s+href="\./workbench\.html"[^>]*>工作台</a>\s*'
        r'<a class="topbar-menu-item(?P<a2> active)?"\s+href="\./project-list\.html"[^>]*>准入管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a3> active)?"\s+href="\./contract-purchase\.html"[^>]*>数字供应链</a>\s*'
        r'<a class="topbar-menu-item(?P<a4> active)?"\s+href="\./warehouse-inbound\.html"[^>]*>仓储管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a5> active)?"\s+href="[^"]*"[^>]*>风险运营管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a6> active)?"\s+href="\./dashboard\.html"[^>]*>数据中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a7> active)?"\s+href="\./warning-list\.html"[^>]*>预警中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a8> active)?"\s+href="[^"]*"[^>]*>账户中心</a>\s*'
        r'</div>',
        re.MULTILINE
    ),
    # v1.4 旧 <a> 格式（无 data-menu-key）
    re.compile(
        r'<div class="topbar-menu">\s*'
        r'<a class="topbar-menu-item(?P<a1> active)?"\s+href="\./workbench\.html">工作台</a>\s*'
        r'<a class="topbar-menu-item(?P<a2> active)?"\s+href="\./project-list\.html">准入管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a3> active)?"\s+href="\./contract-purchase\.html">数字供应链</a>\s*'
        r'<a class="topbar-menu-item(?P<a4> active)?"\s+href="\./warehouse-inbound\.html">仓储管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a5> active)?"\s+href="#">风险运营管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a6> active)?"\s+href="\./warning-list\.html">预警中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a7> active)?"\s+href="\./dashboard\.html">数据中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a8> active)?"\s+href="#">账户中心</a>\s*'
        r'</div>',
        re.MULTILINE
    ),
    # v1.4 旧 <a> 格式（无 data-menu-key，顺序不同）
    re.compile(
        r'<div class="topbar-menu">\s*'
        r'<a class="topbar-menu-item(?P<a1> active)?"\s+href="\./workbench\.html">工作台</a>\s*'
        r'<a class="topbar-menu-item(?P<a2> active)?"\s+href="\./project-list\.html">准入管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a3> active)?"\s+href="\./contract-purchase\.html">数字供应链</a>\s*'
        r'<a class="topbar-menu-item(?P<a4> active)?"\s+href="\./warehouse-inbound\.html">仓储管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a5> active)?"\s+href="#">风险运营管理</a>\s*'
        r'<a class="topbar-menu-item(?P<a6> active)?"\s+href="\./dashboard\.html">数据中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a7> active)?"\s+href="\./warning-list\.html">预警中心</a>\s*'
        r'<a class="topbar-menu-item(?P<a8> active)?"\s+href="#">账户中心</a>\s*'
        r'</div>',
        re.MULTILINE
    ),
]

# v1.7 已应用 8 menu + changelog 按钮的版本（用于幂等性检查）
NEW_TOPBAR_RE = re.compile(
    r'<div class="topbar-menu">\s*'
    r'(?:<a class="topbar-menu-item(?:\s+active)?"\s+href="[^"]*"\s+data-menu-key="[^"]+">[^<]+</a>\s*){8}'
    r'\s*<button class="topbar-changelog-btn"',
    re.MULTILINE
)


def detect_active_module(filename):
    """根据文件名判断属于哪个 module"""
    for name, rep, pattern in MODULES:
        if name == '工作台' and filename == 'workbench.html':
            return name
        if pattern and re.match(pattern, filename):
            return name
    return None


def build_topbar(active_module):
    """构建新 topbar 菜单 HTML（v1.7：8 menu + data-menu-key + 版本变更记录按钮）"""
    items = []
    for name, rep, _ in MODULES:
        if rep:
            href = f'./{rep}.html'
        else:
            href = '#'  # 占位
        klass = 'topbar-menu-item'
        if active_module and active_module == name:
            klass += ' active'
        items.append(f'      <a class="{klass}" href="{href}" data-menu-key="{name}">{name}</a>')
    # 顶部右侧加"版本变更记录"按钮（window.open 新页签打开 changelog.html）
    items.append('      <button class="topbar-changelog-btn" onclick="window.open(\'./changelog.html\', \'_blank\')" title="查看高保真原型版本变更记录">📋 版本变更记录</button>')
    return '    <div class="topbar-menu">\n' + '\n'.join(items) + '\n    </div>'


DRAWER_SCRIPT = '  <script src="../shared/js/topnav-drawer.js"></script>\n'
LEFT_SCRIPT = '  <script src="../shared/js/left-sidemenu.js"></script>\n'

# 已引用的标记（避免重复插入）
DRAWER_SCRIPT_RE = re.compile(
    r'<script src="(?:\.\./)?shared/js/topnav-drawer\.js"></script>'
)
LEFT_SCRIPT_RE = re.compile(
    r'<script src="(?:\.\./)?shared/js/left-sidemenu\.js"></script>'
)

# 旧 sidemenu 块（v1.5 JS 渲染版：sidemenu 是空容器）
OLD_SIDEMENU_RE = re.compile(
    r'(<div class="sidemenu">)(.*?)(?=<div class="page-header">)',
    re.DOTALL
)
NEW_SIDEMENU = '<div class="sidemenu" id="leftSidemenu"></div>\n\n    <div class="main-content" style="flex: 1; min-width: 0; display: flex; flex-direction: column;">'

# 早期版本：静态 10 group sidemenu（v1.5 之前没跑过的 page）
# 匹配 <div style="display: flex;"> 后到 <div class="page-header"> 前的所有 sidemenu-group
OLD_STATIC_SIDEMENU_RE = re.compile(
    r'(<div style="display: flex;">)\s*(?:<div class="sidemenu-group.*?</div>\s*)+',
    re.DOTALL
)
NEW_STATIC_SIDEMENU = (
    '<div style="display: flex;">\n'
    '    <div class="sidemenu" id="leftSidemenu"></div>\n\n'
    '    <div class="main-content" style="flex: 1; min-width: 0; display: flex; flex-direction: column;">\n'
    '    <div class="page-header">'
)


def process_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # workbench.html 跳过
    if filename == 'workbench.html':
        return False, 'workbench-skip'

    # 幂等性：v1.6 已应用 → 跳过
    if (NEW_TOPBAR_RE.search(content)
        and DRAWER_SCRIPT_RE.search(content)
        and LEFT_SCRIPT_RE.search(content)
        and 'id="leftSidemenu"' in content
        and 'class="main-content"' in content
        and '<!-- /main-content -->' in content):
        return False, 'already-v1.6'

    # 匹配旧 topbar
    matched = False
    active = detect_active_module(filename)
    for old_re in OLD_TOPBAR_RES:
        m = old_re.search(content)
        if m:
            matched = True
            new_topbar = build_topbar(active)
            content = content[:m.start()] + new_topbar + content[m.end():]
            break
    if not matched and not NEW_TOPBAR_RE.search(content):
        return False, 'no-old-topbar-match'

    # 替换旧 sidemenu 块为动态容器
    if not ('id="leftSidemenu"' in content):
        # 先检查是否有早期静态 10 group sidemenu
        static_sm = OLD_STATIC_SIDEMENU_RE.search(content)
        if static_sm:
            content = content[:static_sm.start()] + NEW_STATIC_SIDEMENU + content[static_sm.end():]
            if '<!-- /main-content -->' not in content:
                content = content.replace('</body>', '  </div>\n  <!-- /main-content -->\n</body>', 1)
        else:
            sm = OLD_SIDEMENU_RE.search(content)
            if sm:
                content = content[:sm.start()] + NEW_SIDEMENU + content[sm.end():]
                if '<!-- /main-content -->' not in content:
                    content = content.replace('</body>', '  </div>\n  <!-- /main-content -->\n</body>', 1)
            else:
                return False, 'no-sidemenu'
    else:
        if 'class="main-content"' not in content and '<!-- /main-content -->' not in content:
            sm_end_re = re.compile(r'<div class="sidemenu" id="leftSidemenu"></div>\s*')
            m2 = sm_end_re.search(content)
            if m2:
                insert_pos = m2.end()
                content = (
                    content[:insert_pos]
                    + '<div class="main-content" style="flex: 1; min-width: 0; display: flex; flex-direction: column;">'
                    + content[insert_pos:]
                )
                if '<!-- /main-content -->' not in content:
                    content = content.replace('</body>', '  </div>\n  <!-- /main-content -->\n</body>', 1)

    # 在 </body> 之前插入 drawer.js + left-sidemenu.js
    if not DRAWER_SCRIPT_RE.search(content):
        content = content.replace('</body>', DRAWER_SCRIPT + '</body>', 1)
    if not LEFT_SCRIPT_RE.search(content):
        content = content.replace('</body>', LEFT_SCRIPT + '</body>', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True, active or 'no-active'


def main():
    files = sorted(glob.glob(os.path.join(PAGES_DIR, '*.html')))
    print(f'Processing {len(files)} files...')
    success = 0
    skipped = 0
    failed = []
    for f in files:
        ok, info = process_file(f)
        if ok:
            success += 1
        elif info == 'already-v1.6' or info == 'workbench-skip':
            skipped += 1
        else:
            failed.append((f, info))
    print(f'✓ {success} updated, {skipped} skipped (already v1.6), {len(failed)} failed')
    for f, info in failed:
        print(f'  ✗ {os.path.basename(f)}: {info}')


if __name__ == '__main__':
    main()
