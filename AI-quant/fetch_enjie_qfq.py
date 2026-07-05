import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

os.makedirs('output', exist_ok=True)
end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')

def fetch_sina_qfq(symbol, ts_code):
    df = ak.stock_zh_a_daily(symbol=f'sh{symbol}' if symbol.startswith('6') else f'sz{symbol}', adjust='qfq')
    if df is not None and not df.empty:
        df = df.rename(columns={
            'date': 'trade_date', 'open': 'open', 'close': 'close',
            'high': 'high', 'low': 'low', 'volume': 'vol'
        })
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)]
        df = df.sort_values('trade_date').reset_index(drop=True)
        if 'amount' not in df.columns:
            df['amount'] = 0
        df['ts_code'] = ts_code
        df.to_csv(f'output/{ts_code}_daily_data.csv', index=False)
        r = df['trade_date']
        print(f'{ts_code}: {len(df)}条, {r.min().strftime("%Y-%m-%d")} ~ {r.max().strftime("%Y-%m-%d")}')
        return df
    else:
        print(f'{ts_code}: 返回为空')
        return None

print('获取恩捷股份(002812)前复权数据...')
df = fetch_sina_qfq('002812', '002812.SZ')

if df is not None:
    print('\n最新5条数据：')
    print(df.tail(5)[['trade_date', 'open', 'close', 'high', 'low', 'vol']].to_string())
    print(f'\n最新收盘价: {df["close"].iloc[-1]:.2f}元')
    print(f'区间涨跌幅: {((df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0] * 100):.2f}%')
