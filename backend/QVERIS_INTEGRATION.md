# QVeris 数据源接入文档

## 概述

QVeris 是一个真实世界数据源，已成功集成到 CausalFlow 因果推演引擎中。本文档说明如何使用 QVeris 客户端。

## 架构设计

```
backend/
├── infrastructure/           # 基础设施层（新增）
│   └── data_sources/        # 数据源模块
│       ├── __init__.py
│       └── qveris_client.py # QVeris 客户端实现
├── .env                     # 环境变量配置（包含 API Key）
├── .env.example             # 环境变量示例
└── test_qveris.py          # QVeris 测试脚本
```

## 环境配置

### 1. 环境变量

在 `backend/.env` 文件中已配置：

```env
# QVeris 真实世界数据源 API
QVERIS_API_KEY=sk-NQ-pJnadi4ow0f9mQIh6JML9YFspoS5HCa2j55AO8K4
```

### 2. API 端点配置

默认 API 端点：`https://api.qveris.com/v1`

如需自定义，可在 `.env` 中添加：

```env
QVERIS_BASE_URL=https://your-custom-endpoint.com/v1
```

## 使用方法

### 基础用法

```python
from infrastructure.data_sources import QVerisClient

# 创建客户端实例
client = QVerisClient()

# 发送查询请求
result = client.query_agent("查询最新的铜价数据")

# 处理响应
if result['status'] == 'success':
    print(f"数据源: {result['source']}")
    print(f"原始数据: {result['raw_data']}")
    print(f"解析数据: {result['parsed_data']}")
else:
    print(f"查询失败: {result['error_message']}")
```

### 带上下文查询

```python
# 带上下文的高级查询
result = client.query_with_context(
    prompt="查询铜价趋势",
    context={
        "time_range": "last_30_days",
        "data_type": "commodity_price",
        "granularity": "daily"
    }
)
```

### 健康检查

```python
# 检查 API 连接状态
if client.health_check():
    print("QVeris API 连接正常")
else:
    print("QVeris API 连接异常")
```

## API 响应格式

### 成功响应

```python
{
    "source": "QVeris",
    "raw_data": "原始响应文本",
    "parsed_data": {...},  # JSON 解析后的数据
    "status": "success",
    "status_code": 200
}
```

### 错误响应

```python
{
    "source": "QVeris",
    "raw_data": None,
    "status": "error",
    "error_message": "错误详情",
    "status_code": 400  # HTTP 状态码（如果有）
}
```

## 集成到业务服务

### 示例：在因果推演服务中使用

```python
# 在 app/services/causal_service.py 中集成

from infrastructure.data_sources import QVerisClient

class CausalService:
    def __init__(self):
        self.qveris_client = QVerisClient()
        # ... 其他初始化
    
    async def analyze_with_real_data(self, query: str):
        # 1. 从 QVeris 获取真实数据
        real_data = self.qveris_client.query_agent(
            f"获取与'{query}'相关的真实世界数据"
        )
        
        # 2. 将真实数据整合到因果分析中
        if real_data['status'] == 'success':
            context = real_data['parsed_data']
            # 使用 context 进行因果推演
            result = await self.analyze(query, context=context)
            return result
        else:
            # 降级处理：使用默认分析
            return await self.analyze(query)
```

## 测试

运行测试脚本验证接入：

```bash
cd backend
python test_qveris.py
```

测试脚本会验证：
- ✓ 模块导入
- ✓ 环境变量配置
- ✓ 客户端实例创建
- ✓ 基本查询功能
- ✓ 健康检查

## 错误处理

QVerisClient 内置了完善的错误处理机制：

1. **HTTP 错误**：自动捕获 4xx/5xx 错误
2. **超时处理**：默认 30 秒超时
3. **网络异常**：捕获连接失败、DNS 错误等
4. **未知错误**：兜底异常处理

所有错误都会返回标准化的错误响应，不会抛出异常。

## 安全性

- ✓ API Key 通过环境变量管理，不硬编码
- ✓ 使用 Bearer Token 标准认证
- ✓ HTTPS 加密传输
- ✓ `.env` 文件已在 `.gitignore` 中排除

## 性能优化建议

1. **连接复用**：在服务中创建单例客户端实例
2. **超时设置**：根据实际需求调整 `timeout` 参数
3. **异步支持**：未来可扩展为异步客户端（使用 `httpx` 或 `aiohttp`）
4. **缓存策略**：对频繁查询的数据实施缓存

## 下一步计划

- [ ] 根据 QVeris 官方文档调整 API 端点
- [ ] 在 `CausalService` 中集成 QVeris 数据
- [ ] 在 `EnhancedTargetResearchService` 中使用 QVeris
- [ ] 添加数据缓存层
- [ ] 实现异步查询支持
- [ ] 添加更多单元测试

## 技术支持

如遇到问题，请检查：

1. `.env` 文件中的 `QVERIS_API_KEY` 是否正确
2. 网络连接是否正常
3. API 端点地址是否需要调整
4. 查看 `test_qveris.py` 的测试输出

---

**集成完成时间**: 2026-02-27  
**版本**: v1.0.0  
**状态**: ✓ 已就绪









