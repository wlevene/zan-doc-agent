#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Agent 系统测试 (向后兼容入口)

注意：此文件已重构为模块化测试结构。
推荐使用以下新的测试文件：
- test_content_validator.py: ContentValidatorAgent 测试
- test_scenario_generator.py: ScenarioGeneratorAgent 测试  
- test_agent_manager.py: AgentManager 测试
- test_runner.py: 统一测试运行器

使用方法：
  python test_runner.py                    # 运行所有测试
  python test_runner.py -t content_validator # 运行指定测试
  python test_runner.py -i                 # 交互式模式
"""

import warnings
from agents import ContentValidatorAgent, ScenarioGeneratorAgent, AgentConfig, AgentManager

# 导入新的测试模块
try:
    import test_content_validator
    import test_scenario_generator
    import test_agent_manager
    import test_runner
except ImportError as e:
    print(f"警告：无法导入新的测试模块: {e}")
    print("请确保所有测试文件都在同一目录下")


def test_content_validator():
    """测试文案场景验收器 (已迁移到 test_content_validator.py)"""
    warnings.warn(
        "test_content_validator() 已迁移到 test_content_validator.py，"
        "建议使用新的模块化测试结构",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("\n=== 测试文案场景验收器 (兼容模式) ===")
    print("提示：此功能已迁移到 test_content_validator.py")
    print("建议运行: python test_content_validator.py")
    
    validator = ContentValidatorAgent(
        endpoint="http://119.45.130.88:8080/v1",
        app_key="app-ixK02FbhtS9QiklR0pXo0eu0"  # 请替换为实际的app_key
    )
    
    try:
        # 阻塞模式测试
        print("\n--- 阻塞模式验收 ---")
        params = {
            "query": "女儿藏薯片被发现",
            "persona": "这个人设是一个 养生妈妈 38 岁，你是一个非常尊重别人的人，包括家人， 养生妈妈会看重家人家人"
        }
        result = validator.process(params)
        print(f"验收成功: {result.success}")
        if result.success:
            print(f"验收结果: {result.content}")
        else:
            print(f"验收失败: {result.error_message}")
        
    except Exception as e:
        print(f"验收器测试出错: {e}")


def test_scenario_generator():
    """测试场景生成器 (已迁移到 test_scenario_generator.py)"""
    warnings.warn(
        "test_scenario_generator() 已迁移到 test_scenario_generator.py，"
        "建议使用新的模块化测试结构",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("\n=== 测试场景生成器 (兼容模式) ===")
    print("提示：此功能已迁移到 test_scenario_generator.py")
    print("建议运行: python test_scenario_generator.py")
    
    # 调用新的测试模块
    try:
        test_scenario_generator.test_scenario_generator()
    except NameError:
        print("无法调用新的测试模块，使用简化版本")
        print("请运行: python test_scenario_generator.py 获得完整测试")


def test_agent_info():
    """测试Agent信息获取 (已迁移到各个测试模块)"""
    warnings.warn(
        "test_agent_info() 已迁移到各个测试模块，"
        "建议使用新的模块化测试结构",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("\n=== 测试Agent信息 (兼容模式) ===")
    print("提示：此功能已分别迁移到各个测试模块")
    print("建议运行: python test_runner.py 获得完整测试")
    
    # 调用新的测试模块
    try:
        print("\n--- ContentValidatorAgent 信息 ---")
        test_content_validator.test_agent_info()
        print("\n--- ScenarioGeneratorAgent 信息 ---")
        test_scenario_generator.test_agent_info()
    except NameError:
        print("无法调用新的测试模块，请运行各个独立的测试文件")


def test_agent_manager():
    """测试 AgentManager (已迁移到 test_agent_manager.py)"""
    warnings.warn(
        "test_agent_manager() 已迁移到 test_agent_manager.py，"
        "建议使用新的模块化测试结构",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("\n=== 测试 AgentManager (兼容模式) ===")
    print("提示：此功能已迁移到 test_agent_manager.py")
    print("建议运行: python test_agent_manager.py")
    
    # 调用新的测试模块
    try:
        test_agent_manager.test_agent_manager()
    except NameError:
        print("无法调用新的测试模块，使用简化版本")
        print("请运行: python test_agent_manager.py 获得完整测试")


def test_parameter_validation():
    """测试参数验证 (已迁移到各个测试模块)"""
    warnings.warn(
        "test_parameter_validation() 已迁移到各个测试模块，"
        "建议使用新的模块化测试结构",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("\n=== 测试参数验证 (兼容模式) ===")
    print("提示：此功能已分别迁移到各个测试模块")
    print("建议运行: python test_runner.py 获得完整测试")
    
    # 调用新的测试模块
    try:
        test_content_validator.test_parameter_validation()
        test_scenario_generator.test_parameter_validation()
    except NameError:
        print("无法调用新的测试模块，请运行各个独立的测试文件")


def main():
    """主函数 - 运行所有测试 (向后兼容)"""
    print("开始 Dify Agent 系统测试 (向后兼容模式)...")
    print("\n" + "="*60)
    print("注意：此文件已重构为模块化测试结构")
    print("推荐使用: python test_runner.py 运行完整测试")
    print("="*60)
    
    # 运行兼容性测试
    try:
        test_content_validator()
        test_scenario_generator()
        test_agent_info()
        test_agent_manager()
        test_parameter_validation()
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        print("建议使用新的模块化测试结构")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("如需完整测试，请运行: python test_runner.py")
    print("="*60)


if __name__ == "__main__":
    main()