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

import sys
import os
from pathlib import Path
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 先导入本地模块
from content_item import ContentCollector

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入所有需要的agent
from agents.wellness.wellness_mom_agent import WellnessMomAgent
from agents.agents import AgentConfig, AgentType
from agents.scenario_generator.scenario_generator_agent import ScenarioGeneratorAgent
from agents.scenario_validator.scenario_validator_agent import ScenarioValidatorAgent
from agents.content_generator.content_generator_agent import ContentGeneratorAgent
from agents.content_validator.content_validator_agent import ContentValidatorAgent
from agents.product_recommender.product_recommender_agent import ProductRecommenderAgent
from agents.product_recommendation_validator.product_recommendation_validator_agent import ProductRecommendationValidatorAgent
from agents.product_recommender.product_database import ProductDatabase

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
    
    def __init__(self, config: AgentConfig, persona_detail: str):
        """初始化工作流"""
        self.config = config
        self.product_db = ProductDatabase()
        self.persona_detail = persona_detail
        
        # 定义API配置
        api_key = "app-default-key"  # 默认API密钥
        base_url = "http://119.45.130.88:8080/v1"  # 默认API端点
        app_id = "wellness-mom-app"  # 默认应用ID
        
        # 初始化所有agent
        self.wellness_mom = WellnessMomAgent(api_key, base_url, app_id)
        self.scenario_generator = ScenarioGeneratorAgent()
        self.scenario_validator = ScenarioValidatorAgent()
        self.content_generator = ContentGeneratorAgent()
        self.content_validator = ContentValidatorAgent()
        self.product_recommender = ProductRecommenderAgent()
        self.product_recommendation_validator = ProductRecommendationValidatorAgent(base_url, api_key)
        
        # 初始化数据收集器
        self.content_collector = ContentCollector()
        
        logger.info("养生妈妈工作流初始化完成")
    
    def run_complete_workflow(self, user_input: str) -> WorkflowResult:
        """运行完整的工作流程"""
        try:
            logger.info(f"开始执行完整工作流，用户输入: {user_input}")
            
            # 步骤1: 单人设处理
            # persona_result = self.wellness_mom.process({'query': user_input})
            # if not persona_result.success:
            #     return WorkflowResult(False, {}, f"单人设处理失败: {persona_result.error_message}")
            
            # 步骤2: 场景生成
            scenario_result = self.scenario_generator.process({"query":self.persona_detail})
            if not scenario_result.success:
                return WorkflowResult(False, {}, f"场景生成失败: {scenario_result.error_message}")

            print(f"scenario_result: {scenario_result.content}")
            scenario_result.content = scenario_result.content.replace("```json", "").replace("```", "")

            # array scenario  for scenario_result.content
            # scenario_result.content is already processed as newline-separated strings
            scenario_array = [line.strip() for line in scenario_result.content.split('\n') if line.strip()]
            print(f"scenario_array: {scenario_array}")

            # 步骤2: 场景验证和处理
            for scenario in scenario_array:
                try:
                    # 场景验证
                    scenario_validation_result = self.scenario_validator.process({"scene":scenario, "persona":self.persona_detail})
                    if not scenario_validation_result.success:
                        # 场景验证失败，记录错误
                        self.content_collector.add_scenario_only(
                            user_input=user_input,
                            persona_detail=self.persona_detail,
                            scenario=scenario,
                            scenario_validation_result=False,
                            scenario_validation_reason=f"场景验证API调用失败: {scenario_validation_result.error_message}"
                        )
                        continue
                    
                    scenario_result_content = scenario_validation_result.content.replace("```json", "").replace("```", "")
                    scenario_result_json = json.loads(scenario_result_content)
                    scenario_validation_passed = scenario_result_json.get("result", False)
                    scenario_validation_reason = scenario_result_json.get("reason", "")
                    
                    if not scenario_validation_passed:
                        # 场景验证未通过，记录失败原因
                        print(f"场景验证失败: {scenario_validation_reason}")
                        self.content_collector.add_scenario_only(
                            user_input=user_input,
                            persona_detail=self.persona_detail,
                            scenario=scenario,
                            scenario_validation_result=False,
                            scenario_validation_reason=scenario_validation_reason
                        )
                        continue
                    
                    print(f"场景验证通过: {scenario_validation_reason}")
                    
                    # 文案生成和验证（带重试机制）
                    max_retries = 3
                    content_generation_success = False
                    content_result = None
                    content_validation_reason = ""
                    
                    for retry_count in range(max_retries):
                        print(f"\n=== 文案生成尝试 {retry_count + 1}/{max_retries} ===")
                        
                        # 文案生成
                        if retry_count == 0:
                            # 第一次生成，不传suggestion
                            content_result = self.content_generator.process(
                                {
                                    "query": scenario, 
                                    "suggestion": "无"
                                })
                        else:
                            # 重试时传递suggestion参数
                            content_result = self.content_generator.process({
                                "query": scenario,
                                "suggestion": content_validation_reason
                            })
                            print(f"重试文案生成，建议: {content_validation_reason}")
                        
                        if not content_result.success:
                            # 文案生成失败
                            print(f"文案生成失败: {content_result.error_message}")
                            if retry_count == max_retries - 1:  # 最后一次重试也失败
                                self.content_collector.add_content(
                                    user_input=user_input,
                                    persona_detail=self.persona_detail,
                                    scenario_data={"content": scenario},
                                    scenario_validation_result=True,
                                    scenario_validation_reason=scenario_validation_reason,
                                    content_data={"content": ""},
                                    content_validation_data={"validation_reason": ""},
                                    content_validation_result=False,
                                    content_generation_success=False,
                                    content_generation_error=content_result.error_message,
                                    processing_stage="content_generation",
                                    final_status="content_failed"
                                )
                            continue
                        
                        print(f"文案生成成功: {content_result.content}")
                        
                        # 文案验证
                        content_validation = self.content_validator.process({"query": content_result.content, "scenario": scenario})
                        if not content_validation.success:
                            # 文案验证API调用失败
                            print(f"文案验证API调用失败: {content_validation.error_message}")
                            if retry_count == max_retries - 1:  # 最后一次重试也失败
                                self.content_collector.add_content(
                                    user_input=user_input,
                                    persona_detail=self.persona_detail,
                                    scenario_data={"content": scenario},
                                    scenario_validation_result=True,
                                    scenario_validation_reason=scenario_validation_reason,
                                    content_data={"content": content_result.content},
                                    content_validation_data={"validation_reason": f"验证API调用失败: {content_validation.error_message}"},
                                    content_validation_result=False,
                                    processing_stage="content_validation",
                                    final_status="validation_failed"
                                )
                            continue
                        
                        print(f"\ncontent_validation: {content_validation}")
                        content_validation_json = json.loads(content_validation.content.replace("```json", "").replace("```", ""))
                        content_validation_passed = content_validation_json.get("result", False)
                        content_validation_reason = content_validation_json.get("reason", "")
                        
                        if content_validation_passed:
                            # 文案验证通过，跳出重试循环
                            print(f"文案验证通过: {content_result.content}")
                            content_generation_success = True
                            break
                        else:
                            # 文案验证未通过
                            print(f"文案验证未通过 (尝试 {retry_count + 1}/{max_retries}): {content_validation_reason}")
                            if retry_count == max_retries - 1:  # 最后一次重试也未通过
                                self.content_collector.add_content(
                                    user_input=user_input,
                                    persona_detail=self.persona_detail,
                                    scenario_data={"content": scenario},
                                    scenario_validation_result=True,
                                    scenario_validation_reason=scenario_validation_reason,
                                    content_data={"content": content_result.content},
                                    content_validation_data={"validation_reason": content_validation_reason},
                                    content_validation_result=False,
                                    processing_stage="content_validation",
                                    final_status="validation_failed"
                                )
                    
                    # 如果所有重试都失败，跳过当前场景
                    if not content_generation_success:
                        print(f"文案生成和验证在 {max_retries} 次尝试后仍然失败，跳过当前场景")
                        continue
                    
                    # 商品推荐
                    product_result = self.product_recommender.process({
                        "query": content_result.content
                    })
                    recommended_products = ""
                    product_success = False
                    product_error = ""
                    
                    if product_result.success:
                        print(f"\n商品推荐成功: {product_result.content}")
                        recommended_products = product_result.content.replace("```json", "").replace("```", "")
                        
                        # 解析JSON数据
                        product_goods_list = ""
                        product_recommendation_reason = ""
                        try:
                            product_data = json.loads(recommended_products)
                            # 提取商品列表和推荐原因
                            goods_list = product_data.get('goods_list', [])
                            reason = product_data.get('reason', '')
                            
                            # 格式化商品列表
                            if goods_list:
                                product_goods_list = json.dumps(goods_list, ensure_ascii=False, indent=2)
                            else:
                                product_goods_list = "无推荐商品"
                            
                            product_recommendation_reason = reason
                            
                            # 将解析后的JSON数据格式化存储
                            recommended_products = json.dumps(product_data, ensure_ascii=False, indent=2)
                            print(f"解析商品推荐JSON: {product_data}")
                            print(f"商品列表: {product_goods_list}")
                            print(f"推荐原因: {product_recommendation_reason}")
                        except json.JSONDecodeError as e:
                            print(f"JSON解析失败: {e}, 原始数据: {recommended_products}")
                            # 如果解析失败，保持原始字符串
                            product_goods_list = "JSON解析失败"
                            product_recommendation_reason = "JSON解析失败"
                        
                        product_success = True
                    else:
                        print(f"\n商品推荐失败: {product_result.error_message}")
                        product_error = product_result.error_message
                    
                    # 收集完整的文案数据
                    self.content_collector.add_content(
                        user_input=user_input,
                        persona_detail=self.persona_detail,
                        scenario_data={"content": scenario},
                        scenario_validation_result=True,
                        scenario_validation_reason=scenario_validation_reason,
                        content_data={"content": content_result.content},
                        content_validation_data={"validation_reason": content_validation_reason},
                        content_validation_result=True,
                        recommended_products=recommended_products,
                        product_goods_list=product_goods_list,
                        product_recommendation_reason=product_recommendation_reason,
                        product_recommendation_success=product_success,
                        product_recommendation_error=product_error,
                        processing_stage="completed",
                        final_status="success"
                    )
                    
                except Exception as e:
                    # 处理过程中的异常
                    print(f"处理场景时发生异常: {str(e)}")
                    self.content_collector.add_scenario_only(
                        user_input=user_input,
                        persona_detail=self.persona_detail,
                        scenario=scenario,
                        scenario_validation_result=False,
                        scenario_validation_reason=f"处理异常: {str(e)}"
                    )


            # return WorkflowResult(False, {}, f"测试完成")
                        
            # # 步骤6: 商品推荐
            # product_result = self.product_recommender.process(content_validation.data)
            # if not product_result.success:
            #     return WorkflowResult(False, {}, f"商品推荐失败: {product_result.error_message}")
            
            # # 步骤7: 商品推荐验收
            # product_validation = self.product_recommendation_validator.process(product_result.data)
            # if not product_validation.success:
            #     return WorkflowResult(False, {}, f"商品推荐验收失败: {product_validation.error_message}")
            
            # # 步骤8: 获取商品信息(图片)
            # product_info = self._get_product_info(product_validation.data)
            
            # # 步骤9: 最终文案生成
            # final_content = self.content_generator.process({
            #     "content": content_validation.data,
            #     "products": product_info
            # })
            
            # if not final_content.success:
            #     return WorkflowResult(False, {}, f"最终文案生成失败: {final_content.error_message}")
            
            # 整合所有结果
            workflow_data = {
                "persona": self.persona_detail,
                "content_count": self.content_collector.get_count(),
                "message": "文案收集完成"
            }
            
            logger.info("完整工作流执行成功")
            return WorkflowResult(True, workflow_data)
            
        except Exception as e:
            logger.error(f"工作流执行异常: {str(e)}")
            return WorkflowResult(False, {}, str(e))
    

    
    def export_content_to_excel(self, filename: str = None) -> Optional[str]:
        """导出收集的文案数据到Excel
        
        Args:
            filename: Excel文件名，如果为None则自动生成
            
        Returns:
            Optional[str]: 生成的Excel文件路径，如果没有数据则返回None
        """
        try:
            excel_file = self.content_collector.export_to_excel(filename)
            if excel_file:
                logger.info(f"文案数据已导出到: {excel_file}")
            return excel_file
        except Exception as e:
            logger.error(f"导出文案数据失败: {str(e)}")
            return None
    
    def get_collected_content_count(self) -> int:
        """获取已收集的文案数据数量
        
        Returns:
            int: 数据数量
        """
        return len(self.content_collector)
    
    def get_valid_content_count(self) -> int:
        """获取验收通过的文案数据数量
        
        Returns:
            int: 验收通过的数据数量
        """
        return len(self.content_collector.get_valid_items())
    
    def clear_collected_content(self) -> None:
        """清空已收集的文案数据"""
        self.content_collector.clear()
        logger.info("已清空收集的文案数据")
    
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
            persona_result = self.wellness_mom.process({'query': user_input})
            if not persona_result.success:
                return WorkflowResult(False, {}, f"单人设处理失败: {persona_result.error_message}")
            
            scenario_result = self.scenario_generator.process(persona_result.data)
            if not scenario_result.success:
                return WorkflowResult(False, {}, f"场景生成失败: {scenario_result.error_message}")
            
            scenario_validation = self.scenario_validator.process(scenario_result.data)
            if not scenario_validation.success:
                return WorkflowResult(False, {}, f"场景验收失败: {scenario_validation.error_message}")
            
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
                return WorkflowResult(False, {}, f"文案生成失败: {content_result.error_message}")
            
            content_validation = self.content_validator.process(content_result.data)
            if not content_validation.success:
                return WorkflowResult(False, {}, f"文案验收失败: {content_validation.error_message}")
            
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
                return WorkflowResult(False, {}, f"商品推荐失败: {product_result.error_message}")
            
            product_validation = self.product_recommendation_validator.process(product_result.data)
            if not product_validation.success:
                return WorkflowResult(False, {}, f"商品推荐验收失败: {product_validation.error_message}")
            
            return WorkflowResult(True, product_validation.data)
            
        except Exception as e:
            logger.error(f"商品推荐流程异常: {str(e)}")
            return WorkflowResult(False, {}, str(e))

