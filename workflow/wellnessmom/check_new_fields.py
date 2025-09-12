import pandas as pd

# 读取最新生成的Excel文件
df = pd.read_excel('output/wellness_content_20250911_185941.xlsx')

print('Excel文件列名:')
print(df.columns.tolist())

print('\n数据行数:', len(df))

print('\n新增字段检查:')
if 'product_goods_list' in df.columns:
    print('\nproduct_goods_list字段内容:')
    for i, value in enumerate(df['product_goods_list'].head()):
        print(f'{i+1}. {value}')
else:
    print('product_goods_list字段不存在')

if 'product_recommendation_reason' in df.columns:
    print('\nproduct_recommendation_reason字段内容:')
    for i, value in enumerate(df['product_recommendation_reason'].head()):
        print(f'{i+1}. {value}')
else:
    print('product_recommendation_reason字段不存在')

print('\nrecommended_products字段内容（前3条）:')
for i, value in enumerate(df['recommended_products'].head(3)):
    print(f'{i+1}. {value}')
    print()