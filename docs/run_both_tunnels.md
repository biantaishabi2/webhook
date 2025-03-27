# 同时运行临时隧道和固定隧道的配置指南

本文档说明如何同时运行 Cloudflare 的临时隧道和永久隧道。

## 当前配置

### 临时隧道 (已配置并运行中)

- 配置文件: `/etc/cloudflared/config.yml`
- 服务名称: `cloudflared.service`
- 启动命令: `sudo systemctl start cloudflared.service`
- URL查找: `sudo journalctl -u cloudflared.service | grep -E "https://.*?\.trycloudflare\.com"`

### 永久隧道 (已配置但未启动)

- 隧道ID: `0a0bd0a5-fac8-47f7-894e-2f8213117b08`
- 服务安装命令: `sudo cloudflared service install eyJhIjoiNzdlNDgwMTNkZmUwMWZjMjlkZTUwZDQwNGUzMjUzN2YiLCJ0IjoiMGEwYmQwYTUtZmFjOC00N2Y3LTg5NGUtMmY4MjEzMTE3YjA4IiwicyI6IlkyUmtabVZoT0RZdFlqQmtNQzAwTm1Nd0xXSmtOR1F0TmpGbU5UWmpZV015TnpKaSJ9`
- 域名: `webhook.biantaishabi.xyz`

## 安全启动永久隧道

### 1. 确认服务名称

安装永久隧道后，系统会自动创建服务。检查具体名称：
```bash
sudo systemctl list-units | grep cloudflared
```

可能的名称包括：
- `cloudflared.service` (如果与临时隧道冲突)
- `cloudflared-tunnel.service`
- `cloudflared-<隧道ID>.service`
- 其他带有 cloudflared 前缀的服务

### 2. 处理可能的冲突

如果永久隧道服务与临时隧道冲突（同名为 `cloudflared.service`），有两个选项：

选项 1: 临时停止现有服务，测试永久隧道
```bash
# 停止临时隧道
sudo systemctl stop cloudflared.service

# 备份临时隧道配置
sudo cp /etc/cloudflared/config.yml /etc/cloudflared/temp_tunnel_config.yml.bak

# 启动服务（现在运行的将是永久隧道）
sudo systemctl start cloudflared.service

# 恢复临时隧道
sudo cp /etc/cloudflared/temp_tunnel_config.yml.bak /etc/cloudflared/config.yml
sudo systemctl restart cloudflared.service
```

选项 2: 修改永久隧道服务名称
```bash
# 停止服务（如果正在运行）
sudo systemctl stop cloudflared.service

# 编辑服务文件创建新名称
sudo cp /etc/systemd/system/cloudflared.service /etc/systemd/system/cloudflared-permanent.service
sudo systemctl daemon-reload
```

### 3. 安全启动和管理隧道

临时隧道管理:
```bash
# 启动临时隧道
sudo systemctl start cloudflared.service

# 重启临时隧道 (会生成新URL)
sudo systemctl restart cloudflared.service

# 停止临时隧道
sudo systemctl stop cloudflared.service
```

永久隧道管理（假设服务名为 cloudflared-permanent.service）:
```bash
# 启动永久隧道
sudo systemctl start cloudflared-permanent.service

# 重启永久隧道
sudo systemctl restart cloudflared-permanent.service

# 停止永久隧道
sudo systemctl stop cloudflared-permanent.service
```

### 4. 查看日志

临时隧道日志:
```bash
sudo journalctl -u cloudflared.service -f
```

永久隧道日志 (替换为实际服务名称):
```bash
sudo journalctl -u cloudflared-permanent.service -f
```

### 5. 测试访问

临时隧道 URL (每次重启变化):
```bash
sudo journalctl -u cloudflared.service | grep -E "https://.*?\.trycloudflare\.com" | tail -1
```

永久隧道 URL (固定):
```
https://webhook.biantaishabi.xyz
```

## 注意事项

1. **避免冲突**: 永久隧道安装可能会覆盖临时隧道的服务名称
2. **配置管理**: 
   - 临时隧道使用 `/etc/cloudflared/config.yml`
   - 永久隧道配置存储在您的 Cloudflare 账户中
3. **服务重启**: 两种隧道都可能服务于同一个本地端口(12345)，确保不同时运行它们
4. **URL 特性**:
   - 临时隧道每次重启生成新的随机 URL
   - 永久隧道 URL 固定为 webhook.biantaishabi.xyz
5. **安全测试**: 
   - 先备份所有配置文件和服务文件
   - 建议创建脚本以便快速切换不同隧道
6. **最佳实践**: 如果只需要一个固定地址，建议只用永久隧道

## 使用建议

长期使用: 仅使用永久隧道，减少维护复杂性
测试场景: 临时隧道方便快速测试，无需 DNS 配置