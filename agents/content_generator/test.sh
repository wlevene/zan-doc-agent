#!/bin/bash
# ContentGenerator Agent 测试脚本
# 用于运行当前目录下的 test_content_generator.py

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 获取项目根目录（向上两级）
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 设置PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ContentGenerator Agent 测试 ===${NC}"
echo -e "${YELLOW}脚本目录: $SCRIPT_DIR${NC}"
echo -e "${YELLOW}项目根目录: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}PYTHONPATH: $PYTHONPATH${NC}"
echo ""

# 切换到脚本所在目录
cd "$SCRIPT_DIR"

# 运行测试
echo -e "${BLUE}正在运行 test_content_generator.py...${NC}"
echo "----------------------------------------"

if python3 test_content_generator.py; then
    echo ""
    echo -e "${GREEN}✓ ContentGenerator 测试完成！${NC}"
else
    echo ""
    echo -e "${RED}✗ ContentGenerator 测试失败！${NC}"
    exit 1
fi