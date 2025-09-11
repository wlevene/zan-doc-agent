import pandas as pd

# 读取Excel文件
df = pd.read_excel('output/wellness_content_20250911_175016.xlsx')

print('Excel文件列名:')
print(df.columns.tolist())
print('\n数据行数:', len(df))

print('\n检查scenario_validation列:')
print(df['scenario_validation'].value_counts())

print('\n检查content_validation列:')
print(df['content_validation'].value_counts())

print('\n检查processing_stage列:')
print(df['processing_stage'].value_counts())

print('\n检查是否有错误信息:')
print('content_generation_error非空行数:', df['content_generation_error'].notna().sum())
print('product_recommendation_error非空行数:', df['product_recommendation_error'].notna().sum())

print('\n查看所有场景描述:')
for i, row in df.iterrows():
    print(f'{i+1}. {row["scenario_description"]}')

print('\n查看scenario_validation_reason列:')
for i, row in df.iterrows():
    print(f'{i+1}. {row["scenario_validation_reason"]}')

print('\n查看content_validation_feedback列:')
for i, row in df.iterrows():
    print(f'{i+1}. {row["content_validation_feedback"]}')