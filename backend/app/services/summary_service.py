"""
因果关系摘要生成服务
根据图结构复杂度动态生成不同风格的分析简报
"""

from openai import AsyncOpenAI
import os
import json
from typing import Dict, Any, Optional, Union
import asyncio

class SummaryGenerationService:
    """摘要生成服务"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        # 使用更快的模型生成摘要
        self.simple_model = os.getenv("OPENAI_SUMMARY_MODEL", "deepseek-chat")
        self.complex_model = os.getenv("OPENAI_MODEL", "deepseek-reasoner")
        
        # 超时设置（秒）
        self.timeout = 30
    
    def _calculate_complexity(self, analysis_result: Dict[str, Any]) -> str:
        """
        计算图的复杂度
        
        Args:
            analysis_result: 包含 nodes 和 edges 的分析结果
            
        Returns:
            "simple" 或 "complex"
        """
        edges_count = len(analysis_result.get("edges", []))
        
        if edges_count <= 2:
            return "simple"
        else:
            return "complex"
    
    def _build_simple_prompt(self, analysis_result: Dict[str, Any]) -> str:
        """构建简单场景的提示词"""
        
        data_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        
        prompt = f"""你是一个宏观分析师。请根据以下提取出的因果链数据，用【一句话】总结核心结论（直接说明某事件对某资产的利好/利空影响），不需要任何多余解释。

数据：
{data_json}

要求：
1. 只输出一句话，不要任何前缀或解释
2. 直接说明因果关系和影响
3. 语言简洁有力，突出核心观点
4. 如果涉及资产，明确说明利好或利空"""

        return prompt
    
    def _build_complex_prompt(self, analysis_result: Dict[str, Any]) -> str:
        """构建复杂场景的提示词"""
        
        data_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        
        prompt = f"""你是一个首席宏观策略师。请根据以下因果关系图数据，写一份结构化简报。

数据：
{data_json}

必须包含两个模块：
1. 核心传导路径：描述事件如何一步步影响资产，梳理完整的因果链条
2. 资产映射与策略：分析对不同资产类别的影响，给出策略建议

请以 JSON 格式输出，结构如下：
{{
    "type": "structured_analysis",
    "sections": [
        {{
            "title": "核心传导路径",
            "body": "详细描述因果传导机制..."
        }},
        {{
            "title": "资产映射与策略",
            "body": "分析资产影响和策略建议..."
        }}
    ]
}}

要求：
1. 严格按照上述 JSON 格式输出
2. 每个 section 的 body 要详细且有逻辑性
3. 突出关键节点和强因果关系
4. 策略建议要具体可操作"""

        return prompt
    
    async def _generate_simple_summary(self, analysis_result: Dict[str, Any]) -> str:
        """
        生成简单摘要（一句话总结）
        
        Returns:
            摘要字符串
        """
        prompt = self._build_simple_prompt(analysis_result)
        
        response = await self.client.chat.completions.create(
            model=self.simple_model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的宏观分析师，擅长用简洁的语言总结复杂的因果关系。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
    
    async def _generate_complex_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成复杂摘要（结构化分析）
        
        Returns:
            结构化摘要对象
        """
        prompt = self._build_complex_prompt(analysis_result)
        
        response = await self.client.chat.completions.create(
            model=self.complex_model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个首席宏观策略师，擅长撰写深度的结构化分析报告。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        try:
            summary = json.loads(content)
            return summary
        except json.JSONDecodeError:
            # 如果 JSON 解析失败，返回文本格式
            return {
                "type": "text",
                "content": content
            }
    
    async def generate_causal_summary(
        self, 
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        根据图结构动态生成文字简报
        
        Args:
            analysis_result: 包含 nodes 和 edges 的分析结果
            
        Returns:
            在原始结果基础上添加 summary 字段的新对象
        """
        
        # 复制原始结果，避免修改输入
        result = analysis_result.copy()
        
        try:
            # 1. 计算复杂度
            complexity = self._calculate_complexity(analysis_result)
            
            # 2. 根据复杂度选择不同的生成策略
            if complexity == "simple":
                # 简单场景：生成一句话摘要
                summary = await asyncio.wait_for(
                    self._generate_simple_summary(analysis_result),
                    timeout=self.timeout
                )
                result["summary"] = {
                    "type": "simple",
                    "complexity": complexity,
                    "content": summary
                }
            else:
                # 复杂场景：生成结构化分析
                summary = await asyncio.wait_for(
                    self._generate_complex_summary(analysis_result),
                    timeout=self.timeout
                )
                result["summary"] = {
                    "type": "complex",
                    "complexity": complexity,
                    "content": summary
                }
            
            return result
            
        except asyncio.TimeoutError:
            # 超时处理
            print(f"摘要生成超时（{self.timeout}秒）")
            result["summary"] = None
            return result
            
        except Exception as e:
            # 其他错误处理
            print(f"摘要生成失败: {str(e)}")
            result["summary"] = None
            return result
    
    async def generate_causal_summary_safe(
        self, 
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        安全版本：确保即使摘要生成失败也不影响主体数据返回
        
        这是推荐使用的版本，保证容错性
        """
        try:
            return await self.generate_causal_summary(analysis_result)
        except Exception as e:
            # 任何异常都不影响主体数据
            print(f"摘要生成完全失败: {str(e)}")
            result = analysis_result.copy()
            result["summary"] = None
            return result








