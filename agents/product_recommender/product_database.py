from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
import pandas as pd
import os

@dataclass
class ProductInfo:
    """商品信息类"""
    product_id: str
    name: str
    description: str
    price: float
    category: str
    brand: str
    image_url: str
    features: List[str]
    target_audience: str
    stock: int = 100
    rating: float = 4.5
    core_selling_point: str = ""  # 一句话核心卖点
    product_selling_points: str = ""  # 产品卖点
    formula_source: str = ""  # 配方出处
    usage_method: str = ""  # 使用方法
    k3_code: str = ""  # K3编码
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "brand": self.brand,
            "image_url": self.image_url,
            "features": self.features,
            "target_audience": self.target_audience,
            "stock": self.stock,
            "rating": self.rating,
            "core_selling_point": self.core_selling_point,
            "product_selling_points": self.product_selling_points,
            "formula_source": self.formula_source,
            "usage_method": self.usage_method,
            "k3_code": self.k3_code
        }

class ProductDatabase:
    """商品信息数据库模拟类"""
    
    def __init__(self):
        self._products = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, ProductInfo]:
        """从Excel文件读取商品数据"""
        return self._load_from_excel()
    
    def _load_from_excel(self) -> Dict[str, ProductInfo]:
        """从正安产品资料库.xlsx读取商品数据"""
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(current_dir, '正安产品资料库.xlsx')
        
        # 读取Excel文件，跳过第一行标题，使用第二行作为列名
        df = pd.read_excel(excel_path, sheet_name='正安国货铺', header=1)
        
        products = {}
        
        for index, row in df.iterrows():
            # 跳过无效行
            if pd.isna(row['品项']) or pd.isna(row['K3编码']):
                continue
                
            # 字段映射和数据处理
            k3_code = str(row['K3编码']) if not pd.isna(row['K3编码']) else f"product_{index}"
            product_id = k3_code  # 使用K3编码作为product_id
            name = str(row['品项']) if not pd.isna(row['品项']) else "未知商品"
            description = str(row['产品卖点']) if not pd.isna(row['产品卖点']) else "暂无描述"
            
            # 解析价格 - 处理可能包含换行符的价格数据
            price_raw = row['零售价']
            if pd.isna(price_raw):
                price = 0.0
            else:
                price_str = str(price_raw).strip()
                # 如果包含换行符，取第一个数字
                if '\n' in price_str:
                    price_str = price_str.split('\n')[0].strip()
                try:
                    price = float(price_str)
                except (ValueError, TypeError):
                    price = 0.0
            category = self._extract_category(row['一级分类'], row['二级分类']) if not pd.isna(row['一级分类']) else "其他"
            brand = str(row['品牌']) if not pd.isna(row['品牌']) else "正安"
            image_url = ""  # Excel中没有图片链接字段
            features = self._extract_features(row['一级分类'], row['产品卖点'])
            target_audience = self._extract_target_audience(row['一级分类'])
            stock = 100  # 默认库存
            
            # 读取新增字段
            core_selling_point = str(row['一句话核心卖点']) if not pd.isna(row['一句话核心卖点']) else ""
            product_selling_points = str(row['产品卖点']) if not pd.isna(row['产品卖点']) else ""
            formula_source = str(row['古方出处']) if not pd.isna(row['古方出处']) else ""
            usage_method = str(row['使用方法']) if not pd.isna(row['使用方法']) else ""
            
            product = ProductInfo(
                product_id=product_id,
                name=name,
                description=description,
                price=price,
                category=category,
                brand=brand,
                image_url=image_url,
                features=features,
                target_audience=target_audience,
                stock=stock,
                core_selling_point=core_selling_point,
                product_selling_points=product_selling_points,
                formula_source=formula_source,
                usage_method=usage_method,
                k3_code=k3_code
            )
            
            products[product_id] = product
            
        return products
    
    def _extract_category(self, primary_category, secondary_category) -> str:
        """从一级分类和二级分类信息中提取分类"""
        if pd.isna(primary_category):
            return "其他"
            
        primary_str = str(primary_category)
        secondary_str = str(secondary_category) if not pd.isna(secondary_category) else ""
        
        if "用品" in primary_str:
            if "艾制品" in secondary_str:
                return "艾制品"
            elif "洗护" in secondary_str:
                return "洗护用品"
            else:
                return "生活用品"
        elif "食品" in primary_str:
            return "健康食品"
        elif "保健" in primary_str:
            return "保健品"
        else:
            return primary_str
    
    def _extract_features(self, primary_category, selling_point) -> List[str]:
        """从商品信息中提取特性"""
        features = []
        
        # 从一级分类提取特性
        if not pd.isna(primary_category):
            category_str = str(primary_category)
            if "用品" in category_str:
                features.append("生活用品")
            if "食品" in category_str:
                features.append("健康食品")
        
        # 从商品卖点提取特性
        if not pd.isna(selling_point):
            selling_str = str(selling_point)
            if "温和" in selling_str:
                features.append("温和配方")
            if "天然" in selling_str:
                features.append("天然成分")
            if "精选" in selling_str:
                features.append("精选原料")
            if "艾" in selling_str:
                features.append("艾草制品")
        
        return features if features else ["优质产品"]
    
    def _extract_target_audience(self, primary_category) -> str:
        """从一级分类信息中提取目标用户群体"""
        if pd.isna(primary_category):
            return "一般用户"
            
        category_str = str(primary_category)
        if "用品" in category_str:
            return "注重健康的家庭"
        elif "食品" in category_str:
            return "健康饮食人群"
        else:
            return "养生爱好者"
    

    
    def get_product_by_id(self, product_id: str) -> Optional[ProductInfo]:
        """根据商品ID获取商品信息"""
        return self._products.get(product_id)
    
    def get_product_by_k3_code(self, k3_code: str) -> Optional[ProductInfo]:
        """根据K3编码获取商品信息"""
        for product in self._products.values():
            if product.k3_code == k3_code:
                return product
        return None
    
    def get_products_by_category(self, category: str) -> List[ProductInfo]:
        """根据分类获取商品列表"""
        return [product for product in self._products.values() 
                if product.category == category]
    
    def get_products_by_target_audience(self, target_audience: str) -> List[ProductInfo]:
        """根据目标用户群体获取商品列表"""
        return [product for product in self._products.values() 
                if target_audience.lower() in product.target_audience.lower()]
    
    def search_products(self, keyword: str) -> List[ProductInfo]:
        """根据关键词搜索商品"""
        keyword = keyword.lower()
        results = []
        
        for product in self._products.values():
            if (keyword in product.name.lower() or 
                keyword in product.description.lower() or 
                keyword in product.category.lower() or
                any(keyword in feature.lower() for feature in product.features)):
                results.append(product)
        
        return results
    
    def get_all_products(self) -> List[ProductInfo]:
        """获取所有商品信息"""
        return list(self._products.values())
    
    def get_product_image_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """获取商品图片信息"""
        product = self.get_product_by_id(product_id)
        if product:
            return {
                "product_id": product_id,
                "image_url": product.image_url,
                "alt_text": f"{product.name} - {product.description}",
                "product_name": product.name
            }
        return None
    
    def get_recommended_products(self, user_profile: Dict[str, Any], limit: int = 3) -> List[ProductInfo]:
        """根据用户画像推荐商品"""
        # 简单的推荐逻辑：根据用户兴趣和需求匹配商品
        interests = user_profile.get('interests', [])
        health_goals = user_profile.get('health_goals', [])
        
        scored_products = []
        
        for product in self._products.values():
            score = 0
            
            # 根据兴趣匹配
            for interest in interests:
                if interest.lower() in product.category.lower() or \
                   interest.lower() in product.target_audience.lower():
                    score += 2
            
            # 根据健康目标匹配
            for goal in health_goals:
                if goal.lower() in product.description.lower() or \
                   any(goal.lower() in feature.lower() for feature in product.features):
                    score += 3
            
            if score > 0:
                scored_products.append((product, score))
        
        # 按分数排序并返回前N个
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [product for product, score in scored_products[:limit]]
    
    def to_json(self) -> str:
        """将所有商品信息转换为JSON格式"""
        products_dict = {pid: product.to_dict() for pid, product in self._products.items()}
        return json.dumps(products_dict, ensure_ascii=False, indent=2)