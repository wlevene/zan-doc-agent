#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Agent 系统测试
测试文案场景验收器和场景生成器的功能
"""

from agents import ContentValidatorAgent, ScenarioGeneratorAgent, AgentConfig, AgentManager


def test_content_validator():
    """测试文案场景验收器"""
    print("\n=== 测试文案场景验收器 ===")
    
    # 初始化验收器Agent（带dify_params测试）
    dify_params = {
        "query":"xx",
        "scene":"xxx",
        "persona":"zxxx"

    }

    validator = ContentValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="app-your-content-validator-key",  # 请替换为实际的app_key
        dify_params=dify_params
    )
    
    try:
        # 阻塞模式测试
        print("\n--- 阻塞模式验收 ---")
        params = {
            "query": "请对以下文案进行全面验收，检查语法、内容准确性、风格一致性和合规性",
            "content_to_validate": "这是一段测试文案内容",
            "user": "test_user"
        }
        result = validator.process(params)
        print(f"验收成功: {result.success}")
        if result.success:
            print(f"验收结果: {result.content}")
        else:
            print(f"验收失败: {result.error_message}")
        
        # 流式模式测试
        print("\n--- 流式模式验收 ---")
        print("流式验收结果:")
        params = {
            "query": "请对以下文案进行全面验收",
            "content_to_validate": "这是一段测试文案内容",
            "user": "test_user"
        }
        for chunk in validator.process_streaming(params):
            if chunk.success:
                print(chunk.content, end="", flush=True)
            else:
                print(f"\n错误: {chunk.error_message}")
        print("\n")
        
    except Exception as e:
        print(f"验收器测试出错: {e}")


def test_scenario_generator():
    """测试场景生成器"""
    print("\n=== 测试场景生成器 ===")
    
    # 初始化生成器Agent（带dify_params测试）
    dify_params = {
        "temperature": 0.8,
        "max_tokens": 2000
    }
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="app-your-scenario-generator-key",  # 请替换为实际的app_key
        dify_params=dify_params
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
    print("\n=== Agent 信息测试 ===")
    
    # 创建Agent实例
    validator = ContentValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="app-validator-key"
    )
    
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="app-generator-key"
    )
    
    # 打印Agent信息
    print(f"验收器类型: {validator.config.agent_type.value}")
    print(f"验收器名称: {validator.config.name}")
    print(f"验收器描述: {validator.config.description}")
    print(f"生成器类型: {generator.config.agent_type.value}")
    print(f"生成器名称: {generator.config.name}")
    print(f"生成器描述: {generator.config.description}")


def test_agent_manager():
    """测试 AgentManager"""
    print("\n=== 测试 AgentManager ===")
    
    # 初始化 AgentManager
    manager = AgentManager(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key-12345"
    )
    
    print("\n1. 获取文案验收器 Agent")
    validator = manager.getContentValidatorAgent(
        validation_criteria=["语法检查", "内容准确性"],
        dify_params={"temperature": 0.7, "max_tokens": 1000}
    )
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
    generator = manager.getScenarioGeneratorAgent(
        scenario_types=["营销场景", "用户故事"],
        dify_params={"temperature": 0.8, "max_tokens": 1500}
    )
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


def test_parameter_validation():
    """测试参数验证"""
    print("\n=== 测试参数验证 ===")
    
    manager = AgentManager()
    validator = manager.getContentValidatorAgent()
    
    print("\n1. 测试缺少必需参数")
    try:
        result = validator.process({"inputs": {"test": "value"}})
        print(f"结果: {result.success}")
    except ValueError as e:
        print(f"参数验证错误（预期）: {e}")
    
    print("\n2. 测试正确的参数")
    try:
        result = validator.process({
            "query": "测试查询",
            "inputs": {"test": "value"}
        })
        print(f"结果: {result.success}")
        if not result.success:
            print(f"API错误（预期）: {result.error_message}")
    except Exception as e:
        print(f"其他错误: {e}")


def main():
    """主函数 - 运行所有测试"""
    print("开始 Dify Agent 系统测试...")
    
    # 测试Agent信息
    test_agent_info()
    
    # 测试文案场景验收器
    test_content_validator()
    
    # 测试场景生成器
    test_scenario_generator()
    
    # 测试 AgentManager
    test_agent_manager()
    
    # 测试参数验证
    test_parameter_validation()
    
    print("\n=== 测试完成 ===")
    print("\n注意事项:")
    print("1. 请确保已正确配置 endpoint 和 app_key")
    print("2. 如果出现API错误，请检查网络连接和API配置")
    print("3. 实际使用时请替换为真实的app_key")
    print("\n=== 新功能说明 ===")
    print("1. 使用 AgentManager 单例模式管理 Agent")
    print("2. 通过 getXXAgent() 方法获取 Agent 实例")
    print("3. process() 方法现在使用 map 参数格式")
    print("4. 参数字典必须包含 'query' 字段")
    print("5. 支持参数验证和错误处理")


if __name__ == "__main__":
    main()