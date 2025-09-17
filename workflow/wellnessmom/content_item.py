import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ContentItem:
    """文案数据项"""
    user_input: str = ""
    persona_detail: str = ""
    scenario_data: Dict[str, Any] = None
    scenario_validation_result: bool = False
    scenario_validation_reason: str = ""
    content_data: Dict[str, Any] = None
    content_validation_data: Dict[str, Any] = None
    content_validation_result: bool = False
    recommended_products: List[Dict[str, Any]] = None
    product_goods_list: str = ""
    product_recommendation_reason: str = ""
    product_recommendation_success: bool = False
    product_recommendation_error: str = ""
    processing_stage: str = "pending"
    final_status: str = "pending"
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.scenario_data is None:
            self.scenario_data = {}
        if self.content_data is None:
            self.content_data = {}
        if self.content_validation_data is None:
            self.content_validation_data = {}
        if self.recommended_products is None:
            self.recommended_products = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    def is_valid(self) -> bool:
        """检查是否为有效的文案数据（场景和内容都验收通过）"""
        return (self.scenario_validation_result and 
                self.content_validation_result and 
                self.final_status == "success")


class ContentCollector:
    """文案数据收集器"""
    
    def __init__(self):
        self.items: List[ContentItem] = []
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def add_content(self, **kwargs) -> None:
        """添加完整的文案数据"""
        item = ContentItem(**kwargs)
        self.items.append(item)
    
    def add_scenario_only(self, user_input: str, persona_detail: str, 
                         scenario: str, scenario_validation_result: bool,
                         scenario_validation_reason: str) -> None:
        """仅添加场景数据（用于场景验收失败的情况）"""
        item = ContentItem(
            user_input=user_input,
            persona_detail=persona_detail,
            scenario_data={"content": scenario},
            scenario_validation_result=scenario_validation_result,
            scenario_validation_reason=scenario_validation_reason,
            processing_stage="scenario_only",
            final_status="failed" if not scenario_validation_result else "partial"
        )
        self.items.append(item)
    
    def get_valid_items(self) -> List[ContentItem]:
        """获取验收通过的文案数据"""
        return [item for item in self.items if item.is_valid()]
    
    def clear(self) -> None:
        """清空所有数据"""
        self.items.clear()
    
    def __len__(self) -> int:
        """返回数据总数"""
        return len(self.items)
    
    def get_count(self) -> int:
        """获取收集的数据总数（与 __len__ 功能相同）"""
        return len(self.items)
    
    def export_to_excel(self, filename: str = None) -> Optional[str]:
        """导出数据到Excel文件"""
        if not self.items:
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wellness_content_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # 准备数据
            data_rows = []
            for item in self.items:
                row = {
                    "用户输入": item.user_input,
                    "人设详情": item.persona_detail,
                    "场景内容": item.scenario_data.get("content", "") if item.scenario_data else "",
                    "场景验收结果": "通过" if item.scenario_validation_result else "未通过",
                    "场景验收原因": item.scenario_validation_reason,
                    "文案内容": item.content_data.get("content", "") if item.content_data else "",
                    "是否重写": "是" if (item.content_data and item.content_data.get("rewritten", False)) else "否",
                    "原始文案": item.content_data.get("original_content", "") if item.content_data else "",
                    "重写原因": item.content_data.get("rewrite_reason", "") if item.content_data else "",
                    "文案验收结果": "通过" if item.content_validation_result else "未通过",
                    "文案验收原因": item.content_validation_data.get("validation_reason", "") if item.content_validation_data else "",
                    "推荐商品数量": len(item.recommended_products) if item.recommended_products else 0,
                    "商品推荐原因": item.product_recommendation_reason,
                    "商品推荐成功": "是" if item.product_recommendation_success else "否",
                    "商品推荐错误": item.product_recommendation_error,
                    "处理阶段": item.processing_stage,
                    "最终状态": item.final_status,
                    "创建时间": item.created_at
                }
                
                # 添加推荐商品详情
                if item.recommended_products:
                    products_info = []
                    # 检查 recommended_products 是字符串还是列表
                    if isinstance(item.recommended_products, str):
                        # 如果是字符串，尝试解析为JSON
                        try:
                            product_data = json.loads(item.recommended_products)
                            goods_list = product_data.get('goods_list', [])
                            for product_name in goods_list:
                                products_info.append(f"商品名称:{product_name}")
                        except (json.JSONDecodeError, AttributeError):
                            # 如果解析失败，直接使用字符串
                            products_info.append(item.recommended_products)
                    elif isinstance(item.recommended_products, list):
                        # 如果是列表，按原来的方式处理
                        for product in item.recommended_products:
                            if isinstance(product, dict):
                                product_info = f"ID:{product.get('id', 'N/A')}, 名称:{product.get('name', 'N/A')}, 价格:{product.get('price', 'N/A')}"
                            else:
                                product_info = str(product)
                            products_info.append(product_info)
                    
                    row["推荐商品详情"] = "; ".join(products_info)
                else:
                    row["推荐商品详情"] = ""
                
                data_rows.append(row)
            
            # 创建DataFrame并导出
            df = pd.DataFrame(data_rows)
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            return filepath
            
        except Exception as e:
            print(f"导出Excel文件失败: {str(e)}")
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """获取数据统计摘要"""
        total_count = len(self.items)
        valid_count = len(self.get_valid_items())
        
        stage_counts = {}
        status_counts = {}
        
        for item in self.items:
            stage = item.processing_stage
            status = item.final_status
            
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_count": total_count,
            "valid_count": valid_count,
            "success_rate": valid_count / total_count if total_count > 0 else 0,
            "stage_distribution": stage_counts,
            "status_distribution": status_counts
        }