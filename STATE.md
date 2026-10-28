# 豫港通数字供应链管理平台 — 当前状态快照
最后更新: 2026-10-28 腾讯云轻量服务器（192.144.175.203）托管上线 + 本机一键部署脚本

## 当前部署
- **apex URL**: https://yugangtong-prototype.pages.dev/ (永远指向最新)
- **最新 hash**: 见 CF Pages 控制台 / `git log`（本文件不随站点发布，故不记 hash）
  - v1.15.0 起本文件已从部署产物中排除（`scripts/deploy_cf.sh`），避免内部工作笔记公开
- **CF API Token**: 不入库 —— 从环境变量 `CLOUDFLARE_API_TOKEN` 读取
  （v1.7.99.349.2 修正：此前 STATE.md 明文记录 token，触发 GitHub push protection 拦截）
- **部署命令**:
  ```
  CLOUDFLARE_API_TOKEN=<token> bash scripts/deploy_cf.sh
  ```
  ⚠️ **必须走 `scripts/deploy_cf.sh`，不能直接 `wrangler pages deploy .`**：
  脚本会先 rsync 出干净暂存目录（排除 `.git/` `.offline-build/` `.deploy_tmp/`
  `.prototype-flow/` `prd-library/` 等），把上传量从 685 文件/48MB 压到 ~350 文件/14MB，
  否则会触发 CF 429。
  （`--cwd` 必须带：父目录 workspace 下有别的项目的 wrangler.toml 含 `[assets]`，
   wrangler 4.x 会向上递归搜到并导致 "Configuration file for Pages projects
   does not support 'assets'"）

## Git
- 仓库: git@github.com:Ummyue/gyt-admin.git
- 最新 commit: `b0db217` (feat(receipt): v1.15.0 回款管理列表页补「回款列表」导航入口 + 删除「数据来源」筛选，已推送)
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

### 部署限流排查 + 暂存目录部署（2026-10-26）
**现象**：`wrangler pages deploy` 连续报 `POST /pages/assets/upload -> 429 Too Many Requests`，
换 token / 换代理 / 退避重试**全部无效**。

**根因**：① 本机代理客户端（127.0.0.1:7890）瞬时抽风；
② **`.offline-build/` 是整个站点的完整副本**（304 文件 / 28MB，含 4 组截图 + 离线包 + dist），
`wrangler pages deploy .` 传的是**整个目录**（含 gitignore 的构建产物），上传量 685 文件 / 48MB；
③ **失败的重试本身在消耗上传配额**，让限流窗口一直不恢复。

⚠️ **bash 变量名后紧跟全角标点 → 变量名被吞掉 → `set -u` 直接报错**：
`echo "（project=$PROJECT）"` 里的 `）` 是**全角括号**，在非 UTF-8 locale 下
bash 会把它的字节当成变量名的一部分 → 实际展开成 `$PROJECT\xef...` → 报
`PROJECT: unbound variable` → **脚本在跑 wrangler 之前就退出了**，
而输出里只看到「待上传 N 个文件」，极易误判成「部署了但没生效」。
**修法：变量后紧跟非 ASCII 字符一律用 `${VAR}` 界定边界。**
本项目 `scripts/deploy_cf.sh` 踩过 2 次（v1.12.0 / v1.13.0 均因此静默失败）。

⚠️ **脚本里的强删清理会被权限网关拦截 → 脚本非零退出 → 部署其实已发生，
但输出里只看得到「待上传 341 个文件」，极易误判成「没部署」**（v1.12.0 踩过一次，
线上 config 仍是旧的 27 条映射）。现已把清理改成可恢复删除且**清理失败不影响部署结果**，
脚本末尾加了提示。**每次部署后必须回线上核验文件内容，不能只看脚本输出。**

**修法**：新增 `scripts/deploy_cf.sh` —— 先 rsync 出「只含公开文件」的暂存目录（排除
`.git/` `.offline-build/` `.deploy_tmp/` `.prototype-flow/` `prd-library/` `local_tasks/`
`.work/` `.session-handoff/` `.wrangler/` `*.zip`），再从暂存目录部署。
上传量 **685 文件 / 48MB → 339 文件 / 11MB**。

