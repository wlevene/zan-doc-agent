#!/usr/bin/env python3
"""
测试强制重写功能的简化脚本
"""

import sys
import os
from pathlib import Path
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from workflow.wellnessmom.wellness_workflow import WellnessWorkflow
from agents.agents import AgentConfig, AgentType

def test_force_rewrite():
    """测试强制重写功能"""
    
    # 简化的人设
    persona_detail = """- 你是一个养生妈妈，40岁，关注全家健康
- 有一个儿子，14岁，易过敏
- 有一个女儿，10岁，挑食易上火
- 特别注重养生，有中医基础"""
    
    # 创建工作流配置
    config = AgentConfig(
        name="test_wellness_workflow",
        description="测试养生妈妈工作流配置",
        agent_type=AgentType.CUSTOM
    )
    
    # 创建工作流实例
    workflow = WellnessWorkflow(config, persona_detail)
    
    # 手动设置少量场景进行测试
    test_scenarios = [
        "儿子熬夜打游戏眼睛发红",
        "女儿挑食只吃炸鸡薯条"
    ]
    
    print("开始测试强制重写功能...")
    print(f"测试场景数量: {len(test_scenarios)}")
    
    # 手动处理每个场景
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*50}")
        print(f"处理场景 {i+1}/{len(test_scenarios)}: {scenario}")
        print(f"{'='*50}")
        
        # 生成文案
        content_result = workflow.content_generator.process({
            "persona": persona_detail,
            "scenario": scenario
        })
        
        if content_result.success:
            print(f"✅ 文案生成成功: {content_result.content}")
            
            # 验证文案
            content_validation = workflow.content_validator.process({
                "persona": persona_detail,
                "scenario": scenario,
                "content": content_result.content
            })
            
            if content_validation.success:
                validation_json = json.loads(content_validation.content.replace("```json", "").replace("```", ""))
                validation_passed = validation_json.get("result", False)
                validation_reason = validation_json.get("reason", "")
                
                print(f"📋 文案验证结果: {'通过' if validation_passed else '未通过'}")
                print(f"📋 验证原因: {validation_reason}")
                
                if validation_passed:
                    # 强制重写处理
                    print(f"🔄 开始强制重写处理...")
                    original_content = content_result.content
                    
                    rewrite_result = workflow.content_rewriter.process({
                        "persona": persona_detail,
                        "scenario": scenario,
                        "query": original_content
                    })
                    
                    if rewrite_result.success:
                        print(f"✅ 强制重写成功!")
                        print(f"📝 原始文案: {original_content}")
                        print(f"📝 重写文案: {rewrite_result.content}")
                        print(f"📊 长度变化: {len(original_content)} → {len(rewrite_result.content)}")
                        
                        # 记录数据
                        workflow.content_collector.add_content(
                            user_input="",
                            persona_detail=persona_detail,
                            scenario_data={"content": scenario},
                            scenario_validation_result=True,
                            scenario_validation_reason="测试场景",
                            content_data={
                                "content": rewrite_result.content, 
                                "rewritten": True,
                                "original_content": original_content,
                                "rewrite_reason": "强制重写测试"
                            },
                            content_validation_data={"validation_reason": validation_reason},
                            content_validation_result=True,
                            processing_stage="content_rewrite",
                            final_status="rewrite_success"
                        )
                        print(f"📋 数据已记录")
                    else:
                        print(f"❌ 强制重写失败: {rewrite_result.error_message}")
                else:
                    print(f"⚠️  文案验证未通过，跳过重写")
            else:
                print(f"❌ 文案验证失败: {content_validation.error_message}")
        else:
            print(f"❌ 文案生成失败: {content_result.error_message}")
    
    # 导出Excel
    print(f"\n{'='*50}")
    print("导出测试结果...")
    excel_file = workflow.export_content_to_excel("test_force_rewrite")
    if excel_file:
        print(f"✅ 测试结果已导出到: {excel_file}")
        
        # 检查Excel内容
        import pandas as pd
        df = pd.read_excel(excel_file)
        print(f"📊 总记录数: {len(df)}")
        if '是否重写' in df.columns:
            rewrite_counts = df['是否重写'].value_counts()
            print(f"📊 重写统计: {rewrite_counts}")
        else:
            print("⚠️  未找到'是否重写'字段")
    else:
        print("❌ 导出失败")

if __name__ == "__main__":
    test_force_rewrite()