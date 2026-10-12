// ===== 通用审批流程引擎 v1.0.0 =====
// 目标：把各业务模块硬编码的审批节点，抽象为「配置驱动 + 统一渲染」
// 能力：串行审批 / 并行会签（全部通过）/ 条件分支（金额阈值）
// 设计原则：
//   1. 配置与渲染分离 —— 配置是纯数据（FLOW_TEMPLATES），渲染是纯函数
//   2. 零依赖 —— 不引第三方库，复用 assets/css/approval.css 的 timeline 样式
//   3. 可降级 —— 业务页面可通过 window.APPROVAL_CONFIG_BY_PAGE 覆盖默认配置
//   4. 无侵入 —— 业务页面只需 1 行 <script> + 1 个容器 div

(function (global) {
  'use strict';

  // ================================================================
  // 一、审批节点类型
  // ================================================================
  const NODE_TYPE = {
    START: 'start',        // 发起（系统自动）
    SERIAL: 'serial',      // 串行审批：单人依次审批
    PARALLEL_ALL: 'parallel_all', // 并行会签：全部通过才过
    BRANCH: 'branch'       // 条件分支：按条件走不同路径
  };

  const NODE_STATUS = {
    DONE: 'done',          // 已通过
    REJECTED: 'rejected',  // 已驳回
    CURRENT: 'current',    // 进行中
    PENDING: 'pending',    // 待开始
    SKIPPED: 'skipped'     // 已跳过（条件不满足）
  };

  // ================================================================
  // 二、审批角色字典（可扩展）
  // ================================================================
  const ROLES = {
    submitter:      { label: '提交申请',   dept: '发起人',   color: '#64748B' },
    biz_manager:    { label: '业务审批',   dept: '业务部',   color: '#2563EB' },
    risk_manager:   { label: '风控审批',   dept: '风控部',   color: '#7C3AED' },
    finance_manager:{ label: '财务审批',   dept: '财务部',   color: '#059669' },
    legal_review:   { label: '合规审查',   dept: '法务部',   color: '#0891B2' },
    gm:             { label: '总经理审批', dept: '总经理',   color: '#DC2626' }
  };

  // ================================================================
  // 三、内置流程模板（从现有业务页面反推的审批规则）
  // ================================================================
  // 条件分支示例：金额 > 100 万增加总经理节点
  const DEFAULT_BRANCH_RULES = [
    { field: 'amount', operator: 'gt', value: 1000000, then: ['gm'] }
  ];

  const FLOW_TEMPLATES = {
    // 通用默认流程（金额条件分支）
    standard: {
      id: 'standard',
      name: '标准审批流程',
      desc: '发起 → 业务审批 → 风控+财务会签 →（金额 > 100 万加总经理）→ 完成',
      status: 'enabled',
      applicableModules: ['通用'],
      updatedAt: '2026-10-12 10:30',
      updatedBy: '张爽',
      nodes: [
        { id: 'n1', type: NODE_TYPE.START, name: '提交申请', role: 'submitter' },
        { id: 'n2', type: NODE_TYPE.SERIAL, name: '业务审批', role: 'biz_manager', slaHours: 24 },
        {
          id: 'n3', type: NODE_TYPE.PARALLEL_ALL, name: '风控财务会签',
          role: 'risk_manager',
          approvers: [
            { role: 'risk_manager',    dept: '风控部' },
            { role: 'finance_manager', dept: '财务部' }
          ],
          slaHours: 48,
          desc: '风控、财务全部通过才算通过'
        },
        { id: 'n4', type: NODE_TYPE.BRANCH, name: '金额分支', condition: DEFAULT_BRANCH_RULES },
        { id: 'n5', type: NODE_TYPE.SERIAL, name: '归档完成', role: 'system', auto: true }
      ]
    },

    // 简化流程（小额免风控）
    simple: {
      id: 'simple',
      name: '简易审批流程',
      desc: '发起 → 业务审批 → 财务审批 → 完成（适用小额单据）',
      status: 'enabled',
      applicableModules: ['合同管理', '收发货管理'],
      updatedAt: '2026-10-12 09:15',
      updatedBy: '李娜',
      nodes: [
        { id: 'n1', type: NODE_TYPE.START, name: '提交申请', role: 'submitter' },
        { id: 'n2', type: NODE_TYPE.SERIAL, name: '业务审批', role: 'biz_manager', slaHours: 24 },
        { id: 'n3', type: NODE_TYPE.SERIAL, name: '财务审批', role: 'finance_manager', slaHours: 48 },
        { id: 'n4', type: NODE_TYPE.SERIAL, name: '归档完成', role: 'system', auto: true }
      ]
    },

    // 高风险流程（追保函 / 保证金调整，金额大 + 合规）
    highRisk: {
      id: 'highRisk',
      name: '高风险审批流程',
      desc: '发起 → 业务审批 → 风控+财务会签 → 合规审查 → 总经理审批 → 完成',
      status: 'enabled',
      applicableModules: ['追保函管理', '资金管理'],
      updatedAt: '2026-10-11 17:40',
      updatedBy: '王浩',
      nodes: [
        { id: 'n1', type: NODE_TYPE.START, name: '提交申请', role: 'submitter' },
        { id: 'n2', type: NODE_TYPE.SERIAL, name: '业务审批', role: 'biz_manager', slaHours: 12 },
        {
          id: 'n3', type: NODE_TYPE.PARALLEL_ALL, name: '风控财务会签',
          role: 'risk_manager',
          approvers: [
            { role: 'risk_manager',    dept: '风控部' },
            { role: 'finance_manager', dept: '财务部' }
          ],
          slaHours: 24
        },
        { id: 'n4', type: NODE_TYPE.SERIAL, name: '合规审查', role: 'legal_review', slaHours: 48 },
        { id: 'n5', type: NODE_TYPE.SERIAL, name: '总经理审批', role: 'gm', slaHours: 24 },
        { id: 'n6', type: NODE_TYPE.SERIAL, name: '归档完成', role: 'system', auto: true }
      ]
    }
  };

  // ================================================================
  // 四、流程模板 CRUD（localStorage 持久化）
  // ================================================================
  const STORAGE_KEY = 'ygt_approval_flow_templates_v1';

  function loadAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') return parsed;
      }
    } catch (e) { /* 忽略：降级到内置模板 */ }
    // 深拷贝内置模板，避免污染常量
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
    return Object.keys(all).map(k => all[k]);
  }

  function getFlow(id) {
    return loadAll()[id] || null;
  }

  function saveFlow(flow) {
    const all = loadAll();
    all[flow.id] = Object.assign({}, flow, {
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
    return saveFlow(Object.assign({}, JSON.parse(JSON.stringify(src)), {
      id: newId,
      name: newName || (src.name + ' - 副本'),
      status: 'draft',
      nodes: src.nodes.map(n => Object.assign({}, n, { id: n.id + '_' + Date.now().toString().slice(-4) }))
    }));
  }

  function nowStr() {
    const d = new Date();
    const p = n => String(n).padStart(2, '0');
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' +
           p(d.getHours()) + ':' + p(d.getMinutes());
  }

  // ================================================================
  // 五、条件分支求值
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
   * 求值条件分支节点：返回 true 时走 then 分支（追加节点），false 时跳过
   */
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
        then: thenList,                              // 命中时追加的角色 key 列表
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
    (flow.nodes || []).forEach(node => {
      if (node.type === NODE_TYPE.BRANCH) {
        const res = evalBranch(node, formData);
        if (res.matched) {
          // 命中的分支：把每条命中规则的 then 角色去重后展开为串行节点
          // 注意：必须用 res.rules（已求值，含 matched/then/text），不能用 node.condition（原始配置）
          const seen = {};
          const branches = res.rules.filter(r => r.matched);
          branches.forEach(r => {
            (r.then || []).forEach(roleKey => {
              if (seen[roleKey]) return;          // 同一次展开内按 roleKey 去重
              seen[roleKey] = true;
              const meta = ROLES[roleKey] || { label: roleKey, dept: '—', color: '#64748B' };
              out.push({
                id: node.id + '_' + roleKey,
                type: NODE_TYPE.SERIAL,
                name: meta.label,
                roleKey: roleKey,
                role: meta.label,
                dept: meta.dept,
                color: meta.color,
                slaHours: 24,
                fromBranch: true,
                branchRule: r.text,
                status: NODE_STATUS.PENDING
              });
            });
          });
        } else {
          out.push({
            id: node.id,
            type: NODE_TYPE.BRANCH,
            name: node.name || '条件分支',
            skipped: true,
            status: NODE_STATUS.SKIPPED,
            branchRules: res.rules
          });
        }
      } else {
        out.push(Object.assign({}, node, { status: node.status || NODE_STATUS.PENDING }));
      }
    });
    return out;
  }

  // ================================================================
  // 六、渲染器
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

  /**
   * 渲染审批时间线（纯 HTML 字符串）
   * @param {Object} opts
   *   flow       流程模板
   *   formData   表单数据（用于条件分支求值）
   *   currentIdx 当前进行中的节点序号（-1 = 全部待开始）
   *   compact    精简模式（只显示节点名 + 状态）
   */
  function renderTimeline(opts, bare) {
    const o = opts || {};
    const flow = o.flow || getFlow('standard');
    const nodes = resolveFlow(flow, o.formData || {});
    const currentIdx = o.currentIdx == null ? -1 : o.currentIdx;

    // bare=true 时不输出外层 .timeline 包裹（供容器自身已带 timeline 类的场景使用）
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
      const meta = ROLES[node.role] || { label: node.role || '—', dept: node.dept || '—', color: '#64748B' };
      const idx = CIRCLED[i] || (i + 1);

      html += '<div class="timeline-item ' + status + '" data-node-id="' + esc(node.id) + '">';
      html += '  <div class="timeline-dot"><span class="timeline-dot-num">' + idx + '</span></div>';
      html += '  <div class="timeline-content">';
      html += '    <div class="timeline-title">' + esc(node.name || meta.label);

      // 类型 chip
      if (node.type === NODE_TYPE.PARALLEL_ALL) {
        html += ' <span class="chip chip-gray">会签 ALL</span>';
      } else if (node.type === NODE_TYPE.START) {
        html += ' <span class="chip chip-gray">发起</span>';
      } else if (node.fromBranch) {
        html += ' <span class="chip chip-blue">条件命中</span>';
      }

      // 状态 chip
      if (status === NODE_STATUS.DONE)        html += ' <span class="chip chip-green">已通过</span>';
      else if (status === NODE_STATUS.CURRENT)html += ' <span class="chip chip-orange">进行中</span>';
      else if (status === NODE_STATUS.PENDING)html += ' <span class="chip chip-gray">待开始</span>';
      else if (status === NODE_STATUS.SKIPPED)html += ' <span class="chip chip-gray">已跳过</span>';

      html += '  </div>';

      // 会签子审批人
      if (node.type === NODE_TYPE.PARALLEL_ALL && node.approvers && node.approvers.length) {
        node.approvers.forEach((a, ai) => {
          const aMeta = ROLES[a.role] || { label: a.role, dept: a.dept || '—' };
          const aStatus = status === NODE_STATUS.DONE ? '已通过' : (status === NODE_STATUS.CURRENT ? '审批中' : '待审批');
          const aCls = status === NODE_STATUS.DONE ? 'chip-green'
                     : (status === NODE_STATUS.CURRENT ? 'chip-orange' : 'chip-gray');
          html += '    <div class="timeline-subitem">';
          html += '      <div class="timeline-subitem-header">';
          html += '        <div class="timeline-subitem-name">';
          html += '          <div class="avatar" style="background:' + aMeta.color + ';">' + esc(aMeta.label.charAt(0)) + '</div>';
          html += '          <span><strong>' + esc(aMeta.label) + '</strong> · ' + esc(a.dept || aMeta.dept) + '</span>';
          html += '        </div>';
          html += '        <span class="chip ' + aCls + '">' + aStatus + '</span>';
          html += '      </div>';
          html += '    </div>';
        });
      }

      // 条件分支说明
      if (node.fromBranch && node.branchRule) {
        html += '    <div class="timeline-meta"><span>触发条件：' + esc(node.branchRule) + '</span></div>';
      }
      if (isBranchSkipped && node.branchRules && node.branchRules.length) {
        html += '    <div class="timeline-meta"><span>条件未命中，已跳过（' +
                esc(node.branchRules.map(r => r.text + ' → 实际 ' + r.actual).join('；')) + '）</span></div>';
      }

      // SLA
      if (node.slaHours && status !== NODE_STATUS.SKIPPED) {
        html += '    <div class="timeline-meta"><span>⏱ 审批时限 ' + node.slaHours + ' 小时</span></div>';
      }

      html += '  </div>';
      html += '</div>';
    });

    html += bare ? '' : '</div>';
    return html;
  }

  /**
   * 渲染流程图（横向节点链，用于流程配置页预览）
   */
  function renderFlowChain(flow, formData) {
    const nodes = resolveFlow(flow, formData || {});
    let html = '<div class="afc-chain">';
    nodes.forEach((n, i) => {
      const meta = ROLES[n.role] || { label: n.role || '—', color: '#64748B' };
      const isSkip = n.skipped;
      html += '<div class="afc-node' + (isSkip ? ' is-skipped' : '') + '" style="--node-color:' + meta.color + '">';
      html += '  <div class="afc-node-no">' + (CIRCLED[i] || (i + 1)) + '</div>';
      html += '  <div class="afc-node-name">' + esc(n.name || meta.label) + '</div>';
      html += '  <div class="afc-node-role">' + esc(meta.dept || '—') + '</div>';
      if (n.type === NODE_TYPE.PARALLEL_ALL) {
        html += '  <div class="afc-node-tag">会签 ' + (n.approvers ? n.approvers.length : 0) + ' 人</div>';
      }
      if (n.fromBranch) html += '  <div class="afc-node-tag is-blue">条件命中</div>';
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
  // 七、业务页面接入 API（一行代码接入）
  // ================================================================
  /**
   * 页面级配置覆盖表：pageName -> flowId
   * 业务页面可在引入引擎后设置，覆盖该页使用的默认流程
   *
   * 注意：必须动态读取 global，而不是在 IIFE 执行时快照。
   * 页面 <script> 顺序可能把 approval-engine.js 排在 approval-config.js 之前，
   * 快照会永久捕获空对象，导致所有页面静默回退到 standard 流程。
   */
  function configByPage(pageName) {
    var map = global.APPROVAL_CONFIG_BY_PAGE;
    return (map && map[pageName]) || null;
  }
  function amountConfig() {
    return global.APPROVAL_AMOUNT_CONFIG || {};
  }

  /**
   * 自动提取当前页面的单据金额（条件分支求值用）
   * 优先级：显式 opts.formData.amount > DOM 选择器 > URL 参数 > undefined
   */
  function detectAmount(pageName) {
    // 1. 页面显式标注
    const explicit = document.querySelector('[data-approval-amount]');
    if (explicit) {
      const v = Number(String(explicit.getAttribute('data-approval-amount') || '').replace(/[^\d.]/g, ''));
      if (!isNaN(v) && v > 0) return v;
    }
    // 2. URL 参数 ?amount=
    try {
      const q = new URLSearchParams(location.search).get('amount');
      if (q && !isNaN(Number(q))) return Number(q);
    } catch (e) { /* ignore */ }
    // 3. 配置的通用选择器
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

  /**
   * 便捷挂载：在指定容器渲染当前页面的审批时间线
   */
  function mount(selector, opts) {
    const el = typeof selector === 'string' ? document.querySelector(selector) : selector;
    if (!el) { console.warn('[approval-engine] 容器未找到:', selector); return; }
    const o = Object.assign({}, opts || {});
    const pageName = (location.pathname.split('/').pop() || '').replace(/\.html$/i, '');
    if (!o.flow) {
      const flowId = o.flowId || configByPage(pageName) || 'standard';
      o.flow = getFlow(flowId) || getFlow('standard');
    }
    // 自动补 formData.amount（条件分支需要）
    if (!o.formData) o.formData = {};
    if (o.formData.amount == null) {
      const amt = detectAmount(pageName);
      if (amt != null) o.formData.amount = amt;
    }
    if (!o.currentIdx && o.currentIdx !== 0) o.currentIdx = detectCurrentIdx(el, o);
    // 业务页面的挂载点原本就是 <div class="timeline" id="approvalTimeline_xxx">，
    // 若再套一层 .timeline 会产生嵌套同名容器（重复边框/内边距），此处按容器类名自适应。
    const bare = el.classList && el.classList.contains('timeline');
    el.innerHTML = renderTimeline(o, bare);
  }

  /** 从页面已有的 timeline DOM 反推当前节点（兼容未改造的老页面） */
  function detectCurrentIdx(container, opts) {
    const items = container.querySelectorAll('.timeline-item');
    for (let i = 0; i < items.length; i++) {
      if (items[i].classList.contains('current')) return i;
      if (items[i].classList.contains('rejected')) return i;
    }
    return opts && opts.allDone ? items.length - 1 : -1;
  }

  // ================================================================
  // 八、导出
  // ================================================================
  global.ApprovalEngine = {
    // 常量
    NODE_TYPE, NODE_STATUS, ROLES, OPERATORS, OP_LABELS, FIELD_LABELS,
    // 流程 CRUD
    listFlows, getFlow, saveFlow, deleteFlow, duplicateFlow,
    // 求值
    evalBranch, resolveFlow,
    // 渲染
    renderTimeline, renderFlowChain,
    // 接入
    mount, detectAmount,
    // 工具
    nowStr, esc, fmtAmount, CIRCLED
  };

})(window);