⚠️ **`.assetsignore` 对 `wrangler pages deploy` 无效**（那是 Workers 静态资源的特性，
实测 Pages 忽略它）。文件保留但已注明；Pages 走暂存目录方案。

⚠️ **CF Pages 的资源存储是累积的**：新部署只上传本次的 339 个文件，
**上次部署里存在、本次没上传的路径仍会继续对外提供**（实测 `.offline-build/shots/` 仍 200）。
- 想彻底清掉 → 需要**删除并同名重建项目**（`pages.dev` 子域由项目名派生，URL 不变；
  token 已验证具备 create/delete 权限，用一次性项目验过）。
- **本项目未做**：删线上项目属不可逆动作，需 user 明确同意。
- 现状风险可控：站点本来就公开 `docs/` `docs-v2/`（含裁决记录），`prd-library/` 不算新增暴露类别；
  真正别扭的是 `.offline-build/dist/` 那份 v1.0.0 旧版站点副本可被猜到 URL 浏览。

⚠️ **CF Pages `_redirects` 不支持 404 重写**（官方文档：Rewrites (other status codes) ❌，
示例 `/blog/* /blog/404.html 404` 被明确标为不支持）→ 非破坏性封堵内部路径走不通，
只能靠「删项目重建」或「加 Pages Function 拦 404」。

**排查手法（下次直接用）**：
```bash
curl -s -D - -o /dev/null -H "Authorization: Bearer $TOKEN" https://api.cloudflare.com/client/v4/accounts | grep -iE "retry-after|ratelimit"
# error code: 1015 = Cloudflare 限流中
```
⚠️ **重试策略**：429 时**不要密集重试**（每次失败都在烧配额）——
先看 `retry-after` 头，**静默等待后再打一次**。密集重试会让窗口永远恢复不了。

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

### v1.19.0 项目立项新增「待上传决议文件」状态（2026-10-28）

user 截图标注三处改动：

| 改动 | 位置 | 内容 |
|---|---|---|
| 状态机新增状态 | `pages/project-list.html` | 「执行中」后、「已完结」前插入 **待上传决议文件**（紫 #7C3AED）→ 7 状态变 8 状态；页签计数 **执行中 76→68、新增 8、全部 156 不变**（口径：原执行中 76 个里有 8 个已流转到新环节） |
| 状态枚举数据 | 同上 | `PROJECT_MOCK` 新增 2 行（LX20260408017 / LX20260412018，`filePending: true`） |
| 该状态操作项 | 同上 | **查看**（`project-detail.html?no=..&status=待上传决议文件`，与「执行中」一致的详情页）/ **上传决议文件** |
| 上传弹窗参数化 | 同上 | `openUploadModal(no, fileType)` —— 标题与描述按类型切换；决议文件描述改「请上传经审批通过的决议文件…上传后项目进入「已完结」」。**原「上传客户准入报告」文案保持不变**（已回归验证） |
| 详情页新增节点 | `pages/project-detail.html` | 步骤 5「准入完成 · 关键信息」内，③ 准入完成·最终状态 **之后**新增 **④ 决议文件信息 · 最终状态**：文件名 + 大小/上传时间/上传人 + **查看** / **下载** |

文档：`docs/p-project-list.md`（旅程图/§3.4 状态 Tab/§4 状态机 mermaid/§5.1 状态色/§5.2 操作矩阵）、
`docs/p-project-detail.md`（新增 §5.6 节点说明 + §13 版本记录）、`docs/prd-build/modules/project-apply.json`（事实层）。

### 腾讯云轻量服务器部署（v1.18.0，2026-10-28）✅ 已上线

