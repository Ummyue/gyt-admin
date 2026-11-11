// 本文件由 scripts/extract_permissions.py 自动生成，请勿手工编辑
// 生成时间：2026-11-11 16:04:22
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
        "ops": [],
        "mergedMenus": []
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
        ],
        "mergedMenus": []
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
        ],
        "mergedMenus": []
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
          },
          {
            "label": "修改",
            "code": "准入管理/黑名单管理#edit"
          },
          {
            "label": "移入/解除",
            "code": "准入管理/黑名单管理#move"
          }
        ],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "新增框架合同",
                "code": "数字供应链/合同管理/采购合同#create-framework"
              },
              {
                "label": "新增单批次或订单合同",
                "code": "数字供应链/合同管理/采购合同#create-order"
              },
              {
                "label": "数据导出（框架合同）",
                "code": "数字供应链/合同管理/采购合同#export-framework"
              },
              {
                "label": "数据导出（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#export-order"
              },
              {
                "label": "合同详情（框架合同）",
                "code": "数字供应链/合同管理/采购合同#view-framework"
              },
              {
                "label": "合同详情（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#view-order"
              },
              {
                "label": "新增补充协议（框架合同）",
                "code": "数字供应链/合同管理/采购合同#create-supp-framework"
              },
              {
                "label": "新增补充协议（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#create-supp-order"
              },
              {
                "label": "发起合同完结（框架合同）",
                "code": "数字供应链/合同管理/采购合同#finish-framework"
              },
              {
                "label": "发起合同完结（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#finish-order"
              },
              {
                "label": "合同修改（框架合同）",
                "code": "数字供应链/合同管理/采购合同#edit-framework"
              },
              {
                "label": "合同修改（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#edit-order"
              },
              {
                "label": "合同作废（框架合同）",
                "code": "数字供应链/合同管理/采购合同#void-framework"
              },
              {
                "label": "合同作废（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#void-order"
              },
              {
                "label": "撤回审批（框架合同）",
                "code": "数字供应链/合同管理/采购合同#withdraw-framework"
              },
              {
                "label": "撤回审批（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#withdraw-order"
              },
              {
                "label": "上传双签合同（框架合同）",
                "code": "数字供应链/合同管理/采购合同#upload-sign-framework"
              },
              {
                "label": "上传双签合同（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#upload-sign-order"
              },
              {
                "label": "关联合同（订单或单批次）",
                "code": "数字供应链/合同管理/采购合同#relate"
              },
              {
                "label": "开票申请（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#invoice-apply"
              },
              {
                "label": "发起结算（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#settle-apply"
              },
              {
                "label": "开具货转（单批次或订单合同）",
                "code": "数字供应链/合同管理/采购合同#transfer-issue"
              }
            ],
            "mergedMenus": [
              {
                "label": "新增采购框架合同",
                "code": "menu:数字供应链/合同管理/新增采购框架合同",
                "opCount": 0
              },
              {
                "label": "新增采购订单/单批次合同",
                "code": "menu:数字供应链/合同管理/新增采购订单/单批次合同",
                "opCount": 0
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
            "ops": [
              {
                "label": "新增框架合同",
                "code": "数字供应链/合同管理/销售合同#create-framework"
              },
              {
                "label": "新增单批次或订单合同",
                "code": "数字供应链/合同管理/销售合同#create-order"
              },
              {
                "label": "数据导出（框架合同）",
                "code": "数字供应链/合同管理/销售合同#export-framework"
              },
              {
                "label": "数据导出（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#export-order"
              },
              {
                "label": "合同详情（框架合同）",
                "code": "数字供应链/合同管理/销售合同#view-framework"
              },
              {
                "label": "合同详情（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#view-order"
              },
              {
                "label": "新增补充协议（框架合同）",
                "code": "数字供应链/合同管理/销售合同#create-supp-framework"
              },
              {
                "label": "新增补充协议（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#create-supp-order"
              },
              {
                "label": "发起合同完结（框架合同）",
                "code": "数字供应链/合同管理/销售合同#finish-framework"
              },
              {
                "label": "发起合同完结（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#finish-order"
              },
              {
                "label": "合同修改（框架合同）",
                "code": "数字供应链/合同管理/销售合同#edit-framework"
              },
              {
                "label": "合同修改（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#edit-order"
              },
              {
                "label": "合同作废（框架合同）",
                "code": "数字供应链/合同管理/销售合同#void-framework"
              },
              {
                "label": "合同作废（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#void-order"
              },
              {
                "label": "撤回审批（框架合同）",
                "code": "数字供应链/合同管理/销售合同#withdraw-framework"
              },
              {
                "label": "撤回审批（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#withdraw-order"
              },
              {
                "label": "上传双签合同（框架合同）",
                "code": "数字供应链/合同管理/销售合同#upload-sign-framework"
              },
              {
                "label": "上传双签合同（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#upload-sign-order"
              },
              {
                "label": "关联合同（订单或单批次）",
                "code": "数字供应链/合同管理/销售合同#relate"
              },
              {
                "label": "开票申请（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#invoice-apply"
              },
              {
                "label": "发起结算（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#settle-apply"
              },
              {
                "label": "开具货转（单批次或订单合同）",
                "code": "数字供应链/合同管理/销售合同#transfer-issue"
              }
            ],
            "mergedMenus": [
              {
                "label": "新增销售框架合同",
                "code": "menu:数字供应链/合同管理/新增销售框架合同",
                "opCount": 0
              },
              {
                "label": "新增销售订单/单批次合同",
                "code": "menu:数字供应链/合同管理/新增销售订单/单批次合同",
                "opCount": 0
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
            "ops": [
              {
                "label": "新增补充协议（框架合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#create-framework"
              },
              {
                "label": "新增补充协议（订单或单批次合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#create-order"
              },
              {
                "label": "补协详情（框架合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#view-framework"
              },
              {
                "label": "补协详情（订单或单批次合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#view-order"
              },
              {
                "label": "修改补协（框架合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#edit-framework"
              },
              {
                "label": "修改补协（订单或单批次合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#edit-order"
              },
              {
                "label": "上传双签协议（框架合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#upload-sign-framework"
              },
              {
                "label": "上传双签协议（订单或单批次合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#upload-sign-order"
              },
              {
                "label": "作废补协（框架合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#void-framework"
              },
              {
                "label": "作废补协（订单或单批次合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#void-order"
              },
              {
                "label": "数据导出（框架合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#export-framework"
              },
              {
                "label": "数据导出（订单或单批次合同补充协议）",
                "code": "数字供应链/合同管理/补充协议#export-order"
              }
            ],
            "mergedMenus": [
              {
                "label": "新增补协-框架合同",
                "code": "menu:数字供应链/合同管理/新增补协-框架合同",
                "opCount": 0
              },
              {
                "label": "新增补协-订单/单批次合同",
                "code": "menu:数字供应链/合同管理/新增补协-订单/单批次合同",
                "opCount": 0
              }
            ]
          }
        ],
        "code": "menu:数字供应链/合同管理",
        "ops": [],
        "mergedMenus": []
      },
      {
        "label": "业务线管理",
        "file": "business-line.html",
        "buttons": [
          "数据导出"
        ],
        "children": [],
        "code": "menu:数字供应链/业务线管理",
        "ops": [
          {
            "label": "数据导出",
            "code": "数字供应链/业务线管理#export"
          },
          {
            "label": "解除业务线",
            "code": "数字供应链/业务线管理#unbind"
          },
          {
            "label": "申请业务完结",
            "code": "数字供应链/业务线管理#finish"
          },
          {
            "label": "一键下载附件",
            "code": "数字供应链/业务线管理#download-attach"
          },
          {
            "label": "监控查看",
            "code": "数字供应链/业务线管理#monitor"
          }
        ],
        "mergedMenus": []
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
            "ops": [
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
            ],
            "mergedMenus": []
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
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:数字供应链/收发货管理",
        "ops": [],
        "mergedMenus": []
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
        "ops": [
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
            "label": "上传货权转让协议",
            "code": "数字供应链/货转管理#upload-transfer-agreement"
          }
        ],
        "mergedMenus": []
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
              },
              {
                "label": "修改",
                "code": "数字供应链/资金管理/付款管理#edit"
              },
              {
                "label": "作废",
                "code": "数字供应链/资金管理/付款管理#void"
              },
              {
                "label": "撤回审批",
                "code": "数字供应链/资金管理/付款管理#withdraw"
              }
            ],
            "mergedMenus": []
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
            "ops": [
              {
                "label": "新增退款",
                "code": "数字供应链/资金管理/退款管理#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/资金管理/退款管理#export"
              },
              {
                "label": "修改",
                "code": "数字供应链/资金管理/退款管理#edit"
              },
              {
                "label": "作废",
                "code": "数字供应链/资金管理/退款管理#void"
              },
              {
                "label": "撤回审批",
                "code": "数字供应链/资金管理/退款管理#withdraw"
              }
            ],
            "mergedMenus": []
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
                  },
                  {
                    "label": "立即催办",
                    "code": "数字供应链/资金管理/回款管理/回款审批详情#urge",
                    "src": "回款审批详情"
                  },
                  {
                    "label": "审批通过",
                    "code": "数字供应链/资金管理/回款管理/回款审批详情#approve",
                    "src": "回款审批详情"
                  },
                  {
                    "label": "驳回审批",
                    "code": "数字供应链/资金管理/回款管理/回款审批详情#reject",
                    "src": "回款审批详情"
                  },
                  {
                    "label": "上传",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#upload",
                    "src": "编辑回款"
                  },
                  {
                    "label": "按比例分摊",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#allocate",
                    "src": "编辑回款"
                  },
                  {
                    "label": "全部现金",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#allocate3",
                    "src": "编辑回款"
                  },
                  {
                    "label": "删除",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#delete",
                    "src": "编辑回款"
                  },
                  {
                    "label": "提交",
                    "code": "数字供应链/资金管理/回款管理/编辑回款#submit",
                    "src": "编辑回款"
                  }
                ],
                "mergedMenus": [
                  {
                    "label": "回款详情",
                    "code": "menu:数字供应链/资金管理/回款管理/回款详情",
                    "opCount": 0
                  },
                  {
                    "label": "回款审批详情",
                    "code": "menu:数字供应链/资金管理/回款管理/回款审批详情",
                    "opCount": 3
                  },
                  {
                    "label": "编辑回款",
                    "code": "menu:数字供应链/资金管理/回款管理/编辑回款",
                    "opCount": 5
                  }
                ]
              }
            ],
            "code": "menu:数字供应链/资金管理/回款管理",
            "ops": [],
            "mergedMenus": []
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
                  },
                  {
                    "label": "+ 选择销售订单（贸易）合同",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整#transfer",
                    "src": "保证金调整"
                  },
                  {
                    "label": "+ 上传",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整#upload",
                    "src": "保证金调整"
                  },
                  {
                    "label": "提交",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整#submit",
                    "src": "保证金调整"
                  },
                  {
                    "label": "设置等比例冲抵货款比例",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#edit",
                    "src": "保证金调整记录"
                  },
                  {
                    "label": "一键下载",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#export",
                    "src": "保证金调整记录"
                  },
                  {
                    "label": "下载",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#export3",
                    "src": "保证金调整记录"
                  },
                  {
                    "label": "保存",
                    "code": "数字供应链/资金管理/保证金管理/保证金调整记录#save",
                    "src": "保证金调整记录"
                  }
                ],
                "mergedMenus": [
                  {
                    "label": "保证金调整",
                    "code": "menu:数字供应链/资金管理/保证金管理/保证金调整",
                    "opCount": 3
                  },
                  {
                    "label": "保证金调整记录",
                    "code": "menu:数字供应链/资金管理/保证金管理/保证金调整记录",
                    "opCount": 4
                  }
                ]
              }
            ],
            "code": "menu:数字供应链/资金管理/保证金管理",
            "ops": [],
            "mergedMenus": []
          }
        ],
        "code": "menu:数字供应链/资金管理",
        "ops": [],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "新增采购结算单",
                "code": "数字供应链/结算单管理/采购结算#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/结算单管理/采购结算#export"
              }
            ],
            "mergedMenus": []
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
            "ops": [
              {
                "label": "新增销售结算单",
                "code": "数字供应链/结算单管理/销售结算#create"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/结算单管理/销售结算#export"
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:数字供应链/结算单管理",
        "ops": [],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "Excel 导出",
                "code": "数字供应链/发票管理/进项发票#export"
              },
              {
                "label": "新增发票",
                "code": "数字供应链/发票管理/进项发票#create"
              }
            ],
            "mergedMenus": []
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
            "ops": [
              {
                "label": "Excel 导出",
                "code": "数字供应链/发票管理/销项发票#export"
              },
              {
                "label": "新增发票",
                "code": "数字供应链/发票管理/销项发票#create"
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:数字供应链/发票管理",
        "ops": [],
        "mergedMenus": []
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
            "ops": [],
            "mergedMenus": []
          }
        ],
        "code": "menu:数字供应链/盯市管理",
        "ops": [],
        "mergedMenus": []
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
        ],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "新建流程",
                "code": "数字供应链/审批管理/审批流程配置#op1"
              },
              {
                "label": "数据导出",
                "code": "数字供应链/审批管理/审批流程配置#export"
              },
              {
                "label": "流程图预览",
                "code": "数字供应链/审批管理/流程编排画布#view",
                "src": "流程编排画布"
              },
              {
                "label": "保存",
                "code": "数字供应链/审批管理/流程编排画布#save",
                "src": "流程编排画布"
              },
              {
                "label": "下一步：流程设计",
                "code": "数字供应链/审批管理/流程编排画布#op3",
                "src": "流程编排画布"
              },
              {
                "label": "上一步：基础信息",
                "code": "数字供应链/审批管理/流程编排画布#op4",
                "src": "流程编排画布"
              },
              {
                "label": "完成",
                "code": "数字供应链/审批管理/流程编排画布#op5",
                "src": "流程编排画布"
              }
            ],
            "mergedMenus": [
              {
                "label": "流程编排画布",
                "code": "menu:数字供应链/审批管理/流程编排画布",
                "opCount": 5
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
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:数字供应链/审批管理",
        "ops": [],
        "mergedMenus": []
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
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:仓储管理/入库管理",
        "ops": [],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "新增出库",
                "code": "仓储管理/出库管理/出库记录#create"
              },
              {
                "label": "数据导出",
                "code": "仓储管理/出库管理/出库记录#export"
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:仓储管理/出库管理",
        "ops": [],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "提货申请",
                "code": "仓储管理/提放货管理/提货管理#create"
              },
              {
                "label": "数据导出",
                "code": "仓储管理/提放货管理/提货管理#export"
              }
            ],
            "mergedMenus": []
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
            "ops": [
              {
                "label": "新增放货指令",
                "code": "仓储管理/提放货管理/放货管理#create"
              },
              {
                "label": "数据导出",
                "code": "仓储管理/提放货管理/放货管理#export"
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:仓储管理/提放货管理",
        "ops": [],
        "mergedMenus": []
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
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:仓储管理/库存管理",
        "ops": [],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "新增视频监控",
                "code": "仓储管理/视频监控/库点监控#create"
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:仓储管理/视频监控",
        "ops": [],
        "mergedMenus": []
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
            "ops": [],
            "mergedMenus": []
          }
        ],
        "code": "menu:仓储管理/巡库管理",
        "ops": [],
        "mergedMenus": []
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
            "ops": [
              {
                "label": "监控信息",
                "code": "仓储管理/系统管理/库点信息管理#view"
              },
              {
                "label": "上传合同",
                "code": "仓储管理/系统管理/库点信息管理#upload"
              }
            ],
            "mergedMenus": []
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
            ],
            "mergedMenus": []
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
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:仓储管理/系统管理",
        "ops": [],
        "mergedMenus": []
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
        "ops": [],
        "mergedMenus": []
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
        "ops": [
          {
            "label": "导出 Excel",
            "code": "数据中心/项目台账表#export"
          },
          {
            "label": "查看",
            "code": "数据中心/项目台账表#view"
          }
        ],
        "mergedMenus": []
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
        ],
        "mergedMenus": []
      },
      {
        "label": "资金占压表",
        "file": "report-fund.html",
        "buttons": [
          "数据导出"
        ],
        "children": [],
        "code": "menu:数据中心/资金占压表",
        "ops": [
          {
            "label": "数据导出",
            "code": "数据中心/资金占压表#export"
          }
        ],
        "mergedMenus": []
      },
      {
        "label": "库存明细表",
        "file": "report-inventory.html",
        "buttons": [
          "数据导出"
        ],
        "children": [],
        "code": "menu:数据中心/库存明细表",
        "ops": [
          {
            "label": "数据导出",
            "code": "数据中心/库存明细表#export"
          }
        ],
        "mergedMenus": []
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
        "ops": [
          {
            "label": "导出 Excel",
            "code": "数据中心/应收应付表#export"
          },
          {
            "label": "数据导出",
            "code": "数据中心/应收应付表#export2"
          }
        ],
        "mergedMenus": []
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
        "ops": [
          {
            "label": "数据导出",
            "code": "数据中心/合规验证报告管理#export"
          },
          {
            "label": "查看报告",
            "code": "数据中心/合规验证报告管理#view"
          }
        ],
        "mergedMenus": []
      }
    ]
  },
  {
    "key": "预警中心",
    "label": "预警中心",
    "icon": "🔔",
    "subMenus": [
      {
        "label": "预警查询",
        "file": "warning-list.html",
        "buttons": [
          "导出",
          "详情"
        ],
        "children": [],
        "code": "menu:预警中心/预警查询",
        "ops": [
          {
            "label": "导出",
            "code": "预警中心/预警查询#export"
          },
          {
            "label": "详情",
            "code": "预警中心/预警查询#view"
          }
        ],
        "mergedMenus": []
      },
      {
        "label": "预警设置",
        "file": "warning-config.html",
        "buttons": [
          "添加规则",
          "编辑",
          "合同配置",
          "提交"
        ],
        "children": [],
        "code": "menu:预警中心/预警设置",
        "ops": [
          {
            "label": "添加规则",
            "code": "预警中心/预警设置#op1"
          },
          {
            "label": "编辑",
            "code": "预警中心/预警设置#edit"
          },
          {
            "label": "合同配置",
            "code": "预警中心/预警设置#op3"
          },
          {
            "label": "提交",
            "code": "预警中心/预警设置#submit"
          }
        ],
        "mergedMenus": []
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
        "file": "",
        "buttons": [],
        "explicit_ops": null,
        "children": [
          {
            "label": "个人信息",
            "file": "account-personal.html",
            "buttons": [],
            "explicit_ops": [
              [
                "编辑资料",
                "edit"
              ],
              [
                "保存",
                "save"
              ],
              [
                "上传头像",
                "upload"
              ]
            ],
            "children": [],
            "code": "menu:账户中心/个人管理/个人信息",
            "ops": [
              {
                "label": "编辑资料",
                "code": "账户中心/个人管理/个人信息#edit"
              },
              {
                "label": "保存",
                "code": "账户中心/个人管理/个人信息#save"
              },
              {
                "label": "上传头像",
                "code": "账户中心/个人管理/个人信息#upload"
              }
            ],
            "mergedMenus": []
          },
          {
            "label": "安全设置",
            "file": "",
            "buttons": [],
            "explicit_ops": [
              [
                "修改登录密码",
                "update-password"
              ],
              [
                "更换绑定手机号",
                "bind-phone"
              ],
              [
                "更换绑定邮箱",
                "bind-email"
              ],
              [
                "查看登录设备",
                "view-device"
              ],
              [
                "退出其他设备",
                "logout-others"
              ]
            ],
            "children": [],
            "code": "menu:账户中心/个人管理/安全设置",
            "ops": [
              {
                "label": "修改登录密码",
                "code": "账户中心/个人管理/安全设置#update-password"
              },
              {
                "label": "更换绑定手机号",
                "code": "账户中心/个人管理/安全设置#bind-phone"
              },
              {
                "label": "更换绑定邮箱",
                "code": "账户中心/个人管理/安全设置#bind-email"
              },
              {
                "label": "查看登录设备",
                "code": "账户中心/个人管理/安全设置#view-device"
              },
              {
                "label": "退出其他设备",
                "code": "账户中心/个人管理/安全设置#logout-others"
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:账户中心/个人管理",
        "ops": [],
        "mergedMenus": []
      },
      {
        "label": "企业管理",
        "file": "",
        "buttons": [],
        "explicit_ops": null,
        "children": [
          {
            "label": "我的企业",
            "file": "",
            "buttons": [],
            "explicit_ops": [
              [
                "查看企业信息",
                "view"
              ],
              [
                "编辑企业信息",
                "edit"
              ],
              [
                "切换企业",
                "switch"
              ],
              [
                "提交认证",
                "submit-cert"
              ]
            ],
            "children": [],
            "code": "menu:账户中心/企业管理/我的企业",
            "ops": [
              {
                "label": "查看企业信息",
                "code": "账户中心/企业管理/我的企业#view"
              },
              {
                "label": "编辑企业信息",
                "code": "账户中心/企业管理/我的企业#edit"
              },
              {
                "label": "切换企业",
                "code": "账户中心/企业管理/我的企业#switch"
              },
              {
                "label": "提交认证",
                "code": "账户中心/企业管理/我的企业#submit-cert"
              }
            ],
            "mergedMenus": []
          },
          {
            "label": "企业账号管理",
            "file": "",
            "buttons": [],
            "explicit_ops": [
              [
                "新增账号",
                "create"
              ],
              [
                "编辑账号",
                "edit"
              ],
              [
                "删除账号",
                "delete"
              ],
              [
                "重置密码",
                "reset-password"
              ],
              [
                "分配角色",
                "assign-role"
              ],
              [
                "启用账号",
                "enable"
              ],
              [
                "停用账号",
                "disable"
              ],
              [
                "审核入职申请",
                "approve"
              ],
              [
                "审批邀请",
                "approve-invite"
              ],
              [
                "导出账号列表",
                "export"
              ]
            ],
            "children": [],
            "code": "menu:账户中心/企业管理/企业账号管理",
            "ops": [
              {
                "label": "新增账号",
                "code": "账户中心/企业管理/企业账号管理#create"
              },
              {
                "label": "编辑账号",
                "code": "账户中心/企业管理/企业账号管理#edit"
              },
              {
                "label": "删除账号",
                "code": "账户中心/企业管理/企业账号管理#delete"
              },
              {
                "label": "重置密码",
                "code": "账户中心/企业管理/企业账号管理#reset-password"
              },
              {
                "label": "分配角色",
                "code": "账户中心/企业管理/企业账号管理#assign-role"
              },
              {
                "label": "启用账号",
                "code": "账户中心/企业管理/企业账号管理#enable"
              },
              {
                "label": "停用账号",
                "code": "账户中心/企业管理/企业账号管理#disable"
              },
              {
                "label": "审核入职申请",
                "code": "账户中心/企业管理/企业账号管理#approve"
              },
              {
                "label": "审批邀请",
                "code": "账户中心/企业管理/企业账号管理#approve-invite"
              },
              {
                "label": "导出账号列表",
                "code": "账户中心/企业管理/企业账号管理#export"
              }
            ],
            "mergedMenus": []
          },
          {
            "label": "企业资料管理",
            "file": "account-company.html",
            "buttons": [],
            "explicit_ops": [
              [
                "编辑企业资料",
                "edit"
              ],
              [
                "上传资质文件",
                "upload"
              ],
              [
                "替换附件",
                "replace"
              ],
              [
                "删除附件",
                "delete"
              ],
              [
                "提交审核",
                "submit"
              ]
            ],
            "children": [],
            "code": "menu:账户中心/企业管理/企业资料管理",
            "ops": [
              {
                "label": "编辑企业资料",
                "code": "账户中心/企业管理/企业资料管理#edit"
              },
              {
                "label": "上传资质文件",
                "code": "账户中心/企业管理/企业资料管理#upload"
              },
              {
                "label": "替换附件",
                "code": "账户中心/企业管理/企业资料管理#replace"
              },
              {
                "label": "删除附件",
                "code": "账户中心/企业管理/企业资料管理#delete"
              },
              {
                "label": "提交审核",
                "code": "账户中心/企业管理/企业资料管理#submit"
              }
            ],
            "mergedMenus": []
          },
          {
            "label": "密码管理",
            "file": "",
            "buttons": [],
            "explicit_ops": [
              [
                "修改密码策略",
                "edit-policy"
              ],
              [
                "重置成员密码",
                "reset-password"
              ],
              [
                "强制成员下线",
                "force-logout"
              ]
            ],
            "children": [],
            "code": "menu:账户中心/企业管理/密码管理",
            "ops": [
              {
                "label": "修改密码策略",
                "code": "账户中心/企业管理/密码管理#edit-policy"
              },
              {
                "label": "重置成员密码",
                "code": "账户中心/企业管理/密码管理#reset-password"
              },
              {
                "label": "强制成员下线",
                "code": "账户中心/企业管理/密码管理#force-logout"
              }
            ],
            "mergedMenus": []
          },
          {
            "label": "角色权限管理",
            "file": "account-role-permission.html",
            "buttons": [],
            "explicit_ops": [
              [
                "新增角色",
                "create"
              ],
              [
                "保存",
                "save"
              ],
              [
                "编辑该角色",
                "edit"
              ],
              [
                "确认删除",
                "delete"
              ]
            ],
            "children": [],
            "code": "menu:账户中心/企业管理/角色权限管理",
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
                "code": "账户中心/企业管理/角色权限管理#delete"
              }
            ],
            "mergedMenus": []
          }
        ],
        "code": "menu:账户中心/企业管理",
        "ops": [],
        "mergedMenus": []
      }
    ]
  }
];
