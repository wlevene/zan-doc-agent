#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContentValidatorAgent 测试模块
测试文案场景验收器的功能
"""

from content_validator_agent import ContentValidatorAgent


def test_content_validator():
    """测试文案场景验收器"""
    print("\n=== 测试文案场景验收器 ===")
    
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
        
        # 流式模式测试
        print("\n--- 流式模式验收 ---")
        print("流式验收结果:")
        params = {
            "query": "1",
            "scene": "女儿藏薯片被发现",
            "persona": "这个人设是一个 养生妈妈 38 岁，你是一个非常尊重别人的人，包括家人， 养生妈妈会看重家人家人"
        }
        for chunk in validator.process_streaming(params):
            if chunk.success:
                print(chunk.content, end="", flush=True)
            else:
                print(f"\n错误: {chunk.error_message}")
        print("\n")
        
    except Exception as e:
        print(f"验收器测试出错: {e}")


def main():
    """主函数 - 运行ContentValidator测试"""
    print("开始 ContentValidatorAgent 测试...")
    
    # 运行所有测试
    test_content_validator()
    
    print("\nContentValidatorAgent 测试完成！")


if __name__ == "__main__":
    main()