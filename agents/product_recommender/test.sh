#!/bin/bash

# 商品推荐器测试脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 获取项目根目录（向上两级）
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 设置 PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 商品推荐器测试 ===${NC}"
echo -e "${YELLOW}项目根目录: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}PYTHONPATH: $PYTHONPATH${NC}"
echo ""

# 切换到脚本目录
cd "$SCRIPT_DIR"

# 运行测试
echo -e "${BLUE}开始运行商品推荐器测试...${NC}"
echo ""

if python3 test_product_recommender.py; then
    echo ""
    echo -e "${GREEN}✅ 商品推荐器测试完成${NC}"
else
    echo ""
    echo -e "${RED}❌ 商品推荐器测试失败${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 所有测试执行完毕${NC}"