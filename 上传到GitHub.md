# 上传因果引擎到 GitHub 的步骤

## 前提条件

1. **安装 Git**
   - 下载：https://git-scm.com/download/win
   - 安装后重启终端

2. **注册 GitHub 账号**
   - 访问：https://github.com/signup

---

## 第一步：初始化 Git 仓库

打开 PowerShell 或 Git Bash，执行以下命令：

```powershell
# 进入项目目录
cd "X:\因果引擎"

# 初始化 Git 仓库
git init

# 配置用户信息（首次使用需要）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 因果引擎项目"
```

---

## 第二步：创建 GitHub 仓库

1. 登录 GitHub：https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `causal-engine` 或 `因果引擎`
   - Description: `因果推理引擎 - 基于多源数据的因果关系分析系统`
   - 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

---

## 第三步：推送到 GitHub

GitHub 会显示推送命令，复制执行：

```powershell
# 添加远程仓库（替换成你的用户名和仓库名）
git remote add origin https://github.com/你的用户名/causal-engine.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

如果需要登录，会弹出浏览器进行 GitHub 授权。

---

## 第四步：验证上传

访问你的 GitHub 仓库页面，应该能看到所有文件已上传。

---

## 常见问题

### 1. Git 命令不存在
**解决**：安装 Git 后重启终端
- 下载：https://git-scm.com/download/win

### 2. 推送时要求登录
**解决**：使用 Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → 勾选 `repo` 权限
3. 复制 token
4. 推送时用 token 作为密码

### 3. 文件太大无法上传
**解决**：检查是否有大文件
```powershell
# 查找大于 50MB 的文件
Get-ChildItem -Recurse | Where-Object {$_.Length -gt 50MB} | Select-Object FullName, Length
```

如果有大文件，添加到 `.gitignore`：
```
# 大文件
*.zip
*.tar.gz
*.model
```

### 4. 中文路径问题
**解决**：配置 Git 支持中文
```powershell
git config --global core.quotepath false
```

---

## 下一步：部署到公网

上传到 GitHub 后，可以选择以下部署方式：

### 方案 A：Railway（推荐，最简单）
1. 访问 https://railway.app
2. 用 GitHub 登录
3. New Project → Deploy from GitHub repo
4. 选择你的仓库
5. 自动部署完成

### 方案 B：Render
1. 访问 https://render.com
2. 连接 GitHub
3. New → Web Service
4. 选择仓库并配置

### 方案 C：云服务器
参考 `部署指南.md` 中的详细步骤

---

## 快速命令参考

```powershell
# 查看状态
git status

# 添加新文件
git add .

# 提交更改
git commit -m "更新说明"

# 推送到 GitHub
git push

# 拉取最新代码
git pull

# 查看提交历史
git log --oneline
```

---

## 需要帮助？

如果遇到问题，可以：
1. 查看 Git 官方文档：https://git-scm.com/doc
2. GitHub 帮助中心：https://docs.github.com
3. 或者告诉我具体的错误信息，我来帮你解决

