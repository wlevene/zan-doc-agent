#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景生成器 Agent
专门用于生成各种场景内容，如营销场景、用户故事、测试用例等
"""

from typing import Dict, Any, Optional, List, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from dify.dify_client import DifyClient, DifyAPIError
from datetime import datetime
from agents.product_recommender.product_database import ProductDatabase


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
        import json
        try:
            answer = raw_response.get('answer', '')
            
            # 尝试解析JSON格式的answer
            try:
                # 如果answer是JSON格式，解析它
                if answer.strip().startswith('```json'):
                    # 移除markdown代码块标记
                    json_content = answer.strip()
                    json_content = json_content.replace('```json\n', '').replace('\n```', '')
                    parsed_data = json.loads(json_content)
                    
                    # 如果有scenes字段，提取场景列表
                    if 'scenes' in parsed_data:
                        content = '\n'.join(parsed_data['scenes'])
                    else:
                        content = json.dumps(parsed_data, ensure_ascii=False, indent=2)
                elif answer.strip().startswith('{\n[') or answer.strip().startswith('['):
                    # 处理特殊格式：{\n[...]} 或直接的数组
                    clean_answer = answer.strip()
                    if clean_answer.startswith('{\n[') and clean_answer.endswith(']\n}'):
                        # 提取数组部分
                        array_content = clean_answer[2:-2]  # 移除 '{\n' 和 '\n}'
                        parsed_array = json.loads('[' + array_content + ']')
                        content = '\n'.join(parsed_array)
                    else:
                        # 直接解析数组
                        parsed_array = json.loads(clean_answer)
                        if isinstance(parsed_array, list):
                            content = '\n'.join(parsed_array)
                        else:
                            content = json.dumps(parsed_array, ensure_ascii=False, indent=2)
                else:
                    # 尝试直接解析JSON
                    parsed_data = json.loads(answer)
                    if 'scenes' in parsed_data:
                        content = '\n'.join(parsed_data['scenes'])
                    elif isinstance(parsed_data, list):
                        content = '\n'.join(parsed_data)
                    else:
                        content = json.dumps(parsed_data, ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, KeyError, IndexError):
                # 如果不是JSON格式，直接使用原始内容
                content = answer
            
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


class ScenarioGeneratorAgent(BaseAgent):
    """场景生成器 Agent
    
    专门用于生成各种场景内容，如营销场景、用户故事、测试用例等。
    支持根据不同的参数和模板生成定制化的场景内容。
    """
    
    def __init__(self, 
                 endpoint: str = "http://119.45.130.88:8080/v1",
                 app_key: str = "app-AqCx801U23UaSywIF4zNvhXs"):
        """
        初始化场景生成器
        
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
            name="场景生成器",
            description="智能场景内容生成工具，支持多种场景类型的定制化生成",
            agent_type=AgentType.SCENARIO_GENERATOR
        )
        
        # 初始化商品数据库（用于通过 K3 编码查询商品信息）
        self.product_db = ProductDatabase()
        
        super().__init__(dify_client, config)
    
    def set_k3code(self, k3_code: str):
        """设置产品K3代码"""
        self.product_k3_code = k3_code
        
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """生成场景内容
        
        Args:
            params: 参数字典，包含:
                - query: 场景生成需求描述（必需）
                - user: 用户标识（可选）
            
        Returns:
            AgentResponse: 生成结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            user = params.get('user', 'scenario_generator')
            
            # 获取场景类型和目标受众
            scenario_type = params.get('scenario_type')
            target_audience = params.get('target_audience')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            print(f"final_inputs 1: {final_inputs}")
            final_inputs["date"] = datetime.now().strftime("%Y-%m-%d")
            print(f"final_inputs 2: {final_inputs}")
            # 根据 K3 编码查询商品信息并加入到 inputs 中
            if getattr(self, "product_k3_code", None):
                k3_code = str(self.product_k3_code).strip()
                product_info_obj = self.product_db.get_product_by_k3_code(k3_code)
                if product_info_obj:
                    # 仅注入字符串：商品名称 + 卖点
                    final_inputs["product"] = f"商品：{product_info_obj.name}；卖点：{product_info_obj.product_selling_points}"
            
            # 将所有其他参数添加到inputs中（除了特殊参数）
            special_params = {'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建查询
            full_query = self._build_scenario_query(query, scenario_type, target_audience)
            print(f"full_query: {full_query}")
            
            print(f"final_inputs 22: {final_inputs}")
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
                - user: 用户标识（可选）
        
        Yields:
            AgentResponse: 流式生成结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            scenario_type = params.get('scenario_type')
            target_audience = params.get('target_audience')
            user = params.get('user', 'scenario_generator')
            
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
            full_query = self._build_scenario_query(query, scenario_type, target_audience)
            
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
            result = self.process({'query': query, 'scenario_type': scenario_type})
            results.append(result)
        
        return results