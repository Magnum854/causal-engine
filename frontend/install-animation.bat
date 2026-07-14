@echo off
chcp 65001 >nul
echo ========================================
echo 前端动画优化 - 快速安装
echo ========================================

cd /d "%~dp0"

echo.
echo [1/3] 安装 framer-motion...
call npm install framer-motion

if errorlevel 1 (
    echo.
    echo ❌ 安装失败！
    echo 请检查网络连接或手动运行：npm install framer-motion
    pause
    exit /b 1
)

echo.
echo [2/3] 验证安装...
call npm list framer-motion

echo.
echo [3/3] 启动开发服务器...
echo.
echo ✅ 安装完成！
echo.
echo 动画特性：
echo   - 图谱缩放：75%% 等比例缩小
echo   - 向左位移：-15%%
echo   - 背景模糊：4px
echo   - 弹簧物理：自然回弹效果
echo.
echo 正在启动前端服务...
echo 访问地址：http://localhost:5173
echo.

call npm run dev










