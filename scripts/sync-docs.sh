#!/bin/bash
# 豫港通 prototype 文档同步脚本
# 用法：./scripts/sync-docs.sh [module_code]  (不传则全量同步 16 个模块)
# 流程：源 MD → prototype/docs/ → wrangler pages deploy → 验证
set -e

PROJ_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="/Users/fuyu/.mavis/agents/mavis/workspace/yugangtong-design/02-模块设计"
DEST_DIR="$PROJ_DIR/docs"
# CF_TOKEN 从环境变量读取，禁止硬编码（v1.7.99.349.2 GitHub push protection 拦截）
CF_TOKEN="${CF_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
if [ -z "$CF_TOKEN" ]; then
  echo "❌ 未设置 CF_TOKEN 环境变量" >&2
  echo "   用法：CF_TOKEN=<token> ./scripts/sync-docs.sh [module_code]" >&2
  exit 1
fi
PROJECT="yugangtong-prototype"

# 02.01 拆成 list/apply/detail 3 个子文件
declare -A SPLIT_001=(
  ["02.01-list"]="02.01-项目管理-立项.md"
  ["02.01-apply"]="02.01-项目管理-立项.md"
  ["02.01-detail"]="02.01-项目管理-立项.md"
)

# 同步单文件到 prototype/docs
sync_file() {
  local code="$1" src_file="$2"
  if [ ! -f "$SRC_DIR/$src_file" ]; then
    echo "  ⚠️  源文件不存在：$src_file"
    return
  fi
  cp "$SRC_DIR/$src_file" "$DEST_DIR/$code.md"
  echo "  ✓ $code.md ← $src_file"
}

echo "==> 同步 docs/ 到 $DEST_DIR"

if [ -z "$1" ]; then
  # 全量同步：02.02-02.16（19 个原文件 + 02.01 拆 3 个）
  for f in "$SRC_DIR"/*.md; do
    name=$(basename "$f" .md)
    # 02.01 由外部单独处理（已拆 3 份）
    if [ "$name" = "02.01-项目管理-立项" ]; then continue; fi
    sync_file "$name" "$name.md"
  done
  echo "  (02.01 走 docs/02.01-list.md 等 3 份独立文件)"
else
  # 单模块同步
  case "$1" in
    02.01)
      sync_file "02.01-list" "02.01-项目管理-立项.md"
      sync_file "02.01-apply" "02.01-项目管理-立项.md"
      sync_file "02.01-detail" "02.01-项目管理-立项.md"
      ;;
    *)
      sync_file "$1" "$1.md"
      ;;
  esac
fi

echo ""
echo "==> 部署到 Cloudflare Pages"
cd "$PROJ_DIR"
CLOUDFLARE_API_TOKEN="$CF_TOKEN" npx wrangler pages deploy . --project-name="$PROJECT" 2>&1 | tail -5

echo ""
echo "==> 验证公网访问"
sleep 3
URL="https://yugangtong-prototype.pages.dev"
for path in "/" "/app.html" "/docs/02.01-list.md" "/docs/02.02-客户管理.md"; do
  code=$(curl -s -L -o /dev/null -w "%{http_code}" --max-time 10 "$URL$path")
  echo "  $code $URL$path"
done

echo ""
echo "✅ Done."
