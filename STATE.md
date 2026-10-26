# 豫港通数字供应链管理平台 — 当前状态快照
最后更新: 2026-10-26 页面标记点 pin annotation 接入补全 + 触发按钮绑定修复

## 当前部署
- **apex URL**: https://yugangtong-prototype.pages.dev/ (永远指向最新)
- **最新 hash**: `25c52367` (审批管理模块 v1.11.0 应用模块新增「回款管理」+ 遗留手机号脱敏)
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
- 最新 commit: `decfc7c` (feat(approval): v1.11.0 应用模块新增「回款管理」+ 补做遗留手机号脱敏，已推送)
- 项目级 config: `git -c user.name="Mavis" -c user.email="Mavis@local"`

## 审批管理模块（v1.11.0，2026-10-21）
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

### ⚠️ 脱敏扫描的两种误报（2026-10-21 踩）
手机号正则 `[1][3-9]\d{9}` 会在**长数字串**里误命中：
- `SKZJ20240618150005005`（银行流水号）→ 命中其中 `18150005005`
- 发票号 `264120000001452870092` → 命中其中 `18150005005` 同类片段
**判定方法**：看命中处**上下文是不是手机号语境**（人名后缀、`data-owner`、
`contactPhone`）。误报**不要改**，改了就破坏流水号/发票号。

另外：`.offline-build/` 与 `.deploy_tmp/` 在 `.gitignore` 里（第 5、12 行），
git 未跟踪 → **不发布到公开仓库**，里面的旧值不算泄漏；但 `.offline-build/`
是给业主的离线包，内容已陈旧（早于 2026-07-09 脱敏），要重打需 user 确认。

### 顺带修掉的 2 个页面脚本结构缺陷（2026-10-26）
排查 pin 缺口时发现**全站只有 2 页的脚本块结构是断的**（用「HTML 里声明了 + 浏览器实际加载了」双向比对定位）：

| 页面 | 病因 | 症状 | 修法 |
|---|---|---|---|
| `pages/shipment-in-detail.html` | 闭合标签写成转义形式 `<\/script>`（3 处）—— HTML 解析器在 script-data 状态下**不认** `\/` 转义，导致整个块不闭合 | `left-sidemenu.js` / 内联脚本 / pin 脚本**全都没加载**；左侧菜单空白 | 还原为 `</script>` |
| `pages/changelog.html` | 缺 pin 脚本引用 | 无标记点能力 | 在**真正的** `</body>` 前注入（见下方坑） |
| `docs-renderer.html` | `h.textContent.replace(/#, '')` —— 非法正则（未闭合字符类） | 控制台 `Invalid regular expression: missing /` | 改为 `replace(/^#\s*/, '')` |

⚠️ **注入 `</body>` 前必须用 `rfind` 而不是 `replace`（第一次匹配）**：
`changelog.html` 的变更记录**数据字符串里含有字面量 `</body>`**（那段文字在描述
「在 body 末尾 … 之前插入 modal 弹窗」）。用 `s.replace("</body>", ...)` 会把脚本标签
插进 JS 字符串中间 → `Invalid or unexpected token`，页面直接白屏。
**通用规则：往 HTML 注入脚本一律用 `rfind("</body>")` 定位最后一个。**

### 页面标记点 pin annotation 接入补全（2026-10-26）
**背景**：功能早在 `v1.7.99.262` 就全局装好了（`assets/js/pin-annotation.js` + `assets/css/pin-annotation.css`），
但**后续新建的页面没被覆盖到**，且触发按钮存在「渲染出来但点不动」的隐患。

