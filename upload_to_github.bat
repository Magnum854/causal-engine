@echo off
chcp 65001 >nul
echo ================================
echo 因果引擎 - GitHub 上传脚本
echo ================================
echo.

REM 检查 Git 是否安装
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未检测到 Git，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] 检查 Git 配置...
git config --global user.name >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    set /p username="请输入你的 GitHub 用户名: "
    set /p email="请输入你的邮箱: "
    git config --global user.name "%username%"
    git config --global user.email "%email%"
    echo Git 配置完成！
)

echo [2/6] 初始化 Git 仓库...
if not exist .git (
    git init
    echo Git 仓库初始化完成
) else (
    echo Git 仓库已存在
)

echo [3/6] 添加文件到暂存区...
git add .

echo [4/6] 提交更改...
git commit -m "Initial commit: 因果引擎项目"

echo [5/6] 配置远程仓库...
echo.
echo 请先在 GitHub 创建一个新仓库，然后输入仓库地址
echo 格式: https://github.com/用户名/仓库名.git
echo.
set /p repo_url="请输入 GitHub 仓库地址: "

git remote remove origin >nul 2>nul
git remote add origin %repo_url%

echo [6/6] 推送到 GitHub...
git branch -M main
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================
    echo ✓ 上传成功！
    echo ================================
    echo.
    echo 你的项目已上传到: %repo_url%
    echo.
    echo 下一步可以：
    echo 1. 访问 https://railway.app 部署到公网
    echo 2. 访问 https://render.com 部署到公网
    echo 3. 查看 部署指南.md 了解更多部署方式
    echo.
) else (
    echo.
    echo [错误] 推送失败，请检查：
    echo 1. GitHub 仓库地址是否正确
    echo 2. 是否有权限访问该仓库
    echo 3. 网络连接是否正常
    echo.
    echo 如需使用 Token 登录：
    echo 1. 访问 https://github.com/settings/tokens
    echo 2. 生成新 token（勾选 repo 权限）
    echo 3. 推送时使用 token 作为密码
)

echo.
pause

