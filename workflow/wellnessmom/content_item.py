#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文案数据收集和导出模块

提供ContentItem和ContentCollector类，用于收集工作流中的文案数据并导出到Excel。
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ContentItem:
    """
    文案数据项，包含工作流中生成的文案相关信息
    """
    # 基础信息
    timestamp: str  # 生成时间
    user_input: str  # 用户输入
    persona_detail: str  # 人物设定
    
    # 场景信息
    scenario_title: str  # 场景标题
    scenario_description: str  # 场景描述
    scenario_validation: bool  # 场景验收结果
    scenario_validation_reason: str = ""  # 场景验收原因
    
    # 文案信息
    content_title: str = ""  # 文案标题
    content_body: str = ""  # 文案正文
    content_validation: bool = False  # 文案验收结果
    content_validation_feedback: str = ""  # 文案验收反馈
    content_generation_success: bool = True  # 文案生成是否成功
    content_generation_error: str = ""  # 文案生成错误信息
    
    # 推荐商品信息（可选）
    recommended_products: str = ""  # 推荐商品列表
    product_recommendation_success: bool = False  # 商品推荐是否成功
    product_recommendation_error: str = ""  # 商品推荐错误信息
    
    # 处理状态
    processing_stage: str = ""  # 当前处理阶段（scenario_validation, content_generation, content_validation, product_recommendation）
    final_status: str = ""  # 最终状态（success, scenario_failed, content_failed, validation_failed）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    @staticmethod
    def to_excel(items: List['ContentItem'], filename: str = None) -> str:
        """
        将ContentItem列表导出到Excel文件
        
        Args:
            items: ContentItem对象列表
            filename: 输出文件名，如果为None则自动生成
            
        Returns:
            str: 生成的Excel文件路径
        """
        if not items:
            return None
            
        # 转换为DataFrame
        data = [item.to_dict() for item in items]
        df = pd.DataFrame(data)
        
        # 重新排列列的顺序，使其更易读
        column_order = [
            'timestamp', 'user_input', 'persona_detail',
            'scenario_title', 'scenario_description', 'scenario_validation', 'scenario_validation_reason',
            'content_title', 'content_body', 'content_validation', 'content_validation_feedback',
            'content_generation_success', 'content_generation_error',
            'recommended_products', 'product_recommendation_success', 'product_recommendation_error',
            'processing_stage', 'final_status'
        ]
        
        # 只保留存在的列
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # 生成文件名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wellness_content_{timestamp}.xlsx"
        
        # 确保输出目录存在
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 导出到Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='文案数据', index=False)
            
            # 获取工作表并设置列宽
            worksheet = writer.sheets['文案数据']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # 限制最大宽度
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filepath
    
    @staticmethod
    def from_excel(filepath: str) -> List['ContentItem']:
        """
        从Excel文件读取ContentItem列表
        
        Args:
            filepath: Excel文件路径
            
        Returns:
            List[ContentItem]: ContentItem对象列表
        """
        try:
            df = pd.read_excel(filepath, sheet_name='文案数据')
            items = []
            
            for _, row in df.iterrows():
                # 处理NaN值
                row_dict = row.to_dict()
                for key, value in row_dict.items():
                    if pd.isna(value):
                        row_dict[key] = ""
                
                item = ContentItem(**row_dict)
                items.append(item)
            
            return items
        except Exception as e:
            print(f"读取Excel文件失败: {e}")
            return []


