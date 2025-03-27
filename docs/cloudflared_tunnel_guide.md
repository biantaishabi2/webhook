# Cloudflared 临时隧道使用指南

本文档记录了如何配置、启动 Cloudflare 临时隧道并查找其公网 URL。

## 配置文件

临时隧道配置文件位于 `/etc/cloudflared/config.yml`：

```yaml
url: http://127.0.0.1:12345
protocol: http2
loglevel: debug
metrics: 127.0.0.1:20000
no-tls-verify: true
no-chunked-encoding: true
```

## 系统服务

服务配置文件位于 `/etc/systemd/system/cloudflared.service`：

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --config /etc/cloudflared/config.yml
Restart=always
RestartSec=5
StartLimitInterval=0

[Install]
WantedBy=multi-user.target
```

## 启动和管理隧道

启动隧道：
```bash
sudo systemctl start cloudflared.service
```

重启隧道（会生成新的临时 URL）：
```bash
sudo systemctl restart cloudflared.service
```

停止隧道：
```bash
sudo systemctl stop cloudflared.service
```

查看隧道状态：
```bash
sudo systemctl status cloudflared.service
```

## 查找临时隧道 URL

每次启动或重启服务，都会生成一个随机的 `trycloudflare.com` 子域名。查看方法：

```bash
sudo journalctl -u cloudflared.service | grep -E "https://.*?\.trycloudflare\.com"
```

或仅查看最近日志中的 URL：
```bash
sudo journalctl -u cloudflared.service --since "1 minute ago" | grep -E "https://.*?\.trycloudflare\.com"
```

## 临时隧道特点

1. **URL 不固定**：每次重启服务都会分配一个新的随机域名
2. **免费使用**：不需要 Cloudflare 账户即可使用
3. **无需配置 DNS**：自动使用 `*.trycloudflare.com` 子域名
4. **适合临时测试**：不适合生产环境长期使用

## 测试脚本

使用当前临时隧道 URL 的测试脚本位于：
```
/home/wangbo/document/wangbo/dev/webhook/test_cloudflare_webhook.sh
```

## 升级到永久隧道

如需固定域名，请使用 Cloudflare Zero Trust 控制台创建永久隧道，并配置 DNS CNAME 记录指向隧道（如已完成：webhook.biantaishabi.xyz）。