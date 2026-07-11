import pandas as pd
import numpy as np
import json

stock_code = '300504.SZ'
stock_name = '天邑股份'
channel_period_s1 = 20
channel_period_s2 = 55
atr_period = 14
initial_capital = 100000
commission_rate = 0.0003
slippage_rate = 0.0001
stamp_tax_rate = 0.0005
stop_loss_multiplier = 2
risk_per_unit = 0.01

df = pd.read_csv(f'output/{stock_code}_daily_data.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)

end_date = df['trade_date'].max()
start_date = end_date - pd.Timedelta(days=3*365)
df = df[df['trade_date'] >= start_date].reset_index(drop=True)

print(f'数据量: {len(df)}条')
print(f'时间范围: {df["trade_date"].min().strftime("%Y-%m-%d")} ~ {df["trade_date"].max().strftime("%Y-%m-%d")}')

df['high_channel_s1'] = df['high'].rolling(window=channel_period_s1).max()
df['low_channel_s1'] = df['low'].rolling(window=channel_period_s1).min()
df['mid_channel_s1'] = (df['high_channel_s1'] + df['low_channel_s1']) / 2

df['high_channel_s2'] = df['high'].rolling(window=channel_period_s2).max()
df['low_channel_s2'] = df['low'].rolling(window=channel_period_s2).min()

df['tr1'] = df['high'] - df['low']
df['tr2'] = abs(df['high'] - df['close'].shift(1))
df['tr3'] = abs(df['low'] - df['close'].shift(1))
df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

df['atr'] = df['tr'].rolling(window=atr_period).mean()

df['prev_high_s1'] = df['high_channel_s1'].shift(1)
df['prev_low_s1'] = df['low_channel_s1'].shift(1)
df['prev_high_s2'] = df['high_channel_s2'].shift(1)
df['prev_low_s2'] = df['low_channel_s2'].shift(1)

df['buy_signal_s1'] = (df['close'] > df['prev_high_s1']).astype(int)
df['sell_signal_s1'] = (df['close'] < df['prev_low_s1']).astype(int)
df['buy_signal_s2'] = (df['close'] > df['prev_high_s2']).astype(int)
df['sell_signal_s2'] = (df['close'] < df['prev_low_s2']).astype(int)

df['buy_signal'] = df[['buy_signal_s1', 'buy_signal_s2']].max(axis=1)
df['sell_signal'] = df[['sell_signal_s1', 'sell_signal_s2']].max(axis=1)

df['signal'] = np.where(df['buy_signal'] == 1, 1, np.where(df['sell_signal'] == 1, -1, 0))

cash = initial_capital
position = 0
holdings = []
trades = []
win_trades = 0
lose_trades = 0
total_profit = 0
total_loss = 0
entry_price = 0
stop_loss_price = 0

for i in range(len(df)):
    row = df.iloc[i]
    current_total_asset = cash + position * row['close']
    
    if row['buy_signal'] == 1 and position == 0 and not np.isnan(row['atr']):
        buy_price = row['open'] * (1 + slippage_rate)
        atr_value = row['atr']
        stop_loss_price = buy_price - stop_loss_multiplier * atr_value
        
        risk_amount = current_total_asset * risk_per_unit
        shares_per_unit = int(risk_amount / atr_value / 100) * 100
        
        max_shares = int(cash / (buy_price * (1 + commission_rate)) / 100) * 100
        shares = min(shares_per_unit, max_shares)
        
        if shares > 0:
            cost = shares * buy_price
            commission = cost * commission_rate
            total_cost = cost + commission
            position = shares
            cash -= total_cost
            entry_price = buy_price
            
            system_trigger = '系统一(S1)' if row['buy_signal_s1'] == 1 else '系统二(S2)'
            
            trades.append({
                'date': row['trade_date'].strftime('%Y-%m-%d'),
                'type': '买入',
                'price': round(buy_price, 2),
                'shares': shares,
                'amount': round(cost, 2),
                'commission': round(commission, 2),
                'slippage': round(shares * row['open'] * slippage_rate, 2),
                'cash_after': round(cash, 2),
                'stop_loss': round(stop_loss_price, 2),
                'atr_at_entry': round(atr_value, 2),
                'system': system_trigger,
                'risk_per_unit': f'{risk_per_unit*100}%'
            })
    
    elif position > 0:
        current_low = row['low']
        
        stop_loss_triggered = current_low <= stop_loss_price
        sell_signal_triggered = row['sell_signal'] == 1
        
        if stop_loss_triggered:
            sell_price = stop_loss_price * (1 - slippage_rate)
            exit_type = '止损卖出'
        elif sell_signal_triggered:
            sell_price = row['open'] * (1 - slippage_rate)
            exit_type = '突破卖出'
        else:
            stop_loss_price = max(stop_loss_price, entry_price - stop_loss_multiplier * row['atr']) if not np.isnan(row['atr']) else stop_loss_price
            holdings.append({
                'date': row['trade_date'].strftime('%Y-%m-%d'),
                'total_asset': round(current_total_asset, 2),
                'cash': round(cash, 2),
                'position': position,
                'position_value': round(position * row['close'], 2),
                'stop_loss': round(stop_loss_price, 2)
            })
            continue
        
        revenue = position * sell_price
        commission = revenue * commission_rate
        stamp_tax = revenue * stamp_tax_rate
        net_revenue = revenue - commission - stamp_tax
        
        trade_profit = net_revenue - (position * entry_price)
        if trade_profit > 0:
            win_trades += 1
            total_profit += trade_profit
        else:
            lose_trades += 1
            total_loss += abs(trade_profit)
        
        cash += net_revenue
        
        trades.append({
            'date': row['trade_date'].strftime('%Y-%m-%d'),
            'type': exit_type,
            'price': round(sell_price, 2),
            'shares': position,
            'amount': round(revenue, 2),
            'commission': round(commission, 2),
            'stamp_tax': round(stamp_tax, 2),
            'slippage': round(position * row['open'] * slippage_rate, 2),
            'cash_after': round(cash, 2),
            'profit': round(trade_profit, 2),
            'exit_reason': exit_type
        })
        position = 0
    
    else:
        holdings.append({
            'date': row['trade_date'].strftime('%Y-%m-%d'),
            'total_asset': round(current_total_asset, 2),
            'cash': round(cash, 2),
            'position': position,
            'position_value': round(position * row['close'], 2)
        })

if position > 0:
    sell_price = df['close'].iloc[-1] * (1 - slippage_rate)
    revenue = position * sell_price
    commission = revenue * commission_rate
    stamp_tax = revenue * stamp_tax_rate
    net_revenue = revenue - commission - stamp_tax
    
    trade_profit = net_revenue - (position * entry_price)
    if trade_profit > 0:
        win_trades += 1
        total_profit += trade_profit
    else:
        lose_trades += 1
        total_loss += abs(trade_profit)
    
    cash += net_revenue
    
    trades.append({
        'date': df['trade_date'].iloc[-1].strftime('%Y-%m-%d'),
        'type': '期末平仓',
        'price': round(sell_price, 2),
        'shares': position,
        'amount': round(revenue, 2),
        'commission': round(commission, 2),
        'stamp_tax': round(stamp_tax, 2),
        'slippage': round(position * df['close'].iloc[-1] * slippage_rate, 2),
        'cash_after': round(cash, 2),
        'profit': round(trade_profit, 2),
        'exit_reason': '期末平仓'
    })
    position = 0

holdings_df = pd.DataFrame(holdings)
holdings_df['return'] = holdings_df['total_asset'] / initial_capital - 1
holdings_df['return_pct'] = holdings_df['return'] * 100

drawdown = []
max_asset = initial_capital
for _, row in holdings_df.iterrows():
    if row['total_asset'] > max_asset:
        max_asset = row['total_asset']
    drawdown.append((row['total_asset'] - max_asset) / max_asset * 100)
holdings_df['drawdown'] = drawdown

daily_returns = holdings_df['total_asset'].pct_change().dropna()
risk_free_rate = 0.02
excess_daily_returns = daily_returns - risk_free_rate / 252
sharpe_ratio = np.sqrt(252) * excess_daily_returns.mean() / excess_daily_returns.std() if excess_daily_returns.std() > 0 else 0

max_drawdown = holdings_df['drawdown'].min()
final_return = holdings_df['return'].iloc[-1]
final_asset = holdings_df['total_asset'].iloc[-1]
total_trades = len(trades) // 2

holding_return = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]
excess_return = final_return - holding_return

