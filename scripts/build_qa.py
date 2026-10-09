#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
待确认清单生成器（QA 问答表格式）

设计原则（2026-10-09 用户反馈驱动）：
    旧版问题 = 7 类正则自动分类 + 6 列表格截断 150 字 + 每类重新编号
               → 用户看不出"到底在问什么"，无法一次性批量答复。
    新版做法 = 按【模块】分组（自然业务序）+ 连续编号 QA-001..QA-426
             + 每条一张问答卡（问题原句不截断 + 背景 + 影响 + 你的答复）

重要：本文件是 99-待确认清单.md 的唯一生成源。
      业务方已补充的答复硬编在 ANSWERS 中，**不会因重新生成而丢失**。

用法:
    python3 scripts/build_qa.py
"""
import json
import os
import re
import collections
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'docs-v2')
OUT = os.path.join(SRC, '99-待确认清单.md')

# ---------------------------------------------------------------- 模块顺序
# 顺序 = 业务人员脑中的系统结构（总纲 → 客户 → 项目 → 合同 → 收发货 → 业务线
#      → 货转 → 盯市 → 追保函 → 保证金 → 预警 → 仓储 → 结算 → 资金 → 发票 → 数据中心）
MODULES = [
    ('00', '00-产品概述与需求总纲.md', '总纲与全局口径'),
    ('02.01', '02.01-项目管理.md', '项目管理（立项）'),
    ('02.02', '02.02-客户管理.md', '客户管理'),
    ('02.03', '02.03-合同管理.md', '合同管理'),
    ('02.05', '02.05-收发货管理.md', '收发货管理'),
    ('02.06', '02.06-业务线管理.md', '业务线管理'),
    ('02.07', '02.07-货转管理.md', '货转管理'),
    ('02.08', '02.08-盯市价格管理.md', '盯市价格管理'),
    ('02.09', '02.09-追保函管理.md', '追保函管理'),
    ('02.10', '02.10-保证金管理.md', '保证金管理'),
    ('02.11', '02.11-预警中心.md', '预警中心'),
    ('02.12', '02.12-仓储管理.md', '仓储管理'),
    ('02.13', '02.13-结算单管理.md', '结算单管理'),
    ('02.14', '02.14-资金管理.md', '资金管理'),
    ('02.15', '02.15-发票管理.md', '发票管理'),
    ('02.16', '02.16-数据中心.md', '数据中心'),
]

# ------------------------------------------------ 业务方已补充的答复（硬编）
# key = (文件名, 条目号)   → { 'ans': 原样保留的答复, 'res': 残留问题 }
ANSWERS = {
    ('00-产品概述与需求总纲.md', 'Q7'): {
        'ans': '合同部分的状态机统一为：全部 / 待提交 / 审批中 / 待上传双签合同 / '
               '执行中 / 已完结 / 审批驳回 / 已作废',
        'res': '底层 `t_contract.status` 的 snake_case 枚举值仍未给（只定了中文名）；'
               '「待盖章 / 已双签」签署状态是挂在 `status` 上还是独立字段也未定。'
               '→ 见 02.03 合同管理 的 QA 编号',
    },
    ('02.01-项目管理.md', 'C1'): {
        'ans': '是业务周期，并且是一个时间范围',
        'res': '字段中文名按「业务周期」落表；另需确认该字段存的是「月数」还是'
               '「起止日期」——业务方口径为「时间范围」，但源文档字段名为 '
               '`project_period_months`（月数），二者不一致。',
    },
    ('02.02-客户管理.md', 'C5'): {
        'ans': '只保留登记逻辑，且等级为：一般 / 中度 / 高度',
        'res': '① 落库仍缺：黑名单状态机有 4 状态（active / lift_pending / lifted / '
               'expired）但表中无 `status` 字段，`lift_pending`（待解除）无落库字段；'
               '② 源文档另有「永久 / 期限 / 观察 / 行业」4 值维度，是否确认**全部作废**？',
    },
    ('02.05-收发货管理.md', 'Q12'): {
        'ans': '收发货管理中的状态机统一为：全部 / 待收货 / 已收货 / 已作废',
        'res': '① 与源文档 §11.4 的「待发货 / 已发货 / 已收货 / 已作废」4 态不一致，'
               '「待发货 / 已发货」2 态是否**取消**？② 4 个状态对应的 snake_case 枚举值仍未给。',
    },
    ('02.06-业务线管理.md', 'C2'): {
        'ans': '业务线状态机统一为：全部 / 执行中 / 采购已完结 / 销售已完结 / 全部完结',
        'res': '① 源文档另有 `finished` / `done` 等写法，是否全部作废？'
               '② 5 个状态的 snake_case 枚举值仍未给。',
    },
    ('02.07-货转管理.md', 'C8'): {
        'ans': '上下游货转的状态机为：全部 / 审批中 / 待上传已生效单据 / 已生效 / '
               '驳回 / 已作废',
        'res': '⚠️ 你答的是**主列表 6 状态**。子页 `goods-transfer-up/down.html` 另有 '
               '**9 状态**（待提交 / 审批中 / 待签约 / 已签约 / 退回 / 已作废 / 待确认 / '
               '已驳回），其中「待签约 / 已签约 / 退回 / 待确认」4 态源文档从未定义、'
               '本次也未覆盖 —— 是否**取消子页 9 状态、统一用这 6 个**？',
    },
    ('02.08-盯市价格管理.md', 'C4'): {
        'ans': '目前项目中的品类为：淀粉制品 / 糖粉 / 谷物',
        'res': '① 与源文档 §1.3 / §6.5 的「玉米 / 糖粉 / 木薯淀粉」不一致：'
               '「谷物」是否即「玉米」、「淀粉制品」是否即「木薯淀粉」？'
               '② 源文档 v1.7.99.33 汇总表还记过「货物品类 4 选项」，第 4 个是什么？',
    },
}

# ---- 已由业务方裁决（D1~D5，2026-10-08）自动关闭的条目 ----
DECIDED = {
    ('00-产品概述与需求总纲.md', 'Q1'): {
        'ans': 'D1 —— **串行审批流**（非 OR 会签），业务方 2026-10-08 已裁决并写入正文',
        'res': '',
    },
    ('00-产品概述与需求总纲.md', 'Q2'): {
        'ans': 'D5 + 你的补充 —— 上下游货转统一为：全部 / 审批中 / 待上传已生效单据 / '
               '已生效 / 驳回 / 已作废（详见 02.07 货转管理 QA）',
        'res': '',
    },
    ('02.01-项目管理.md', 'C3'): {
        'ans': 'D1 —— **串行逐级通过 + 任一节点驳回即终止**（OR 会签表述全项目作废）',
        'res': '⚠️ 遗留：源文档中「OR 会签」表述共 8 处需研发逐份清理，否则文档与实现会打架。',
    },
    ('02.03-合同管理.md', 'C4'): {
        'ans': 'D2 —— 签署状态枚举值已定：**单签 = 待盖章 / 双签 = 已双签**'
               '（已获线上录屏实证，2026-10-08）',
        'res': '⚠️ 遗留：`t_contract` 29 字段中无 `signStatus` 列，落库字段名 / 类型由研发确定。',
    },
    ('02.10-保证金管理.md', 'C11'): {
        'ans': 'D3 —— 保证金调整方式 = **3 种**（冲抵最后一笔货款 / 转移为另一笔业务的保证金 / '
               '保证金退款），飞书手册标题「追加 / 释放 / 转移」的命名作废',
        'res': '',
    },
    ('02.14-资金管理.md', 'C1'): {
        'ans': 'D4 —— 资金链路**系统仅作为登记方**，不涉及真实付款；'
               '「收款方」不是平台业务角色，「已确认」终态删除',
        'res': '⚠️ 遗留：研发核对线上代码中 `已确认` / `confirmed` 是否仍有残留。',
    },
}
ANSWERS = {**DECIDED, **ANSWERS}   # 显式补充优先于已裁决默认

# 问题改写：业务方反馈「看不出问什么」的条目，改成把用途说清楚
REWRITE = {
    ('02.01-项目管理.md', 'Q13'):
        '项目审批流类型 `flow_type` 一共有哪几种取值？'
        '<br/>（现已确认 `oa_sync` = 走致远 A8 OA。该字段决定列表关键指标卡展示'
        '「致远 A8 OA」还是站内消息推送；v1.0 设计的「消息推送」审批模式还没给枚举值，'
        '也没说 v1.0 模式是否还要保留。）',
    ('02.01-项目管理.md', 'C1'):
        '项目周期的字段中文名定哪个？'
        '<br/>（源文档一处写「项目周期（月）」、一处写「业务周期（月）」，两处标签不一致，'
        '表单 label / 导出表头要统一用哪个？）',
    ('02.02-客户管理.md', 'C5'):
        '客户黑名单要保留哪些能力、等级怎么分？'
        '<br/>（源文档出现两套完全不同的等级体系：DB 里是「永久 / 期限 / 观察 / 行业」，'
        '弹窗和列表里是「高度 / 中度 / 一般 / 低度」，需要确认保留哪一套。）',
    ('02.08-盯市价格管理.md', 'C4'):
        '盯市价格监控覆盖哪几个品类？'
        '<br/>（§1 声称监控的品类中有 2 类不在枚举内，需确认最终品类清单。）',
}


# ---------------------------------------------------------------- 抽取
def ans_of(key):
    v = ANSWERS.get(key)
    return v if v else None


def extract():
    """从各模块的「待确认问题」章节抽取全部条目（含完整原文，不截断）。

    列语义一律按【表头列名】映射，不按列序猜 —— 各模块表头并不统一：
        02.01-02.16 : | # | 问题 | 冲突详情 | 影响 | 状态 |   (§7.1)
                     | # | 问题 | 出处   | 归属 |          (§7.2)
        00 总纲     : | # | 问题 | 冲突详情 | 影响 |          (§9.1)
                     | # | 问题 | 归属 |                   (§9.2)
    """
    # 表头列名 → 内部字段
    COLMAP = [
        ('问题', 'q'), ('冲突详情', 'bg'), ('背景', 'bg'), ('详情', 'bg'),
        ('影响', 'impact'), ('归属', 'owner'), ('出处', 'bg'), ('状态', 'state'),
    ]

    def by_header(header, cells):
        out = {}
        for i, h in enumerate(header):
            if i >= len(cells):
                break
            h = re.sub(r'[*`]', '', h).strip()
            for name, field in COLMAP:
                if h.startswith(name) or name in h:
                    out.setdefault(field, cells[i])
                    break
        return out

    items = []
    for key, fn, disp in MODULES:
        p = os.path.join(SRC, fn)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding='utf-8').read()
        # 00 总纲的待确认在 §9，其余模块在 §7
        sec_re = r'\n## 9\.\s' if key == '00' else r'\n## 7\.\s'
        m = re.search(sec_re, txt)
        if not m:
            continue
        sec = txt[m.start():]
        header = None
        for ln in sec.split('\n'):
            s = ln.strip()
            if s.startswith('### '):          # 小节切换 → 表头失效
                header = None
                continue
            if not s.startswith('|'):
                continue
            if re.match(r'^\|[\s:|-]+\|$', s):   # 分隔行 → 上一行即表头
                continue
            cells = [c.strip() for c in s.strip('|').split('|')]
            if cells and re.sub(r'[*`]', '', cells[0]) == '#':
                header = cells
                continue
            if not cells or not header:
                continue
            cid = re.sub(r'[*`]', '', cells[0]).strip()
            if not re.match(r'^(C\d+|Q\d+)$', cid):
                continue
            d = by_header(header, cells)
            if not d.get('q'):
                continue
            if 'owner' not in d:               # 无归属列 → 一律归业务方
                d['owner'] = '业务方'
            items.append({
                'key': key, 'file': fn, 'disp': disp, 'id': cid,
                'q': d.get('q', ''), 'bg': d.get('bg', ''),
                'impact': d.get('impact', ''), 'owner': d.get('owner', ''),
                'state': d.get('state', ''),
            })
    return items


def classify(it):
    """判定优先级：🔴 业务方必答 / 🟡 业务方确认 / ⚪ 研发或文档自决。"""
    own = re.sub(r'[*`]', '', it['owner'] or '')
    # 00 总纲 §9.2 的「归属」列填的是责任模块（如「仓储管理」「全局」）而非人，
    # 只要没点名研发/产品/文档维护，一律视为需业务方回答。
    dev = any(w in own for w in ('研发', '产品', '文档维护'))
    need_biz = '业务方' in own or not dev
    imp = re.sub(r'[*`]', '', it['impact'] or '')
    blocked = it['id'].startswith('C') or '🔴' in imp or '阻塞' in imp
    if need_biz and blocked:
        return 0, '🔴'
    if need_biz:
        return 1, '🟡'
    return 2, '⚪'


def clean(s):
    """压掉多余空白，但保留 markdown 行内标记。"""
    s = re.sub(r'<br\s*/?>', '；', s or '')
    s = re.sub(r'\s*\|\s*', ' | ', s) if ' | ' in s else s
    s = re.sub(r'[ \t　]+', ' ', s).strip()
    return s


# ---------------------------------------------------------------- 生成
def build(items):
    by_mod = collections.OrderedDict()
    for it in items:
        pr, icon = classify(it)
        it['prio'], it['icon'] = pr, icon
        by_mod.setdefault(it['key'], []).append(it)
    for k in by_mod:
        by_mod[k].sort(key=lambda x: (1 if ans_of((x['file'], x['id'])) else 0,
                                      x['prio'], x['id']))

    # 连续编号
    seq, index = 0, {}
    for k, lst in by_mod.items():
        for it in lst:
            seq += 1
            it['qa'] = 'QA-%03d' % seq
            index[(it['file'], it['id'])] = it['qa']

    total = len(items)
    cnt = collections.Counter(it['icon'] for it in items)
    answered = [it for it in items if ans_of((it['file'], it['id']))]
    resid = [it for it in items if ans_of((it['file'], it['id']))
             and ans_of((it['file'], it['id'])).get('res')]

    L = []
    A = L.append
    A('# 待确认问题清单（QA 问答表）')
    A('')
    A('> **文档类型**：PRD Writer 范式 · 交付附件 · 业主回填用')
    A('> **生成日期**：%s' % date.today().isoformat())
    A('> **总量**：%d 条　|　🔴 业务方必答 %d　🟡 业务方确认 %d　⚪ 研发或文档自决 %d'
      % (total, cnt['🔴'], cnt['🟡'], cnt['⚪']))
    A('')
    A('## 📌 怎么答这份清单')
    A('')
    A('1. 全文编号 `QA-001` ~ `QA-%03d` 连续，**回复时请注明编号**，例如「QA-003：是 6 个」。' % total)
    A('2. 每条最后一行是 **`你的答复：______`**，直接写在冒号后面，或在 Word 里另起一段写。')
    A('3. 优先级：')
    A('   - 🔴 **必答** —— 源文档自相矛盾，不裁决无法开发')
    A('   - 🟡 **确认** —— 影响实现细节，可批量答')
    A('   - ⚪ **自决** —— 研发或文档维护层面即可解决，**无需你回答**，列出仅供知悉')
    A('4. 你已补充过的 **%d 条**标 🟢 并原样保留在「你的补充」栏，不需要重复回答；'
      '其中 **%d 条还有残留问题**，已在该条下用 ⚠️ 单独列出。'
      % (len(answered), len(resid)))
    A('')
    A('## 进度总览')
    A('')
    A('| # | 模块 | 🔴 必答 | 🟡 确认 | ⚪ 自决 | 小计 | 你已补充 |')
    A('|---|---|---|---|---|---|---|')
    for idx, (k, lst) in enumerate(by_mod.items(), 1):
        c = collections.Counter(x['icon'] for x in lst)
        a = sum(1 for x in lst if ans_of((x['file'], x['id'])))
        A('| %d | [%s](%s) | %d | %d | %d | %d | %s |'
          % (idx, lst[0]['disp'], './' + lst[0]['file'],
             c['🔴'], c['🟡'], c['⚪'], len(lst), a or '—'))
    A('| | **合计** | **%d** | **%d** | **%d** | **%d** | **%d** |'
      % (cnt['🔴'], cnt['🟡'], cnt['⚪'], total, len(answered)))
    A('')
    A('> **建议回复顺序**：先把 🔴 全部答完（不答无法开工），再一次性过 🟡。')
    A('> ⚪ 部分你可以直接跳过，等研发给出方案后确认即可。')
    A('')
    A('---')
    A('')
    A('## ✅ 已裁决，无需再问（业务负责人 2026-10-08）')
    A('')
    A('| # | 裁决内容 | 影响范围 |')
    A('|---|---|---|')
    for i, (t, s) in enumerate([
        ('立项 / 合同 / 货转审批 = **串行审批流**（非 OR 会签）', '全项目审批引擎'),
        ('合同签署状态 = **单签 / 双签**，界面文案「待盖章 / 已双签」', '02.03 合同（已获线上录屏实证）'),
        ('保证金调整方式 = **3 种**（冲抵最后一笔货款 / 转移为另一笔业务的保证金 / 保证金退款）', '02.10 保证金'),
        ('资金链路 = **系统仅作为登记方**，不涉及真实付款', '02.14 资金（原第一号阻塞已解除）'),
        ('货转上下游 = 上游货权由供应商转核心企业 / 下游由核心企业转客户', '02.07 货转'),
    ], 1):
        A('| D%d | %s | %s |' % (i, t, s))
    A('')

    cn = ('一 二 三 四 五 六 七 八 九 十 十一 十二 十三 十四 十五 十六 '
          '十七 十八 十九 二十').split()
    for idx, (k, lst) in enumerate(by_mod.items(), 1):
        A('---')
        A('')
        A('## 第 %s 部分 · %s（%s）　共 %d 条'
          % (cn[idx - 1], lst[0]['disp'], k, len(lst)))
        A('')
        for it in lst:
            key = (it['file'], it['id'])
            a = ans_of(key)
            q = REWRITE.get(key) or it['q']
            badge = '🟢 已答' if a else it['icon']
            A('**%s** ｜ %s ｜ %s' % (it['qa'], badge, clean(q)))
            A('')
            if it['bg']:
                lab = '背景' if it['id'].startswith('C') else '出处'
                A('- **%s**：%s' % (lab, clean(it['bg'])))
            if it['impact']:
                A('- **影响**：%s' % clean(it['impact']))
            if it['owner']:
                A('- **归属**：%s' % clean(it['owner']))
            if it['state']:
                A('- **文档现状态**：%s' % clean(it['state']))
            if a:
                A('- 🟢 **你的补充**：%s' % a['ans'])
                if a.get('res'):
                    A('- ⚠️ **残留问题**：%s' % a['res'])
            else:
                A('- **你的答复**：')
            A('')
    return '\n'.join(L) + '\n', total


def main():
    items = extract()
    md, total = build(items)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(md)
    print('✅ QA 清单：%d 条 → %s' % (total, OUT))
    # 残留问题索引（便于后续回写正文）
    resid = {}
    for it in items:
        a = ans_of((it['file'], it['id']))
        if a and a.get('res'):
            resid[it['qa']] = a['res']
    with open('/tmp/ygt-qa-residual.json', 'w', encoding='utf-8') as f:
        json.dump(resid, f, ensure_ascii=False, indent=1)
    print('   含残留问题：%d 条 → /tmp/ygt-qa-residual.json' % len(resid))


if __name__ == '__main__':
    main()