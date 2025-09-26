#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品推荐器 Agent
专门用于根据用户需求和场景推荐合适的商品
"""

from typing import Dict, Any, Optional, List, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from dify.dify_client import DifyClient, DifyAPIError
from .product_database import ProductDatabase


class AgentType(Enum):
    """Agent 类型枚举"""
    CONTENT_VALIDATOR = "content_validator"  # 文案场景验收器
    SCENARIO_GENERATOR = "scenario_generator"  # 场景生成器
    PRODUCT_RECOMMENDER = "product_recommender"  # 商品推荐器
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


class ProductRecommenderAgent(BaseAgent):
    """商品推荐器 Agent
    
    专门用于根据用户需求和场景推荐合适的商品。
    支持根据不同的参数和条件生成个性化的商品推荐。
    """
    
    def __init__(self, 
                 endpoint: str = "http://119.45.130.88:8080/v1",
                 app_key: str = "app-oM9cjamwbeTy4em5KoEUvuDL"):
        """
        初始化商品推荐器
        
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
            name="商品推荐器",
            description="智能商品推荐工具，根据用户需求和场景推荐合适的商品",
            agent_type=AgentType.PRODUCT_RECOMMENDER
        )
        
        # 初始化商品数据库
        self.product_db = ProductDatabase()
        
        super().__init__(dify_client, config)
    
    def process(self, params: Dict[str, Any]) -> AgentResponse:
        """推荐商品
        
        Args:
            params: 参数字典，包含:
                - query: 商品推荐需求描述（必需）
                - inputs: 额外输入参数（可选）
                - user_profile: 用户画像（可选）
                - scenario: 使用场景（可选）
                - budget: 预算范围（可选）
                - category: 商品类别（可选）
                - user: 用户标识（可选）
            
        Returns:
            AgentResponse: 推荐结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            user_profile = params.get('user_profile')
            scenario = params.get('scenario')
            budget = params.get('budget')
            category = params.get('category')
            user = params.get('user', 'product_recommender')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加query到inputs中（某些Dify应用需要）
            final_inputs["query"] = query
            
            # 自动补齐goods_list参数
            goods_list = params.get('goods_list')
            if not goods_list:  # 如果goods_list为空或None，自动补齐
                goods_list = self._get_goods_list_json()
                final_inputs["goods_list"] = goods_list

                # 打印final_inputs的数量和内容（在所有参数添加完成后）
                print(f"📊 goods_list 信息:")
                # goods_list是JSON字符串，需要解析后计算商品数量
                import json
                try:
                    goods_data = json.loads(goods_list)
                    goods_count = len(goods_data) if isinstance(goods_data, list) else 0
                    print(f"  goods_list商品数量: {goods_count}")
                    print(f"  goods_list字符串长度: {len(goods_list)}")
                except Exception as e:
                    print(f"  goods_list解析失败: {e}")
                    print(f"  goods_list字符串长度: {len(goods_list)}")
            
            # 将所有其他参数添加到inputs中（除了特殊参数）
            special_params = {'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            
            # 打印每个参数的详细信息
            for key, value in final_inputs.items():
                if key == "goods_list":
                    # goods_list是JSON字符串，计算商品数量
                    import json
                    try:
                        goods_data = json.loads(value) if isinstance(value, str) else value
                        goods_count = len(goods_data) if isinstance(goods_data, list) else 0
                        print(f"  {key}: JSON字符串，包含 {goods_count} 个商品")
                    except:
                        print(f"  {key}: {type(value).__name__}，长度: {len(str(value))}")
                else:
                    # 其他参数显示类型和内容预览
                    value_str = str(value)
                    preview = value_str[:100] + "..." if len(value_str) > 100 else value_str
                    print(f"  {key}: {type(value).__name__} = {preview}")
            
            # 构建查询
            full_query = self._build_recommendation_query(query, user_profile, scenario, budget, category)
            
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
                error_message=f"Dify API error: {e.message}",
                raw_response=None
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=f"Unexpected error: {str(e)}",
                raw_response=None
            )
    
    def process_streaming(self, params: Dict[str, Any]) -> Iterator[AgentResponse]:
        """流式推荐商品
        
        Args:
            params: 参数字典，格式同process方法
            
        Yields:
            AgentResponse: 流式推荐结果
        """
        try:
            query = params.get('query', '')
            inputs = params.get('inputs')
            user_profile = params.get('user_profile')
            scenario = params.get('scenario')
            budget = params.get('budget')
            category = params.get('category')
            user = params.get('user', 'product_recommender')
            
            # 准备输入参数
            final_inputs = self._prepare_inputs(inputs)
            
            # 添加query到inputs中
            final_inputs["query"] = query
            
            # 自动补齐goods_list参数
            goods_list = params.get('goods_list')
            if not goods_list:  # 如果goods_list为空或None，自动补齐
                goods_list = self._get_goods_list_json()
                final_inputs["goods_list"] = goods_list
            
            # 将所有其他参数添加到inputs中
            special_params = {'query', 'inputs', 'user'}
            for key, value in params.items():
                if key not in special_params and value is not None:
                    final_inputs[key] = value
            
            # 构建查询
            full_query = self._build_recommendation_query(query, user_profile, scenario, budget, category)
            
            # 调用流式API
            for chunk in self.client.completion_messages_streaming(
                query=full_query,
                inputs=final_inputs,
                user=user
            ):
                if chunk.get('event') == 'message':
                    content = chunk.get('answer', '')
                    yield AgentResponse(
                        success=True,
                        content=content,
                        metadata={'chunk': chunk},
                        raw_response=chunk
                    )
                elif chunk.get('event') == 'message_end':
                    # 最终响应
                    yield self._handle_response(chunk)
                    
        except DifyAPIError as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=f"Dify API error: {e.message}",
                raw_response=None
            )
        except Exception as e:
            yield AgentResponse(
                success=False,
                content="",
                error_message=f"Unexpected error: {str(e)}",
                raw_response=None
            )
    
    def _build_recommendation_query(self, query: str, user_profile: str = None, 
                                  scenario: str = None, budget: str = None, 
                                  category: str = None) -> str:
        """构建商品推荐查询"""
        query_parts = [query]
        
        if user_profile:
            query_parts.append(f"用户画像: {user_profile}")
        if scenario:
            query_parts.append(f"使用场景: {scenario}")
        if budget:
            query_parts.append(f"预算范围: {budget}")
        if category:
            query_parts.append(f"商品类别: {category}")
        
        full_query = "\n".join(query_parts)
        return self._build_query(full_query)
    
    def _get_goods_list_json(self) -> str:
        """获取商品列表的JSON格式数据
        
        Returns:
            str: 商品列表的JSON字符串
        """
        try:
            # 获取所有商品信息
            all_products = self.product_db.get_all_products()
            
            # 转换为简化的商品列表格式
            goods_list = []
            for product in all_products:
                # 验证价格是否为有效数字且大于0
                try:
                    price_value = float(product.price)
                    if price_value <= 0:
                        continue  # 跳过价格为0或负数的商品
                except (ValueError, TypeError):
                    continue  # 跳过价格不是数字的商品
                
                # 只有当product_selling_points不为空时才将商品加入列表
                if not (product.product_selling_points and product.product_selling_points.strip()):
                    continue  # 跳过product_selling_points为空的商品
                
                goods_item = {
                    "k3_code": product.k3_code,
                    "name": product.name,
                    # "description": product.description,
                    "price": product.price,
                    # "brand": product.brand,
                    # "target_audience": product.target_audience,
                    "formula_source" : product.formula_source,
                    "product_selling_points": product.core_selling_point,
                    # "product_selling_points": product.product_selling_points,
                }
                
                goods_list.append(goods_item)
            
            # 转换为JSON字符串
            import json
            return json.dumps(goods_list, ensure_ascii=False, indent=2)
            
        except Exception as e:
            # 如果出现异常，返回空列表的JSON
            import json
            return json.dumps([], ensure_ascii=False)