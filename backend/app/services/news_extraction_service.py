from openai import AsyncOpenAI
import os
import json
from typing import Optional, Dict, Any
from app.prompts.system_prompts import NEWS_CAUSALITY_EXTRACTION_PROMPT

class NewsExtractionService:
    """新闻因果关系提取服务"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
    
    async def extract_causality(self, news_text: str) -> Dict[str, Any]:
        """
        从新闻文本中提取因果关系
        
        Args:
            news_text: 新闻文本内容
            
        Returns:
            包含 nodes、edges 和 explanation 的字典
            
        Raises:
            ValueError: 当 LLM 返回的 JSON 格式无效时
            Exception: 当 API 调用失败时
        """
        
        if not news_text or not news_text.strip():
            raise ValueError("新闻文本不能为空")
        
        # 构建用户提示词
        user_prompt = f"""请分析以下新闻文本中的因果关系：

【新闻内容】
{news_text}

【分析要求】
1. 识别新闻中所有的因果关系
2. 构建完整的因果推理图谱
3. 标注每个因果关系的强度和置信度
4. 提供整体的因果分析说明

请严格按照 JSON 格式返回结果。"""
        
        try:
            # 调用大模型 API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": NEWS_CAUSALITY_EXTRACTION_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.3,  # 降低温度以获得更稳定的输出
                response_format={"type": "json_object"}  # 强制 JSON 输出
            )
            
            # 获取响应内容
            content = response.choices[0].message.content
            
            if not content:
                raise ValueError("LLM 返回内容为空")
            
            # 解析 JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 解析失败: {str(e)}\n原始内容: {content[:200]}...")
            
            # 验证必需字段
            if "nodes" not in result:
                raise ValueError("返回结果缺少 'nodes' 字段")
            if "edges" not in result:
                raise ValueError("返回结果缺少 'edges' 字段")
            if "explanation" not in result:
                raise ValueError("返回结果缺少 'explanation' 字段")
            
            # 验证数据类型
            if not isinstance(result["nodes"], list):
                raise ValueError("'nodes' 必须是数组")
            if not isinstance(result["edges"], list):
                raise ValueError("'edges' 必须是数组")
            if not isinstance(result["explanation"], str):
                raise ValueError("'explanation' 必须是字符串")
            
            # 验证节点和边不为空
            if len(result["nodes"]) == 0:
                raise ValueError("节点列表不能为空")
            
            # 验证节点结构
            for i, node in enumerate(result["nodes"]):
                if "id" not in node or "label" not in node or "type" not in node:
                    raise ValueError(f"节点 {i} 缺少必需字段 (id, label, type)")
            
            # 验证边的引用
            node_ids = {node["id"] for node in result["nodes"]}
            for i, edge in enumerate(result["edges"]):
                if "source" not in edge or "target" not in edge:
                    raise ValueError(f"边 {i} 缺少必需字段 (source, target)")
                if edge["source"] not in node_ids:
                    raise ValueError(f"边 {i} 引用了不存在的源节点: {edge['source']}")
                if edge["target"] not in node_ids:
                    raise ValueError(f"边 {i} 引用了不存在的目标节点: {edge['target']}")
            
            return result
            
        except Exception as e:
            # 记录错误日志（生产环境中应使用专业的日志系统）
            print(f"因果关系提取失败: {str(e)}")
            raise








