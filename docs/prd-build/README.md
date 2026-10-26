# PRD 汇编（Word）生成包

本目录是 `docs/数字供应链平台-产品需求文档汇编.docx` 的可再生来源。改需求 → 改事实层 JSON → 重跑脚本 → 重新出 Word。

## 目录结构

```
prd-build/
├── modules/*.json        29 个业务模块的结构化事实层（唯一数据源）
├── capture_shots.py      抓原型截图并做品牌中性化（输出到 /tmp，脚本内路径可改）
├── render_mermaid.py     把 JSON 里的 mermaid 渲染成 PNG（本地 Chrome，不外传内容）
├── parse_mermaid.py      解析 mermaid 源码 → flow_tables.json（泳道 / 节点 / 流转）
├── flow_tables.json      26 个模块的流程结构化数据
├── build_prd_docx.py     组装 Word（python-docx）
├── verify_docx.py        成品校验（结构 / 图片 / 品牌字样 / 字体 / 域）
└── verify_images_ocr.py  逐图 OCR 校验（图片里画出来的字也查）
```

## 事实层 JSON schema

每个模块一个 JSON，顶层字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `slug` | string | 模块唯一标识，同时是文件名与截图名 |
| `name` / `menu_path` | string | 模块中文名 / 菜单路径 |
| `purpose` | string | 一句话定位（30–60 字） |
| `pain_points` | array | `{problem, current, solution}` |
| `goals` | array | 可衡量口径（不写运行数值） |
| `roles` | array | `{role, dept, need}`，need 用「我要…以便…」句式 |
| `functions` | array | `{name, desc, rule}`，rule 必须可判断、可测试 |
| `entities` | array | `{name, key_fields[], relation}` |
| `flow_nodes` | array | 主流程步骤（有序） |
| `exceptions` | array | `{scene, handling}` |
| `pages` | array | `{name, file, entry, blocks, buttons, jump}`，file 必须是 pages/ 下真实存在的文件 |
| `permissions_note` | string | 权限与数据可见性口径 |
| `open_questions` | array | 待业务方确认项（统一以「待业务方确认：」开头） |
| `mermaid` | string | 流程图源码（flowchart LR），无则空串 |
| `screenshot_page` | string | 原型页面文件名（用于配图） |
| `evidence` | array | 实际读过的源文档路径 |

## 写作铁律

1. **不编造**：源文档没有的不推测，写进 `open_questions`
2. **裁决优先**：业务方裁决（D1–D18 / QA-xxx）优先于文档中的 ⚠️ 存疑与多套并列口径；未裁决项只记录不代答
3. **清除内部标记**：不出现 ✅ 🔷 ⚠️ [待补充] 与「源文档未写」等过程性表述
4. **品牌中性**：全文不得出现平台原品牌名，统一为「数字供应链」；企业名用中性名
5. **资金口径**：线下操作 + 凭证上传 + 系统内确认，不写线上扣款打款
6. **权限口径**：本期未划分角色权限、系统全量权限（裁决 D17），文档中的角色仅表示典型使用角色

## 流程图在 Word 里的处理规则

mermaid 泳道图横向展开后宽度可达 4000+ CSS px，**塞进 A4 竖版后字号只有 2–4pt，等于不可读**。因此：

- 估算图内 16px 字号嵌入 15.6cm 宽后的物理磅值
- **≥ 7pt** → 直接嵌图（图 4-x-1）
- **< 7pt** → 不嵌图，改为 Word 原生两张表：
  - 表 4-x-0 流程泳道：泳道（角色）| 步骤 | 节点内容 | 后继节点
  - 表 4-x-1 跨角色流转：发起方 | 动作 | 接收方 | 流转内容

表格可读、可编辑、可搜索，比压扁的图更适合 Word 分发。完整流程图仍保留在各模块的 Markdown 源文档与原型页面中。

## 品牌中性化的三道防线

1. **响应级改写**：所有文本类响应（含无扩展名的 HTML，如外部 BI 的 `/dashboard-command-center`）做字符串替换
2. **canvas 绘制拦截**：`fillText` / `strokeText` 传参替换（画布上的字）
3. **逐图 OCR 校验**：`verify_images_ocr.py` 对 Word 内嵌的每一张图做 OCR 并检索品牌词——这是最终硬标准，图片里画出来的字也能查出来

> 注意：注入脚本里的 MutationObserver 必须**只在值变化时写回**，否则自触发死循环会导致页面永远加载不出来。

## 重新生成

```bash
# 1) 抓原型截图（品牌中性化，输出 /Users/fuyu/.minimax/tmp/prd-modules/shots）
python3 capture_shots.py
# 2) 渲染 mermaid 流程图 + 解析流程结构
python3 render_mermaid.py
python3 parse_mermaid.py
# 3) 组装 Word
python3 build_docd_docx.py 2>/dev/null || python3 build_prd_docx.py
# 4) 校验（结构 + 逐图 OCR）
python3 verify_docx.py
python3 verify_images_ocr.py
```

## 校验口径

`verify_docx.py` 必须全绿才算通过：

- ZIP 完整性 OK
- 全部 XML/rels 无品牌字样（豫港通 / 中豫 / 港通 / 豫）
- Heading1 = 8（目录、1–5 章、附录 A/B），Heading2 含 29 个模块章，Heading3 = 29×8
- Normal eastAsia = 宋体，Heading 1–3 eastAsia = 黑体
- TOC 域、PAGE 域、NUMPAGES 域均存在
- 单节 + 首页不同（封面无页眉页脚）
- 无空表（仅表头）
