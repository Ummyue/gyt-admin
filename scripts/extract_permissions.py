#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限配置项数据抽取器
====================
从 shared/js/topnav-drawer.js 的 window.TOPNAV_MENU 解析出
「一级菜单 → 二级菜单 → 三级菜单 → 页面」结构，
再逐页扫描该页面里的操作按钮（<button> / <a class="btn"> / 操作列链接），
输出供「角色权限管理」页使用的权限树 JSON。

用法:
    python3 scripts/extract_permissions.py            # 输出 JSON 到 stdout
    python3 scripts/extract_permissions.py -o out.json # 写文件
"""

import json
import os
import re
import sys
from datetime import datetime
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "pages")
MENU_JS = os.path.join(ROOT, "shared", "js", "topnav-drawer.js")
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 操作按钮 → 权限 scope（找不到就退化成 op<N>）
SCOPE_MAP = [
    (("查看", "详情", "查看报告", "查看补协", "补协详情", "入库明细", "出库明细", "货位",
      "监控信息", "列设置", "恢复默认", "查看状态机说明", "查看额度", "查看未关联业务线的合同(0)",
      "全部标记已读", "流程图预览"), "view"),
    (("新增", "新增立项申请", "新增客户", "新增黑名单企业", "新增补充协议", "登记保证金",
      "开具货转", "新增入库", "新增出库", "提货申请", "新增放货指令", "新增追保函",
      "新增发票", "新增合同", "新增付款", "新增退款", "新增回款", "新增采购结算单",
      "新增销售结算单", "新增仓房", "新增品类", "新增视频监控", "新增系统监控",
      "登记订单发货数据", "登记采购订单发运数据", "登记销售订单发运数据",
      "新增采购框架合同框架", "新增销售框架合同框架"), "create"),
    (("编辑", "修改", "设置等比例冲抵货款比例"), "edit"),
    (("删除", "批量删除"), "delete"),
    (("作废", "失效"), "void"),
    (("撤回", "撤回申请"), "withdraw"),
    (("提交", "确认提交", "确认收货", "确认上传", "确认删除", "确认进入", "发起完结", "重新提交"), "submit"),
    (("保存",), "save"),
    (("导出", "数据导出", "Excel 导出", "导出 Excel", "批量下载", "下载", "一键下载", "下载模板"), "export"),
    (("审批通过", "审核", "通过"), "approve"),
    (("驳回", "驳回审批"), "reject"),
    (("立即催办", "催办"), "urge"),
    (("上传", "+ 上传", "上传附件", "上传双签附件", "上传客户准入报告", "上传决议文件",
      "上传已生效单据", "↑ 上传上游货转"), "upload"),
    (("批量导入", "开始导入", "导入"), "import"),
    (("复制",), "copy"),
    (("打印",), "print"),
    (("发起货转", "↓ 新增下游货转", "+ 选择销售订单（贸易）合同"), "transfer"),
    (("查看货转",), "view-transfer"),
    (("按比例分摊", "全部现金"), "allocate"),
    (("替换",), "replace"),
    (("新增行",), "add-row"),
]


# ===== 人工审核剔除清单（v1.24.0，2026-11-09）=====
# user 逐项审核准入管理模块后确认：勾选的按钮 = 该模块应有的全部权限项，
# 未勾选的现存按钮属于噪音权限项，从权限配置项中删除。
# key = 菜单路径（与权限码里的路径一致），value = 要剔除的按钮名。
# 其他模块后续同样审核时，往这里加即可，不用改逻辑。
EXCLUDE_OPS = {
    # 图1：项目准入 15 项 → 保留 10 项（删 确认上传 / 全部标记已读 / 查看 / 替换 / 删除）
    "准入管理/项目准入": {
        "确认上传", "全部标记已读", "查看", "替换", "删除",
    },
    # 图2：客户准入 9 项 → 保留 6 项（删 查看状态机说明 / 查看额度 / 发起完结）
    "准入管理/客户准入": {
        "查看状态机说明", "查看额度", "发起完结",
    },
    # 图3：黑名单管理 7 项 → 保留 4 项（删 批量删除 / 下载模板 / 开始导入）
    "准入管理/黑名单管理": {
        "批量删除", "下载模板", "开始导入",
    },
    # 角色权限管理页自身：「全选 / 清空」是权限面板的工具条按钮，不是业务操作权限项
    "账户中心/企业管理/角色权限管理": {
        "全选", "清空",
    },
}


# ===== 真实系统菜单口径（v1.28.0，2026-11-09，user 提供线上截图）=====
# 权限配置树的**菜单结构与命名以真实系统为准**，与原型自身页面导航（TOPNAV_MENU）
# 不完全一致是正常的 —— 原型里账户中心只有 2 个占位页，真实系统是 6 个子菜单。

# 一）节点改名：真实系统里的叫法
MENU_RENAME = {
    "预警管理": "预警查询",
    "预警规则配置": "预警设置",
}

# 二）菜单结构重建：key = 一级菜单，value = {二级菜单: [三级菜单定义]}
#    ops 用 (按钮名, 权限scope) 二元组声明；不给 ops 但给 file 时仍按页面自动抽取
MENU_STRUCTURE_OVERRIDE = {
    "账户中心": {
        "个人管理": [
            {"label": "个人信息", "file": "account-personal.html", "ops": [
                ("编辑资料", "edit"), ("保存", "save"), ("上传头像", "upload"),
            ]},
            {"label": "安全设置", "ops": [
                ("修改登录密码", "update-password"), ("更换绑定手机号", "bind-phone"),
                ("更换绑定邮箱", "bind-email"), ("查看登录设备", "view-device"),
                ("退出其他设备", "logout-others"),
            ]},
        ],
        "企业管理": [
            {"label": "我的企业", "ops": [
                ("查看企业信息", "view"), ("编辑企业信息", "edit"),
                ("切换企业", "switch"), ("提交认证", "submit-cert"),
            ]},
            {"label": "企业账号管理", "ops": [
                ("新增账号", "create"), ("编辑账号", "edit"), ("删除账号", "delete"),
                ("重置密码", "reset-password"), ("分配角色", "assign-role"),
                ("启用账号", "enable"), ("停用账号", "disable"),
                ("审核入职申请", "approve"), ("审批邀请", "approve-invite"),
                ("导出账号列表", "export"),
            ]},
            {"label": "企业资料管理", "file": "account-company.html", "ops": [
                ("编辑企业资料", "edit"), ("上传资质文件", "upload"),
                ("替换附件", "replace"), ("删除附件", "delete"),
                ("提交审核", "submit"),
            ]},
            {"label": "密码管理", "ops": [
                ("修改密码策略", "edit-policy"), ("重置成员密码", "reset-password"),
                ("强制成员下线", "force-logout"),
            ]},
            # 原型新增页（真实系统截图里没有，属于企业级配置，挂在企业管理下）
            # 显式声明 ops：页面行内「删除」是 span 不是 a/button，自动抽取抓不到
            {"label": "角色权限管理", "file": "account-role-permission.html", "ops": [
                ("新增角色", "create"), ("保存", "save"),
                ("编辑该角色", "edit"), ("确认删除", "delete"),
            ]},
        ],
    },
}


def _slug(fname):
    """contract-purchase.html → contract-purchase"""
    return (fname or "").replace(".html", "")


# ===== 子节点并入（v1.25.0，2026-11-09）=====
# 「新增XXX」「编辑XXX」这类**新增/编辑页不是独立菜单**，而是所属业务列表页下的操作入口，
# 不该各占一个可勾选的菜单节点；它们的可访问性用右侧的「操作按钮权限」来管。
# key = 父菜单路径，value = {宿主菜单标签: [要并入的子菜单标签]}
# 并入后：宿主节点的操作权限 = 自身 ops + 被并入子节点的 ops（权限码保留各自原路径，不失效）
MERGE_CHILDREN = {
    # 合同管理：只保留 采购合同 / 销售合同 / 补充协议 三个可配置菜单
    "数字供应链/合同管理": {
        "采购合同": ["新增采购框架合同", "新增采购订单/单批次合同"],
        "销售合同": ["新增销售框架合同", "新增销售订单/单批次合同"],
        "补充协议": ["新增补协-框架合同", "新增补协-订单/单批次合同"],
    },
    # 资金管理/回款管理：只保留 回款列表；详情 / 审批详情 / 编辑页并入
    "数字供应链/资金管理/回款管理": {
        "回款列表": ["回款详情", "回款审批详情", "编辑回款"],
    },
    # 资金管理/保证金管理：只保留 保证金明细；调整 / 调整记录页并入
    "数字供应链/资金管理/保证金管理": {
        "保证金明细": ["保证金调整", "保证金调整记录"],
    },
    # 审批管理：只保留 审批流程配置 / 审批流程监控；编排画布是配置页的操作项
    "数字供应链/审批管理": {
        "审批流程配置": ["流程编排画布"],
    },
}


def _scope(text, idx):
    for keys, scope in SCOPE_MAP:
        if text in keys:
            return scope
    for keys, scope in SCOPE_MAP:
        for k in keys:
            if k and k in text:
                return scope
    return "op%d" % idx


def _build_ops(buttons, src_path, src_label=None):
    """构造某个页面的操作权限项。

    src_path  = 该按钮所属页面的菜单路径（用于生成权限码）
    src_label = 并入场景下的来源菜单标签（宿主菜单自己的按钮为 None）
    """
    used = set()
    out = []
    drop = EXCLUDE_OPS.get(src_path, set())
    for i, b in enumerate(buttons):
        scope = _scope(b, i + 1)
        if scope in used:
            scope = "%s%d" % (scope, i + 1)
        used.add(scope)
        # 被剔除的按钮不再产出权限项，但仍占用 scope 编号，
        # 这样其余按钮的权限码与剔除前完全一致（已保存角色的权限不会失效）
        if b in drop:
            continue
        op = {"label": b, "code": "%s#%s" % (src_path, scope)}
        if src_label:
            op["src"] = src_label
        out.append(op)
    return out


def _stamp(node, path, merged=None):
    """给菜单节点补 code / ops 明细。

    code 用「菜单路径」生成，保证可读且唯一：
        menu:数字供应链/合同管理/采购合同
    只有叶子节点（没有下级菜单）才挂操作按钮，
    中间层是纯目录，它的页面就是第一个子节点的落地页，重复列会让人困惑。

    merged = 被本节点吸收的子节点（新增页并入到宿主菜单）
    """
    node["code"] = "menu:" + path
    merged = merged or []

    raw_children = node.get("children") or []
    merge_map = MERGE_CHILDREN.get(path, {})
    consumed = set()
    child_merged = {}
    for host_label, labels in merge_map.items():
        for c in raw_children:
            if c["label"] in labels:
                child_merged.setdefault(host_label, []).append({
                    "label": c["label"],
                    "path": path + "/" + c["label"],
                    "buttons": c.get("buttons", []),
                })
                consumed.add(c["label"])

    kids = [c for c in raw_children if c["label"] not in consumed]
    node["children"] = kids          # ← 被并入的子节点要从树里移除，必须回写

    # 并入菜单的元信息（含它贡献了几个操作权限项）+ 它带的操作权限项
    merged_info = []
    merged_ops = []
    for m in merged:
        mops = _build_ops(m["buttons"], m["path"], m["label"])
        merged_info.append({
            "label": m["label"],
            "code": "menu:" + m["path"],
            "opCount": len(mops),
        })
        merged_ops.extend(mops)
    node["mergedMenus"] = merged_info

    if node.get("explicit_ops") is not None:
        # 真实系统菜单口径下显式声明的操作权限项
        used = set()
        ops = []
        for o in node["explicit_ops"]:
            scope = o[1]
            if scope in used:
                scope = "%s%d" % (scope, len(ops) + 1)
            used.add(scope)
            ops.append({"label": o[0], "code": "%s#%s" % (path, scope)})
        node["ops"] = ops + merged_ops
    elif kids:
        node["ops"] = []
    else:
        node["ops"] = _build_ops(node.get("buttons", []), path) + merged_ops

    for c in kids:
        _stamp(c, path + "/" + c["label"], child_merged.get(c["label"], []))

# 页面外壳（顶栏/分页/导航）按钮不算业务操作权限
CHROME_TEXT = {
    "版本变更记录", "查询", "重置", "刷新", "新建", "更多", "展开",
    "全部", "上一页", "下一页", "确定", "取消", "关闭", "返回",
}

# 明显属于页面外壳的元素 class
CHROME_CLASS_HINT = (
    "topbar", "pagination", "page-num", "breadcrumb", "sidemenu",
    "topnav", "pin-annotation", "chat-float", "ai-float",
)


# --------------------------------------------------------------------------
# 1. 解析 TOPNAV_MENU
# --------------------------------------------------------------------------
def parse_topnav_menu():
    """从 topnav-drawer.js 里抠出 window.TOPNAV_MENU = { ... }; 的字面量并求值。"""
    src = open(MENU_JS, encoding="utf-8").read()
    # 注意：文件头注释里也提到 window.TOPNAV_MENU，必须匹配「赋值 + {」的那一处
    m = re.search(r"window\.TOPNAV_MENU\s*=\s*\{", src)
    if not m:
        raise SystemExit("未在 %s 中找到 window.TOPNAV_MENU 定义" % MENU_JS)
    start = m.end() - 1
    depth = 0
    end = None
    for i in range(start, len(src)):
        c = src[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    literal = src[start:end]
    # JS 字面量 → Python：键统一加引号即可（值都是字符串/数组/对象）
    literal = re.sub(r"([{,]\s*)([A-Za-z_][\w\-]*)\s*:", r'\1"\2":', literal)
    literal = literal.replace("true", "True").replace("false", "False").replace("null", "None")
    # 去掉行尾注释
    literal = re.sub(r"//[^\n]*", "", literal)
    return eval(literal)  # noqa: S307 - 数据来自本仓库自有的静态文件


# --------------------------------------------------------------------------
# 2. 抽取页面里的操作按钮
# --------------------------------------------------------------------------
class ButtonScanner(HTMLParser):
    """收集 <button> / <a> 的可见文本，按 class 过滤掉页面外壳。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.buttons = []          # [(text, is_link, classes)]
        self._stack = []           # 当前未闭合的标签栈
        self._capture = None       # 正在收集文本的标签
        self._buf = []
        self._classes = ""
        self._is_link = False
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = a.get("class") or ""
        if self._skip_depth:
            self._skip_depth += 1
            return
        if tag in ("script", "style"):
            self._skip_depth = 1
            return
        # 图标/角标文字不是按钮文案（+ ico、desc 描述标签）
        if self._capture and re.search(r"\b(ico|desc|badge|caret)\b", classes):
            self._skip_depth = 1
            return
        if tag in ("button", "a"):
            self._stack.append(tag)
            self._capture = tag
            self._buf = []
            self._classes = classes
            self._is_link = (tag == "a")
            return
        if self._capture:
            self._stack.append(tag)

    def handle_endtag(self, tag):
        if self._skip_depth:
            self._skip_depth -= 1
            return
        if self._capture and tag == self._capture:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self.buttons.append((text, self._is_link, self._classes))
            self._capture = None
            self._buf = []
            self._classes = ""
            self._is_link = False
            self._stack = []
            return
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if self._capture and not self._skip_depth:
            self._buf.append(data)


