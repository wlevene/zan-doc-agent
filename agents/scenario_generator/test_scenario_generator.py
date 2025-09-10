#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScenarioGeneratorAgent 测试模块
测试场景生成器的功能
"""

from agents.scenario_generator.scenario_generator_agent import ScenarioGeneratorAgent


def test_basic_generation():
    """测试基本场景生成功能"""
    print("\n=== 测试基本场景生成 ===")
    
    generator = ScenarioGeneratorAgent()
    
    test_requirement = """
    这个人设是一个 养生妈妈 38 岁，你是一个非常尊重别人的人，包括家人， 养生妈妈会看重家人家人的健康，不论是小孩、丈夫、老人、还有闺蜜、亲戚等
    """
    
    try:
        params = {
            "query": test_requirement,
        }
        result = generator.process(params)
        print(f"生成成功: {result.success}")
        if result.success:
            print(f"生成的场景: {result.content[:200]}...")
        else:
            print(f"生成失败: {result.error_message}")
    except Exception as e:
        print(f"测试出错: {e}")



def main():
    """主函数 - 运行ScenarioGenerator测试"""
    print("开始 ScenarioGeneratorAgent 测试...")
    
    # 运行所有测试
    test_basic_generation()
    
    print("\nScenarioGeneratorAgent 测试完成！")


if __name__ == "__main__":
    main()