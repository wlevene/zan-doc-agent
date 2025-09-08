#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentManager 测试模块
测试Agent管理器和工厂类的功能
"""

from agents import AgentManager, AgentFactory, AgentType


def test_agent_manager():
    """测试 AgentManager"""
    print("\n=== 测试 AgentManager ===")
    
    # 初始化 AgentManager
    manager = AgentManager(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key-12345"
    )
    
    print("\n1. 获取文案验收器 Agent")
    validator = manager.getContentValidatorAgent()
    print(f"获取成功: {validator.config.name}")
    
    # 测试使用 map 参数格式
    print("\n2. 测试 map 参数格式")
    try:
        params = {
            "query": "请验收这段文案",
            "content_to_validate": "这是一段需要验收的文案。",
            "inputs": {"focus": "语法和逻辑"},
            "user": "test_user"
        }
        result = validator.process(params)
        print(f"验收结果: {result.success}")
        if not result.success:
            print(f"错误信息: {result.error_message}")
    except Exception as e:
        print(f"调用失败: {e}")
    
    print("\n3. 获取场景生成器 Agent")
    generator = manager.getScenarioGeneratorAgent()
    print(f"获取成功: {generator.config.name}")
    
    # 测试场景生成
    print("\n4. 测试场景生成")
    try:
        params = {
            "query": "为电商平台生成购物场景",
            "scenario_type": "营销场景",
            "target_audience": "年轻消费者",
            "inputs": {"product_type": "数码产品"},
            "user": "test_user"
        }
        result = generator.process(params)
        print(f"生成结果: {result.success}")
        if not result.success:
            print(f"错误信息: {result.error_message}")
    except Exception as e:
        print(f"调用失败: {e}")
    
    print("\n5. 测试单例模式")
    manager2 = AgentManager()
    print(f"单例验证: {manager is manager2}")
    
    print("\n6. 列出所有 Agent")
    agents = manager.listAgents()
    print(f"已创建的 Agent 数量: {len(agents)}")
    for agent_info in agents:
        print(f"- {agent_info['name']}: {agent_info['type']}")


def test_agent_factory():
    """测试 AgentFactory"""
    print("\n=== 测试 AgentFactory ===")
    
    factory = AgentFactory(
        endpoint="https://api.dify.ai/v1",
        app_key="test-factory-key"
    )
    
    print("\n1. 创建 ContentValidator Agent")
    try:
        validator = factory.create_agent(AgentType.CONTENT_VALIDATOR)
        print(f"创建成功: {validator.config.name}")
        print(f"Agent类型: {validator.config.agent_type.value}")
    except Exception as e:
        print(f"创建失败: {e}")
    
    print("\n2. 创建 ScenarioGenerator Agent")
    try:
        generator = factory.create_agent(AgentType.SCENARIO_GENERATOR)
        print(f"创建成功: {generator.config.name}")
        print(f"Agent类型: {generator.config.agent_type.value}")
    except Exception as e:
        print(f"创建失败: {e}")
    
    print("\n3. 测试单例模式获取")
    try:
        validator1 = factory.get_or_create_agent(AgentType.CONTENT_VALIDATOR, "validator1")
        validator2 = factory.get_or_create_agent(AgentType.CONTENT_VALIDATOR, "validator1")
        print(f"单例验证: {validator1 is validator2}")
    except Exception as e:
        print(f"单例测试失败: {e}")
    
    print("\n4. 列出工厂创建的 Agent")
    try:
        agents = factory.list_agents()
        print(f"工厂创建的 Agent 数量: {len(agents)}")
        for agent_info in agents:
            print(f"- {agent_info['name']}: {agent_info['type']}")
    except Exception as e:
        print(f"列表获取失败: {e}")
    
    print("\n5. 测试不支持的Agent类型")
    try:
        unsupported_agent = factory.create_agent(AgentType.CUSTOM)
        print(f"意外成功: {unsupported_agent}")
    except ValueError as e:
        print(f"预期错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")


def test_agent_caching():
    """测试Agent缓存机制"""
    print("\n=== 测试Agent缓存机制 ===")
    
    manager = AgentManager(
        endpoint="https://api.dify.ai/v1",
        app_key="test-cache-key"
    )
    
    print("\n1. 测试重复获取相同Agent")
    validator1 = manager.getContentValidatorAgent()
    validator2 = manager.getContentValidatorAgent()
    print(f"缓存验证: {validator1 is validator2}")
    
    generator1 = manager.getScenarioGeneratorAgent()
    generator2 = manager.getScenarioGeneratorAgent()
    print(f"缓存验证: {generator1 is generator2}")
    
    print("\n2. 清空缓存测试")
    manager.clearAgents()
    agents_after_clear = manager.listAgents()
    print(f"清空后Agent数量: {len(agents_after_clear)}")
    
    print("\n3. 清空后重新获取")
    validator3 = manager.getContentValidatorAgent()
    print(f"清空后重新获取: {validator1 is validator3}")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    print("\n1. 测试无效endpoint")
    try:
        manager = AgentManager(
            endpoint="invalid-endpoint",
            app_key="test-key"
        )
        validator = manager.getContentValidatorAgent()
        result = validator.process({"query": "测试"})
        print(f"结果: {result.success}")
        if not result.success:
            print(f"预期错误: {result.error_message}")
    except Exception as e:
        print(f"异常处理: {e}")
    
    print("\n2. 测试空app_key")
    try:
        manager = AgentManager(
            endpoint="https://api.dify.ai/v1",
            app_key=""
        )
        validator = manager.getContentValidatorAgent()
        result = validator.process({"query": "测试"})
        print(f"结果: {result.success}")
        if not result.success:
            print(f"预期错误: {result.error_message}")
    except Exception as e:
        print(f"异常处理: {e}")


def main():
    """主函数 - 运行AgentManager测试"""
    print("开始 AgentManager 测试...")
    
    # 运行所有测试
    test_agent_manager()
    test_agent_factory()
    test_agent_caching()
    test_error_handling()
    
    print("\nAgentManager 测试完成！")


if __name__ == "__main__":
    main()