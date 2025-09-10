#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
养生妈妈 Agent
专门提供健康养生建议、育儿指导、营养搭配等温馨贴心的服务
"""

from typing import Dict, Any, Optional, List, Iterator
from dify.dify_client import DifyClient, DifyAPIError
from agents.agents import AgentType, AgentConfig, AgentResponse, BaseAgent


class WellnessMomAgent(BaseAgent):
    """养生妈妈 Agent
    
    专门提供健康养生建议、育儿指导、营养搭配等温馨贴心的服务
    """
    
    def __init__(self, api_key: str, base_url: str, app_id: str):
        """初始化养生妈妈 Agent"""
        dify_client = DifyClient(api_key=api_key, base_url=base_url)
        
        config = AgentConfig(
            name="养生妈妈",
            description="专门提供健康养生建议、育儿指导、营养搭配等温馨贴心的服务",
            agent_type=AgentType.WELLNESS_MOM,
            default_inputs={
                "app_id": app_id
            }
        )
        
        super().__init__(dify_client, config)
    
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """处理养生建议请求"""
        try:
            # 准备输入参数
            final_inputs = self._prepare_inputs(params)
            
            # 获取用户查询
            user_query = params.get('query', '')
            if not user_query:
                return AgentResponse(
                    success=False,
                    content="",
                    error_message="缺少用户查询内容"
                )
            
            # 构建查询
            query = self._build_query(user_query)
            
            # 调用 Dify API
            response = self.client.completion_messages_blocking(
                inputs=final_inputs,
                query=query,
                user="wellness_user"
            )
            
            return self._handle_response(response)
            
        except DifyAPIError as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=f"Dify API 错误: {str(e)}"
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=str(e)
            )
    
    def process_streaming(self, params: Dict[str, Any]) -> Iterator[AgentResponse]:
        """流式处理养生建议请求"""
        try:
            # 准备输入参数
            final_inputs = self._prepare_inputs(params)
            
            # 获取用户查询
            user_query = params.get('query', '')
            if not user_query:
                yield AgentResponse(
                    success=False,
                    content="",
                    error_message="缺少用户查询内容"
                )
                return
            
            # 构建查询
            query = self._build_query(user_query)
            
            # 调用 Dify API 流式接口
            for response in self.client.completion_messages_streaming(
                inputs=final_inputs,
                query=query,
                user="wellness_user"
            ):
                yield self._handle_response(response)
                
        except DifyAPIError as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=f"Dify API 错误: {str(e)}"
            )
        except Exception as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=str(e)
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