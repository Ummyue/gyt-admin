#!/usr/bin/env bash
# ===== Cloudflare Pages 部署脚本 =====
# 为什么需要它：`wrangler pages deploy .` 传的是**整个目录**，
# 包含 .offline-build/（整个站点的完整副本 + 4 组截图 + 离线包，约 28MB）
# 等本地产物，既拖慢部署、又把内部文件发布到公网。
# wrangler pages **不认 .assetsignore**（那是 Workers 静态资源的特性）。
#
# 做法：rsync 出「只含公开文件」的暂存目录，再从暂存目录部署。
#
# 用法：
#   CLOUDFLARE_API_TOKEN=<token> ./scripts/deploy_cf.sh
#
# 依赖：rsync（macOS 自带 openrsync 即可）、npx wrangler

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="yugangtong-prototype"
STAGE="$(mktemp -d /tmp/ygt-cf-stage-XXXXXX)"

echo "▸ 项目根目录: $ROOT"
echo "▸ 暂存目录:   $STAGE"

# ---- 1. 只同步公开内容 ----
# 排除：版本控制 / 本地构建产物 / 部署临时目录 / prototype-flow 运行时与 PRD 库
#       / agent 工作目录 / 离线压缩包
rsync -a \
  --exclude='.git/' \
  --exclude='.offline-build/' \
  --exclude='.deploy_tmp/' \
  --exclude='.prototype-flow/' \
  --exclude='prd-library/' \
  --exclude='local_tasks/' \
  --exclude='.work/' \
  --exclude='.session-handoff/' \
  --exclude='.wrangler/' \
  --exclude='.DS_Store' \
  --exclude='*.zip' \
  "$ROOT/" "$STAGE/"

# ---- 2. 统计 ----
N=$(find "$STAGE" -type f | wc -l | tr -d ' ')
MB=$(du -sm "$STAGE" | cut -f1)
echo "▸ 待上传: $N 个文件 / ${MB}MB"

# ---- 3. 部署 ----
echo "▸ 开始部署到 Cloudflare Pages（project=$PROJECT）…"
cd "$STAGE"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:?请先设置 CLOUDFLARE_API_TOKEN}" \
  npx --prefix "$ROOT" wrangler pages deploy . \
    --project-name="$PROJECT" \
    --skip-caching \
    --cwd="$STAGE"

# ---- 4. 清理暂存目录 ----
rm -rf "$STAGE"
echo "▸ 已清理暂存目录"
