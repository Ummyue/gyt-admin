# 02.17 审批管理 · 审批流程配置（流程模板列表）

> **页面**：`approval-flow-list.html`
> **版本**：v1.1.0（2026-10-15）
> **模块归属**：数字供应链 → 审批管理 → 审批流程配置
> **引擎**：`shared/js/approval-engine.js` v1.1.0
> **页面映射**：`shared/js/approval-config.js`

---

## 1. 业务定位

**通用审批流程配置**让管理员无需开发即可自定义各业务模块的审批链路，解决三个痛点：

| 痛点 | 现状 | 本模块解决方式 |
|---|---|---|
| 审批节点硬编码在页面里 | 14 个业务页面各写一套 timeline，改节点要改代码 | 节点抽成配置数据，页面读配置渲染 |
| 不同业务审批规则不同 | 合同/回款/立项各不一样，无法统一 | 内置 3 套模板 + 可自由复制新建 |
| 金额大的单据审批层级不够 | 小额和大额走同样流程 | 条件分支按金额阈值自动增减节点 |

**一句话**：配置一次流程，全平台业务模块复用；改流程只改配置，不动代码。

---

## 2. 菜单结构

```
数字供应链（📦）
└── 审批管理
    ├── 审批流程配置   ← 本文档（模板列表）
    ├── 流程编排画布   ← 见 p-approval-flow-editor.md（两步向导）
    └── 审批流程监控   ← 见 p-approval-monitor.md
```

> **v1.1.0**：节点编排已从本页拆出，独立成「流程编排画布」页。
> 本页只负责模板列表（增删改查 / 复制 / 启停 / 跳转编排）。

---

## 3. 页面结构

### 3.1 流程模板列表卡

| 列 | 内容 | 说明 |
|---|---|---|
| 流程名称 | 加粗蓝色 | 点击「编辑」进入编排器 |
| 状态 | 已启用 / 草稿 / 已停用 | 三色 tag |
| 节点数 | 整数 | 不含「提交申请」发起节点 |
| 流程说明 | 一句话描述 | 编辑器内维护 |
| 应用模块 | 模块 chip，带子项的显示子项名 | 多选，在编排画布页维护 |
| 最后修改 | 修改人 + 时间 | 自动记录 |
| 操作 | 编排 / 复制 / 启用停用 / 删除 | 「编排」跳转独立画布页；删除有二次确认 |

**顶部工具条**：搜索框（按名称/说明实时过滤）+ 状态下拉 + 「+ 新建流程」

### 3.2 跳转独立编排画布

本页**不再内联节点编排器**。列表行的「编排」按钮、标题行的「新建流程」按钮均跳转到独立页面：

| 入口 | 目标 URL |
|---|---|
| 新建流程 | `approval-flow-editor.html?flowId=new` |
| 编排 | `approval-flow-editor.html?flowId={flowId}` |

编排页为**两步向导**：① 基础信息（流程名称/说明/状态/应用模块）② 流程设计（节点画布）。
新建与编辑共用同一套向导，详见 `p-approval-flow-editor.md`。

### 3.3 筛选与分页

- 筛选区：`流程名称`（模糊匹配名称与说明）、`流程状态`、`应用模块`
- 实时过滤，无「查询 / 重置」按钮（遵循全站标准筛选控件规范）
- 接入 `shared/js/filter-chips.js`，已录入条件以 chip 展示，可单独删除或一键清除
- 表格下方标准分页组件（每页 10 / 20 / 50 条）

## 4. 字段规则

### 4.1 流程模板主表

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 系统 | 内置：`standard` / `simple` / `highRisk`；新建：`flow_{时间戳}` |
| `name` | text | ✅ | 流程名称 |
| `desc` | textarea | - | 一句话流程说明 |
| `status` | select | ✅ | `draft` 草稿 / `enabled` 已启用 / `disabled` 已停用 |
| `applyModules` | array | - | **v1.1.0 改名** 应用模块，结构见 `p-approval-flow-editor.md` §5.3 |
| `nodes` | array | ✅ | 节点数组，见 §4.2 |
| `updatedAt` | datetime | 自动 | 保存时自动写入 |
| `updatedBy` | string | 自动 | 当前操作人 |

