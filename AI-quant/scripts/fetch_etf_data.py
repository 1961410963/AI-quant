import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

os.makedirs('output', exist_ok=True)

end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')

# 华夏黄金ETF 159562
print('获取华夏黄金ETF(159562)...')
try:
    df1 = ak.fund_etf_hist_sina(symbol='sz159562')
    if df1 is not None and not df1.empty:
        df1 = df1.rename(columns={
            'date': 'trade_date', 'open': 'open', 'high': 'high',
            'low': 'low', 'close': 'close', 'volume': 'vol'
        })
        df1['trade_date'] = pd.to_datetime(df1['trade_date'])
        df1 = df1[(df1['trade_date'] >= start_date) & (df1['trade_date'] <= end_date)]
        df1 = df1.sort_values('trade_date').reset_index(drop=True)
        df1['amount'] = 0
        df1.to_csv('output/159562.SZ_daily_data.csv', index=False)
        print(f'华夏黄金ETF: {len(df1)}条, {df1["trade_date"].min()} ~ {df1["trade_date"].max()}')
    else:
        print('返回为空')
except Exception as e:
    print(f'失败: {e}')

# 易方达红利低波ETF 563020
print('获取易方达红利低波ETF(563020)...')
try:
    df2 = ak.fund_etf_hist_sina(symbol='sh563020')
    if df2 is not None and not df2.empty:
        df2 = df2.rename(columns={
            'date': 'trade_date', 'open': 'open', 'high': 'high',
            'low': 'low', 'close': 'close', 'volume': 'vol'
        })
        df2['trade_date'] = pd.to_datetime(df2['trade_date'])
        df2 = df2[(df2['trade_date'] >= start_date) & (df2['trade_date'] <= end_date)]
        df2 = df2.sort_values('trade_date').reset_index(drop=True)
        df2['amount'] = 0
        df2.to_csv('output/563020.SH_daily_data.csv', index=False)
        print(f'易方达红利低波ETF: {len(df2)}条, {df2["trade_date"].min()} ~ {df2["trade_date"].max()}')
    else:
        print('返回为空')
except Exception as e:
    print(f'失败: {e}')

print('完成')
