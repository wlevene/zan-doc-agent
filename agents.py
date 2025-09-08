#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Agent 封装模块
基于 DifyClient 实现特定业务场景的 Agent，提供可扩展的架构
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Iterator, Union
from dataclasses import dataclass
from enum import Enum
import json

from dify_client import DifyClient, DifyAPIError, FileInfo, ResponseMode


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
    
    def __init__(self, dify_client: DifyClient, config: AgentConfig, dify_params: Optional[Dict[str, Any]] = None):
        """
        初始化 Agent
        
        Args:
            dify_client: Dify API 客户端实例
            config: Agent 配置信息
            dify_params: 传递给Dify API的额外参数
        """
        self.client = dify_client
        self.config = config
        self.dify_params = dify_params or {}
        self._validate_config()
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        if not self.config.name:
            raise ValueError("Agent name cannot be empty")
        if not isinstance(self.config.agent_type, AgentType):
            raise ValueError("Invalid agent type")
    
    @abstractmethod
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """处理请求的抽象方法
        
        Args:
            params: 包含所有参数的字典，必须包含'query'字段
                   - query: 用户查询内容
                   - inputs: 输入参数（可选）
                   - 其他业务相关参数
            
        Returns:
            AgentResponse: 处理结果
        """
        pass
    
    @abstractmethod
    def process_streaming(self, params: Dict[str, Any]) -> Iterator[AgentResponse]:
        """流式处理请求的抽象方法
        
        Args:
            params: 包含所有参数的字典，必须包含'query'字段
                   - query: 用户查询内容
                   - inputs: 输入参数（可选）
                   - 其他业务相关参数
            
        Yields:
            AgentResponse: 流式处理结果
        """
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
                 app_key: str,
                 validation_criteria: Optional[List[str]] = None,
                 dify_params: Optional[Dict[str, Any]] = None):
        """
        初始化文案验收器
        
        Args:
            endpoint: Dify API 端点地址
            app_key: Dify 应用密钥
            validation_criteria: 验收标准列表
            dify_params: 传递给Dify API的额外参数
        """
        # 创建 DifyClient 实例
        dify_client = DifyClient(
            api_key=app_key,
            base_url=endpoint
        )
        self.validation_criteria = validation_criteria or [
            "语法正确性",
            "内容准确性", 
            "风格一致性",
            "合规性检查"
        ]
        
        config = AgentConfig(
            name="文案场景验收器",
            description="专业的文案内容验收工具，支持多维度质量检查",
            agent_type=AgentType.CONTENT_VALIDATOR,
            default_inputs={
                "validation_criteria": self.validation_criteria,
                "output_format": "structured"
            },
            system_prompt="你是一个专业的文案验收专家，请根据提供的验收标准对文案进行全面评估。"
        )
        
        super().__init__(dify_client, config, dify_params)
    
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
            # 验证必需参数
            if 'query' not in params:
                raise ValueError("Missing required parameter: query")
            
            query = params['query']
            inputs = params.get('inputs')
            content_to_validate = params.get('content_to_validate')
            user = params.get('user', 'content_validator')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 如果提供了待验收内容，添加到输入中
            if content_to_validate:
                final_inputs["content_to_validate"] = content_to_validate
            
            # 构建查询
            full_query = self._build_validation_query(query, content_to_validate)
            
            # 合并dify_params到inputs中
            if self.dify_params:
                final_inputs.update(self.dify_params)
            
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
            # 验证必需参数
            if 'query' not in params:
                raise ValueError("Missing required parameter: query")
            
            query = params['query']
            inputs = params.get('inputs')
            content_to_validate = params.get('content_to_validate')
            user = params.get('user', 'content_validator')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            if content_to_validate:
                final_inputs["content_to_validate"] = content_to_validate
            
            # 构建查询
            full_query = self._build_validation_query(query, content_to_validate)
            
            # 合并dify_params到inputs中
            if self.dify_params:
                final_inputs.update(self.dify_params)
            
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
            result = self.process(query, content_to_validate=content)
            results.append(result)
        
        return results


