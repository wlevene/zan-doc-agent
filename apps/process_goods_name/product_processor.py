#!/usr/bin/env python3
"""
商品名称处理器，用于调用 Dify API 处理商品名称
"""

from typing import List, Dict
from pydantic import BaseModel, Field, validator
import json
from dify_client import DifyClient, WorkflowInput


class ProcessedProduct(BaseModel):
    """处理后的商品数据模型"""
    o: str = Field(..., description="原始商品名称")
    n: str = Field(..., description="处理后的商品名称")
    
    @validator('n')
    def validate_processed_name(cls, v):
        # 如果处理后的名称为空，将在创建对象时处理，这里只做基本清理
        return v.strip() if v else ""


class DifyProductProcessor:
    """Dify 商品处理器类"""
    
    def __init__(self, base_url: str, api_key: str, user_id: str = "product_processor"):
        """
        初始化商品处理器
        
        Args:
            base_url: Dify API 基础URL
            api_key: API 密钥
            user_id: 用户标识
        """
        self.client = DifyClient(base_url=base_url, api_key=api_key)
        self.user_id = user_id
    
    def extract_json_array(self, text: str) -> str:
        left_index = text.find('[')
        right_index = text.rfind(']')
        return text[left_index:right_index + 1]
    
    def extract_unique_product_names(self, sheet, product_name_col: int) -> Dict[str, int]:
        unique_products = {}
        for row_num in range(2, sheet.max_row + 1):
            cell = sheet.cell(row=row_num, column=product_name_col)
            if cell.value:
                product_name = str(cell.value).strip()
                if product_name and product_name not in unique_products:
                    unique_products[product_name] = row_num
        return unique_products
    
    def process_all_products(self, unique_products: Dict[str, int]) -> Dict[str, ProcessedProduct]:
        product_names = list(unique_products.keys())
        processed_results = {}
        
        for i in range(0, len(product_names), 10):
            batch = product_names[i:i + 10]
            batch_results = self.process_products(batch)
            
            for processed_product in batch_results:
                processed_results[processed_product.o] = processed_product
        
        return processed_results
    
    def update_worksheet_with_processed_names(self, sheet, product_name_col: int, unique_products: Dict[str, int], processed_results: Dict[str, ProcessedProduct]):
        for row_num in range(2, sheet.max_row + 1):
            cell = sheet.cell(row=row_num, column=product_name_col)
            if cell.value:
                original_name = str(cell.value).strip()
                if original_name in processed_results:
                    processed_product = processed_results[original_name]
                    cell.value = processed_product.n
    
    def process_products(self, product_names: List[str]) -> List[ProcessedProduct]:
        products_json = json.dumps(product_names, ensure_ascii=False)
        workflow_input = WorkflowInput(
            inputs={"text": products_json},
            response_mode="blocking",
            user=self.user_id
        )
        
        response = self.client.run_workflow(workflow_input)
        output_data = response.data.outputs
        json_text = self.extract_json_array(output_data['text'])
        result = json.loads(json_text)
        print(result)
        processed_products = []
        for item in result:
            # 如果处理后的商品名称为空，就使用原来的名称
            processed_name = item['n'] if item['n'] and item['n'].strip() else item['o']
            processed_products.append(ProcessedProduct(o=item['o'], n=processed_name))
        
        return processed_products
    