total_days = (df['trade_date'].iloc[-1] - df['trade_date'].iloc[0]).days
years = total_days / 365
annualized_return = (1 + final_return) ** (1 / years) - 1 if years > 0 else 0

win_rate = win_trades / (win_trades + lose_trades) * 100 if (win_trades + lose_trades) > 0 else 0
profit_loss_ratio = (total_profit / win_trades) / (total_loss / lose_trades) if (win_trades > 0 and lose_trades > 0) else 0

expected_return = (win_rate / 100) * (total_profit / win_trades if win_trades > 0 else 0) - ((1 - win_rate / 100) * (total_loss / lose_trades if lose_trades > 0 else 0))

print(f'交易次数: {total_trades}次')
print(f'最终资产: {final_asset:.2f}元')
print(f'累计回报: {final_return*100:.2f}%')
print(f'年化回报: {annualized_return*100:.2f}%')
print(f'超额收益: {excess_return*100:.2f}%')
print(f'最大回撤: {max_drawdown:.2f}%')
print(f'夏普比率: {sharpe_ratio:.2f}')
print(f'胜率: {win_rate:.2f}%')
print(f'盈亏比: {profit_loss_ratio:.2f}')
print(f'期望收益: {expected_return:.2f}元/次')
print(f'持有收益: {holding_return*100:.2f}%')

dates = [d.strftime('%Y-%m-%d') for d in df['trade_date']]
close_prices = [round(p, 2) for p in df['close'].tolist()]
high_channel_s1 = [round(p, 2) if not np.isnan(p) else None for p in df['high_channel_s1'].tolist()]
low_channel_s1 = [round(p, 2) if not np.isnan(p) else None for p in df['low_channel_s1'].tolist()]
high_channel_s2 = [round(p, 2) if not np.isnan(p) else None for p in df['high_channel_s2'].tolist()]
low_channel_s2 = [round(p, 2) if not np.isnan(p) else None for p in df['low_channel_s2'].tolist()]
atr_values = [round(p, 2) if not np.isnan(p) else None for p in df['atr'].tolist()]

buy_points = []
sell_points = []
for i in range(len(df)):
    if df['buy_signal'].iloc[i] == 1:
        buy_price = df['open'].iloc[i] * (1 + slippage_rate)
        buy_points.append([i, round(buy_price, 2)])
    elif df['sell_signal'].iloc[i] == 1:
        sell_price = df['open'].iloc[i] * (1 - slippage_rate)
        sell_points.append([i, round(sell_price, 2)])

holdings_data = []
holdings_drawdown = []
holdings_dates = holdings_df['date'].tolist()
holdings_assets = [round(a, 2) for a in holdings_df['total_asset'].tolist()]
holdings_drawdown = [round(d, 2) for d in holdings_df['drawdown'].tolist()]
for d, a in zip(holdings_dates, holdings_assets):
    idx = dates.index(d) if d in dates else -1
    if idx >= 0:
        holdings_data.append([idx, a])

