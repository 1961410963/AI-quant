import pandas as pd
import numpy as np
import json

stock_code = '300504.SZ'
stock_name = '天邑股份'
short_period = 5
long_period = 20

df = pd.read_csv(f'output/{stock_code}_daily_data.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)
print(f'数据量: {len(df)}条')
print(f'时间范围: {df["trade_date"].min().strftime("%Y-%m-%d")} ~ {df["trade_date"].max().strftime("%Y-%m-%d")}')

df[f'MA{short_period}'] = df['close'].rolling(window=short_period).mean()
df[f'MA{long_period}'] = df['close'].rolling(window=long_period).mean()

df['prev_MA_short'] = df[f'MA{short_period}'].shift(1)
df['prev_MA_long'] = df[f'MA{long_period}'].shift(1)

df['signal'] = 0
golden_mask = (df[f'MA{short_period}'] > df[f'MA{long_period}']) & (df['prev_MA_short'] <= df['prev_MA_long'])
death_mask = (df[f'MA{short_period}'] < df[f'MA{long_period}']) & (df['prev_MA_short'] >= df['prev_MA_long'])
df.loc[golden_mask, 'signal'] = 1
df.loc[death_mask, 'signal'] = -1

buy_count = len(df[df['signal'] == 1])
sell_count = len(df[df['signal'] == -1])
print(f'买入信号: {buy_count}个')
print(f'卖出信号: {sell_count}个')

position = 0
cash = 100000
initial_cash = cash
holdings = []
trades = []

for i in range(len(df)):
    row = df.iloc[i]
    if row['signal'] == 1 and position == 0:
        shares = int(cash / row['close'])
        cost = shares * row['close']
        position = shares
        cash -= cost
        trades.append({
            'date': row['trade_date'].strftime('%Y-%m-%d'),
            'type': '买入',
            'price': round(row['close'], 2),
            'shares': shares,
            'amount': round(cost, 2),
            'cash_after': round(cash, 2)
        })
    elif row['signal'] == -1 and position > 0:
        revenue = position * row['close']
        cash += revenue
        trades.append({
            'date': row['trade_date'].strftime('%Y-%m-%d'),
            'type': '卖出',
            'price': round(row['close'], 2),
            'shares': position,
            'amount': round(revenue, 2),
            'cash_after': round(cash, 2)
        })
    
    if position > 0:
        holdings.append({
            'date': row['trade_date'].strftime('%Y-%m-%d'),
            'total_asset': round(cash + position * row['close'], 2)
        })

final_return = 0
max_drawdown = 0
sharpe_ratio = 0
total_trades = len(trades)
final_asset = initial_cash

if holdings:
    holdings_df = pd.DataFrame(holdings)
    holdings_df['return'] = holdings_df['total_asset'] / initial_cash - 1
    
    drawdown = []
    max_asset = initial_cash
    for _, row in holdings_df.iterrows():
        if row['total_asset'] > max_asset:
            max_asset = row['total_asset']
        drawdown.append((row['total_asset'] - max_asset) / max_asset * 100)
    holdings_df['drawdown'] = drawdown
    
    daily_returns = holdings_df['total_asset'].pct_change().dropna()
    sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0
    
    max_drawdown = holdings_df['drawdown'].min()
    final_return = holdings_df['return'].iloc[-1]
    final_asset = holdings_df['total_asset'].iloc[-1]

print(f'交易次数: {total_trades}次')
print(f'最终资产: {final_asset:.2f}元')
print(f'累计回报: {final_return*100:.2f}%')
print(f'最大回撤: {max_drawdown:.2f}%')
print(f'夏普比率: {sharpe_ratio:.2f}')

dates = [d.strftime('%Y-%m-%d') for d in df['trade_date']]
close_prices = [round(p, 2) for p in df['close'].tolist()]
ma_short = [round(p, 2) if not np.isnan(p) else None for p in df[f'MA{short_period}'].tolist()]
ma_long = [round(p, 2) if not np.isnan(p) else None for p in df[f'MA{long_period}'].tolist()]

buy_points = []
sell_points = []
for i in range(len(df)):
    if df['signal'].iloc[i] == 1:
        buy_points.append([i, round(df['close'].iloc[i], 2)])
    elif df['signal'].iloc[i] == -1:
        sell_points.append([i, round(df['close'].iloc[i], 2)])

holdings_data = []
holdings_drawdown = []
if len(holdings_df) > 0:
    holdings_dates = holdings_df['date'].tolist()
    holdings_assets = [round(a, 2) for a in holdings_df['total_asset'].tolist()]
    holdings_drawdown = [round(d, 2) for d in holdings_df['drawdown'].tolist()]
    for d, a in zip(holdings_dates, holdings_assets):
        idx = dates.index(d) if d in dates else -1
        if idx >= 0:
            holdings_data.append([idx, a])

trade_rows = []
for t in trades:
    row_class = 'buy-row' if t['type'] == '买入' else 'sell-row'
    trade_rows.append(f'<tr class="{row_class}"><td>{t["date"]}</td><td>{t["type"]}</td><td>{t["price"]}</td><td>{t["shares"]}</td><td>{t["amount"]:.2f}</td><td>{t["cash_after"]:.2f}</td></tr>')

strategy_eval = '优秀' if final_return > 0.3 else '良好' if final_return > 0.1 else '一般' if final_return >= 0 else '较差'
risk_eval = '最大回撤控制在合理范围内。' if abs(max_drawdown) < 30 else '但最大回撤较大，需注意风险控制。'

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
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 20px; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; }
        .stat-card .label { font-size: 12px; opacity: 0.9; margin-bottom: 5px; }
        .stat-card .value { font-size: 24px; font-weight: bold; }
        .stat-card .unit { font-size: 12px; opacity: 0.7; margin-top: 5px; }
        .chart-section { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .chart-section h2 { color: #1a1a2e; font-size: 20px; margin-bottom: 20px; }
        .chart-container { width: 100%; height: 400px; }
        .trade-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .trade-table th, .trade-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .trade-table th { background: #f8f9fa; font-weight: 600; color: #666; }
        .trade-table tr:hover { background: #f8f9fa; }
        .buy-row { color: #10b981; }
        .sell-row { color: #ef4444; }
        .intro-text { color: #666; line-height: 1.8; margin-bottom: 20px; font-size: 14px; }
        .interpretation { background: #f8f9fa; padding: 20px; border-radius: 10px; color: #333; line-height: 1.8; font-size: 14px; }
        .strategy-rule { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0; }
        .strategy-rule strong { color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NAME</h1>
            <p>策略参数：短均线 MA{short_period}，长均线 MA{long_period} | 数据周期：前复权近三年</p>
            <div class="stats-grid">
                <div class="stat-card"><div class="label">累计回报</div><div class="value">RETURN%</div><div class="unit">vs 初始资金</div></div>
                <div class="stat-card"><div class="label">最大回撤</div><div class="value">MDD%</div><div class="unit">MDD</div></div>
                <div class="stat-card"><div class="label">夏普比率</div><div class="value">SHARPE</div><div class="unit">年化</div></div>
                <div class="stat-card"><div class="label">交易次数</div><div class="value">TRADES</div><div class="unit">次</div></div>
            </div>
        </div>

        <div class="chart-section">
            <h2>1. 策略规则</h2>
            <div class="intro-text">双均线策略是经典的趋势跟踪策略，通过短期均线与长期均线的交叉信号来判断市场趋势变化。</div>
            <div class="strategy-rule">
                <strong>金叉（买入信号）：</strong>短期均线（MA{short_period}）从下方上穿长期均线（MA{long_period}）<br>
                条件：MA<sub>short(t)</sub> &gt; MA<sub>long(t)</sub> 且 MA<sub>short(t-1)</sub> ≤ MA<sub>long(t-1)</sub>
            </div>
            <div class="strategy-rule">
                <strong>死叉（卖出信号）：</strong>短期均线（MA{short_period}）从上方下穿长期均线（MA{long_period}）<br>
                条件：MA<sub>short(t)</sub> &lt; MA<sub>long(t)</sub> 且 MA<sub>short(t-1)</sub> ≥ MA<sub>long(t-1)</sub>
            </div>
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
            <h2>5. 策略评估</h2>
            <div class="interpretation">
                <strong>【累计回报】</strong>策略累计回报为 RETURN%，初始资金 100000 元最终变为 FINAL_ASSET 元。<br><br>
                <strong>【最大回撤】</strong>策略最大回撤为 MDD%，反映了策略在最不利情况下的亏损幅度。<br><br>
                <strong>【夏普比率】</strong>策略夏普比率为 SHARPE，衡量单位风险所获得的超额收益。<br><br>
                <strong>【交易频率】</strong>共执行 TRADES 次交易，平均约 AVG_DAYS 个交易日交易一次。<br><br>
                <strong>【策略评价】</strong>该双均线策略（MA{short_period}/{long_period}）在{stock_name}上表现{EVAL}，{RISK_EVAL}
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

        var priceChart = echarts.init(document.getElementById('priceChart'));
        var priceOption = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
            legend: { data: ['收盘价', 'MA{short_period}', 'MA{long_period}', '买入信号', '卖出信号'] },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: { type: 'value', axisLabel: { formatter: function(v) { return v.toFixed(2); } } },
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
            legend: { data: ['资产净值', '最大回撤'] },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: [
                { type: 'value', name: '资产净值(元)', position: 'left' },
                { type: 'value', name: '回撤(%)', position: 'right', axisLabel: { formatter: '{value}%' } }
            ],
            series: [
                { name: '资产净值', type: 'line', yAxisIndex: 0, data: closePrices.map(function(p, i) {
                    var h = holdingsData.find(function(d) { return d[0] === i; });
                    return h ? h[1] : null;
                }), smooth: true, lineStyle: { color: '#667eea', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(102,126,234,0.3)'}, {offset: 1, color: 'rgba(102,126,234,0.05)'}]) } },
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
html_content = html_content.replace('MDD%', f'{max_drawdown:.2f}%')
html_content = html_content.replace('SHARPE', f'{sharpe_ratio:.2f}')
html_content = html_content.replace('TRADES', str(total_trades))
html_content = html_content.replace('FINAL_ASSET', f'{final_asset:.2f}')
html_content = html_content.replace('AVG_DAYS', f'{len(df)/total_trades:.0f}' if total_trades > 0 else '-')
html_content = html_content.replace('EVAL', strategy_eval)
html_content = html_content.replace('RISK_EVAL', risk_eval)

if trades:
    trade_table = f'<table class="trade-table"><thead><tr><th>日期</th><th>类型</th><th>价格(元)</th><th>数量(股)</th><th>金额(元)</th><th>交易后现金(元)</th></tr></thead><tbody>{"".join(trade_rows)}</tbody></table>'
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

with open(f'output/{stock_code}_ma_strategy.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'报告已保存: output/{stock_code}_ma_strategy.html')