JS_BTN_RE = re.compile(
    r"['\"]\s*<(button|a)\b[^>]*>(.*?)</\1\s*>",
    re.S,
)


def extract_js_buttons(html):
    """抓 script 里动态拼接的操作按钮（行内操作列就是这种）。"""
    out = []
    for m in JS_BTN_RE.finditer(html):
        inner = re.sub(r"<[^>]*>", "", m.group(2))
        inner = re.sub(r"\s+", " ", inner).strip()
        if inner:
            out.append(inner)
    return out


NOISE_EXACT = {
    "清除全部", "查看全部 →", "查看全部", "确认", "取消", "关闭", "确定",
    "<", ">", "×", "+ 新增行", "‹ 返回列表", "↩ 返回列表", "🔄 刷新", "刷新",
    "‹ 返回", "↩ 返回", "修改", "复制", "调整", "解冻", "冻结", "解除",
    "更多 ▾", "更多", "我知道了", "暂不关联",
}
NOISE_PREFIX = ("‹ ", "↩ ", "🔄 ", "业务线号：", "合同编号：", "回款凭证", "查看未关联")
NOISE_SUFFIX = (".pdf", ".PDF", ".jpg", ".jpeg", ".png", ".docx", ".xlsx", ".zip", "×", ">>")


def normalize(text):
    """'取 消' → '取消'（按钮文案常被 letter-spacing 拆开）。"""
    t = re.sub(r"(?<=[一-鿿])\s+(?=[一-鿿])", "", text)
    return t.strip()


