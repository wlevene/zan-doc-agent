#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景验收器 Agent 测试文件
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from agents.scenario_validator.scenario_validator_agent import ScenarioValidatorAgent


def test_scenario_validator():
    """测试场景验收器功能"""
    print("\n=== 场景验收器测试 ===")
    
    # 创建验收器实例
    validator = ScenarioValidatorAgent(
        endpoint="http://119.45.130.88:8080/v1",
        app_key="app-PeReRRrb0s3Yr23eIr7BIPL6"
    )
    
    print(f"验收器信息: {validator.get_info()}")
    
    # 测试1: 阻塞模式验收
    print("\n--- 测试阻塞模式验收 ---")
    test_params = {
        'query': '请验收这个场景设计是否合理',
        'scenario_to_validate': '''
        场景名称：智能家居控制场景
        场景描述：
        用户回到家中，通过语音助手说"我回来了"，系统自动执行以下操作：
        1. 打开客厅和卧室的灯光，调节到舒适亮度
        2. 启动空调，设置温度为26度
        3. 播放用户喜欢的音乐
        4. 显示今日天气和重要提醒
        5. 如果是晚餐时间，推荐附近餐厅或菜谱
        
        触发条件：用户语音指令"我回来了"
        执行时间：2-3秒内完成所有操作
        适用用户：智能家居用户
        ''',
        'inputs': {
            'validation_criteria': '完整性、可行性、用户体验、技术实现难度'
        }
    }
    
    try:
        response = validator.process(test_params)
        if response.success:
            print(f"验收成功: {response.content[:200]}...")
            print(f"元数据: {response.metadata}")
        else:
            print(f"验收失败: {response.error_message}")
    except Exception as e:
        print(f"阻塞模式测试异常: {e}")
    
    # 测试2: 流式模式验收
    print("\n--- 测试流式模式验收 ---")
    try:
        response_count = 0
        for response in validator.process_streaming(test_params):
            response_count += 1
            if response.success:
                print(f"流式响应 {response_count}: {response.content[:100]}...")
            else:
                print(f"流式响应错误: {response.error_message}")
            
            # 限制输出数量
            if response_count >= 3:
                print("...（省略更多流式响应）")
                break
        
        print(f"流式模式验收成功，共收到 {response_count} 个响应")
    except Exception as e:
        print(f"流式模式测试异常: {e}")


def test_scenario_validator_edge_cases():
    """测试边界情况"""
    print("\n=== 边界情况测试 ===")
    
    validator = ScenarioValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key"
    )
    
    # 测试1: 空查询
    print("\n--- 测试空查询 ---")
    try:
        response = validator.process({'query': ''})
        print(f"空查询结果: 成功={response.success}, 内容长度={len(response.content)}")
    except Exception as e:
        print(f"空查询测试异常: {e}")
    
    # 测试2: 只有基本查询
    print("\n--- 测试基本查询 ---")
    try:
        response = validator.process({'query': '验收这个场景'})
        if response.success:
            print(f"基本查询成功: {response.content[:100]}...")
        else:
            print(f"基本查询失败: {response.error_message}")
    except Exception as e:
        print(f"基本查询测试异常: {e}")
    
    # 测试3: 复杂验收场景
    print("\n--- 测试复杂验收场景 ---")
    complex_params = {
        'query': '请从多个维度验收这个电商场景',
        'scenario_to_validate': '''
        场景名称：个性化购物推荐场景
        场景描述：
        当用户浏览商品超过30秒但未加入购物车时，系统分析用户行为：
        1. 记录用户浏览时长、点击位置、滚动行为
        2. 结合用户历史购买记录和偏好
        3. 实时推荐3-5个相关商品
        4. 以非侵入式弹窗展示推荐
        5. 提供"不再提醒"选项
        
        触发条件：浏览时长>30秒且未操作
        目标用户：电商平台用户
        预期效果：提升转化率15%
        ''',
        'inputs': {
            'validation_criteria': '用户体验、技术可行性、商业价值、隐私保护',
            'business_context': '电商平台个性化推荐系统',
            'target_metrics': '转化率提升、用户满意度'
        }
    }
    
    try:
        response = validator.process(complex_params)
        if response.success:
            print(f"复杂验收成功: {response.content[:150]}...")
        else:
            print(f"复杂验收失败: {response.error_message}")
    except Exception as e:
        print(f"复杂验收测试异常: {e}")
    
    # 测试4: 批量验收
    print("\n--- 测试批量验收 ---")
    scenarios = [
        "场景A：用户登录后自动同步数据",
        "场景B：支付失败时的重试机制",
        "场景C：新用户引导流程设计"
    ]
    
    try:
        batch_results = validator.validate_batch(
            scenarios=scenarios,
            criteria="请验收场景的完整性和可行性"
        )
        
        for i, result in enumerate(batch_results):
            if result.success:
                print(f"批量验收 {i+1} 成功: {result.content[:80]}...")
            else:
                print(f"批量验收 {i+1} 失败: {result.error_message}")
        
        print(f"批量验收完成，共处理 {len(batch_results)} 个场景")
    except Exception as e:
        print(f"批量验收测试异常: {e}")


def test_scenario_validator_specific_cases():
    """测试特定场景验收"""
    print("\n=== 特定场景验收测试 ===")
    
    validator = ScenarioValidatorAgent(
        endpoint="https://api.dify.ai/v1",
        app_key="test-key"
    )
    
    # 测试1: 移动应用场景
    print("\n--- 测试移动应用场景验收 ---")
    mobile_params = {
        'query': '验收移动应用的用户体验场景',
        'scenario_to_validate': '''
        场景：移动端一键分享功能
        用户操作：长按图片 -> 选择分享 -> 选择平台 -> 添加文字 -> 发送
        设计要求：
        - 长按响应时间<200ms
        - 分享选项不超过6个
        - 支持自定义文字编辑
        - 分享成功有明确反馈
        '''
    }
    
    try:
        response = validator.process(mobile_params)
        if response.success:
            print(f"移动场景验收: {response.content[:120]}...")
        else:
            print(f"移动场景验收失败: {response.error_message}")
    except Exception as e:
        print(f"移动场景测试异常: {e}")
    
    # 测试2: 异常处理场景
    print("\n--- 测试异常处理场景验收 ---")
    error_params = {
        'query': '验收系统异常处理场景的完整性',
        'scenario_to_validate': '''
        场景：网络异常处理
        异常情况：用户操作时网络中断
        处理流程：
        1. 检测网络状态变化
        2. 显示网络异常提示
        3. 保存用户当前操作状态
        4. 提供重试和离线模式选项
        5. 网络恢复后自动同步数据
        '''
    }
    
    try:
        response = validator.process(error_params)
        if response.success:
            print(f"异常处理验收: {response.content[:120]}...")
        else:
            print(f"异常处理验收失败: {response.error_message}")
    except Exception as e:
        print(f"异常处理测试异常: {e}")


def main():
    """主测试函数"""
    print("开始场景验收器测试...")
    
    try:
        test_scenario_validator()
        test_scenario_validator_edge_cases()
        test_scenario_validator_specific_cases()
        print("\n✅ 所有测试完成")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()