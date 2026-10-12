# 02.17 审批管理 · 通用审批流程配置

> **页面**：`approval-flow-list.html`
> **版本**：v1.0.0（2026-10-12）
> **模块归属**：数字供应链 → 审批管理 → 审批流程配置
> **引擎**：`shared/js/approval-engine.js`
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
    ├── 审批流程配置   ← 本文档
    └── 审批流程监控   ← 见 p-approval-monitor.md
```

---

## 3. 页面结构

### 3.1 流程模板列表卡

| 列 | 内容 | 说明 |
|---|---|---|
| 流程名称 | 加粗蓝色 | 点击「编辑」进入编排器 |
| 状态 | 已启用 / 草稿 / 已停用 | 三色 tag |
| 节点数 | 整数 | 不含「提交申请」发起节点 |
| 流程说明 | 一句话描述 | 编辑器内维护 |
| 适用模块 | 模块名顿号分隔 | 多选，勾选后该模块引用此流程 |
| 最后修改 | 修改人 + 时间 | 自动记录 |
| 操作 | 编辑 / 复制 / 启用停用 / 删除 | 删除有二次确认 |

**顶部工具条**：搜索框（按名称/说明实时过滤）+ 状态下拉 + 「+ 新建流程」

### 3.2 流程编排器（点击编辑展开）

**左侧节点编排区**：

```
① 提交申请    发起节点 · 发起人提交，系统自动记录        ↑ ↓ ×
② 业务审批    串行审批 · 业务部 · 时限 24h              ↑ ↓ ×
③ 风控财务会签  并行会签 · 2 人会签 · 全部通过才算过       ↑ ↓ ×
④ 金额分支    条件分支 · 1 条条件规则 · 不满足则跳过      ↑ ↓ ×   ← 橙色虚线
⑤ 归档完成    串行审批 · —                               ↑ ↓ ×

[+ 串行审批] [+ 并行会签] [+ 条件分支]
```

- 点击节点 → 右侧属性面板加载该节点配置
- `↑ ↓` 调整顺序，`×` 删除（发起节点和归档节点禁止删除）
- 新增节点自动插入到「归档完成」之前

**右侧属性面板**（按节点类型动态渲染）：

| 节点类型 | 可配置项 |
|---|---|
| 发起节点 | 仅名称（只读） |
| 串行审批 | 节点名称、审批角色（下拉 6 选 1）、审批时限、节点说明 |
| 并行会签 | 主审批角色、会签成员列表（可增删，每行角色+部门）、审批时限、节点说明 |
| 条件分支 | 条件规则列表（字段/操作符/阈值/命中节点）、节点说明 |
| 归档节点 | 仅名称（只读） |

**流程说明** textarea + **适用模块** 多选 chip 组（12 个业务模块）

### 3.3 流程图预览

点击「预览流程图」展开，支持调整「模拟单据金额」实时看条件分支命中效果。

节点卡片显示：序号 / 节点名 / 部门 / 类型标签（会签 N 人 / 条件命中 / 已跳过）

---

## 4. 字段规则

### 4.1 流程模板主表

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 系统 | 内置：`standard` / `simple` / `highRisk`；新建：`flow_{时间戳}` |
| `name` | text | ✅ | 流程名称 |
| `desc` | textarea | - | 一句话流程说明 |
| `status` | select | ✅ | `draft` 草稿 / `enabled` 已启用 / `disabled` 已停用 |
| `applicableModules` | multi-select | - | 适用业务模块（12 选 N） |
| `nodes` | array | ✅ | 节点数组，见 §4.2 |
| `updatedAt` | datetime | 自动 | 保存时自动写入 |
| `updatedBy` | string | 自动 | 当前操作人 |

**持久化**：`localStorage['ygt_approval_flow_templates_v1']`，首次进入自动加载内置模板

### 4.2 节点结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 节点唯一标识 |
| `type` | enum | `start` 发起 / `serial` 串行 / `parallel_all` 并行会签 / `branch` 条件分支 |
| `name` | text | 节点显示名 |
| `role` | enum | 审批角色：`biz_manager` / `risk_manager` / `finance_manager` / `legal_review` / `gm` / `system` |
| `approvers[]` | array | **仅 `parallel_all`**：会签成员 `[{role, dept}]` |
| `condition[]` | array | **仅 `branch`**：条件规则 `[{field, operator, value, then[]}]` |
| `slaHours` | number | 审批时限（小时），超时在监控页标记 |
| `auto` | boolean | 是否归档节点（禁止删除） |
| `desc` | text | 节点说明（审批人提示语） |

### 4.3 审批角色字典（6 个）

| roleKey | 名称 | 部门 | 色值 |
|---|---|---|---|
| `submitter` | 提交申请 | 发起人 | `#64748B` |
| `biz_manager` | 业务审批 | 业务部 | `#2563EB` |
| `risk_manager` | 风控审批 | 风控部 | `#7C3AED` |
| `finance_manager` | 财务审批 | 财务部 | `#059669` |
| `legal_review` | 合规审查 | 法务部 | `#0891B2` |
| `gm` | 总经理审批 | 总经理 | `#DC2626` |

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

