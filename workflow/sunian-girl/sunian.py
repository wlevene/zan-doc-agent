#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


作者: SOLO Coding
创建时间: 2024-01-15
"""

import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加项目根目录到Python路径（必须在导入本地模块之前）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入通用模块
from workflow.base_workflow import ContentItem, ContentCollector

# 导入所有需要的agent
from agents.wellness.wellness_mom_agent import WellnessMomAgent
from agents.agents import AgentConfig, AgentType
from agents.scenario_generator.scenario_generator_agent import ScenarioGeneratorAgent
from agents.scenario_validator.scenario_validator_agent import ScenarioValidatorAgent
from agents.content_generator.content_generator_agent import ContentGeneratorAgent
from agents.content_validator.content_validator_agent import ContentValidatorAgent
from agents.content_rewriter.content_rewriter_agent import ContentRewriterAgent
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
    """工作流程"""
    
    def __init__(self, config: AgentConfig, persona_detail: str, product_k3_code: str):
        """初始化工作流"""
        self.config = config
        self.product_db = ProductDatabase()
        self.persona_detail = persona_detail
        self.product_k3_code = product_k3_code
        
        # 定义API配置
        api_key = "app-default-key"  # 默认API密钥
        base_url = "http://119.45.130.88:8080/v1"  # 默认API端点
        app_id = "wellness-mom-app"  # 默认应用ID
        
        # 初始化所有agent
        self.wellness_mom = WellnessMomAgent(api_key, base_url, app_id)
        self.scenario_generator = ScenarioGeneratorAgent()
        self.scenario_generator.set_k3code(self.product_k3_code)
        self.scenario_validator = ScenarioValidatorAgent()
        self.content_generator = ContentGeneratorAgent()
        self.content_validator = ContentValidatorAgent()
        self.content_rewriter = ContentRewriterAgent()
        self.product_recommender = ProductRecommenderAgent()
        self.product_recommendation_validator = ProductRecommendationValidatorAgent(base_url, api_key)
        
        # 初始化数据收集器
        self.content_collector = ContentCollector()
        
        logger.info("工作流初始化完成")
    
    def run_complete_workflow(self, user_input: str) -> WorkflowResult:
        """运行完整的工作流程"""
        try:
            logger.info(f"开始执行完整工作流，用户输入: {user_input}")
            
            # 步骤1: 单人设处理
            # persona_result = self.wellness_mom.process({'query': user_input})
            # if not persona_result.success:
            #     return WorkflowResult(False, {}, f"单人设处理失败: {persona_result.error_message}")
            
            # 步骤2: 场景生成
            scenario_result = self.scenario_generator.process(
                {"query": self.persona_detail
                }
                )
            if not scenario_result.success:
                return WorkflowResult(False, {}, f"场景生成失败: {scenario_result.error_message}")

            print(f"scenario_result: {scenario_result.content}")
            scenario_result.content = scenario_result.content.replace("```json", "").replace("```", "")

            # array scenario  for scenario_result.content
            # scenario_result.content is already processed as newline-separated strings
            scenario_array = [line.strip() for line in scenario_result.content.split('\n') if line.strip()]
            print(f"scenario_array: {scenario_array}")

            # 步骤2: 场景验证和处理
            index = 0
            for scenario in scenario_array:
                index = index + 1

                # if index > 1:
                #     break
                print(f"\n🔍 开始处理场景: {scenario}")
                try:
                    # 场景验证
                    print(f"📋 正在进行场景验证...")
                    scenario_validation_result = self.scenario_validator.process({"scene":scenario, "persona":self.persona_detail})
                    if not scenario_validation_result.success:
                        # 场景验证失败，记录错误
                        print(f"❌ 场景验证API调用失败: {scenario_validation_result.error_message}")
                        self.content_collector.add_scenario_only(
                            user_input=user_input,
                            persona_detail=self.persona_detail,
                            scenario=scenario,
                            scenario_validation_result=False,
                            scenario_validation_reason=f"场景验证API调用失败: {scenario_validation_result.error_message}"
                        )
                        continue
                    
                    print(f"✅ 场景验证API调用成功，解析结果...")
                    scenario_result_content = scenario_validation_result.content.replace("```json", "").replace("```", "")
                    print(f"📄 场景验证原始内容: {scenario_result_content}")
                    
                    try:
                        scenario_result_json = json.loads(scenario_result_content)
                        scenario_validation_passed = scenario_result_json.get("result", False)
                        scenario_validation_reason = scenario_result_json.get("reason", "")
                        print(f"🔍 解析结果 - 验证通过: {scenario_validation_passed}, 原因: {scenario_validation_reason}")
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {e}")
                        print(f"📄 原始内容: {scenario_result_content}")
                        self.content_collector.add_scenario_only(
                            user_input=user_input,
                            persona_detail=self.persona_detail,
                            scenario=scenario,
                            scenario_validation_result=False,
                            scenario_validation_reason=f"JSON解析失败: {e}"
                        )
                        continue
                    
                    if not scenario_validation_passed:
                        # 场景验证未通过，记录失败原因
                        print(f"❌ 场景验证失败: {scenario_validation_reason}")
                        self.content_collector.add_scenario_only(
                            user_input=user_input,
                            persona_detail=self.persona_detail,
                            scenario=scenario,
                            scenario_validation_result=False,
                            scenario_validation_reason=scenario_validation_reason
                        )
                        continue
                    
                    print(f"✅ 场景验证通过: {scenario_validation_reason}")
                    print(f"🚀 开始文案生成和验证流程...")
                    
                    # 文案生成和验证（带重试机制）
                    max_retries = 3
                    content_generation_success = False
                    content_result = None
                    content_validation_reason = ""
                    
                    for retry_count in range(max_retries):
                        print(f"\n=== 文案生成尝试 {retry_count + 1}/{max_retries} ===")
                        
                        # 文案生成
                        if retry_count == 0:
                            # 第一次生成，使用文案生成器
                            print("使用文案生成器进行首次生成")
                            content_result = self.content_generator.process(
                                {
                                    "query": scenario, 
                                    "suggestion": "无",
                                    "persona": self.persona_detail,
                                    "text":"无",
                                })
                        else:
                            # 重试时使用文案重写器，传入原文案和修改建议
                            print(f"使用文案重写器进行重写，建议: {content_validation_reason}")
                            content_result = self.content_generator.process({
                                "query": scenario, 
                                "suggestion": content_validation_reason,     
                                "persona": self.persona_detail,
                                "text": content_result.content, 
                            })
                        
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
                                    k3_code="",  # 空的K3编码
                                    processing_stage="content_generation",
                                    final_status="content_failed"
                                )
                            continue
                        
                        print(f"文案生成成功: {content_result.content}")
                        
                        # 文案验证
                        content_validation = self.content_validator.process({
                            "query": "请验收这个养生文案是否符合要求",
                            "content_to_validate": content_result.content,
                            "persona": self.persona_detail,
                            "scenario": scenario
                        })
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
                                    k3_code="",  # 空的K3编码
                                    processing_stage="content_validation",
                                    final_status="validation_failed"
                                )
                            continue
                        
                        print(f"\ncontent_validation: {content_validation}")
                        content_validation_json = json.loads(content_validation.content.replace("```json", "").replace("```", ""))
                        content_validation_passed = content_validation_json.get("result", False)
                        content_validation_reason = content_validation_json.get("reason", "")
                        
                        if content_validation_passed:
                            # 文案验证通过，继续后续流程
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
                                    k3_code="",  # 空的K3编码
                                    processing_stage="content_validation",
                                    final_status="validation_failed"
                                )


                    if self.product_k3_code:
                        # 直接使用指定的K3编码获取商品信息
                        product_info = self.product_db.get_product_by_k3_code(self.product_k3_code)
                        if product_info:
                            # 构造与推荐器相同格式的响应
                            product_data = {"goods": product_info.to_dict()}
                            product_result = type('AgentResponse', (), {
                                'success': True,
                                'content': json.dumps(product_data, ensure_ascii=False, indent=2),
                                'error': None
                            })()
                        else:
                            # 如果找不到商品，创建失败响应
                            product_result = type('AgentResponse', (), {
                                'success': False,
                                'content': "",
                                'error': f"未找到K3编码为 {self.product_k3_code} 的商品"
                            })()
                    else:
                        # 使用推荐器获取商品
                        product_result = self.product_recommender.process({
                            "query": content_result.content,
                        })

                 
                    recommended_products = ""
                    product_success = False
                    product_error = ""
                    # 初始化商品相关变量，确保在所有情况下都有定义
                    product_recommendation_reason = ""
                    k3_code = ""
                    
                    if product_result.success:
                        print(f"\n商品推荐成功: {product_result.content}")
                        recommended_products = product_result.content.replace("```json", "").replace("```", "")
                        
                        # 解析JSON数据
                        try:
                            product_data = json.loads(recommended_products)
                            # 提取商品信息和推荐原因
                            reason = product_data.get('reason', '')
                            
                            # 支持两种数据结构：goods_list（数组）或 goods（单个对象）
                            # 由于现在只推荐单个商品，优先处理 goods 单个对象格式
                            if 'goods' in product_data:
                                # 新格式：goods 单个对象
                                goods_obj = product_data.get('goods')
                                if goods_obj and isinstance(goods_obj, dict):
                                    # 提取K3编码
                                    k3_code = goods_obj.get('k3_code', '')
                            elif 'goods_list' in product_data:
                                # 旧格式：goods_list 数组，取第一个商品
                                goods_list = product_data.get('goods_list', [])
                                if goods_list and len(goods_list) > 0:
                                    first_good = goods_list[0]
                                    if isinstance(first_good, dict):
                                        k3_code = first_good.get('k3_code', '')
                            
                            product_recommendation_reason = reason
                            
                            # 将解析后的JSON数据格式化存储
                            recommended_products = json.dumps(product_data, ensure_ascii=False, indent=2)
                            print(f"解析商品推荐JSON: {product_data}")
                            print(f"K3编码: {k3_code}")
                            print(f"推荐原因: {product_recommendation_reason}")
                        except json.JSONDecodeError as e:
                            print(f"JSON解析失败: {e}, 原始数据: {recommended_products}")
                            # 如果解析失败，保持原始字符串
                            product_recommendation_reason = "JSON解析失败"
                            k3_code = ""
                        
                        product_success = True
                        
                        # 商品推荐成功后，进行文案重写处理
                        print(f"🔄 开始文案重写处理（基于推荐商品优化文案）")
                        
                        # 保存原始文案
                        original_content = content_result.content
                        
                        # 准备商品信息用于重写
                        goods_info = ""
                        selling_points = ""
                        formula_source = ""
                        product_name = ""  # 添加产品名称变量
                        price = ""  # 添加价格变量
                        if recommended_products and recommended_products != "无推荐商品" and product_recommendation_reason != "JSON解析失败":
                            try:
                                goods_data = json.loads(recommended_products)
                                # 处理单个商品，从goods对象中提取信息
                                if isinstance(goods_data, dict) and 'goods' in goods_data:
                                    goods_obj = goods_data['goods']
                                    name = goods_obj.get('name', '未知商品')
                                    product_name = name  # 保存产品名称
                                    description = goods_obj.get('description', '无描述')
                                    price = str(goods_obj.get('price', '未知价格'))  # 保存价格信息
                                    # 添加新字段：产品卖点和配方出处
                                    selling_points = goods_obj.get('product_selling_points', '').strip()
                                    formula_source = goods_obj.get('formula_source', '').strip()
                                    
                                    # 构建完整的商品信息格式：名称-描述-价格-卖点-配方出处
                                    goods_parts = [name, description, f"价格:{price}元"]
                                    # if selling_points:
                                    #     goods_parts.append(f"卖点:{selling_points}")
                                    # if formula_source:
                                    #     goods_parts.append(f"配方:{formula_source}")
                                    
                                    goods_info = "-".join(goods_parts)  # 单个商品信息
                                elif isinstance(goods_data, dict):
                                    # 兼容旧格式：直接从根对象获取
                                    name = goods_data.get('name', '未知商品')
                                    product_name = name  # 保存产品名称
                                    description = goods_data.get('description', '无描述')
                                    price = str(goods_data.get('price', '未知价格'))  # 保存价格信息
                                    selling_points = goods_data.get('product_selling_points', '').strip()
                                    formula_source = goods_data.get('formula_source', '').strip()
                                    
                                    goods_parts = [name, description, f"价格:{price}元"]
                                    if selling_points:
                                        goods_parts.append(f"卖点:{selling_points}")
                                    if formula_source:
                                        goods_parts.append(f"配方:{formula_source}")
                                    
                                    goods_info = "-".join(goods_parts)
                            except Exception as e:
                                print(f"商品信息解析异常: {e}")
                                goods_info = recommended_products
                        
                        # 使用文案重写大师重写文案
                        print(f"📝 准备重写文案: {original_content}")
                        print(f"👤 重写参数 - 人设: {self.persona_detail[:100]}...")
                        print(f"🎬 重写参数 - 场景: {scenario}")
                        print(f"🛍️ 重写参数 - 商品信息: {goods_info[:200]}..." if goods_info else "🛍️ 重写参数 - 商品信息: 无")
                        
                        rewrite_result = self.content_rewriter.process({
                            "persona": self.persona_detail,
                            "scenario": scenario,
                            "query": original_content,
                            "goods": goods_info if goods_info else None,
                            "formula_source": formula_source,
                            "product_selling_points": selling_points,
                        })
                        
                        if rewrite_result.success:
                            print(f"✅ 文案重写成功!")
                            print(f"📝 重写后文案内容: {rewrite_result.content}")
                            print(f"📊 文案长度变化: {len(original_content)} → {len(rewrite_result.content)}")
                            
                            # 使用重写后的文案
                            content_result = rewrite_result
                            
                            print(f"📋 文案重写成功，将在后续统一记录完整数据")
                        else:
                            print(f"❌ 文案重写失败: {rewrite_result.error_message}")
                            print(f"🔄 使用原始文案继续流程")
                            
                            print(f"📋 重写失败，使用原始文案，将在后续统一记录完整数据")
                    else:
                        print(f"\n商品推荐失败: {product_result.error_message}")
                        product_error = product_result.error_message
                        
                        # 商品推荐失败，仍然尝试重写文案（不传入商品信息）
                        print(f"🔄 商品推荐失败，但仍进行文案重写处理")
                        
                        # 保存原始文案
                        original_content = content_result.content
                        
                        # 使用文案重写大师重写文案（不传入商品信息）
                        print(f"📝 准备重写文案: {original_content}")
                        print(f"👤 重写参数 - 人设: {self.persona_detail[:100]}...")
                        print(f"🎬 重写参数 - 场景: {scenario}")
                        
                        rewrite_result = self.content_rewriter.process({
                            "persona": self.persona_detail,
                            "scenario": scenario,
                            "query": original_content
                        })
                        
                        if rewrite_result.success:
                            print(f"✅ 文案重写成功!")
                            print(f"📝 重写后文案内容: {rewrite_result.content}")
                            print(f"📊 文案长度变化: {len(original_content)} → {len(rewrite_result.content)}")
                            
                            # 使用重写后的文案
                            content_result = rewrite_result
                            
                            print(f"📋 文案重写成功，将在后续统一记录完整数据")
                        else:
                            print(f"❌ 文案重写失败: {rewrite_result.error_message}")
                            print(f"🔄 使用原始文案继续流程")
                            
                            print(f"📋 重写失败，使用原始文案，将在后续统一记录完整数据")
                    
                    # 收集完整的文案数据
                    # 构建content_data，如果进行了重写，需要保存原始内容和重写标记
                    content_data = {"content": content_result.content}
                    
                    # 检查是否进行了重写（通过比较original_content变量是否存在且不同）
                    if 'original_content' in locals() and original_content != content_result.content:
                        content_data.update({
                            "rewritten": True,
                            "original_content": original_content,
                            "rewrite_reason": "强制重写处理"
                        })
                        print(f"📋 记录重写信息: 原始长度={len(original_content)}, 重写后长度={len(content_result.content)}")
                    
                    
                    self.content_collector.add_content(
                        user_input=user_input,
                        persona_detail=self.persona_detail,
                        scenario_data={"content": scenario},
                        scenario_validation_result=True,
                        scenario_validation_reason=scenario_validation_reason,
                        content_data=content_data,
                        content_validation_data={"validation_reason": content_validation_reason},
                        content_validation_result=True,
                        recommended_products=recommended_products,
                        product_recommendation_reason=product_recommendation_reason,
                        product_recommendation_success=product_success,
                        product_recommendation_error=product_error,
                        k3_code=k3_code,  # 新增：传递K3编码
                        product_name=product_name,  # 新增：传递产品名称
                        product_selling_points=selling_points,  # 新增：传递商品卖点
                        formula_source=formula_source,  # 新增：传递配方出处
                        product_price=price,  # 新增：传递商品价格
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
    
    def _get_product_info(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取单个商品信息包括图片"""
        try:
            k3_code = product_data.get('k3_code', '')
            if not k3_code:
                return {}
            
            # 通过k3_code获取商品信息
            product = self.product_db.get_product_by_k3_code(k3_code)
            if product:
                product_dict = product.to_dict()
                # 获取图片信息
                image_info = self.product_db.get_product_image(product.id)
                if image_info:
                    product_dict['image'] = image_info
                return product_dict
            
            return {}
            
        except Exception as e:
            logger.error(f"获取商品信息失败: {str(e)}")
            return {}
    
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
    
    # 从配置文件中导入人物画像和产品K3代码
    from workflow.configs.sunian_config import persona_detail, product_k3_code
    
    # 配置
    config = AgentConfig(
        name="sunian_workflow",
        description="素年养生工作流配置",
        agent_type=AgentType.CUSTOM
    )
    # 创建工作流
    workflow = WellnessWorkflow(config, persona_detail, product_k3_code)
    
    # 运行完整工作流
    result = workflow.run_complete_workflow("")
    
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