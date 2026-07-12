import pandas as pd
import numpy as np

df = pd.read_csv(r'd:\北大光华AI交易课程\AI-quant\output\300504.SZ_daily_data.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)

end_date = df['trade_date'].max()
start_date = end_date - pd.Timedelta(days=3*365)
df = df[df['trade_date'] >= start_date].reset_index(drop=True)

df['MA5'] = df['close'].rolling(window=5).mean()
df['MA20'] = df['close'].rolling(window=20).mean()
df['signal'] = np.where(df['MA5'] > df['MA20'], 1, np.where(df['MA5'] < df['MA20'], -1, 0))
df['signal_t'] = df['signal'].shift(1)
df['cross_signal'] = df['signal_t'].diff()

buy_signals = df[df['cross_signal'] == 2]
sell_signals = df[df['cross_signal'] == -2]

print('=== 买入信号 ===')
for _, r in buy_signals.iterrows():
    d = r.trade_date.strftime("%Y-%m-%d")
    print(f'{d}  open={r.open:.2f}  close={r.close:.2f}  MA5={r.MA5:.2f}  MA20={r.MA20:.2f}')

print()
print('=== 卖出信号 ===')
for _, r in sell_signals.iterrows():
    d = r.trade_date.strftime("%Y-%m-%d")
    print(f'{d}  open={r.open:.2f}  close={r.close:.2f}  MA5={r.MA5:.2f}  MA20={r.MA20:.2f}')

print()
print(f'首日收盘: {df.close.iloc[0]:.2f}')
print(f'末日收盘: {df.close.iloc[-1]:.2f}')
print(f'买入持有收益: {(df.close.iloc[-1]-df.close.iloc[0])/df.close.iloc[0]*100:.2f}%')

# 模拟交易
initial_capital = 100000
commission_rate = 0.0003
slippage_rate = 0.0001
stamp_tax_rate = 0.0005
cash = initial_capital
position = 0

print()
print('=== 交易明细 ===')
for i in range(len(df)):
    row = df.iloc[i]
    d = row.trade_date.strftime("%Y-%m-%d")
    
    if row['cross_signal'] == 2 and position == 0:
        buy_price = row['open'] * (1 + slippage_rate)
        max_shares = int(cash / (buy_price * (1 + commission_rate)) / 100) * 100
        if max_shares > 0:
            shares = max_shares
            cost = shares * buy_price
            commission = cost * commission_rate
            total_cost = cost + commission
            position = shares
            cash -= total_cost
            print(f'[买入] {d}  价格={buy_price:.2f}  数量={shares}  成本={cost:.2f}  佣金={commission:.2f}  剩余现金={cash:.2f}')
    
    elif row['cross_signal'] == -2 and position > 0:
        sell_price = row['open'] * (1 - slippage_rate)
        revenue = position * sell_price
        commission = revenue * commission_rate
        stamp_tax = revenue * stamp_tax_rate
        net_revenue = revenue - commission - stamp_tax
        
        # 查找买入价
        buy_price_prev = None
        for j in range(i-1, -1, -1):
            if df.iloc[j]['cross_signal'] == 2:
                buy_price_prev = df.iloc[j]['open'] * (1 + slippage_rate)
                break
        
        profit = net_revenue - (position * buy_price_prev) if buy_price_prev else 0
        pct = profit / (position * buy_price_prev) * 100 if buy_price_prev else 0
        print(f'[卖出] {d}  价格={sell_price:.2f}  数量={position}  收入={net_revenue:.2f}  佣金={commission:.2f}  印花税={stamp_tax:.2f}  盈亏={profit:.2f} ({pct:+.2f}%)  现金={cash+net_revenue:.2f}')
        cash += net_revenue
        position = 0

# 如果最后还持仓，按末日收盘价计算
if position > 0:
    final_value = cash + position * df['close'].iloc[-1]
    print(f'[期末持仓] {position}股  末日收盘={df.close.iloc[-1]:.2f}  总资产={final_value:.2f}')
else:
    print(f'[期末空仓] 现金={cash:.2f}')

print(f'\n最终资产: {cash + position * df.close.iloc[-1]:.2f}')
print(f'累计回报: {(cash + position * df.close.iloc[-1] - initial_capital) / initial_capital * 100:.2f}%')