class ContentCollector:
    """
    文案数据收集器，用于在工作流中收集和管理文案数据
    """
    
    def __init__(self):
        self.items: List[ContentItem] = []
    
    def add_content(self, 
                   user_input: str,
                   persona_detail: str,
                   scenario_data: Dict[str, Any],
                   scenario_validation_result: bool,
                   content_data: Dict[str, Any],
                   content_validation_data: Dict[str, Any],
                   content_validation_result: bool,
                   recommended_products: str = "",
                   scenario_validation_reason: str = "",
                   content_generation_success: bool = True,
                   content_generation_error: str = "",
                   product_recommendation_success: bool = False,
                   product_recommendation_error: str = "",
                   processing_stage: str = "",
                   final_status: str = "") -> None:
        """
        添加一条文案数据
        
        Args:
            user_input: 用户输入
            persona_detail: 人物设定
            scenario_data: 场景数据
            scenario_validation_result: 场景验收结果
            content_data: 文案数据
            content_validation_data: 文案验收数据
            content_validation_result: 文案验收结果
            recommended_products: 推荐商品信息
            scenario_validation_reason: 场景验收原因
            content_generation_success: 文案生成是否成功
            content_generation_error: 文案生成错误信息
            product_recommendation_success: 商品推荐是否成功
            product_recommendation_error: 商品推荐错误信息
            processing_stage: 当前处理阶段
            final_status: 最终状态
        """
        item = ContentItem(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_input=user_input,
            persona_detail=persona_detail,
            scenario_title=scenario_data.get('title', ''),
            scenario_description=scenario_data.get('content', scenario_data.get('description', '')),
            scenario_validation=scenario_validation_result,
            scenario_validation_reason=scenario_validation_reason,
            content_title=content_data.get('title', ''),
            content_body=content_data.get('content', ''),
            content_validation=content_validation_result,
            content_validation_feedback=content_validation_data.get('validation_reason', content_validation_data.get('feedback', '')),
            content_generation_success=content_generation_success,
            content_generation_error=content_generation_error,
            recommended_products=recommended_products,
            product_recommendation_success=product_recommendation_success,
            product_recommendation_error=product_recommendation_error,
            processing_stage=processing_stage,
            final_status=final_status
        )
        
        self.items.append(item)
    
    def add_scenario_only(self, 
                         user_input: str,
                         persona_detail: str,
                         scenario: str,
                         scenario_validation_result: bool,
                         scenario_validation_reason: str = "") -> None:
        """
        仅添加场景数据（用于场景验证失败的情况）
        
        Args:
            user_input: 用户输入
            persona_detail: 人物设定
            scenario: 场景内容
            scenario_validation_result: 场景验收结果
            scenario_validation_reason: 场景验收原因
        """
        item = ContentItem(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_input=user_input,
            persona_detail=persona_detail,
            scenario_title="",
            scenario_description=scenario,
            scenario_validation=scenario_validation_result,
            scenario_validation_reason=scenario_validation_reason,
            processing_stage="scenario_validation",
            final_status="scenario_failed" if not scenario_validation_result else "success"
        )
        
        self.items.append(item)
    
    def get_items(self) -> List[ContentItem]:
        """获取所有收集的文案数据"""
        return self.items.copy()
    
    def get_count(self) -> int:
        """获取收集的文案数据数量"""
        return len(self.items)
    
    def export_to_excel(self, filename: str = None) -> Optional[str]:
        """
        导出收集的数据到Excel文件
        
        Args:
            filename: 输出文件名，如果为None则自动生成
            
        Returns:
            str: 生成的Excel文件路径，如果没有数据则返回None
        """
        if not self.items:
            return None
        
        return ContentItem.to_excel(self.items, filename)
    
    def clear(self) -> None:
        """清空收集的数据"""
        self.items.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取收集数据的统计信息
        
        Returns:
            Dict: 包含统计信息的字典
        """
        if not self.items:
            return {
                'total_count': 0,
                'scenario_pass_rate': 0,
                'content_pass_rate': 0,
                'date_range': None
            }
        
        total_count = len(self.items)
        scenario_passed = sum(1 for item in self.items if item.scenario_validation)
        content_passed = sum(1 for item in self.items if item.content_validation)
        
        timestamps = [item.timestamp for item in self.items]
        
        return {
            'total_count': total_count,
            'scenario_pass_rate': scenario_passed / total_count * 100,
            'content_pass_rate': content_passed / total_count * 100,
            'date_range': {
                'start': min(timestamps),
                'end': max(timestamps)
            }
        }