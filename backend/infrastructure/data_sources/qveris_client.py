# -*- coding: utf-8 -*-
"""
QVeris 真实世界数据源客户端
用于接入 QVeris AI Agent 提供的真实世界数据
"""
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class QVerisClient:
    """
    QVeris 数据源客户端
    
    提供与 QVeris AI Agent 的标准化接口，用于查询真实世界数据
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化 QVeris 客户端
        
        Args:
            api_key: QVeris API 密钥，如果不提供则从环境变量读取
            base_url: QVeris API 基础 URL，默认使用官方地址
        """
        self.api_key = api_key or os.getenv('QVERIS_API_KEY')
        if not self.api_key:
            raise ValueError(
                "QVeris API Key 未配置。请在 .env 文件中设置 QVERIS_API_KEY "
                "或在初始化时传入 api_key 参数"
            )
        
        # 设置基础 URL（根据 QVeris 实际 API 地址调整）
        self.base_url = base_url or os.getenv(
            'QVERIS_BASE_URL', 
            'https://api.qveris.com/v1'
        )
        
        # 设置请求超时时间（秒）
        self.timeout = 30
        
    def _get_headers(self) -> Dict[str, str]:
        """
        构建标准的 HTTP 请求头
        
        Returns:
            包含认证信息的请求头字典
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'CausalFlow-Engine/1.0'
        }
    
    def query_agent(self, prompt: str) -> Dict[str, Any]:
        """
        向 QVeris AI Agent 发送查询请求
        
        Args:
            prompt: 查询提示词，描述需要获取的数据
            
        Returns:
            标准化的响应字典，格式为：
            {
                "source": "QVeris",
                "raw_data": "原始响应文本",
                "status": "success" | "error",
                "error_message": "错误信息（仅在失败时存在）"
            }
            
        Example:
            >>> client = QVerisClient()
            >>> result = client.query_agent("查询最新的铜价数据")
            >>> print(result['status'])
            'success'
        """
        try:
            # 构建请求负载
            payload = {
                'prompt': prompt,
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            # 发送 POST 请求到 QVeris API
            response = requests.post(
                f'{self.base_url}/agent/query',
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            # 检查 HTTP 状态码
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            
            # 返回标准化格式
            return {
                'source': 'QVeris',
                'raw_data': response.text,
                'parsed_data': response_data,
                'status': 'success',
                'status_code': response.status_code
            }
            
        except requests.exceptions.HTTPError as e:
            # HTTP 错误（4xx, 5xx）
            return {
                'source': 'QVeris',
                'raw_data': None,
                'status': 'error',
                'error_message': f'HTTP 错误: {e.response.status_code} - {e.response.text}',
                'status_code': e.response.status_code if e.response else None
            }
            
        except requests.exceptions.Timeout:
            # 请求超时
            return {
                'source': 'QVeris',
                'raw_data': None,
                'status': 'error',
                'error_message': f'请求超时（超过 {self.timeout} 秒）'
            }
            
        except requests.exceptions.RequestException as e:
            # 其他网络错误
            return {
                'source': 'QVeris',
                'raw_data': None,
                'status': 'error',
                'error_message': f'网络请求失败: {str(e)}'
            }
            
        except Exception as e:
            # 未预期的错误
            return {
                'source': 'QVeris',
                'raw_data': None,
                'status': 'error',
                'error_message': f'未知错误: {str(e)}'
            }
    
    def query_with_context(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        带上下文的查询（高级功能）
        
        Args:
            prompt: 查询提示词
            context: 额外的上下文信息，如时间范围、数据类型等
            
        Returns:
            标准化的响应字典
        """
        try:
            payload = {
                'prompt': prompt,
                'context': context or {},
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            response = requests.post(
                f'{self.base_url}/agent/query',
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            return {
                'source': 'QVeris',
                'raw_data': response.text,
                'parsed_data': response_data,
                'status': 'success',
                'status_code': response.status_code
            }
            
        except Exception as e:
            return {
                'source': 'QVeris',
                'raw_data': None,
                'status': 'error',
                'error_message': str(e)
            }
    
    def health_check(self) -> bool:
        """
        检查 QVeris API 连接状态
        
        Returns:
            True 表示连接正常，False 表示连接失败
        """
        try:
            response = requests.get(
                f'{self.base_url}/health',
                headers=self._get_headers(),
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


# 便捷函数：快速创建客户端实例
def create_qveris_client() -> QVerisClient:
    """
    创建 QVeris 客户端实例的便捷函数
    
    Returns:
        配置好的 QVerisClient 实例
    """
    return QVerisClient()









