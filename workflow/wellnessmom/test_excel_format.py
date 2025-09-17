#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel导出格式，确保一条文案一行
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from content_item import ContentCollector, ContentItem

def test_excel_export_format():
    """测试Excel导出格式"""
    print("🧪 开始测试Excel导出格式...")
    
    # 创建收集器
    collector = ContentCollector()
    
    # 创建包含各种可能导致多行的测试数据
    test_cases = [
        {
            "user_input": "这是一个\n包含换行符的\r用户输入\t还有制表符",
            "persona_detail": "40岁养生妈妈，\n本科哲学+中医，\r165cm/65kg",
            "scenario_data": {"content": "秋季养生场景：\n1. 早晨起床\n2. 喝温水\n3. 做运动"},
            "scenario_validation_result": True,
            "scenario_validation_reason": "场景验收通过，\n符合养生要求",
            "content_data": {"content": "这是重写后的文案\n包含多行内容\r和特殊字符\"引号\""},
            "content_validation_data": {"validation_reason": "文案验收通过\n内容丰富"},
            "content_validation_result": True,
            "recommended_products": [
                {"id": "001", "name": "蜂蜜\n纯天然", "price": "99.9"},
                {"id": "002", "name": "枸杞\r宁夏特产", "price": "59.9"}
            ],
            "product_recommendation_reason": "推荐理由：\n1. 适合秋季\n2. 营养丰富",
            "product_recommendation_success": True,
            "product_recommendation_error": "",
            "processing_stage": "completed\nstage",
            "final_status": "success\nwith\ttabs",
            "created_at": "2024-01-15\n10:30:00"
        },
        {
            "user_input": "简单输入",
            "persona_detail": "简单人设",
            "scenario_data": {"content": "简单场景"},
            "scenario_validation_result": False,
            "scenario_validation_reason": "验收失败",
            "content_data": {"content": "简单文案"},
            "content_validation_data": {"validation_reason": "简单原因"},
            "content_validation_result": False,
            "recommended_products": [],
            "product_recommendation_reason": "",
            "product_recommendation_success": False,
            "product_recommendation_error": "推荐失败",
            "processing_stage": "failed",
            "final_status": "failed",
            "created_at": "2024-01-15 10:31:00"
        },
        {
            "user_input": "JSON字符串测试",
            "persona_detail": "测试人设",
            "scenario_data": {"content": "测试场景"},
            "scenario_validation_result": True,
            "scenario_validation_reason": "测试通过",
            "content_data": {"content": "测试文案"},
            "content_validation_data": {"validation_reason": "测试原因"},
            "content_validation_result": True,
            "recommended_products": '{"goods_list": ["商品A\\n换行", "商品B\\r回车", "商品C\\t制表符"]}',
            "product_recommendation_reason": "JSON测试",
            "product_recommendation_success": True,
            "product_recommendation_error": "",
            "processing_stage": "completed",
            "final_status": "success",
            "created_at": "2024-01-15 10:32:00"
        }
    ]
    
    # 添加测试数据
    for i, case in enumerate(test_cases):
        print(f"📝 添加测试用例 {i+1}")
        collector.add_content(**case)
    
    # 导出Excel
    print("📊 导出Excel文件...")
    excel_file = collector.export_to_excel("test_format.xlsx")
    
    if excel_file:
        print(f"✅ Excel文件导出成功: {excel_file}")
        
        # 验证文件是否存在
        if os.path.exists(excel_file):
            print("✅ 文件确实存在")
            
            # 读取Excel文件验证格式
            try:
                import pandas as pd
                df = pd.read_excel(excel_file)
                print(f"📋 Excel文件包含 {len(df)} 行数据")
                print(f"📋 Excel文件包含 {len(df.columns)} 列")
                
                # 检查是否有任何单元格包含换行符
                has_newlines = False
                for col in df.columns:
                    for idx, value in enumerate(df[col]):
                        if isinstance(value, str) and ('\n' in value or '\r' in value or '\t' in value):
                            print(f"❌ 发现换行符在第{idx+1}行，列'{col}': {repr(value)}")
                            has_newlines = True
                
                if not has_newlines:
                    print("✅ 所有字段都已正确清理，没有换行符")
                else:
                    print("❌ 仍有字段包含换行符")
                    
            except Exception as e:
                print(f"❌ 读取Excel文件失败: {e}")
        else:
            print("❌ 文件不存在")
    else:
        print("❌ Excel文件导出失败")
    
    print("🧪 测试完成")

if __name__ == "__main__":
    test_excel_export_format()