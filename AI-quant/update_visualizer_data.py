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

df0 = pd.read_csv('output/600967.SH_daily_data.csv')
df0['trade_date'] = pd.to_datetime(df0['trade_date'])
df0 = df0.sort_values('trade_date').reset_index(drop=True)
data_600967 = df_to_js_array(df0)
print(f'600967.SH: {len(data_600967)}条')

df1 = pd.read_csv('output/600346.SH_daily_data.csv')
df1['trade_date'] = pd.to_datetime(df1['trade_date'])
df1 = df1.sort_values('trade_date').reset_index(drop=True)
data_600346 = df_to_js_array(df1)
print(f'600346.SH: {len(data_600346)}条')

df2 = pd.read_csv('output/002080.SZ_daily_data.csv')
df2['trade_date'] = pd.to_datetime(df2['trade_date'])
df2 = df2.sort_values('trade_date').reset_index(drop=True)
data_002080 = df_to_js_array(df2)
print(f'002080.SZ: {len(data_002080)}条')

with open('stock-indicator-visualizer.html', 'r', encoding='utf-8') as f:
    html = f.read()

data_block = f"""const RAW_DATA = {{
    '600967.SH': {json.dumps(data_600967, ensure_ascii=False)},
    '600346.SH': {json.dumps(data_600346, ensure_ascii=False)},
    '002080.SZ': {json.dumps(data_002080, ensure_ascii=False)}
}};"""

pattern = r"const RAW_DATA = \{[\s\S]*?\};"
new_html = re.sub(pattern, data_block, html)

with open('stock-indicator-visualizer.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('可视化工具数据已更新')