holding_line = []
start_price = df['close'].iloc[0]
for p in close_prices:
    holding_line.append(initial_capital * (p / start_price))

trade_rows = []
for t in trades:
    row_class = 'buy-row' if t['type'] == '买入' else 'sell-row'
    slippage_val = t.get('slippage', '-')
    stamp_tax_val = t.get('stamp_tax', '-')
    profit_val = t.get('profit', '-')
    stop_loss_val = t.get('stop_loss', '-')
    exit_reason_val = t.get('exit_reason', '-')
    atr_val = t.get('atr_at_entry', '-')
    system_val = t.get('system', '-')
    trade_rows.append(f'<tr class="{row_class}"><td>{t["date"]}</td><td>{t["type"]}</td><td>{t["price"]}</td><td>{t["shares"]}</td><td>{t["amount"]:.2f}</td><td>{t["commission"]:.2f}</td><td>{slippage_val}</td><td>{stamp_tax_val}</td><td>{profit_val}</td><td>{stop_loss_val}</td><td>{atr_val}</td><td>{system_val}</td><td>{exit_reason_val}</td><td>{t["cash_after"]:.2f}</td></tr>')

strategy_eval = '优秀' if annualized_return > 0.1 else '良好' if annualized_return > 0.05 else '一般' if annualized_return >= 0 else '亏损'
risk_eval = '风险很低（绿色）' if abs(max_drawdown) < 10 else '风险适中（浅绿）' if abs(max_drawdown) < 20 else '风险较高（橙色）' if abs(max_drawdown) < 30 else '风险很高（红色）'