class ScenarioGeneratorAgent(BaseAgent):
    """场景生成器 Agent
    
    专门用于生成各种场景内容，如营销场景、用户故事、测试用例等。
    支持根据不同的参数和模板生成定制化的场景内容。
    """
    
    def __init__(self, 
                 endpoint: str,
                 app_key: str,
                 scenario_types: Optional[List[str]] = None,
                 dify_params: Optional[Dict[str, Any]] = None):
        """
        初始化场景生成器
        
        Args:
            endpoint: Dify API 端点地址
            app_key: Dify 应用密钥
            scenario_types: 支持的场景类型列表
            dify_params: 传递给Dify API的额外参数
        """
        # 创建 DifyClient 实例
        dify_client = DifyClient(
            api_key=app_key,
            base_url=endpoint
        )
        self.scenario_types = scenario_types or [
            "营销场景",
            "用户故事",
            "测试用例",
            "产品演示",
            "培训场景"
        ]
        
        config = AgentConfig(
            name="场景生成器",
            description="智能场景内容生成工具，支持多种场景类型的定制化生成",
            agent_type=AgentType.SCENARIO_GENERATOR,
            default_inputs={
                "scenario_types": self.scenario_types,
                "output_format": "detailed",
                "creativity_level": "medium"
            },
            system_prompt="你是一个专业的场景设计师，擅长根据需求生成各种类型的场景内容。"
        )
        
        super().__init__(dify_client, config, dify_params)
    
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """生成场景内容
        
        Args:
            params: 参数字典，包含:
                - query: 场景生成需求描述（必需）
                - inputs: 额外输入参数（可选）
                - scenario_type: 场景类型（可选）
                - target_audience: 目标受众（可选）
                - user: 用户标识（可选）
            
        Returns:
            AgentResponse: 生成结果
        """
        try:
            # 验证必需参数
            if 'query' not in params:
                raise ValueError("Missing required parameter: query")
            
            query = params['query']
            inputs = params.get('inputs')
            scenario_type = params.get('scenario_type')
            target_audience = params.get('target_audience')
            user = params.get('user', 'scenario_generator')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加场景特定参数
            if scenario_type:
                final_inputs["scenario_type"] = scenario_type
            if target_audience:
                final_inputs["target_audience"] = target_audience
            
            # 构建查询
            full_query = self._build_scenario_query(query, scenario_type, target_audience)
            
            # 合并dify_params到inputs中
            if self.dify_params:
                final_inputs.update(self.dify_params)
            
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
        """流式生成场景内容
        
        Args:
            params: 参数字典，包含:
                - query: 场景生成需求描述（必需）
                - inputs: 额外输入参数（可选）
                - scenario_type: 场景类型（可选）
                - target_audience: 目标受众（可选）
                - user: 用户标识（可选）
        
        Yields:
            AgentResponse: 流式生成结果
        """
        try:
            # 验证必需参数
            if 'query' not in params:
                raise ValueError("Missing required parameter: query")
            
            query = params['query']
            inputs = params.get('inputs')
            scenario_type = params.get('scenario_type')
            target_audience = params.get('target_audience')
            user = params.get('user', 'scenario_generator')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            if scenario_type:
                final_inputs["scenario_type"] = scenario_type
            if target_audience:
                final_inputs["target_audience"] = target_audience
            
            # 构建查询
            full_query = self._build_scenario_query(query, scenario_type, target_audience)
            
            # 合并dify_params到inputs中
            if self.dify_params:
                final_inputs.update(self.dify_params)
            
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
    
    def _build_scenario_query(self, 
                             query: str, 
                             scenario_type: Optional[str], 
                             target_audience: Optional[str]) -> str:
        """构建场景生成查询"""
        base_query = self._build_query(query)
        
        additional_info = []
        if scenario_type:
            additional_info.append(f"场景类型：{scenario_type}")
        if target_audience:
            additional_info.append(f"目标受众：{target_audience}")
        
        if additional_info:
            return f"{base_query}\n\n{chr(10).join(additional_info)}"
        
        return base_query
    
    def generate_multiple_scenarios(self, 
                                   base_query: str, 
                                   count: int = 3,
                                   scenario_type: Optional[str] = None) -> List[AgentResponse]:
        """生成多个场景变体
        
        Args:
            base_query: 基础查询
            count: 生成数量
            scenario_type: 场景类型
            
        Returns:
            List[AgentResponse]: 场景列表
        """
        results = []
        
        for i in range(count):
            query = f"{base_query} (变体 {i+1})"
            result = self.process(query, scenario_type=scenario_type)
            results.append(result)
        
        return results


