/* ================================================================
 * 企业风险扫描 · 主体风险 tab（v1.38.0）
 * ----------------------------------------------------------------
 * 需求：贸易风险 + 主体风险 两个 tab 合并为单一「主体风险」tab，
 *       检查分类收敛为 4 类，校验项按业务清单重排。
 *
 * from = 复用原型现有**同义校验项**（取其检查规则 / 检查过程 / 诊断状态）
 *        null = 原型中找不到对应检查过程 → 该项的检查规则与检查过程留空
 *
 * 口径：检查过程必须与原型现有「检查规则 / 校验项」一致，不得凭空新写。
 * ================================================================ */
(function () {
  'use strict';

  var SUBJECT = {
    tabKey: 'subject',
    label: '主体风险',
    categories: [
      {
        label: '主责主业合规',
        items: [
          { name: '经营范围中无贸易、供应链管理', from: '经营范围中无贸易、供应链管理' },
          { name: '业务品类是否属于流通性强、易变现产品', from: null, aliases: ['禁止品类业务风险'] },
          { name: '企业具有清晰的供应链业务方向与模式', from: '公司具有清晰的供应链业务方向和模式', aliases: ['业务方向模糊风险'] },
          { name: '服务集团主业', from: null, aliases: ['低关联业务规模风险'] },
        ],
      },
      {
        label: '空壳企业风险',
        items: [
          { name: '成立时间＜6 个月且拟开展单笔＞500 万大额贸易', from: '成立时间＜6 个月', aliases: ['大额贸易风险', '拟开展单笔＞500 万大额贸易'] },
          { name: '社保人数≤1 人、无工资个税记录、无水电消耗数据', from: '社保人数≤1 人', aliases: ['无工资个税记录'] },
          { name: '注册地址为虚拟/集群/托管地址、一址多企≥5 家', from: '注册地址为虚拟/集群/托管地址', aliases: ['一址多企 ≥5 家'] },
          { name: '长期零申报、非正常户、走逃失联、欠税≥3 次', from: null },
          { name: '无实缴资本、经营范围宽泛无具体品类', from: '无实缴资本' },
          { name: '与该无历史业务记录且突然开展大额新增品类贸易', from: '无历史业务记录', aliases: ['历史业务缺失风险'] },
        ],
      },
      {
        label: '资质缺失风险',
        items: [
          { name: '拟交易商品品类不在其工商经营范围内', from: '拟交易商品不在工商经营范围内', aliases: ['超范围经营风险'] },
          { name: '企业是否有与本次贸易相关的资质临期或已过期', from: '资质已过期或 30 天内即将到期', aliases: ['资质缺失风险'] },
          { name: '与下游客户无仓库、仓储协议', from: '无仓库、无仓储协议', aliases: ['仓储协议缺失风险'] },
          { name: '企业无实际经营场地或使用虚拟/托管地址', from: null },
          { name: '特定货品无有效专项存储设备', from: '危化/粮油/医药/能源无有效专项资质', aliases: ['品牌授权缺失风险', '物流资质缺失风险'] },
        ],
      },
      {
        label: '客户产业链定位',
        items: [
          { name: '上下游双方是否均为贸易类型企业且过往合作项目中对手为贸易企业占比超过 80%', from: '合作客户中贸易类企业占比超过 80%', aliases: ['上下游贸易类风险', '客户集中贸易类风险'] },
          { name: '该企业连续三个月客户变动率>50%', from: '前五大客户变动频繁（连续三个月变动率＞50%）', aliases: ['合作方频繁变更风险'] },
        ],
      },
    ],
  };

  /**
   * 规则占位文案：原型里 getRiskMeta 找不到映射时的兜底，
   * 不算「匹配到的检查规则」→ 按未匹配处理（留空）
   */
  var PLACEHOLDER_RULE = '按风险模型规则校验';

  function realRule(r) {
    if (!r) return '';
    if (Array.isArray(r)) {
      var keep = r.filter(function (x) { return x && x !== PLACEHOLDER_RULE; });
      return keep.length ? keep : '';
    }
    return r === PLACEHOLDER_RULE ? '' : r;
  }

  /**
   * 按 4 分类清单构建「主体风险」tab 的条目
   * @param {Object} lookup  旧项索引：{ 旧校验项名: { desc, status, rule } }
   * @returns {Array} items
   */
  SUBJECT.buildItems = function (lookup) {
    lookup = lookup || {};
    var out = [];
    SUBJECT.categories.forEach(function (cat) {
      cat.items.forEach(function (it) {
        // 候选源：主 from 优先，再按 aliases 顺序
        var candidates = [];
        if (it.from) candidates.push(it.from);
        (it.aliases || []).forEach(function (a) { candidates.push(a); });
        var hit = null, hitName = '';
        candidates.forEach(function (nm) {
          if (!hit && lookup[nm]) { hit = lookup[nm]; hitName = nm; }
        });
        var isWarn = false;
        candidates.forEach(function (nm) {
          if (lookup[nm] && lookup[nm].status === 'warn') isWarn = true;
        });
        out.push({
          name: it.name,
          category: cat.label,
          from: hitName,
          // 未匹配到原型的检查过程 / 占位规则 → 留空
          rule: hit ? realRule(hit.rule) : '',
          desc: hit && hit.desc ? hit.desc : '',
          status: isWarn ? 'warn' : (hit && hit.status ? hit.status : 'ok'),
          // 源项位置：改「系统诊断结论」时要写回原来的 trade / internal 条目
          srcTab: hit ? (hit.tab || '') : '',
          srcIdx: hit && typeof hit.idx === 'number' ? hit.idx : -1,
        });
      });
    });
    return out;
  };

  /** 「自动结论备注」的选项（低/中/高风险 + 自定义描述） */
  SUBJECT.remarkOptions = [
    { value: 'low', label: '低风险' },
    { value: 'mid', label: '中风险' },
    { value: 'high', label: '高风险' },
    { value: 'custom', label: '自定义描述' },
  ];

  /** 自定义描述字数上限 */
  SUBJECT.remarkMaxLength = 24;

  // ===== 备注持久化（跨页：申请页填写 → 详情页回显）=====

  /** 当前操作人：与顶栏展示的用户一致 */
  SUBJECT.currentUser = function () {
    var el = document.querySelector('.topbar-user-name');
    return el ? (el.textContent || '').trim() || '—' : '—';
  };

  /** 存储键：按企业名（申请页与详情页的企业名一致，可对齐） */
  SUBJECT.storeKey = function (companyName) {
    return 'ygt_risk_remarks_' + (companyName || 'unknown');
  };

  /**
   * 读取某企业的全部备注
   * @returns {Object} { [tab]: { [校验项名]: { value, text, operator, time } } }
   */
  SUBJECT.loadRemarks = function (companyName) {
    try {
      var raw = localStorage.getItem(SUBJECT.storeKey(companyName));
      var obj = raw ? JSON.parse(raw) : {};
      return (obj && typeof obj === 'object') ? obj : {};
    } catch (e) {
      return {};
    }
  };

  /** 写入某企业的全部备注 */
  SUBJECT.saveRemarks = function (companyName, data) {
    try {
      localStorage.setItem(SUBJECT.storeKey(companyName), JSON.stringify(data || {}));
    } catch (e) { /* 隐私模式等场景忽略 */ }
  };

  /** 备注结构规范化（补齐 operator / time） */
  SUBJECT.remarkRecord = function (value, text, operator, time) {
    return {
      value: value || '',
      text: text || '',
      operator: operator || SUBJECT.currentUser(),
      time: time || SUBJECT.now(),
    };
  };

  /** HTML 转义（页面内无 esc 工具时用这个） */
  SUBJECT.esc = function (s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  /** 当前时间（yyyy-MM-dd HH:mm:ss） */
  SUBJECT.now = function () {
    var d = new Date();
    function p(n) { return n < 10 ? '0' + n : '' + n; }
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate())
      + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
  };

  /**
   * 「风险逻辑（对应合规要求）」——按**检查分类**给出的固定合规要求文本
   * （取代原来的「检查规则（负面清单）」列）
   * 未列入映射的分类（经营行为类 / 合规记录类 / 关联关系类 / 人员合规类）沿用原检查规则。
   */
  SUBJECT.complianceLogic = {
    '主责主业合规':
      '违反「不准开展背离主业的贸易业务」，非主业贸易无审批，易形成无效资产',
    '空壳企业风险':
      '违反「不准与无实际经营能力的企业交易」，空壳企业易引发虚开发票、资金流失',
    '资质缺失风险':
      '违反「不准开展需特许资质但无资质的贸易」，无证经营易触发行政追责；'
      + '或违反「不准开展对交易标的没有控制权的空转、走单等贸易业务」，不具备资质的仓储企业无法保障货权清晰',
    '客户产业链定位':
      '违反「不准开展无商业实质的循环贸易」，交易对手生产型企业占比较低或变动频繁，'
      + '难以核实贸易背景，无法确定货物流转是否创造价值',
  };

  /** 取某检查分类对应的风险逻辑（对应合规要求）；无映射时返回 null */
  SUBJECT.logicOf = function (category) {
    return SUBJECT.complianceLogic[category] || null;
  };

  window.RISK_SCAN_SUBJECT = SUBJECT;
})();
