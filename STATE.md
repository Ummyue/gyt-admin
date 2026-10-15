# 豫港通数字供应链管理平台 — 当前状态快照
最后更新: 2026-10-15 审批管理模块 v1.1.0

## 当前部署
- **apex URL**: https://yugangtong-prototype.pages.dev/ (永远指向最新)
- **最新 hash**: `c39dfd7b` (审批管理模块 v1.1.0)
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
- 最新 commit: `154480b` (refactor(approval): 审批模块 v1.1.0 独立编排画布，已推送)
- 项目级 config: `git -c user.name="Mavis" -c user.email="Mavis@local"`

## 审批管理模块（v1.1.0，2026-10-15）
- **引擎**: `shared/js/approval-engine.js` v1.1.0
- **页面映射**: `shared/js/approval-config.js`（`window.APPROVAL_CONFIG_BY_PAGE`）
- **持久化**: `localStorage['ygt_approval_flow_templates_v2']`（v1 结构不兼容，未迁移）
- **页面（三页）**:
  - `pages/approval-flow-list.html`   审批流程配置（模板列表）
  - `pages/approval-flow-editor.html` 流程编排画布（独立画布，新建/编辑都进这里）
  - `pages/approval-monitor.html`     审批流程监控
- **已接入 14 个业务页**: 合同详情 ×6、付款、退款、追保函详情、客户准入、项目立项、
  货转上/下、仓储放货详情
- **PRD**: `docs/p-approval-flow-list.md`、`p-approval-flow-editor.md`、`p-approval-monitor.md`

### 人员目录（引擎内 PEOPLE，16 人 / 7 部门）
业务部 张磊·李娜·王浩·陈晨 / 风控部 赵敏·孙丽·郑浩 / 财务部 周涛·吴静·冯雪 /
法务部 许文静·何俊 / 仓储部 马强·高倩 / 总经理 秦建国 / 运营管理部 张爽
手机号全部为 `1XX 000X XXXX` 脱敏形式。下拉展示「完整姓名 + 脱敏手机号」。

### 应用模块（8 项，3 项带子项级联）
项目准入 / 合同管理（采购合同·销售合同）/ 货转管理（上游货转·下游货转）/
付款管理 / 退款管理 / 结算单管理（上游结算单·下游结算单）/ 追保函管理 / 放货管理

### ⚠️ 接入约束（改引擎时必读）
1. 引擎**不得**在 IIFE 执行时快照 `window.APPROVAL_CONFIG_BY_PAGE`，
   必须在 `mount()` 时动态读取（否则 script 顺序会让所有页面回退 standard）
2. 业务页挂载容器本身带 `class="timeline"` 时，引擎走 bare 渲染不再套第二层
3. 条件分支必须读 `evalBranch()` 返回的 `res.rules`（含 `matched`），
   不能读 `node.condition`（原始配置无该字段）

### ⚠️ 列表页组件规范（v1.1.0 统一，勿回退）
全站标准列表页必须用：`page-body`(bg-page) > `cp-panel` > `cp-block` >
`cp-table` / `cp-filter` + `cp-filter-summary` / `cp-pagination`，
标题用 `page-h1`(22px)，面包屑用 `breadcrumb-inline`，
操作列 `th+td` 都要 `col-action`（sticky 右固定），
状态标签只用 `tag-blue/yellow/green/red/gray`（**没有 tag-orange**），
表格类用 `cp-table`（**没有 data-table**），
边框 token 用 `--border-default`（**没有 --border-color，全站未定义，用了 border 整条失效**）。

### ⚠️ wrangler 部署坑
父目录 `workspace/` 下有别的项目的 wrangler.toml 含 `[assets]`，
wrangler 4.x 向上递归会命中并报 "Pages projects does not support 'assets'"。
**部署必须带 `--cwd` 锁当前目录**。
