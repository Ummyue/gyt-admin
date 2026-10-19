# 豫港通数字供应链管理平台 — 当前状态快照
最后更新: 2026-10-19 审批管理模块 v1.5.0（去掉应用模块子项）

## 当前部署
- **apex URL**: https://yugangtong-prototype.pages.dev/ (永远指向最新)
- **最新 hash**: `bde075aa` (审批管理模块 v1.5.0 去掉应用模块子项)
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
- 最新 commit: `547430b` (refactor(approval): v1.5.0 去掉应用模块子项，8 模块全部平级，已推送)
- 项目级 config: `git -c user.name="Mavis" -c user.email="Mavis@local"`

## 审批管理模块（v1.5.0，2026-10-19）
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

### 应用模块（8 项，v1.5.0 起全部平级，无子项）
项目准入 / 合同管理 / 货转管理 / 付款管理 / 退款管理 / 结算单管理 / 追保函管理 / 放货管理

`applyModules` 数据结构 = **纯字符串数组**：`['contract','payment','refund','bond_letter']`。
v1.4.0 及之前是 `[{key, children:[...]}]`。读取侧用 `AE.normModules()` 统一收敛，
旧 localStorage 数据无需迁移即可正常渲染与筛选 → **持久化 key 保持 `..._v2` 不升版**。
⚠️ 子项概念已彻底下线，`APPLY_MODULES` 上不要再加 `children`；
调用方一律先用 `AE.normModules(list)` 再判断，list 页的 `e.key === md` 写法已失效。

### 编排向导（v1.2.0）
- 两步：① 基础信息（名称/说明/状态/应用模块）② 流程设计（画布），新建与编辑共用
- 顶部常驻保存，保存后回列表；步骤间可点击切换，切步骤 2 前校验基础信息
- 画布：连接线 `+` 向下弹出选项卡片插入节点；点节点弹右侧抽屉改属性；画布满宽
- 流程图预览为弹窗，用引擎渲染时间线（与业务单据「审批详情」同一视觉）
- 平台统一右侧抽屉：`.ap-drawer*` 定义在 `assets/css/approval.css`，
  监控页审批详情 / 画布节点属性 / 预览弹窗三处共用

### v1.4.0 变更（2026-10-19，user 指定）
1. **流程状态文案全站统一为「草稿 / 启用 / 停用」**（原「草稿 / 已启用 / 已停用」）。
   改的位点：编排页 3 个 radio + 帮助文案、编排页 `STATUS_META`、
   列表页 `statusMeta` + 筛选下拉 option。列表页操作列按钮本来就是「启用/停用」。
   顺带统一了 `disabled` 的 tag 色（编排页原 `tag-yellow` / 列表页 `tag-gray` → 统一 `tag-gray`）。
   **保留不动**：列表页操作后的 toast「流程已启用/流程已停用」——那是动作结果，
   「已启用」是正确的完成态表述，不要跟状态名混淆。
2. **应用模块子项从平铺改为复选下拉**。合同管理 / 货转管理 / 结算单管理 三个模块
   的子项不再向下平铺，改为 checkbox 右侧的复选下拉（`.wz-dd*`）。
   触发器文案：未选「请选择子项」/ 全选「全部（2）」/ 单选显示子项名 / 多选「首项 等 N 项」。
   面板顶部有「全选 / 清空」；点子项后面板保持展开（靠 `openDD` 变量在重渲染时恢复）。
   父模块未勾选时触发器 `is-disabled` 不可点开。存储结构与级联规则均未变。
   - ⚠️ `let openDD` 必须声明在脚本顶部（与 `let draft` / `let step` 同处），
     否则 `renderModules()` 在 init 时就调用它 → TDZ `Cannot access before initialization`

### v1.5.0 变更（2026-10-19，user 指定「本次需求去掉子项」）
子项整条链路下线：编排页的复选下拉（`.wz-dd*`）与「至少 1 子项」校验、
引擎 `APPLY_MODULES` 的 children、3 套内置模板的 children、列表页 chip 的
`has-child` 样式与子项后缀，全部删除。**v1.4.0 那版复选下拉已整体回退。**
改动文件：`approval-engine.js` / `approval-flow-editor.html` / `approval-flow-list.html`。
监控页与 14 个业务页无需改动（筛选下拉由 `APPLY_MODULES` 自动生成，
页面映射只用顶级模块 key），已回归确认。

## ⚠️ 已知既有缺陷（v1.4.0 排查时发现，非本轮引入，待产品决策）
**117 页里有 61 页左侧 sidemenu 渲染 0 项**（空 div）。
原因：这 61 页未登记进 `shared/js/topnav-drawer.js` 的 `window.TOPNAV_MENU`，
`left-sidemenu.js` 的 `getCurrentModule()` 按文件名反查，查不到就返回 null → 什么都不渲染。
历史上登记数一直是 67→70→71（71 是 v1.2.0 补的编排页），这 61 页从未登记过。
典型：所有 `*-detail.html` / `*-new.html` 下钻页，含 14 个已接审批引擎的业务详情页。
修复需要逐页确定「归属哪个一级模块 / 二级菜单」，属产品结构决策，未擅自批量补。

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

### ⚠️ 清除全部必须派发事件（v1.4.0 修，勿回退）
`shared/js/filter-chips.js` 的 `clearAllFilters()` 清空 `.cp-filter input/select` 后
**必须** `dispatchEvent(new Event('input'))` + `Event('change')`，
否则页面 `oninput="renderList()"` 这类实时过滤不会重绘表格 —— 表现为：
输入框空了、chip 也清了，但表格仍停在筛选结果，用户以为筛选坏了。
（单个 chip 的 `×` 一直有派发事件，`clearAllFilters` 漏了；`payment-list` /
`goods-transfer-up` / 审批两页都中招。是全站通病，不止审批模块。）

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
