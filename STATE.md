# 豫港通数字供应链管理平台 — 当前状态快照
最后更新: 2026-10-12 审批管理模块 v1.0.0

## 当前部署
- **apex URL**: https://yugangtong-prototype.pages.dev/ (永远指向最新)
- **最新 hash**: `fb6274c2` (审批管理模块 v1.0.0)
- **CF API Token**: 不入库 —— 从环境变量 `CLOUDFLARE_API_TOKEN` 读取
  （v1.7.99.349.2 修正：此前 STATE.md 明文记录 token，触发 GitHub push protection 拦截）
- **部署命令**: 
  ```
  CLOUDFLARE_API_TOKEN=<token> npx wrangler pages deploy . \
    --project-name=yugangtong-prototype --skip-caching \
    --cwd=$(pwd)
  ```
  （`--cwd` 必须带：父目录 workspace 下有别的项目的 wrangler.toml 含 `[assets]`，
   wrangler 4.x 会向上递归搜到并导致 "Configuration file for Pages projects
   does not support 'assets'"）

## Git
- 仓库: git@github.com:Ummyue/gyt-admin.git
- 最新 commit: `26b3087` (feat(approval): 审批管理模块 + 14 页面接入，已推送)
- 项目级 config: `git -c user.name="Mavis" -c user.email="Mavis@local"`

## 审批管理模块（v1.0.0，2026-10-12 新增）
- **引擎**: `shared/js/approval-engine.js` — 节点类型 start / serial /
  parallel_all / branch；内置 standard / simple / highRisk 三套模板
- **页面映射**: `shared/js/approval-config.js`（`window.APPROVAL_CONFIG_BY_PAGE`）
- **持久化**: `localStorage['ygt_approval_flow_templates_v1']`（同一浏览器内联动）
- **页面**: `pages/approval-flow-list.html`（配置）、`pages/approval-monitor.html`（监控）
- **已接入 14 个业务页**: 合同详情 ×6、付款、退款、追保函详情、客户准入、项目立项、
  货转上/下、仓储放货详情
- **PRD**: `docs/p-approval-flow-list.md`、`docs/p-approval-monitor.md`
- **⚠️ 接入约束（改引擎时必读）**:
  1. 引擎**不得**在 IIFE 执行时快照 `window.APPROVAL_CONFIG_BY_PAGE`，
     必须在 `mount()` 时动态读取（否则 script 顺序会让所有页面回退 standard）
  2. 业务页挂载容器本身带 `class="timeline"` 时，引擎走 bare 渲染不再套第二层
  3. 条件分支必须读 `evalBranch()` 返回的 `res.rules`（含 `matched`），
     不能读 `node.condition`（原始配置无该字段）


## 最近 12 版改动 (v1.7.99.337 ~ 348)
| 版本 | 模块 | 核心改动 |
|---|---|---|
| 337 | margin-pool | 5→6 统计卡 + 已付保证金列 + 登记保证金按钮 + 抽屉初版 |
| 338 | margin-register | section 改名"保证金登记信息" + 合同设定比例 + 本次登记保证金换行 |
| 339 | margin-pool | 抽屉重做（表格+单选+chips+取消/确定+8列）+ MARGIN_MOCK 多元化 |
| 340 | margin-pool | 抽屉过滤"签订日期"→"业务类型"下拉 |
| 341 | register/调整/pool 三页联动 | 等比例冲抵配置统一移至列表页 |
| 342 | register/调整 | 详情/新建页去 checkbox，纯状态徽标回显 |
| 343 | margin-pool | 数据导出按钮下移到表格上方 |
| 344 | receipt-edit | 保证金类型去 checkbox + 货款类型"68,750.00"去重 |
| 345 | margin-pool | **足额硬卡**（方案 B）: paid>=payTotal 才允许开启 |
| 346 | margin-pool | depositRatio 修改策略 B + 变更记录 + toast 提示 |
| 347 | receipt-edit | 字段拆分（应付/实付/冲抵）+ 实时摘要 + 快捷按钮 + 剩余未付 |
| 348 | receipt-edit | 移除"保证金"收款类型，简化 |

## 关键业务公式
**v1.7.99.336 calcOffset**（B 端供应链金融标准）:
```
totalPayable  = cash / (1 - depositRatio/100)
depositOffset = totalPayable × depositRatio / 100
cash (用户输入) = totalPayable × (1 - depositRatio/100)
```
**v1.7.99.345 足额校验**: `paid >= payTotal` 才允许开启 depositEnabled
**v1.7.99.346 修改策略 B**: 允许修改 depositRatio，未来笔按新比例，已完成不回溯，变更记录最多 10 条

## 关键 UX 模式
**v1.7.99.347 字段拆分**: 应付总额(自动) / 现金实付(用户输入) / 保证金冲抵(自动) + 实时摘要 + "按比例分摊"+"全部现金" 2 快捷按钮 + 顶部"剩余未付"提示条 — 可复用到任何应付/实付分裂场景

## 当前未完成任务
**无** — v1.7.99.337~348 全部完成、推送。

## 新 session 启动方式
第一句话: 
> "接豫港通保证金模块 v1.7.99.348 (commit 2b1d8c4)，参考 memory/topics/dhzl-supply-chain.md 第 50 节"

## 校验工具
- `/tmp/ygt-v337.py` ~ `/tmp/ygt-v348.py` Playwright 验证脚本 (各版本独立)
