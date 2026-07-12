import pandas as pd
df = pd.read_csv(r'd:\北大光华AI交易课程\AI-quant\output\300504.SZ_daily_data.csv')
avg_close = df['close'].mean()
avg_vol = df['vol'].mean()
avg_amount = df['amount'].mean()

print(f"日均成交量: {avg_vol:.0f}股 = {avg_vol/1e4:.2f}万股")
print(f"日均成交额(raw): {avg_amount:.0f}")
print(f"如果amount单位=元: {avg_amount/1e8:.2f}亿元")
print(f"如果amount单位=千元: {avg_amount/1e7:.2f}亿元")
print(f"验证: {avg_vol/1e4:.2f}万股 x {avg_close:.2f}元 = {avg_vol*avg_close/1e8:.2f}亿元")
print()
end_price = df['close'].iloc[-1]
print(f"总股本2.67亿股 x 末价{end_price:.2f}元 = {2.67*end_price:.2f}亿元")
print(f"流通股本2.2亿股 x 末价{end_price:.2f}元 = {2.2*end_price:.2f}亿元")
print()
# 检查换手率
float_shares = 2.2e8
df['turnover_calc'] = df['vol'] / float_shares * 100
print(f"日均换手率(估算): {df['turnover_calc'].mean():.2f}%")
print(f"换手率最大值: {df['turnover_calc'].max():.2f}%")
print(f"换手率最小值: {df['turnover_calc'].min():.2f}%")
print()
# 检查其他数据合理性
print(f"价格波动率: {df['close'].std()/df['close'].mean()*100:.2f}%")
print(f"振幅(最高-最低)/最低: {(df['high'].max()-df['low'].min())/df['low'].min()*100:.2f}%")
