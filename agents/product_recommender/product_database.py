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
        try:
            return self._load_from_excel()
        except Exception as e:
            print(f"从Excel读取数据失败: {e}，使用默认数据")
            return self._get_fallback_data()
    
    def _load_from_excel(self) -> Dict[str, ProductInfo]:
        """从goods.xlsx读取商品数据"""
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(current_dir, 'goods.xlsx')
        
        # 读取Excel文件
        df = pd.read_excel(excel_path, sheet_name='sheet1')
        
        products = {}
        
        for index, row in df.iterrows():
            # 跳过无效行
            if pd.isna(row['商品id']) or pd.isna(row['商品名称']):
                continue
                
            # 字段映射和数据处理
            product_id = str(int(row['商品id'])) if not pd.isna(row['商品id']) else f"product_{index}"
            name = str(row['商品名称']) if not pd.isna(row['商品名称']) else "未知商品"
            description = str(row['分享描述']) if not pd.isna(row['分享描述']) else str(row['商品卖点']) if not pd.isna(row['商品卖点']) else "暂无描述"
            price = float(row['价格（元）']) if not pd.isna(row['价格（元）']) else 0.0
            category = self._extract_category(row['商品分组']) if not pd.isna(row['商品分组']) else "其他"
            brand = "正安" if "正安" in name else "未知品牌"
            image_url = str(row['商品链接']) if not pd.isna(row['商品链接']) else ""
            features = self._extract_features(row['商品分组'], row['商品卖点'])
            target_audience = self._extract_target_audience(row['商品分组'])
            stock = int(row['库存']) if not pd.isna(row['库存']) else 100
            
            # 读取新增字段
            core_selling_point = str(row['一句话核心卖点']) if '一句话核心卖点' in row and not pd.isna(row['一句话核心卖点']) else ""
            product_selling_points = str(row['产品卖点']) if '产品卖点' in row and not pd.isna(row['产品卖点']) else ""
            formula_source = str(row['配方出处']) if '配方出处' in row and not pd.isna(row['配方出处']) else ""
            usage_method = str(row['使用方法']) if '使用方法' in row and not pd.isna(row['使用方法']) else ""
            k3_code = str(row['K3编码']) if 'K3编码' in row and not pd.isna(row['K3编码']) else ""
            
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
    
    def _extract_category(self, group_info: str) -> str:
        """从商品分组信息中提取分类"""
        if pd.isna(group_info):
            return "其他"
            
        group_str = str(group_info)
        if "草本洗护" in group_str:
            return "洗护用品"
        elif "道地风物" in group_str:
            return "保健品"
        elif "家居生活" in group_str:
            return "家居用品"
        else:
            return "健康食品"
    
    def _extract_features(self, group_info, selling_point) -> List[str]:
        """从商品信息中提取特性"""
        features = []
        
        # 从商品分组提取特性
        if not pd.isna(group_info):
            group_str = str(group_info)
            if "草本" in group_str:
                features.append("天然草本")
            if "道地" in group_str:
                features.append("道地原材")
            if "家庭养护" in group_str:
                features.append("家庭适用")
        
        # 从商品卖点提取特性
        if not pd.isna(selling_point):
            selling_str = str(selling_point)
            if "温和" in selling_str:
                features.append("温和配方")
            if "天然" in selling_str:
                features.append("天然成分")
            if "精选" in selling_str:
                features.append("精选原料")
        
        return features if features else ["优质产品"]
    
    def _extract_target_audience(self, group_info) -> str:
        """从商品分组信息中提取目标用户群体"""
        if pd.isna(group_info):
            return "一般用户"
            
        group_str = str(group_info)
        if "家庭养护" in group_str:
            return "注重健康的家庭"
        elif "湿热体质" in group_str:
            return "湿热体质人群"
        elif "阴虚体质" in group_str:
            return "阴虚体质人群"
        else:
            return "养生爱好者"
    
    def _get_fallback_data(self) -> Dict[str, ProductInfo]:
        """获取备用数据（原硬编码数据）"""
        products = {
            "wellness_001": ProductInfo(
                product_id="wellness_001",
                name="有机燕麦片",
                description="100%有机燕麦，富含膳食纤维，适合全家人的健康早餐选择",
                price=39.9,
                category="健康食品",
                brand="自然之选",
                image_url="https://example.com/images/organic_oats.jpg",
                features=["有机认证", "高纤维", "无添加糖", "易消化"],
                target_audience="注重健康的家庭",
                core_selling_point="100%有机燕麦，营养健康全家适用",
                product_selling_points="有机认证、高纤维、无添加糖、易消化、适合全家人",
                formula_source="澳洲有机农场直供",
                usage_method="每次30-50g，用热水或牛奶冲泡，可加入水果或坚果",
                k3_code="K3001"
            ),
            "wellness_002": ProductInfo(
                product_id="wellness_002",
                name="蛋白质粉",
                description="高品质乳清蛋白，支持肌肉生长和恢复，适合运动人群",
                price=199.0,
                category="运动营养",
                brand="力量源",
                image_url="https://example.com/images/protein_powder.jpg",
                features=["高蛋白含量", "易吸收", "多种口味", "无人工色素"],
                target_audience="健身爱好者",
                core_selling_point="高品质乳清蛋白，快速补充运动营养",
                product_selling_points="高蛋白含量、易吸收、多种口味、无人工色素、支持肌肉生长",
                formula_source="新西兰优质乳清蛋白",
                usage_method="运动后30分钟内，用250ml水或牛奶冲调一勺蛋白粉",
                k3_code="K3002"
            )
        }
        return products
    
    def get_product_by_id(self, product_id: str) -> Optional[ProductInfo]:
        """根据商品ID获取商品信息"""
        return self._products.get(product_id)
    
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