import pandas as pd

df = pd.read_csv('output/600967.SH_daily_data.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date')

print('=== 基础统计 ===')
print(f'交易日数: {len(df)}')
print(f'起始日期: {df["trade_date"].min().strftime("%Y-%m-%d")}')
print(f'结束日期: {df["trade_date"].max().strftime("%Y-%m-%d")}')
print(f'起始收盘价: {df["close"].iloc[0]:.2f}')
print(f'结束收盘价: {df["close"].iloc[-1]:.2f}')
print(f'区间涨跌幅: {(df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0] * 100:.2f}%')
print(f'最高价: {df["high"].max():.2f} (日期: {df.loc[df["high"].idxmax(), "trade_date"].strftime("%Y-%m-%d")})')
print(f'最低价: {df["low"].min():.2f} (日期: {df.loc[df["low"].idxmin(), "trade_date"].strftime("%Y-%m-%d")})')
print(f'平均收盘价: {df["close"].mean():.2f}')
print(f'日均成交量(手): {df["vol"].mean():.0f}')
print(f'日均成交额(千元): {df["amount"].mean():.0f}')
print(f'日均成交额(亿元): {df["amount"].mean() / 100000:.2f}')
print(f'上涨天数: {len(df[df["close"] > df["open"]])}')
print(f'下跌天数: {len(df[df["close"] < df["open"]])}')
print(f'平盘天数: {len(df[df["close"] == df["open"]])}')
print(f'上涨占比: {len(df[df["close"] > df["open"]]) / len(df) * 100:.1f}%')
print(f'价格波动率: {df["close"].std() / df["close"].mean() * 100:.2f}%')

print()
print('=== 年度统计 ===')
df['year'] = df['trade_date'].dt.year
for year in sorted(df['year'].unique()):
    yd = df[df['year'] == year]
    start_p = yd['close'].iloc[0]
    end_p = yd['close'].iloc[-1]
    print(f'{year}: 开盘{start_p:.2f} 收盘{end_p:.2f} 涨跌{(end_p-start_p)/start_p*100:+.2f}% 天数{len(yd)} 上涨{len(yd[yd["close"] > yd["open"]])} 下跌{len(yd[yd["close"] < yd["open"]])} 日均成交{yd["vol"].mean():.0f}')

print()
print('=== 成交量峰值检查 ===')
print(f'最大单日成交量: {df["vol"].max():.0f} 手 ({df.loc[df["vol"].idxmax(), "trade_date"].strftime("%Y-%m-%d")})')
print(f'最大单日成交额: {df["amount"].max():.0f} 千元 = {df["amount"].max() / 100000:.2f} 亿元')
print(f'最小单日成交量: {df["vol"].min():.0f} 手 ({df.loc[df["vol"].idxmin(), "trade_date"].strftime("%Y-%m-%d")})')
print(f'最小单日成交额: {df["amount"].min():.0f} 千元 = {df["amount"].min() / 100000:.2f} 亿元')

print()
print('=== 近期数据检查 ===')
print(df[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']].tail(10).to_string(index=False))
