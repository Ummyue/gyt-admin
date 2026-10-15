// ===== 审批流程页面映射表 v1.1.0 =====
// 用途：告诉通用审批引擎「哪个业务页面用哪个流程模板」
// 加载方式：业务页面引入本文件后，ApprovalEngine.mount() 会动态读取
// 注意：引擎在 mount() 时才读取本表，两个 script 的先后顺序不影响结果
//
// 流程模板说明：
//   standard   标准审批流程（发起 → 业务 → 风控财务会签 → 金额>100万加总经理 → 归档）
//   simple     简易审批流程（发起 → 业务 → 财务 → 归档）
//   highRisk   高风险审批流程（发起 → 业务 → 风控财务会签 → 合规 → 总经理 → 归档）
//
// 应用模块（见 approval-engine.js APPLY_MODULES）：
//   project 项目准入 / contract 合同管理 / goods_transfer 货转管理 /
//   payment 付款管理 / refund 退款管理 / settlement 结算单管理 /
//   bond_letter 追保函管理 / release 放货管理

window.APPROVAL_CONFIG_BY_PAGE = {

  // ---------- 合同管理（highRisk：合同金额大 + 需合规） ----------
  'contract-purchase-framework-detail':  'highRisk',
  'contract-purchase-order-detail':      'highRisk',
  'contract-sales-framework-detail':     'highRisk',
  'contract-sales-order-detail':         'highRisk',
  'contract-supplement-framework-detail':'highRisk',
  'contract-supplement-order-detail':    'highRisk',
  'contract-shipping':                   'highRisk',

  // ---------- 付款管理 / 退款管理（highRisk：资金流出） ----------
  'payment-detail':      'highRisk',
  'refund-detail':       'highRisk',
  'margin-adjust-detail':'highRisk',

  // ---------- 追保函管理（highRisk：涉担保责任） ----------
  'bond-letter-detail':  'highRisk',

  // ---------- 客户准入 / 项目准入 ----------
  'project-apply':       'standard',
  'project-detail':      'standard',
  'customer-apply':      'highRisk',
  'customer-detail':     'highRisk',

  // ---------- 货转管理（simple：小额高频） ----------
  'goods-transfer-up-detail':   'simple',
  'goods-transfer-down-detail': 'simple',

  // ---------- 放货管理（simple：仓储放货） ----------
  'warehouse-release-detail':    'simple',

  // ---------- 收发货管理 ----------
  'shipment-out-detail': 'simple',
  'shipment-in-detail':  'simple',

  // ---------- 结算单管理 ----------
  'settlement-purchase-detail': 'standard',
  'settlement-sales-detail':    'standard',

  // ---------- 发票管理 ----------
  'invoice-detail':       'simple',
  'invoice-out-detail':   'simple',

  // ---------- 回款管理 ----------
  'receipt-edit':         'simple',
  'receipt-detail':       'simple',

  // ---------- 业务线管理 ----------
  'business-line-detail': 'standard'
};

// 各页面的审批单据金额提取配置（用于条件分支求值）
window.APPROVAL_AMOUNT_CONFIG = {
  // 按优先级尝试：data 属性 → 页面显式标注 → URL 参数 ?amount=
  defaultSelectors: [
    '[data-approval-amount]',
    '#approvalAmount',
    '.approval-amount'
  ],
  // 单位换算：若页面金额单位是「万元」，乘 10000 转为「元」
  unitMultiplier: {
    'project-apply': 10000   // 立项页总投资单位是万元
  }
};