**持久化**：`localStorage['ygt_approval_flow_templates_v2']`，首次进入自动加载内置模板
> v1.0.0 用 `_v1`，数据结构不兼容（节点字段、模块结构全变），**不做迁移**。

### 4.2 节点结构（v1.1.0）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 节点唯一标识 |
| `type` | enum | `start` 发起 / `serial` 串行 / `parallel_all` 并行会签 / `branch` 条件分支 |
| `name` | text | 节点显示名 |
| `roleKey` | enum | 审批环节 key（分支指向 + 默认配色用） |
| `approver` | string | **v1.1.0** 审批人员 id（`type=serial` 且非归档时必填） |
| `approvers` | string[] | **v1.1.0** 会签人员 id 数组（`type=parallel_all` 时必填） |
| `remind` | object | **v1.1.0** 提醒规则 `{ enabled, afterHours }` |
| `condition` | array | **仅 `branch`**：条件规则 `[{field, operator, value, then[]}]` |
| `auto` | boolean | 是否归档节点（禁止删除） |
| `desc` | text | 节点说明（审批人提示语） |
| ~~`slaHours`~~ | — | **v1.1.0 下线**，由 `remind` 替代 |

### 4.3 审批环节字典（7 个）

> v1.1.0 起，环节只用于「条件分支指向」和「默认配色/默认审批人」，
> 实际审批人以节点上的 `approver` / `approvers` 为准。

| roleKey | 环节名 | 部门 | 配色 | 默认审批人 |
|---|---|---|---|---|
| `submitter` | 提交申请 | 发起人 | `#64748B` | — |
| `biz_manager` | 业务审批 | 业务部 | `#2563EB` | 张磊 |
| `risk_manager` | 风控审批 | 风控部 | `#7C3AED` | 赵敏 |
| `finance_manager` | 财务审批 | 财务部 | `#059669` | 周涛 |
| `legal_review` | 合规审查 | 法务部 | `#0891B2` | 许文静 |
| `warehouse` | 放货审批 | 仓储部 | `#EA580C` | 马强 |
| `gm` | 总经理审批 | 总经理 | `#DC2626` | 秦建国 |

**平台人员目录**：16 人，字段 `{ id, name, phone, dept, post }`，手机号全部脱敏。
完整名单见 `p-approval-flow-editor.md` §4.1。

### 4.4 条件分支字段

| 字段 | 类型 | 可选值 | 说明 |
|---|---|---|---|
| `field` | enum | `amount` 单据金额 / `bizType` 业务类型 / `contractType` 合同类型 / `customerLevel` 客户等级 / `riskLevel` 风险等级 | 求值字段 |
| `operator` | enum | `gt` > / `gte` ≥ / `lt` < / `lte` ≤ / `eq` = / `ne` ≠ | 比较操作符 |
| `value` | number | - | 阈值 |
| `then[]` | string[] | 审批角色 key 数组 | 命中时追加的节点 |

**求值规则**：`matched = OR(所有规则)`，任一条命中即展开对应角色节点；全部不命中 → 该分支节点标记「已跳过」，流程继续向下走。

---

## 5. 内置流程模板（3 套）

> 节点上的 `👤` 为审批人员，`⏰` 为提醒规则阈值。

### 5.1 标准审批流程 `standard`

```
提交申请 → 业务审批(张磊·24h) → 风控财务会签(赵敏+周涛·48h) → [金额 > 100 万 → 总经理审批] → 归档完成
```

应用模块：项目准入

### 5.2 简易审批流程 `simple`

```
提交申请 → 业务审批(王浩·24h) → 财务审批(吴静·48h) → 归档完成
```

