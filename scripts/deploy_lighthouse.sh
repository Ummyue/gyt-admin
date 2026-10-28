#!/usr/bin/env bash
# ==========================================================================
# 豫港通高保真原型 · 腾讯云轻量应用服务器（Lighthouse）部署脚本
#                        —— **在服务器上执行**
#
# 目标机器： Ubuntu-M5MG / lhins-aiyspy7i / ap-beijing / 192.144.175.203
# 访问方式： http://192.144.175.203/   （域名未备案，暂只能用 IP 直连）
#
# 站点布局：
#   /var/www/yugangtong   豫港通原型（本脚本部署）
#   /var/www/fujingtang   福景堂站点（**本脚本不改动其目录与配置文件**）
#   http://192.144.175.203/       → 豫港通（本 server 块，server_name 匹配 IP）
#   http://192.144.175.203/fjt/   → 福景堂（alias 到其原目录）
#   fujingtang.conf 的 server_name _ 保持不变 → 其它 Host 头仍命中福景堂
#
# 用法（在服务器上，任意目录执行）：
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ummyue/gyt-admin/main/scripts/deploy_lighthouse.sh)"
#
# 环境变量可覆盖：
#   HOST_IP   服务器公网 IP（默认 192.144.175.203）—— 同时写入 server_name
#   WEBROOT   站点根目录（默认 /var/www/yugangtong）
#   SRC       源码临时目录（默认 /tmp/ygt-src）
# ==========================================================================
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Ummyue/gyt-admin.git}"
SRC="${SRC:-/tmp/ygt-src}"
WEBROOT="${WEBROOT:-/var/www/yugangtong}"
FJT_ROOT="${FJT_ROOT:-/var/www/fujingtang}"
NGINX_CONF="${NGINX_CONF:-/etc/nginx/conf.d/yugangtong.conf}"
HOST_IP="${HOST_IP:-192.144.175.203}"

say() { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
ok()  { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
err() { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; }

# ---------------------------------------------------------------- 1. 依赖
need() { command -v "$1" >/dev/null 2>&1; }
if ! need git || ! need rsync; then
  say "安装依赖 git / rsync"
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y git rsync
fi

# ---------------------------------------------------------------- 2. 拉源码
if [ ! -d "$SRC/.git" ]; then
  say "拉取源码 → $SRC"
  rm -rf "$SRC" 2>/dev/null || true
  git clone --depth 1 "$REPO_URL" "$SRC"
fi
cd "$SRC"
ok "源码版本： $(git log --oneline -1)"

# ---------------------------------------------------------------- 3. 同步文件
# 排除口径与 CF Pages 部署（scripts/deploy_cf.sh）保持一致：
# 内部工作笔记 / 构建产物 / 离线包 一律不对外发布
say "同步站点文件 → $WEBROOT"
sudo mkdir -p "$WEBROOT"
sudo rsync -a --delete \
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
  --exclude='*.docx' \
  --exclude='prd-build/' \
  --exclude='STATE.md' \
  ./ "$WEBROOT/"
ok "已同步 $(sudo find "$WEBROOT" -type f | wc -l | tr -d ' ') 个文件"

# ---------------------------------------------------------------- 4. nginx 配置
say "写入 nginx 站点配置 → $NGINX_CONF"
sudo tee "$NGINX_CONF" >/dev/null <<'NGINX_CONF_EOF'
server {
    listen       80;
    listen       [::]:80;

    # 只匹配 IP 直连；备案后把域名追加到这里（逗号分隔）即可
    server_name  __HOST_IP__;

    root   __WEBROOT__;
    index  index.html;
    charset utf-8;

    # ---- 静态资源缓存 ----
    location = /index.html { add_header Cache-Control "public, max-age=3600"; }
    location ~* \.(css|js)$ {
        add_header Cache-Control "public, max-age=604800";
    }
    location ~* \.(png|jpg|jpeg|gif|svg|webp|ico|woff2?)$ {
        add_header Cache-Control "public, max-age=2592000";
    }

    # ---- 压缩 ----
    gzip on;
    gzip_min_length 1k;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;

    # ---- 内部文件不对外 ----
    location ~ /\.          { deny all; }
    location = /STATE.md   { deny all; }
    location ~* ^/prd-library/ { deny all; }

    # ---- 福景堂站点：原目录与原配置均未改动，仅在此挂一个别名路径 ----
    location /fjt/ {
        alias __FJT_ROOT__/;
        index index.html;
        try_files $uri $uri/ /fjt/index.html;
    }
}
NGINX_CONF_EOF

sudo sed -i "s#__HOST_IP__#${HOST_IP}#g"  "$NGINX_CONF"
sudo sed -i "s#__WEBROOT__#${WEBROOT}#g"  "$NGINX_CONF"
sudo sed -i "s#__FJT_ROOT__#${FJT_ROOT}#g" "$NGINX_CONF"

say "nginx 配置校验"
sudo nginx -t
sudo systemctl reload nginx
ok "nginx 已重载"

# ---------------------------------------------------------------- 5. 自检
ok "部署完成，访问地址： http://${HOST_IP}/"
for p in / /index.html /app.html /pages/project-list.html /pages/receipt-list.html /shared/js/topnav-drawer.js /fjt/; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1${p}")
  printf '   %-42s %s\n' "$p" "$code"
done
