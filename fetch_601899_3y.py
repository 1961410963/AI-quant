import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

os.makedirs('output', exist_ok=True)
end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')

symbol = '601899'
ts_code = '601899.SH'

print(f'获取紫金矿业({ts_code})近三年前复权数据...')
print(f'时间范围: {start_date} ~ {end_date}')

try:
    df = ak.stock_zh_a_daily(symbol=f'sh{symbol}', adjust='qfq')
    if df is not None and not df.empty:
        df = df.rename(columns={
            'date': 'trade_date', 'open': 'open', 'close': 'close',
            'high': 'high', 'low': 'low', 'volume': 'vol'
        })
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)]
        df = df.sort_values('trade_date').reset_index(drop=True)
        if 'amount' not in df.columns:
            df['amount'] = df['open'] * df['vol'] / 100
        df.to_csv(f'output/{ts_code}_daily_data.csv', index=False)
        r = df['trade_date']
        print(f'{ts_code}: {len(df)}条, {r.min().strftime("%Y-%m-%d")} ~ {r.max().strftime("%Y-%m-%d")}')
        print(f'最新收盘价: {df.iloc[-1]["close"]}')
    else:
        print('返回为空')
except Exception as e:
    print(f'失败 - {str(e)}')

print('完成')