### 5.1 标准审批流程 `standard`

```
提交申请 → 业务审批 → 风控财务会签 → [金额 > 100万 → 总经理审批] → 归档完成
```

| # | 节点 | 类型 | 时限 |
|---|---|---|---|
| ① | 提交申请 | 发起 | — |
| ② | 业务审批 | 串行 | 24h |
| ③ | 风控财务会签 | 并行会签（2 人） | 48h |
| ④ | 金额分支 | 条件分支 | — |
| ⑤ | 归档完成 | 串行（auto） | — |

### 5.2 简易审批流程 `simple`

```
提交申请 → 业务审批 → 财务审批 → 归档完成
```
适用：合同管理、收发货管理（小额单据）

### 5.3 高风险审批流程 `highRisk`

```
提交申请 → 业务审批 → 风控财务会签 → 合规审查 → 总经理审批 → 归档完成
```
适用：追保函管理、资金管理（保证金调整、付款、退款）

---

## 6. 页面 → 流程映射

`shared/js/approval-config.js` 定义 `window.APPROVAL_CONFIG_BY_PAGE`：

| 业务模块 | 页面 | 引用流程 |
|---|---|---|
| 合同管理 | 采购/销售/补充合同详情（6 个） | `highRisk` |
| 资金管理 | 付款详情、退款详情、保证金调整记录 | `highRisk` |
| 资金管理 | 回款详情、回款编辑 | `simple` |
| 追保函管理 | 追保函详情 | `highRisk` |
| 准入管理 | 立项申请、项目详情 | `standard` |
| 准入管理 | 客户申请、客户详情 | `highRisk` |
| 收发货/货转 | 发货/收货详情、货转上下单、仓储放货详情 | `simple` |
| 结算单 | 采购/销售结算详情 | `standard` |
| 发票管理 | 进项/销项发票详情 | `simple` |
| 业务线 | 业务线详情 | `standard` |

---

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

## 8. 按钮交互

| 按钮 | 位置 | 行为 |
|---|---|---|
| + 新建流程 | 列表卡右上 | 生成含「提交申请 + 业务审批 + 归档完成」的草稿 |
| 编辑 | 列表行 | 展开编排器 |
| 复制 | 列表行 | 复制为 `xxx - 副本`，状态置 `draft`，节点 id 重映射 |
| 启用 / 停用 | 列表行 | 切换 `status` |
| 删除 | 列表行 | 二次确认弹窗，提示「引用该流程的业务模块需重新配置」 |
| 预览流程图 | 编排器右上 | 展开流程链 + 金额模拟器 |
| 保存 | 编排器右上 | 校验（发起节点/归档节点/会签成员/名称非空）→ 写 localStorage |
| 关闭 | 编排器右上 | 收起编排器（不保存草稿） |
| + 串行/会签/分支 | 编排器底部 | 新增节点，插入到归档之前并自动选中 |
| ↑ ↓ × | 每个节点右侧 | 调序 / 删除 |

---

## 9. 异常处理

| 异常 | 表现 | 处理 |
|---|---|---|
| 删发起/归档节点 | 点击 × | 弹窗「发起节点不可删除」/「归档节点不可删除」 |
| 会签无成员 | 点保存 | 弹窗「会签节点「xxx」至少需要 1 名会签人」 |
| 流程名为空 | 点保存 | 弹窗「请填写流程名称」 |
| 缺失发起或归档 | 点保存 | 弹窗提示必须保留 |
| localStorage 不可用 | 隐私模式 | `console.warn` 降级，配置仅本次会话有效 |
| 引用已删除流程 | 业务页打开 | `getFlow()` 返回 null → fallback 到 `standard` |
| 无单据金额 | 条件分支求值 | 条件判定为 false → 分支节点标记「已跳过」 |

---

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

- **v1.0.0（2026-10-12）**：首版
  - 通用审批引擎 `approval-engine.js`（串行 / 并行会签 / 条件分支）
  - 3 套内置流程模板 + 完整 CRUD
  - 14 个业务页面接入改造
  - 页面映射配置 `approval-config.js`
  - 修复页面映射未生效、timeline 容器嵌套、待提交状态节点错位三个缺陷