| 改动 | 说明 |
|---|---|
| 3 个审批页补引用 | `approval-flow-list` / `approval-flow-editor` / `approval-monitor` 建于 pin 全量注入之后，缺 CSS+JS 引用 |
| `index.html` 补全 | 原型首页（用户实际入口）原本无任何 pin 引用；补 CSS+JS + 顶部工具区触发按钮 |
| **修 JS bug（关键）** | `init()` 里 `ensureTriggerBtn()` / `updateTriggerBtn()` 原本**只在存在 `#btnCenter` 时才调用**（`#btnCenter` 是 app.html 专有）。导致任何「自带 `#pinTriggerBtn` 但没有 `#btnCenter`」的页面，按钮渲染出来却**没绑事件，点了没反应**。改为无条件调用（`ensureTriggerBtn` 内部对「无自带按钮且无 `#btnCenter`」会直接返回，不会多造按钮） |
| `_clear-pins.html` 不注入 | 它就是「清理全站标记点」工具页本身，注入反而自相矛盾 |

⚠️ **不要用 skill 的基础版资产覆盖项目版**：`assets/js/pin-annotation.js` 有 22 处
iframe / postMessage 增强（cockpit 嵌外部 BI 站点、project-apply/detail 带 iframe），
skill 原版没有这些，会丢 `v1.7.99.262.x` 系列热修。

**pin 的真实行为**（写验证脚本时别踩）：
- 存储 `localStorage['ygt_pin_data']` = `{ password, pins: [] }`，`pins` 是**扁平数组**，
  每条带 `page` 字段按 URL 归一化（无 `.html`）→ **pin 按页面隔离，跨页不串**
- 描述保存走 **`#pinEditorSave` 按钮**（不是 skill 文档写的 Ctrl+Enter）
- 锁定是**内存态** `state.lockedUntil`（5 分钟），**不落 localStorage**
- 输错 3 次 → 关闭密码框 + `alert('密码错误次数过多，已锁定 5 分钟')`；
  锁定期间再点触发 → `alert('密码输入已被锁定…')` 且**不再创建密码框**

### v1.11.0 变更（2026-10-21，user 要求「基础信息页应用模块增加回款管理」）
- **`APPLY_MODULES` 新增第 9 项** `{ key: 'receipt', label: '回款管理' }`，
  位置插在「退款管理」之后 —— 依据产品菜单「数字供应链 → 资金管理」下
  付款管理 → 退款管理 → 回款管理 → 保证金管理 的相对顺序。
- **模块 key = `receipt`**，与 `receipt-list.html` / `receipt-detail.html` / `receipt-edit.html` 对齐。
- **全站自动生效**：列表页 `#filterModule`、监控页 `#fltModule`、编排页 `.wz-mods`
  全部从 `AE.APPLY_MODULES` 派生，改一处就够，**不用逐页改**。
- **内置模板 `applyModules` 默认值未动**（`standard`/`simple`/`highRisk` 保持原样），
  避免影响既有演示行为；localStorage key 不升版。
- ⚠️ **发现缺口（未修，待 user 决策）**：`approval-config.js` 里已写了
  `'receipt-detail': 'simple'` / `'receipt-edit': 'simple'`，
  但 **4 个回款页都没引入 `approval-engine.js`**，所以这些映射是**死配置**，
  回款单据上不会出现审批时间线。接入成本不高（参照 `payment-detail.html`：
  容器 div + 2 个 script 标签 + `mount()` 调用，参数读 URL query），
  但属于「新增 2 个业务页接审批」的独立范围，需 user 确认是否要做。

### ⚠️ wrangler「fetch failed」= 代理瞬时抖动，不是 token 问题（2026-10-20 踩）
连续 6 次 `fetch failed` 时**先别怀疑 token 有效性**。用 curl 分层定位：
```
curl --noproxy '*' https://api.cloudflare.com/client/v4/ips   # 直连
curl -x http://127.0.0.1:7890 https://api.cloudflare.com/client/v4/ips  # 走代理
nc -z 127.0.0.1 7890   # 代理端口
```
本例：curl 全部 `status=000 t=0.008s`（秒失败不是超时 = 连接被拒），
但 github / pages.dev 同时正常 → 是**本机代理客户端瞬时抽风**，等一会儿重试即恢复。
判定要点：**秒级失败 ≠ 超时**，秒级失败看代理端口；超长超时才看 token / 权限。

