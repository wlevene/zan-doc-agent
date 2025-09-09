#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
养生妈妈工作流程

这个文件整合了所有的agent，形成完整的养生内容生成工作流：
1. 单人设 -> 场景生成器 -> 场景验收器
2. 场景验收器 -> 文案生成器 -> 文案验收器  
3. 文案验收器 -> 商品推荐 -> 商品推荐验收器
4. 商品推荐验收器 -> 商品信息(图片) -> 文案生成

作者: SOLO Coding
创建时间: 2024-01-15
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 导入所有需要的agent
from wellness_mom_agent import WellnessMomAgent, AgentConfig
from scenario_generator_agent import ScenarioGeneratorAgent
from scenario_validator_agent import ScenarioValidatorAgent
from content_generator_agent import ContentGeneratorAgent
from content_validator_agent import ContentValidatorAgent
from product_recommender_agent import ProductRecommenderAgent
from product_recommendation_validator_agent import ProductRecommendationValidatorAgent
from product_database import ProductDatabase

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowResult:
    """工作流结果"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

class WellnessWorkflow:
    """养生妈妈工作流程"""
    
    def __init__(self, config: AgentConfig):
        """初始化工作流"""
        self.config = config
        self.product_db = ProductDatabase()
        
        # 初始化所有agent
        self.wellness_mom = WellnessMomAgent(config)
        self.scenario_generator = ScenarioGeneratorAgent(config)
        self.scenario_validator = ScenarioValidatorAgent(config)
        self.content_generator = ContentGeneratorAgent(config)
        self.content_validator = ContentValidatorAgent(config)
        self.product_recommender = ProductRecommenderAgent(config)
        self.product_recommendation_validator = ProductRecommendationValidatorAgent(config)
        
        logger.info("养生妈妈工作流初始化完成")
    
    def run_complete_workflow(self, user_input: str) -> WorkflowResult:
        """运行完整的工作流程"""
        try:
            logger.info(f"开始执行完整工作流，用户输入: {user_input}")
            
            # 步骤1: 单人设处理
            persona_result = self.wellness_mom.process(user_input)
            if not persona_result.success:
                return WorkflowResult(False, {}, f"单人设处理失败: {persona_result.error}")
            
            # 步骤2: 场景生成
            scenario_result = self.scenario_generator.process(persona_result.data)
            if not scenario_result.success:
                return WorkflowResult(False, {}, f"场景生成失败: {scenario_result.error}")
            
            # 步骤3: 场景验收
            scenario_validation = self.scenario_validator.process(scenario_result.data)
            if not scenario_validation.success:
                return WorkflowResult(False, {}, f"场景验收失败: {scenario_validation.error}")
            
            # 步骤4: 文案生成
            content_result = self.content_generator.process(scenario_validation.data)
            if not content_result.success:
                return WorkflowResult(False, {}, f"文案生成失败: {content_result.error}")
            
            # 步骤5: 文案验收
            content_validation = self.content_validator.process(content_result.data)
            if not content_validation.success:
                return WorkflowResult(False, {}, f"文案验收失败: {content_validation.error}")
            
            # 步骤6: 商品推荐
            product_result = self.product_recommender.process(content_validation.data)
            if not product_result.success:
                return WorkflowResult(False, {}, f"商品推荐失败: {product_result.error}")
            
            # 步骤7: 商品推荐验收
            product_validation = self.product_recommendation_validator.process(product_result.data)
            if not product_validation.success:
                return WorkflowResult(False, {}, f"商品推荐验收失败: {product_validation.error}")
            
            # 步骤8: 获取商品信息(图片)
            product_info = self._get_product_info(product_validation.data)
            
            # 步骤9: 最终文案生成
            final_content = self.content_generator.process({
                "content": content_validation.data,
                "products": product_info
            })
            
            if not final_content.success:
                return WorkflowResult(False, {}, f"最终文案生成失败: {final_content.error}")
            
            # 整合所有结果
            workflow_data = {
                "persona": persona_result.data,
                "scenarios": scenario_validation.data,
                "content": content_validation.data,
                "products": product_info,
                "final_content": final_content.data
            }
            
            logger.info("完整工作流执行成功")
            return WorkflowResult(True, workflow_data)
            
        except Exception as e:
            logger.error(f"工作流执行异常: {str(e)}")
            return WorkflowResult(False, {}, str(e))
    
    def _get_product_info(self, product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取商品信息包括图片"""
        try:
            product_ids = product_data.get('product_ids', [])
            products = []
            
            for product_id in product_ids:
                product = self.product_db.get_product_by_id(product_id)
                if product:
                    product_dict = product.to_dict()
                    # 获取图片信息
                    image_info = self.product_db.get_product_image(product_id)
                    if image_info:
                        product_dict['image'] = image_info
                    products.append(product_dict)
            
            return products
            
        except Exception as e:
            logger.error(f"获取商品信息失败: {str(e)}")
            return []
    
    def run_scenario_generation(self, user_input: str) -> WorkflowResult:
        """运行场景生成流程"""
        try:
            # 单人设 -> 场景生成器 -> 场景验收器
            persona_result = self.wellness_mom.process(user_input)
            if not persona_result.success:
                return WorkflowResult(False, {}, f"单人设处理失败: {persona_result.error}")
            
            scenario_result = self.scenario_generator.process(persona_result.data)
            if not scenario_result.success:
                return WorkflowResult(False, {}, f"场景生成失败: {scenario_result.error}")
            
            scenario_validation = self.scenario_validator.process(scenario_result.data)
            if not scenario_validation.success:
                return WorkflowResult(False, {}, f"场景验收失败: {scenario_validation.error}")
            
            return WorkflowResult(True, scenario_validation.data)
            
        except Exception as e:
            logger.error(f"场景生成流程异常: {str(e)}")
            return WorkflowResult(False, {}, str(e))
    
    def run_content_generation(self, scenario_data: Dict[str, Any]) -> WorkflowResult:
        """运行文案生成流程"""
        try:
            # 场景验收器 -> 文案生成器 -> 文案验收器
            content_result = self.content_generator.process(scenario_data)
            if not content_result.success:
                return WorkflowResult(False, {}, f"文案生成失败: {content_result.error}")
            
            content_validation = self.content_validator.process(content_result.data)
            if not content_validation.success:
                return WorkflowResult(False, {}, f"文案验收失败: {content_validation.error}")
            
            return WorkflowResult(True, content_validation.data)
            
        except Exception as e:
            logger.error(f"文案生成流程异常: {str(e)}")
            return WorkflowResult(False, {}, str(e))
    
    def run_product_recommendation(self, content_data: Dict[str, Any]) -> WorkflowResult:
        """运行商品推荐流程"""
        try:
            # 文案验收器 -> 商品推荐 -> 商品推荐验收器
            product_result = self.product_recommender.process(content_data)
            if not product_result.success:
                return WorkflowResult(False, {}, f"商品推荐失败: {product_result.error}")
            
            product_validation = self.product_recommendation_validator.process(product_result.data)
            if not product_validation.success:
                return WorkflowResult(False, {}, f"商品推荐验收失败: {product_validation.error}")
            
            return WorkflowResult(True, product_validation.data)
            
        except Exception as e:
            logger.error(f"商品推荐流程异常: {str(e)}")
            return WorkflowResult(False, {}, str(e))

# 使用示例
if __name__ == "__main__":
    # 配置
    config = AgentConfig(
        api_key="your-dify-api-key",
        base_url="https://api.dify.ai/v1",
        app_id="your-app-id"
    )
    
    # 创建工作流
    workflow = WellnessWorkflow(config)
    
    # 运行完整工作流
    result = workflow.run_complete_workflow("我想要一些秋季养生的建议")
    
    if result.success:
        print("工作流执行成功!")
        print(json.dumps(result.data, ensure_ascii=False, indent=2))
    else:
        print(f"工作流执行失败: {result.error}")