应用模块：货转管理（上游货转 / 下游货转）、放货管理

### 5.3 高风险审批流程 `highRisk`

```
提交申请 → 业务审批(李娜·12h) → 风控财务会签(赵敏+周涛·24h) → 合规审查(许文静·48h) → 总经理审批(秦建国·24h) → 归档完成
```

应用模块：合同管理（采购合同 / 销售合同）、付款管理、退款管理、追保函管理

## 6. 页面 → 流程映射

`shared/js/approval-config.js` 定义 `window.APPROVAL_CONFIG_BY_PAGE`：

| 应用模块 | 业务页面 | 引用流程 |
|---|---|---|
| 合同管理 | 采购/销售/补充合同详情 + 框架/订单（6 个） | `highRisk` |
| 付款管理 | 付款详情 | `highRisk` |
| 退款管理 | 退款详情 | `highRisk` |
| 追保函管理 | 追保函详情 | `highRisk` |
| 合同管理（保证金） | 保证金调整记录 | `highRisk` |
| 项目准入 | 立项申请、项目详情 | `standard` |
| 客户准入 | 客户申请、客户详情 | `highRisk` |
| 货转管理 | 上游/下游货转详情 | `simple` |
| 放货管理 | 仓储放货详情 | `simple` |
| 结算单管理 | 采购/销售结算详情 | `standard` |
| 发票 / 收发货 | 发票详情、发货/收货详情 | `simple` |
| 回款管理 | 回款详情、回款编辑 | `simple` |
| 业务线 | 业务线详情 | `standard` |

## 7. 业务页面接入方式

```html
<!-- 1. 引入引擎（顺序不敏感：引擎在 mount() 时才动态读取映射表） -->
<script src="../shared/js/approval-engine.js"></script>
<script src="../shared/js/approval-config.js"></script>

<!-- 2. 审批容器（id 由页面自定义；容器带 timeline 类时引擎不再套第二层） -->
<div class="timeline" id="approvalTimeline" data-approval-engine="1"></div>

<!-- 3. 挂载（放在 </body> 前，且需在两个 script 之后） -->
<script>
(function () {
  function boot() {
    var el = document.getElementById('approvalTimeline');
    if (!el || !window.ApprovalEngine) return;
    var q = new URLSearchParams(location.search);
    var status = q.get('status') || '';
    var opts = {};
    // ?step=N 指定当前节点（0-based）；否则按 status 推断
    if (q.get('step')) opts.currentIdx = parseInt(q.get('step'), 10);
    else if (/待提交|草稿|未提交|暂存/.test(status)) opts.currentIdx = 0;
    else if (/已通过|已完成|已完结|执行中|审批中|待审批/.test(status)) opts.currentIdx = 2;
    else opts.currentIdx = 1;
    if (q.get('amount')) opts.formData = { amount: Number(q.get('amount')) };
    window.ApprovalEngine.mount(el, opts);
  }
  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', boot)
    : boot();
  window.addEventListener('load', boot);
})();
</script>
```

**引擎 API**：

| 方法 | 说明 |
|---|---|
| `ApprovalEngine.listFlows()` | 返回全部流程数组 |
| `ApprovalEngine.getFlow(id)` | 按 id 取流程 |
| `ApprovalEngine.saveFlow(flow)` | 新建/更新 |
| `ApprovalEngine.deleteFlow(id)` | 删除 |
| `ApprovalEngine.duplicateFlow(id, name)` | 复制 |
| `ApprovalEngine.evalBranch(node, formData)` | 条件分支求值 |
| `ApprovalEngine.resolveFlow(flow, formData)` | 展开为实际节点序列 |
| `ApprovalEngine.renderTimeline(opts)` | 渲染时间线 HTML |
| `ApprovalEngine.renderFlowChain(flow, formData)` | 渲染流程链 HTML |
| `ApprovalEngine.mount(selector, opts)` | 一行挂载到容器 |
| `ApprovalEngine.detectAmount(pageName)` | 自动提取页面单据金额 |

