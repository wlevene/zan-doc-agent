#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有赞商品详情页图片获取工具类

提供YouZanProductScraper类，用于从有赞商品详情页获取商品大图URLs。
支持多种图片格式和尺寸处理。
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time
import logging
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImageInfo:
    """图片信息数据类"""
    url: str
    alt_text: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    format: str = "jpg"
    size_type: str = "original"  # original, thumbnail, medium, large


class YouZanProductScraper:
    """
    有赞商品详情页图片获取器
    
    用于从有赞商品详情页面抓取商品大图URLs，支持多种图片格式和尺寸。
    """
    
    def __init__(self, timeout: int = 10, retry_count: int = 3):
        """
        初始化爬虫器
        
        Args:
            timeout: 请求超时时间（秒）
            retry_count: 重试次数
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()
        
        # 设置请求头，模拟移动端浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_product_images(self, product_url: str) -> List[ImageInfo]:
        """
        获取商品详情页的所有商品大图
        
        Args:
            product_url: 商品详情页URL
            
        Returns:
            List[ImageInfo]: 图片信息列表
            
        Raises:
            Exception: 当网络请求失败或解析失败时抛出异常
        """
        try:
            # 获取页面HTML内容
            html_content = self._fetch_page_content(product_url)
            
            # 解析HTML并提取图片信息
            images = self._extract_product_images(html_content, product_url)
            
            logger.info(f"成功获取到 {len(images)} 张商品图片")
            return images
            
        except Exception as e:
            logger.error(f"获取商品图片失败: {str(e)}")
            raise
    
    def get_product_image_urls(self, product_url: str) -> List[str]:
        """
        获取商品详情页的所有商品大图URLs（简化版本）
        
        Args:
            product_url: 商品详情页URL
            
        Returns:
            List[str]: 图片URL列表
        """
        images = self.get_product_images(product_url)
        return [img.url for img in images]
    
    def _fetch_page_content(self, url: str) -> str:
        """
        获取页面HTML内容
        
        Args:
            url: 页面URL
            
        Returns:
            str: HTML内容
            
        Raises:
            Exception: 当请求失败时抛出异常
        """
        last_exception = None
        
        for attempt in range(self.retry_count):
            try:
                logger.info(f"正在获取页面内容 (尝试 {attempt + 1}/{self.retry_count}): {url}")
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # 让requests自动处理编码
                response.encoding = response.apparent_encoding or 'utf-8'
                
                return response.text
                
            except Exception as e:
                last_exception = e
                logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                
                if attempt < self.retry_count - 1:
                    time.sleep(1)  # 重试前等待1秒
        
        raise Exception(f"获取页面内容失败，已重试 {self.retry_count} 次: {str(last_exception)}")
    
    def _extract_product_images(self, html_content: str, base_url: str) -> List[ImageInfo]:
        """
        从HTML内容中提取商品图片信息
        
        Args:
            html_content: HTML内容
            base_url: 基础URL，用于处理相对路径
            
        Returns:
            List[ImageInfo]: 图片信息列表
        """
        soup = BeautifulSoup(html_content, 'lxml')
        images = []
        
        # 方法1: 查找轮播图容器中的图片
        # 根据用户提供的HTML结构：<div class="custom-class tee-swiper-item"><img src="..."></div>
        swiper_images = soup.find_all('div', class_=re.compile(r'.*swiper.*item.*'))
        for div in swiper_images:
            img_tag = div.find('img')
            if img_tag and img_tag.get('src'):
                image_info = self._create_image_info(img_tag, base_url)
                if image_info:
                    images.append(image_info)
        
        # 方法2: 查找所有可能的商品图片容器
        # 查找包含商品图片的常见class名称
        image_containers = soup.find_all('div', class_=re.compile(r'.*(image|img|photo|pic|gallery).*', re.I))
        for container in image_containers:
            img_tags = container.find_all('img')
            for img_tag in img_tags:
                if img_tag.get('src'):
                    image_info = self._create_image_info(img_tag, base_url)
                    if image_info and not self._is_duplicate_image(image_info, images):
                        images.append(image_info)
        
        # 方法3: 直接查找所有img标签，过滤出商品图片
        all_img_tags = soup.find_all('img')
        for img_tag in all_img_tags:
            src = img_tag.get('src')
            if src and self._is_product_image(src):
                image_info = self._create_image_info(img_tag, base_url)
                if image_info and not self._is_duplicate_image(image_info, images):
                    images.append(image_info)
        
        # 方法4: 使用正则表达式从HTML源码中直接提取图片URL（适用于动态加载的页面）
        regex_images = self._extract_images_by_regex(html_content, base_url)
        for image_info in regex_images:
            if not self._is_duplicate_image(image_info, images):
                images.append(image_info)
        
        # 去重并排序
        unique_images = self._deduplicate_images(images)
        
        return unique_images
    
    def _create_image_info(self, img_tag, base_url: str) -> Optional[ImageInfo]:
        """
        从img标签创建ImageInfo对象
        
        Args:
            img_tag: BeautifulSoup的img标签对象
            base_url: 基础URL
            
        Returns:
            Optional[ImageInfo]: 图片信息对象，如果创建失败返回None
        """
        try:
            src = img_tag.get('src')
            if not src:
                return None
            
            # 处理相对URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(base_url, src)
            
            # 获取图片信息
            alt_text = img_tag.get('alt', '')
            width = self._parse_dimension(img_tag.get('width'))
            height = self._parse_dimension(img_tag.get('height'))
            
            # 从URL推断图片格式
            format_match = re.search(r'\.(jpg|jpeg|png|webp|gif)(?:\?|$)', src.lower())
            image_format = format_match.group(1) if format_match else 'jpg'
            
            # 从URL推断尺寸类型
            size_type = self._infer_size_type(src)
            
            return ImageInfo(
                url=src,
                alt_text=alt_text,
                width=width,
                height=height,
                format=image_format,
                size_type=size_type
            )
            
        except Exception as e:
            logger.warning(f"创建图片信息失败: {str(e)}")
            return None
    
    def _parse_dimension(self, dimension_str: Optional[str]) -> Optional[int]:
        """
        解析尺寸字符串为整数
        
        Args:
            dimension_str: 尺寸字符串
            
        Returns:
            Optional[int]: 尺寸整数，解析失败返回None
        """
        if not dimension_str:
            return None
        
        try:
            # 移除px等单位
            clean_str = re.sub(r'[^0-9]', '', str(dimension_str))
            return int(clean_str) if clean_str else None
        except (ValueError, TypeError):
            return None
    
    def _infer_size_type(self, url: str) -> str:
        """
        从URL推断图片尺寸类型
        
        Args:
            url: 图片URL
            
        Returns:
            str: 尺寸类型
        """
        url_lower = url.lower()
        
        if any(keyword in url_lower for keyword in ['thumb', 'small', 's_']):
            return 'thumbnail'
        elif any(keyword in url_lower for keyword in ['medium', 'm_']):
            return 'medium'
        elif any(keyword in url_lower for keyword in ['large', 'l_', 'big']):
            return 'large'
        elif re.search(r'/w/\d+', url) or re.search(r'w_\d+', url):
            # 检查是否有宽度参数，通常大尺寸图片会有较大的宽度值
            width_match = re.search(r'(?:w[/_])(\d+)', url)
            if width_match:
                width = int(width_match.group(1))
                if width >= 750:
                    return 'large'
                elif width >= 400:
                    return 'medium'
                else:
                    return 'thumbnail'
        
        return 'original'
    
    def _is_product_image(self, src: str) -> bool:
        """
        判断是否为商品图片
        
        Args:
            src: 图片URL
            
        Returns:
            bool: 是否为商品图片
        """
        # 过滤掉明显不是商品图片的URL
        exclude_patterns = [
            r'logo',
            r'icon',
            r'avatar',
            r'thumb',
            r'banner',
            r'/ad[_-]',  # 修复：只匹配路径中的ad，避免误匹配upload等词
            r'advertisement',
            r'placeholder',
            r'loading',
            r'default',
            r'skeleton',  # 骨架屏图片
            r'\.(svg)$',  # 通常logo和图标是SVG格式
        ]
        
        src_lower = src.lower()
        
        # 检查排除模式
        for pattern in exclude_patterns:
            if re.search(pattern, src_lower):
                return False
        
        # 检查是否包含有赞CDN域名或常见图片格式
        include_patterns = [
            r'yzcdn\.cn',  # 有赞CDN (包括img01.yzcdn.cn等子域名)
            r'youzan',     # 有赞相关
        ]
        
        # 必须包含有赞相关域名
        has_youzan_domain = any(re.search(pattern, src_lower) for pattern in include_patterns)
        
        # 检查是否有图片格式
        has_image_format = re.search(r'\.(jpg|jpeg|png|webp)', src_lower)
        
        # 检查是否是商品图片路径（通常在upload_files目录下）
        is_upload_file = 'upload_files' in src_lower
        
        return has_youzan_domain and has_image_format and is_upload_file
    
    def _is_duplicate_image(self, new_image: ImageInfo, existing_images: List[ImageInfo]) -> bool:
        """
        检查是否为重复图片
        
        Args:
            new_image: 新图片信息
            existing_images: 已存在的图片列表
            
        Returns:
            bool: 是否重复
        """
        for existing in existing_images:
            # 比较URL（去除参数）
            new_url_base = new_image.url.split('?')[0]
            existing_url_base = existing.url.split('?')[0]
            
            if new_url_base == existing_url_base:
                return True
        
        return False
    
    def _extract_images_by_regex(self, html_content: str, base_url: str) -> List[ImageInfo]:
        """
        使用正则表达式从HTML源码中提取图片URL
        
        Args:
            html_content: HTML内容
            base_url: 基础URL
            
        Returns:
            List[ImageInfo]: 图片信息列表
        """
        images = []
        
        # 查找所有图片URL（包括相对协议URL）
        patterns = [
            r'https?://[^\s\"\'>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"\'>]*)?',  # 完整URL
            r'//[^\s\"\'>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"\'>]*)?'  # 相对协议URL
        ]
        
        all_urls = set()
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            all_urls.update(matches)
        
        full_urls = list(all_urls)
        
        for url in full_urls:
            # 处理相对协议URL
            if url.startswith('//'):
                url = 'https:' + url
            
            # 过滤出图片URL
            if re.search(r'\.(jpg|jpeg|png|webp)(?:\?|$)', url, re.IGNORECASE):
                if self._is_product_image(url):
                    # 创建ImageInfo对象
                    format_match = re.search(r'\.(jpg|jpeg|png|webp)(?:\?|$)', url.lower())
                    image_format = format_match.group(1) if format_match else 'jpg'
                    
                    size_type = self._infer_size_type(url)
                    
                    image_info = ImageInfo(
                        url=url,
                        alt_text="",
                        format=image_format,
                        size_type=size_type
                    )
                    images.append(image_info)
        
        return images
    
    def _deduplicate_images(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """
        去重图片列表
        
        Args:
            images: 图片列表
            
        Returns:
            List[ImageInfo]: 去重后的图片列表
        """
        seen_urls = set()
        unique_images = []
        
        for image in images:
            url_base = image.url.split('?')[0]
            if url_base not in seen_urls:
                seen_urls.add(url_base)
                unique_images.append(image)
        
        # 按尺寸类型排序，优先显示大图
        size_priority = {'large': 0, 'original': 1, 'medium': 2, 'thumbnail': 3}
        unique_images.sort(key=lambda x: size_priority.get(x.size_type, 4))
        
        return unique_images
    
    def get_high_quality_images(self, product_url: str) -> List[ImageInfo]:
        """
        获取高质量商品图片（过滤掉缩略图）
        
        Args:
            product_url: 商品详情页URL
            
        Returns:
            List[ImageInfo]: 高质量图片信息列表
        """
        all_images = self.get_product_images(product_url)
        
        # 过滤出高质量图片
        high_quality_images = [
            img for img in all_images 
            if img.size_type in ['large', 'original', 'medium']
        ]
        
        return high_quality_images
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 便捷函数
def get_youzan_product_images(product_url: str, high_quality_only: bool = True) -> List[str]:
    """
    便捷函数：获取有赞商品图片URLs
    
    Args:
        product_url: 商品详情页URL
        high_quality_only: 是否只返回高质量图片
        
    Returns:
        List[str]: 图片URL列表
    """
    with YouZanProductScraper() as scraper:
        if high_quality_only:
            images = scraper.get_high_quality_images(product_url)
        else:
            images = scraper.get_product_images(product_url)
        
        return [img.url for img in images]


if __name__ == "__main__":
    # 测试代码
    test_url = "https://shop18443051.m.youzan.com/wscgoods/detail/3ngm8yx62rws3ji"
    
    try:
        # 使用上下文管理器
        with YouZanProductScraper() as scraper:
            images = scraper.get_product_images(test_url)
            
            print(f"\n找到 {len(images)} 张商品图片:")
            for i, img in enumerate(images, 1):
                print(f"{i}. {img.url}")
                print(f"   尺寸类型: {img.size_type}, 格式: {img.format}")
                if img.alt_text:
                    print(f"   描述: {img.alt_text}")
                print()
        
        # 使用便捷函数
        print("\n使用便捷函数获取高质量图片:")
        urls = get_youzan_product_images(test_url, high_quality_only=True)
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")