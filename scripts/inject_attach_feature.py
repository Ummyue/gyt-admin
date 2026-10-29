#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附件分类增强 · 批量注入器。

背景（2026-10-29 用户需求）：
    「客户准入材料上传」在 pages/project-apply.html 上做了两件事：
      1. 每个材料类别行新增「上传无此附件说明」入口
      2. 附件区下方追加「自定义附件」分区（新增 / 改名 / 删除条目）
    并要求「上传的附件需要回显其文件名称」。
    用户要求把同一套交互铺到截图列出的 12 个模块的附件区。

做法：
    把交互抽成 shared/js/attach-categories.js（零依赖、零构建），
    本脚本按「每个页面一份定位配置」往目标页面注入：
      <script>window.__ATTACH_ZONES__ = [...];</script>
      <script src="../shared/js/attach-categories.js"></script>

    注入点在 </body> 前；定位用纯 CSS 选择器，组件运行时解析。

用法：
    python3 scripts/inject_attach_feature.py            # 注入
    python3 scripts/inject_attach_feature.py --check    # 只体检不写
    python3 scripts/inject_attach_feature.py --revert   # 回滚（移除注入块）
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, 'pages')

MARK_BEGIN = '<!-- ==== attach-categories 注入开始 (v1.22.0) ==== -->'
MARK_END = '<!-- ==== attach-categories 注入结束 ==== -->'
SCRIPT_REF = '<script src="../shared/js/attach-categories.js"></script>'

# --------------------------------------------------------------------------
# 每个模块的落地页面 + 附件区定位
#   zone —— 附件区容器（自定义附件分区追加到它之后）
#   row  —— 容器内的「材料类别行」
# --------------------------------------------------------------------------
TARGETS = [
    # ---- 客户准入（v1.22.0 新建材料上传区块，类别行由页面静态给出） ----
    {'module': '客户准入-附件', 'file': 'customer-apply.html',
     'zone': '#custMaterialsList', 'row': '.cm-mat-row'},
    # ---- 收发货 ----
    {'module': '收发货-附件', 'file': 'shipment-out-new.html',
     'titleSel': '.info-section-title', 'titleText': '附件', 'zoneSel': '.info-section-body',
     'row': '.attach-row'},
    # ---- 货转 ----
    {'module': '货转-附件', 'file': 'goods-transfer-up-new.html',
     'titleSel': 'h3.info-section-title', 'titleText': '附件', 'zoneSel': '.info-section-body',
     'row': '.attach-row'},
    {'module': '货转-附件', 'file': 'goods-transfer-down-new.html',
     'titleSel': 'h3.info-section-title', 'titleText': '附件', 'zoneSel': '.info-section-body',
     'row': '.attach-row'},
    # ---- 付款 ----
    {'module': '付款-附件', 'file': 'payment-detail.html',
     'titleSel': 'h3.info-section-title', 'titleText': '附件', 'zoneSel': '.info-section-body',
     'row': 'tbody > tr'},
    # ---- 退款 ----
    {'module': '退款-附件', 'file': 'refund-detail.html',
     'titleSel': 'h3.info-section-title', 'titleText': '附件', 'zoneSel': '.info-section-body',
     'row': 'tbody > tr'},
    # ---- 保证金 ----
    {'module': '保证金-附件', 'file': 'margin-register.html',
     'zone': '.info-section-body:has(table.attach-table)', 'row': 'tbody > tr'},
    {'module': '保证金-附件', 'file': 'margin-adjust.html',
     'zone': '.info-section-body:has(table.attach-table)', 'row': 'tbody > tr'},
    # ---- 采购 / 销售结算单 ----
    {'module': '采购/销售结算单-附件', 'file': 'settlement-purchase-new.html',
     'zone': '.info-section-body:has(table.attach-table)', 'row': 'tbody > tr'},
    {'module': '采购/销售结算单-附件', 'file': 'settlement-sales-new.html',
     'zone': '.info-section-body:has(table.attach-table)', 'row': 'tbody > tr'},
    # ---- 追保函 ----
    {'module': '追保函-附件', 'file': 'bond-letter-new.html',
     'titleSel': '.bl-form-card-title', 'titleText': '附件', 'zoneSel': '.bl-form-card-body',
     'row': '.bl-uploaded-row'},
    {'module': '追保函-附件', 'file': 'bond-letter-detail.html',
     'zone': '.block:has(table.attach-table)', 'row': 'tbody > tr'},
    # ---- 出入库 ----
    {'module': '出入库-附件', 'file': 'warehouse-inbound-new.html',
     'zone': '.form-section-body:has(table.attach-table)', 'row': 'tbody > tr'},
    {'module': '出入库-附件', 'file': 'warehouse-outbound-new.html',
     'zone': '.form-section-body:has(table.attach-table)', 'row': 'tbody > tr'},
    {'module': '出入库-附件', 'file': 'warehouse-inbound-detail.html',
     'zone': '.card-body:has(table.attach-table)', 'row': 'tbody > tr'},
    # ---- 提放货 ----
    {'module': '提放货-附件', 'file': 'warehouse-release-new.html',
     'zone': '.form-section-body:has(table.attach-table)', 'row': 'tbody > tr'},
]


