from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.services.causal_service import CausalService
from app.services.news_extraction_service import NewsExtractionService
from app.services.summary_service import SummaryGenerationService
from app.services.target_research_service import TargetResearchService
from app.services.streaming_research_service import StreamingTargetResearchService
from app.services.node_sensing_service import NodeSensingService
from app.services.enhanced_research_service import EnhancedTargetResearchService
from app.services.two_pass_causal_service import TwoPassCausalService

router = APIRouter()
causal_service = CausalService()
news_extraction_service = NewsExtractionService()
summary_service = SummaryGenerationService()
target_research_service = TargetResearchService()
streaming_research_service = StreamingTargetResearchService()
node_sensing_service = NodeSensingService()
enhanced_research_service = EnhancedTargetResearchService()
two_pass_service = TwoPassCausalService()

class CausalQuery(BaseModel):
    """因果推演查询请求"""
    query: str
    context: Optional[str] = None
    max_depth: Optional[int] = 3

class NewsExtractionRequest(BaseModel):
    """新闻因果关系提取请求"""
    news_text: str = Field(..., description="新闻文本内容", min_length=10)
    generate_summary: Optional[bool] = Field(True, description="是否生成摘要简报")

class TargetResearchRequest(BaseModel):
    """标的研究请求"""
    target: str = Field(..., description="标的名称（如：中证1000指数）", min_length=2)

class CausalNode(BaseModel):
    """因果图节点"""
    id: str
    label: str
    type: str  # cause, effect, intermediate, hypothesis, evidence
    description: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class CausalEdge(BaseModel):
    """因果图边"""
    source: str
    target: str
    label: Optional[str] = None
    description: Optional[str] = None
    strength: Optional[float] = Field(None, ge=0.0, le=1.0)

class AnalysisResult(BaseModel):
    """分析结果（标准接口）"""
    nodes: List[CausalNode]
    edges: List[CausalEdge]
    explanation: str
    metadata: Optional[Dict[str, Any]] = None

# 保持向后兼容
class CausalGraph(BaseModel):
    """因果图响应（旧版本，保持兼容）"""
    nodes: List[CausalNode]
    edges: List[CausalEdge]
    explanation: str