# 使用示例
if __name__ == "__main__":
    
    # 定义人物画像
    persona_detail = """## 人物画像
- 你一个 养生妈妈 45 岁, 有一份清闲的文职工作
- 有一个儿子，上初中，学习一般，但非常懂礼貌、热情、好动
- 有一个丈夫，职场打工人，46 岁，面临失业风险
- 婆婆，传统且挑剔
- 闺蜜朋友多
- 特别注意养生，对全家人的养生非常注重，
- 你是一个非常尊重别人的人，包括家人， 你会看重家人家人的养生，不论是小孩、丈夫、老人、还有闺蜜、亲戚等
- 你特别懂一些网络热梗"""
    
    # 配置
    config = AgentConfig(
        name="wellness_workflow",
        description="养生妈妈工作流配置",
        agent_type=AgentType.CUSTOM
    )
    
    # 创建工作流
    workflow = WellnessWorkflow(config, persona_detail)
    
    # 运行完整工作流
    result = workflow.run_complete_workflow("")
    # result = workflow.run_complete_workflow("我想要一些秋季养生的建议")
    
    if result.success:
        print("工作流执行成功!")
        print(json.dumps(result.data, ensure_ascii=False, indent=2))
        
        # 导出收集的文案数据到Excel
        excel_file = workflow.export_content_to_excel()
        if excel_file:
            print(f"文案数据已导出到: {excel_file}")
        else:
            print("没有文案数据需要导出")
    else:
        print(f"工作流执行失败: {result.error}")