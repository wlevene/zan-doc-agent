#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试失败场景的记录功能
"""

import sys
import os
from pathlib import Path
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from content_item import ContentCollector
from agents.wellness.wellness_mom_agent import WellnessMomAgent
from agents.agents import AgentConfig, AgentType
from agents.scenario_generator.scenario_generator_agent import ScenarioGeneratorAgent
from agents.scenario_validator.scenario_validator_agent import ScenarioValidatorAgent
from agents.content_generator.content_generator_agent import ContentGeneratorAgent
from agents.content_validator.content_validator_agent import ContentValidatorAgent
from agents.product_recommender.product_recommender_agent import ProductRecommenderAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFailureScenarios:
    def __init__(self):
        self.content_collector = ContentCollector()
        
    def test_scenario_validation_failure(self):
        """测试场景验证失败的记录"""
        print("\n=== 测试场景验证失败 ===")
        
        # 模拟场景验证失败
        self.content_collector.add_scenario_only(
            user_input="测试用户输入",
            persona_detail="养生妈妈人设",
            scenario="完全不相关的场景：讨论火箭发射技术",
            scenario_validation_result=False,
            scenario_validation_reason="场景与养生妈妈人设不符，不适合生成相关文案"
        )
        
        print("已记录场景验证失败的情况")
        
    def test_content_generation_failure(self):
        """测试文案生成失败的记录"""
        print("\n=== 测试文案生成失败 ===")
        
        # 模拟文案生成失败
        self.content_collector.add_content(
            user_input="测试用户输入",
            persona_detail="养生妈妈人设",
            scenario_data={"content": "儿子熬夜打游戏黑眼圈重"},
            scenario_validation_result=True,
            scenario_validation_reason="符合养生妈妈关注家人健康的设定",
            content_data={"content": ""},
            content_validation_data={"validation_reason": ""},
            content_validation_result=False,
            content_generation_success=False,
            content_generation_error="API调用超时，文案生成失败",
            processing_stage="content_generation",
            final_status="content_failed"
        )
        
        print("已记录文案生成失败的情况")
        
    def test_content_validation_failure(self):
        """测试文案验证失败的记录"""
        print("\n=== 测试文案验证失败 ===")
        
        # 模拟文案验证失败
        self.content_collector.add_content(
            user_input="测试用户输入",
            persona_detail="养生妈妈人设",
            scenario_data={"content": "丈夫加班回家腰酸背痛"},
            scenario_validation_result=True,
            scenario_validation_reason="符合养生妈妈关注家人健康的设定",
            content_data={"content": "老公你这腰不行啊，要不要去医院看看？"},
            content_validation_data={"validation_reason": "文案语气过于直接，不符合养生妈妈温和关怀的特点"},
            content_validation_result=False,
            processing_stage="content_validation",
            final_status="validation_failed"
        )
        
        print("已记录文案验证失败的情况")
        
    def test_product_recommendation_failure(self):
        """测试商品推荐失败的记录"""
        print("\n=== 测试商品推荐失败 ===")
        
        # 模拟商品推荐失败但其他步骤成功
        self.content_collector.add_content(
            user_input="测试用户输入",
            persona_detail="养生妈妈人设",
            scenario_data={"content": "婆婆总说饭菜太清淡没味"},
            scenario_validation_result=True,
            scenario_validation_reason="符合养生妈妈注重全家养生的设定",
            content_data={"content": "婆婆您这嘴巴真是被重口味惯坏了！咱们试试用天然香料调味，既健康又有味道～"},
            content_validation_data={"validation_reason": "文案符合养生妈妈的设定，语气亲切自然"},
            content_validation_result=True,
            recommended_products="",
            product_recommendation_success=False,
            product_recommendation_error="商品数据库连接失败，无法获取推荐商品",
            processing_stage="completed",
            final_status="success"
        )
        
        print("已记录商品推荐失败的情况")
        
    def test_exception_handling(self):
        """测试异常处理的记录"""
        print("\n=== 测试异常处理 ===")
        
        # 模拟处理过程中的异常
        self.content_collector.add_scenario_only(
            user_input="测试用户输入",
            persona_detail="养生妈妈人设",
            scenario="闺蜜聚会狂炫奶茶不健康",
            scenario_validation_result=False,
            scenario_validation_reason="处理异常: JSON解析错误，无法处理场景验证结果"
        )
        
        print("已记录异常处理的情况")
        
    def run_all_tests(self):
        """运行所有测试"""
        print("开始测试失败场景的记录功能...")
        
        self.test_scenario_validation_failure()
        self.test_content_generation_failure()
        self.test_content_validation_failure()
        self.test_product_recommendation_failure()
        self.test_exception_handling()
        
        # 导出测试结果
        excel_file = self.content_collector.export_to_excel("test_failure_scenarios")
        if excel_file:
            print(f"\n测试结果已导出到: {excel_file}")
            print(f"总共记录了 {len(self.content_collector.items)} 条数据")
        else:
            print("\n导出失败")
            
if __name__ == "__main__":
    test = TestFailureScenarios()
    test.run_all_tests()