@router.post("/analyze", response_model=CausalGraph)
async def analyze_causal_chain(query: CausalQuery):
    """
    分析因果链（旧版本，保持兼容）
    """
    try:
        result = await causal_service.analyze(
            query.query, 
            query.context, 
            query.max_depth
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-v2")
async def analyze_causal_chain_v2(query: CausalQuery):
    """
    双阶段因果分析（推荐使用）
    
    Two-Pass Pipeline with Data Provenance:
    
    Pass 1: 生成因果图谱拓扑结构
    - LLM 分析因果关系
    - 每个节点包含 search_query 字段
    
    Pass 2: 动态富化 + 数据溯源
    - 并发调用搜索引擎（真实 API 或 Mock）
    - 解析搜索结果为 realtime_state
    - 注入 sources 数组（包含 title, url, domain）
    
    返回结构：
    {
        "nodes": [
            {
                "id": "n1",
                "label": "美元指数",
                "type": "cause",
                "search_query": "美元指数最新走势",
                "realtime_state": {
                    "latest_value": "103.5",
                    "sources": [
                        {
                            "title": "美元指数升至103.5",
                            "url": "https://www.reuters.com/...",
                            "domain": "reuters.com"
                        }
                    ],
                    "updated_at": "2024-02-19T10:30:00Z"
                }
            }
        ],
        "edges": [...],
        "explanation": "..."
    }
    
    特性：
    - ✅ 实时联网感知
    - ✅ 严格数据溯源
    - ✅ Mock 模式支持（无需真实 API 即可测试）
    - ✅ 并发处理提升性能
    """
    try:
        result = await two_pass_service.analyze_two_pass(
            query.query,
            query.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-causality")
async def extract_causality(request: NewsExtractionRequest):
    """
    从新闻文本中提取因果关系（支持动态生成摘要）
    
    接收新闻文本，调用大语言模型分析其中的因果关系，
    返回结构化的因果图数据（nodes 和 edges），并可选生成智能摘要
    
    Args:
        request: 包含 news_text 和 generate_summary 字段的请求体
        
    Returns:
        AnalysisResult: 包含 nodes、edges、explanation 和可选的 summary 字段
        
    Raises:
        HTTPException 400: 请求参数无效
        HTTPException 500: LLM 调用失败或 JSON 解析失败
        
    摘要生成逻辑：
        - edges <= 2: 简单场景，生成一句话总结
        - edges > 2: 复杂场景，生成结构化分析报告
        - 摘要生成失败不影响主体数据返回
    """
    try:
        # 1. 调用新闻提取服务，获取因果图数据
        result = await news_extraction_service.extract_causality(request.news_text)
        
        # 2. 如果需要生成摘要，调用摘要生成服务
        if request.generate_summary:
            result = await summary_service.generate_causal_summary_safe(result)
        
        # 3. 返回结果（包含可选的 summary 字段）
        return result
        
    except ValueError as e:
        # 参数验证错误或 JSON 解析错误
        raise HTTPException(
            status_code=400,
            detail=f"数据验证失败: {str(e)}"
        )
    except Exception as e:
        # 其他错误（API 调用失败等）
        raise HTTPException(
            status_code=500,
            detail=f"因果关系提取失败: {str(e)}"
        )

@router.post("/research-target/stream")
async def research_target_stream(request: TargetResearchRequest):
    """
    标的逆向推演与实时分析（流式版本）
    
    使用 Server-Sent Events (SSE) 实时推送分析进度
    
    执行三步走 Pipeline：
    1. 逆向因子提取与关键词生成
    2. 并发联网搜索获取最新动态
    3. 综合分析与因果图生成
    
    Args:
        request: 包含 target 字段的请求体
        
    Returns:
        StreamingResponse: text/event-stream 格式的流式响应
        
    事件格式：
        每行一个 JSON 对象，包含：
        - status: 状态标识 (start, step1_start, step1_complete, step2_start, 
                  step2_complete, step3_start, step3_complete, success, error)
        - message: 进度消息
        - data: 可选的数据负载
        - timestamp: 时间戳
        
    最终成功事件：
        {"status": "success", "message": "...", "data": {...完整的AnalysisResult...}}
    """
    
    async def event_generator():
        """生成 SSE 事件流"""
        try:
            async for event in streaming_research_service.stream_research_target(request.target):
                # 发送事件数据
                yield f"data: {event}\n\n"
        except Exception as e:
            # 发送错误事件
            import json
            error_event = json.dumps({
                "status": "error",
                "message": f"流式处理失败: {str(e)}",
                "timestamp": __import__('time').time()
            }, ensure_ascii=False)
            yield f"data: {error_event}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )

@router.post("/research-target")
async def research_target(request: TargetResearchRequest):
    """
    标的逆向推演与实时分析（非流式版本，保持向后兼容）
    
    执行三步走 Pipeline：
    1. 逆向因子提取与关键词生成
    2. 并发联网搜索获取最新动态
    3. 综合分析与因果图生成
    
    Args:
        request: 包含 target 字段的请求体
        
    Returns:
        完整的分析结果，包含：
        - nodes: 因果图节点
        - edges: 因果图边
        - explanation: 文字解释
        - metadata: 元数据（包含因子、搜索词、耗时等）
        
    Raises:
        HTTPException 400: 请求参数无效
        HTTPException 500: Pipeline 执行失败
    """
    try:
        # 执行完整的研究 Pipeline
        result = await target_research_service.research_target(request.target)
        
        return result
        
    except ValueError as e:
        # 参数验证错误
        raise HTTPException(
            status_code=400,
            detail=f"参数验证失败: {str(e)}"
        )
    except Exception as e:
        # Pipeline 执行错误
        raise HTTPException(
            status_code=500,
            detail=f"标的研究失败: {str(e)}"
        )

@router.post("/research-target-enhanced")
async def research_target_enhanced(request: TargetResearchRequest):
    """
    增强型标的研究 - 自动感知节点实时状态（推荐使用）
    
    完整的四步走 Pipeline：
    1. 因果分析 - 识别影响标的的核心因子
    2. 自动配置 - 为每个因子生成搜索查询
    3. 状态感知 - 并发获取所有因子的实时数据
    4. 综合报告 - 结合因果关系和实时状态生成深度分析
    
    与普通版本的区别：
    - ✅ 自动识别影响因子（如：美元指数、美联储利率）
    - ✅ 自动搜索每个因子的实时状态（如：美元指数当前值、趋势）
    - ✅ 生成包含实时数据的综合分析报告
    - ✅ 每个节点包含 current_state 字段
    
    示例：
    输入: "黄金价格"
    输出:
    - 节点1: 美元指数 (current_state: {value: "103.5", trend: "rising", ...})
    - 节点2: 美联储利率 (current_state: {value: "5.25%-5.50%", trend: "stable", ...})
    - 节点3: 地缘政治风险 (current_state: {value: "高", trend: "rising", ...})
    - 综合分析: "当前美元指数走强至103.5，美联储维持利率不变，地缘政治风险上升，
                 综合判断黄金价格面临下行压力但避险需求提供支撑..."
    
    Args:
        request: 包含 target 字段的请求体
        
    Returns:
        完整的分析结果，包含：
        - nodes: 因果图节点（每个节点包含 current_state）
        - edges: 因果图边
        - explanation: 综合分析报告（结合实时数据）
        - metadata: 元数据（包含耗时、状态更新统计等）
        
    Raises:
        HTTPException 400: 请求参数无效
        HTTPException 500: Pipeline 执行失败
    """
    try:
        # 执行增强型研究 Pipeline
        result = await enhanced_research_service.research_target_with_sensing(
            request.target
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"参数验证失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"增强型标的研究失败: {str(e)}"
        )

class NodeEnrichmentRequest(BaseModel):
    """节点状态更新请求"""
    nodes: List[Dict[str, Any]] = Field(..., description="需要更新状态的节点列表")

@router.post("/enrich-nodes")
async def enrich_nodes(request: NodeEnrichmentRequest):
    """
    节点自主感知 - 批量更新节点实时状态
    
    接收一个节点列表，为每个节点自动搜索最新信息并更新 current_state 字段。
    
    工作流程：
    1. 读取每个节点的 sensing_config.auto_queries 配置
    2. 并发调用搜索引擎 API（Tavily/Serper）获取最新数据
    3. 使用 LLM 将搜索结果解析为结构化状态
    4. 注入 current_state 字段到节点
    
    Args:
        request: 包含 nodes 数组的请求体
        
    Returns:
        更新后的节点列表，每个节点包含：
        - current_state: {
            value: string,           # 当前值（如 "5.25%" 或 "unknown"）
            trend: enum,             # rising/falling/stable
            narrative_context: string # 一句话背景说明
          }
        - last_updated: ISO 时间戳
        
    节点配置示例：
        {
            "id": "n1",
            "label": "美联储利率",
            "sensing_config": {
                "auto_queries": [
                    "美联储最新利率决议",
                    "Federal Reserve interest rate 2024"
                ]
            }
        }
        
    Raises:
        HTTPException 400: 请求参数无效
        HTTPException 500: 批量处理失败
    """
    try:
        if not request.nodes:
            raise ValueError("节点列表不能为空")
        
        # 批量并发处理节点状态更新
        enriched_nodes = await node_sensing_service.enrich_nodes_batch(request.nodes)
        
        return {
            "success": True,
            "total": len(enriched_nodes),
            "nodes": enriched_nodes
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"参数验证失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"节点状态更新失败: {str(e)}"
        )

@router.get("/examples")
async def get_examples():
    """
    获取示例查询
    """
    return {
        "examples": [
            "全球变暖会导致什么后果？",
            "经济衰退的原因是什么？",
            "人工智能发展对就业市场的影响"
        ],
        "target_examples": [
            "中证1000指数",
            "比特币",
            "特斯拉股票",
            "黄金期货",
            "人民币汇率"
        ],
        "node_sensing_example": {
            "id": "n1",
            "label": "美联储利率",
            "type": "cause",
            "sensing_config": {
                "auto_queries": [
                    "美联储最新利率决议 2024",
                    "Federal Reserve interest rate latest"
                ]
            }
        }
    }