### v1.10.0 变更（2026-10-20，user 要求「节点属性抽屉增加通知类型，默认勾选站内信 + 支持短信」）
三个决策点已与 user 确认：① **只作用于「审批通知」**，提醒规则不变（仍固定站内信+短信）；
② **站内信强制勾选不可取消**（合规留痕）；③ **画布卡片 + 时间线同步显示渠道**。

- **引擎**：`NOTIFY_CHANNEL{inbox,sms}` / `NOTIFY_CHANNEL_LABEL` / `NOTIFY_CHANNEL_ORDER` /
  `notifyChannelsText(list)`；`normNode` 里 **恒补 `inbox`**、只认 `inbox`/`sms`、去重、
  按固定顺序排列 —— 前端绕过直接改 localStorage 也去不掉站内信。
- **编排页抽屉**：「审批通知」下方新增 `.cv-field` 「通知类型」，2 行 `.cv-chan-opt`；
  站内信 `disabled` + 行尾蓝色「必选」标记；短信可勾。
- **依赖态**：未选接收人 → `.cv-chan-box.is-disabled` 整块置灰 + 换文案
  「请先在上方选择接收通知的人员，再配置推送渠道」。
- **同步展示**：画布卡片 🔔 行与引擎 `renderTimeline` 通知行都追加 `（站内信、短信提醒）`。
- ⚠️ **localStorage 结构是 `{ flowId: flow }`（按 id 存），不是 `{flows:[...]}`** ——
  写验证脚本读落库数据时别读错路径。
- ⚠️ **保存/点画布前要先关抽屉**：`.ap-drawer` 的遮罩会拦截 topbar 的「保存」按钮，
  playwright 直接 click 会超时。用 `#propsDrawer .ap-drawer-close` 的 JS click 关掉。
- ⚠️ **关预览弹窗要用 `#previewMask .ap-drawer-close`**：`[onclick='closePreview()']`
  会同时命中 × 和「关闭」按钮（strict mode violation）；
  `.ap-drawer-close` 裸选会先命中抽屉的关闭按钮。

### v1.9.0 变更（2026-10-19，user 指出「预览审批流下方的金额没有实际意义，删除」）
- **删除流程图预览弹窗 footer 的「模拟单据金额」输入框**：配置态没有真实单据，
  让人手输一个假金额去驱动条件求值没有意义。改动 4 处：
  ① footer 的 `.pv-amount` 容器删除；② `.pv-amount` CSS 删除，
  `.pv-summary .v .hint` 替代；③ `renderPreview()` 的 `amt` 改取模块级常量
  `PREVIEW_AMOUNT = 500000`，不再读 DOM；④ `.ap-modal-footer` 的
  `justify-content` 由 `space-between` 改 `flex-end`（只剩一个按钮，
  否则会贴到左边）。
- **摘要区「模拟金额」→「条件评估金额 ¥ 500,000.00（演示基准值）」**：
  求值明细表的「实际值」列仍要有数可看，所以保留展示，但改名为
  「条件评估金额」并加灰色小字「演示基准值」，避免被误读成可编辑的真实业务输入。
- ⚠️ **别把这个输入框加回来**。求值基准是**演示常量**不是业务参数；
  真实金额只在业务单据提交时由单据自身带入。

### v1.8.0 变更（2026-10-19，user 指定「条件只留一条金额 + 会签无条件 + 加审批通知」）
- **触发条件收敛为单条金额条件**：`condition` 长度恒 ≤ 1、`field` 恒为 `'amount'`；
  抽屉里「字段」下拉换成固定灰底标签「单据金额」，「+ 添加条件」按钮删除，
  `renderRules`/`addRule`/`removeRule` 三个函数删掉，换成 `setCondEnabled`/`setCondRule`。
