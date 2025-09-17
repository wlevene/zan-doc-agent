#!/usr/bin/env python3
"""
测试文案重写大师功能的脚本
通过模拟文案验收失败来触发重写机制
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from workflow.wellnessmom.wellness_workflow import WellnessWorkflow
from agents.agents import AgentConfig, AgentType

def test_rewrite_functionality():
    """测试文案重写功能"""
    
    # 使用简化的人设，更容易触发验收失败
    persona_detail = """
    你是一个养生妈妈，45岁，关注家人健康。
    """
    
    config = AgentConfig(
        name="test_rewrite_workflow",
        description="测试文案重写功能",
        agent_type=AgentType.CUSTOM
    )
    
    workflow = WellnessWorkflow(config, persona_detail)
    
    # 使用一个简单的输入来测试
    test_input = "测试重写功能"
    
    print("🧪 开始测试文案重写功能...")
    print(f"📝 测试输入: {test_input}")
    print(f"👤 人设: {persona_detail.strip()}")
    print("=" * 50)
    
    result = workflow.run_complete_workflow(test_input)
    
    if result.success:
        print("\n✅ 测试完成!")
        print(f"📊 生成文案数量: {result.data.get('content_count', 0)}")
        
        # 导出Excel查看结果
        excel_file = workflow.export_content_to_excel("test_rewrite_result.xlsx")
        if excel_file:
            print(f"📋 测试结果已导出到: {excel_file}")
            
            # 检查是否有重写的文案
            import pandas as pd
            df = pd.read_excel(excel_file)
            rewrite_count = len(df[df['是否重写'] == '是'])
            print(f"🔄 重写文案数量: {rewrite_count}")
            
            if rewrite_count > 0:
                print("🎉 文案重写功能正常工作!")
                print("\n重写文案详情:")
                rewrite_rows = df[df['是否重写'] == '是']
                for idx, row in rewrite_rows.iterrows():
                    print(f"  - 原始文案: {row['原始文案'][:50]}...")
                    print(f"  - 重写文案: {row['文案内容'][:50]}...")
                    print(f"  - 重写原因: {row['重写原因']}")
                    print()
            else:
                print("ℹ️  本次测试没有触发文案重写（所有文案都通过了验收）")
        else:
            print("❌ Excel导出失败")
    else:
        print(f"❌ 测试失败: {result.error}")

if __name__ == "__main__":
    test_rewrite_functionality()