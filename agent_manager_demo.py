#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentManager 使用示例
演示如何使用封装后的 AgentManager 来获取和使用 Agent
"""

from agents import AgentManager

def demo_agent_manager():
    """演示 AgentManager 的基本使用"""
    print("=== AgentManager 使用示例 ===")
    
    # 初始化 AgentManager（单例模式）
    manager = AgentManager(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key-12345"
    )
    
    print("\n1. 获取文案验收器 Agent")
    validator = manager.getContentValidatorAgent(
        validation_criteria=["语法检查", "内容准确性", "风格一致性"]
    )
    
    # 使用 map 参数格式调用 process
    validation_params = {
        "query": "请验收以下文案的质量",
        "content_to_validate": "这是一段需要验收的文案内容。",
        "inputs": {
            "validation_focus": "语法和逻辑"
        },
        "user": "demo_user"
    }
    
    try:
        result = validator.process(validation_params)
        print(f"验收结果: {result.success}")
        if not result.success:
            print(f"错误信息: {result.error_message}")
    except Exception as e:
        print(f"调用失败: {e}")
    
    print("\n2. 获取场景生成器 Agent")
    generator = manager.getScenarioGeneratorAgent(
        scenario_types=["营销场景", "用户故事", "产品演示"]
    )
    
    # 使用 map 参数格式调用 process
    generation_params = {
        "query": "为电商平台生成一个购物场景",
        "scenario_type": "营销场景",
        "target_audience": "年轻消费者",
        "inputs": {
            "product_category": "数码产品",
            "season": "双十一"
        },
        "user": "demo_user"
    }
    
    try:
        result = generator.process(generation_params)
        print(f"生成结果: {result.success}")
        if not result.success:
            print(f"错误信息: {result.error_message}")
    except Exception as e:
        print(f"调用失败: {e}")
    
    print("\n3. 流式处理示例")
    streaming_params = {
        "query": "生成一个详细的用户购买流程场景",
        "scenario_type": "用户故事",
        "inputs": {
            "detail_level": "high"
        }
    }
    
    try:
        print("开始流式生成...")
        for chunk in generator.process_streaming(streaming_params):
            if chunk.success:
                print(f"流式内容: {chunk.content[:50]}...")
            else:
                print(f"流式错误: {chunk.error_message}")
                break
    except Exception as e:
        print(f"流式调用失败: {e}")
    
    print("\n4. 管理器信息")
    agents_info = manager.listAgents()
    print(f"已创建的 Agent 数量: {len(agents_info)}")
    for info in agents_info:
        print(f"- {info['name']}: {info['type']}")

def demo_singleton_pattern():
    """演示单例模式"""
    print("\n=== 单例模式验证 ===")
    
    # 第一次创建
    manager1 = AgentManager(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key-12345"
    )
    
    # 第二次创建（应该返回同一个实例）
    manager2 = AgentManager()
    
    print(f"manager1 和 manager2 是同一个实例: {manager1 is manager2}")
    print(f"manager1 endpoint: {manager1.endpoint}")
    print(f"manager2 endpoint: {manager2.endpoint}")

def demo_parameter_validation():
    """演示参数验证"""
    print("\n=== 参数验证示例 ===")
    
    manager = AgentManager()
    validator = manager.getContentValidatorAgent()
    
    # 测试缺少必需参数
    print("1. 测试缺少 query 参数")
    try:
        result = validator.process({"inputs": {"test": "value"}})
        print(f"结果: {result.success}")
    except ValueError as e:
        print(f"参数验证错误: {e}")
    
    # 测试正确的参数
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
    """主函数"""
    print("AgentManager 封装演示")
    print("=" * 50)
    
    demo_agent_manager()
    demo_singleton_pattern()
    demo_parameter_validation()
    
    print("\n=== 使用说明 ===")
    print("1. 使用 AgentManager 单例模式管理 Agent 实例")
    print("2. 通过 getXXAgent() 方法获取特定类型的 Agent")
    print("3. 使用 map 格式传递参数给 process() 方法")
    print("4. 参数字典必须包含 'query' 字段")
    print("5. 其他参数如 inputs、user 等都是可选的")
    print("6. 支持流式处理和批量处理")

if __name__ == "__main__":
    main()