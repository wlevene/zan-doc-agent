#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品推荐器 Agent 测试文件
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from agents.product_recommender.product_recommender_agent import ProductRecommenderAgent


def test_product_recommender():
    """测试商品推荐器功能"""
    print("\n=== 商品推荐器测试 ===")
    
    # 创建推荐器实例
    recommender = ProductRecommenderAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key"
    )
    
    print(f"推荐器信息: {recommender.get_info()}")
    
    # 测试1: 阻塞模式推荐
    print("\n--- 测试阻塞模式推荐 ---")
    test_params = {
        'query': '我想买一款适合办公的笔记本电脑',
        'user_profile': '程序员，经常出差',
        'scenario': '办公、编程、轻度游戏',
        'budget': '8000-12000元',
        'category': '笔记本电脑'
    }
    
    try:
        response = recommender.process(test_params)
        if response.success:
            print(f"推荐成功: {response.content[:200]}...")
            print(f"元数据: {response.metadata}")
        else:
            print(f"推荐失败: {response.error_message}")
    except Exception as e:
        print(f"阻塞模式测试异常: {e}")
    
    # 测试2: 流式模式推荐
    print("\n--- 测试流式模式推荐 ---")
    try:
        response_count = 0
        for response in recommender.process_streaming(test_params):
            response_count += 1
            if response.success:
                print(f"流式响应 {response_count}: {response.content[:100]}...")
            else:
                print(f"流式响应错误: {response.error_message}")
            
            # 限制输出数量
            if response_count >= 3:
                print("...（省略更多流式响应）")
                break
        
        print(f"流式模式生成成功，共收到 {response_count} 个响应")
    except Exception as e:
        print(f"流式模式测试异常: {e}")


def test_product_recommender_edge_cases():
    """测试边界情况"""
    print("\n=== 边界情况测试 ===")
    
    recommender = ProductRecommenderAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key"
    )
    
    # 测试1: 空查询
    print("\n--- 测试空查询 ---")
    try:
        response = recommender.process({'query': ''})
        print(f"空查询结果: 成功={response.success}, 内容长度={len(response.content)}")
    except Exception as e:
        print(f"空查询测试异常: {e}")
    
    # 测试2: 只有基本查询
    print("\n--- 测试基本查询 ---")
    try:
        response = recommender.process({'query': '推荐一款手机'})
        if response.success:
            print(f"基本查询成功: {response.content[:100]}...")
        else:
            print(f"基本查询失败: {response.error_message}")
    except Exception as e:
        print(f"基本查询测试异常: {e}")
    
    # 测试3: 复杂参数
    print("\n--- 测试复杂参数 ---")
    complex_params = {
        'query': '为我推荐适合的产品',
        'user_profile': '25岁女性，喜欢时尚，注重品质',
        'scenario': '日常通勤、社交聚会、旅行',
        'budget': '1000-3000元',
        'category': '包包',
        'inputs': {
            'style_preference': '简约现代',
            'color_preference': '黑色、米色',
            'brand_preference': '中高端品牌'
        }
    }
    
    try:
        response = recommender.process(complex_params)
        if response.success:
            print(f"复杂参数推荐成功: {response.content[:150]}...")
        else:
            print(f"复杂参数推荐失败: {response.error_message}")
    except Exception as e:
        print(f"复杂参数测试异常: {e}")


def main():
    """主测试函数"""
    print("开始商品推荐器测试...")
    
    try:
        test_product_recommender()
        test_product_recommender_edge_cases()
        print("\n✅ 所有测试完成")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()