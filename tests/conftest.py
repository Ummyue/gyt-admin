# -*- coding: utf-8 -*-
"""
v1.7.99.x 自动化 E2E 测试 fixture
- 启动 chromium headless
- 部署 URL 通过命令行参数传入（默认 v1.7.99.231 hotfix 部署 hash 63ddaa19）
"""
import os
import pytest
from playwright.sync_api import sync_playwright

CHROME = "/Users/fuyu/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

# 默认部署 hash（v1.7.99.231 hotfix 后）
DEFAULT_DEPLOY_HASH = "63ddaa19"
PROJECT = "/Users/fuyu/.minimax/agents/mavis/workspace/yugangtong-prototype"


def pytest_addoption(parser):
    parser.addoption(
        "--deploy-hash",
        action="store",
        default=os.environ.get("DEPLOY_HASH", DEFAULT_DEPLOY_HASH),
        help="CF Pages 部署 hash（默认 v1.7.99.231 hotfix）",
    )


@pytest.fixture(scope="session")
def deploy_url(request):
    h = request.config.getoption("--deploy-hash")
    return f"https://{h}.yugangtong-prototype.pages.dev"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, headless=True, args=["--no-sandbox"])
        yield b
        b.close()


@pytest.fixture
def context(browser):
    ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
    yield ctx
    ctx.close()


@pytest.fixture
def page(context, deploy_url):
    """默认打开 app.html 主页 + 注入 console 捕获"""
    p = context.new_page()
    p._deploy_url = deploy_url  # 注入供用例使用
    yield p
    p.close()
