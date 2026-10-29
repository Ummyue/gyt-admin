# 附件分类增强（跨模块统一交互）· v1.22.0

> **模块**：准入管理 / 收发货 / 货转 / 付款 / 退款 / 保证金 / 采购·销售结算单 / 追保函 / 出入库 / 提放货 / 黑名单
> **实现**：`shared/js/attach-categories.js`（零依赖、零构建、不引 CDN）+ `scripts/inject_attach_feature.py`（批量注入）
> **来源**：`pages/project-apply.html` 的「客户准入材料上传」交互口径（v1.21.0 先落地，本版铺开）

---

## 1. 三项能力

### 1.1 「上传无此附件说明」入口

每个**材料类别行**的上传按钮后方新增一个琥珀色虚线按钮：

| 项 | 规则 |
|---|---|
| 位置 | 类别行内，紧跟「上传」按钮之后 |
| 行为 | 点击同样弹文件选择框，但走 `no-such` 模式（与本体上传分离） |
| 文件属性 | 上传后的文件带 `noSuch: true` |
| 行内标记 | 该类别行显示徽标「⚠ 含无此附件说明」 |
| 文件级标记 | 文件 chip 上显示徽标「**非本附件本体**」（琥珀色） |
| 更换 / 删除 | 该类文件支持「更换」（重选文件替换，替换后保留 `noSuch` 属性）与「删除」 |
| 必填校验 | **不计入**必填项的上传判定 —— 必填材料仍必须上传材料本体，不能用说明顶替 |

### 1.2 上传后回显文件名称

原先多数模块的上传按钮是**纯装饰**（无事件）或 `alert('上传')` 占位，且上传后不显示文件名。
本版组件**接管**类别行内的上传按钮，改为真实文件选择，并在该行内回显：

```
[📄 body.pdf  ×]  [📄 nosuch.pdf  ×]   ← 文件 chip（文件名可点击预览，× 删除）
```

- 文件名超长自动省略，hover 显示全名 + 大小 + 上传时间
- 图片类型显示 🖼️，其余显示 📄

### 1.3 「自定义附件」分区

在附件区**下方**追加一个独立分区（紫色系标识，与内置材料区分）：

| 能力 | 规则 |
|---|---|
| 新增条目 | 分组头「+ 新增附件」→ 组内出现内联输入行 → 输入名称回车/点「确定」；名称为空或与已有条目重名时拦截并提示 |
| 编辑名称 | 点击条目名称 → 就地变为输入框 → 回车/失焦保存，Esc 取消；重名同样拦截 |
| 删除条目 | 条目行「删除条目」按钮；**若该条目已上传附件 → 弹二次确认**，文案点明已上传附件数与「一并删除且无法恢复」；未上传附件则直接删除 |
| 必填性 | 一律非必填，不参与必填项校验 |
| 自身上传 | 每个自定义条目有「↑ 上传」与「📄 上传无此附件说明」两个入口，行为与类别行一致 |
| 摘要 | 分组头显示「X / Y 已上传」进度 |

---

## 2. 覆盖范围

| 模块 | 落地页面 | 附件区形态 |
|---|---|---|
| 准入管理 | `project-apply.html` | 分组材料清单（内联实现，v1.21.0） |
| **客户准入** | `customer-apply.html` | **v1.22.0 新建材料上传区块**（见 §2.0） |
| 收发货 | `shipment-out-new.html` | `.attach-row` 行式 |
| 货转 | `goods-transfer-up-new.html`、`goods-transfer-down-new.html` | `.attach-row` 行式 |
| 付款 | `payment-detail.html` | 表格（标题「附件」定位） |
| 退款 | `refund-detail.html` | 表格（标题「附件」定位） |
| 保证金 | `margin-register.html`、`margin-adjust.html` | 表格 |
| 采购 / 销售结算单 | `settlement-purchase-new.html`、`settlement-sales-new.html` | 表格 |
| 追保函 | `bond-letter-new.html`、`bond-letter-detail.html` | 行式 / 表格 |
| 出入库 | `warehouse-inbound-new.html`、`warehouse-outbound-new.html`、`warehouse-inbound-detail.html` | 表格 |
| 提放货 | `warehouse-release-new.html` | 表格 |

### 2.0 客户准入：新建「客户准入材料上传」区块（v1.22.0）

