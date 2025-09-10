from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json

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
            "rating": self.rating
        }

class ProductDatabase:
    """商品信息数据库模拟类"""
    
    def __init__(self):
        self._products = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, ProductInfo]:
        """初始化模拟商品数据"""
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
                target_audience="注重健康的家庭"
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
                target_audience="健身爱好者"
            ),
            "wellness_003": ProductInfo(
                product_id="wellness_003",
                name="维生素C片",
                description="天然维生素C，增强免疫力，美白肌肤，每日一片健康守护",
                price=89.0,
                category="保健品",
                brand="健康伴侣",
                image_url="https://example.com/images/vitamin_c.jpg",
                features=["天然提取", "高含量", "易吞咽", "无副作用"],
                target_audience="关注免疫力的人群"
            ),
            "wellness_004": ProductInfo(
                product_id="wellness_004",
                name="瑜伽垫",
                description="环保TPE材质，防滑耐用，适合各种瑜伽和健身运动",
                price=128.0,
                category="运动器材",
                brand="禅意生活",
                image_url="https://example.com/images/yoga_mat.jpg",
                features=["环保材质", "防滑设计", "易清洁", "便携收纳"],
                target_audience="瑜伽爱好者"
            ),
            "wellness_005": ProductInfo(
                product_id="wellness_005",
                name="蜂蜜柠檬茶",
                description="天然蜂蜜配新鲜柠檬，清香怡人，富含维生素，温润养生",
                price=45.0,
                category="健康饮品",
                brand="蜜语茶香",
                image_url="https://example.com/images/honey_lemon_tea.jpg",
                features=["天然蜂蜜", "新鲜柠檬", "无添加剂", "温润养生"],
                target_audience="注重养生的人群"
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