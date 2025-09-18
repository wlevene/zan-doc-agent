"""
文案重写大师Agent

专业的文案重写工具，基于给定的人设、场景和原始文案，生成优化后的文案内容。
"""

from typing import Dict, Any, Optional, List, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from dify.dify_client import DifyClient, DifyAPIError


class AgentType(Enum):
    """Agent 类型枚举"""
    CONTENT_VALIDATOR = "content_validator"  # 文案场景验收器
    SCENARIO_GENERATOR = "scenario_generator"  # 场景生成器
    CONTENT_REWRITER = "content_rewriter"  # 文案重写大师
    WELLNESS_MOM = "wellness_mom"  # 养生妈妈
    CUSTOM = "custom"  # 自定义类型


@dataclass
class AgentConfig:
    """Agent 配置信息"""
    name: str
    description: str
    agent_type: AgentType
    default_inputs: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


@dataclass
class AgentResponse:
    """Agent 响应信息"""
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class BaseAgent(ABC):
    """基础 Agent 抽象类
    
    所有具体的 Agent 都应该继承这个类，并实现相应的抽象方法。
    提供了统一的接口和基础功能，确保代码的一致性和可扩展性。
    """
    
    def __init__(self, dify_client: DifyClient, config: AgentConfig):
        """初始化 Agent"""
        self.client = dify_client
        self.config = config
        self._validate_config()
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        if not self.config.name:
            raise ValueError("Agent name cannot be empty")
        if not isinstance(self.config.agent_type, AgentType):
            raise ValueError("Invalid agent type")
    
    @abstractmethod
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """处理请求的抽象方法"""
        pass
    
    @abstractmethod
    def process_streaming(self, params: Dict[str, Any]) -> Iterator[AgentResponse]:
        """流式处理请求的抽象方法"""
        pass
    
    def _prepare_inputs(self, inputs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """准备输入参数，合并默认参数和用户参数"""
        final_inputs = {}
        
        # 添加默认参数
        if self.config.default_inputs:
            final_inputs.update(self.config.default_inputs)
        
        # 添加用户参数（覆盖默认参数）
        if inputs:
            final_inputs.update(inputs)
        
        return final_inputs
    
    def _handle_response(self, raw_response: Dict[str, Any]) -> AgentResponse:
        """处理 Dify API 响应"""
        try:
            # 提取响应内容
            content = raw_response.get('answer', '')
            
            # 提取元数据
            metadata = {
                'conversation_id': raw_response.get('conversation_id'),
                'message_id': raw_response.get('message_id'),
                'created_at': raw_response.get('created_at')
            }
            
            return AgentResponse(
                success=True,
                content=content,
                metadata=metadata,
                raw_response=raw_response
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=str(e),
                raw_response=raw_response
            )
    
    def _handle_streaming_response(self, response_chunk: Dict[str, Any]) -> AgentResponse:
        """处理流式响应块"""
        try:
            # 提取响应内容
            content = response_chunk.get('answer', '')
            
            # 提取元数据
            metadata = {
                'conversation_id': response_chunk.get('conversation_id'),
                'message_id': response_chunk.get('message_id'),
                'created_at': response_chunk.get('created_at')
            }
            
            return AgentResponse(
                success=True,
                content=content,
                metadata=metadata,
                raw_response=response_chunk
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=str(e),
                raw_response=response_chunk
            )
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Agent 信息"""
        return {
            'name': self.config.name,
            'description': self.config.description,
            'type': self.config.agent_type.value,
            'default_inputs': self.config.default_inputs
        }


class ContentRewriterAgent(BaseAgent):
    """文案重写大师Agent
    
    用于重写和优化文案内容，支持基于人设和场景的个性化重写。
    """
    
    def __init__(self, 
                 endpoint: str = "http://119.45.130.88:8080/v1",
                 app_key: str = "app-7aKaGK6AL5WXWdlDpwP7cgIF"):
        """初始化文案重写大师Agent
        
        Args:
            endpoint: Dify API 端点地址
            app_key: Dify 应用密钥
        """
        # 创建 DifyClient 实例
        dify_client = DifyClient(
            api_key=app_key,
            base_url=endpoint
        )
        
        config = AgentConfig(
            name="文案重写大师",
            description="专业的文案重写工具，基于人设和场景优化文案内容",
            agent_type=AgentType.CONTENT_REWRITER
        )
        
        super().__init__(dify_client, config)
    
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """重写文案内容
        
        Args:
            params: 参数字典，包含:
                - persona: 人设描述（必需）
                - scenario: 场景描述（必需）
                - query: 重写要求描述（可选，如果没有text参数则作为文案内容）
                - inputs: 额外输入参数（可选）
                - user: 用户标识（可选）
            
        Returns:
            AgentResponse: 文案重写结果
        """
        try:
            # 获取必需参数
            persona = params.get('persona')
            scenario = params.get('scenario')
            
            # 验证必需参数
            if not persona:
                return AgentResponse(
                    success=False,
                    content="",
                    error_message="缺少必需参数: persona"
                )
            
            if not scenario:
                return AgentResponse(
                    success=False,
                    content="",
                    error_message="缺少必需参数: scenario"
                )
         
            # 获取可选参数，处理text和query的兼容性
            text = params.get('query')  # 在非流式模式下，query参数实际是原始文案
        
            inputs = params.get('inputs')
            user = params.get('user', 'content_rewriter')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加核心参数到inputs中
            final_inputs["persona"] = persona
            final_inputs["scenario"] = scenario
            final_inputs["query"] = text
            
            # 将所有其他参数添加到inputs中（除了特殊参数）
            special_params = {'persona', 'scenario', 'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建查询
            full_query = self._build_rewrite_query(persona, scenario, text)
            
            # 调用 Dify API
            raw_response = self.client.completion_messages_blocking(
                query=full_query,
                inputs=final_inputs,
                user=user
            )
            
            return self._handle_response(raw_response)
            
        except DifyAPIError as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=f"Dify API调用失败: {str(e)}",
                raw_response={"error": str(e)}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=f"文案重写失败: {str(e)}",
                raw_response={"error": str(e)}
            )
    
    def process_streaming(self, params: Dict[str, Any]) -> Iterator[AgentResponse]:
        """流式重写文案内容
        
        Args:
            params: 参数字典，格式同process方法
            
        Yields:
            AgentResponse: 流式文案重写结果
        """
        try:
            # 获取必需参数
            persona = params.get('persona')
            scenario = params.get('scenario')
            text = params.get('text')
            
            # 验证必需参数
            if not persona or not scenario or not text:
                yield AgentResponse(
                    success=False,
                    content="",
                    error_message="缺少必需参数: persona, scenario, text"
                )
                return
            
            # 获取可选参数
            query = params.get('query', '请重写以下文案，使其更符合人设和场景要求')
            inputs = params.get('inputs')
            user = params.get('user', 'content_rewriter')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            final_inputs["persona"] = persona
            final_inputs["scenario"] = scenario
            final_inputs["text"] = text
            final_inputs["query"] = query
            
            # 将所有其他参数添加到inputs中
            special_params = {'persona', 'scenario', 'text', 'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建查询
            full_query = self._build_rewrite_query(persona, scenario, text, query)
            
            # 流式调用 Dify API
            for response in self.client.completion_messages_streaming(
                query=full_query,
                inputs=final_inputs,
                user=user
            ):
                yield self._handle_streaming_response(response)
                
        except DifyAPIError as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=f"Dify API调用失败: {str(e)}",
                raw_response={"error": str(e)}
            )
        except Exception as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=f"流式文案重写失败: {str(e)}",
                raw_response={"error": str(e)}
            )
    
    def _build_rewrite_query(self, persona: str, scenario: str, text: str) -> str:
        """构建文案重写查询
        
        Args:
            persona: 人设描述
            scenario: 场景描述
            query: 原始文案
            
        Returns:
            str: 完整的查询字符串
        """
        return f"""
人设信息：
{persona}

场景信息：
{scenario}

原始文案：
{text}
        """.strip()