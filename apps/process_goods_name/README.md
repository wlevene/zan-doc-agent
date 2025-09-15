# 商品数据处理工具

这是一个用于处理 Excel 商品数据的命令行工具，可以过滤和清理商品名称。

## 功能特性

- 复制并处理 Excel 文件
- 根据关键词过滤商品行，默认清除包含“员工,测试”这两个关键词的行
- 清理商品名称（移除【】中的内容）
- 支持 AI 处理商品名称（通过 Dify API）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 命令行用法

### 基本用法

```bash
python process_goods.py goods.xlsx
```

### 完整参数用法

```bash
python process_goods.py goods.xlsx \
  --output goods_processed.xlsx \
  --filter "员工,测试,样品" \
  --column "商品名称"
```

## 参数说明

- `file_path` (必需): 输入的 Excel 文件路径
- `--output, -o`: 输出文件路径（可选，默认为输入文件名加 "_processed" 后缀）
- `--filter, -f`: 过滤关键词，用逗号分隔（默认: "员工, 测试"）
- `--column, -c`: 商品名称列名（默认: "商品名称"）

## 处理流程

1. 复制原始文件到新文件
2. 在新文件中创建名为 "sheet1" 的工作表
3. 复制原始数据到新工作表
4. 根据过滤关键词清除相关行
5. 清理商品名称（移除【】内容）
6. 可选：通过 Dify API 进行 AI 处理
7. 保存处理后的文件

## 示例

处理 goods.xlsx 文件，过滤包含"员工"和"测试"的行：

```bash
python process_goods.py goods.xlsx --filter "员工,测试"
```

输出文件将保存为 `goods_processed.xlsx`。