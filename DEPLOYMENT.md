# 因果推演引擎 - 部署指南

## 快速部署（Docker）

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+
- 域名（可选，用于 HTTPS）

### 部署步骤

#### 1. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
OPENAI_API_KEY=sk-3acec92e29fe4df383224c493f044c67
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-reasoner
```

#### 2. 修改前端 API 地址

编辑 `frontend/src/utils/streamClient.js` 和其他 API 调用文件，将：
```javascript
const API_BASE = 'http://localhost:8000'
```
改为：
```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://your-domain.com'
```

#### 3. 构建并启动服务

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 4. 验证部署

- 前端: http://your-domain.com
- 后端 API: http://your-domain.com:8000/docs
- 健康检查: http://your-domain.com:8000/health

---

## 传统部署（无 Docker）

### 服务器环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装 Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装 Nginx
sudo apt install nginx -y
```

### 后端部署

```bash
cd /var/www/因果引擎/backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
nano .env  # 填入 API 密钥

# 使用 systemd 管理服务
sudo nano /etc/systemd/system/causal-backend.service
```

**systemd 配置文件内容：**

```ini
[Unit]
Description=Causal Engine Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/因果引擎/backend
Environment="PATH=/var/www/因果引擎/backend/venv/bin"
ExecStart=/var/www/因果引擎/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable causal-backend
sudo systemctl start causal-backend
```

### 前端部署

```bash
cd /var/www/因果引擎/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 将构建产物复制到 Nginx 目录
sudo cp -r dist/* /var/www/html/
```

### Nginx 配置

```bash
sudo nano /etc/nginx/sites-available/causal-engine
```

**配置内容：**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # SSE 支持
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/causal-engine /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## HTTPS 配置（推荐）

### 使用 Let's Encrypt 免费证书

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 自动配置 HTTPS
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 性能优化建议

### 1. 后端优化
- 使用 Gunicorn + Uvicorn workers
- 配置连接池
- 启用 Redis 缓存（可选）

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 前端优化
- 启用 Gzip 压缩
- 配置 CDN（可选）
- 静态资源缓存

### 3. 数据库（未来扩展）
- 添加 PostgreSQL 存储历史分析
- 使用 Neo4j 持久化因果图谱

---

## 监控与日志

### 日志查看

```bash
# 后端日志
sudo journalctl -u causal-backend -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker 日志
docker-compose logs -f backend
```

### 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端访问测试
curl http://localhost
```

---

## 安全建议

1. **API 密钥保护**: 不要将 `.env` 文件提交到 Git
2. **防火墙配置**: 只开放 80/443 端口
3. **限流**: 配置 Nginx rate limiting
4. **CORS**: 生产环境限制允许的域名

---

## 故障排查

### 后端无法启动
```bash
# 检查端口占用
sudo lsof -i :8000

# 检查环境变量
cat backend/.env

# 查看详细错误
python backend/main.py
```

### 前端无法访问后端
- 检查 CORS 配置
- 确认 API_BASE_URL 正确
- 查看浏览器控制台错误

---

## 更新部署

```bash
# Docker 方式
git pull
docker-compose down
docker-compose build
docker-compose up -d

# 传统方式
git pull
cd backend && source venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart causal-backend
cd ../frontend && npm install && npm run build
sudo cp -r dist/* /var/www/html/
```

