#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品推荐验收器 Agent 测试文件
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from agents.product_recommendation_validator.product_recommendation_validator_agent import ProductRecommendationValidatorAgent


def test_product_recommendation_validator():
    """测试商品推荐验收器功能"""
    print("\n=== 商品推荐验收器测试 ===")
    
    # 创建验收器实例
    validator = ProductRecommendationValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key"
    )
    
    print(f"验收器信息: {validator.get_info()}")
    
    # 测试1: 阻塞模式验收
    print("\n--- 测试阻塞模式验收 ---")
    test_params = {
        'query': '请验收这个商品推荐是否合理',
        'recommendation_to_validate': '''
        推荐商品：MacBook Pro 14英寸 M3芯片
        推荐理由：
        1. 适合程序员开发工作，性能强劲
        2. 14英寸屏幕便于携带，适合出差
        3. M3芯片能效比高，续航时间长
        4. 价格在预算范围内（约12000元）
        5. 支持多种开发环境和工具
        ''',
        'inputs': {
            'validation_criteria': '准确性、相关性、合理性、实用性'
        }
    }
    
    try:
        response = validator.process(test_params)
        if response.success:
            print(f"验收成功: {response.content[:200]}...")
            print(f"元数据: {response.metadata}")
        else:
            print(f"验收失败: {response.error_message}")
    except Exception as e:
        print(f"阻塞模式测试异常: {e}")
    
    # 测试2: 流式模式验收
    print("\n--- 测试流式模式验收 ---")
    try:
        response_count = 0
        for response in validator.process_streaming(test_params):
            response_count += 1
            if response.success:
                print(f"流式响应 {response_count}: {response.content[:100]}...")
            else:
                print(f"流式响应错误: {response.error_message}")
            
            # 限制输出数量
            if response_count >= 3:
                print("...（省略更多流式响应）")
                break
        
        print(f"流式模式验收成功，共收到 {response_count} 个响应")
    except Exception as e:
        print(f"流式模式测试异常: {e}")


def test_product_recommendation_validator_edge_cases():
    """测试边界情况"""
    print("\n=== 边界情况测试 ===")
    
    validator = ProductRecommendationValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key"
    )
    
    # 测试1: 空查询
    print("\n--- 测试空查询 ---")
    try:
        response = validator.process({'query': ''})
        print(f"空查询结果: 成功={response.success}, 内容长度={len(response.content)}")
    except Exception as e:
        print(f"空查询测试异常: {e}")
    
    # 测试2: 只有基本查询
    print("\n--- 测试基本查询 ---")
    try:
        response = validator.process({'query': '验收这个推荐'})
        if response.success:
            print(f"基本查询成功: {response.content[:100]}...")
        else:
            print(f"基本查询失败: {response.error_message}")
    except Exception as e:
        print(f"基本查询测试异常: {e}")
    
    # 测试3: 复杂验收场景
    print("\n--- 测试复杂验收场景 ---")
    complex_params = {
        'query': '请从多个维度验收这个商品推荐',
        'recommendation_to_validate': '''
        推荐商品：iPhone 15 Pro Max
        用户需求：拍照、游戏、商务使用
        推荐理由：
        1. 摄像头系统先进，支持专业摄影
        2. A17 Pro芯片性能强劲，游戏体验佳
        3. 商务功能完善，支持多种办公应用
        4. 品牌知名度高，保值性好
        ''',
        'inputs': {
            'validation_criteria': '需求匹配度、性价比、功能完整性、用户体验',
            'user_profile': '30岁商务人士，注重品质和效率',
            'budget_range': '8000-15000元'
        }
    }
    
    try:
        response = validator.process(complex_params)
        if response.success:
            print(f"复杂验收成功: {response.content[:150]}...")
        else:
            print(f"复杂验收失败: {response.error_message}")
    except Exception as e:
        print(f"复杂验收测试异常: {e}")
    
    # 测试4: 批量验收（手动实现）
    print("\n--- 测试批量验收 ---")
    recommendations = [
        "推荐商品A：适合办公的笔记本电脑",
        "推荐商品B：适合游戏的台式机",
        "推荐商品C：适合学习的平板电脑"
    ]
    
    try:
        batch_results = []
        for i, rec in enumerate(recommendations):
            params = {
                'query': f'验收推荐{i+1}',
                'recommendation_to_validate': rec
            }
            result = validator.process(params)
            batch_results.append(result)
            if result.success:
                print(f"批量验收 {i+1} 成功: {result.content[:80]}...")
            else:
                print(f"批量验收 {i+1} 失败: {result.error_message}")
        
        print(f"批量验收完成，共处理 {len(batch_results)} 个推荐")
    except Exception as e:
        print(f"批量验收测试异常: {e}")


def main():
    """主测试函数"""
    print("开始商品推荐验收器测试...")
    
    try:
        test_product_recommendation_validator()
        test_product_recommendation_validator_edge_cases()
        print("\n✅ 所有测试完成")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()