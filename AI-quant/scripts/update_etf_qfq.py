import akshare as ak
import pandas as pd
import json
import re
from datetime import datetime, timedelta
import os

os.makedirs('output', exist_ok=True)

end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')

def fetch_etf_qfq(symbol, ts_code):
    df = ak.fund_etf_hist_em(symbol=symbol, period='daily', start_date=start_date, end_date=end_date, adjust='qfq')
    if df is None or df.empty:
        return None
    df = df.rename(columns={
        '日期': 'trade_date', '开盘': 'open', '收盘': 'close',
        '最高': 'high', '最低': 'low', '成交量': 'vol', '成交额': 'amount'
    })
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    csv_path = f'output/{ts_code}_daily_data.csv'
    df.to_csv(csv_path, index=False)
    print(f'{ts_code}: {len(df)}条, {df["trade_date"].min().strftime("%Y-%m-%d")} ~ {df["trade_date"].max().strftime("%Y-%m-%d")}')
    return df

print('获取华夏黄金ETF(159562)前复权数据...')
df1 = fetch_etf_qfq('159562', '159562.SZ')

print('获取易方达红利低波ETF(563020)前复权数据...')
df2 = fetch_etf_qfq('563020', '563020.SH')

# 读取600967数据（已有）
df0 = pd.read_csv('output/600967.SH_daily_data.csv')
df0['trade_date'] = pd.to_datetime(df0['trade_date'])
df0 = df0.sort_values('trade_date').reset_index(drop=True)
print(f'600967.SH: {len(df0)}条, {df0["trade_date"].min().strftime("%Y-%m-%d")} ~ {df0["trade_date"].max().strftime("%Y-%m-%d")}')

# 转为JS数组格式
def df_to_js_array(df):
    rows = []
    for _, row in df.iterrows():
        rows.append([
            row['trade_date'].strftime('%Y-%m-%d'),
            round(float(row['open']), 2),
            round(float(row['high']), 2),
            round(float(row['low']), 2),
            round(float(row['close']), 2),
            round(float(row['vol']), 2) if 'vol' in df.columns else 0,
            round(float(row['amount']), 2) if 'amount' in df.columns else 0
        ])
    return rows

data_600967 = df_to_js_array(df0)
data_159562 = df_to_js_array(df1)
data_563020 = df_to_js_array(df2)

# 读取HTML并替换数据
with open('stock-indicator-visualizer.html', 'r', encoding='utf-8') as f:
    html = f.read()

data_block = f"""const RAW_DATA = {{
    '600967.SH': {json.dumps(data_600967, ensure_ascii=False)},
    '159562.SZ': {json.dumps(data_159562, ensure_ascii=False)},
    '563020.SH': {json.dumps(data_563020, ensure_ascii=False)}
}};"""

pattern = r"const RAW_DATA = \{[\s\S]*?\};"
new_html = re.sub(pattern, data_block, html)

with open('stock-indicator-visualizer.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('前复权ETF数据已嵌入HTML文件')