| 项 | 值 |
|---|---|
| 实例 | `Ubuntu-M5MG` / `lhins-aiyspy7i` / ap-beijing / **192.144.175.203** |
| 访问 | `http://192.144.175.203/`（域名未备案，只能 IP 直连） |
| 站点目录 | `/var/www/yugangtong`（303 个文件 / 14MB） |
| nginx | `/etc/nginx/conf.d/yugangtong.conf`（`server_name 192.144.175.203`） |
| 脚本 | `scripts/deploy_lighthouse_local.sh`（**本机跑**）+ `scripts/deploy_lighthouse.sh`（**服务器端跑**） |
| SSH | 本机私钥 `~/.ssh/id_lighthouse`，公钥已写入服务器 `~/.ssh/authorized_keys`（可用 `ssh-keygen -R`/删除该行撤销） |

**本机一条命令完成部署（以后更新就用它）**

```bash
bash scripts/deploy_lighthouse_local.sh
```

流程：本机按「对外发布口径」打包 → rsync 到服务器 → 服务器端脚本解包 → rsync 到站点目录
→ 写 nginx 配置 → `nginx -t` → reload → curl 自检。整轮约 40 秒。

**站点布局（福景堂原目录与原配置均未改动）**

| 路径 | 内容 |
|---|---|
| `http://192.144.175.203/` | 豫港通原型（新 server 块，server_name 匹配 IP） |
| `http://192.144.175.203/fjt/` | 福景堂站点（alias 挂载到 `/var/www/fujingtang`） |
| 其它 Host 头 | 仍命中 `fujingtang.conf` 的 `server_name _` |

⚠️ **备案完成后**：把域名追加到 `yugangtong.conf` 的 `server_name`（逗号分隔），
域名解析到本 IP；在此之前域名访问会被未备案监测拦截。

⚠️ **nginx server 块按 Host 头匹配**，本地自检必须带 `-H "Host: 192.144.175.203"`，
否则会落到 default server（福景堂）上，看���是「自己的」站点其实是福景堂。

### 本次踩坑（腾讯云 / OrcaTerm / 境内网络）

1. **境内服务器到 github.com 的 git 协议会挂死**
   clone 跑 11 分钟仍未建立连接（`/tmp/ygt-src` 连目录都没建出来）；
   而 `raw.githubusercontent.com` 是通的（脚本能 curl 下来）。
   → **部署改走「本机打包 + rsync」，服务器不 clone**。

2. **服务器是密码模式 SSH，本机密钥不匹配**
   免密通道只有控制台 OrcaTerm「免密连接（TAT）」。
   解决：用 OrcaTerm 的 **Monaco 命令面板**在服务器上写入本机公钥，之后本机就能直接 SSH。

3. **OrcaTerm 里怎么可靠地执行命令**
   - ❌ **xterm 终端里 `type` 会把字符重复发送**（`sudo` → `ssuuddoo`），
     且 `
` 不触发 Enter、右键「粘贴」走的是 OrcaTerm 的命令模板而不是系统剪贴板。
   - ✅ **底部 Monaco 命令面板**（`textarea.inputarea.monaco-mouse-cursor-text`）：
     `type` 进去字符零重复，用 `press_key` **Meta+Enter** 执行。
   - ⚠️ `press_key` **必须不带 `ref`**（带了就报 "Browser action failed in Electron main"）；
     带 `ref` 的 `type`/`fill` 在 xterm textarea 上无效。
   - ⚠️ 文件管理器面板打开时会把命令面板挤掉，Monaco 输入的内容会丢 —— 先关面板再操作。

4. **macOS 打包会带出 AppleDouble 垃圾文件**
   `tar -czf` 把扩展属性打成 `._xxx`（几百个），在 Linux 解出来就是垃圾。
   → 打包用 `COPYFILE_DISABLE=1` + `rsync --exclude='._*'`。

5. **rsync 的 `--exclude` 会保护目标端同名文件不被 `--delete` 删除**
   在服务端 rsync 里排除 `._*` → 那些垃圾文件会永远留在站点目录里删不掉。
   → 排除清单要干净：垃圾在**打包端**挡掉，服务端不放宽。

6. **bash 变量名后紧跟全角字符会被吞掉变量名**（`$HOST）` → `HOSTï...: unbound variable`）
   → 一律写 `${VAR}`。

7. **`USER` 是 bash 内置环境变量**（本地用户名），`USER="${USER:-ubuntu}"` 不会生效。
   → 用 `SSH_USER`。

