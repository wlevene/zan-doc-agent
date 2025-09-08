#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文案场景验收器 Agent
专门用于验收文案内容，检查文案是否符合特定的标准和要求
"""

from typing import Dict, Any, Optional, List, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from dify_client import DifyClient, DifyAPIError


class AgentType(Enum):
    """Agent 类型枚举"""
    CONTENT_VALIDATOR = "content_validator"  # 文案场景验收器
    SCENARIO_GENERATOR = "scenario_generator"  # 场景生成器
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
    """Agent 响应结果"""
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
        
        # 添加用户参数（会覆盖默认参数）
        if inputs:
            final_inputs.update(inputs)
        
        return final_inputs
    
    def _build_query(self, query: str, **kwargs) -> str:
        """构建查询字符串，子类可以重写此方法来自定义查询格式"""
        if self.config.system_prompt:
            return f"{self.config.system_prompt}\n\n{query}"
        return query
    
    def _handle_response(self, raw_response: Dict[str, Any]) -> AgentResponse:
        """处理原始响应，转换为 AgentResponse 格式"""
        try:
            content = raw_response.get('answer', '')
            metadata = {
                'message_id': raw_response.get('message_id'),
                'usage': raw_response.get('usage'),
                'retriever_resources': raw_response.get('retriever_resources', [])
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
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Agent 信息"""
        return {
            'name': self.config.name,
            'description': self.config.description,
            'type': self.config.agent_type.value,
            'default_inputs': self.config.default_inputs
        }


class ContentValidatorAgent(BaseAgent):
    """文案场景验收器 Agent
    
    专门用于验收文案内容，检查文案是否符合特定的标准和要求。
    可以检查语法、风格、合规性等多个维度。
    """
    
    def __init__(self, 
                 endpoint: str,
                 app_key: str):
        """
        初始化文案验收器
        
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
            name="文案场景验收器",
            description="专业的文案内容验收工具，支持多维度质量检查",
            agent_type=AgentType.CONTENT_VALIDATOR
        )
        
        super().__init__(dify_client, config)
    
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """验收文案内容
        
        Args:
            params: 参数字典，包含:
                - query: 验收要求描述（必需）
                - inputs: 额外输入参数（可选）
                - content_to_validate: 待验收的文案内容（可选）
                - user: 用户标识（可选）
            
        Returns:
            AgentResponse: 验收结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            content_to_validate = params.get('content_to_validate')
            user = params.get('user', 'content_validator')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加query到inputs中（某些Dify应用需要）
            final_inputs["query"] = query
            
            # 将所有其他参数添加到inputs中（除了特殊参数）
            special_params = {'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建查询
            full_query = self._build_validation_query(query, content_to_validate)
            
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
                error_message=f"API调用失败: {str(e)}"
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=f"处理失败: {str(e)}"
            )
    
    def process_streaming(self, params: Dict[str, Any]) -> Iterator[AgentResponse]:
        """流式验收文案内容
        
        Args:
            params: 参数字典，包含:
                - query: 验收要求描述（必需）
                - inputs: 额外输入参数（可选）
                - content_to_validate: 待验收的文案内容（可选）
                - user: 用户标识（可选）
        
        Yields:
            AgentResponse: 流式验收结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            content_to_validate = params.get('content_to_validate')
            user = params.get('user', 'content_validator')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加query到inputs中（某些Dify应用需要）
            final_inputs["query"] = query
            
            # 将所有其他参数添加到inputs中（除了特殊参数）
            special_params = {'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建查询
            full_query = self._build_validation_query(query, content_to_validate)
            
            # 流式调用 Dify API
            for chunk in self.client.completion_messages_streaming(
                query=full_query,
                inputs=final_inputs,
                user=user
            ):
                yield self._handle_response(chunk)
                
        except DifyAPIError as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=f"API调用失败: {str(e)}"
            )
        except Exception as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=f"处理失败: {str(e)}"
            )
    
    def _build_validation_query(self, query: str, content: Optional[str]) -> str:
        """构建验收查询"""
        base_query = self._build_query(query)
        
        if content:
            return f"{base_query}\n\n待验收内容：\n{content}"
        
        return base_query
    
    def validate_batch(self, 
                      contents: List[str], 
                      criteria: Optional[str] = None) -> List[AgentResponse]:
        """批量验收文案
        
        Args:
            contents: 待验收的文案列表
            criteria: 验收标准
            
        Returns:
            List[AgentResponse]: 验收结果列表
        """
        results = []
        
        for i, content in enumerate(contents):
            query = criteria or f"请对第{i+1}个文案进行验收"
            result = self.process({'query': query, 'content_to_validate': content})
            results.append(result)
        
        return results