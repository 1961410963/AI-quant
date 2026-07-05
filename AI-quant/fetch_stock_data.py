import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os
import time

os.makedirs('output', exist_ok=True)
end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')

# 新浪源前复权
def fetch_sina_qfq(symbol, ts_code, max_retry=3):
    for attempt in range(max_retry):
        try:
            # 新浪源：sz或sh前缀
            sina_symbol = symbol  # 6位代码
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
                df.to_csv(f'output/{ts_code}_daily_data.csv', index=False)
                r = df['trade_date']
                print(f'{ts_code}: {len(df)}条, {r.min().strftime("%Y-%m-%d")} ~ {r.max().strftime("%Y-%m-%d")}')
                return df
            else:
                print(f'{ts_code}: 返回为空')
        except Exception as e:
            print(f'{ts_code}: 第{attempt+1}次失败 - {str(e)[:100]}')
            if attempt < max_retry - 1:
                time.sleep(5)
    return None

print('获取恒力石化(600346)前复权数据...')
fetch_sina_qfq('600346', '600346.SH')

time.sleep(3)

print('获取中材科技(002080)前复权数据...')
fetch_sina_qfq('002080', '002080.SZ')

print('完成')
