import pandas as pd

df = pd.read_csv('data/enhanced_job_titles.csv')
print(f'Job titles rows: {len(df)}')
print(f'Columns: {list(df.columns)}')
if 'category' in df.columns:
    print(f'Categories: {df.category.unique()}')
else:
    print('No category column')
