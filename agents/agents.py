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

from dify.dify_client import DifyClient, DifyAPIError, FileInfo, ResponseMode

# 导入具体的Agent实现
from agents.content_validator.content_validator_agent import ContentValidatorAgent
from agents.scenario_generator.scenario_generator_agent import ScenarioGeneratorAgent


class AgentType(Enum):
    """Agent 类型枚举"""
    CONTENT_VALIDATOR = "content_validator"  # 文案场景验收器
    SCENARIO_GENERATOR = "scenario_generator"  # 场景生成器
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
        """
        初始化 Agent
        
        Args:
            dify_client: Dify API 客户端实例
            config: Agent 配置信息
        """
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


# ContentValidatorAgent 已移动到 content_validator_agent.py


# ScenarioGeneratorAgent 已移动到 scenario_generator_agent.py


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
    
    def getContentValidatorAgent(self) -> 'ContentValidatorAgent':
        """获取文案验收器Agent
            
        Returns:
            ContentValidatorAgent: 文案验收器实例
        """
        cache_key = "content_validator"
        
        if cache_key not in self._agents:
            self._agents[cache_key] = ContentValidatorAgent()
        
        return self._agents[cache_key]
    
    def getScenarioGeneratorAgent(self) -> 'ScenarioGeneratorAgent':
        """获取场景生成器Agent
            
        Returns:
            ScenarioGeneratorAgent: 场景生成器实例
        """
        cache_key = "scenario_generator"
        
        if cache_key not in self._agents:
            self._agents[cache_key] = ScenarioGeneratorAgent(
                endpoint=self.endpoint,
                app_key=self.app_key
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
            return ContentValidatorAgent()
        elif agent_type == AgentType.SCENARIO_GENERATOR:
            return ScenarioGeneratorAgent(
                endpoint=self.endpoint,
                app_key=self.app_key
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