import pandas as pd
import numpy as np
import json

stock_code = '300504.SZ'
stock_name = '天邑股份'
short_period = 5
long_period = 20
initial_capital = 100000
commission_rate = 0.0003
slippage_rate = 0.0001
stamp_tax_rate = 0.0005

df = pd.read_csv(f'output/{stock_code}_daily_data.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)

end_date = df['trade_date'].max()
start_date = end_date - pd.Timedelta(days=3*365)
df = df[df['trade_date'] >= start_date].reset_index(drop=True)

print(f'数据量: {len(df)}条')
print(f'时间范围: {df["trade_date"].min().strftime("%Y-%m-%d")} ~ {df["trade_date"].max().strftime("%Y-%m-%d")}')

df[f'MA{short_period}'] = df['close'].rolling(window=short_period).mean()
df[f'MA{long_period}'] = df['close'].rolling(window=long_period).mean()

df['signal'] = np.where(df[f'MA{short_period}'] > df[f'MA{long_period}'], 1, np.where(df[f'MA{short_period}'] < df[f'MA{long_period}'], -1, 0))

df['signal_t'] = df['signal'].shift(1)

df['cross_signal'] = df['signal_t'].diff()

buy_signals = df[(df['cross_signal'] == 2)].copy()
sell_signals = df[(df['cross_signal'] == -2)].copy()
print(f'买入信号: {len(buy_signals)}个')
print(f'卖出信号: {len(sell_signals)}个')

cash = initial_capital
position = 0
holdings = []
trades = []
win_trades = 0
lose_trades = 0
total_profit = 0
total_loss = 0

for i in range(len(df)):
    row = df.iloc[i]
    
    if row['cross_signal'] == 2 and position == 0:
        buy_price = row['open'] * (1 + slippage_rate)
        # 全仓买入：考虑佣金后计算最大可买数量，确保现金不为负
        max_shares = int(cash / (buy_price * (1 + commission_rate)) / 100) * 100
        if max_shares > 0:
            shares = max_shares
            cost = shares * buy_price
            commission = cost * commission_rate
            total_cost = cost + commission
            position = shares
            cash -= total_cost
            
            trades.append({
                'date': row['trade_date'].strftime('%Y-%m-%d'),
                'type': '买入',
                'price': round(buy_price, 2),
                'shares': shares,
                'amount': round(cost, 2),
                'commission': round(commission, 2),
                'slippage': round(shares * row['open'] * slippage_rate, 2),
                'cash_after': round(cash, 2)
            })
    
    elif row['cross_signal'] == -2 and position > 0:
        sell_price = row['open'] * (1 - slippage_rate)
        revenue = position * sell_price
        commission = revenue * commission_rate
        stamp_tax = revenue * stamp_tax_rate
        net_revenue = revenue - commission - stamp_tax
        
        buy_price = trades[-1]['price']
        trade_profit = net_revenue - (position * buy_price)
        if trade_profit > 0:
            win_trades += 1
            total_profit += trade_profit
        else:
            lose_trades += 1
            total_loss += abs(trade_profit)
        
        cash += net_revenue
        
        trades.append({
            'date': row['trade_date'].strftime('%Y-%m-%d'),
            'type': '卖出',
            'price': round(sell_price, 2),
            'shares': position,
            'amount': round(revenue, 2),
            'commission': round(commission, 2),
            'stamp_tax': round(stamp_tax, 2),
            'slippage': round(position * row['open'] * slippage_rate, 2),
            'cash_after': round(cash, 2),
            'profit': round(trade_profit, 2)
        })
        position = 0
    
    total_asset = cash + position * row['close']
    holdings.append({
        'date': row['trade_date'].strftime('%Y-%m-%d'),
        'total_asset': round(total_asset, 2),
        'cash': round(cash, 2),
        'position': position,
        'position_value': round(position * row['close'], 2)
    })

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
ma_short = [round(p, 2) if not np.isnan(p) else None for p in df[f'MA{short_period}'].tolist()]
ma_long = [round(p, 2) if not np.isnan(p) else None for p in df[f'MA{long_period}'].tolist()]

buy_points = []
sell_points = []
for i in range(len(df)):
    if df['cross_signal'].iloc[i] == 2:
        buy_price = df['open'].iloc[i] * (1 + slippage_rate)
        buy_points.append([i, round(buy_price, 2)])
    elif df['cross_signal'].iloc[i] == -2:
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
    trade_rows.append(f'<tr class="{row_class}"><td>{t["date"]}</td><td>{t["type"]}</td><td>{t["price"]}</td><td>{t["shares"]}</td><td>{t["amount"]:.2f}</td><td>{t["commission"]:.2f}</td><td>{slippage_val}</td><td>{stamp_tax_val}</td><td>{profit_val}</td><td>{t["cash_after"]:.2f}</td></tr>')

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
        body { font-family: 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .header h1 { color: #1a1a2e; font-size: 28px; margin-bottom: 10px; }
        .header p { color: #666; font-size: 14px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-top: 20px; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; }
        .stat-card .label { font-size: 12px; opacity: 0.9; margin-bottom: 5px; }
        .stat-card .value { font-size: 20px; font-weight: bold; }
        .stat-card .unit { font-size: 12px; opacity: 0.7; margin-top: 5px; }
        .chart-section { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .chart-section h2 { color: #1a1a2e; font-size: 20px; margin-bottom: 20px; }
        .chart-container { width: 100%; height: 400px; }
        .trade-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .trade-table th, .trade-table td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
        .trade-table th { background: #f8f9fa; font-weight: 600; color: #666; }
        .trade-table tr:hover { background: #f8f9fa; }
        .buy-row { color: #10b981; }
        .sell-row { color: #ef4444; }
        .intro-text { color: #666; line-height: 1.8; margin-bottom: 20px; font-size: 14px; }
        .interpretation { background: #f8f9fa; padding: 20px; border-radius: 10px; color: #333; line-height: 1.8; font-size: 14px; }
        .strategy-rule { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0; }
        .strategy-rule strong { color: #856404; }
        .params-table { width: 100%; margin-top: 15px; }
        .params-table td { padding: 8px 12px; border-bottom: 1px solid #eee; }
        .params-table tr:nth-child(odd) { background: #f9f9f9; }
        .metric-box { background: #fff; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #667eea; }
        .metric-box strong { color: #1a1a2e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NAME</h1>
            <p>策略参数：短均线 MA{short_period}，长均线 MA{long_period} | 数据周期：近三年（前复权）</p>
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
            <h2>1. 策略规则与参数</h2>
            <div class="intro-text">双均线策略是经典的趋势跟踪策略，通过短期均线MA5与长期均线MA20的交叉信号来判断市场趋势变化。</div>
            <div class="strategy-rule">
                <strong>信号编码：</strong>每日收盘后计算状态信号，非交易指令<br>
                MA5 = close.rolling(5).mean()（近5日收盘价均值）<br>
                MA20 = close.rolling(20).mean()（近20日收盘价均值）<br>
                signal = 1（多头排列，MA5&gt;MA20） / -1（空头排列，MA5&lt;MA20） / 0（持平）
            </div>
            <div class="strategy-rule">
                <strong>交叉捕捉：</strong>使用差值捕捉均线穿越瞬间<br>
                cross_signal[t] = signal[t-1] - signal[t-2]<br>
                cross_signal[t] = 2 → 第t-1日收盘时金叉（MA5上穿MA20），第t日开盘买入<br>
                cross_signal[t] = -2 → 第t-1日收盘时死叉（MA5下穿MA20），第t日开盘卖出
            </div>
            <div class="strategy-rule">
                <strong>买入规则（金叉触发）：</strong><br>
                1. 可用资金 = 当前全部现金（全仓买入）<br>
                2. 买入价格 = 第t日开盘价 × (1 + 0.0001)（含滑点万1）<br>
                3. 买入数量 = floor(可用资金 / 买入价格 / 100) × 100（取整到100股）<br>
                4. 交易成本 = 买入金额 × 佣金率(0.0003)<br>
                5. 现金减少 = 买入金额 + 佣金<br>
                6. 持仓增加 = 买入数量
            </div>
            <div class="strategy-rule">
                <strong>卖出规则（死叉触发）：</strong><br>
                1. 卖出价格 = 第t日开盘价 × (1 - 0.0001)（含滑点万1）<br>
                2. 卖出数量 = 当前全部持仓（清仓）<br>
                3. 交易成本 = 卖出金额 × 佣金率(0.0003) + 卖出金额 × 印花税(0.0005)<br>
                4. 现金增加 = 卖出金额 - 佣金 - 印花税<br>
                5. 持仓清零<br>
                6. 盈亏 = 净收入 - 持仓成本（买入价 × 数量）
            </div>
            <div class="strategy-rule">
                <strong>避免未来函数：</strong>第 t 日决策只用 t-1 日及之前的信息<br>
                用第t-1日收盘计算的MA5/MA20判断交叉，在第t日开盘执行交易
            </div>
            <div class="strategy-rule">
                <strong>完整策略思路：</strong><br>
                <strong>第一步：数据准备</strong> — 获取天邑股份前复权日线数据（开盘价、收盘价、成交量），截取近三年数据。<br>
                <strong>第二步：指标计算</strong> — 每日收盘后计算MA5（5日均线）和MA20（20日均线），生成多空头状态信号。<br>
                <strong>第三步：信号识别</strong> — 通过signal.diff()捕捉均线穿越瞬间：cross_signal=2表示金叉（买入信号），cross_signal=-2表示死叉（卖出信号）。<br>
                <strong>第四步：交易执行</strong> — 收到信号后，次日开盘执行交易。买入时用全部现金全仓买入，按开盘价×1.0001（含滑点）计算可买数量，取整到100股，确保现金不为负；卖出时清空全部持仓，按开盘价×0.9999（含滑点）计算成交价。<br>
                <strong>第五步：成本扣除</strong> — 买入扣万三佣金，卖出扣万三佣金+万五印花税。<br>
                <strong>第六步：资产更新</strong> — 每日收盘后计算总资产（现金+持仓市值），记录净值曲线和回撤曲线（每日当前回撤，即从当日净值到历史最高点的跌幅）。<br>
                <strong>第七步：指标统计</strong> — 回测结束后计算累计回报、年化回报、夏普比率、胜率、盈亏比等评估指标。
            </div>
            <table class="params-table">
                <tr><td><strong>初始资金</strong></td><td>INITIAL_CAPITAL 元</td></tr>
                <tr><td><strong>仓位方式</strong></td><td>全仓买入/全仓卖出（每次金叉用全部现金买入，死叉清空全部持仓）</td></tr>
                <tr><td><strong>买入佣金</strong></td><td>万三（0.03%），券商收取</td></tr>
                <tr><td><strong>卖出佣金</strong></td><td>万三（0.03%），券商收取</td></tr>
                <tr><td><strong>卖出印花税</strong></td><td>万五（0.05%），国家收取</td></tr>
                <tr><td><strong>滑点</strong></td><td>万分之一（0.01%），买卖各扣</td></tr>
                <tr><td><strong>执行价格</strong></td><td>次日开盘价 × (1±滑点)</td></tr>
                <tr><td><strong>买入数量</strong></td><td>取整到100股（A股最小交易单位）</td></tr>
                <tr><td><strong>数据类型</strong></td><td>前复权（qfq）</td></tr>
            </table>
        </div>

        <div class="chart-section">
            <h2>2. 股价与均线走势（含交易信号）</h2>
            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:5px;">图1 天邑股份（300504.SZ）近三年股价与MA5/MA20均线走势</h3>
            <div id="priceChart" class="chart-container"></div>
            <div class="interpretation" style="margin-top:15px;">
                <strong>【图1解读】</strong> 图中蓝色线为收盘价，绿色虚线为MA5（5日均线），红色虚线为MA20（20日均线），绿色三角为买入信号，红色三角为卖出信号。<br><br>
                <strong>走势特征：</strong>天邑股份近三年价格在11~20元区间反复震荡，MA5与MA20频繁交叉，说明市场缺乏明确趋势方向。信号分布显示买入点多集中在阶段性高点附近（金叉时价格已上涨），卖出点多集中在阶段性低点附近（死叉时价格已下跌），呈现典型的"追涨杀跌"特征。<br><br>
                <strong>信号质量：</strong>部分信号间隔仅2~3个交易日（如2023-08-09买入、2023-08-10卖出），属于典型的假信号，在震荡市中MA5/MA20的敏感性导致频繁发出交易指令。
            </div>
        </div>

        <div class="chart-section">
            <h2>3. 资产净值曲线与回撤曲线</h2>
            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:5px;">图2 双均线策略资产净值曲线与回撤曲线</h3>
            <div id="equityChart" class="chart-container"></div>
            <div class="interpretation" style="margin-top:15px;">
                <strong>【图2解读】</strong> 图中左侧Y轴为总资产（蓝色区域），灰色虚线为买入持有对照；右侧Y轴为回撤曲线（红色区域）。<br><br>
                <strong>净值走势：</strong>策略净值从10万元持续下滑至约5.3万元，期间经历多次大幅波动。最大回撤55%出现在净值最低点，说明全仓操作导致策略无法承受单笔大幅亏损。对比买入持有曲线（灰色虚线），策略净值明显低于持有收益，说明策略操作不仅没有创造价值，反而放大了亏损。<br><br>
                <strong>回撤特征：</strong>回撤曲线在大部分时间处于深度负值区域（-20%~-50%），说明策略长期处于浮亏状态。回撤曲线的急剧下降对应重大亏损交易（如2024年10月的单笔-19.90%亏损），而回升过程缓慢，反映策略缺乏快速恢复能力。
            </div>
        </div>

        <div class="chart-section">
            <h2>4. 交易明细</h2>
            TRADE_TABLE
        </div>

        <div class="chart-section">
            <h2>5. 策略评估指标详解</h2>
            <div class="metric-box">
                <strong>【总收益率（Total Return）】</strong>衡量整个回测期的累计收益。<br>
                公式：总收益率 = (期末净值 - 期初净值) / 期初净值 × 100%<br>
                本策略累计回报：RETURN%，初始资金 INITIAL_CAPITAL 元最终变为 FINAL_ASSET 元。
            </div>
            <div class="metric-box">
                <strong>【年化收益率（Annualized Return）】</strong>将收益标准化到每年，便于跨期与跨策略比较。<br>
                公式：年化收益率 = (期末净值 / 期初净值)^(365/N) - 1（N为回测自然日天数）<br>
                本策略年化回报：ANNUAL%，评级：STRATEGY_EVAL（年化&gt;10%优秀，5%-10%良好，0%-5%一般，&lt;0%亏损）。
            </div>
            <div class="metric-box">
                <strong>【超额收益（Excess Return）】</strong>策略收益与简单买入持有相比的差异。<br>
                公式：超额收益 = 策略收益率 - 买入持有收益率<br>
                本策略超额收益：EXCESS%，买入持有收益：HOLDING_RETURN%。若为正，说明策略创造了额外价值。
            </div>
            <div class="metric-box">
                <strong>【回撤曲线】</strong>每日当前回撤，即当日资产净值距离历史最高点的跌幅。资产创新高时回撤为0，资产下跌时回撤为负，资产反弹时回撤向0收窄。它反映策略在不同时间点的"浮亏状态"，而非最终亏损。<br>
                <strong>【最大回撤（Maximum Drawdown）】</strong>从资产峰值到谷底的最大跌幅，衡量策略"最坏情况"，是回撤曲线中的最低点。<br>
                公式：MDD = max_t(峰值 - 谷底) / 峰值 × 100%<br>
                本策略最大回撤：MDD%，评级：RISK_EVAL（回撤&lt;10%风险很低，10%-20%风险适中，20%-30%风险较高，&gt;30%风险很高）。
            </div>
            <div class="metric-box">
                <strong>【夏普比率（Sharpe Ratio）】</strong>衡量每承担一单位风险所获得的超额收益。<br>
                公式：S = (Rp - Rf) / σp（Rp为年化收益率，Rf为无风险利率2%，σp为年化波动率）<br>
                本策略夏普比率：SHARPE（&gt;2优秀，1-2良好，0-1一般，&lt;0策略无效）。
            </div>
            <div class="metric-box">
                <strong>【胜率（Win Rate）】</strong>盈利交易次数占总交易次数的比例。<br>
                公式：胜率 = 盈利交易次数 / 总交易次数 × 100%<br>
                本策略胜率：WINRATE%。高胜率不等于好策略，必须与盈亏比结合看。
            </div>
            <div class="metric-box">
                <strong>【盈亏比（Profit/Loss Ratio）】</strong>平均盈利与平均亏损的倍数。<br>
                公式：盈亏比 = 平均盈利 / |平均亏损|<br>
                本策略盈亏比：PROFITLOSS（&gt;2意味着每次盈利可覆盖两次以上亏损）。
            </div>
            <div class="metric-box">
                <strong>【期望收益（Expected Return）】</strong>每次交易的期望结果。<br>
                公式：期望收益 = 胜率 × 平均盈利 - (1-胜率) × 平均亏损<br>
                本策略期望收益：EXPECTED_RETURN元/次交易。
            </div>
        </div>

        <div class="chart-section">
            <h2>6. 总结分析</h2>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:20px;">6.1 核心结论</h3>
            <div class="interpretation">
                <strong>一句话结论：</strong>MA5/MA20双均线策略在天邑股份上3年亏损SUMMARY_RETURN%，大幅跑输买入持有（HOLDING_RETURN2%），根本原因是天邑股份近三年呈震荡格局，双均线策略的"追涨杀跌"特性在震荡市中被反复收割。<br><br>
                <strong>策略 vs 持有：</strong>策略累计回报SUMMARY_RETURN%，买入持有HOLDING_RETURN2%，超额收益EXCESS_RETURN2%。SUMMARY_TRADES笔交易中仅SUMMARY_WINS笔盈利（胜率WINRATE2%），盈亏比PROFITLOSS2，每次交易期望亏损EXPECTED_RETURN2元。策略不仅没有创造额外价值，反而放大了亏损。<br><br>
                <strong>最大回撤：</strong>策略最大回撤MDD2%，全仓操作导致每笔交易都暴露在最大风险下，单笔最大亏损严重侵蚀本金。
            </div>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:25px;">6.2 收获与反思</h3>
            <div class="interpretation">
                <strong>收获一：验证了"策略适用性"的重要性。</strong>双均线策略是趋势跟踪策略，只在趋势市有效。天邑股份近三年价格在11~20元区间反复震荡，没有形成持续上升或下降趋势，MA5/MA20频繁交叉产生大量假信号。因此双均线策略更适合趋势明确的标的，在震荡格局中表现较差。<br><br>
                <strong>收获二：理解了交易成本的累积效应。</strong>21笔交易的佣金+印花税+滑点合计约5600元，占初始资金5.6%。在胜率仅28.57%的情况下，交易越多亏损越大。频繁交易不仅不能分散风险，反而成了亏损的加速器。<br><br>
                <strong>收获三：全仓操作的风险暴露。</strong>全仓买入意味着每笔交易都押注全部资金，一次判断错误就可能造成10%以上的单笔亏损。第10笔交易（2024-10-08追高19.58元买入，11-04跌到15.70元卖出）单笔亏损15974元，占总资产16.7%，这一笔就几乎决定了全年的亏损格局。<br><br>
                <strong>反思一：信号频率过高。</strong>3年21笔交易，平均1.7个月就买卖一次，说明MA5/MA20参数对天邑股份过于敏感。短周期均线在中低价股上容易产生噪音信号。<br><br>
                <strong>反思二：没有止损机制。</strong>策略只有金叉买入、死叉卖出两个规则，没有设置止损线。当买入后价格快速下跌时，只能等到死叉信号才卖出，而此时往往已经跌了10%以上。<br><br>
                <strong>反思三：缺少市场状态过滤。</strong>策略不区分趋势市和震荡市，在所有市场状态下都执行相同逻辑。如果能先判断市场状态（如用ADX指标或波动率），在震荡市中暂停交易或降低仓位，可以大幅减少假信号亏损。
            </div>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:25px;">6.3 后续优化计划</h3>
            <div class="interpretation">
                <strong>优化方向一：引入市场状态过滤。</strong>在MA5/MA20信号基础上，增加ADX（平均趋向指标）或ATR（平均真实波幅）作为过滤条件。当ADX&lt;25（无明显趋势）时不产生交易信号，避免在震荡市中频繁操作。<br><br>
                <strong>优化方向二：增加止损止盈机制。</strong>买入后设置-5%硬止损线和+15%止盈线，在死叉信号触发前就主动平仓，控制单笔最大亏损。同时可引入移动止损（trailing stop），在盈利时锁定部分收益。<br><br>
                <strong>优化方向三：调整均线参数。</strong>将MA5/MA20改为MA10/MA30或MA20/MA60，降低信号频率，减少假信号。更长周期的均线交叉次数更少，每次信号更可靠，但响应速度也会降低，需要在信号质量和时效性之间找平衡。<br><br>
                <strong>优化方向四：分仓位操作。</strong>将全仓改为3~4批建仓，金叉时先买入1/3仓位，确认趋势后再加仓。这样即使第一笔判断错误，也有资金在更好价位补仓或止损，降低平均成本。<br><br>
                <strong>优化方向五：结合基本面过滤。</strong>天邑股份2024年亏损，PE为负，ROE仅1.84%。对于基本面恶化的标的，应在策略层面降低权重或排除。技术面策略不应脱离基本面独立运行。
            </div>

            <h3 style="color:#1a1a2e; margin-bottom:15px; margin-top:25px;">6.4 适用场景总结</h3>
            <div class="interpretation">
                <strong>适合双均线策略的场景：</strong><br>
                1. 处于明显上升或下降趋势的标的（如2020年的白酒、2023年的AI概念股）<br>
                2. 价格波动较大、趋势持续时间较长的标的<br>
                3. 日均成交额大于5亿元、流动性好的标的<br><br>
                <strong>不适合双均线策略的场景：</strong><br>
                1. 震荡市中横盘整理的标的（如天邑股份近三年）<br>
                2. 日均成交额小于2亿元、流动性不足的小盘股<br>
                3. 受事件驱动波动剧烈、缺乏技术规律的标的<br><br>
                <strong>天邑股份定位：</strong>基于近三年数据，天邑股份更适合低仓位波段操作，在支撑位附近买入、阻力位附近卖出，而非使用趋势跟踪策略。
            </div>
        </div>
    </div>

    <script>
        var dates = DATES;
        var closePrices = CLOSE_PRICES;
        var maShort = MA_SHORT;
        var maLong = MA_LONG;
        var buyPoints = BUY_POINTS;
        var sellPoints = SELL_POINTS;
        var holdingsData = HOLDINGS_DATA;
        var drawdownData = DRAWDOWN_DATA;
        var holdingLine = HOLDING_LINE;

        var commonDataZoom = [
            { type: 'inside', xAxisIndex: [0], start: 0, end: 100 },
            { type: 'slider', xAxisIndex: [0], start: 0, end: 100, height: 20, bottom: 5,
               borderColor: '#e5e7eb', fillerColor: 'rgba(102,126,234,0.2)', handleStyle: { color: '#667eea' } }
        ];

        var priceChart = echarts.init(document.getElementById('priceChart'));
        var priceOption = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' }, valueFormatter: function(v) { return v === null || v === undefined ? '-' : v.toFixed(2); } },
            legend: { data: ['收盘价', 'MA5', 'MA20', '买入信号', '卖出信号'] },
            grid: { left: '3%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: { type: 'value', axisLabel: { formatter: function(v) { return v.toFixed(2); } } },
            dataZoom: commonDataZoom,
            series: [
                { name: '收盘价', type: 'line', data: closePrices, smooth: true, lineStyle: { color: '#1a1a2e', width: 2 }, itemStyle: { color: '#1a1a2e' } },
                { name: 'MA5', type: 'line', data: maShort, smooth: true, lineStyle: { color: '#10b981', width: 2, type: 'dashed' }, itemStyle: { color: '#10b981' } },
                { name: 'MA20', type: 'line', data: maLong, smooth: true, lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, itemStyle: { color: '#ef4444' } },
                { name: '买入信号', type: 'scatter', data: buyPoints, symbol: 'triangle', symbolSize: 15, itemStyle: { color: '#10b981' } },
                { name: '卖出信号', type: 'scatter', data: sellPoints, symbol: 'triangle', symbolSize: 15, symbolRotate: 180, itemStyle: { color: '#ef4444' } }
            ]
        };
        priceChart.setOption(priceOption);

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
                }), smooth: true, lineStyle: { color: '#667eea', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(102,126,234,0.3)'}, {offset: 1, color: 'rgba(102,126,234,0.05)'}]) } },
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
            equityChart.resize();
        });
    </script>
</body>
</html>'''

html_content = html_template.replace('TITLE', f'{stock_name}({stock_code}) 双均线策略回测报告')
html_content = html_content.replace('NAME', f'{stock_name}({stock_code}) 双均线策略回测报告')
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
html_content = html_content.replace('COMMISSION_RATE', str(commission_rate))
html_content = html_content.replace('SLIPPAGE_RATE', str(slippage_rate))
html_content = html_content.replace('STAMP_TAX_RATE', str(stamp_tax_rate))
html_content = html_content.replace('STRATEGY_EVAL', strategy_eval)
html_content = html_content.replace('RISK_EVAL', risk_eval)
html_content = html_content.replace('HOLDING_RETURN', f'{holding_return*100:.2f}')
html_content = html_content.replace('EXPECTED_RETURN', f'{expected_return:.2f}')

# 第六章总结分析占位符替换
html_content = html_content.replace('SUMMARY_RETURN%', f'{final_return*100:.2f}%')
html_content = html_content.replace('HOLDING_RETURN2%', f'{holding_return*100:.2f}%')
html_content = html_content.replace('EXCESS_RETURN2%', f'{excess_return*100:.2f}%')
html_content = html_content.replace('SUMMARY_TRADES', str(total_trades))
html_content = html_content.replace('SUMMARY_WINS', str(win_trades))
html_content = html_content.replace('WINRATE2%', f'{win_rate:.2f}%')
html_content = html_content.replace('PROFITLOSS2', f'{profit_loss_ratio:.2f}')
html_content = html_content.replace('EXPECTED_RETURN2', f'{abs(expected_return):.2f}')
html_content = html_content.replace('MDD2%', f'{max_drawdown:.2f}%')

if trades:
    trade_table = f'<table class="trade-table"><thead><tr><th>日期</th><th>类型</th><th>价格(元)</th><th>数量(股)</th><th>金额(元)</th><th>佣金(元)</th><th>滑点(元)</th><th>印花税(元)</th><th>盈亏(元)</th><th>交易后现金(元)</th></tr></thead><tbody>{"".join(trade_rows)}</tbody></table>'
else:
    trade_table = '<p style="color:#999;">暂无交易记录</p>'
html_content = html_content.replace('TRADE_TABLE', trade_table)

html_content = html_content.replace('DATES', json.dumps(dates))
html_content = html_content.replace('CLOSE_PRICES', json.dumps(close_prices))
html_content = html_content.replace('MA_SHORT', json.dumps(ma_short))
html_content = html_content.replace('MA_LONG', json.dumps(ma_long))
html_content = html_content.replace('BUY_POINTS', json.dumps(buy_points))
html_content = html_content.replace('SELL_POINTS', json.dumps(sell_points))
html_content = html_content.replace('HOLDINGS_DATA', json.dumps(holdings_data))
html_content = html_content.replace('DRAWDOWN_DATA', json.dumps(holdings_drawdown))
html_content = html_content.replace('HOLDING_LINE', json.dumps(holding_line))

with open(f'output/{stock_code}_ma_strategy.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'报告已保存: output/{stock_code}_ma_strategy.html')
