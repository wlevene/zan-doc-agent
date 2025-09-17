#!/usr/bin/env python3
"""
测试严格验收标准下的文案重写功能
通过临时修改验收标准来强制触发重写
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from workflow.wellnessmom.wellness_workflow import WellnessWorkflow
from agents.agents import AgentConfig, AgentType

def test_strict_validation():
    """测试严格验收下的重写功能"""
    
    # 创建一个临时的严格验收配置
    persona_detail = """
    你是一个非常严格的养生妈妈，45岁，对文案要求极高。
    文案必须包含具体的养生建议、时间安排和详细的操作步骤。
    """
    
    config = AgentConfig(
        name="strict_validation_test",
        description="严格验收测试",
        agent_type=AgentType.CUSTOM
    )
    
    workflow = WellnessWorkflow(config, persona_detail)
    
    # 使用一个简单的输入，容易被严格验收拒绝
    test_input = "累了"
    
    print("🔍 开始严格验收测试...")
    print(f"📝 测试输入: {test_input}")
    print(f"👤 严格人设: {persona_detail.strip()}")
    print("=" * 60)
    
    # 创建严格的验收标准，通过修改工作流中的验收逻辑
    print("📋 设置严格验收标准...")
    
    # 保存原始的验收方法
    original_validate_content = workflow._validate_content
    
    def strict_validate_content(content, persona):
        """严格的文案验收函数"""
        strict_query = f"""
        你是一个极其严格的养生内容验收专家。请验收以下文案是否符合要求：

        验收标准（必须全部满足）：
        1. 文案长度必须超过100字
        2. 必须包含至少3个具体的养生建议
        3. 必须包含具体的时间安排（如"每天30分钟"）
        4. 必须包含详细的操作步骤
        5. 必须使用专业的养生术语
        6. 必须包含科学依据或原理说明

        如果不满足任何一个标准，请返回：
        验收结果: 不通过
        验收原因: [具体说明哪些标准未满足]

        如果全部满足，请返回：
        验收结果: 通过
        验收原因: 文案符合所有验收标准

        待验收文案：{content}
        人设要求：{persona}
        """
        
        # 调用原始验收器，但使用严格的查询
        params = {
            'query': strict_query,
            'content_to_validate': content,
            'persona': persona
        }
        return workflow.content_validator.process(params)
    
    # 临时替换验收方法
    workflow._validate_content = strict_validate_content
    
    try:
        result = workflow.run_complete_workflow(test_input)
        
        if result.success:
            print("\n✅ 严格验收测试完成!")
            print(f"📊 生成文案数量: {result.data.get('content_count', 0)}")
            
            # 导出Excel查看结果
            excel_file = workflow.export_content_to_excel("strict_validation_test.xlsx")
            if excel_file:
                print(f"📋 测试结果已导出到: {excel_file}")
                
                # 检查重写情况
                import pandas as pd
                df = pd.read_excel(excel_file)
                rewrite_count = len(df[df['是否重写'] == '是'])
                failed_validation = len(df[df['文案验收结果'] == '不通过'])
                
                print(f"❌ 验收失败数量: {failed_validation}")
                print(f"🔄 重写文案数量: {rewrite_count}")
                
                if rewrite_count > 0:
                    print("\n🎉 文案重写功能正常工作!")
                    print("\n重写文案详情:")
                    rewrite_rows = df[df['是否重写'] == '是']
                    for idx, row in rewrite_rows.iterrows():
                        print(f"  📝 原始文案: {row['原始文案'][:80]}...")
                        print(f"  ✏️  重写文案: {row['文案内容'][:80]}...")
                        print(f"  💡 重写原因: {row['重写原因']}")
                        print(f"  ✅ 验收结果: {row['文案验收结果']}")
                        print("-" * 40)
                else:
                    print("⚠️  没有触发重写，可能是:")
                    print("  1. 验收都通过了")
                    print("  2. 重写功能有问题")
                    
                    # 显示验收失败的情况
                    if failed_validation > 0:
                        print(f"\n❌ 有 {failed_validation} 个文案验收失败但没有重写:")
                        failed_rows = df[df['文案验收结果'] == '不通过']
                        for idx, row in failed_rows.iterrows():
                            print(f"  📝 文案: {row['文案内容'][:50]}...")
                            print(f"  ❌ 失败原因: {row['文案验收原因']}")
                            print(f"  🔄 是否重写: {row['是否重写']}")
                            print("-" * 30)
            else:
                print("❌ Excel导出失败")
        else:
            print(f"❌ 测试失败: {result.error}")
            
    finally:
        # 恢复原始验收方法
        workflow._validate_content = original_validate_content

if __name__ == "__main__":
    test_strict_validation()