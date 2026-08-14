# 豫港通原型 自动化 E2E 测试

## 跑测试

```bash
# 1. 装依赖（已完成可跳过）
pip3 install playwright pytest pytest-html

# 2. 跑测试（默认用 v1.7.99.231 hotfix 部署 hash）
cd /Users/fuyu/.minimax/agents/mavis/workspace/yugangtong-prototype/tests
python3 -m pytest -v

# 3. 指定部署 hash
python3 -m pytest -v --deploy-hash=<hash>

# 4. 看 HTML 报告
open reports/report.html
```

## 测试覆盖

- `e2e/test_workbench_todo.py` — 工作台 10 个待办 tab
  - 加载 + 10 tab 验证
  - 每个 tab 渲染 ≥ 1 行
  - 跨页跳转不 404（10 个 tab × 2-3 行 = 20+ href）
  - 总行数 20-30 合理性检查

## 部署 hash 来源

CF Pages 部署日志末尾的 URL：
```
https://<hash>.yugangtong-prototype.pages.dev
```

v1.7.99.x 最近 hash：
- v1.7.99.231 hotfix: `63ddaa19`
- v1.7.99.231: `9bd97fee`
- v1.7.99.230: `8007bcba`
- v1.7.99.229 hotfix: `308c683b`
- v1.7.99.229: `21497b36`
- v1.7.99.228: `9a903aee`

## 限制

- 项目是 mock 数据，**状态变化不持久化**（关页面就丢）
- 只能测"跨页跳转路径"和"单次会话内状态机切换"
- 不能测"业务流端到端"（需要真实后端）