### 腾讯云轻量服务器部署（v1.18.0 初始方案）

| 项 | 值 |
|---|---|
| 实例 | `Ubuntu-M5MG` / `lhins-aiyspy7i` / ap-beijing / **192.144.175.203** |
| 访问 | `http://192.144.175.203/`（域名未备案，只能 IP 直连） |
| 脚本 | `scripts/deploy_lighthouse.sh`（**服务器端执行**，一条命令完成全部） |

```bash
# 在服务器上执行（自动 clone + rsync + 写 nginx + reload + 自检）
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ummyue/gyt-admin/main/scripts/deploy_lighthouse.sh)"
```

**站点布局（不改动福景堂任何东西）**

| 路径 | 内容 |
|---|---|
| `/var/www/yugangtong` | 豫港通原型（本脚本部署） |
| `/var/www/fujingtang` | 福景堂站点（**目录与 `fujingtang.conf` 均未改动**） |
| `http://192.144.175.203/` | 豫港通（新 server 块，`server_name` 匹配 IP） |
| `http://192.144.175.203/fjt/` | 福景堂（alias 挂载） |
| 其它 Host 头 | 仍命中 `fujingtang.conf` 的 `server_name _` |

⚠️ **备案完成后**把域名追加到 `yugangtong.conf` 的 `server_name`（逗号分隔），
并把域名解析到本 IP；在此之前域名访问会被未备案监测拦截。

### CF Pages 部署 429 限流（2026-10-26 v1.17.0 部署时遇到）

本会话短时间内连续部署 6+ 次，Cloudflare API 开始返回 429：

| 现象 | `wrangler` 报 `GET /accounts -> 429 Too Many Requests`，或 `POST /pages/assets/upload -> 429`（带 `retryAfterMs`） |
|---|---|
| 绕过 /accounts 限流 | 设置 `CLOUDFLARE_ACCOUNT_ID=9bd52949bf6d4e023b94a32feaa72dd9`（可从 `~/Library/Preferences/.wrangler/logs/` 里 grep `"account_id":"..."` 拿到），wrangler 就不再调 `/accounts` |
| upload 限流 | 没有绕过办法，只能**按 `retryAfterMs` 退避后重试**（本次 retryAfterMs 给了 214000~255000，约 3.5~4.3 分钟） |
| 部署脚本 | `scripts/deploy_cf.sh` 本身没问题，限流是账号级配额；建议**同一小时内不要连续多次部署** |

⚠️ 排查顺序：先看报错是 `/accounts` 还是 `/pages/assets/upload` ——
前者加 `CLOUDFLARE_ACCOUNT_ID` 即可，后者只能等。

### v1.17.0 项目立项「业务负责人」改模糊搜索 + 修 chip × 点不动（2026-10-26）

**改动 1：业务负责人由单选下拉改为模糊搜索输入框**（user 截图标注）

| 项 | 内容 |
|---|---|
| 控件 | `<select>`（枚举 张爽/李建国/王慧敏/陈志远）→ `<input type="text" placeholder="模糊搜索业务负责人">` |
| 理由 | 人员名单来自用户中心且会增减，前端枚举会失真；改为文本模糊查询后与「企业名称」写法一致 |
| 页面 | `pages/project-list.html` |
| 文档 | `docs/p-project-list.md` §3.3 筛选区表（原本写成 7 字段且与原型脱节，本次按原型 10 字段逐项校准） |

⚠️ 全站只有项目立项这一处「业务负责人」下拉，其他页面无同类控件。

**改动 2：修 `shared/js/filter-chips.js` 的 chip「×」点不动（真 bug，影响 51 个页面）**

| 症状 | 先在输入框输内容 → chip 出现 → 点 chip 上的 ×，**无任何反应** |
|---|---|
| 根因 | 点 × 的 **mousedown** 让输入框失焦 → 触发 `change` → `renderChips()` 执行 `chipsContainer.innerHTML = ''` **整体重建** → 用户正要点的那个 × 节点在 mouseup/click 之前就被摘除 → click 落在**已分离节点**上不冒泡 → 事件丢失 |
| 修复 | `renderChips()` 改为**按筛选项下标做增量对齐**（键 = `data-filter-idx`）：只删多余 chip、只建缺失 chip、已有 chip 只更新取值；顺序不对才 `insertBefore` 归位 |
| 配套 | × 的点击改为**事件委托**到 `chipsContainer`，chip 节点即使重建也不丢监听器 |

