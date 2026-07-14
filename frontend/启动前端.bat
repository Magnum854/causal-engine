@echo off
chcp 65001 >nul
echo ========================================
echo 因果引擎 - 动画修复完成！
echo ========================================
echo.
echo ✅ 已完成的修改：
echo    1. CausalGraph.jsx - 添加 framer-motion 动画
echo    2. NodeDetailDrawer.jsx - 优化抽屉组件
echo    3. framer-motion 已安装 (v11.18.2)
echo.
echo 🎬 动画效果：
echo    - 点击节点：图谱缩小至 75%%
echo    - 向左平移：-15%%
echo    - 背景模糊：4px
echo    - 抽屉滑入：从右侧弹出
echo    - 物理效果：自然回弹
echo.
echo ========================================
echo 正在启动前端服务...
echo ========================================
echo.

cd /d "%~dp0"
npm run dev

pause










