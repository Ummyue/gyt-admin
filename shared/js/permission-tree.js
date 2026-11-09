// 本文件由 scripts/extract_permissions.py 自动生成，请勿手工编辑
// 生成时间：2026-11-09 17:42:39
// 用途：角色权限管理页的权限配置项（一/二/三级菜单 + 页面操作按钮）

window.PERMISSION_TREE = [
  {
    "key": "工作台",
    "label": "工作台",
    "icon": "🏠",
    "subMenus": [
      {
        "label": "工作台",
        "file": "workbench.html",
        "buttons": [],
        "children": [],
        "code": "menu:工作台/工作台",
        "mergedMenus": [],
        "ops": []
      }
    ]
  },
  {
    "key": "准入管理",
    "label": "准入管理",
    "icon": "📋",
    "subMenus": [
      {
        "label": "项目准入",
        "file": "project-list.html",
        "buttons": [
          "新增立项申请",
          "数据导出",
          "确认上传",
          "全部标记已读",
          "查看",
          "编辑",
          "提交",
          "作废",
          "撤回",
          "重新提交",
          "上传客户准入报告",
          "上传决议文件",
          "发起完结",
          "替换",
          "删除"
        ],
        "children": [],
        "code": "menu:准入管理/项目准入",
        "mergedMenus": [],
        "ops": [
          {
            "label": "新增立项申请",
            "code": "准入管理/项目准入#create"
          },
          {
            "label": "数据导出",
            "code": "准入管理/项目准入#export"
          },
          {
            "label": "编辑",
            "code": "准入管理/项目准入#edit"
          },
          {
            "label": "提交",
            "code": "准入管理/项目准入#submit7"
          },
          {
            "label": "作废",
            "code": "准入管理/项目准入#void"
          },
          {
            "label": "撤回",
            "code": "准入管理/项目准入#withdraw"
          },
          {
            "label": "重新提交",
            "code": "准入管理/项目准入#submit10"
          },
          {
            "label": "上传客户准入报告",
            "code": "准入管理/项目准入#upload"
          },
          {
            "label": "上传决议文件",
            "code": "准入管理/项目准入#upload12"
          },
          {
            "label": "发起完结",
            "code": "准入管理/项目准入#submit13"
          }
        ]
      },
      {
        "label": "客户准入",
        "file": "customer-list.html",
        "buttons": [
          "新增客户",
          "数据导出",
          "查看状态机说明",
          "编辑",
          "查看",
          "查看额度",
          "撤回",
          "作废",
          "发起完结"
        ],
        "children": [],
        "code": "menu:准入管理/客户准入",
        "mergedMenus": [],
        "ops": [
          {
            "label": "新增客户",
            "code": "准入管理/客户准入#create"
          },
          {
            "label": "数据导出",
            "code": "准入管理/客户准入#export"
          },
          {
            "label": "编辑",
            "code": "准入管理/客户准入#edit"
          },
          {
            "label": "查看",
            "code": "准入管理/客户准入#view5"
          },
          {
            "label": "撤回",
            "code": "准入管理/客户准入#withdraw"
          },
          {
            "label": "作废",
            "code": "准入管理/客户准入#void"
          }
        ]
      },
      {
        "label": "黑名单管理",
        "file": "blacklist.html",
        "buttons": [
          "新增黑名单企业",
          "批量导入",
          "数据导出",
          "批量删除",
          "下载模板",
          "开始导入",
          "详情"
        ],
        "children": [],
        "code": "menu:准入管理/黑名单管理",
        "mergedMenus": [],
        "ops": [
          {
            "label": "新增黑名单企业",
            "code": "准入管理/黑名单管理#create"
          },
          {
            "label": "批量导入",
            "code": "准入管理/黑名单管理#import"
          },
          {
            "label": "数据导出",
            "code": "准入管理/黑名单管理#export"
          },
          {
            "label": "详情",
            "code": "准入管理/黑名单管理#view"
          }
        ]
      }
    ]
  },
  {
    "key": "数字供应链",
    "label": "数字供应链",
    "icon": "📦",
    "subMenus": [
      {
        "label": "合同管理",
        "file": "contract-purchase.html",
        "buttons": [
          "新增合同",
          "数据导出",
          "确认提交",
          "查看补协"
        ],
        "children": [
          {
            "label": "采购合同",
            "file": "contract-purchase.html",
            "buttons": [
              "新增合同",
              "数据导出",
              "确认提交",
              "查看补协"
            ],
            "children": [],
            "code": "menu:数字供应链/合同管理/采购合同",
            "mergedMenus": [
              {
                "label": "新增采购框架合同",
                "code": "menu:数字供应链/合同管理/新增采购框架合同"
              },
              {
                "label": "新增采购订单/单批次合同",
                "code": "menu:数字供应链/合同管理/新增采购订单/单批次合同"
              }
            ],
            "ops": [
              {
                "label": "新增合同",
                "code": "数字供应链/合同管理/采购合同#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/合同管理/采购合同#export"
              },
              {
                "label": "确认提交",
                "code": "数字供应链/合同管理/采购合同#submit"
              },
              {
                "label": "查看补协",
                "code": "数字供应链/合同管理/采购合同#view"
              },
              {
                "label": "+ 上传",
                "code": "数字供应链/合同管理/新增采购框架合同#upload",
                "src": "新增采购框架合同"
              },
              {
                "label": "保存",
                "code": "数字供应链/合同管理/新增采购框架合同#save",
                "src": "新增采购框架合同"
              },
              {
                "label": "提交",
                "code": "数字供应链/合同管理/新增采购框架合同#submit",
                "src": "新增采购框架合同"
              },
              {
                "label": "+ 上传",
                "code": "数字供应链/合同管理/新增采购订单/单批次合同#upload",
                "src": "新增采购订单/单批次合同"
              },
              {
                "label": "提交",
                "code": "数字供应链/合同管理/新增采购订单/单批次合同#submit",
                "src": "新增采购订单/单批次合同"
              }
            ]
          },
          {
            "label": "销售合同",
            "file": "contract-sales.html",
            "buttons": [
              "新增合同",
              "数据导出",
              "确认提交",
              "查看补协"
            ],
            "children": [],
            "code": "menu:数字供应链/合同管理/销售合同",
            "mergedMenus": [
              {
                "label": "新增销售框架合同",
                "code": "menu:数字供应链/合同管理/新增销售框架合同"
              },
              {
                "label": "新增销售订单/单批次合同",
                "code": "menu:数字供应链/合同管理/新增销售订单/单批次合同"
              }
            ],
            "ops": [
              {
                "label": "新增合同",
                "code": "数字供应链/合同管理/销售合同#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/合同管理/销售合同#export"
              },
              {
                "label": "确认提交",
                "code": "数字供应链/合同管理/销售合同#submit"
              },
              {
                "label": "查看补协",
                "code": "数字供应链/合同管理/销售合同#view"
              },
              {
                "label": "+ 上传",
                "code": "数字供应链/合同管理/新增销售框架合同#upload",
                "src": "新增销售框架合同"
              },
              {
                "label": "保存",
                "code": "数字供应链/合同管理/新增销售框架合同#save",
                "src": "新增销售框架合同"
              },
              {
                "label": "提交",
                "code": "数字供应链/合同管理/新增销售框架合同#submit",
                "src": "新增销售框架合同"
              },
              {
                "label": "+ 上传",
                "code": "数字供应链/合同管理/新增销售订单/单批次合同#upload",
                "src": "新增销售订单/单批次合同"
              },
              {
                "label": "提交",
                "code": "数字供应链/合同管理/新增销售订单/单批次合同#submit",
                "src": "新增销售订单/单批次合同"
              }
            ]
          },
          {
            "label": "补充协议",
            "file": "contract-supplement.html",
            "buttons": [
              "新增补充协议",
              "数据导出",
              "补协详情",
              "上传双签附件",
              "作废"
            ],
            "children": [],
            "code": "menu:数字供应链/合同管理/补充协议",
            "mergedMenus": [
              {
                "label": "新增补协-框架合同",
                "code": "menu:数字供应链/合同管理/新增补协-框架合同"
              },
              {
                "label": "新增补协-订单/单批次合同",
                "code": "menu:数字供应链/合同管理/新增补协-订单/单批次合同"
              }
            ],
            "ops": [
              {
                "label": "新增补充协议",
                "code": "数字供应链/合同管理/补充协议#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/合同管理/补充协议#export"
              },
              {
                "label": "补协详情",
                "code": "数字供应链/合同管理/补充协议#view"
              },
              {
                "label": "上传双签附件",
                "code": "数字供应链/合同管理/补充协议#upload"
              },
              {
                "label": "作废",
                "code": "数字供应链/合同管理/补充协议#void"
              },
              {
                "label": "+ 上传",
                "code": "数字供应链/合同管理/新增补协-框架合同#upload",
                "src": "新增补协-框架合同"
              },
              {
                "label": "提交",
                "code": "数字供应链/合同管理/新增补协-框架合同#submit",
                "src": "新增补协-框架合同"
              },
              {
                "label": "+ 上传",
                "code": "数字供应链/合同管理/新增补协-订单/单批次合同#upload",
                "src": "新增补协-订单/单批次合同"
              },
              {
                "label": "提交",
                "code": "数字供应链/合同管理/新增补协-订单/单批次合同#submit",
                "src": "新增补协-订单/单批次合同"
              }
            ]
          }
        ],
        "code": "menu:数字供应链/合同管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "业务线管理",
        "file": "business-line.html",
        "buttons": [
          "数据导出"
        ],
        "children": [],
        "code": "menu:数字供应链/业务线管理",
        "mergedMenus": [],
        "ops": [
          {
            "label": "数据导出",
            "code": "数字供应链/业务线管理#export"
          }
        ]
      },
      {
        "label": "收发货管理",
        "file": "shipment-out.html",
        "buttons": [
          "登记订单发货数据",
          "登记采购订单发运数据",
          "登记销售订单发运数据",
          "数据导出",
          "查看",
          "作废",
          "发起货转",
          "查看货转"
        ],
        "children": [
          {
            "label": "发货管理",
            "file": "shipment-out.html",
            "buttons": [
              "登记订单发货数据",
              "登记采购订单发运数据",
              "登记销售订单发运数据",
              "数据导出",
              "查看",
              "作废",
              "发起货转",
              "查看货转"
            ],
            "children": [],
            "code": "menu:数字供应链/收发货管理/发货管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "登记订单发货数据",
                "code": "数字供应链/收发货管理/发货管理#create"
              },
              {
                "label": "登记采购订单发运数据",
                "code": "数字供应链/收发货管理/发货管理#create2"
              },
              {
                "label": "登记销售订单发运数据",
                "code": "数字供应链/收发货管理/发货管理#create3"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/收发货管理/发货管理#export"
              },
              {
                "label": "查看",
                "code": "数字供应链/收发货管理/发货管理#view"
              },
              {
                "label": "作废",
                "code": "数字供应链/收发货管理/发货管理#void"
              },
              {
                "label": "发起货转",
                "code": "数字供应链/收发货管理/发货管理#transfer"
              },
              {
                "label": "查看货转",
                "code": "数字供应链/收发货管理/发货管理#view-transfer"
              }
            ]
          },
          {
            "label": "收货管理",
            "file": "shipment-in.html",
            "buttons": [
              "数据导出",
              "查看",
              "作废",
              "确认收货",
              "删除",
              "确认删除"
            ],
            "children": [],
            "code": "menu:数字供应链/收发货管理/收货管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "数据导出",
                "code": "数字供应链/收发货管理/收货管理#export"
              },
              {
                "label": "查看",
                "code": "数字供应链/收发货管理/收货管理#view"
              },
              {
                "label": "作废",
                "code": "数字供应链/收发货管理/收货管理#void"
              },
              {
                "label": "确认收货",
                "code": "数字供应链/收发货管理/收货管理#submit"
              },
              {
                "label": "删除",
                "code": "数字供应链/收发货管理/收货管理#delete"
              },
              {
                "label": "确认删除",
                "code": "数字供应链/收发货管理/收货管理#submit6"
              }
            ]
          }
        ],
        "code": "menu:数字供应链/收发货管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "货转管理",
        "file": "goods-transfer.html",
        "buttons": [
          "开具货转",
          "↑ 上传上游货转",
          "↓ 新增下游货转",
          "数据导出",
          "批量下载",
          "+ 上传",
          "确认上传",
          "查看",
          "上传已生效单据",
          "作废",
          "下载"
        ],
        "children": [],
        "code": "menu:数字供应链/货转管理",
        "mergedMenus": [],
        "ops": [
          {
            "label": "开具货转",
            "code": "数字供应链/货转管理#create"
          },
          {
            "label": "↑ 上传上游货转",
            "code": "数字供应链/货转管理#upload"
          },
          {
            "label": "↓ 新增下游货转",
            "code": "数字供应链/货转管理#transfer"
          },
          {
            "label": "数据导出",
            "code": "数字供应链/货转管理#export"
          },
          {
            "label": "批量下载",
            "code": "数字供应链/货转管理#export5"
          },
          {
            "label": "+ 上传",
            "code": "数字供应链/货转管理#upload6"
          },
          {
            "label": "确认上传",
            "code": "数字供应链/货转管理#submit"
          },
          {
            "label": "查看",
            "code": "数字供应链/货转管理#view"
          },
          {
            "label": "上传已生效单据",
            "code": "数字供应链/货转管理#upload9"
          },
          {
            "label": "作废",
            "code": "数字供应链/货转管理#void"
          },
          {
            "label": "下载",
            "code": "数字供应链/货转管理#export11"
          }
        ]
      },
      {
        "label": "资金管理",
        "file": "payment-list.html",
        "buttons": [
          "新增付款",
          "数据导出",
          "详情"
        ],
        "children": [
          {
            "label": "付款管理",
            "file": "payment-list.html",
            "buttons": [
              "新增付款",
              "数据导出",
              "详情"
            ],
            "children": [],
            "code": "menu:数字供应链/资金管理/付款管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增付款",
                "code": "数字供应链/资金管理/付款管理#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/资金管理/付款管理#export"
              },
              {
                "label": "详情",
                "code": "数字供应链/资金管理/付款管理#view"
              }
            ]
          },
          {
            "label": "退款管理",
            "file": "refund-list.html",
            "buttons": [
              "新增退款",
              "数据导出"
            ],
            "children": [],
            "code": "menu:数字供应链/资金管理/退款管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增退款",
                "code": "数字供应链/资金管理/退款管理#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/资金管理/退款管理#export"
              }
            ]
          },
          {
            "label": "回款管理",
            "file": "receipt-list.html",
            "buttons": [
              "新增回款",
              "数据导出",
              "详情",
              "删除",
              "撤回"
            ],
            "children": [
              {
                "label": "回款列表",
                "file": "receipt-list.html",
                "buttons": [
                  "新增回款",
                  "数据导出",
                  "详情",
                  "删除",
                  "撤回"
                ],
                "code": "menu:数字供应链/资金管理/回款管理/回款列表",
                "mergedMenus": [],
                "children": [],
                "ops": [
                  {
                    "label": "新增回款",
                    "code": "数字供应链/资金管理/回款管理/回款列表#create"
                  },
                  {
                    "label": "数据导出",
                    "code": "数字供应链/资金管理/回款管理/回款列表#export"
                  },
                  {
                    "label": "详情",
                    "code": "数字供应链/资金管理/回款管理/回款列表#view"
                  },
                  {
                    "label": "删除",
                    "code": "数字供应链/资金管理/回款管理/回款列表#delete"
                  },
                  {
                    "label": "撤回",
                    "code": "数字供应链/资金管理/回款管理/回款列表#withdraw"
                  }
                ]
              },
              {
                "label": "回款详情",
                "file": "receipt-detail.html",
                "buttons": [],
                "code": "menu:数字供应链/资金管理/回款管理/回款详情",
                "mergedMenus": [],
                "children": [],
                "ops": []
              },
              {
                "label": "回款审批详情",
                "file": "receipt-approval-detail.html",
                "buttons": [
                  "立即催办",
                  "审批通过",
                  "驳回审批"
                ],
                "code": "menu:数字供应链/资金管理/回款管理/回款审批详情",
                "mergedMenus": [],
                "children": [],
                "ops": [
                  {
                    "label": "立即催办",
                    "code": "数字供应链/资金管理/回款管理/回款审批详情#urge"
                  },
                  {
                    "label": "审批通过",
                    "code": "数字供应链/资金管理/回款管理/回款审批详情#approve"
                  },
                  {
                    "label": "驳回审批",
                    "code": "数字供应链/资金管理/回款管理/回款审批详情#reject"
                  }
                ]
              },
              {
                "label": "编辑回款",
                "file": "receipt-edit.html",
                "buttons": [
                  "上传",
                  "按比例分摊",
                  "全部现金",
                  "删除",
                  "提交"
                ],
                "code": "menu:数字供应链/资金管理/回款管理/编辑回款",
                "mergedMenus": [],
                "children": [],
                "ops": [
                  {
                    "label": "上传",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#upload"
                  },
                  {
                    "label": "按比例分摊",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#allocate"
                  },
                  {
                    "label": "全部现金",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#allocate3"
                  },
                  {
                    "label": "删除",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#delete"
                  },
                  {
                    "label": "提交",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#submit"
                  }
                ]
              }
            ],
            "code": "menu:数字供应链/资金管理/回款管理",
            "mergedMenus": [],
            "ops": []
          },
          {
            "label": "保证金管理",
            "file": "margin-pool.html",
            "buttons": [
              "登记保证金",
              "数据导出",
              "查看"
            ],
            "children": [
              {
                "label": "保证金明细",
                "file": "margin-pool.html",
                "buttons": [
                  "登记保证金",
                  "数据导出",
                  "查看"
                ],
                "code": "menu:数字供应链/资金管理/保证金管理/保证金明细",
                "mergedMenus": [],
                "children": [],
                "ops": [
                  {
                    "label": "登记保证金",
                    "code": "数字供应链/资金管理/保证金管理/保证金明细#create"
                  },
                  {
                    "label": "数据导出",
                    "code": "数字供应链/资金管理/保证金管理/保证金明细#export"
                  },
                  {
                    "label": "查看",
                    "code": "数字供应链/资金管理/保证金管理/保证金明细#view"
                  }
                ]
              },
              {
                "label": "保证金调整",
                "file": "margin-adjust.html",
                "buttons": [
                  "+ 选择销售订单（贸易）合同",
                  "+ 上传",
                  "提交"
                ],
                "code": "menu:数字供应链/资金管理/保证金管理/保证金调整",
                "mergedMenus": [],
                "children": [],
                "ops": [
                  {
                    "label": "+ 选择销售订单（贸易）合同",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整#transfer"
                  },
                  {
                    "label": "+ 上传",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整#upload"
                  },
                  {
                    "label": "提交",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整#submit"
                  }
                ]
              },
              {
                "label": "保证金调整记录",
                "file": "margin-adjust-detail.html",
                "buttons": [
                  "设置等比例冲抵货款比例",
                  "一键下载",
                  "下载",
                  "保存"
                ],
                "code": "menu:数字供应链/资金管理/保证金管理/保证金调整记录",
                "mergedMenus": [],
                "children": [],
                "ops": [
                  {
                    "label": "设置等比例冲抵货款比例",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#edit"
                  },
                  {
                    "label": "一键下载",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#export"
                  },
                  {
                    "label": "下载",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#export3"
                  },
                  {
                    "label": "保存",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#save"
                  }
                ]
              }
            ],
            "code": "menu:数字供应链/资金管理/保证金管理",
            "mergedMenus": [],
            "ops": []
          }
        ],
        "code": "menu:数字供应链/资金管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "结算单管理",
        "file": "settlement-purchase.html",
        "buttons": [
          "新增采购结算单",
          "数据导出"
        ],
        "children": [
          {
            "label": "采购结算",
            "file": "settlement-purchase.html",
            "buttons": [
              "新增采购结算单",
              "数据导出"
            ],
            "children": [],
            "code": "menu:数字供应链/结算单管理/采购结算",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增采购结算单",
                "code": "数字供应链/结算单管理/采购结算#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/结算单管理/采购结算#export"
              }
            ]
          },
          {
            "label": "销售结算",
            "file": "settlement-sales.html",
            "buttons": [
              "新增销售结算单",
              "数据导出"
            ],
            "children": [],
            "code": "menu:数字供应链/结算单管理/销售结算",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增销售结算单",
                "code": "数字供应链/结算单管理/销售结算#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/结算单管理/销售结算#export"
              }
            ]
          }
        ],
        "code": "menu:数字供应链/结算单管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "发票管理",
        "file": "invoice.html",
        "buttons": [
          "Excel 导出",
          "新增发票"
        ],
        "children": [
          {
            "label": "进项发票",
            "file": "invoice.html",
            "buttons": [
              "Excel 导出",
              "新增发票"
            ],
            "children": [],
            "code": "menu:数字供应链/发票管理/进项发票",
            "mergedMenus": [],
            "ops": [
              {
                "label": "Excel 导出",
                "code": "数字供应链/发票管理/进项发票#export"
              },
              {
                "label": "新增发票",
                "code": "数字供应链/发票管理/进项发票#create"
              }
            ]
          },
          {
            "label": "销项发票",
            "file": "invoice-out.html",
            "buttons": [
              "Excel 导出",
              "新增发票"
            ],
            "children": [],
            "code": "menu:数字供应链/发票管理/销项发票",
            "mergedMenus": [],
            "ops": [
              {
                "label": "Excel 导出",
                "code": "数字供应链/发票管理/销项发票#export"
              },
              {
                "label": "新增发票",
                "code": "数字供应链/发票管理/销项发票#create"
              }
            ]
          }
        ],
        "code": "menu:数字供应链/发票管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "盯市管理",
        "file": "market-price.html",
        "buttons": [],
        "children": [
          {
            "label": "盯市价格管理",
            "file": "market-price.html",
            "buttons": [],
            "children": [],
            "code": "menu:数字供应链/盯市管理/盯市价格管理",
            "mergedMenus": [],
            "ops": []
          }
        ],
        "code": "menu:数字供应链/盯市管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "追保函管理",
        "file": "bond-letter.html",
        "buttons": [
          "数据导出",
          "新增追保函",
          "作废",
          "详情",
          "上传附件",
          "撤回"
        ],
        "children": [],
        "code": "menu:数字供应链/追保函管理",
        "mergedMenus": [],
        "ops": [
          {
            "label": "数据导出",
            "code": "数字供应链/追保函管理#export"
          },
          {
            "label": "新增追保函",
            "code": "数字供应链/追保函管理#create"
          },
          {
            "label": "作废",
            "code": "数字供应链/追保函管理#void"
          },
          {
            "label": "详情",
            "code": "数字供应链/追保函管理#view"
          },
          {
            "label": "上传附件",
            "code": "数字供应链/追保函管理#upload"
          },
          {
            "label": "撤回",
            "code": "数字供应链/追保函管理#withdraw"
          }
        ]
      },
      {
        "label": "审批管理",
        "file": "approval-flow-list.html",
        "buttons": [
          "新建流程",
          "数据导出"
        ],
        "children": [
          {
            "label": "审批流程配置",
            "file": "approval-flow-list.html",
            "buttons": [
              "新建流程",
              "数据导出"
            ],
            "children": [],
            "code": "menu:数字供应链/审批管理/审批流程配置",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新建流程",
                "code": "数字供应链/审批管理/审批流程配置#op1"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/审批管理/审批流程配置#export"
              }
            ]
          },
          {
            "label": "流程编排画布",
            "file": "approval-flow-editor.html",
            "buttons": [
              "流程图预览",
              "保存",
              "下一步：流程设计",
              "上一步：基础信息",
              "完成"
            ],
            "children": [],
            "code": "menu:数字供应链/审批管理/流程编排画布",
            "mergedMenus": [],
            "ops": [
              {
                "label": "流程图预览",
                "code": "数字供应链/审批管理/流程编排画布#view"
              },
              {
                "label": "保存",
                "code": "数字供应链/审批管理/流程编排画布#save"
              },
              {
                "label": "下一步：流程设计",
                "code": "数字供应链/审批管理/流程编排画布#op3"
              },
              {
                "label": "上一步：基础信息",
                "code": "数字供应链/审批管理/流程编排画布#op4"
              },
              {
                "label": "完成",
                "code": "数字供应链/审批管理/流程编排画布#op5"
              }
            ]
          },
          {
            "label": "审批流程监控",
            "file": "approval-monitor.html",
            "buttons": [
              "数据导出",
              "立即催办",
              "撤回申请"
            ],
            "children": [],
            "code": "menu:数字供应链/审批管理/审批流程监控",
            "mergedMenus": [],
            "ops": [
              {
                "label": "数据导出",
                "code": "数字供应链/审批管理/审批流程监控#export"
              },
              {
                "label": "立即催办",
                "code": "数字供应链/审批管理/审批流程监控#urge"
              },
              {
                "label": "撤回申请",
                "code": "数字供应链/审批管理/审批流程监控#withdraw"
              }
            ]
          }
        ],
        "code": "menu:数字供应链/审批管理",
        "mergedMenus": [],
        "ops": []
      }
    ]
  },
  {
    "key": "仓储管理",
    "label": "仓储管理",
    "icon": "🏭",
    "subMenus": [
      {
        "label": "入库管理",
        "file": "warehouse-inbound.html",
        "buttons": [
          "新增入库",
          "数据导出",
          "确认进入"
        ],
        "children": [
          {
            "label": "入库记录",
            "file": "warehouse-inbound.html",
            "buttons": [
              "新增入库",
              "数据导出",
              "确认进入"
            ],
            "children": [],
            "code": "menu:仓储管理/入库管理/入库记录",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增入库",
                "code": "仓储管理/入库管理/入库记录#create"
              },
              {
                "label": "数据导出",
                "code": "仓储管理/入库管理/入库记录#export"
              },
              {
                "label": "确认进入",
                "code": "仓储管理/入库管理/入库记录#submit"
              }
            ]
          }
        ],
        "code": "menu:仓储管理/入库管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "出库管理",
        "file": "warehouse-outbound.html",
        "buttons": [
          "新增出库",
          "数据导出"
        ],
        "children": [
          {
            "label": "出库记录",
            "file": "warehouse-outbound.html",
            "buttons": [
              "新增出库",
              "数据导出"
            ],
            "children": [],
            "code": "menu:仓储管理/出库管理/出库记录",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增出库",
                "code": "仓储管理/出库管理/出库记录#create"
              },
              {
                "label": "数据导出",
                "code": "仓储管理/出库管理/出库记录#export"
              }
            ]
          }
        ],
        "code": "menu:仓储管理/出库管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "提放货管理",
        "file": "warehouse-pickup.html",
        "buttons": [
          "提货申请",
          "数据导出"
        ],
        "children": [
          {
            "label": "提货管理",
            "file": "warehouse-pickup.html",
            "buttons": [
              "提货申请",
              "数据导出"
            ],
            "children": [],
            "code": "menu:仓储管理/提放货管理/提货管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "提货申请",
                "code": "仓储管理/提放货管理/提货管理#create"
              },
              {
                "label": "数据导出",
                "code": "仓储管理/提放货管理/提货管理#export"
              }
            ]
          },
          {
            "label": "放货管理",
            "file": "warehouse-release.html",
            "buttons": [
              "新增放货指令",
              "数据导出"
            ],
            "children": [],
            "code": "menu:仓储管理/提放货管理/放货管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增放货指令",
                "code": "仓储管理/提放货管理/放货管理#create"
              },
              {
                "label": "数据导出",
                "code": "仓储管理/提放货管理/放货管理#export"
              }
            ]
          }
        ],
        "code": "menu:仓储管理/提放货管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "库存管理",
        "file": "warehouse-inventory.html",
        "buttons": [
          "数据导出",
          "入库明细",
          "出库明细",
          "详情"
        ],
        "children": [
          {
            "label": "库存台账",
            "file": "warehouse-inventory.html",
            "buttons": [
              "数据导出",
              "入库明细",
              "出库明细",
              "详情"
            ],
            "children": [],
            "code": "menu:仓储管理/库存管理/库存台账",
            "mergedMenus": [],
            "ops": [
              {
                "label": "数据导出",
                "code": "仓储管理/库存管理/库存台账#export"
              },
              {
                "label": "入库明细",
                "code": "仓储管理/库存管理/库存台账#view"
              },
              {
                "label": "出库明细",
                "code": "仓储管理/库存管理/库存台账#view3"
              },
              {
                "label": "详情",
                "code": "仓储管理/库存管理/库存台账#view4"
              }
            ]
          }
        ],
        "code": "menu:仓储管理/库存管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "视频监控",
        "file": "warehouse-video.html",
        "buttons": [
          "新增视频监控"
        ],
        "children": [
          {
            "label": "库点监控",
            "file": "warehouse-video.html",
            "buttons": [
              "新增视频监控"
            ],
            "children": [],
            "code": "menu:仓储管理/视频监控/库点监控",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增视频监控",
                "code": "仓储管理/视频监控/库点监控#create"
              }
            ]
          }
        ],
        "code": "menu:仓储管理/视频监控",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "巡库管理",
        "file": "warehouse-patrol.html",
        "buttons": [],
        "children": [
          {
            "label": "巡库记录",
            "file": "warehouse-patrol.html",
            "buttons": [],
            "children": [],
            "code": "menu:仓储管理/巡库管理/巡库记录",
            "mergedMenus": [],
            "ops": []
          }
        ],
        "code": "menu:仓储管理/巡库管理",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "系统管理",
        "file": "warehouse-system.html",
        "buttons": [
          "新增系统监控",
          "数据导出",
          "详情",
          "日志",
          "处理"
        ],
        "children": [
          {
            "label": "库点信息管理",
            "file": "warehouse-point.html",
            "buttons": [
              "监控信息",
              "上传合同"
            ],
            "children": [],
            "code": "menu:仓储管理/系统管理/库点信息管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "监控信息",
                "code": "仓储管理/系统管理/库点信息管理#view"
              },
              {
                "label": "上传合同",
                "code": "仓储管理/系统管理/库点信息管理#upload"
              }
            ]
          },
          {
            "label": "仓房管理",
            "file": "warehouse-warehouse.html",
            "buttons": [
              "新增仓房",
              "编辑",
              "货位"
            ],
            "children": [],
            "code": "menu:仓储管理/系统管理/仓房管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增仓房",
                "code": "仓储管理/系统管理/仓房管理#create"
              },
              {
                "label": "编辑",
                "code": "仓储管理/系统管理/仓房管理#edit"
              },
              {
                "label": "货位",
                "code": "仓储管理/系统管理/仓房管理#view"
              }
            ]
          },
          {
            "label": "品类配置",
            "file": "warehouse-category.html",
            "buttons": [
              "新增品类",
              "删除",
              "保存"
            ],
            "children": [],
            "code": "menu:仓储管理/系统管理/品类配置",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增品类",
                "code": "仓储管理/系统管理/品类配置#create"
              },
              {
                "label": "删除",
                "code": "仓储管理/系统管理/品类配置#delete"
              },
              {
                "label": "保存",
                "code": "仓储管理/系统管理/品类配置#save"
              }
            ]
          }
        ],
        "code": "menu:仓储管理/系统管理",
        "mergedMenus": [],
        "ops": []
      }
    ]
  },
  {
    "key": "数据中心",
    "label": "数据中心",
    "icon": "📊",
    "subMenus": [
      {
        "label": "驾驶舱",
        "file": "cockpit.html",
        "buttons": [],
        "children": [],
        "code": "menu:数据中心/驾驶舱",
        "mergedMenus": [],
        "ops": []
      },
      {
        "label": "项目台账表",
        "file": "report-project.html",
        "buttons": [
          "导出 Excel",
          "查看"
        ],
        "children": [],
        "code": "menu:数据中心/项目台账表",
        "mergedMenus": [],
        "ops": [
          {
            "label": "导出 Excel",
            "code": "数据中心/项目台账表#export"
          },
          {
            "label": "查看",
            "code": "数据中心/项目台账表#view"
          }
        ]
      },
      {
        "label": "业务线台账表",
        "file": "report-bizline.html",
        "buttons": [
          "导出 Excel",
          "列设置",
          "恢复默认",
          "查看"
        ],
        "children": [],
        "code": "menu:数据中心/业务线台账表",
        "mergedMenus": [],
        "ops": [
          {
            "label": "导出 Excel",
            "code": "数据中心/业务线台账表#export"
          },
          {
            "label": "列设置",
            "code": "数据中心/业务线台账表#view"
          },
          {
            "label": "恢复默认",
            "code": "数据中心/业务线台账表#view3"
          },
          {
            "label": "查看",
            "code": "数据中心/业务线台账表#view4"
          }
        ]
      },
      {
        "label": "资金占压表",
        "file": "report-fund.html",
        "buttons": [
          "数据导出"
        ],
        "children": [],
        "code": "menu:数据中心/资金占压表",
        "mergedMenus": [],
        "ops": [
          {
            "label": "数据导出",
            "code": "数据中心/资金占压表#export"
          }
        ]
      },
      {
        "label": "库存明细表",
        "file": "report-inventory.html",
        "buttons": [
          "数据导出"
        ],
        "children": [],
        "code": "menu:数据中心/库存明细表",
        "mergedMenus": [],
        "ops": [
          {
            "label": "数据导出",
            "code": "数据中心/库存明细表#export"
          }
        ]
      },
      {
        "label": "应收应付表",
        "file": "report-ar-ap.html",
        "buttons": [
          "导出 Excel",
          "数据导出"
        ],
        "children": [],
        "code": "menu:数据中心/应收应付表",
        "mergedMenus": [],
        "ops": [
          {
            "label": "导出 Excel",
            "code": "数据中心/应收应付表#export"
          },
          {
            "label": "数据导出",
            "code": "数据中心/应收应付表#export2"
          }
        ]
      },
      {
        "label": "合规验证报告管理",
        "file": "report-compliance.html",
        "buttons": [
          "数据导出",
          "查看报告"
        ],
        "children": [],
        "code": "menu:数据中心/合规验证报告管理",
        "mergedMenus": [],
        "ops": [
          {
            "label": "数据导出",
            "code": "数据中心/合规验证报告管理#export"
          },
          {
            "label": "查看报告",
            "code": "数据中心/合规验证报告管理#view"
          }
        ]
      }
    ]
  },
  {
    "key": "预警中心",
    "label": "预警中心",
    "icon": "🔔",
    "subMenus": [
      {
        "label": "预警管理",
        "file": "warning-list.html",
        "buttons": [
          "导出",
          "详情"
        ],
        "children": [],
        "code": "menu:预警中心/预警管理",
        "mergedMenus": [],
        "ops": [
          {
            "label": "导出",
            "code": "预警中心/预警管理#export"
          },
          {
            "label": "详情",
            "code": "预警中心/预警管理#view"
          }
        ]
      },
      {
        "label": "预警规则配置",
        "file": "warning-config.html",
        "buttons": [
          "添加规则",
          "编辑",
          "合同配置",
          "提交"
        ],
        "children": [],
        "code": "menu:预警中心/预警规则配置",
        "mergedMenus": [],
        "ops": [
          {
            "label": "添加规则",
            "code": "预警中心/预警规则配置#op1"
          },
          {
            "label": "编辑",
            "code": "预警中心/预警规则配置#edit"
          },
          {
            "label": "合同配置",
            "code": "预警中心/预警规则配置#op3"
          },
          {
            "label": "提交",
            "code": "预警中心/预警规则配置#submit"
          }
        ]
      }
    ]
  },
  {
    "key": "账户中心",
    "label": "账户中心",
    "icon": "👤",
    "subMenus": [
      {
        "label": "个人管理",
        "file": "account-personal.html",
        "buttons": [
          "新增个人中心"
        ],
        "children": [],
        "code": "menu:账户中心/个人管理",
        "mergedMenus": [],
        "ops": [
          {
            "label": "新增个人中心",
            "code": "账户中心/个人管理#create"
          }
        ]
      },
      {
        "label": "企业管理",
        "file": "account-company.html",
        "buttons": [
          "新增企业中心"
        ],
        "children": [
          {
            "label": "企业中心",
            "file": "account-company.html",
            "buttons": [
              "新增企业中心"
            ],
            "children": [],
            "code": "menu:账户中心/企业管理/企业中心",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增企业中心",
                "code": "账户中心/企业管理/企业中心#create"
              }
            ]
          },
          {
            "label": "角色权限管理",
            "file": "account-role-permission.html",
            "buttons": [
              "新增角色",
              "全选",
              "清空",
              "保存",
              "编辑该角色",
              "确认删除"
            ],
            "children": [],
            "code": "menu:账户中心/企业管理/角色权限管理",
            "mergedMenus": [],
            "ops": [
              {
                "label": "新增角色",
                "code": "账户中心/企业管理/角色权限管理#create"
              },
              {
                "label": "保存",
                "code": "账户中心/企业管理/角色权限管理#save"
              },
              {
                "label": "编辑该角色",
                "code": "账户中心/企业管理/角色权限管理#edit"
              },
              {
                "label": "确认删除",
                "code": "账户中心/企业管理/角色权限管理#submit"
              }
            ]
          }
        ],
        "code": "menu:账户中心/企业管理",
        "mergedMenus": [],
        "ops": []
      }
    ]
  }
];
