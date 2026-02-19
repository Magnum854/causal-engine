from openai import AsyncOpenAI
import os
import json
from typing import Optional

class CausalService:
    """因果推演服务"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
    
    async def analyze(self, query: str, context: Optional[str] = None, max_depth: int = 3):
        """
        分析因果关系并生成因果图
        """
        
        # 构建提示词
        prompt = self._build_prompt(query, context, max_depth)
        
        # 调用大模型
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的因果分析专家，擅长分析事件之间的因果关系，并以结构化的方式呈现。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        result = json.loads(response.choices[0].message.content)
        
        return result
    
    def _build_prompt(self, query: str, context: Optional[str], max_depth: int) -> str:
        """构建分析提示词"""
        
        prompt = f"""请分析以下问题的因果关系：

问题：{query}
"""
        
        if context:
            prompt += f"\n背景信息：{context}\n"
        
        prompt += f"""
请生成一个因果关系图，包含最多 {max_depth} 层的因果链。

返回格式为 JSON，包含以下字段：
{{
    "nodes": [
        {{
            "id": "节点唯一ID",
            "label": "节点标签（简短）",
            "type": "cause/effect/intermediate",
            "description": "节点详细描述"
        }}
    ],
    "edges": [
        {{
            "source": "源节点ID",
            "target": "目标节点ID",
            "label": "关系描述",
            "strength": 0.8  // 因果强度 0-1
        }}
    ],
    "explanation": "整体因果关系的文字解释"
}}

注意：
1. 节点ID使用简短的英文标识符（如 node1, node2）
2. 节点label使用中文，简洁明了
3. type 必须是 cause（原因）、effect（结果）或 intermediate（中间节点）之一
4. 因果强度 strength 表示因果关系的确定性程度
5. 确保返回的是有效的 JSON 格式
"""
        
        return prompt

