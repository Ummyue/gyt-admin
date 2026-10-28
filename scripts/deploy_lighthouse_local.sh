#!/usr/bin/env bash
# ==========================================================================
# 豫港通高保真原型 · 腾讯云轻量服务器（192.144.175.203）**本机侧**一键部署
#
# 用法：
#   bash scripts/deploy_lighthouse_local.sh
#
# 做的事：
#   1. 按「对外发布口径」打包站点（排除内部工作笔记 / 构建产物 / 开发工具）
#   2. rsync 部署包 + 服务器端脚本到服务器（走 SSH 公钥，免密）
#   3. 在服务器上执行 deploy_lighthouse.sh：解包 → 写 nginx → nginx -t → reload → 自检
#
# 前置条件（已在 2026-10-28 完成）：
#   · 本机已有 SSH 私钥 ~/.ssh/id_lighthouse，公钥已写入服务器 ~/.ssh/authorized_keys
#   · 服务器已通过控制台 OrcaTerm「免密连接（TAT）」装好 nginx + rsync
#   · 服务器到 github.com 的 git 协议在境内会挂死 —— **本脚本不走 git clone**
#
# 常用环境变量：
#   HOST=192.144.175.203        服务器地址
#   SSH_KEY=~/.ssh/id_lighthouse 本机私钥
#   SSH_USER=ubuntu             SSH 用户（注意别用 USER，那是 bash 内置的本地用户名）
#   REMOTE_BUNDLE=/home/ubuntu/ygt-deploy.tar.gz
# ==========================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${HOST:-192.144.175.203}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_lighthouse}"
SSH_USER="${SSH_USER:-ubuntu}"
REMOTE_BUNDLE="${REMOTE_BUNDLE:-/home/ubuntu/ygt-deploy.tar.gz}"
PKG_DIR="$(mktemp -d /tmp/ygt-pkg-XXXXXX)"
# ⚠️ 压缩包必须放在 PKG_DIR 之外，否则 tar 会把自己打进去（"Can't add archive to itself"）
BUNDLE="$(mktemp /tmp/ygt-deploy-XXXXXX.tar.gz)"

blue() { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
green() { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
red() { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; }

SSH=(ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new)
RSYNC=(rsync -az -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=accept-new")

# ---------------------------------------------------------------- 0. 前置检查
[ -f "$SSH_KEY" ] || { red "找不到私钥 $SSH_KEY"; exit 1; }
"${SSH[@]}" "$SSH_USER@$HOST" true 2>/dev/null || {
  red "SSH 免密不通（$SSH_USER@${HOST}）。请确认服务器 ~/.ssh/authorized_keys 含 $SSH_KEY 的公钥。"; exit 1; }

# ---------------------------------------------------------------- 1. 打包
# 排除口径：内部工作笔记 / 构建产物 / 离线包 / 开发工具一律不对外发布
blue "打包站点（对外发布口径）"
rsync -a \
  --exclude='.git/' --exclude='.offline-build/' --exclude='.deploy_tmp/' \
  --exclude='.prototype-flow/' --exclude='prd-library/' --exclude='local_tasks/' \
  --exclude='.work/' --exclude='.session-handoff/' --exclude='.wrangler/' \
  --exclude='.DS_Store' --exclude='*.zip' --exclude='*.docx' \
  --exclude='prd-build/' --exclude='STATE.md' \
  --exclude='scripts/' --exclude='tests/' --exclude='wrangler.toml' \
  --exclude='_headers' --exclude='.assetsignore' --exclude='.gitignore' --exclude='README.md' \
  --exclude='._*' \
  "$ROOT/" "$PKG_DIR/"
# ⚠️ macOS 的 tar 会把扩展属性打包成 ._xxx（AppleDouble）文件，
#    在 Linux 上解出来是几百个垃圾文件还多占体积 → 必须 COPYFILE_DISABLE=1
COPYFILE_DISABLE=1 tar -czf "$BUNDLE" -C "$PKG_DIR" .
green "部署包： $(du -h "$BUNDLE" | cut -f1) / $(tar -tzf "$BUNDLE" | wc -l | tr -d ' ') 个条目"

# ---------------------------------------------------------------- 2. 上传
blue "上传到服务器 → $SSH_USER@${HOST}:$REMOTE_BUNDLE"
"${RSYNC[@]}" "$BUNDLE" "$SSH_USER@$HOST:$REMOTE_BUNDLE"
"${RSYNC[@]}" "$ROOT/scripts/deploy_lighthouse.sh" "$SSH_USER@$HOST:/home/ubuntu/deploy_lighthouse.sh"
green "上传完成"

# ---------------------------------------------------------------- 3. 服务器端部署
blue "执行服务器端部署脚本"
"${SSH[@]}" "$SSH_USER@$HOST" "BUNDLE=$REMOTE_BUNDLE bash /home/ubuntu/deploy_lighthouse.sh" | grep -vE "LIBARCHIVE|Ignoring unknown extended header"

green "完成 → http://$HOST/"

# 清理本地暂存
find "$PKG_DIR" -type f -delete 2>/dev/null || true
find "$PKG_DIR" -depth -type d -empty -delete 2>/dev/null || true
find "$BUNDLE" -type f -delete 2>/dev/null || true