⚠️ **关键坑：增量对齐里也不能无条件 `appendChild` 归位。**
`appendChild` / `insertBefore` 对已在容器里的节点 = 「移除 + 重新插入」，
mousedown 与 mouseup 之间移动节点会让浏览器判定 **mousedown 与 mouseup 目标不一致**
→ 不派发 click 事件（点击照样丢）。
必须**先判断顺序是否真的需要调整**，顺序正确时**完全不动 DOM**。

**影响面**：`shared/js/filter-chips.js` 被 **51 个列表页**引用（客户准入/项目立项/付款/退款/
回款/合同/发票/结算/仓储/报表/黑名单/审批监控等），此 bug 是**全站通用**的 ——
之前没人报是因为多数人不用鼠标点 chip 的 ×，或以为"筛选区本来就没实现过滤"。

### v1.16.0 审批监控页删「已触发审批提醒」KPI 卡（2026-10-26）
user 在监控页截图上红框标注删除第 4 张 KPI 卡「已触发审批提醒」。

| 改动 | 说明 |
|---|---|
| 删 KPI 卡 | `pages/approval-monitor.html` 删除「已触发审批提醒」卡（值 5）。KPI 由 4 张减为 3 张：审批实例总数 / 审批中 / 已通过 |
| 网格列数 | `.ap-kpi-row` 由 `repeat(4,1fr)` 改 `repeat(3,1fr)` —— 少一张卡不改列数会留一个空列 |
| JS 清理 | `renderKPI()` 里 `kpiRemind` 赋值、`REMINDS` mock（5 条）、`.ap-kpi.is-warn` 样式一并移除 |
| 文档收口 | `docs/p-approval-monitor.md` §3.1 / §9.1 / §10；`docs/02.17-审批管理-产品需求文档.md`（11 处，含 §1.2、§3、§4、§5、§6、§7.2、§7.3.2、§8.1）；`docs/prd-build/modules/approval.json` 事实层（desc / rule / blocks） |

⚠️ **提醒相关能力未被删**：编排页节点的「提醒规则」属性、监控页详情抽屉的
「提醒规则」字段与「立即催办」操作全部保留 —— 删的只是监控页上那张**统计卡**
（提醒触发量在监控页已无明细入口，单列统计卡无数据支撑）。

⚠️ **v1.14.0 的「留 KPI 删明细」判断已被 v1.16.0 推翻**：
v1.14.0 删「审批提醒记录」明细表时保留了 KPI 卡「已触发审批提醒」，
理由是「总量与明细不是同一层信息」。业务方最终选择连这张卡一并删除。
**这说明「删明细保留汇总」不是默认安全做法** —— 遇到同类精简，
汇总卡是否保留应由业务方定，不要自行保留。

### v1.15.0 回款管理列表页两项修正（2026-10-26）
user 截图标注：回款管理缺少列表页的导航菜单按钮 + 「数据来源」筛选可删除。

| 改动 | 说明 |
|---|---|
| 菜单补「回款列表」入口 | `topnav-drawer.js` 的「回款管理」children 原本只有 回款详情 / 回款审批详情 / 编辑回款，**唯独缺指向列表页的入口**。现为 回款列表 / 回款详情 / 回款审批详情 / 编辑回款，与「保证金管理 → 保证金明细」结构对齐 |
| 删「数据来源」筛选 | `pages/receipt-list.html` 筛选区删除该下拉（选项 OA同步 / 手工录入 / 银行同步），6 项减为 5 项（编号/回款方/收款账号/回款日期/回款方式）。该筛选**无 JS 过滤逻辑**，纯展示，删除安全 |
| 保留项 | 详情页顶栏的「数据来源」是**展示字段**（非筛选项），不动 |
| 文档 | `docs/p-receipt-list.md` 筛字段落改 5 项 + 追加 v1.15.0 版本记录 |

