#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScenarioGeneratorAgent 测试模块
测试场景生成器的功能
"""

from scenario_generator_agent import ScenarioGeneratorAgent


def test_scenario_generator():
    """测试场景生成器"""
    print("\n=== 测试场景生成器 ===")
    
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="app-your-scenario-generator-key"  # 请替换为实际的app_key
    )
    
    # 测试需求
    test_requirement = """
    产品：智能家居控制系统
    目标用户：25-40岁的城市白领
    核心功能：语音控制、远程监控、节能管理
    使用场景：工作日晚上回家、周末在家休息、出差期间远程控制
    """
    
    try:
        # 阻塞模式测试
        print("\n--- 阻塞模式生成 ---")
        params = {
            "query": test_requirement,
            "scenario_type": "营销场景",
            "target_audience": "25-40岁的城市白领",
            "user": "test_user"
        }
        result = generator.process(params)
        print(f"生成成功: {result.success}")
        if result.success:
            print(f"生成的场景: {result.content}")
        else:
            print(f"生成失败: {result.error_message}")
        
        # 流式模式测试
        print("\n--- 流式模式生成 ---")
        print("流式生成结果:")
        params = {
            "query": test_requirement,
            "scenario_type": "营销场景",
            "target_audience": "25-40岁的城市白领",
            "user": "test_user"
        }
        for chunk in generator.process_streaming(params):
            if chunk.success:
                print(chunk.content, end="", flush=True)
            else:
                print(f"\n错误: {chunk.error_message}")
        print("\n")
        
    except Exception as e:
        print(f"生成器测试出错: {e}")


def test_agent_info():
    """测试Agent信息"""
    print("\n=== ScenarioGenerator Agent 信息测试 ===")
    
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="app-generator-key"
    )
    
    # 打印Agent信息
    print(f"生成器类型: {generator.config.agent_type.value}")
    print(f"生成器名称: {generator.config.name}")
    print(f"生成器描述: {generator.config.description}")


def test_multiple_scenarios():
    """测试批量场景生成"""
    print("\n=== 批量场景生成测试 ===")
    
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="app-generator-key"
    )
    
    try:
        scenarios = generator.generate_multiple_scenarios(
            base_requirement="智能家居产品推广",
            scenario_count=3,
            scenario_types=["营销场景", "用户故事", "使用案例"]
        )
        
        print(f"生成场景数量: {len(scenarios)}")
        for i, scenario in enumerate(scenarios, 1):
            if scenario.success:
                print(f"\n场景 {i}: {scenario.content[:100]}...")
            else:
                print(f"\n场景 {i} 生成失败: {scenario.error_message}")
                
    except Exception as e:
        print(f"批量生成测试出错: {e}")


def test_parameter_validation():
    """测试参数验证"""
    print("\n=== ScenarioGenerator 参数验证测试 ===")
    
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key"
    )
    
    print("\n1. 测试缺少必需参数")
    try:
        result = generator.process({"inputs": {"test": "value"}})
        print(f"结果: {result.success}")
    except ValueError as e:
        print(f"参数验证错误（预期）: {e}")
    
    print("\n2. 测试正确的参数")
    try:
        result = generator.process({
            "query": "测试场景生成",
            "scenario_type": "测试场景",
            "inputs": {"test": "value"}
        })
        print(f"结果: {result.success}")
        if not result.success:
            print(f"API错误（预期）: {result.error_message}")
    except Exception as e:
        print(f"其他错误: {e}")


def main():
    """主函数 - 运行ScenarioGenerator测试"""
    print("开始 ScenarioGeneratorAgent 测试...")
    
    # 运行所有测试
    test_scenario_generator()
    test_agent_info()
    test_multiple_scenarios()
    test_parameter_validation()
    
    print("\nScenarioGeneratorAgent 测试完成！")


if __name__ == "__main__":
    main()