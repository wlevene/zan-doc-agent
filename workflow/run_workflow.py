#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.base_workflow import BaseWellnessWorkflow, ContentCollector
from workflow.configs import CONFIG_MAP


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="运行健康文案生成工作流")
    parser.add_argument(
        "--type",
        type=str,
        choices=["workmen", "sunian", "wellnessmom"],
        default="workmen",
        help="选择工作流类型（workmen/sunian/wellnessmom）"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="用户输入的主题或关键词"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出Excel文件路径（可选）"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="内容验证失败时的最大重试次数"
    )
    
    return parser.parse_args()


def setup_output_directory(workflow_type):
    """设置输出目录"""
    # 根据工作流类型确定输出目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, workflow_type, "output")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir


def run_workflow(workflow_type, user_input, max_retries, output_file=None):
    """运行指定类型的工作流"""
    try:
        # 1. 获取配置
        if workflow_type not in CONFIG_MAP:
            raise ValueError(f"不支持的工作流类型: {workflow_type}")
        
        config = CONFIG_MAP[workflow_type]
        persona_detail = config["persona_detail"]
        agent_config = config["agent_config"]
        workflow_config = config["workflow_config"]
        
        # 2. 设置输出目录
        output_dir = setup_output_directory(workflow_type)
        
        # 3. 创建工作流实例
        workflow = BaseWellnessWorkflow(
            persona_detail=persona_detail,
            agent_config=agent_config
        )
        
        # 4. 执行工作流
        print(f"开始执行{workflow_type}工作流...")
        print(f"用户输入: {user_input}")
        
        result = workflow.run_complete_workflow(
            user_input=user_input,
            max_retries=max_retries or workflow_config["max_retries"]
        )
        
        # 5. 处理结果
        if not result["success"]:
            print(f"工作流执行失败: {result['error']}")
            return False
        
        # 6. 收集结果
        collector = ContentCollector(output_dir=output_dir)
        
        # 准备数据项
        data = result["data"]
        item_data = {
            "user_input": user_input,
            "persona_detail": persona_detail,
            "scenario_data": {"content": data["scenario"]},
            "scenario_validation_result": True,  # 已经通过验证
            "scenario_validation_reason": "场景验证通过",
            "processing_stage": "completed",
            "final_status": "success"
        }
        
        # 添加内容信息
        if "original_content" in data:
            item_data["content_data"] = {
                "content": data["rewritten_content"],
                "original_content": data["original_content"],
                "rewritten": True
            }
            item_data["content_validation_result"] = True  # 已经通过验证
            item_data["content_validation_data"] = {
                "validation_reason": "内容验证通过"
            }
        elif "content" in data:
            item_data["content_data"] = {
                "content": data["content"]
            }
            item_data["content_validation_result"] = True  # 已经通过验证
            item_data["content_validation_data"] = {
                "validation_reason": "内容验证通过"
            }
        
        # 添加商品推荐信息
        if data.get("recommended_product"):
            product = data["recommended_product"]
            item_data["recommended_products"] = product
            item_data["product_recommendation_success"] = True
            item_data["product_recommendation_reason"] = "商品推荐成功"
            
            # 提取商品详情
            if isinstance(product, dict):
                item_data["k3_code"] = product.get("k3_code", "")
                item_data["product_name"] = product.get("name", "")
                item_data["product_selling_points"] = product.get("description", "")
                item_data["product_price"] = product.get("price", "")
        elif "product_recommendation_error" in data:
            item_data["product_recommendation_success"] = False
            item_data["product_recommendation_error"] = data["product_recommendation_error"]
        
        # 添加到收集器
        collector.add_content(**item_data)
        
        # 7. 导出结果到Excel
        if output_file:
            filepath = os.path.join(output_dir, output_file)
        else:
            filepath = None
        
        exported_file = collector.export_to_excel(filepath)
        if exported_file:
            print(f"结果已导出到: {exported_file}")
        else:
            print("导出结果失败")
        
        # 8. 打印执行成功信息
        print(f"{workflow_type}工作流执行成功！")
        return True
        
    except Exception as e:
        print(f"执行工作流时发生错误: {str(e)}")
        return False


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 运行工作流
    success = run_workflow(
        workflow_type=args.type,
        user_input=args.input,
        max_retries=args.max_retries,
        output_file=args.output
    )
    
    # 设置退出状态码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()