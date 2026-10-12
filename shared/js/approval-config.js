// ===== 审批流程页面映射表 v1.0.0 =====
// 用途：告诉通用审批引擎「哪个业务页面用哪个流程模板」
// 加载方式：业务页面引入本文件后，ApprovalEngine.mount() 会自动读取
// 说明：页面名（去掉 .html）→ 流程模板 id 的映射
//
// 流程模板说明：
//   standard      标准审批流程（发起 → 业务 → 风控财务会签 → 金额>100万加总经理 → 归档）
//   simple        简易审批流程（发起 → 业务 → 财务 → 归档）
//   highRisk      高风险审批流程（发起 → 业务 → 风控财务会签 → 合规 → 总经理 → 归档）

window.APPROVAL_CONFIG_BY_PAGE = {

  // ---------- 合同管理 ----------
  'contract-purchase-framework-detail':  'highRisk',
  'contract-purchase-order-detail':      'highRisk',
  'contract-sales-framework-detail':     'highRisk',
  'contract-sales-order-detail':         'highRisk',
  'contract-supplement-framework-detail':'highRisk',
  'contract-supplement-order-detail':    'highRisk',
  'contract-shipping':                   'standard',

  // ---------- 资金管理 ----------
  'payment-detail':      'highRisk',   // 付款金额大，走高风险
  'refund-detail':       'highRisk',   // 退款需风控+财务
  'receipt-edit':        'simple',     // 回款登记流程简单
  'receipt-detail':      'simple',
  'margin-adjust-detail':'highRisk',   // 保证金调整敏感

  // ---------- 追保函管理 ----------
  'bond-letter-detail':  'highRisk',   // 追保函涉及担保责任

  // ---------- 准入管理 ----------
  'project-apply':       'standard',   // 立项：金额>100万加总经理
  'project-detail':      'standard',
  'customer-apply':      'highRisk',   // 客户准入需合规审查
  'customer-detail':     'highRisk',

  // ---------- 收发货 / 货转 ----------
  'shipment-out-detail': 'simple',
  'shipment-in-detail':  'simple',
  'goods-transfer-up-detail':   'simple',
  'goods-transfer-down-detail': 'simple',
  'warehouse-release-detail':    'simple',

  // ---------- 结算单 ----------
  'settlement-purchase-detail': 'standard',
  'settlement-sales-detail':    'standard',

  // ---------- 发票 ----------
  'invoice-detail':       'simple',
  'invoice-out-detail':   'simple',

  // ---------- 业务线 ----------
  'business-line-detail': 'standard'
};

// 各页面的审批单据金额提取配置（用于条件分支求值）
// 规则：引擎会按顺序尝试从页面 DOM 或 URL 参数中读取金额
window.APPROVAL_AMOUNT_CONFIG = {
  // 默认：从页面上 id 含 amount / total / price 的元素取数值
  defaultSelectors: [
    '[data-approval-amount]',
    '#approvalAmount',
    '.approval-amount'
  ],
  // 单位换算：若页面金额单位是"万元"，乘以 10000 转为"元"
  unitMultiplier: {
    'project-apply': 10000   // 立项页总投资单位是万元
  }
};