客户准入模块原本**没有任何附件区**（`customer-apply` 是单企业表单、无「添加关联企业」弹窗；
`customer-detail` 的「📎 附件 4 份」只是审批时间线里的静态文字）。
按产品决定，在 **`customer-apply` 的「新增客户」表单内新增一个「客户准入材料上传」区块**，
内容与 `project-apply` 的客户准入材料完全一致：

| 项 | 规则 |
|---|---|
| 位置 | 「新增客户」卡片内，「关联项目」展开区之后 |
| 材料清单 | 13 类（必填 6 + 非必填 7），与 project-apply 一致 |
| 区块内容 | 顶部摘要（必填 X/6 · 非必填 X/7）+ 13 个材料类别行 + 共享组件注入的「上传无此附件说明」与「自定义附件」分区 |
| 交互 | 与 project-apply 同一套：接管上传按钮 → 真实文件选择 → 行内回显文件名；无此附件说明带「非本附件本体」标记 |
| **必填校验** | Step 1「下一步」时校验 6 项必填材料；**只认材料本体**，「无此附件说明」不计入；缺失时弹窗列出未传项 |
| 实现 | 复用 `shared/js/attach-categories.js`（注入器 TARGETS 已加该页），类别行由页面静态给出 |

### 2.1 两个模块未覆盖（需产品确认）

| 模块 | 原因 |
|---|---|
| **黑名单**（`blacklist.html`） | 该页的「附件」实为 **Excel 名单批量导入**弹窗（导入 xlsx/xls/csv），语义是「导入名单文件」而非「单据附件」，不适用本套交互 |

（客户准入已按产品决定新建材料上传区块，见 §2.0）

### 2.2 `shipment-in.html`（收发货-入库）无附件区

该页只有 `.attach-row-list` 的 **CSS 规则**（从别页复制而来），**HTML 里没有任何附件区标记**，因此未注入。属死样式，不影响功能。

---

## 3. 技术实现

### 3.1 共享组件 `shared/js/attach-categories.js`

零依赖、零构建、不引任何 CDN；样式由组件自己注入 `<style>`。

**页面配置**（由注入器写入）：

```js
window.__ATTACH_ZONES__ = [
  // 方式 A：按「区标题文本」定位（最稳，优先用）
  { titleSel: 'h3.info-section-title', titleText: '附件', zoneSel: '.info-section-body', row: 'tbody > tr' },
  // 方式 B：直接给容器选择器
  { zone: '.form-section-body:has(table.attach-table)', row: 'tbody > tr' },
  // 方式 C：不配置 → 组件自动识别（找含 table.attach-table 的最近容器 + tbody > tr）
];
```

**类别行识别**：
- 表格行 → 第一个 `td` 的文本（去掉必填星号）
- `.attach-row` → `.attach-label` 文本
- `.bl-uploaded-row` → `.bl-up-label` 文本

**上传按钮接管**：给行内上传按钮加 `data-ac-bound="zoneId|key"`，并绑定 click → 真实文件选择。原有 `onclick`（`alert('上传')` / mock toast）被 `preventDefault + stopPropagation` 拦截。

### 3.2 批量注入器 `scripts/inject_attach_feature.py`

```bash
python3 scripts/inject_attach_feature.py            # 注入
python3 scripts/inject_attach_feature.py --check    # 只体检
python3 scripts/inject_attach_feature.py --revert   # 回滚
```

- 注入块带注释标记 `<!-- ==== attach-categories 注入开始 (v1.22.0) ==== -->`，可幂等重复执行 / 精准回滚
- 目标页与定位配置集中在脚本顶部的 `TARGETS` 表里，一目了然

### 3.3 注意事项

⚠️ **组件接管上传按钮后，页面原有的 `uploadAttach()` / `alert('上传')` 等 mock 逻辑不再触发**——
这是有意的：那些是占位实现，现在换成真实上传 + 文件名回显。若某页需要保留特定业务逻辑，
应在 `TARGETS` 里给该页加 `keepOnclick: true` 单独处理。

⚠️ **组件状态存在内存**（`ZONES`），刷新页面即清空 —— 与原型其它 mock 一致。
若要持久化，需接入 localStorage（客户准入版已实现条目名持久化）。

---

## 4. 与「客户准入材料上传」（v1.21.0）的关系

`pages/project-apply.html` 的客户准入材料区是**内联实现**（13 类材料、必填 6 + 非必填 7、必填校验），
交互口径与本组件一致，但**尚未抽成共享组件**（它还额外承担了必填校验与随材料入库的职责）。
后续如要收敛，可把 project-apply 也切到共享组件 + 保留其校验逻辑。
