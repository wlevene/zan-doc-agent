#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Agent 使用示例
演示如何使用不同类型的 Agent 进行业务场景处理
"""

from agents import (
    AgentFactory, 
    AgentType, 
    ContentValidatorAgent, 
    ScenarioGeneratorAgent
)


def demo_content_validator():
    """演示文案场景验收器的使用"""
    print("\n" + "="*50)
    print("文案场景验收器 Agent 示例")
    print("="*50)
    
    validator = ContentValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="your-content-validator-key",
        validation_criteria=[
            "语法正确性",
            "内容准确性",
            "品牌一致性",
            "合规性检查",
            "用户体验友好性"
        ]
    )
    
    # 示例文案内容
    sample_content = """
    欢迎使用我们的AI助手！我们的产品能够帮助您提高工作效率，
    让您的生活更加便捷。立即体验，享受智能科技带来的便利！
    """
    
    try:
        print("\n=== 阻塞模式验收 ===")
        result = validator.process(
            query="请对这个营销文案进行全面验收，检查是否符合标准",
            content_to_validate=sample_content,
            inputs={
                "target_audience": "企业用户",
                "brand_tone": "专业友好"
            }
        )
        
        if result.success:
            print(f"验收结果：\n{result.content}")
            print(f"\n元数据：{result.metadata}")
        else:
            print(f"验收失败：{result.error_message}")
        
        print("\n=== 流式模式验收 ===")
        print("流式验收结果：")
        for chunk in validator.process_streaming(
            query="请逐步分析这个文案的各个方面",
            content_to_validate=sample_content
        ):
            if chunk.success:
                print(chunk.content, end="", flush=True)
            else:
                print(f"\n错误：{chunk.error_message}")
                break
        
        print("\n\n=== 批量验收示例 ===")
        batch_contents = [
            "产品A：高效便捷的办公助手",
            "产品B：让工作变得更简单！",
            "产品C：专业级AI解决方案，值得信赖"
        ]
        
        batch_results = validator.validate_batch(
            contents=batch_contents,
            criteria="检查文案的专业性和吸引力"
        )
        
        for i, result in enumerate(batch_results):
            print(f"\n文案{i+1}验收结果：")
            if result.success:
                print(result.content[:200] + "..." if len(result.content) > 200 else result.content)
            else:
                print(f"验收失败：{result.error_message}")
                
    except Exception as e:
        print(f"示例运行出错：{e}")


def demo_scenario_generator():
    """演示场景生成器的使用"""
    print("\n" + "="*50)
    print("场景生成器 Agent 示例")
    print("="*50)
    
    generator = ScenarioGeneratorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="your-scenario-generator-key",
        scenario_types=[
            "营销场景",
            "用户故事",
            "产品演示",
            "客户服务场景",
            "培训场景"
        ]
    )
    
    try:
        print("\n=== 营销场景生成 ===")
        result = generator.process(
            query="为AI办公助手产品生成一个营销场景",
            scenario_type="营销场景",
            target_audience="中小企业主",
            inputs={
                "product_features": ["智能文档处理", "自动化工作流", "数据分析"],
                "pain_points": ["工作效率低", "重复性任务多", "数据处理复杂"]
            }
        )
        
        if result.success:
            print(f"生成的营销场景：\n{result.content}")
        else:
            print(f"生成失败：{result.error_message}")
        
        print("\n=== 用户故事生成 ===")
        result = generator.process(
            query="生成一个关于用户使用AI助手解决工作问题的故事",
            scenario_type="用户故事",
            target_audience="职场新人"
        )
        
        if result.success:
            print(f"生成的用户故事：\n{result.content}")
        else:
            print(f"生成失败：{result.error_message}")
        
        print("\n=== 流式场景生成 ===")
        print("流式生成产品演示场景：")
        for chunk in generator.process_streaming(
            query="创建一个产品演示场景，展示AI助手的核心功能",
            scenario_type="产品演示",
            target_audience="潜在客户"
        ):
            if chunk.success:
                print(chunk.content, end="", flush=True)
            else:
                print(f"\n错误：{chunk.error_message}")
                break
        
        print("\n\n=== 多场景变体生成 ===")
        scenarios = generator.generate_multiple_scenarios(
            base_query="为在线教育平台生成客户服务场景",
            count=3,
            scenario_type="客户服务场景"
        )
        
        for i, scenario in enumerate(scenarios):
            print(f"\n场景变体{i+1}：")
            if scenario.success:
                print(scenario.content[:300] + "..." if len(scenario.content) > 300 else scenario.content)
            else:
                print(f"生成失败：{scenario.error_message}")
                
    except Exception as e:
        print(f"示例运行出错：{e}")


def demo_agent_factory():
    """演示 Agent 工厂的使用"""
    print("\n" + "="*50)
    print("Agent 工厂使用示例")
    print("="*50)
    
    # 初始化工厂
    factory = AgentFactory(
        endpoint="https://api.dify.ai/v1",
        app_key="your-factory-key"
    )
    
    try:
        print("\n=== 创建不同类型的 Agent ===")
        
        # 创建文案验收器
        validator = factory.create_agent(
            AgentType.CONTENT_VALIDATOR,
            validation_criteria=["专业性", "可读性", "准确性"]
        )
        print(f"创建的验收器：{validator.get_info()}")
        
        # 创建场景生成器
        generator = factory.create_agent(
            AgentType.SCENARIO_GENERATOR,
            scenario_types=["营销", "培训", "演示"]
        )
        print(f"创建的生成器：{generator.get_info()}")
        
        print("\n=== 使用单例模式获取 Agent ===")
        
        # 获取或创建 Agent（单例）
        validator1 = factory.get_or_create_agent(
            AgentType.CONTENT_VALIDATOR, 
            "default_validator"
        )
        validator2 = factory.get_or_create_agent(
            AgentType.CONTENT_VALIDATOR, 
            "default_validator"
        )
        
        print(f"两个验收器是否为同一实例：{validator1 is validator2}")
        
        print("\n=== 列出所有 Agent ===")
        agents = factory.list_agents()
        for i, agent_info in enumerate(agents):
            print(f"Agent {i+1}: {agent_info}")
        
        print("\n=== 使用工厂创建的 Agent 进行处理 ===")
        
        # 使用验收器
        result = validator1.process(
            query="验收这个标题的有效性",
            content_to_validate="AI革命：改变未来工作方式的智能助手"
        )
        
        if result.success:
            print(f"验收结果摘要：{result.content[:100]}...")
        else:
            print(f"验收失败：{result.error_message}")
        
        # 使用生成器
        result = generator.process(
            query="生成一个AI产品发布会的演示场景",
            scenario_type="演示"
        )
        
        if result.success:
            print(f"生成场景摘要：{result.content[:100]}...")
        else:
            print(f"生成失败：{result.error_message}")
            
    except Exception as e:
        print(f"示例运行出错：{e}")


def demo_custom_agent():
    """演示如何扩展自定义 Agent"""
    print("\n" + "="*50)
    print("自定义 Agent 扩展示例")
    print("="*50)
    
    from agents import BaseAgent, AgentConfig, AgentResponse
    
    class TranslationAgent(BaseAgent):
        """翻译 Agent 示例"""
        
        def __init__(self, endpoint, app_key, supported_languages=None):
            self.supported_languages = supported_languages or ["英语", "中文", "日语", "韩语"]
            
            config = AgentConfig(
                name="翻译助手",
                description="多语言翻译工具",
                agent_type=AgentType.CUSTOM,
                default_inputs={
                    "supported_languages": self.supported_languages,
                    "translation_style": "professional"
                },
                system_prompt="你是一个专业的翻译助手，请提供准确、流畅的翻译。"
            )
            
            from dify_client import DifyClient
            dify_client = DifyClient(api_key=app_key, base_url=endpoint)
            super().__init__(dify_client, config)
        
        def process(self, query, inputs=None, source_lang=None, target_lang=None, **kwargs):
            try:
                final_inputs = self._prepare_inputs(inputs)
                
                if source_lang:
                    final_inputs["source_language"] = source_lang
                if target_lang:
                    final_inputs["target_language"] = target_lang
                
                full_query = self._build_translation_query(query, source_lang, target_lang)
                
                raw_response = self.client.completion_messages_blocking(
                    query=full_query,
                    inputs=final_inputs,
                    user=kwargs.get('user', 'translator')
                )
                
                return self._handle_response(raw_response)
                
            except Exception as e:
                return AgentResponse(
                    success=False,
                    content="",
                    error_message=f"翻译失败: {str(e)}"
                )
        
        def process_streaming(self, query, inputs=None, **kwargs):
            # 简化的流式实现
            try:
                for chunk in self.client.completion_messages_streaming(
                    query=self._build_query(query),
                    inputs=self._prepare_inputs(inputs),
                    user=kwargs.get('user', 'translator')
                ):
                    yield self._handle_response(chunk)
            except Exception as e:
                yield AgentResponse(
                    success=False,
                    content="",
                    error_message=f"翻译失败: {str(e)}"
                )
        
        def _build_translation_query(self, query, source_lang, target_lang):
            base_query = self._build_query(query)
            
            if source_lang and target_lang:
                return f"{base_query}\n\n请将以下内容从{source_lang}翻译为{target_lang}："
            
            return base_query
    
    # 使用自定义 Agent
    try:
        translator = TranslationAgent(
            endpoint="https://api.dify.ai/v1",
            app_key="your-translation-key"
        )
        
        print(f"\n自定义翻译 Agent 信息：{translator.get_info()}")
        
        result = translator.process(
            query="Hello, how are you today?",
            source_lang="英语",
            target_lang="中文"
        )
        
        if result.success:
            print(f"翻译结果：{result.content}")
        else:
            print(f"翻译失败：{result.error_message}")
            
    except Exception as e:
        print(f"自定义 Agent 示例出错：{e}")


def main():
    """主函数，运行所有示例"""
    print("Dify Agent 系统使用示例")
    print("="*60)
    print("⚠️  请先将API密钥替换为真实密钥后再运行示例")
    
    try:
        # 运行各种示例
        demo_content_validator()
        demo_scenario_generator()
        demo_agent_factory()
        demo_custom_agent()
        
        print("\n" + "="*60)
        print("所有示例运行完成！")
        print("\n💡 扩展建议：")
        print("1. 根据业务需求创建更多专用 Agent")
        print("2. 实现 Agent 之间的协作机制")
        print("3. 添加配置文件支持")
        print("4. 实现 Agent 性能监控")
        print("5. 添加缓存机制提高效率")
        
    except KeyboardInterrupt:
        print("\n用户中断了示例运行")
    except Exception as e:
        print(f"\n示例运行出现错误：{e}")


if __name__ == "__main__":
    main()