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
    product_recommendation_reason: str = ""
    product_recommendation_success: bool = False
    product_recommendation_error: str = ""
    k3_code: str = ""  # K3编码
    product_name: str = ""  # 产品名称
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
        """添加内容项"""
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
    
    def _get_original_content(self, item: ContentItem) -> str:
        """获取原始文案内容"""
        if not item.content_data:
            return ""
        
        # 如果明确标记为重写且有original_content字段，使用original_content
        if (item.content_data.get("rewritten", False) and 
            "original_content" in item.content_data):
            return item.content_data.get("original_content", "")
        
        # 否则使用content作为原始文案
        return item.content_data.get("content", "")
    
    def _clean_text_for_excel(self, text: str) -> str:
        """清理文本，确保Excel中不会出现多行"""
        if not text:
            return ""
        
        # 转换为字符串（防止非字符串类型）
        text = str(text)
        
        # 替换所有可能导致换行的字符
        text = text.replace('\n', ' ')  # 换行符替换为空格
        text = text.replace('\r', ' ')  # 回车符替换为空格
        text = text.replace('\t', ' ')  # 制表符替换为空格
        
        # 清理多余的空格
        text = ' '.join(text.split())
        
        # 移除可能导致Excel解析问题的字符
        text = text.replace('"', "'")  # 双引号替换为单引号
        
        return text
    
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
                    "用户输入": self._clean_text_for_excel(item.user_input),
                    "人设详情": self._clean_text_for_excel(item.persona_detail),
                    "场景内容": self._clean_text_for_excel(item.scenario_data.get("content", "") if item.scenario_data else ""),
                    "场景验收结果": "通过" if item.scenario_validation_result else "未通过",
                    "场景验收原因": self._clean_text_for_excel(item.scenario_validation_reason),
                    "文案内容": self._clean_text_for_excel(self._get_original_content(item)),
                    "文案验收结果": "通过" if item.content_validation_result else "未通过",
                    "文案验收原因": self._clean_text_for_excel(item.content_validation_data.get("validation_reason", "") if item.content_validation_data else ""),
                    "重写后文案": self._clean_text_for_excel(item.content_data.get("content", "") if item.content_data else ""),
                    "K3编码": self._clean_text_for_excel(item.k3_code),
                    # 商品信息将在后面统一添加，保持K3编码和产品名称相邻
                    "商品推荐原因": self._clean_text_for_excel(item.product_recommendation_reason),
                    "商品推荐成功": "是" if item.product_recommendation_success else "否",
                    "商品推荐错误": self._clean_text_for_excel(item.product_recommendation_error),
                    "处理阶段": self._clean_text_for_excel(item.processing_stage),
                    "最终状态": self._clean_text_for_excel(item.final_status),
                    "创建时间": self._clean_text_for_excel(item.created_at)
                }
                
                # 解析推荐商品信息（单商品模式）
                product_id = ""
                product_name = ""
                product_description = ""
                product_price = ""
                
                # 优先使用ContentItem中已解析的product_name字段
                if item.product_name:
                    product_name = self._clean_text_for_excel(item.product_name)
                
                # 如果product_name为空，则从recommended_products解析
                if not product_name and item.recommended_products:
                    # 检查 recommended_products 是字符串还是字典
                    if isinstance(item.recommended_products, str):
                        # 如果是字符串，尝试解析为JSON
                        try:
                            product_data = json.loads(item.recommended_products)
                            
                            # 处理单个商品字典格式
                            if isinstance(product_data, dict):
                                product_id = self._clean_text_for_excel(str(product_data.get('id', '')))
                                if not product_name:  # 只有在product_name为空时才从这里获取
                                    product_name = self._clean_text_for_excel(str(product_data.get('name', '')))
                                product_description = self._clean_text_for_excel(str(product_data.get('description', product_data.get('desc', ''))))
                                product_price = self._clean_text_for_excel(str(product_data.get('price', '')))
                                        
                        except (json.JSONDecodeError, AttributeError):
                            # 如果解析失败，将整个字符串作为商品名称
                            if not product_name:
                                product_name = self._clean_text_for_excel(str(item.recommended_products))
                    elif isinstance(item.recommended_products, dict):
                        # 如果直接是字典格式
                        product_id = self._clean_text_for_excel(str(item.recommended_products.get('id', '')))
                        if not product_name:  # 只有在product_name为空时才从这里获取
                            product_name = self._clean_text_for_excel(str(item.recommended_products.get('name', '')))
                        product_description = self._clean_text_for_excel(str(item.recommended_products.get('description', item.recommended_products.get('desc', ''))))
                        product_price = self._clean_text_for_excel(str(item.recommended_products.get('price', '')))
                
                # 将商品信息插入到K3编码后面，保持相关信息集中
                # 创建一个新的有序字典，重新排列列顺序
                ordered_row = {}
                
                # 基本信息
                ordered_row["用户输入"] = row["用户输入"]
                ordered_row["人设详情"] = row["人设详情"]
                
                # 场景相关
                ordered_row["场景内容"] = row["场景内容"]
                ordered_row["场景验收结果"] = row["场景验收结果"]
                ordered_row["场景验收原因"] = row["场景验收原因"]
                
                # 文案相关
                ordered_row["文案内容"] = row["文案内容"]
                ordered_row["文案验收结果"] = row["文案验收结果"]
                ordered_row["文案验收原因"] = row["文案验收原因"]
                ordered_row["重写后文案"] = row["重写后文案"]
                
                # 商品相关信息集中放置
                ordered_row["K3编码"] = row["K3编码"]
                ordered_row["产品名称"] = product_name
                ordered_row["商品描述"] = product_description
                ordered_row["商品推荐原因"] = row["商品推荐原因"]
                ordered_row["商品推荐成功"] = row["商品推荐成功"]
                ordered_row["商品推荐错误"] = row["商品推荐错误"]
                
                # 状态信息
                ordered_row["处理阶段"] = row["处理阶段"]
                ordered_row["最终状态"] = row["最终状态"]
                ordered_row["创建时间"] = row["创建时间"]
                
                # 使用重新排序的行数据
                row = ordered_row
                
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