---

## 8. 按钮交互（v1.1.0）

| 按钮 | 位置 | 行为 |
|---|---|---|
| 数据导出 | 标题行右上 | Toast「已导出 N 条流程配置」（演示态） |
| 新建流程 | 标题行右上 | 跳 `approval-flow-editor.html?flowId=new` |
| 编排 | 列表行 | 跳 `approval-flow-editor.html?flowId={id}`（两步向导） |
| 复制 | 列表行 | 复制为 `xxx - 副本`，状态置 `draft`，节点 id 重映射 |
| 停用 / 启用 | 列表行 | 切换 `status` |
| 删除 | 列表行 | 二次确认，提示「引用该流程的业务模块需重新配置」 |

> v1.0.0 的「编辑 / 预览流程图 / 保存 / 关闭 / + 节点类型 / ↑↓×」等编排相关按钮，
> 已全部迁移到独立的编排画布页。

## 9. 异常处理

| 异常 | 表现 | 处理 |
|---|---|---|
| 引用已删除流程 | 业务页打开 | `getFlow()` 返回 null → fallback 到 `standard` |
| 无单据金额 | 条件分支求值 | 条件判定为 false → 分支节点标记「已跳过」 |
| localStorage 不可用 | 隐私模式 | `console.warn` 降级，配置仅本次会话有效 |
| v1 存量配置 | 升级后打开 | `_v1` key 不再读取，自动回落到内置模板 |
| 编排画布流程 id 不存在 | 打开画布 | Alert「流程不存在或已被删除」并跳新建态 |

> 节点级校验（发起/归档不可删、会签至少 1 人、串行必须选审批人、模块子项至少 1 个）
> 已迁移到画布页，见 `p-approval-flow-editor.md` §7。

## 10. 跨模块流转

```
审批流程配置（改流程）
      │  localStorage 持久化
      ▼
ApprovalEngine.getFlow(flowId)
      │
      ├─→ approval-monitor.html（流程监控引用同一份配置渲染节点）
      └─→ 14 个业务页面（读 APPROVAL_CONFIG_BY_PAGE 找到 flowId → 渲染时间线）
```

**关键约束**：配置存 `localStorage`，**同一浏览器**内配置页改动会实时影响业务页面；跨浏览器不同步（原型阶段限制）。

---

## 11. 技术实现要点

### 11.1 条件分支求值链路

```
resolveFlow(flow, formData)
  └─ 遍历 flow.nodes
      └─ node.type === 'branch'
          └─ evalBranch(node, formData)   ← 返回已求值的 rules（含 matched / then / text）
              └─ res.rules.filter(r => r.matched)
                  └─ each rule → push 展开的角色节点（fromBranch: true）
```

> ⚠️ **必须用 `res.rules`（已求值）而非 `node.condition`（原始配置）** —— 原始配置的规则上没有 `matched` 字段，filter 会全部落空导致分支节点不渲染。v1.0.0 开发期曾因此产生 bug，已修复并有 30 项回归测试覆盖。

### 11.2 渲染层级

```
renderTimeline(opts)
  └─ resolveFlow → 节点数组
      └─ 按 index 与 currentIdx 比较推导状态：
          i < currentIdx  → done（绿色 ✓）
          i === currentIdx → current（橙色高亮）
          i > currentIdx  → pending（灰色）
```

### 11.3 单据金额自动提取

`detectAmount(pageName)` 按优先级：
1. `data-approval-amount` 属性
2. URL 参数 `?amount=`
3. `APPROVAL_AMOUNT_CONFIG.defaultSelectors` 通用选择器
4. 单位换算：`unitMultiplier`（立项页金额单位是万元，×10000）

---

## 12. 验证记录

### 12.1 引擎单元测试（30 项全通过）

