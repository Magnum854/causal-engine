# 因果引擎 - GitHub 上传脚本
# PowerShell 版本

Write-Host "================================" -ForegroundColor Cyan
Write-Host "因果引擎 - GitHub 上传脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
try {
    $null = Get-Command git -ErrorAction Stop
    Write-Host "[✓] Git 已安装" -ForegroundColor Green
} catch {
    Write-Host "[✗] 未检测到 Git，请先安装" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查 Git 配置
Write-Host ""
Write-Host "[1/6] 检查 Git 配置..." -ForegroundColor Yellow

$userName = git config --global user.name
$userEmail = git config --global user.email

if (-not $userName -or -not $userEmail) {
    Write-Host "需要配置 Git 用户信息" -ForegroundColor Yellow
    $userName = Read-Host "请输入你的 GitHub 用户名"
    $userEmail = Read-Host "请输入你的邮箱"
    
    git config --global user.name "$userName"
    git config --global user.email "$userEmail"
    git config --global core.quotepath false
    
    Write-Host "[✓] Git 配置完成" -ForegroundColor Green
} else {
    Write-Host "[✓] Git 已配置 ($userName <$userEmail>)" -ForegroundColor Green
}

# 初始化 Git 仓库
Write-Host ""
Write-Host "[2/6] 初始化 Git 仓库..." -ForegroundColor Yellow

if (-not (Test-Path ".git")) {
    git init
    Write-Host "[✓] Git 仓库初始化完成" -ForegroundColor Green
} else {
    Write-Host "[✓] Git 仓库已存在" -ForegroundColor Green
}

# 添加文件
Write-Host ""
Write-Host "[3/6] 添加文件到暂存区..." -ForegroundColor Yellow
git add .
Write-Host "[✓] 文件已添加" -ForegroundColor Green

# 提交
Write-Host ""
Write-Host "[4/6] 提交更改..." -ForegroundColor Yellow
$commitResult = git commit -m "Initial commit: 因果引擎项目" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] 提交成功" -ForegroundColor Green
} else {
    if ($commitResult -match "nothing to commit") {
        Write-Host "[!] 没有新的更改需要提交" -ForegroundColor Yellow
    } else {
        Write-Host "[✓] 提交完成" -ForegroundColor Green
    }
}

# 配置远程仓库
Write-Host ""
Write-Host "[5/6] 配置远程仓库..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请先在 GitHub 创建一个新仓库:" -ForegroundColor Cyan
Write-Host "1. 访问 https://github.com/new" -ForegroundColor White
Write-Host "2. 填写仓库名称（如: causal-engine）" -ForegroundColor White
Write-Host "3. 选择 Public 或 Private" -ForegroundColor White
Write-Host "4. 不要勾选 'Initialize this repository with a README'" -ForegroundColor White
Write-Host "5. 点击 'Create repository'" -ForegroundColor White
Write-Host ""
Write-Host "然后输入仓库地址，格式: https://github.com/用户名/仓库名.git" -ForegroundColor Cyan
Write-Host ""

$repoUrl = Read-Host "请输入 GitHub 仓库地址"

# 移除旧的 origin（如果存在）
git remote remove origin 2>$null

# 添加新的 origin
git remote add origin $repoUrl
Write-Host "[✓] 远程仓库已配置" -ForegroundColor Green

# 推送到 GitHub
Write-Host ""
Write-Host "[6/6] 推送到 GitHub..." -ForegroundColor Yellow
Write-Host "正在上传，请稍候..." -ForegroundColor Cyan

git branch -M main
$pushResult = git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✓ 上传成功！" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "你的项目已上传到: $repoUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "下一步可以：" -ForegroundColor Yellow
    Write-Host "1. 访问 https://railway.app 部署到公网（推荐）" -ForegroundColor White
    Write-Host "2. 访问 https://render.com 部署到公网" -ForegroundColor White
    Write-Host "3. 查看 部署指南.md 了解更多部署方式" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Red
    Write-Host "✗ 推送失败" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "1. GitHub 仓库地址不正确" -ForegroundColor White
    Write-Host "2. 没有权限访问该仓库" -ForegroundColor White
    Write-Host "3. 网络连接问题" -ForegroundColor White
    Write-Host "4. 需要使用 Personal Access Token 登录" -ForegroundColor White
    Write-Host ""
    Write-Host "使用 Token 登录的步骤：" -ForegroundColor Cyan
    Write-Host "1. 访问 https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "2. 点击 'Generate new token' → 'Tokens (classic)'" -ForegroundColor White
    Write-Host "3. 勾选 'repo' 权限" -ForegroundColor White
    Write-Host "4. 生成并复制 token" -ForegroundColor White
    Write-Host "5. 推送时使用 token 作为密码" -ForegroundColor White
    Write-Host ""
    Write-Host "错误信息：" -ForegroundColor Red
    Write-Host $pushResult -ForegroundColor Gray
}

Write-Host ""
Read-Host "按回车键退出"

