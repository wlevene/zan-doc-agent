#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Params 参数传递演示
演示如何使用 dify_params 向 Dify API 传递额外参数
"""

from agents import ContentValidatorAgent, ScenarioGeneratorAgent, AgentFactory, AgentType


def demo_dify_params_usage():
    """演示 dify_params 参数的使用"""
    print("\n" + "="*60)
    print("Dify Params 参数传递演示")
    print("="*60)
    
    # 示例1：直接创建Agent时使用dify_params
    print("\n=== 示例1：直接创建Agent时传递dify_params ===")
    
    # 为验收器设置较低的temperature确保结果稳定
    validator_params = {
        "temperature": 0.2,
        "max_tokens": 1000,
        "response_format": "json"
    }
    
    validator = ContentValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="your-validator-key",
        validation_criteria=["准确性", "专业性"],
        dify_params=validator_params
    )
    
    print(f"验收器的dify_params: {validator.dify_params}")
    
    # 为生成器设置较高的temperature增加创意性
    generator_params = {
        "temperature": 0.9,
        "max_tokens": 2000,
        "top_p": 0.95,
        "frequency_penalty": 0.1
    }
    
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="your-generator-key",
        scenario_types=["营销", "创意"],
        dify_params=generator_params
    )
    
    print(f"生成器的dify_params: {generator.dify_params}")
    
    # 示例2：通过AgentFactory使用dify_params
    print("\n=== 示例2：通过AgentFactory传递dify_params ===")
    
    factory = AgentFactory(
        endpoint="https://api.dify.ai/v1",
        app_key="your-factory-key"
    )
    
    # 创建带有特定dify_params的验收器
    strict_validator_params = {
        "temperature": 0.1,  # 非常低的温度，确保严格验收
        "max_tokens": 800,
        "presence_penalty": 0.2
    }
    
    strict_validator = factory.create_agent(
        AgentType.CONTENT_VALIDATOR,
        validation_criteria=["严格语法检查", "合规性"],
        dify_params=strict_validator_params
    )
    
    print(f"严格验收器的dify_params: {strict_validator.dify_params}")
    
    # 创建带有特定dify_params的生成器
    creative_generator_params = {
        "temperature": 1.0,  # 最高创意性
        "max_tokens": 3000,
        "top_p": 1.0,
        "frequency_penalty": 0.0
    }
    
    creative_generator = factory.create_agent(
        AgentType.SCENARIO_GENERATOR,
        scenario_types=["创意营销", "故事创作"],
        dify_params=creative_generator_params
    )
    
    print(f"创意生成器的dify_params: {creative_generator.dify_params}")
    
    # 示例3：演示参数如何影响API调用
    print("\n=== 示例3：参数传递机制说明 ===")
    print("当调用Agent的process方法时，dify_params会被合并到inputs中：")
    print("1. 首先准备基础inputs参数")
    print("2. 然后将dify_params合并到inputs中")
    print("3. 最终传递给DifyClient的completion_messages方法")
    print("\n这样可以确保Dify API接收到所有必要的参数，包括：")
    print("- temperature: 控制输出的随机性")
    print("- max_tokens: 限制输出长度")
    print("- top_p: 核采样参数")
    print("- frequency_penalty: 频率惩罚")
    print("- presence_penalty: 存在惩罚")
    print("- response_format: 响应格式")
    
    # 示例4：不同场景的推荐参数
    print("\n=== 示例4：不同场景的推荐dify_params ===")
    
    scenarios = {
        "严格验收": {
            "temperature": 0.1,
            "max_tokens": 1000,
            "description": "低温度确保结果稳定和准确"
        },
        "创意生成": {
            "temperature": 0.9,
            "max_tokens": 2500,
            "top_p": 0.95,
            "description": "高温度和top_p增加创意性"
        },
        "技术文档": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "presence_penalty": 0.1,
            "description": "中低温度确保技术准确性"
        },
        "营销文案": {
            "temperature": 0.7,
            "max_tokens": 1500,
            "frequency_penalty": 0.2,
            "description": "平衡创意性和可读性"
        }
    }
    
    for scenario_name, params in scenarios.items():
        description = params.pop("description")
        print(f"\n{scenario_name}: {description}")
        print(f"  推荐参数: {params}")


def main():
    """主函数"""
    try:
        demo_dify_params_usage()
        
        print("\n" + "="*60)
        print("✅ Dify Params 演示完成！")
        print("\n💡 使用提示：")
        print("1. 根据不同的业务场景选择合适的参数")
        print("2. temperature控制输出的随机性和创意性")
        print("3. max_tokens限制输出长度，避免过长响应")
        print("4. 可以组合多个参数达到最佳效果")
        print("5. 建议先用小参数测试，再逐步调优")
        
    except Exception as e:
        print(f"演示运行出错: {e}")


if __name__ == "__main__":
    main()