import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import tushare as ts

os.makedirs('output', exist_ok=True)

end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')

etfs = [
    ('159562', '159562.SZ', '华夏黄金ETF'),
    ('563020', '563020.SH', '易方达红利低波ETF'),
]

pro = ts.pro_api()

for symbol, ts_code, name in etfs:
    print(f'\n=== {name}({ts_code}) ===')
    df = None

    # 方案A: 东方财富 stock_zh_a_hist
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period='daily',
                                start_date=start_date, end_date=end_date, adjust='qfq')
        if df is not None and not df.empty:
            df = df.rename(columns={
                '日期': 'trade_date', '开盘': 'open', '最高': 'high',
                '最低': 'low', '收盘': 'close', '成交量': 'vol', '成交额': 'amount'
            })
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.sort_values('trade_date').reset_index(drop=True)
            df = df[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']]
            print(f'[东方财富qfq] {len(df)}条, {df["trade_date"].min().strftime("%Y-%m-%d")} ~ {df["trade_date"].max().strftime("%Y-%m-%d")}')
            print(f'最新收盘: {df["close"].iloc[-1]:.4f}')
    except Exception as e:
        print(f'[东方财富] 失败: {str(e)[:100]}')

    # 方案B: 新浪源原始数据 + Tushare复权因子手动前复权
    if df is None or df.empty:
        print(f'[方案B] 使用新浪源原始数据 + Tushare复权因子')
        try:
            sina_symbol = f'sz{symbol}' if symbol.startswith('0') or symbol.startswith('1') else f'sh{symbol}'
            df_raw = ak.fund_etf_hist_sina(symbol=sina_symbol)
            if df_raw is not None and not df_raw.empty:
                df_raw = df_raw.rename(columns={
                    'date': 'trade_date', 'open': 'open', 'high': 'high',
                    'low': 'low', 'close': 'close', 'volume': 'vol'
                })
                df_raw['trade_date'] = pd.to_datetime(df_raw['trade_date'])
                df_raw = df_raw[(df_raw['trade_date'] >= start_date) & (df_raw['trade_date'] <= end_date)]
                df_raw = df_raw.sort_values('trade_date').reset_index(drop=True)
                if 'amount' not in df_raw.columns:
                    df_raw['amount'] = 0
                print(f'[新浪源] 原始数据: {len(df_raw)}条')
                print(f'  原始最新收盘: {df_raw["close"].iloc[-1]:.4f}')

                # 获取复权因子
                print(f'  等待65秒获取复权因子...')
                time.sleep(65)
                try:
                    adj = pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
                    if adj is not None and not adj.empty:
                        adj['trade_date'] = pd.to_datetime(adj['trade_date'])
                        adj = adj.sort_values('trade_date').reset_index(drop=True)
                        print(f'  复权因子: {len(adj)}条, 最新={adj["adj_factor"].iloc[-1]:.6f}, 最早={adj["adj_factor"].iloc[0]:.6f}')

                        df_raw = df_raw.merge(adj[['trade_date', 'adj_factor']], on='trade_date', how='left')
                        df_raw['adj_factor'] = df_raw['adj_factor'].fillna(method='ffill')
                        latest_factor = df_raw['adj_factor'].iloc[-1]
                        df_raw['open'] = df_raw['open'] * df_raw['adj_factor'] / latest_factor
                        df_raw['high'] = df_raw['high'] * df_raw['adj_factor'] / latest_factor
                        df_raw['low'] = df_raw['low'] * df_raw['adj_factor'] / latest_factor
                        df_raw['close'] = df_raw['close'] * df_raw['adj_factor'] / latest_factor
                        df_raw = df_raw.drop(columns=['adj_factor'])
                        print(f'  前复权最新收盘: {df_raw["close"].iloc[-1]:.4f}')
                    else:
                        print(f'  无复权因子（ETF可能无分红），使用原始数据')
                except Exception as e:
                    print(f'  复权因子获取失败: {str(e)[:150]}，使用原始数据')

                df = df_raw[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']]
            else:
                print(f'[新浪源] 返回为空')
        except Exception as e:
            print(f'[新浪源] 失败: {str(e)[:150]}')

    if df is not None and not df.empty:
        df.to_csv(f'output/{ts_code}_daily_data.csv', index=False)
        print(f'已保存: output/{ts_code}_daily_data.csv ({len(df)}条)')
    else:
        print(f'{name}: 所有方案均失败')

    time.sleep(3)

print('\n完成')