def is_noise(text):
    if text in NOISE_EXACT:
        return True
    if "' +" in text or "+ '" in text:        # JS 拼接片段
        return True
    if any(text.startswith(p) for p in NOISE_PREFIX):
        return True
    if any(text.endswith(s) for s in NOISE_SUFFIX):
        return True
    if re.search(r"[：:]", text) and len(text) > 8:   # 数据标签不是按钮
        return True
    if re.fullmatch(r"[A-Za-z]{2,}[-–][A-Za-z0-9\-]{3,}", text):   # 单据号
        return True
    if re.fullmatch(r"[A-Z]{3,}[0-9]{6,}", text):                 # 业务号 SKYWX202607050001
        return True
    if re.fullmatch(r"[\d.\-/]{1,14}", text):
        return True
    if len(text) <= 2 and not re.fullmatch(r"[一-鿿]{2}", text):
        return True
    return False


def extract_buttons(html_path, menu_labels=None):
    """返回该页面去重后的操作按钮文本列表（保持出现顺序）。"""
    html = open(html_path, encoding="utf-8", errors="ignore").read()

    # 先整块剥掉页面外壳：顶栏 / 面包屑 / 左侧菜单容器 / 分页
    html = re.sub(r'<div class="topbar"[^>]*>.*?</div>\s*</div>', "", html, flags=re.S)
    html = re.sub(r'<div class="breadcrumb-inline"[^>]*>.*?</div>', "", html, flags=re.S)
    html = re.sub(r'<div class="sidemenu"[^>]*>.*?</div>', "", html, flags=re.S)
    html = re.sub(r'<div class="[^"]*pagination[^"]*"[^>]*>.*?</div>', "", html, flags=re.S)

    scanner = ButtonScanner()
    try:
        scanner.feed(html)
    except Exception:
        pass

    menu_labels = menu_labels or set()
    seen = set()
    out = []
    for text, is_link, classes in scanner.buttons + [(t, False, "") for t in extract_js_buttons(html)]:
        text = normalize(text)
        if not text or len(text) > 24:
            continue
        if any(hint in classes for hint in CHROME_CLASS_HINT):
            continue
        if text in CHROME_TEXT or text in menu_labels:
            continue
        if is_noise(text):
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


