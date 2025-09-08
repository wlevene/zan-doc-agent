#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
养生妈妈 Agent 测试模块
测试养生妈妈Agent的各项功能
"""

import warnings
from wellness_mom_agent import WellnessMomAgent


def test_basic_wellness_advice():
    """测试基本养生建议功能"""
    print("\n=== 测试基本养生建议 ===")
    
    try:
        # 初始化养生妈妈Agent
        agent = WellnessMomAgent(
            endpoint="http://119.45.130.88:8080/v1",
            app_key="app-kPd3U0xka6D475yOdt9YEMrO"
        )
        
        # 测试基本养生咨询
        test_params = {
            'query': '丈夫加班做PPT晚睡',
        }
        
        result = agent.process(test_params)
        print(f"养生建议生成: {result.success}")
        if result.content:
            print(f"建议内容: {result.content[:100]}...")
        
        return result.success
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False



def main():
    test_basic_wellness_advice()


if __name__ == '__main__':
    main()