⚠️ **菜单层级是四级**：数字供应链 › 资金管理 › 回款管理 › 回款列表。
`TOPNAV_MENU` 是 **object**（7 个一级 key），不是数组；「回款管理」在「资金管理」的
`children` 里，「回款列表」在「回款管理」的 `children` 里 —— 查菜单必须**递归**，
只查一层会漏。

⚠️ **顶栏抽屉（v1.3 设计）只列二级菜单**，不展开三级/四级。
所以「回款列表」**永远不会出现在抽屉里**，它在**左侧菜单**里 —— 验证抽屉断言时
不要断言它含四级项。

### v1.14.0 审批流程监控页精简（2026-10-26）
user 要求删除「引用流程」筛选与「审批提醒记录」子功能模块。

| 改动 | 说明 |
|---|---|
| 删「引用流程（全部流程）」筛选器 | 实例列表**已有「引用流程」数据列**标明每条实例所属流程，无需重复按流程筛。筛选区剩 2 个：单据编号 + 应用模块 |
| 删「审批提醒记录」子模块 | 原为独立区块（8 列：单据编号/应用模块/卡在节点/提醒对象/提醒阈值/推送渠道/触发时间/状态）。**提醒触发总量保留在 KPI 卡「已触发审批提醒」** |
| 导出按钮改口径 | 筛选区「数据导出」原本导出的是提醒记录（`exportReminds`），改为导出**当前筛选下的审批实例记录**（`exportInstances`） |
| JS 清理 | `fltFlow` 初始化、`getFiltered` 里的 `fid` 过滤、`renderReminds()` 函数与其调用、`REMINDS` mock 渲染链路全部移除（`REMINDS` 数据保留供 KPI 计数） |

⚠️ ~~删「提醒记录」但留「提醒 KPI」是有意为之~~（**该判断已被 v1.16.0 推翻**）：
当时认为 KPI 卡「已触发审批提醒」统计的是提醒触发**总量**，明细表删掉后该数字仍有效。
业务方最终要求连这张卡一并删除，v1.16.0 已删除。

### v1.13.1 回款审批详情页按项目准入模板重做（2026-10-26）
user 给了图1，要求「审批页面按照项目准入中的模版呈现」。

**图1 实际是 `pages/project-detail.html` 的「审批详情」步骤（步骤 4）**，不是 project-apply 的
step4 —— 判据是节点名（①提交申请/②一级审批/③二级审批）与右上「刷新」按钮。
它用的是**页面自绘的 `.at-item` 时间线**（`design-system.css` 2357 行起），
**不是**通用引擎的 `.timeline` 渲染 —— 两者观感不同：
- 自绘 `.at-item`：绿勾圈/蓝时钟圈/灰圈 + 节点名 + 状态 tag + 审批人 + 意见框 + 耗时
- 引擎 `.timeline`：节点序号 + 节点类型 chip（发起/串行/会签，带色块）

**改法**：回款审批详情页的「审批管理」tab 整体按图1 重排 ——
顶部黄底状态条（`approval-status`）+ 左右两栏（1.6fr / 1fr）：
左「审批进度」卡（5 节点自绘时间线 + 刷新按钮）、右「关键指标 / 实时活动 / 催办」3 卡；
底部固定栏保留「审批通过 / 驳回审批」。**改为页面自绘，不再挂载通用引擎**，
故从 `APPROVAL_CONFIG_BY_PAGE` 移除 `receipt-approval-detail`（引擎的 14 个页保持不变）。

### v1.13.0 回款管理接入审批流 + 收发货移出应用范围（2026-10-26）
user 要求：① 收发货也没有审批功能；② 按付款管理状态机给回款管理补审批状态；
③ 各状态的操作项；④ 补做回款审批详情页（参考付款管理）。

