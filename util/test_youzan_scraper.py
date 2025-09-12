#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有赞商品图片获取工具测试文件

测试YouZanProductScraper类的功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from util.youzan_product_scraper import YouZanProductScraper, get_youzan_product_images, ImageInfo


def test_basic_functionality():
    """
    测试基本功能
    """
    print("\n=== 测试基本功能 ===")
    
    test_url = "https://shop18443051.m.youzan.com/wscgoods/detail/3ngm8yx62rws3ji"
    
    try:
        with YouZanProductScraper() as scraper:
            print(f"正在测试URL: {test_url}")
            
            # 测试获取所有图片
            images = scraper.get_product_images(test_url)
            print(f"\n找到 {len(images)} 张商品图片:")
            
            for i, img in enumerate(images, 1):
                print(f"{i}. URL: {img.url}")
                print(f"   尺寸类型: {img.size_type}")
                print(f"   格式: {img.format}")
                if img.alt_text:
                    print(f"   描述: {img.alt_text}")
                if img.width and img.height:
                    print(f"   尺寸: {img.width}x{img.height}")
                print()
            
            return len(images) > 0
            
    except Exception as e:
        print(f"基本功能测试失败: {str(e)}")
        return False


def test_high_quality_images():
    """
    测试高质量图片获取
    """
    print("\n=== 测试高质量图片获取 ===")
    
    test_url = "https://shop18443051.m.youzan.com/wscgoods/detail/3ngm8yx62rws3ji"
    
    try:
        with YouZanProductScraper() as scraper:
            # 获取高质量图片
            hq_images = scraper.get_high_quality_images(test_url)
            print(f"找到 {len(hq_images)} 张高质量图片:")
            
            for i, img in enumerate(hq_images, 1):
                print(f"{i}. {img.url} (类型: {img.size_type})")
            
            return len(hq_images) > 0
            
    except Exception as e:
        print(f"高质量图片测试失败: {str(e)}")
        return False


def test_convenience_function():
    """
    测试便捷函数
    """
    print("\n=== 测试便捷函数 ===")
    
    test_url = "https://shop18443051.m.youzan.com/wscgoods/detail/3ngm8yx62rws3ji"
    
    try:
        # 测试便捷函数
        urls = get_youzan_product_images(test_url, high_quality_only=True)
        print(f"便捷函数获取到 {len(urls)} 个图片URL:")
        
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        
        return len(urls) > 0
        
    except Exception as e:
        print(f"便捷函数测试失败: {str(e)}")
        return False


def test_url_validation():
    """
    测试URL验证和错误处理
    """
    print("\n=== 测试URL验证和错误处理 ===")
    
    invalid_urls = [
        "https://invalid-url.com",
        "https://shop18443051.m.youzan.com/invalid-path",
        "not-a-url"
    ]
    
    for url in invalid_urls:
        try:
            with YouZanProductScraper(timeout=5, retry_count=1) as scraper:
                images = scraper.get_product_images(url)
                print(f"URL {url}: 获取到 {len(images)} 张图片")
        except Exception as e:
            print(f"URL {url}: 预期的错误 - {str(e)[:100]}...")
    
    return True


def test_image_filtering():
    """
    测试图片过滤功能
    """
    print("\n=== 测试图片过滤功能 ===")
    
    # 创建测试用的ImageInfo对象
    test_images = [
        ImageInfo(url="https://img.yzcdn.cn/test1.jpg", size_type="large"),
        ImageInfo(url="https://img.yzcdn.cn/test2.jpg", size_type="thumbnail"),
        ImageInfo(url="https://img.yzcdn.cn/test3.jpg", size_type="original"),
        ImageInfo(url="https://img.yzcdn.cn/logo.svg", size_type="thumbnail"),
    ]
    
    scraper = YouZanProductScraper()
    
    # 测试去重功能
    duplicate_images = test_images + [ImageInfo(url="https://img.yzcdn.cn/test1.jpg?v=2", size_type="large")]
    unique_images = scraper._deduplicate_images(duplicate_images)
    
    print(f"原始图片数量: {len(duplicate_images)}")
    print(f"去重后图片数量: {len(unique_images)}")
    
    # 测试图片类型推断
    test_urls = [
        "https://img.yzcdn.cn/upload_files/2025/08/28/test.jpg?imageView2/2/w/750/h/0/q/75/format/jpg",
        "https://img.yzcdn.cn/upload_files/thumb_test.jpg",
        "https://img.yzcdn.cn/upload_files/large_test.png",
    ]
    
    for url in test_urls:
        size_type = scraper._infer_size_type(url)
        is_product = scraper._is_product_image(url)
        print(f"URL: {url[:50]}...")
        print(f"  尺寸类型: {size_type}, 是商品图片: {is_product}")
    
    scraper.close()
    return True


def main():
    """
    主测试函数
    """
    print("开始测试有赞商品图片获取工具...")
    
    test_results = {
        "基本功能": test_basic_functionality(),
        "高质量图片": test_high_quality_images(),
        "便捷函数": test_convenience_function(),
        "错误处理": test_url_validation(),
        "图片过滤": test_image_filtering(),
    }
    
    print("\n=== 测试结果汇总 ===")
    for test_name, result in test_results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    passed_count = sum(test_results.values())
    total_count = len(test_results)
    
    print(f"\n总计: {passed_count}/{total_count} 个测试通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！工具类功能正常。")
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 个测试失败，请检查相关功能。")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)