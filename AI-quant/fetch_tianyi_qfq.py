import pandas as pd
import akshare as ak

stock_code = '300504'
output_file = f'output/{stock_code}.SZ_daily_data.csv'

print(f'=== 获取 {stock_code}.SZ 天邑股份 前复权数据 ===')

df = ak.stock_zh_a_hist(symbol=stock_code, period='daily', start_date='20230709', end_date='20260709', adjust='qfq')

print('返回列名:', df.columns.tolist())
print('前3行:')
print(df.head(3).to_string())
print()

df = df.reset_index(drop=True)

df = df[['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']]
df.rename(columns={'日期': 'trade_date', '开盘': 'open', '最高': 'high', '最低': 'low', '收盘': 'close', '成交量': 'vol', '成交额': 'amount'}, inplace=True)

df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)

print(f'数据量: {len(df)}条')
print(f'时间范围: {df["trade_date"].min().strftime("%Y-%m-%d")} ~ {df["trade_date"].max().strftime("%Y-%m-%d")}')

df.to_csv(output_file, index=False)
print(f'\n数据已保存: {output_file}')
