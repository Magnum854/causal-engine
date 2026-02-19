@echo off
chcp 65001 >nul
echo ========================================
echo 因果引擎快速测试
echo ========================================
echo.

echo [1/2] 测试健康检查...
curl -s http://localhost:8000/health
echo.
echo.

echo [2/2] 测试因果分析 API...
curl -s -X POST http://localhost:8000/api/v1/analyze-v2 ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"黄金价格\",\"context\":null,\"max_depth\":3}" ^
  --max-time 60
echo.
echo.

echo ========================================
echo 测试完成
echo ========================================
pause

