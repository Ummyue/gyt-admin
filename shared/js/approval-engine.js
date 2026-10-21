// ===== 通用审批流程引擎 v1.1.0 =====
// 目标：把各业务模块硬编码的审批节点，抽象为「配置驱动 + 统一渲染」
// 能力：串行审批 / 并行会签（全部通过）/ 条件分支（金额阈值）
// 设计原则：
//   1. 配置与渲染分离 —— 配置是纯数据，渲染是纯函数
//   2. 零依赖 —— 不引第三方库，复用 assets/css/approval.css 的 timeline 样式
//   3. 可降级 —— 业务页面可通过 window.APPROVAL_CONFIG_BY_PAGE 覆盖默认配置
//   4. 无侵入 —— 业务页面只需 1 个容器 div + 1 行 mount()
//
// v1.1.0 变更（2026-10-15）：
//   · 节点 slaHours（审批时限）下线，改为 remind { enabled, afterHours } 提醒规则
//   · 节点 approvers 由「角色」改为「人员」（PEOPLE 目录，姓名 + 脱敏手机号）
//   · flow.applicableModules 改为 flow.applyModules，支持子模块级联
//   · 持久化 key 升到 v2（v1 结构不兼容，不做迁移）

(function (global) {
  'use strict';

  // ================================================================
  // 一、审批节点类型
  // ================================================================
  // v1.6.0：业务节点类型收敛为单一的「审批节点」。
  // 串行审批 / 并行会签不再是两个节点类型，而是审批节点上的 approveMode 二选一；
  // 原「条件分支」不再是独立节点类型，改为审批节点可选的触发条件 condition。
  const NODE_TYPE = {
    START: 'start',      // 提交申请（系统节点，不可编辑）
    APPROVAL: 'approval',// 审批节点（唯一业务节点类型）
    ARCHIVE: 'archive'   // 归档完成（系统节点，不可编辑）
  };

  /** 审批节点的审批方式（单个节点只能二选一） */
  const APPROVE_MODE = {
    SERIAL: 'serial',          // 串行审批：1 名审批人
    PARALLEL_ALL: 'parallel_all' // 并行会签：多人同时，全部通过才过
  };

  const APPROVE_MODE_LABEL = {
    serial: '串行审批',
    parallel_all: '并行会签'
  };

  /** 审批通知的推送渠道（v1.10.0；站内信恒开、不可关闭） */
  const NOTIFY_CHANNEL = {
    INBOX: 'inbox',  // 站内信：强制勾选，保证审批通知有留痕
    SMS: 'sms'       // 短信提醒：可选
  };

  const NOTIFY_CHANNEL_LABEL = {
    inbox: '站内信',
    sms: '短信提醒'
  };

  /** 渠道展示顺序（固定：站内信在前） */
  const NOTIFY_CHANNEL_ORDER = [NOTIFY_CHANNEL.INBOX, NOTIFY_CHANNEL.SMS];

  const NODE_STATUS = {
    DONE: 'done',
    REJECTED: 'rejected',
    CURRENT: 'current',
    PENDING: 'pending',
    SKIPPED: 'skipped'
  };

  // ================================================================
  // 二、平台人员目录（原型 Mock）
  // 说明：接入真实组织架构后，只需替换本表的数据来源
  // 隐私：手机号一律脱敏为「138 0000 XXXX」形式，不含真实号码
  // ================================================================
  const PEOPLE = {
    // 业务部
    u_biz_01: { id: 'u_biz_01', name: '张磊',   phone: '138 0000 XXXX', dept: '业务部',     post: '业务经理'   },
    u_biz_02: { id: 'u_biz_02', name: '李娜',   phone: '139 0000 XXXX', dept: '业务部',     post: '高级业务经理' },
    u_biz_03: { id: 'u_biz_03', name: '王浩',   phone: '137 0000 XXXX', dept: '业务部',     post: '业务专员'   },
    u_biz_04: { id: 'u_biz_04', name: '陈晨',   phone: '136 0000 XXXX', dept: '业务部',     post: '业务专员'   },
    // 风控部
    u_risk_01: { id: 'u_risk_01', name: '赵敏',   phone: '135 0000 XXXX', dept: '风控部',     post: '风控经理'   },
    u_risk_02: { id: 'u_risk_02', name: '孙丽',   phone: '134 0000 XXXX', dept: '风控部',     post: '风控专员'   },
    u_risk_03: { id: 'u_risk_03', name: '郑浩',   phone: '133 0000 XXXX', dept: '风控部',     post: '风控专员'   },
    // 财务部
    u_fin_01: { id: 'u_fin_01', name: '周涛',   phone: '138 0001 XXXX', dept: '财务部',     post: '财务经理'   },
    u_fin_02: { id: 'u_fin_02', name: '吴静',   phone: '139 0001 XXXX', dept: '财务部',     post: '财务主管'   },
    u_fin_03: { id: 'u_fin_03', name: '冯雪',   phone: '137 0001 XXXX', dept: '财务部',     post: '会计'       },
    // 法务部
    u_legal_01: { id: 'u_legal_01', name: '许文静', phone: '136 0001 XXXX', dept: '法务部',   post: '法务经理'   },
    u_legal_02: { id: 'u_legal_02', name: '何俊',   phone: '135 0001 XXXX', dept: '法务部',   post: '法务专员'   },
    // 仓储部
    u_wh_01: { id: 'u_wh_01', name: '马强',   phone: '134 0001 XXXX', dept: '仓储部',     post: '仓储经理'   },
    u_wh_02: { id: 'u_wh_02', name: '高倩',   phone: '133 0001 XXXX', dept: '仓储部',     post: '放货专员'   },
    // 总经理
    u_gm_01: { id: 'u_gm_01', name: '秦建国', phone: '138 0002 XXXX', dept: '总经理',     post: '总经理'     },
    // 运营管理部
    u_admin_01: { id: 'u_admin_01', name: '张爽', phone: '139 0002 XXXX', dept: '运营管理部', post: '系统管理员' }
  };

  function getPerson(id) {
    return (id && PEOPLE[id]) || null;
  }

  function listPeople(dept) {
    return Object.keys(PEOPLE)
      .map(k => PEOPLE[k])
      .filter(p => !dept || p.dept === dept);
  }

  /** 下拉展示文案：完整姓名 + 脱敏手机号 */
  function personLabel(id) {
    const p = getPerson(id);
    return p ? (p.name + '  ' + p.phone) : '—';
  }

  // ================================================================
  // 三、审批环节（roleKey）
  // 说明：环节只用于「条件分支指向」和「默认配色/默认人员」，
  //       实际审批人一律以节点上的 approver / approvers 为准
  // ================================================================
  const ROLES = {
    submitter:       { label: '提交申请', dept: '发起人',   color: '#64748B' },
    biz_manager:     { label: '业务审批', dept: '业务部',   color: '#2563EB', defaultPerson: 'u_biz_01'   },
    risk_manager:    { label: '风控审批', dept: '风控部',   color: '#7C3AED', defaultPerson: 'u_risk_01'  },
    finance_manager: { label: '财务审批', dept: '财务部',   color: '#059669', defaultPerson: 'u_fin_01'   },
    legal_review:    { label: '合规审查', dept: '法务部',   color: '#0891B2', defaultPerson: 'u_legal_01' },
    warehouse:       { label: '放货审批', dept: '仓储部',   color: '#EA580C', defaultPerson: 'u_wh_01'    },
    gm:              { label: '总经理审批', dept: '总经理', color: '#DC2626', defaultPerson: 'u_gm_01'    }
  };

  /** 取节点展示色：优先人员部门色 → 环节色 → 灰 */
  function nodeColorOf(node) {
    let p = node && node.approver ? getPerson(node.approver) : null;
    if (!p && node && node.approvers && node.approvers.length) p = getPerson(node.approvers[0]);
    if (p && DEPT_COLORS[p.dept]) return DEPT_COLORS[p.dept];
    if (node && node.roleKey && ROLES[node.roleKey]) return ROLES[node.roleKey].color;
    if (node && node.role && ROLES[node.role]) return ROLES[node.role].color;
    return '#64748B';
  }

  const DEPT_COLORS = {
    '业务部': '#2563EB',
    '风控部': '#7C3AED',
    '财务部': '#059669',
    '法务部': '#0891B2',
    '仓储部': '#EA580C',
    '总经理': '#DC2626',
    '运营管理部': '#64748B',
    '发起人': '#64748B'
  };

  // ================================================================
  // 四、应用模块（含子模块级联）
  // ================================================================
  // v1.5.0：去掉子项，应用模块全部平级（v1.4.0 及之前的
  // 合同管理 / 货转管理 / 结算单管理 曾带子项，本期需求已下线子项）
  // v1.11.0：新增「回款管理」（receipt），位置按产品菜单「资金管理」下
  // 付款管理 → 退款管理 → 回款管理 的相对顺序，插在退款管理之后
  const APPLY_MODULES = [
    { key: 'project',        label: '项目准入' },
    { key: 'contract',       label: '合同管理' },
    { key: 'goods_transfer', label: '货转管理' },
    { key: 'payment',        label: '付款管理' },
    { key: 'refund',         label: '退款管理' },
    { key: 'receipt',        label: '回款管理' },
    { key: 'settlement',     label: '结算单管理' },
    { key: 'bond_letter',    label: '追保函管理' },
    { key: 'release',        label: '放货管理' }
  ];

  function getModule(key) {
    for (var i = 0; i < APPLY_MODULES.length; i++) {
      if (APPLY_MODULES[i].key === key) return APPLY_MODULES[i];
    }
    return null;
  }

  /**
   * applyModules 归一化 → 纯 key 字符串数组。
   * v1.5.0 起 applyModules 不再有子项；此处兼容历史数据里的
   * { key, children } 写法（旧 localStorage 与 v1.4.0 模板），
   * 一律收敛成父级 key，避免调用方各处再判空。
   */
  function normModules(list) {
    if (!Array.isArray(list)) return [];
    const out = [];
    list.forEach(function (e) {
      const k = (typeof e === 'string') ? e : (e && e.key);
      if (k && out.indexOf(k) < 0) out.push(k);
    });
    return out;
  }

  /** applyModules 数组 → 展示文案 */
  function applyModulesText(list) {
    const keys = normModules(list);
    if (!keys.length) return '—';
    return keys.map(function (key) {
      const mod = getModule(key);
      return mod ? mod.label : key;
    }).join('、');
  }

  // ================================================================
  // 五、内置流程模板
  // ================================================================
  const DEFAULT_BRANCH_RULES = [
    { field: 'amount', operator: 'gt', value: 1000000, then: ['gm'] }
  ];

  const FLOW_TEMPLATES = {
    standard: {
      id: 'standard',
      name: '标准审批流程',
      desc: '发起 → 业务审批 → 风控+财务会签 →（金额 > 100 万加总经理）→ 完成',
      status: 'enabled',
      applyModules: ['project'],
      updatedAt: '2026-10-12 10:30',
      updatedBy: '张爽',
      nodes: [
        { id: 'n1', type: NODE_TYPE.START, name: '提交申请', roleKey: 'submitter' },
        { id: 'n2', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.SERIAL,
          name: '业务审批', roleKey: 'biz_manager',
          approver: 'u_biz_01', remind: { enabled: true, afterHours: 24 }, condition: [] },
        {
          id: 'n3', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.PARALLEL_ALL,
          name: '风控财务会签', roleKey: 'risk_manager',
          approvers: ['u_risk_01', 'u_fin_01'],
          remind: { enabled: true, afterHours: 48 },
          desc: '风控、财务全部通过才算通过'
        },
        // 原「金额分支」节点改为「总经理审批」节点 + 触发条件（金额 > 100 万才需要总经理审批）
        { id: 'n4', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.SERIAL,
          name: '总经理审批', roleKey: 'gm', approver: 'u_gm_01',
          remind: { enabled: true, afterHours: 24 }, condition: DEFAULT_BRANCH_RULES },
        { id: 'n5', type: NODE_TYPE.ARCHIVE, name: '归档完成' }
      ]
    },

    simple: {
      id: 'simple',
      name: '简易审批流程',
      desc: '发起 → 业务审批 → 财务审批 → 完成（适用小额单据）',
      status: 'enabled',
      applyModules: ['goods_transfer', 'release'],
      updatedAt: '2026-10-12 09:15',
      updatedBy: '李娜',
      nodes: [
        { id: 'n1', type: NODE_TYPE.START, name: '提交申请', roleKey: 'submitter' },
        { id: 'n2', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.SERIAL, name: '业务审批', roleKey: 'biz_manager',
          approver: 'u_biz_03', remind: { enabled: true, afterHours: 24 } },
        { id: 'n3', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.SERIAL, name: '财务审批', roleKey: 'finance_manager',
          approver: 'u_fin_02', remind: { enabled: true, afterHours: 48 } },
        { id: 'n4', type: NODE_TYPE.ARCHIVE, name: '归档完成' }
      ]
    },

    highRisk: {
      id: 'highRisk',
      name: '高风险审批流程',
      desc: '发起 → 业务审批 → 风控+财务会签 → 合规审查 → 总经理审批 → 完成',
      status: 'enabled',
      applyModules: ['contract', 'payment', 'refund', 'bond_letter'],
      updatedAt: '2026-10-11 17:40',
      updatedBy: '王浩',
      nodes: [
        { id: 'n1', type: NODE_TYPE.START, name: '提交申请', roleKey: 'submitter' },
        { id: 'n2', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.SERIAL, name: '业务审批', roleKey: 'biz_manager',
          approver: 'u_biz_02', remind: { enabled: true, afterHours: 12 } },
        {
          id: 'n3', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.PARALLEL_ALL,
          name: '风控财务会签', roleKey: 'risk_manager',
          approvers: ['u_risk_01', 'u_fin_01'],
          remind: { enabled: true, afterHours: 24 }
        },
        { id: 'n4', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.SERIAL,
          name: '合规审查', roleKey: 'legal_review',
          approver: 'u_legal_01', remind: { enabled: true, afterHours: 48 } },
        { id: 'n5', type: NODE_TYPE.APPROVAL, approveMode: APPROVE_MODE.SERIAL,
          name: '总经理审批', roleKey: 'gm',
          approver: 'u_gm_01', remind: { enabled: true, afterHours: 24 } },
        { id: 'n6', type: NODE_TYPE.ARCHIVE, name: '归档完成' }
      ]
    }
  };

  // ================================================================
  // 六、流程模板 CRUD（localStorage 持久化）
  // ================================================================
  const STORAGE_KEY = 'ygt_approval_flow_templates_v2';

  function loadAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') return parsed;
      }
    } catch (e) { /* 忽略：降级到内置模板 */ }
    return JSON.parse(JSON.stringify(FLOW_TEMPLATES));
  }

  function saveAll(all) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
      return true;
    } catch (e) {
      console.warn('[approval-engine] 持久化失败（可能是隐私模式）:', e);
      return false;
    }
  }

  function listFlows() {
    const all = loadAll();
    return Object.keys(all).map(k => withNormModules(all[k]));
  }

  function getFlow(id) {
    const f = loadAll()[id];
    return f ? withNormModules(f) : null;
  }

  /** 归一化单个流程的 applyModules */
  function withNormModules(flow) {
    if (!flow) return flow;
    flow.applyModules = normModules(flow.applyModules);
    return flow;
  }

  function saveFlow(flow) {
    const all = loadAll();
    all[flow.id] = Object.assign({}, withNormModules(Object.assign({}, flow)), {
      updatedAt: nowStr(),
      updatedBy: '张爽'
    });
    saveAll(all);
    return all[flow.id];
  }

  function deleteFlow(id) {
    const all = loadAll();
    if (!all[id]) return false;
    delete all[id];
    saveAll(all);
    return true;
  }

  function duplicateFlow(id, newName) {
    const src = getFlow(id);
    if (!src) return null;
    const newId = 'flow_' + Date.now();
    const suffix = Date.now().toString().slice(-4);
    return saveFlow(Object.assign({}, JSON.parse(JSON.stringify(src)), {
      id: newId,
      name: newName || (src.name + ' - 副本'),
      status: 'draft',
      applyModules: normModules(src.applyModules),
      nodes: src.nodes.map(n => Object.assign({}, n, { id: n.id + '_' + suffix }))
    }));
  }

  function nowStr() {
    const d = new Date();
    const p = n => String(n).padStart(2, '0');
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' +
           p(d.getHours()) + ':' + p(d.getMinutes());
  }

  // ================================================================
  // 七、条件分支求值
  // ================================================================
  const OPERATORS = {
    gt:  (a, b) => Number(a) >  Number(b),
    gte: (a, b) => Number(a) >= Number(b),
    lt:  (a, b) => Number(a) <  Number(b),
    lte: (a, b) => Number(a) <= Number(b),
    eq:  (a, b) => String(a) === String(b),
    ne:  (a, b) => String(a) !== String(b)
  };

  const OP_LABELS = { gt: '>', gte: '≥', lt: '<', lte: '≤', eq: '=', ne: '≠' };

  const FIELD_LABELS = {
    amount: '单据金额', bizType: '业务类型', contractType: '合同类型',
    customerLevel: '客户等级', riskLevel: '风险等级'
  };

  /**
   * 通知渠道展示文案（v1.10.0）→ 「（站内信、短信提醒）」
   * 空数组视为仅站内信 —— normNode 已保证 inbox 恒在，这里兜住未归一化的直接调用。
   */
  function notifyChannelsText(list) {
    var arr = Array.isArray(list) && list.length ? list : [NOTIFY_CHANNEL.INBOX];
    var labels = NOTIFY_CHANNEL_ORDER
      .filter(function (c) { return arr.indexOf(c) >= 0; })
      .map(function (c) { return NOTIFY_CHANNEL_LABEL[c]; });
    return labels.length ? '（' + labels.join('、') + '）' : '';
  }

  /**
   * 节点归一化 → v1.6.0 模型（start / approval / archive）。
   * 兼容三代历史数据：
   *   serial          → approval + approveMode:'serial'
   *   parallel_all    → approval + approveMode:'parallel_all'
   *   serial+auto     → archive
   *   branch          → 按 condition[].then 里的角色展开成多个 approval 节点
   *                     （每个角色一个节点，继承同一条触发条件）
   * 同时清掉 condition[].then（新模型里条件只负责「是否执行」，不再指定追加角色）。
   */
  function normNode(node) {
    if (!node) return node;
    const n = Object.assign({}, node);

    if (n.type === 'branch') {
      const rules = (n.condition || []).map(r => ({
        field: r.field, operator: r.operator, value: r.value
      }));
      const roleKeys = [];
      (n.condition || []).forEach(r => (r.then || []).forEach(k => { if (roleKeys.indexOf(k) < 0) roleKeys.push(k); }));
      if (!roleKeys.length) return null;                 // 没有 then 角色的分支节点直接丢弃
      return roleKeys.map(roleKey => {
        const meta = ROLES[roleKey] || { label: roleKey, dept: '—', color: '#64748B' };
        return {
          id: n.id + '_' + roleKey,
          type: NODE_TYPE.APPROVAL,
          approveMode: APPROVE_MODE.SERIAL,
          name: meta.label,
          roleKey: roleKey,
          role: meta.label,
          approver: meta.defaultPerson || null,
          remind: { enabled: true, afterHours: 24 },
          condition: rules
        };
      });
    }

    if (n.auto || n.type === 'serial' || n.type === NODE_TYPE.ARCHIVE) {
      // 归档节点（历史上是 serial + auto:true）
      const isArchive = !!n.auto || n.type === NODE_TYPE.ARCHIVE ||
                        (n.type === 'serial' && n.roleKey === 'system');
      if (isArchive) return { id: n.id, type: NODE_TYPE.ARCHIVE, name: n.name || '归档完成' };
    }

    if (n.type === 'parallel_all') {
      n.type = NODE_TYPE.APPROVAL;
      n.approveMode = APPROVE_MODE.PARALLEL_ALL;
      if (!n.approvers) n.approvers = [];
      n.condition = [];        // 并行会签不支持触发条件（v1.8.0）
    } else if (n.type === NODE_TYPE.START || n.type === 'start') {
      n.type = NODE_TYPE.START;
    } else {
      n.type = NODE_TYPE.APPROVAL;
      n.approveMode = APPROVE_MODE.SERIAL;
    }

    if (Array.isArray(n.notify)) n.notify = n.notify.filter(Boolean);
    else if (n.notify == null) n.notify = [];

    // 通知渠道（v1.10.0）：站内信恒在，其余只认 inbox/sms，去重并按固定顺序
    if (!Array.isArray(n.notifyChannels)) n.notifyChannels = [];
    var chSet = {};
    n.notifyChannels.forEach(function (c) { if (c === NOTIFY_CHANNEL.SMS) chSet[NOTIFY_CHANNEL.SMS] = 1; });
    chSet[NOTIFY_CHANNEL.INBOX] = 1;   // 站内信强制保留，前端绕过也会被这层兜住
    n.notifyChannels = NOTIFY_CHANNEL_ORDER.filter(function (c) { return chSet[c]; });

    if (Array.isArray(n.condition)) {
      n.condition = n.condition.map(r => ({ field: r.field, operator: r.operator, value: r.value }));
    } else if (n.condition == null) {
      n.condition = [];
    }
    return n;
  }

  /** 流程归一化：节点数组展开（旧 branch 会变成多个节点） */
  function normFlow(flow) {
    if (!flow) return flow;
    const nodes = [];
    (flow.nodes || []).forEach(n => {
      const r = normNode(n);
      if (Array.isArray(r)) { r.forEach(x => nodes.push(x)); }
      else if (r) nodes.push(r);
    });
    return Object.assign({}, flow, { nodes: nodes });
  }

  function evalBranch(node, formData) {
    if (!node.condition || !node.condition.length) return { matched: false, rules: [] };
    const rules = node.condition.map(r => {
      const fn = OPERATORS[r.operator];
      const actual = formData ? formData[r.field] : undefined;
      const matched = fn ? fn(actual, r.value) : false;
      const thenList = (r.then && Array.isArray(r.then)) ? r.then : [];
      const thenLabels = thenList.map(k => (ROLES[k] ? ROLES[k].label : k));
      return {
        field: r.field,
        fieldLabel: FIELD_LABELS[r.field] || r.field,
        operator: r.operator,
        opLabel: OP_LABELS[r.operator] || r.operator,
        value: r.value,
        actual: actual === undefined ? '—' : actual,
        matched: matched,
        then: thenList,
        thenLabels: thenLabels,
        text: (FIELD_LABELS[r.field] || r.field) + ' ' + (OP_LABELS[r.operator] || r.operator) + ' ' + r.value
      };
    });
    return { matched: rules.some(r => r.matched), rules: rules };
  }

  /**
   * 展开流程为「实际执行的节点序列」（条件分支在这里被求值）
   */
  function resolveFlow(flow, formData) {
    const out = [];
    normFlow(flow).nodes.forEach(raw => {
      const node = Object.assign({}, raw);
      const rules = node.condition || [];

      // 审批节点带触发条件：任一条命中才执行，全部不命中则跳过本节点
      if (node.type === NODE_TYPE.APPROVAL && rules.length) {
        const res = evalBranch({ condition: rules }, formData);
        if (!res.matched) {
          out.push(Object.assign({}, node, {
            skipped: true,
            status: NODE_STATUS.SKIPPED,
            branchRules: res.rules,
            conditionText: res.rules.map(r => r.text).join(' 或 ')
          }));
          return;
        }
        node.conditionMatched = res.rules.filter(r => r.matched).map(r => r.text);
        node.branchRules = res.rules;
      }

      out.push(Object.assign({}, node, { status: node.status || NODE_STATUS.PENDING }));
    });
    return out;
  }

  /** 取节点当前审批人（串行 → 单人；会签 → 多人） */
  function nodeApprovers(node) {
    if (!node || node.type !== NODE_TYPE.APPROVAL) return [];
    if (node.approveMode === APPROVE_MODE.PARALLEL_ALL) {
      return (node.approvers || []).map(getPerson).filter(Boolean);
    }
    const p = getPerson(node.approver);
    return p ? [p] : [];
  }

  // ================================================================
  // 八、渲染器
  // ================================================================
  const CIRCLED = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩'];

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtAmount(v) {
    const n = Number(v);
    if (isNaN(n)) return String(v);
    return n.toLocaleString('zh-CN');
  }

  function maskPhone(phone) {
    return phone || '—';
  }

  function renderTimeline(opts, bare) {
    const o = opts || {};
    const flow = o.flow || getFlow('standard');
    const nodes = resolveFlow(flow, o.formData || {});
    const currentIdx = o.currentIdx == null ? -1 : o.currentIdx;

    let html = bare ? '' : '<div class="timeline">';

    nodes.forEach((node, i) => {
      const isStart = node.type === NODE_TYPE.START;
      const isBranchSkipped = node.skipped;
      let status = node.status || NODE_STATUS.PENDING;
      if (!isBranchSkipped) {
        if (i < currentIdx) status = NODE_STATUS.DONE;
        else if (i === currentIdx) status = NODE_STATUS.CURRENT;
        else status = NODE_STATUS.PENDING;
      }
      const meta = ROLES[node.roleKey || node.role] ||
                   { label: node.role || '—', dept: node.dept || '—', color: '#64748B' };
      const idx = CIRCLED[i] || (i + 1);

      html += '<div class="timeline-item ' + status + '" data-node-id="' + esc(node.id) + '">';
      html += '  <div class="timeline-dot"><span class="timeline-dot-num">' + idx + '</span></div>';
      html += '  <div class="timeline-content">';
      html += '    <div class="timeline-title">' + esc(node.name || meta.label);

      // 类型 chip
      if (node.type === NODE_TYPE.START) {
        html += ' <span class="chip chip-gray">发起</span>';
      } else if (node.type === NODE_TYPE.ARCHIVE) {
        html += ' <span class="chip chip-gray">归档</span>';
      } else if (node.type === NODE_TYPE.APPROVAL) {
        html += node.approveMode === APPROVE_MODE.PARALLEL_ALL
          ? ' <span class="chip chip-gray">会签</span>'
          : ' <span class="chip chip-gray">串行</span>';
        if (node.conditionMatched && node.conditionMatched.length) {
          html += ' <span class="chip chip-blue">条件命中</span>';
        }
      }

      // 状态 chip
      if (status === NODE_STATUS.DONE)          html += ' <span class="chip chip-green">已通过</span>';
      else if (status === NODE_STATUS.CURRENT)  html += ' <span class="chip chip-orange">进行中</span>';
      else if (status === NODE_STATUS.PENDING)  html += ' <span class="chip chip-gray">待开始</span>';
      else if (status === NODE_STATUS.SKIPPED)  html += ' <span class="chip chip-gray">已跳过</span>';

      html += '  </div>';

      // 串行审批节点：审批人员（姓名 + 脱敏手机号）
      if (node.type === NODE_TYPE.APPROVAL && node.approveMode === APPROVE_MODE.SERIAL) {
        const p = getPerson(node.approver);
        if (p) {
          html += '    <div class="timeline-subitem">';
          html += '      <div class="timeline-subitem-header">';
          html += '        <div class="timeline-subitem-name">';
          html += '          <div class="avatar" style="background:' + (DEPT_COLORS[p.dept] || '#64748B') + ';">' + esc(p.name.charAt(0)) + '</div>';
          html += '          <span><strong>' + esc(p.name) + '</strong> · ' + esc(maskPhone(p.phone)) + ' · ' + esc(p.dept) + '</span>';
          html += '        </div>';
          html += '        <span class="chip ' + (status === NODE_STATUS.DONE ? 'chip-green' : (status === NODE_STATUS.CURRENT ? 'chip-orange' : 'chip-gray')) + '">' +
                  (status === NODE_STATUS.DONE ? '已通过' : (status === NODE_STATUS.CURRENT ? '审批中' : '待审批')) + '</span>';
          html += '      </div>';
          html += '    </div>';
        }
      }

      // 并行会签节点：子审批人
      if (node.type === NODE_TYPE.APPROVAL && node.approveMode === APPROVE_MODE.PARALLEL_ALL) {
        nodeApprovers(node).forEach(p => {
          const aStatus = status === NODE_STATUS.DONE ? '已通过' : (status === NODE_STATUS.CURRENT ? '审批中' : '待审批');
          const aCls = status === NODE_STATUS.DONE ? 'chip-green'
                     : (status === NODE_STATUS.CURRENT ? 'chip-orange' : 'chip-gray');
          html += '    <div class="timeline-subitem">';
          html += '      <div class="timeline-subitem-header">';
          html += '        <div class="timeline-subitem-name">';
          html += '          <div class="avatar" style="background:' + (DEPT_COLORS[p.dept] || '#64748B') + ';">' + esc(p.name.charAt(0)) + '</div>';
          html += '          <span><strong>' + esc(p.name) + '</strong> · ' + esc(maskPhone(p.phone)) + ' · ' + esc(p.dept) + '</span>';
          html += '        </div>';
          html += '        <span class="chip ' + aCls + '">' + aStatus + '</span>';
          html += '      </div>';
          html += '    </div>';
        });
      }

      // 触发条件说明
      if (node.type === NODE_TYPE.APPROVAL && node.conditionText) {
        html += '    <div class="timeline-meta"><span>触发条件：' + esc(node.conditionText) + '</span></div>';
      }
      if (isBranchSkipped && node.branchRules && node.branchRules.length) {
        html += '    <div class="timeline-meta"><span>条件未命中，已跳过（' +
                esc(node.branchRules.map(r => r.text + ' → 实际 ' + r.actual).join('；')) + '）</span></div>';
      }

      // 审批通知（v1.8.0）：本节点通过后通知的人员；v1.10.0 追加推送渠道
      if (node.type === NODE_TYPE.APPROVAL && node.notify && node.notify.length && status !== NODE_STATUS.SKIPPED) {
        const names = node.notify.map(id => { const p = getPerson(id); return p ? p.name : id; });
        html += '    <div class="timeline-meta"><span>🔔 审批通过后通知：' + esc(names.join('、')) +
                notifyChannelsText(node.notifyChannels) + '</span></div>';
      }

      // 提醒规则（v1.1.0：替代原「审批时限」）
      if (node.remind && node.remind.enabled && node.remind.afterHours && status !== NODE_STATUS.SKIPPED) {
        html += '    <div class="timeline-meta"><span>⏰ 未处理满 ' + node.remind.afterHours + ' 小时将发送审批提醒</span></div>';
      }

      html += '  </div>';
      html += '</div>';
    });

    html += bare ? '' : '</div>';
    return html;
  }

  function renderFlowChain(flow, formData) {
    const nodes = resolveFlow(flow, formData || {});
    let html = '<div class="afc-chain">';
    nodes.forEach((n, i) => {
      const isSkip = n.skipped;
      const color = nodeColorOf(n);
      html += '<div class="afc-node' + (isSkip ? ' is-skipped' : '') + '" style="--node-color:' + color + '">';
      html += '  <div class="afc-node-no">' + (CIRCLED[i] || (i + 1)) + '</div>';
      html += '  <div class="afc-node-name">' + esc(n.name || '—') + '</div>';
      const ps = nodeApprovers(n);
      html += '  <div class="afc-node-role">' +
              (ps.length ? esc(ps.map(p => p.name).join('、')) : esc(ROLES[n.roleKey] ? ROLES[n.roleKey].dept : '—')) +
              '</div>';
      if (n.type === NODE_TYPE.APPROVAL && n.approveMode === APPROVE_MODE.PARALLEL_ALL) {
        html += '  <div class="afc-node-tag">会签 ' + ps.length + ' 人</div>';
      }
      if (n.conditionMatched && n.conditionMatched.length) html += '  <div class="afc-node-tag is-blue">条件命中</div>';
      if (isSkip)        html += '  <div class="afc-node-tag is-gray">已跳过</div>';
      html += '</div>';
      if (i < nodes.length - 1) {
        html += '<div class="afc-arrow"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></div>';
      }
    });
    html += '</div>';
    return html;
  }

  // ================================================================
  // 九、业务页面接入 API
  // ================================================================
  /**
   * 页面级配置覆盖表：pageName -> flowId
   * 必须动态读取 global，而不是在 IIFE 执行时快照 —— 页面 script 顺序
   * 可能把引擎排在映射表之前，快照会永久捕获空对象。
   */
  function configByPage(pageName) {
    var map = global.APPROVAL_CONFIG_BY_PAGE;
    return (map && map[pageName]) || null;
  }
  function amountConfig() {
    return global.APPROVAL_AMOUNT_CONFIG || {};
  }

  function detectAmount(pageName) {
    const explicit = document.querySelector('[data-approval-amount]');
    if (explicit) {
      const v = Number(String(explicit.getAttribute('data-approval-amount') || '').replace(/[^\d.]/g, ''));
      if (!isNaN(v) && v > 0) return v;
    }
    try {
      const q = new URLSearchParams(location.search).get('amount');
      if (q && !isNaN(Number(q))) return Number(q);
    } catch (e) { /* ignore */ }
    var AMOUNT_CFG = amountConfig();
    const sels = AMOUNT_CFG.defaultSelectors || [];
    for (let i = 0; i < sels.length; i++) {
      const el = document.querySelector(sels[i]);
      if (!el) continue;
      const raw = el.value != null && el.value !== '' ? el.value : el.textContent;
      const v = Number(String(raw || '').replace(/[^\d.]/g, ''));
      if (!isNaN(v) && v > 0) {
        const mult = (AMOUNT_CFG.unitMultiplier || {})[pageName];
        return mult ? v * mult : v;
      }
    }
    return undefined;
  }

  function mount(selector, opts) {
    const el = typeof selector === 'string' ? document.querySelector(selector) : selector;
    if (!el) { console.warn('[approval-engine] 容器未找到:', selector); return; }
    const o = Object.assign({}, opts || {});
    const pageName = (location.pathname.split('/').pop() || '').replace(/\.html$/i, '');
    if (!o.flow) {
      const flowId = o.flowId || configByPage(pageName) || 'standard';
      o.flow = getFlow(flowId) || getFlow('standard');
    }
    if (!o.formData) o.formData = {};
    if (o.formData.amount == null) {
      const amt = detectAmount(pageName);
      if (amt != null) o.formData.amount = amt;
    }
    if (!o.currentIdx && o.currentIdx !== 0) o.currentIdx = detectCurrentIdx(el, o);
    const bare = el.classList && el.classList.contains('timeline');
    el.innerHTML = renderTimeline(o, bare);
  }

  function detectCurrentIdx(container, opts) {
    const items = container.querySelectorAll('.timeline-item');
    for (let i = 0; i < items.length; i++) {
      if (items[i].classList.contains('current')) return i;
      if (items[i].classList.contains('rejected')) return i;
    }
    return opts && opts.allDone ? items.length - 1 : -1;
  }

  // ================================================================
  // 十、导出
  // ================================================================
  global.ApprovalEngine = {
    // 常量
    NODE_TYPE, NODE_STATUS, APPROVE_MODE, APPROVE_MODE_LABEL,
    NOTIFY_CHANNEL, NOTIFY_CHANNEL_LABEL, NOTIFY_CHANNEL_ORDER, notifyChannelsText,
    ROLES, OPERATORS, OP_LABELS, FIELD_LABELS,
    DEPT_COLORS, APPLY_MODULES, PEOPLE,
    // 人员
    getPerson, listPeople, personLabel, nodeApprovers,
    // 模块
    getModule, applyModulesText, normModules,
    normNode, normFlow,
    // 流程 CRUD
    listFlows, getFlow, saveFlow, deleteFlow, duplicateFlow,
    // 求值
    evalBranch, resolveFlow,
    // 渲染
    renderTimeline, renderFlowChain,
    // 接入
    mount, detectAmount,
    // 工具
    nowStr, esc, fmtAmount, maskPhone, CIRCLED, nodeColorOf
  };

})(window);