class AgentManager:
    """Agent 管理器
    
    提供简化的Agent获取接口，封装初始化逻辑，支持单例模式。
    用户可以直接调用getXXAgent()方法获取Agent实例。
    """
    
    _instance = None
    _agents: Dict[str, BaseAgent] = {}
    
    def __new__(cls, endpoint: str = None, app_key: str = None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, endpoint: str = None, app_key: str = None):
        """
        初始化Agent管理器
        
        Args:
            endpoint: Dify API 端点地址
            app_key: Dify 应用密钥
        """
        if self._initialized:
            return
            
        if not endpoint or not app_key:
            raise ValueError("endpoint and app_key are required for first initialization")
            
        self.endpoint = endpoint
        self.app_key = app_key
        self._initialized = True
    
    def getContentValidatorAgent(self, 
                                validation_criteria: Optional[List[str]] = None,
                                dify_params: Optional[Dict[str, Any]] = None) -> 'ContentValidatorAgent':
        """获取文案验收器Agent
        
        Args:
            validation_criteria: 验收标准列表
            dify_params: 传递给Dify API的额外参数
            
        Returns:
            ContentValidatorAgent: 文案验收器实例
        """
        cache_key = "content_validator"
        
        if cache_key not in self._agents:
            self._agents[cache_key] = ContentValidatorAgent(
                endpoint=self.endpoint,
                app_key=self.app_key,
                validation_criteria=validation_criteria,
                dify_params=dify_params
            )
        
        return self._agents[cache_key]
    
    def getScenarioGeneratorAgent(self,
                                 scenario_types: Optional[List[str]] = None,
                                 dify_params: Optional[Dict[str, Any]] = None) -> 'ScenarioGeneratorAgent':
        """获取场景生成器Agent
        
        Args:
            scenario_types: 支持的场景类型列表
            dify_params: 传递给Dify API的额外参数
            
        Returns:
            ScenarioGeneratorAgent: 场景生成器实例
        """
        cache_key = "scenario_generator"
        
        if cache_key not in self._agents:
            self._agents[cache_key] = ScenarioGeneratorAgent(
                endpoint=self.endpoint,
                app_key=self.app_key,
                scenario_types=scenario_types,
                dify_params=dify_params
            )
        
        return self._agents[cache_key]
    
    def clearAgents(self) -> None:
        """清空所有Agent缓存"""
        self._agents.clear()
    
    def listAgents(self) -> List[Dict[str, Any]]:
        """列出所有已创建的Agent
        
        Returns:
            List[Dict]: Agent信息列表
        """
        return [agent.get_info() for agent in self._agents.values()]


class AgentFactory:
    """Agent 工厂类
    
    用于创建和管理不同类型的 Agent 实例，提供统一的创建接口。
    """
    
    def __init__(self, endpoint: str, app_key: str):
        """
        初始化工厂
        
        Args:
            endpoint: Dify API 端点地址
            app_key: Dify 应用密钥
        """
        self.endpoint = endpoint
        self.app_key = app_key
        self._agents: Dict[str, BaseAgent] = {}
    
    def create_agent(self, agent_type: AgentType, **kwargs) -> BaseAgent:
        """创建 Agent 实例
        
        Args:
            agent_type: Agent 类型
            **kwargs: 创建参数
            
        Returns:
            BaseAgent: Agent 实例
        """
        if agent_type == AgentType.CONTENT_VALIDATOR:
            return ContentValidatorAgent(
                endpoint=self.endpoint,
                app_key=self.app_key,
                validation_criteria=kwargs.get('validation_criteria'),
                dify_params=kwargs.get('dify_params')
            )
        elif agent_type == AgentType.SCENARIO_GENERATOR:
            return ScenarioGeneratorAgent(
                endpoint=self.endpoint,
                app_key=self.app_key,
                scenario_types=kwargs.get('scenario_types'),
                dify_params=kwargs.get('dify_params')
            )
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")
    
    def get_or_create_agent(self, 
                           agent_type: AgentType, 
                           agent_name: Optional[str] = None,
                           **kwargs) -> BaseAgent:
        """获取或创建 Agent 实例（单例模式）
        
        Args:
            agent_type: Agent 类型
            agent_name: Agent 名称（用于缓存）
            **kwargs: 创建参数
            
        Returns:
            BaseAgent: Agent 实例
        """
        cache_key = agent_name or agent_type.value
        
        if cache_key not in self._agents:
            self._agents[cache_key] = self.create_agent(agent_type, **kwargs)
        
        return self._agents[cache_key]
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有已创建的 Agent
        
        Returns:
            List[Dict]: Agent 信息列表
        """
        return [agent.get_info() for agent in self._agents.values()]
    
    def clear_agents(self) -> None:
        """清空所有 Agent 缓存"""
        self._agents.clear()