# --------------------------------------------------------------------------
# 3. 组装权限树
# --------------------------------------------------------------------------
def build_tree():
    menu = parse_topnav_menu()

    # 收集所有菜单标签（面包屑里会出现，需从按钮里剔除）
    menu_labels = set(menu.keys())
    for mod in menu.values():
        menu_labels.add(mod.get("label", ""))
        for sub in mod.get("subMenus", []):
            menu_labels.add(sub["label"])
            for ch in sub.get("children") or []:
                menu_labels.add(ch["label"])
                for g in ch.get("children") or []:
                    menu_labels.add(g["label"])

    def bt(fname):
        if not fname:
            return []
        p = os.path.join(PAGES_DIR, fname)
        if not os.path.exists(p):
            return []
        return extract_buttons(p, menu_labels)

    modules = []
    for mod_key, mod in menu.items():
        sub_menus = []
        for sub in mod.get("subMenus", []):
            children = sub.get("children") or []
            grand_children = []
            for ch in children:
                gchildren = ch.get("children") or []
                grand_children.append({
                    "label": MENU_RENAME.get(ch["label"], ch["label"]),
                    "file": ch.get("file", ""),
                    "buttons": bt(ch.get("file")),
                    "children": [
                        {
                            "label": MENU_RENAME.get(g["label"], g["label"]),
                            "file": g.get("file", ""),
                            "buttons": bt(g.get("file")),
                        }
                        for g in gchildren
                    ],
                })
            sub_menus.append({
                "label": MENU_RENAME.get(sub["label"], sub["label"]),
                "file": sub.get("file", ""),
                "buttons": bt(sub.get("file")),
                "children": grand_children,
            })

        # ===== 真实系统菜单口径：按截图重建该一级菜单的子树 =====
        override = MENU_STRUCTURE_OVERRIDE.get(mod.get("label"))
        if override:
            sub_menus = []
            for sub_label, spec in override.items():
                kids = []
                for k in spec:
                    fname = k.get("file", "")
                    kids.append({
                        "label": k["label"],
                        "file": fname,
                        "buttons": [] if k.get("ops") is not None else bt(fname),
                        "explicit_ops": k.get("ops"),
                        "children": [],
                    })
                sub_menus.append({
                    "label": sub_label,
                    "file": "",
                    "buttons": [],
                    "explicit_ops": None,
                    "children": kids,
                })
        modules.append({
            "key": mod_key,
            "label": mod.get("label", mod_key),
            "icon": mod.get("icon", ""),
            "subMenus": sub_menus,
        })
    return modules


