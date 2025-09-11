import pandas as pd

# 读取失败场景测试的Excel文件
df = pd.read_excel('output/test_failure_scenarios')

print('失败场景测试结果:')
print('数据行数:', len(df))

print('\nfinal_status分布:')
print(df['final_status'].value_counts())

print('\nscenario_validation分布:')
print(df['scenario_validation'].value_counts())

print('\ncontent_validation分布:')
print(df['content_validation'].value_counts())

print('\nprocessing_stage分布:')
print(df['processing_stage'].value_counts())

print('\n详细数据:')
for i, row in df.iterrows():
    print(f'{i+1}. 场景: {row["scenario_description"]}')
    print(f'   场景验证: {row["scenario_validation"]} - {row["scenario_validation_reason"]}')
    print(f'   文案验证: {row["content_validation"]} - {row["content_validation_feedback"]}')
    print(f'   最终状态: {row["final_status"]}')
    if row['content_generation_error']:
        print(f'   文案生成错误: {row["content_generation_error"]}')
    if row['product_recommendation_error']:
        print(f'   商品推荐错误: {row["product_recommendation_error"]}')
    print()