| 类别 | 用例数 | 覆盖 |
|---|---|---|
| 串行审批 | 2 | 节点数、顺序 |
| 并行会签 | 5 | 节点存在、成员数、成员部门、渲染子项、ALL 标记 |
| 条件分支 | 8 | 命中/跳过、边界值（100 万整不命中、1000001 命中）、无分支流程 |
| 流程 CRUD | 8 | 新建/列表/时间戳/复制/副本状态/节点 id 重映射/删除 |
| 持久化 | 1 | localStorage 写入 |
| 渲染健壮性 | 6 | 空流程、越界 index、-1、XSS 转义 |

### 12.2 页面接入验证（14 个页面，全部命中映射流程）

> v1.0.0 初测时曾出现「所有页面都是 5 节点」的现象，原因是引擎在 IIFE 执行时
> 快照了尚未加载的 `APPROVAL_CONFIG_BY_PAGE`（空对象），全部静默回退到 `standard`，
> 而 `standard` 恰好也是 5 节点，掩盖了问题。已修复：引擎改为在 `mount()` 时动态读取，
> 并把 4 个页面的引擎脚本提到 boot 脚本之前。

| 页面 | 命中流程 | 引擎节点 | 会签子项 | JS 错误 |
|---|---|---|---|---|
| contract-purchase-framework-detail | highRisk | 6 | 2 | 0 |
| contract-purchase-order-detail | highRisk | 6 | 2 | 0 |
| contract-sales-framework-detail | highRisk | 6 | 2 | 0 |
| contract-sales-order-detail | highRisk | 6 | 2 | 0 |
| contract-supplement-framework-detail | highRisk | 6 | 2 | 0 |
| contract-supplement-order-detail | highRisk | 6 | 2 | 0 |
| customer-apply | highRisk | 6 | 2 | 0 |
| payment-detail | highRisk | 6 | 2 | 0 |
| refund-detail | highRisk | 6 | 2 | 0 |
| bond-letter-detail | highRisk | 6 | 2 | 0 |
| goods-transfer-up-detail | simple | 4 | 0 | 0 |
| goods-transfer-down-detail | simple | 4 | 0 | 0 |
| warehouse-release-detail | simple | 4 | 0 | 0 |
| project-apply | standard | 5 | 2 | 0 |

**结果：14 / 14 全部通过**，节点标题序列逐一比对一致。

### 12.3 条件分支实测

| 场景 | 金额 | 展开节点 | 分支状态 |
|---|---|---|---|
| 立项申请 | 500,000 | 提交申请 → 业务审批 → 风控财务会签 → **金额分支(跳过)** → 归档完成 | 未命中 |
| 立项申请 | 3,000,000 | 提交申请 → 业务审批 → 风控财务会签 → **总经理审批** → 归档完成 | 命中 |

### 12.4 状态 → 当前节点映射实测（highRisk 流程，共 6 节点）

| `?status=` | 当前节点 | 结果 |
|---|---|---|
| 待提交 | 提交申请（发起） | ✅ |
| 审批中 | 风控财务会签 | ✅ |
| 执行中 | 风控财务会签 | ✅ |

---

## 13. 文档版本

- **v1.1.0（2026-10-15）**：节点编排拆分为独立画布页
  - 新增 `approval-flow-editor.html`（流程编排画布），本页只保留模板列表
  - 节点字段调整：去掉 `slaHours`，新增 `remind` 提醒规则
  - 「审批角色」改为「审批人员」（平台人员目录，姓名 + 脱敏手机号）
  - 「适用模块」改为「应用模块」，8 项 + 3 个带子项级联
  - 持久化 key 升到 `_v2`
- **v1.0.0（2026-10-12）**：首版
  - 通用审批引擎 `approval-engine.js`（串行 / 并行会签 / 条件分支）
  - 3 套内置流程模板 + 完整 CRUD
  - 14 个业务页面接入改造
  - 页面映射配置 `approval-config.js`
  - 修复页面映射未生效、timeline 容器嵌套、待提交状态节点错位三个缺陷