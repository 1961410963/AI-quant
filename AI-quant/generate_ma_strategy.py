import pandas as pd
import numpy as np
import json

stock_code = '300504.SZ'
stock_name = '天邑股份'
short_period = 5
long_period = 20
initial_capital = 50000
position_ratio = 0.5
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
        available_capital = cash * position_ratio
        buy_price = row['open'] * (1 + slippage_rate)
        shares = int(available_capital / buy_price / 100) * 100
        if shares > 0:
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
            <div class="intro-text">双均线策略是经典的趋势跟踪策略，通过短期均线与长期均线的交叉信号来判断市场趋势变化。</div>
            <div class="strategy-rule">
                <strong>信号编码：</strong>每日状态信号，非交易指令<br>
                short_ma = close.rolling({short_period}).mean()<br>
                long_ma = close.rolling({long_period}).mean()<br>
                signal = 1（多头排列，短&gt;长） / -1（空头排列，短&lt;长） / 0（持平）
            </div>
            <div class="strategy-rule">
                <strong>交叉捕捉：</strong>使用差值而非直接比较，确保只在"穿越瞬间"触发<br>
                cross_signal = signal.diff()<br>
                cross_signal = 2 → 金叉买入 / cross_signal = -2 → 死叉卖出
            </div>
            <div class="strategy-rule">
                <strong>避免未来函数：</strong>第 t 日决策只用 t-1 日及之前的信息<br>
                signal_t = signal.shift(1)（用前一日信号在当日开盘执行）
            </div>
            <table class="params-table">
                <tr><td><strong>初始资金</strong></td><td>INITIAL_CAPITAL 元</td></tr>
                <tr><td><strong>仓位比例</strong></td><td>POSITION_RATIO%（固定比例建仓）</td></tr>
                <tr><td><strong>佣金费率</strong></td><td>COMMISSION_RATE（万三）</td></tr>
                <tr><td><strong>滑点</strong></td><td>SLIPPAGE_RATE（万分之一）</td></tr>
                <tr><td><strong>印花税</strong></td><td>STAMP_TAX_RATE（卖出时扣除万五）</td></tr>
                <tr><td><strong>执行价格</strong></td><td>当日开盘价 × (1±滑点)</td></tr>
                <tr><td><strong>数据类型</strong></td><td>前复权（qfq）</td></tr>
            </table>
        </div>

        <div class="chart-section">
            <h2>2. 股价与均线走势（含交易信号）</h2>
            <div id="priceChart" class="chart-container"></div>
        </div>

        <div class="chart-section">
            <h2>3. 资产净值曲线与最大回撤</h2>
            <div id="equityChart" class="chart-container"></div>
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
                <strong>【最大回撤（Maximum Drawdown）】</strong>从资产峰值到谷底的最大跌幅，衡量策略"最坏情况"。<br>
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
                本策略盈亏比：PROFITLOSS（&gt;2意味着每次盈利可覆盖两次亏损）。
            </div>
            <div class="metric-box">
                <strong>【期望收益（Expected Return）】</strong>每次交易的期望结果。<br>
                公式：期望收益 = 胜率 × 平均盈利 - (1-胜率) × 平均亏损<br>
                本策略期望收益：EXPECTED_RETURN元/次交易。
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
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
            legend: { data: ['收盘价', 'MA{short_period}', 'MA{long_period}', '买入信号', '卖出信号'] },
            grid: { left: '3%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: { type: 'value', axisLabel: { formatter: function(v) { return v.toFixed(2); } } },
            dataZoom: commonDataZoom,
            series: [
                { name: '收盘价', type: 'line', data: closePrices, smooth: true, lineStyle: { color: '#1a1a2e', width: 2 }, itemStyle: { color: '#1a1a2e' } },
                { name: 'MA{short_period}', type: 'line', data: maShort, smooth: true, lineStyle: { color: '#10b981', width: 2, type: 'dashed' } },
                { name: 'MA{long_period}', type: 'line', data: maLong, smooth: true, lineStyle: { color: '#ef4444', width: 2, type: 'dashed' } },
                { name: '买入信号', type: 'scatter', data: buyPoints, symbol: 'triangle', symbolSize: 15, itemStyle: { color: '#10b981' } },
                { name: '卖出信号', type: 'scatter', data: sellPoints, symbol: 'triangle', symbolSize: 15, symbolRotate: 180, itemStyle: { color: '#ef4444' } }
            ]
        };
        priceChart.setOption(priceOption);

        var equityChart = echarts.init(document.getElementById('equityChart'));
        var equityOption = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
            legend: { data: ['策略净值', '买入持有', '最大回撤'] },
            grid: { left: '3%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: [
                { type: 'value', name: '资产净值(元)', position: 'left' },
                { type: 'value', name: '回撤(%)', position: 'right', axisLabel: { formatter: '{value}%' } }
            ],
            dataZoom: commonDataZoom,
            series: [
                { name: '策略净值', type: 'line', yAxisIndex: 0, data: closePrices.map(function(p, i) {
                    var h = holdingsData.find(function(d) { return d[0] === i; });
                    return h ? h[1] : null;
                }), smooth: true, lineStyle: { color: '#667eea', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(102,126,234,0.3)'}, {offset: 1, color: 'rgba(102,126,234,0.05)'}]) } },
                { name: '买入持有', type: 'line', yAxisIndex: 0, data: holdingLine, smooth: true, lineStyle: { color: '#9ca3af', width: 2, type: 'dashed' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(156,163,175,0.2)'}, {offset: 1, color: 'rgba(156,163,175,0.02)'}]) } },
                { name: '最大回撤', type: 'line', yAxisIndex: 1, data: closePrices.map(function(p, i) {
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
html_content = html_content.replace('POSITION_RATIO', f'{position_ratio*100:.0f}')
html_content = html_content.replace('COMMISSION_RATE', str(commission_rate))
html_content = html_content.replace('SLIPPAGE_RATE', str(slippage_rate))
html_content = html_content.replace('STAMP_TAX_RATE', str(stamp_tax_rate))
html_content = html_content.replace('STRATEGY_EVAL', strategy_eval)
html_content = html_content.replace('RISK_EVAL', risk_eval)
html_content = html_content.replace('HOLDING_RETURN', f'{holding_return*100:.2f}')
html_content = html_content.replace('EXPECTED_RETURN', f'{expected_return:.2f}')

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
