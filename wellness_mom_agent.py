#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
养生妈妈 Agent
专门提供健康养生建议、育儿指导、营养搭配等温馨贴心的服务
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


class WellnessMomAgent(BaseAgent):
    """养生妈妈 Agent
    
    专门提供健康养生建议、育儿指导、营养搭配等温馨贴心的服务。
    以妈妈的角色为用户提供专业而温暖的健康生活指导。
    """
    
    def __init__(self, 
                 endpoint: str,
                 app_key: str):
        """
        初始化养生妈妈Agent
        
        Args:
            endpoint: Dify API 端点地址
            app_key: Dify 应用密钥
        """
        # 创建 DifyClient 实例
        dify_client = DifyClient(
            api_key=app_key,
            base_url=endpoint
        )
        
        # 养生妈妈的系统提示词
        system_prompt = """
你是一位温暖贴心的养生妈妈，拥有丰富的健康养生知识和育儿经验。
你的特点：
1. 语言温和亲切，像妈妈一样关怀用户
2. 提供专业的健康养生建议
3. 关注营养搭配和生活习惯
4. 重视预防胜于治疗的理念
5. 给出实用可行的建议
6. 适当提醒用户咨询专业医生

请用妈妈般的温暖语调回答用户的健康养生问题。
        """.strip()
        
        config = AgentConfig(
            name="养生妈妈",
            description="温暖贴心的健康养生顾问，提供专业的养生建议和育儿指导",
            agent_type=AgentType.WELLNESS_MOM,
            system_prompt=system_prompt,
            default_inputs={
                "tone": "温暖亲切",
                "expertise": "健康养生",
                "role": "妈妈"
            }
        )
        
        super().__init__(dify_client, config)
    
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """提供养生建议
        
        Args:
            params: 参数字典，包含:
                - query: 健康养生问题（必需）
                - inputs: 额外输入参数（可选）
                - age_group: 年龄段（可选）
                - health_concern: 健康关注点（可选）
                - lifestyle: 生活方式（可选）
                - user: 用户标识（可选）
            
        Returns:
            AgentResponse: 养生建议结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            age_group = params.get('age_group')
            health_concern = params.get('health_concern')
            lifestyle = params.get('lifestyle')
            user = params.get('user', 'wellness_user')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加query到inputs中
            final_inputs["query"] = query
            
            # 将其他参数添加到inputs中
            special_params = {'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建养生查询
            full_query = self._build_wellness_query(query, age_group, health_concern, lifestyle)
            
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
        """流式提供养生建议
        
        Args:
            params: 参数字典，包含:
                - query: 健康养生问题（必需）
                - inputs: 额外输入参数（可选）
                - age_group: 年龄段（可选）
                - health_concern: 健康关注点（可选）
                - lifestyle: 生活方式（可选）
                - user: 用户标识（可选）
        
        Yields:
            AgentResponse: 流式养生建议结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            age_group = params.get('age_group')
            health_concern = params.get('health_concern')
            lifestyle = params.get('lifestyle')
            user = params.get('user', 'wellness_user')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加query到inputs中
            final_inputs["query"] = query
            
            # 将其他参数添加到inputs中
            special_params = {'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建养生查询
            full_query = self._build_wellness_query(query, age_group, health_concern, lifestyle)
            
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
    
    def _build_wellness_query(self, 
                             query: str, 
                             age_group: Optional[str], 
                             health_concern: Optional[str],
                             lifestyle: Optional[str]) -> str:
        """构建养生建议查询"""
        base_query = self._build_query(query)
        
        additional_info = []
        if age_group:
            additional_info.append(f"年龄段：{age_group}")
        if health_concern:
            additional_info.append(f"健康关注：{health_concern}")
        if lifestyle:
            additional_info.append(f"生活方式：{lifestyle}")
        
        if additional_info:
            return f"{base_query}\n\n{chr(10).join(additional_info)}"
        
        return base_query
    
    def get_wellness_plan(self, 
                         user_profile: Dict[str, Any],
                         duration_days: int = 7) -> AgentResponse:
        """生成个性化养生计划
        
        Args:
            user_profile: 用户档案，包含年龄、性别、健康状况等
            duration_days: 计划天数
            
        Returns:
            AgentResponse: 养生计划
        """
        query = f"请为我制定一个{duration_days}天的个性化养生计划"
        
        params = {
            'query': query,
            'inputs': user_profile,
            'plan_duration': duration_days
        }
        
        return self.process(params)
    
    def get_nutrition_advice(self, 
                           food_items: List[str],
                           meal_type: str = "日常饮食") -> AgentResponse:
        """获取营养搭配建议
        
        Args:
            food_items: 食物列表
            meal_type: 餐食类型
            
        Returns:
            AgentResponse: 营养建议
        """
        food_list = "、".join(food_items)
        query = f"请为{meal_type}中的这些食物提供营养搭配建议：{food_list}"
        
        params = {
            'query': query,
            'food_items': food_items,
            'meal_type': meal_type
        }
        
        return self.process(params)
    
    def get_seasonal_advice(self, season: str) -> AgentResponse:
        """获取季节性养生建议
        
        Args:
            season: 季节（春、夏、秋、冬）
            
        Returns:
            AgentResponse: 季节养生建议
        """
        query = f"请提供{season}季的养生建议和注意事项"
        
        params = {
            'query': query,
            'season': season
        }
        
        return self.process(params)