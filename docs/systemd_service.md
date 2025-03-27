# Webhook 系统服务管理

## 启动服务
```bash
sudo systemctl start webhook.service
```

## 停止服务
```bash
sudo systemctl stop webhook.service
```

## 重启服务
```bash
sudo systemctl restart webhook.service
```

## 查看服务状态
```bash
sudo systemctl status webhook.service
```

## 实时查看日志
```bash
sudo journalctl -u webhook.service -f
```

## 开机自启设置
```bash
# 启用开机自启
sudo systemctl enable webhook.service

# 禁用开机自启
sudo systemctl disable webhook.service
```