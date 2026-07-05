import pandas as pd
import json
import re

# 读取三个数据文件
def csv_to_js_array(csv_path, ts_code):
    df = pd.read_csv(csv_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    rows = []
    for _, row in df.iterrows():
        rows.append([
            row['trade_date'].strftime('%Y-%m-%d'),
            round(row['open'], 2),
            round(row['high'], 2),
            round(row['low'], 2),
            round(row['close'], 2),
            round(row['vol'], 2) if 'vol' in df.columns else 0,
            round(row['amount'], 2) if 'amount' in df.columns else 0
        ])
    return rows

data_600967 = csv_to_js_array('output/600967.SH_daily_data.csv', '600967.SH')
data_159562 = csv_to_js_array('output/159562.SZ_daily_data.csv', '159562.SZ')
data_563020 = csv_to_js_array('output/563020.SH_daily_data.csv', '563020.SH')

print(f'600967: {len(data_600967)}条')
print(f'159562: {len(data_159562)}条')
print(f'563020: {len(data_563020)}条')

# 读取现有HTML
with open('stock-indicator-visualizer.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 替换数据块
# 找到 '600967.SH': [ ... ] 并替换为包含所有数据的新版本
# 同时替换空的 159562 和 563020 数据

# 生成新的数据块
data_block = f"""const RAW_DATA = {{
    '600967.SH': {json.dumps(data_600967, ensure_ascii=False)},
    '159562.SZ': {json.dumps(data_159562, ensure_ascii=False)},
    '563020.SH': {json.dumps(data_563020, ensure_ascii=False)}
}};"""

# 使用正则替换整个 RAW_DATA 块
pattern = r"const RAW_DATA = \{[\s\S]*?\};"
new_html = re.sub(pattern, data_block, html)

with open('stock-indicator-visualizer.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('ETF数据已嵌入HTML文件')