html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TITLE</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .header h1 { color: #1a1a2e; font-size: 28px; margin-bottom: 10px; }
        .header p { color: #666; font-size: 14px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-top: 20px; }
        .stat-card { background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; }
        .stat-card .label { font-size: 12px; opacity: 0.9; margin-bottom: 5px; }
        .stat-card .value { font-size: 20px; font-weight: bold; }
        .stat-card .unit { font-size: 12px; opacity: 0.7; margin-top: 5px; }
        .chart-section { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .chart-section h2 { color: #1a1a2e; font-size: 20px; margin-bottom: 20px; }
        .chart-section h3 { color: #333; font-size: 16px; margin-bottom: 15px; }
        .chart-container { width: 100%; height: 400px; }
        .trade-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .trade-table th, .trade-table td { padding: 8px; text-align: left; border-bottom: 1px solid #eee; font-size: 12px; }
        .trade-table th { background: #f8f9fa; font-weight: 600; color: #666; }
        .trade-table tr:hover { background: #f8f9fa; }
        .buy-row { color: #10b981; }
        .sell-row { color: #ef4444; }
        .intro-text { color: #666; line-height: 1.8; margin-bottom: 20px; font-size: 14px; }
        .interpretation { background: #f8f9fa; padding: 20px; border-radius: 10px; color: #333; line-height: 1.8; font-size: 14px; }
        .strategy-rule { background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0; }
        .strategy-rule strong { color: #e65100; }
        .params-table { width: 100%; margin-top: 15px; }
        .params-table td { padding: 8px 12px; border-bottom: 1px solid #eee; }
        .params-table tr:nth-child(odd) { background: #f9f9f9; }
        .metric-box { background: #fff; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #ff6b6b; }
        .metric-box strong { color: #1a1a2e; }
        .concept-box { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0; }
        .concept-box strong { color: #1565c0; }
        .five-elements { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 20px; }
        .element-box { background: #fff; border-radius: 10px; padding: 15px; text-align: center; border: 2px solid #ddd; }
        .element-box .num { font-size: 24px; font-weight: bold; color: #ff6b6b; }
        .element-box .title { font-size: 13px; font-weight: 600; margin-top: 5px; }
        .element-box .desc { font-size: 11px; color: #666; margin-top: 5px; }
        .system-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .system-box { background: #fff; border-radius: 10px; padding: 20px; }
        .system-box.s1 { border-top: 4px solid #ef4444; }
        .system-box.s2 { border-top: 4px solid #2196f3; }
        .system-box h4 { margin-bottom: 10px; }
        .system-box ul { padding-left: 20px; font-size: 13px; line-height: 1.8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NAME</h1>
            <p>策略参数：系统一{S1}日突破，系统二{S2}日突破，ATR周期{atr_period}日，止损倍数{stop_loss_multiplier}×ATR，单单位风险{risk_pct}% | 数据周期：近三年（前复权）</p>
            <div class="stats-grid">
                <div class="stat-card"><div class="label">累计回报</div><div class="value">RETURN%</div><div class="unit">vs 初始资金</div></div>
                <div class="stat-card"><div class="label">年化回报</div><div class="value">ANNUAL%</div><div class="unit">年化</div></div>
                <div class="stat-card"><div class="label">超额收益</div><div class="value">EXCESS%</div><div class="unit">vs 持有</div></div>
                <div class="stat-card"><div class="label">最大回撤</div><div class="value">MDD%</div><div class="unit">MDD</div></div>
                <div class="stat-card"><div class="label">夏普比率</div><div class="value">SHARPE</div><div class="unit">年化</div></div>
                <div class="stat-card"><div class="label">胜率</div><div class="value">WINRATE%</div><div class="unit">盈利交易占比</div></div>
                <div class="stat-card"><div class="label">盈亏比</div><div class="value">PROFITLOSS</div><div class="unit">平均盈利/亏损</div></div>
                <div class="stat-card"><div class="label">交易次数</div><div class="value">TRADES</div><div class="unit">次</div></div>
            </div>
        </div>

        <div class="chart-section">
            <h2>1. 海龟策略五大核心要素</h2>
            
            <div class="five-elements">
                <div class="element-box">
                    <div class="num">1</div>
                    <div class="title">市场选择</div>
                    <div class="desc">交易什么？</div>
                </div>
                <div class="element-box">
                    <div class="num">2</div>
                    <div class="title">头寸规模</div>
                    <div class="desc">买卖多少？</div>
                </div>
                <div class="element-box">
                    <div class="num">3</div>
                    <div class="title">入场规则</div>
                    <div class="desc">何时买入？</div>
                </div>
                <div class="element-box">
                    <div class="num">4</div>
                    <div class="title">止损规则</div>
                    <div class="desc">何时认输？</div>
                </div>
                <div class="element-box">
                    <div class="num">5</div>
                    <div class="title">离场规则</div>
                    <div class="desc">何时了结？</div>
                </div>
            </div>
            <p style="text-align:center; color:#666; font-size:14px;">五个要素缺一不可，共同构成完整的交易系统</p>
        </div>

        <div class="chart-section">
            <h2>2. 核心概念详解</h2>
            
            <div class="concept-box">
                <strong>【海龟策略（Turtle Trading）】</strong><br>
                海龟策略是由传奇交易员理查德·丹尼斯（Richard Dennis）和威廉·埃克哈特（William Eckhardt）在1983年创立的系统化交易策略。其核心思想是"顺势而为"——在市场突破时入场，跟随趋势获利，通过严格的止损和仓位管理控制风险。策略名称来源于丹尼斯的名言："我要培养交易员，就像新加坡人养海龟一样容易。"
            </div>

            <div class="concept-box">
                <strong>【高低点通道（Donchian Channel）】</strong><br>
                高低点通道，又称唐奇安通道，是海龟策略的核心入场信号指标。它由三条线组成：<br>
                <strong>上轨（High Channel）：</strong>过去N个交易日的最高价<br>
                <strong>下轨（Low Channel）：</strong>过去N个交易日的最低价<br>
                <strong>中轨（Mid Channel）：</strong>上轨与下轨的平均值<br>
                当价格突破上轨时产生买入信号，突破下轨时产生卖出信号。
            </div>

            <div class="concept-box">
                <strong>【平均真实波幅（ATR - Average True Range）】</strong><br>
                ATR是衡量市场波动性的指标，由威尔斯·怀尔德（J. Welles Wilder Jr.）发明。真实波幅（TR）取以下三者中的最大值：<br>
                1. 当日最高价 - 当日最低价<br>
                2. |当日最高价 - 前一日收盘价|<br>
                3. |当日最低价 - 前一日收盘价|<br>
                ATR是TR的N日移动平均值（标准周期为{atr_period}日）。ATR越大说明市场波动越剧烈，ATR越小说明市场越平稳。
            </div>

            <div class="concept-box">
                <strong>【止损条件（Stop Loss）】</strong><br>
                海龟策略使用ATR作为止损基准：<br>
                <strong>止损价 = 入场价 - {stop_loss_multiplier}×ATR</strong><br>
                当价格跌破止损价时，立即卖出平仓，控制单笔交易的最大亏损。止损距离不是固定百分比，而是根据市场波动性动态调整——波动大时止损距离宽，波动小时止损距离窄。
            </div>

            <div class="concept-box">
                <strong>【仓位管理（Unit）】</strong><br>
                海龟策略最精妙的部分是仓位管理系统，核心概念是"单位"（Unit）：<br>
                <strong>可买股数 = (账户资金 × {risk_pct}%) / ATR</strong><br>
                一个单位的头寸，如果价格波动1个ATR，账户损失{risk_pct}%。这种方法确保了在不同波动性的市场中，每单位头寸承担相同的风险。
            </div>
        </div>

        <div class="chart-section">
            <h2>3. 双系统突破入场机制</h2>
            
            <div class="system-compare">
                <div class="system-box s1">
                    <h4>系统一（S1）— {S1}日突破</h4>
                    <ul>
                        <li><strong>触发条件：</strong>突破{S1}日最高价 → 买入</li>
                        <li><strong>特点：</strong>更敏感，更快捕捉趋势启动</li>
                        <li><strong>优势：</strong>交易信号更多，入场时机更早</li>
                        <li><strong>劣势：</strong>假突破多，容易受到市场噪音干扰</li>
                    </ul>
                </div>
                <div class="system-box s2">
                    <h4>系统二（S2）— {S2}日突破</h4>
                    <ul>
                        <li><strong>触发条件：</strong>突破{S2}日最高价 → 买入</li>
                        <li><strong>特点：</strong>更稳健，过滤更多噪音</li>
                        <li><strong>优势：</strong>趋势更确认，大趋势捕捉能力更强</li>
                        <li><strong>劣势：</strong>交易信号更少，入场时机稍晚</li>
                    </ul>
                </div>
            </div>

            <p style="text-align:center; color:#666; font-size:14px;">海龟们通常同时运行两个系统，分散风险，提高策略稳定性</p>
        </div>

        <div class="chart-section">
            <h2>4. 策略规则与参数</h2>
            <div class="intro-text">海龟策略通过突破高低点通道来识别趋势方向，结合ATR进行动态风险控制和仓位管理。</div>
            <div class="strategy-rule">
                <strong>高低点通道计算：</strong><br>
                high_channel_S1 = high.rolling({S1}).max()（前{S1}日最高价）<br>
                low_channel_S1 = low.rolling({S1}).min()（前{S1}日最低价）<br>
                high_channel_S2 = high.rolling({S2}).max()（前{S2}日最高价）<br>
                low_channel_S2 = low.rolling({S2}).min()（前{S2}日最低价）
            </div>
            <div class="strategy-rule">
                <strong>ATR计算（Wilder平滑法）：</strong><br>
                TR = max(high-low, |high-prev_close|, |low-prev_close|)<br>
                ATR = TR.rolling({atr_period}).mean()（前{atr_period}日TR均值）
            </div>
            <div class="strategy-rule">
                <strong>买入规则（双系统突破）：</strong><br>
                1. 系统一：收盘价突破前一日{S1}日上轨时产生买入信号<br>
                2. 系统二：收盘价突破前一日{S2}日上轨时产生买入信号<br>
                3. 任一系统触发即买入，次日开盘执行<br>
                4. 计算止损价 = 买入价 - {stop_loss_multiplier}×ATR<br>
                5. 计算仓位 = (账户资金 × {risk_pct}%) / ATR（取整到100股）
            </div>
            <div class="strategy-rule">
                <strong>卖出规则（双重退出机制）：</strong><br>
                1. <strong>止损卖出：</strong>当日最低价跌破止损价时，以止损价卖出<br>
                2. <strong>突破卖出：</strong>收盘价突破前一日下轨时，次日开盘卖出<br>
                优先级：止损 > 突破信号
            </div>
            <div class="strategy-rule">
                <strong>移动止损调整：</strong><br>
                在持仓期间，若ATR下降，止损价会上移（锁定更多利润）；若ATR上升，止损价保持不变（不扩大风险）。
            </div>
            <table class="params-table">
                <tr><td><strong>初始资金</strong></td><td>INITIAL_CAPITAL 元</td></tr>
                <tr><td><strong>仓位方式</strong></td><td>基于ATR的单位仓位管理</td></tr>
                <tr><td><strong>系统一通道周期</strong></td><td>{S1}日</td></tr>
                <tr><td><strong>系统二通道周期</strong></td><td>{S2}日</td></tr>
                <tr><td><strong>ATR周期</strong></td><td>{atr_period}日</td></tr>
                <tr><td><strong>止损倍数</strong></td><td>{stop_loss_multiplier}×ATR</td></tr>
                <tr><td><strong>单单位风险</strong></td><td>{risk_pct}%账户资金</td></tr>
                <tr><td><strong>买入佣金</strong></td><td>万三（0.03%）</td></tr>
                <tr><td><strong>卖出佣金</strong></td><td>万三（0.03%）</td></tr>
                <tr><td><strong>卖出印花税</strong></td><td>万五（0.05%）</td></tr>
                <tr><td><strong>滑点</strong></td><td>万分之一（0.01%）</td></tr>
                <tr><td><strong>数据类型</strong></td><td>前复权（qfq）</td></tr>
            </table>
        </div>

        <div class="chart-section">
            <h2>5. 股价与高低点通道走势（含交易信号）</h2>
            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:5px;">图1 天邑股份（300504.SZ）近三年股价与唐奇安通道</h3>
            <div id="priceChart" class="chart-container"></div>
            <div class="interpretation" style="margin-top:15px;">
                <strong>【图1解读】</strong> 图中黑色线为收盘价，红色线为{S1}日上轨，绿色线为{S1}日下轨，蓝色线为{S2}日上轨，青色线为{S2}日下轨，绿色三角为买入信号，红色三角为卖出信号。<br><br>
                <strong>通道特征：</strong>{S1}日通道（红色/绿色）更敏感，通道宽度较窄；{S2}日通道（蓝色/青色）更稳健，通道宽度较宽。通道上轨和下轨形成了天然的支撑和阻力位。<br><br>
                <strong>信号触发：</strong>买入信号出现在价格突破任一系统上轨时，表明上升趋势确立；卖出信号出现在价格跌破下轨时，表明下降趋势确立。
            </div>
        </div>

        <div class="chart-section">
            <h2>6. ATR指标走势</h2>
            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:5px;">图2 天邑股份（300504.SZ）{atr_period}日ATR指标</h3>
            <div id="atrChart" class="chart-container"></div>
            <div class="interpretation" style="margin-top:15px;">
                <strong>【图2解读】</strong> ATR反映市场波动性。ATR值越高，说明价格波动越剧烈，止损距离和仓位规模也会相应调整；ATR值越低，说明市场越平稳。<br><br>
                <strong>波动周期：</strong>观察ATR的变化可以帮助判断市场处于趋势期还是震荡期。趋势行情中ATR通常较高且稳定，震荡行情中ATR通常较低。
            </div>
        </div>

        <div class="chart-section">
            <h2>7. 资产净值曲线与回撤曲线</h2>
            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:5px;">图3 海龟策略资产净值曲线与回撤曲线</h3>
            <div id="equityChart" class="chart-container"></div>
            <div class="interpretation" style="margin-top:15px;">
                <strong>【图3解读】</strong> 图中左侧Y轴为总资产（蓝色区域），灰色虚线为买入持有对照；右侧Y轴为回撤曲线（红色区域）。<br><br>
                <strong>净值走势：</strong>策略净值反映了海龟策略在天邑股份上的表现。通过ATR动态止损和仓位管理，策略能够控制风险并捕捉趋势利润。<br><br>
                <strong>回撤特征：</strong>回撤曲线反映了策略在不同时间点的浮亏状态。海龟策略的单位风险控制机制有助于限制最大回撤幅度。
            </div>
        </div>

        <div class="chart-section">
            <h2>8. 交易明细</h2>
            TRADE_TABLE
        </div>

        <div class="chart-section">
            <h2>9. 策略评估指标详解</h2>
            <div class="metric-box">
                <strong>【最大回撤（Maximum Drawdown, MDD）】</strong>从资产峰值到谷底的最大跌幅，衡量策略承受的最大亏损。<br>
                公式：MDD = min_t((当日资产 - 历史最高资产) / 历史最高资产) × 100%<br>
                本策略最大回撤：MDD%，评级：RISK_EVAL。
            </div>
            <div class="metric-box">
                <strong>【夏普比率（Sharpe Ratio）】</strong>衡量每承担一单位风险所获得的超额收益。<br>
                公式：S = √252 × (日均超额收益 / 日均收益标准差)，其中超额收益 = 策略收益 - 无风险利率(2%)<br>
                本策略夏普比率：SHARPE（&gt;2优秀，1-2良好，0-1一般，&lt;0策略无效）。
            </div>
            <div class="metric-box">
                <strong>【累计回报（Cumulative Return）】</strong>整个回测期的总收益。<br>
                公式：累计回报 = (期末资产 - 期初资产) / 期初资产 × 100%<br>
                本策略累计回报：RETURN%，初始资金 INITIAL_CAPITAL 元最终变为 FINAL_ASSET 元。
            </div>
            <div class="metric-box">
                <strong>【年化收益率（Annualized Return）】</strong>将收益标准化到每年。<br>
                公式：年化收益率 = (期末资产 / 期初资产)^(365/N) - 1（N为回测自然日天数）<br>
                本策略年化回报：ANNUAL%，评级：STRATEGY_EVAL。
            </div>
            <div class="metric-box">
                <strong>【超额收益（Excess Return）】</strong>策略收益与买入持有收益的差异。<br>
                公式：超额收益 = 策略收益率 - 买入持有收益率<br>
                本策略超额收益：EXCESS%，买入持有收益：BUYHOLD_PCT。
            </div>
            <div class="metric-box">
                <strong>【胜率（Win Rate）】</strong>盈利交易次数占总交易次数的比例。<br>
                公式：胜率 = 盈利交易次数 / 总交易次数 × 100%<br>
                本策略胜率：WINRATE%。
            </div>
            <div class="metric-box">
                <strong>【盈亏比（Profit/Loss Ratio）】</strong>平均盈利与平均亏损的倍数。<br>
                公式：盈亏比 = 平均盈利 / |平均亏损|<br>
                本策略盈亏比：PROFITLOSS。
            </div>
            <div class="metric-box">
                <strong>【期望收益（Expected Return）】</strong>每次交易的期望结果。<br>
                公式：期望收益 = 胜率 × 平均盈利 - (1-胜率) × 平均亏损<br>
                本策略期望收益：EXPECTED_RETURN元/次交易。
            </div>
        </div>

        <div class="chart-section">
            <h2>10. 总结分析</h2>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:20px;">10.1 核心结论</h3>
            <div class="interpretation">
                <strong>一句话结论：</strong>海龟策略在天邑股份上3年累计回报SUMMARY_RET_PCT，与买入持有（BUYHOLD_PCT2）相比超额收益EXCESS_RETURN2%，策略表现STRATEGY_EVAL。<br><br>
                <strong>策略 vs 持有：</strong>策略累计回报SUMMARY_RET_PCT，买入持有BUYHOLD_PCT2，超额收益EXCESS_RETURN2%。SUMMARY_TRADES笔交易中仅SUMMARY_WINS笔盈利（胜率WINRATE2%），盈亏比PROFITLOSS2，每次交易期望EXPECTED_RETURN2元。<br><br>
                <strong>最大回撤：</strong>策略最大回撤MDD2%，ATR动态止损和单位风险控制机制有效控制了单次亏损幅度。
            </div>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:25px;">10.2 收获与反思</h3>
            <div class="interpretation">
                <strong>收获一：理解了海龟策略的五大核心要素。</strong>完整的交易系统必须包含市场选择、头寸规模、入场规则、止损规则和离场规则五个要素，缺一不可。海龟策略的精髓在于将这些要素系统化、规则化，避免情绪化操作。<br><br>
                <strong>收获二：体验了双系统突破的优势。</strong>同时运行系统一（{S1}日）和系统二（{S2}日）可以分散风险。系统一更敏感，能快速捕捉趋势启动；系统二更稳健，过滤噪音能力更强。两者结合提高了策略的稳定性。<br><br>
                <strong>收获三：掌握了基于ATR的仓位管理方法。</strong>通过"单位"概念，每单位头寸承担相同的风险（{risk_pct}%账户资金），确保在不同波动性市场中风险一致。这是海龟策略最精妙的设计之一。<br><br>
                <strong>收获四：认识到ATR动态止损的价值。</strong>与固定百分比止损相比，ATR止损能够根据市场波动性自动调整止损距离，在波动大时给策略更多呼吸空间，在波动小时更紧密地保护利润。<br><br>
                <strong>反思一：通道周期的选择。</strong>标准{S1}日和{S2}日周期在天邑股份上的表现取决于其趋势特征。如果标的长期处于震荡格局，较短周期的通道可能产生过多假信号。<br><br>
                <strong>反思二：单单位风险的设定。</strong>{risk_pct}%的单单位风险是标准设定，但可以根据个人风险承受能力调整。风险偏好低的投资者可以降低此比例。<br><br>
                <strong>反思三：缺乏趋势过滤。</strong>策略在所有市场状态下都执行相同逻辑。如果能先判断市场是否处于趋势状态（如用ADX指标），在震荡市中暂停交易，可以减少假信号亏损。
            </div>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:25px;">10.3 后续优化计划</h3>
            <div class="interpretation">
                <strong>优化方向一：引入趋势过滤指标。</strong>在突破信号基础上增加ADX指标过滤。当ADX&lt;25（无明显趋势）时不产生交易信号，避免在震荡市中频繁操作。<br><br>
                <strong>优化方向二：调整通道周期参数。</strong>尝试不同的通道周期组合，找到最适合天邑股份的参数组合。<br><br>
                <strong>优化方向三：优化仓位管理。</strong>可以考虑在趋势确认后增加单位数量（加仓），提高在大趋势中的收益能力。<br><br>
                <strong>优化方向四：引入移动止盈。</strong>当价格上涨一定幅度后，动态调整止损线为移动止损，锁定更多利润。<br><br>
                <strong>优化方向五：结合基本面分析。</strong>在技术面信号基础上，结合公司基本面进行过滤，避免在基本面恶化的标的上交易。
            </div>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:25px;">10.4 适用场景总结</h3>
            <div class="interpretation">
                <strong>适合海龟策略的场景：</strong><br>
                1. 处于明显上升或下降趋势的标的<br>
                2. 价格波动较大、趋势持续时间较长的标的<br>
                3. 日均成交额大于5亿元、流动性好的标的<br>
                4. 不受重大事件驱动、技术规律较强的标的<br><br>
                <strong>不适合海龟策略的场景：</strong><br>
                1. 长期横盘整理的震荡市标的<br>
                2. 日均成交额小于2亿元、流动性不足的小盘股<br>
                3. 受政策或事件驱动、波动剧烈且无规律的标的<br>
                4. 基本面恶化、存在退市风险的标的<br><br>
                <strong>天邑股份定位：</strong>基于近三年数据，天邑股份的趋势特征决定了海龟策略的适用性。需要结合实际回测结果判断是否适合该策略。
            </div>
        </div>
    </div>

    <script>
        var dates = DATES;
        var closePrices = CLOSE_PRICES;
        var highChannelS1 = HIGH_CHANNEL_S1;
        var lowChannelS1 = LOW_CHANNEL_S1;
        var highChannelS2 = HIGH_CHANNEL_S2;
        var lowChannelS2 = LOW_CHANNEL_S2;
        var atrValues = ATR_VALUES;
        var buyPoints = BUY_POINTS;
        var sellPoints = SELL_POINTS;
        var holdingsData = HOLDINGS_DATA;
        var drawdownData = DRAWDOWN_DATA;
        var holdingLine = HOLDING_LINE;

        var commonDataZoom = [
            { type: 'inside', xAxisIndex: [0], start: 0, end: 100 },
            { type: 'slider', xAxisIndex: [0], start: 0, end: 100, height: 20, bottom: 5,
               borderColor: '#e5e7eb', fillerColor: 'rgba(255,107,107,0.2)', handleStyle: { color: '#ff6b6b' } }
        ];

        var priceChart = echarts.init(document.getElementById('priceChart'));
        var priceOption = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' }, valueFormatter: function(v) { return v === null || v === undefined ? '-' : v.toFixed(2); } },
            legend: { data: ['收盘价', '{S1}日上轨', '{S1}日下轨', '{S2}日上轨', '{S2}日下轨', '买入信号', '卖出信号'] },
            grid: { left: '3%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: { type: 'value', axisLabel: { formatter: function(v) { return v.toFixed(2); } } },
            dataZoom: commonDataZoom,
            series: [
                { name: '收盘价', type: 'line', data: closePrices, smooth: true, lineStyle: { color: '#1a1a2e', width: 2 }, itemStyle: { color: '#1a1a2e' } },
                { name: '{S1}日上轨', type: 'line', data: highChannelS1, smooth: true, lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, itemStyle: { color: '#ef4444' } },
                { name: '{S1}日下轨', type: 'line', data: lowChannelS1, smooth: true, lineStyle: { color: '#10b981', width: 2, type: 'dashed' }, itemStyle: { color: '#10b981' } },
                { name: '{S2}日上轨', type: 'line', data: highChannelS2, smooth: true, lineStyle: { color: '#2196f3', width: 2, type: 'dotted' }, itemStyle: { color: '#2196f3' } },
                { name: '{S2}日下轨', type: 'line', data: lowChannelS2, smooth: true, lineStyle: { color: '#00bcd4', width: 2, type: 'dotted' }, itemStyle: { color: '#00bcd4' } },
                { name: '买入信号', type: 'scatter', data: buyPoints, symbol: 'triangle', symbolSize: 15, itemStyle: { color: '#10b981' } },
                { name: '卖出信号', type: 'scatter', data: sellPoints, symbol: 'triangle', symbolSize: 15, symbolRotate: 180, itemStyle: { color: '#ef4444' } }
            ]
        };
        priceChart.setOption(priceOption);

        var atrChart = echarts.init(document.getElementById('atrChart'));
        var atrOption = {
            tooltip: { trigger: 'axis', valueFormatter: function(v) { return v === null || v === undefined ? '-' : v.toFixed(2); } },
            legend: { data: ['ATR'] },
            grid: { left: '3%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: { type: 'value', name: 'ATR', axisLabel: { formatter: function(v) { return v.toFixed(2); } } },
            dataZoom: commonDataZoom,
            series: [
                { name: 'ATR', type: 'bar', data: atrValues, itemStyle: { color: '#ff6b6b' }, barWidth: '60%' }
            ]
        };
        atrChart.setOption(atrOption);

        var equityChart = echarts.init(document.getElementById('equityChart'));
        var equityOption = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' }, valueFormatter: function(v) { return v === null || v === undefined ? '-' : v.toFixed(2); } },
            legend: { data: ['总资产', '买入持有对照', '回撤曲线'] },
            grid: { left: '3%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: [
                { type: 'value', name: '总资产(元)', position: 'left', axisLabel: { formatter: function(v) { return v.toFixed(2); } } },
                { type: 'value', name: '回撤(%)', position: 'right', axisLabel: { formatter: function(v) { return v.toFixed(2) + '%'; } } }
            ],
            dataZoom: commonDataZoom,
            series: [
                { name: '总资产', type: 'line', yAxisIndex: 0, data: closePrices.map(function(p, i) {
                    var h = holdingsData.find(function(d) { return d[0] === i; });
                    return h ? h[1] : null;
                }), smooth: true, lineStyle: { color: '#ff6b6b', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(255,107,107,0.3)'}, {offset: 1, color: 'rgba(255,107,107,0.05)'}]) } },
                { name: '买入持有对照', type: 'line', yAxisIndex: 0, data: holdingLine, smooth: true, lineStyle: { color: '#9ca3af', width: 2, type: 'dashed' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(156,163,175,0.2)'}, {offset: 1, color: 'rgba(156,163,175,0.02)'}]) } },
                { name: '回撤曲线', type: 'line', yAxisIndex: 1, data: closePrices.map(function(p, i) {
                    var idx = holdingsData.findIndex(function(d) { return d[0] === i; });
                    return idx >= 0 ? drawdownData[idx] : null;
                }), smooth: true, lineStyle: { color: '#ef4444', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(239,68,68,0.3)'}, {offset: 1, color: 'rgba(239,68,68,0.05)'}]) } }
            ]
        };
        equityChart.setOption(equityOption);

        window.addEventListener('resize', function() {
            priceChart.resize();
            atrChart.resize();
            equityChart.resize();
        });
    </script>
</body>
</html>'''

html_content = html_template.replace('TITLE', f'{stock_name}({stock_code}) 海龟策略回测报告')
html_content = html_content.replace('NAME', f'{stock_name}({stock_code}) 海龟策略回测报告')
html_content = html_content.replace('{S1}', str(channel_period_s1))
html_content = html_content.replace('{S2}', str(channel_period_s2))
html_content = html_content.replace('{atr_period}', str(atr_period))
html_content = html_content.replace('{stop_loss_multiplier}', str(stop_loss_multiplier))
html_content = html_content.replace('{risk_pct}', f'{risk_per_unit*100}')

html_content = html_content.replace('SUMMARY_RET_PCT', f'{final_return*100:.2f}%')
html_content = html_content.replace('EXCESS_RETURN2%', f'{excess_return*100:.2f}%')
html_content = html_content.replace('SUMMARY_TRADES', str(total_trades))
html_content = html_content.replace('SUMMARY_WINS', str(win_trades))
html_content = html_content.replace('WINRATE2%', f'{win_rate:.2f}%')
html_content = html_content.replace('PROFITLOSS2', f'{profit_loss_ratio:.2f}')
html_content = html_content.replace('MDD2%', f'{max_drawdown:.2f}%')
html_content = html_content.replace('BUYHOLD_PCT2', f'{holding_return*100:.2f}%')
html_content = html_content.replace('BUYHOLD_PCT', f'{holding_return*100:.2f}%')
html_content = html_content.replace('EXPECTED_RETURN2', f'{expected_return:.2f}')
html_content = html_content.replace('EXPECTED_RETURN', f'{expected_return:.2f}')

html_content = html_content.replace('RETURN%', f'{final_return*100:.2f}%')
html_content = html_content.replace('ANNUAL%', f'{annualized_return*100:.2f}%')
html_content = html_content.replace('EXCESS%', f'{excess_return*100:.2f}%')
html_content = html_content.replace('MDD%', f'{max_drawdown:.2f}%')
html_content = html_content.replace('SHARPE', f'{sharpe_ratio:.2f}')
html_content = html_content.replace('WINRATE%', f'{win_rate:.2f}%')
html_content = html_content.replace('PROFITLOSS', f'{profit_loss_ratio:.2f}')
html_content = html_content.replace('TRADES', str(total_trades))
html_content = html_content.replace('FINAL_ASSET', f'{final_asset:.2f}')
html_content = html_content.replace('INITIAL_CAPITAL', str(initial_capital))
html_content = html_content.replace('STRATEGY_EVAL', strategy_eval)
html_content = html_content.replace('RISK_EVAL', risk_eval)

if trades:
    trade_table = f'<table class="trade-table"><thead><tr><th>日期</th><th>类型</th><th>价格(元)</th><th>数量(股)</th><th>金额(元)</th><th>佣金(元)</th><th>滑点(元)</th><th>印花税(元)</th><th>盈亏(元)</th><th>止损价(元)</th><th>入场ATR</th><th>触发系统</th><th>退出原因</th><th>交易后现金(元)</th></tr></thead><tbody>{"".join(trade_rows)}</tbody></table>'
else:
    trade_table = '<p style="color:#999;">暂无交易记录</p>'
html_content = html_content.replace('TRADE_TABLE', trade_table)

html_content = html_content.replace('DATES', json.dumps(dates))
html_content = html_content.replace('CLOSE_PRICES', json.dumps(close_prices))
html_content = html_content.replace('HIGH_CHANNEL_S1', json.dumps(high_channel_s1))
html_content = html_content.replace('LOW_CHANNEL_S1', json.dumps(low_channel_s1))
html_content = html_content.replace('HIGH_CHANNEL_S2', json.dumps(high_channel_s2))
html_content = html_content.replace('LOW_CHANNEL_S2', json.dumps(low_channel_s2))
html_content = html_content.replace('ATR_VALUES', json.dumps(atr_values))
html_content = html_content.replace('BUY_POINTS', json.dumps(buy_points))
html_content = html_content.replace('SELL_POINTS', json.dumps(sell_points))
html_content = html_content.replace('HOLDINGS_DATA', json.dumps(holdings_data))
html_content = html_content.replace('DRAWDOWN_DATA', json.dumps(holdings_drawdown))
html_content = html_content.replace('HOLDING_LINE', json.dumps(holding_line))

with open(f'output/{stock_code}_turtle_strategy.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'报告已保存: output/{stock_code}_turtle_strategy.html')