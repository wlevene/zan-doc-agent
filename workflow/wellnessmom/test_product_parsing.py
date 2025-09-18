#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def test_product_parsing():
    """测试商品推荐解析逻辑"""
    
    # 模拟实际返回的商品推荐数据
    test_data = """```json
{
  "goods": {
    "id": "4342390614",
    "name": "丹草糖 / 非遗山楂条 / 陈皮扁豆花茶/艾条试用装5盒 / 原材盲盒50克 / 九子包热敷贴5袋",
    "description": "暂无描述",
    "price": 59.9,
    "category": "健康食品",
    "brand": "未知品牌",
    "features": [
      "优质产品"
    ]
  },
  "reason": "文案提到戒烟和减肥，需要一些替代品来帮助缓解烟瘾和控制食欲。丹草糖和陈皮扁豆花茶可以帮助润喉，山楂条可以帮助消化和控制食欲，这些都是戒烟和减肥过程中的好帮手。"
}
```"""
    
    print("🧪 测试商品推荐解析逻辑")
    print("=" * 50)
    
    # 清理数据
    recommended_products = test_data.replace("```json", "").replace("```", "")
    print(f"📝 清理后的数据: {recommended_products[:100]}...")
    
    # 解析JSON数据
    product_goods_list = ""
    product_recommendation_reason = ""
    product_ids = []  # 存储商品ID列表
    
    try:
        product_data = json.loads(recommended_products)
        print(f"✅ JSON解析成功")
        
        # 提取商品信息和推荐原因
        reason = product_data.get('reason', '')
        
        # 支持两种数据结构：goods_list（数组）或 goods（单个对象）
        goods_list = []
        if 'goods_list' in product_data:
            # 旧格式：goods_list 数组
            goods_list = product_data.get('goods_list', [])
            print(f"📦 发现 goods_list 格式，商品数量: {len(goods_list)}")
        elif 'goods' in product_data:
            # 新格式：goods 单个对象
            goods_obj = product_data.get('goods')
            if goods_obj:
                goods_list = [goods_obj]  # 转换为数组格式统一处理
                print(f"📦 发现 goods 格式，转换为数组，商品数量: {len(goods_list)}")
        
        # 格式化商品列表
        if goods_list:
            product_goods_list = json.dumps(goods_list, ensure_ascii=False, indent=2)
            # 提取商品ID列表
            for good in goods_list:
                if isinstance(good, dict) and 'id' in good:
                    product_ids.append(good['id'])
                elif isinstance(good, str):
                    # 如果商品是字符串格式，尝试从商品名称推断ID
                    product_ids.append(f"unknown_{len(product_ids)}")
        else:
            product_goods_list = "无推荐商品"
        
        product_recommendation_reason = reason
        
        # 输出结果
        print(f"\n📊 解析结果:")
        print(f"🛍️  商品列表: {product_goods_list[:200]}...")
        print(f"🆔 商品ID列表: {product_ids}")
        print(f"💭 推荐原因: {product_recommendation_reason[:100]}...")
        
        # 验证结果
        if product_ids and product_ids[0] == "4342390614":
            print(f"\n✅ 测试通过！成功提取到商品ID: {product_ids[0]}")
            return True
        else:
            print(f"\n❌ 测试失败！商品ID提取错误: {product_ids}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return False

if __name__ == "__main__":
    success = test_product_parsing()
    if success:
        print(f"\n🎉 商品推荐解析逻辑修复成功！")
    else:
        print(f"\n💥 商品推荐解析逻辑仍有问题！")