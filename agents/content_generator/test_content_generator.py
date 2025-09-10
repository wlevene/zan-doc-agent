#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContentGeneratorAgent 测试模块
测试文案生成器的功能
"""

from agents.content_generator.content_generator_agent import ContentGeneratorAgent


def test_content_generator():
    """测试文案生成器"""
    print("\n=== 测试文案生成器 ===")
    
    generator = ContentGeneratorAgent()
    
    try:
        # 阻塞模式测试
        print("\n--- 阻塞模式生成 ---")
        params = {
            "query": "为养生妈妈生成一段关于秋季养生的文案",
            "scenario_content": "秋季天气转凉，需要注意保暖和饮食调理",
            "persona": "养生妈妈，38岁，关注家人健康"
        }
        result = generator.process(params)
        print(f"生成成功: {result.success}")
        if result.success:
            print(f"生成结果: {result.content}")
        else:
            print(f"生成失败: {result.error_message}")
        
        # 流式模式测试
        print("\n--- 流式模式生成 ---")
        print("流式生成结果:")
        params = {
            "query": "生成一段关于健康饮食的温馨提醒",
            "scenario_content": "女儿偷吃薯片被发现，需要温和地教育",
            "persona": "养生妈妈，温和耐心，注重家庭和谐"
        }
        for chunk in generator.process_streaming(params):
            if chunk.success:
                print(chunk.content, end="", flush=True)
            else:
                print(f"\n错误: {chunk.error_message}")
        print("\n")
        
        # 批量生成测试
        print("\n--- 批量生成测试 ---")
        queries = [
            "生成一段关于早餐重要性的文案",
            "写一个关于运动健身的温馨提醒",
            "创作一段关于睡眠质量的建议"
        ]
        scenario = "日常生活中的健康管理场景"
        
        # 为批量生成添加必要的参数
        batch_params_list = []
        for query in queries:
            batch_params_list.append({
                "query": query,
                "scenario_content": scenario,
                "persona": "养生妈妈，38岁，关注家人健康"
            })
        
        # 手动批量处理（因为 generate_batch 方法不支持复杂参数）
        batch_results = []
        for params in batch_params_list:
            result = generator.process(params)
            batch_results.append(result)
        for i, result in enumerate(batch_results, 1):
            print(f"\n批量生成 {i}:")
            if result.success:
                print(f"内容: {result.content[:100]}...")  # 只显示前100个字符
            else:
                print(f"失败: {result.error_message}")
        
    except Exception as e:
        print(f"生成器测试出错: {e}")


def test_content_generator_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    generator = ContentGeneratorAgent()
    
    try:
        # 测试空查询
        print("\n--- 测试空查询 ---")
        result = generator.process({"query": ""})
        print(f"空查询结果: {result.success}, 内容长度: {len(result.content)}")
        
        # 测试只有场景没有查询
        print("\n--- 测试只有场景 ---")
        result = generator.process({
            "scenario_content": "这是一个测试场景"
        })
        print(f"只有场景结果: {result.success}")
        
        # 测试复杂参数
        print("\n--- 测试复杂参数 ---")
        complex_params = {
            "query": "生成文案",
            "persona": "养生妈妈",
            "tone": "温和亲切",
            "length": "中等长度",
            "target_audience": "家庭主妇",
            "scenario_content": "日常生活场景"
        }
        result = generator.process(complex_params)
        print(f"复杂参数结果: {result.success}")
        
    except Exception as e:
        print(f"边界测试出错: {e}")


def main():
    """主函数 - 运行ContentGenerator测试"""
    print("开始 ContentGeneratorAgent 测试...")
    
    # 运行所有测试
    test_content_generator()
    test_content_generator_edge_cases()
    
    print("\nContentGeneratorAgent 测试完成！")


if __name__ == "__main__":
    main()