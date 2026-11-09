# nginx 配置参考副本

| 文件 | 作用 | 维护方式 |
|---|---|---|
| `yf9club.conf` | **域名站点** `www.yf9.club` / `yf9.club`（HTTPS + ACME 校验 + 口令门禁 + 福景堂 `/fjt/` 别名） | ⚠️ **手工维护在服务器上**：`/etc/nginx/conf.d/yf9club.conf`。`scripts/deploy_lighthouse.sh` **不会**覆盖它 —— 本目录只是参考副本，改动需上服务器改并 `nginx -t && systemctl reload nginx` |
| IP 直连站点 | `http://192.144.175.203/`（豫港通） | 由 `scripts/deploy_lighthouse.sh` 自动生成到 `/etc/nginx/conf.d/yugangtong.conf`（模板在脚本里） |

## 缓存策略（2026-11-09 调整）

css / js / html 统一 `no-cache, must-revalidate`（带 ETag 协商，未变更回 304），
图片 `max-age=86400`。

⚠️ 此前 js/css 是 `max-age=604800`（**7 天强缓存**），导致用户浏览器一直拿旧版本文件，
而自动化验证每次用全新浏览器 profile（无缓存）测不出来 —— 假绿。
现在由 `scripts/verify_cache_freshness.py`（持久化 profile）专门守这条。
