import pandas as pd
import json
import re

def df_to_js_array(df):
    rows = []
    for _, row in df.iterrows():
        rows.append([
            row['trade_date'].strftime('%Y-%m-%d') if hasattr(row['trade_date'], 'strftime') else str(row['trade_date'])[:10],
            round(float(row['open']), 2),
            round(float(row['high']), 2),
            round(float(row['low']), 2),
            round(float(row['close']), 2),
            round(float(row['vol']), 2) if 'vol' in df.columns else 0,
            round(float(row['amount']), 2) if 'amount' in df.columns else 0
        ])
    return rows

stocks = [
    ('600967.SH', 'output/600967.SH_daily_data.csv'),
    ('600346.SH', 'output/600346.SH_daily_data.csv'),
    ('002080.SZ', 'output/002080.SZ_daily_data.csv'),
    ('002812.SZ', 'output/002812.SZ_daily_data.csv'),
    ('601899.SH', 'output/601899.SH_daily_data.csv'),
    ('159562.SZ', 'output/159562.SZ_daily_data.csv'),
    ('563020.SH', 'output/563020.SH_daily_data.csv'),
]

all_data = {}
for code, path in stocks:
    df = pd.read_csv(path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    all_data[code] = df_to_js_array(df)
    print(f'{code}: {len(all_data[code])}条')

with open('stock-indicator-visualizer.html', 'r', encoding='utf-8') as f:
    html = f.read()

data_entries = ',\n    '.join(f"'{code}': {json.dumps(data, ensure_ascii=False)}" for code, data in all_data.items())
data_block = f"const RAW_DATA = {{\n    {data_entries}\n}};"

pattern = r"const RAW_DATA = \{[\s\S]*?\};"
new_html = re.sub(pattern, data_block, html)

with open('stock-indicator-visualizer.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'可视化工具数据已更新，共 {len(all_data)} 只标的')
