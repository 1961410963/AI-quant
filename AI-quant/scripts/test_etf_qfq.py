import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

os.makedirs('output', exist_ok=True)

end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')

# 试试东方财富的ETF历史行情，看有没有前复权选项
print('尝试东方财富ETF接口（华夏黄金ETF 159562）...')
try:
    # 先查一下symbol
    df_search = ak.fund_etf_spot_em()
    target = df_search[df_search['代码'].str.contains('159562')]
    print(f'搜索结果: {target[["代码", "名称"]].to_dict("records")}')
    
    # 获取历史行情 - 东方财富接口
    df1 = ak.fund_etf_hist_em(symbol='159562', period='daily', start_date=start_date, end_date=end_date, adjust='qfq')
    if df1 is not None and not df1.empty:
        print(f'列名: {df1.columns.tolist()}')
        print(f'行数: {len(df1)}')
        print(df1.head(3))
        print(df1.tail(3))
    else:
        print('返回为空')
except Exception as e:
    print(f'失败: {e}')

print()
print('尝试易方达红利低波ETF(563020)...')
try:
    df2 = ak.fund_etf_hist_em(symbol='563020', period='daily', start_date=start_date, end_date=end_date, adjust='qfq')
    if df2 is not None and not df2.empty:
        print(f'行数: {len(df2)}')
        print(df2.head(3))
        print(df2.tail(3))
    else:
        print('返回为空')
except Exception as e:
    print(f'失败: {e}')