- **并行会签不提供触发条件**：`refreshPropsBody` 里整段包 `if (!isPar)`；
  `setApproveMode('parallel_all')` 清空 `n.condition`；引擎 `normNode` 对 `parallel_all`
  强制 `condition = []`（前端绕过也会被这层兜住）。
- **新增「审批通知」**：提醒规则下方一个复选下拉，按部门分组 16 人 + 全选/清空，
  存储 `node.notify: [人员id]`；画布卡片加 `🔔 通过后通知 N 人`，引擎时间线加
  「🔔 审批通过后通知：xxx」（被跳过节点不显示）。
- ⚠️ **抽屉里的绝对定位下拉，`.ap-drawer-body` 是 `overflow:auto`，向下弹会被裁**。
  必须：① 空间不够时加 `.up` 翻到上方；② **先 `add('open')` 再量 `scrollHeight`** ——
  `display:none` 时 `scrollHeight` 恒为 0，量了也不翻；③ 基准用 `.ap-drawer-body` 的
  可视底边而不是 `window.innerHeight`（抽屉有 sticky header/footer，可视区更矮）。

### v1.7.0 变更（2026-10-19，user 指出步骤 1 底板丢了）
`.page-body` 的 `--bg-page` 底色**没丢**（与标准页实测同为 `rgb(248,250,252)`），
丢的是「白色内容底板」这一层 —— 步骤 1 表单直接浮在灰底上。
改为 `cp-panel.wz-panel`（`#FFF` / 12px 圆角 / `--border-default` 1px / `overflow:hidden`，
与列表页 `cp-panel` 逐项一致）+ 两个 `cp-block`（表单块 / 按钮块）。
面板取 `max-width: 860px` 居中，表单仍 760px。
⚠️ 表单页的惯例是 `.info-section`（6px 圆角 + 蓝色左标题条），列表页是 `.cp-panel`（12px 圆角）。
编排页步骤 1 走 `cp-panel`，因为它是向导里的配置表单、不是单据录入页。

### v1.6.0 变更（2026-10-19，user 指定「节点聚合 + 画布整页纵向」）
1. **业务节点类型收敛为单一「审批节点」**
   `NODE_TYPE = { start, approval, archive }`。串行/并行不再是节点类型，
   而是 `approveMode: 'serial' | 'parallel_all'`（单选互斥）。
   原 `branch` 节点类型删除 —— 条件改为审批节点上的可选 `condition[]`，
   语义是「满足任一条才执行本节点，全不命中则跳过」，**不再有 `condition[].then` 追加角色**。
   插入选项由 3 项（串行/会签/分支）聚合为 **1 项「审批节点」**；
   抽屉表单由「按 n.type 分 3 套」改为「固定 6 段，人员区按 approveMode 切换」。
2. **画布整页铺满 + 节点纵向**
   进入步骤 2 给 `.page-body` 加 `is-canvas`（`overflow: hidden !important` + flex），
   滚动交给 `.cv-canvas` 自身。节点 420px 宽纵向单列居中，连接线改 1×34 竖线。
   ⚠️ `.page-body` 上有内联 `style="overflow-y:auto"`，优先级高于样式表，
   `is-canvas` 的 overflow **必须 `!important`** 才生效。
3. **兼容**：`normNode()` / `normFlow()` 在 listFlows/getFlow/resolveFlow 入口归一化三代历史数据
   （`serial`→`approval+serial`、`parallel_all`→`approval+parallel_all`、`serial+auto`→`archive`、
   `branch`→按 `then` 角色展开成多个 `approval` 节点并继承条件）。
   `standard` 内置模板的「金额分支」节点已直接改写为「总经理审批 + 单据金额>100万 条件」，行为不变。
   持久化 key 仍是 `..._v2`（读取侧已兼容，不升版）。

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