| 改动 | 内容 |
|---|---|
| 回款状态维度 | 3 种（认领态）→ **7 种**：未认领/部分认领/已认领 + **待提交/审批中/驳回/无效** |
| 页签 | 4 个 → **8 个**：全部 → 待提交 → 审批中 → 未认领 → 部分认领 → 已认领 → 驳回 → 无效；计数按数据实时统计 |
| 行内操作 | 待提交 详情·修改·删除 / 审批中 详情·撤回 / 驳回 详情·修改·删除 / 无效 详情 / 认领态 详情·修改·删除 |
| 详情去向 | 审批态 → 新页 `receipt-approval-detail.html`；认领态 → 原 `receipt-detail.html` |
| 新页 | `pages/receipt-approval-detail.html`，流程 `highRisk`，结构照搬付款详情页（顶栏信息条 + 步骤条 + 3 tab + 引擎时间线 + 固定底栏） |
| 收发货 | 从「规划中」移出 → 目前没有应用审批流，移除 `shipment-out-detail` / `shipment-in-detail` 两条映射 |

⚠️ **顺带修掉左侧菜单的长期缺陷**（`shared/js/left-sidemenu.js`）：
- `getCurrentModule()` 原来只查到**第 3 层**（`subMenus` → `children`），
  而「回款管理」「保证金管理」是**第 4 层**（资金管理 → 回款管理 → 其子页），
  导致 回款详情 / 回款审批详情 / 编辑回款 / 保证金明细 等 **6 个页面左侧菜单全空**。
  改为**递归查找**。
- 渲染函数原来只画到三级子项，四级子项**根本没被画出来** → 改为递归渲染，
  新增 `.sidemenu-grandchild` 样式（再缩进一级）。
- 这是「61 页左侧菜单 0 项」里可由代码解决的那部分（其余 55 页是**未登记进
  TOPNAV_MENU**，属产品结构决策，未擅自动）。

### v1.12.0 应用范围口径纠正（2026-10-26）
user 指出：审批管理的「应用范围」描述有误 —— **业务线 / 发票 / 保证金模块目前没有应用审批流程**，
要求删掉对应描述并全量检查该模块需求文档。

**排查方法（可复用）**：用「**HTML 里声明了 + 浏览器实际加载了**」双向比对，
而不是只 grep 源码：
```python
# config 映射了 27 条，但其中 13 条指向的页面根本没引 approval-engine.js → 死映射
has_engine = "shared/js/approval-engine.js" in src
has_box    = bool(re.search(r'approvalTimeline_|class="timeline"|approval-timeline', src))
```

**结论**：实际渲染审批时间线的只有 **14 个引擎页** + **2 个自绘页**（project-detail / customer-detail，
用 `class="approval-timeline"` 页面内联实现，不读映射表）。

**文档纠正（docs/p-approval-flow-list.md §6）** —— 映射表重列 4 类：
| 分类 | 内容 |
|---|---|
| §6.1 已接入通用引擎（14 页） | 合同管理(6) / 付款 / 退款 / 追保函 / 项目准入(1) / 客户准入(1) / 货转(2) / 放货(1) |
| §6.2 页面自绘（2 页） | 项目详情 / 客户详情，不读 `APPROVAL_CONFIG_BY_PAGE` |
| §6.3 规划中（4 项） | 收发货 / 结算单 / 回款 / 运输合同 —— 映射保留，标注**页面尚未引入引擎** |
| §6.4 目前没有审批流（3 模块） | 业务线管理 / 发票管理 / 保证金管理 |

**代码同步**：`shared/js/approval-config.js` 删掉 4 条死映射
（`margin-adjust-detail` / `invoice-detail` / `invoice-out-detail` / `business-line-detail`），
其余 9 条规划中映射保留并加注释。映射 27 → 24 条。

**另外查出两处同类问题**：
- 监控页文档 §3.3 的「全部模块」筛选器写的是 8 项且名称全错，实际取自 `AE.APPLY_MODULES`（9 项）→ 已改
- **客户准入**：申请页已接 `highRisk`、详情页自绘，但**不在可勾选清单内**（`APPLY_MODULES` 9 项无此项），
  编排时无法把应用模块选为客户准入 → 已在文档 §6.5 记为待决，未擅自改清单（会动编排页 UI）

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
