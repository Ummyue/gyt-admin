# 豫港通数字供应链管理平台 — 当前状态快照
最后更新: 2026-10-16 审批管理模块 v1.3.0（页面外壳对齐标准列表页）

## 当前部署
- **apex URL**: https://yugangtong-prototype.pages.dev/ (永远指向最新)
- **最新 hash**: `91b1422c` (审批管理模块 v1.3.0 页面外壳对齐)
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
- 最新 commit: `7f9cd7e` (fix(approval): v1.3.0 页面外壳对齐标准列表页，已推送)
- 项目级 config: `git -c user.name="Mavis" -c user.email="Mavis@local"`

## 审批管理模块（v1.3.0，2026-10-16）
- **引擎**: `shared/js/approval-engine.js` v1.1.0
- **页面映射**: `shared/js/approval-config.js`（`window.APPROVAL_CONFIG_BY_PAGE`）
- **持久化**: `localStorage['ygt_approval_flow_templates_v2']`（v1 结构不兼容，未迁移）
- **页面（三页）**:
  - `pages/approval-flow-list.html`   审批流程配置（模板列表）
  - `pages/approval-flow-editor.html` 流程编排（**两步向导**：① 基础信息 ② 流程设计）
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

### 编排向导（v1.2.0）
- 两步：① 基础信息（名称/说明/状态/应用模块）② 流程设计（画布），新建与编辑共用
- 顶部常驻保存，保存后回列表；步骤间可点击切换，切步骤 2 前校验基础信息
- 画布：连接线 `+` 向下弹出选项卡片插入节点；点节点弹右侧抽屉改属性；画布满宽
- 流程图预览为弹窗，用引擎渲染时间线（与业务单据「审批详情」同一视觉）
- 平台统一右侧抽屉：`.ap-drawer*` 定义在 `assets/css/approval.css`，
  监控页审批详情 / 画布节点属性 / 预览弹窗三处共用

### ⚠️ 测试脚本坑（线上回归）
- `verify_v11_pages.py` 里「画布 · 8 个应用模块」用 `.cv-mod`，但 v1.2.0 已把
  应用模块移到步骤 1，类名改成 `.wz-mod` —— 断言过时会一直 FAIL，别误判成页面回归
- 测「无列被 sticky 操作列遮挡」时，**只能取第一张 `.cp-table`** 的表头。
  用 `querySelectorAll('.cp-table thead th')` 会把抽屉里第二张表（提醒记录）
  一起算进去，产生假 FAIL
- 测 `wz-topbar` 对齐要量**内容区**（`rect.left + paddingLeft`），
  border-box 起点是 220，看起来像没对齐其实是对的
- pages.dev 国内偶发 `ERR_TIMED_OUT` / 30s `Page.goto` 超时，属网络抖动，
  回归脚本要带重试，别当页面缺陷


### ⚠️ 新增页面必须登记 topnav-drawer.js
`left-sidemenu.js` 靠 `window.TOPNAV_MENU` 反查页面所属模块。
新增页面若不登记进去，左侧菜单会**静默渲染 0 项**（画布页曾长期如此）。

### ⚠️ 接入约束（改引擎时必读）
1. 引擎**不得**在 IIFE 执行时快照 `window.APPROVAL_CONFIG_BY_PAGE`，
   必须在 `mount()` 时动态读取（否则 script 顺序会让所有页面回退 standard）
2. 业务页挂载容器本身带 `class="timeline"` 时，引擎走 bare 渲染不再套第二层
3. 条件分支必须读 `evalBranch()` 返回的 `res.rules`（含 `matched`），
   不能读 `node.condition`（原始配置无该字段）

### ⚠️ 列表页组件规范（v1.1.0 统一，v1.3.0 补外壳，勿回退）
全站标准列表页必须用：`page-body`(bg-page) > `cp-panel` > `cp-block` >
`cp-table` / `cp-filter` + `cp-filter-summary` / `cp-pagination`，
标题用 `page-h1`(22px)，面包屑用 `breadcrumb-inline`，
操作列 `th+td` 都要 `col-action`（sticky 右固定），
状态标签只用 `tag-blue/yellow/green/red/gray`（**没有 tag-orange**），
表格类用 `cp-table`（**没有 data-table**），
边框 token 用 `--border-default`（**没有 --border-color，全站未定义，用了 border 整条失效**）。

### ⚠️ 页面外壳三件套（v1.3.0 补齐，审批三页曾集体缺失）
1. **`.page-body { padding: 20px 24px; }`** 必须写在页面自己的 `<style>` 首行。
   漏了 → `cp-panel` 直接贴内容区左右边缘（l=容器左边界），左右无 24px 留白。
   判定：viewport 1600 下 `cp-panel` 应 `L=244 R=1576`，
   `cp-table-wrap` 应 `L=245 R=1575 W=1330`。
2. **topbar 必须写全**：菜单后跟 `topbar-changelog-btn`（📋 版本变更记录），
   再跟 `topbar-right`（通知铃铛 + 用户头像/姓名/部门）。117 页里 113 页有 `topbar-right`。
   topbar 菜单链接也必须归一：`预警中心→./warning-list.html`、`账户中心→./account-personal.html`。
3. **「数据导出」只放 `cp-filter-summary` 右侧**（`btn-text btn-sm` + 下载图标），
   标题行只留主操作按钮（`btn-primary`）。别在标题行堆第二个 default 按钮。

### ⚠️ 表格列宽（v1.3.0）
`.cp-table` 全局 `min-width: 1500px`，在 1330px 容器里必然横向溢出，
sticky 操作列会盖住倒数第二列（表现为表头只剩一个字竖排）。两种合规解法：
- 列少（≤7 列）：`<table class="cp-table" style="min-width: 0;">` + 百分比列宽（和为 100）
- 长文本列必须 `.cp-table tbody td.ap-wrap-cell { white-space: normal; }`
  —— 选择器要写 `.cp-table tbody td.x`（0,2,2）才压得住 `.cp-table tbody td`（0,1,2），
  只写 `.ap-wrap-cell` 不生效

### ⚠️ wrangler 部署坑
父目录 `workspace/` 下有别的项目的 wrangler.toml 含 `[assets]`，
wrangler 4.x 向上递归会命中并报 "Pages projects does not support 'assets'"。
**部署必须带 `--cwd` 锁当前目录**。