def _patch_page_cachebust(out_js):
    """给引用权限树数据的页面 script src 打上 ?v=<内容hash>。

    浏览器会按 URL 缓存同名 js；nginx 改成 no-cache 之前，旧缓存条目在 7 天内
    不会重新校验 —— 用户会一直看到旧版权限树。带版本号 = 新 URL = 必定回源。
    """
    import hashlib
    page = os.path.join(ROOT, "pages", "account-role-permission.html")
    if not os.path.exists(page):
        return
    with open(out_js, "rb") as f:
        digest = hashlib.md5(f.read()).hexdigest()[:8]
    html = open(page, encoding="utf-8").read()
    new_html, n = re.subn(
        r'(src="\.\./shared/js/permission-tree\.js)(\?v=[^"]*)?(")',
        r'\1?v=' + digest + r'\3',
        html,
    )
    if n and new_html != html:
        with open(page, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("   页面 script src 已带版本号 ?v=%s" % digest)


if __name__ == "__main__":
    tree = build_tree()

    # 生成权限编码（菜单节点用菜单路径，操作按钮用 语义 scope）
    # ⚠️ _stamp 内部已递归子节点，这里**只能调一级**，否则会把合并结果覆盖掉
    for mod in tree:
        for sub in mod["subMenus"]:
            _stamp(sub, mod["label"] + "/" + sub["label"])

    if "-j" in sys.argv:
        out = sys.argv[sys.argv.index("-j") + 1]
        with open(out, "w", encoding="utf-8") as f:
            f.write("// 本文件由 scripts/extract_permissions.py 自动生成，请勿手工编辑\n")
            f.write("// 生成时间：%s\n" % NOW)
            f.write("// 用途：角色权限管理页的权限配置项（一/二/三级菜单 + 页面操作按钮）\n\n")
            f.write("window.PERMISSION_TREE = ")
            f.write(json.dumps(tree, ensure_ascii=False, indent=2))
            f.write(";\n")
        print("written -> %s" % out)
        _patch_page_cachebust(out)
    else:
        out = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else None
        data = json.dumps(tree, ensure_ascii=False, indent=2)
        if out:
            with open(out, "w", encoding="utf-8") as f:
                f.write(data)
            print(f"written -> {out}")
        else:
            print(data)