def build_block(cfg):
    """生成注入块。定位方式三选一：titleSel+titleText+zoneSel / zone / 自动识别。"""
    zone = {}
    if cfg.get('titleSel'):
        zone['titleSel'] = cfg['titleSel']
        zone['titleText'] = cfg['titleText']
        zone['zoneSel'] = cfg['zoneSel']
    else:
        zone['zone'] = cfg['zone']
    zone['row'] = cfg['row']
    zones = [zone]
    import json
    js = json.dumps(zones, ensure_ascii=False)
    return (
        '\n  ' + MARK_BEGIN + '\n'
        '  <script>window.__ATTACH_ZONES__ = window.__ATTACH_ZONES__ || [];\n'
        '  window.__ATTACH_ZONES__.push.apply(window.__ATTACH_ZONES__, ' + js + ');</script>\n'
        '  ' + SCRIPT_REF + '\n'
        '  ' + MARK_END + '\n'
    )


def inject(path, cfg):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    orig = html
    # 先清掉旧注入块
    html = re.sub(r'\n\s*' + re.escape(MARK_BEGIN) + r'.*?' + re.escape(MARK_END) + r'\n',
                   '\n', html, flags=re.S)
    block = build_block(cfg)
    if '</body>' in html:
        html = html.replace('</body>', block + '</body>', 1)
    else:
        html += block
    if html != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def revert(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    new = re.sub(r'\n\s*' + re.escape(MARK_BEGIN) + r'.*?' + re.escape(MARK_END) + r'\n',
                 '\n', html, flags=re.S)
    if new != html:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='只体检不写')
    ap.add_argument('--revert', action='store_true', help='回滚注入')
    args = ap.parse_args()

    missing = []
    changed = []
    for cfg in TARGETS:
        p = os.path.join(PAGES_DIR, cfg['file'])
        if not os.path.exists(p):
            missing.append(cfg['file'])
            continue
        if args.revert:
            if revert(p):
                changed.append(cfg['file'])
        elif args.check:
            with open(p, encoding='utf-8') as f:
                h = f.read()
            ok = MARK_BEGIN in h
            print('  %-38s %-22s %s' % (cfg['file'], cfg['module'], '已注入' if ok else '未注入'))
        else:
            if inject(p, cfg):
                changed.append(cfg['file'])
                print('  ✓ 注入 %s（%s）' % (cfg['file'], cfg['module']))
            else:
                print('  · 无变化 %s' % cfg['file'])

    if missing:
        print('\n⚠️ 文件不存在: %s' % ', '.join(missing), file=sys.stderr)
    if changed and not args.check:
        print('\n共改动 %d 个页面' % len(changed))
    return 0


if __name__ == '__main__':
    sys.exit(main())
