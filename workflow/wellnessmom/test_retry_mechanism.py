#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重试机制的脚本
模拟文案验证失败的情况，验证重试逻辑是否正常工作
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

from agents.wellness.wellness_mom_agent import WellnessMomAgent
from agents.agents import AgentConfig, AgentType
from agents.scenario_generator.scenario_generator_agent import ScenarioGeneratorAgent
from agents.scenario_validator.scenario_validator_agent import ScenarioValidatorAgent
from agents.content_generator.content_generator_agent import ContentGeneratorAgent
from agents.content_validator.content_validator_agent import ContentValidatorAgent
from agents.product_recommender.product_recommender_agent import ProductRecommenderAgent
from agents.product_recommendation_validator.product_recommendation_validator_agent import ProductRecommendationValidatorAgent
from agents.product_recommender.product_database import ProductDatabase
from content_item import ContentCollector

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockContentValidator:
    """模拟文案验证器，用于测试重试机制"""
    
    def __init__(self, fail_count=2):
        self.fail_count = fail_count  # 前几次验证失败
        self.call_count = 0
    
    def process(self, data):
        self.call_count += 1
        print(f"\n[MockContentValidator] 第 {self.call_count} 次调用")
        
        # 模拟验证结果
        if self.call_count <= self.fail_count:
            # 前几次验证失败
            result_content = json.dumps({
                "result": False,
                "reason": f"文案不够生动有趣，缺乏网络热梗元素 (第{self.call_count}次验证)"
            }, ensure_ascii=False)
            print(f"[MockContentValidator] 验证失败: {result_content}")
        else:
            # 最后一次验证通过
            result_content = json.dumps({
                "result": True,
                "reason": "文案符合养生妈妈的语言风格，生动有趣"
            }, ensure_ascii=False)
            print(f"[MockContentValidator] 验证通过: {result_content}")
        
        # 模拟返回结果
        class MockResult:
            def __init__(self, success, content):
                self.success = success
                self.content = content
        
        return MockResult(True, result_content)

class MockContentGenerator:
    """模拟文案生成器，用于测试重试机制"""
    
    def __init__(self):
        self.call_count = 0
    
    def process(self, data):
        self.call_count += 1
        query = data.get('query', '')
        suggestion = data.get('suggestion', '')
        
        print(f"\n[MockContentGenerator] 第 {self.call_count} 次调用")
        print(f"[MockContentGenerator] Query: {query}")
        if suggestion:
            print(f"[MockContentGenerator] Suggestion: {suggestion}")
        
        # 根据是否有建议生成不同的文案
        if suggestion:
            content = f"根据建议优化的文案 (第{self.call_count}次): 姐妹们，养生路上不孤单！{suggestion}，让我们一起加油！💪"
        else:
            content = f"初始文案 (第{self.call_count}次): 养生小贴士分享"
        
        print(f"[MockContentGenerator] 生成内容: {content}")
        
        # 模拟返回结果
        class MockResult:
            def __init__(self, success, content):
                self.success = success
                self.content = content
        
        return MockResult(True, content)

def test_retry_mechanism():
    """测试重试机制"""
    print("=== 开始测试重试机制 ===")
    
    # 创建模拟的生成器和验证器
    mock_content_generator = MockContentGenerator()
    mock_content_validator = MockContentValidator(fail_count=2)  # 前2次失败，第3次成功
    
    # 创建内容收集器
    content_collector = ContentCollector()
    
    # 模拟重试逻辑（从wellness_workflow.py复制的逻辑）
    scenario = "测试场景：分享养生小贴士"
    user_input = "测试用户输入"
    persona_detail = "养生妈妈"
    scenario_validation_reason = "场景验证通过"
    
    print(f"\n测试场景: {scenario}")
    
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
            content_result = mock_content_generator.process({"query": scenario})
        else:
            # 重试时传递suggestion参数
            content_result = mock_content_generator.process({
                "query": scenario,
                "suggestion": content_validation_reason
            })
            print(f"重试文案生成，建议: {content_validation_reason}")
        
        if not content_result.success:
            # 文案生成失败
            print(f"文案生成失败: {content_result.error_message}")
            continue
        
        print(f"文案生成成功: {content_result.content}")
        
        # 文案验证
        content_validation = mock_content_validator.process({"query": content_result.content, "scenario": scenario})
        if not content_validation.success:
            # 文案验证API调用失败
            print(f"文案验证API调用失败: {content_validation.error_message}")
            continue
        
        print(f"\ncontent_validation: {content_validation.content}")
        content_validation_json = json.loads(content_validation.content)
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
    
    # 如果所有重试都失败，跳过当前场景
    if not content_generation_success:
        print(f"文案生成和验证在 {max_retries} 次尝试后仍然失败")
        return False
    else:
        print(f"\n=== 重试机制测试成功！===")
        print(f"总共尝试了 {mock_content_generator.call_count} 次文案生成")
        print(f"总共尝试了 {mock_content_validator.call_count} 次文案验证")
        print(f"最终生成的文案: {content_result.content}")
        return True

if __name__ == "__main__":
    success = test_retry_mechanism()
    if success:
        print("\n✅ 重试机制测试通过！")
    else:
        print("\n❌ 重试机制测试失败！")