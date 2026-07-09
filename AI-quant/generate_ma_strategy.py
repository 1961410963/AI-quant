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
stamp_tax_rate = 0.001

df = pd.read_csv(f'output/{stock_code}_daily_data.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date').reset_index(drop=True)
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
        shares = int(available_capital / row['open'] / 100) * 100
        if shares > 0:
            cost = shares * row['open']
            commission = cost * commission_rate
            total_cost = cost + commission
            position = shares
            cash -= total_cost
            
            trades.append({
                'date': row['trade_date'].strftime('%Y-%m-%d'),
                'type': '买入',
                'price': round(row['open'], 2),
                'shares': shares,
                'amount': round(cost, 2),
                'commission': round(commission, 2),
                'cash_after': round(cash, 2)
            })
    
    elif row['cross_signal'] == -2 and position > 0:
        revenue = position * row['open']
        commission = revenue * commission_rate
        stamp_tax = revenue * stamp_tax_rate
        net_revenue = revenue - commission - stamp_tax
        
        trade_profit = net_revenue - (position * trades[-1]['price'])
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
            'price': round(row['open'], 2),
            'shares': position,
            'amount': round(revenue, 2),
            'commission': round(commission, 2),
            'stamp_tax': round(stamp_tax, 2),
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
sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0

max_drawdown = holdings_df['drawdown'].min()
final_return = holdings_df['return'].iloc[-1]
final_asset = holdings_df['total_asset'].iloc[-1]
total_trades = len(trades) // 2

holding_return = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]
excess_return = final_return - holding_return

years = len(df) / 252
annualized_return = (1 + final_return) ** (1 / years) - 1 if years > 0 else 0

win_rate = win_trades / (win_trades + lose_trades) * 100 if (win_trades + lose_trades) > 0 else 0
profit_loss_ratio = (total_profit / win_trades) / (total_loss / lose_trades) if (win_trades > 0 and lose_trades > 0) else 0

print(f'交易次数: {total_trades}次')
print(f'最终资产: {final_asset:.2f}元')
print(f'累计回报: {final_return*100:.2f}%')
print(f'年化回报: {annualized_return*100:.2f}%')
print(f'超额收益: {excess_return*100:.2f}%')
print(f'最大回撤: {max_drawdown:.2f}%')
print(f'夏普比率: {sharpe_ratio:.2f}')
print(f'胜率: {win_rate:.2f}%')
print(f'盈亏比: {profit_loss_ratio:.2f}')
print(f'持有收益: {holding_return*100:.2f}%')

dates = [d.strftime('%Y-%m-%d') for d in df['trade_date']]
close_prices = [round(p, 2) for p in df['close'].tolist()]
ma_short = [round(p, 2) if not np.isnan(p) else None for p in df[f'MA{short_period}'].tolist()]
ma_long = [round(p, 2) if not np.isnan(p) else None for p in df[f'MA{long_period}'].tolist()]

buy_points = []
sell_points = []
for i in range(len(df)):
    if df['cross_signal'].iloc[i] == 2:
        buy_points.append([i, round(df['open'].iloc[i], 2)])
    elif df['cross_signal'].iloc[i] == -2:
        sell_points.append([i, round(df['open'].iloc[i], 2)])

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
    extra_cols = f'<td>{t["commission"]:.2f}</td><td>{t.get("stamp_tax", "-")}</td><td>{t.get("profit", "-")}</td>' if t['type'] == '卖出' else '<td>{t["commission"]:.2f}</td><td>-</td><td>-</td>'
    trade_rows.append(f'<tr class="{row_class}"><td>{t["date"]}</td><td>{t["type"]}</td><td>{t["price"]}</td><td>{t["shares"]}</td><td>{t["amount"]:.2f}</td>{extra_cols}<td>{t["cash_after"]:.2f}</td></tr>')

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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NAME</h1>
            <p>策略参数：短均线 MA{short_period}，长均线 MA{long_period} | 数据周期：前复权近三年</p>
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
                <tr><td><strong>印花税</strong></td><td>STAMP_TAX_RATE（卖出时扣除千一）</td></tr>
                <tr><td><strong>执行价格</strong></td><td>当日开盘价（避免未来函数）</td></tr>
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
            <h2>5. 策略评估</h2>
            <div class="interpretation">
                <strong>【累计回报】</strong>策略累计回报为 RETURN%，初始资金 INITIAL_CAPITAL 元最终变为 FINAL_ASSET 元。<br><br>
                <strong>【年化回报】</strong>年化收益率为 ANNUAL%，衡量策略在单位时间内的收益能力。<br><br>
                <strong>【超额收益】</strong>超额收益为 EXCESS%，策略收益与简单买入持有相比的差异。若为正，说明策略创造了额外价值；若为负，说明策略不如持有不动。<br><br>
                <strong>【最大回撤】</strong>策略最大回撤为 MDD%，反映了策略在最不利情况下的亏损幅度。回撤控制是衡量策略风险承受能力的重要指标。<br><br>
                <strong>【夏普比率】</strong>策略夏普比率为 SHARPE，衡量单位风险所获得的超额收益。一般认为夏普比率大于1为优秀，大于2为卓越。<br><br>
                <strong>【胜率】</strong>胜率为 WINRATE%，表示盈利交易次数占总交易次数的比例。胜率高意味着策略在多数交易中赚钱。<br><br>
                <strong>【盈亏比】</strong>盈亏比为 PROFITLOSS，表示平均盈利金额与平均亏损金额的比值。盈亏比大于1说明每次盈利能覆盖亏损。<br><br>
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
        var holdingLine = HOLDING_LINE;

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
            legend: { data: ['策略净值', '买入持有', '最大回撤'] },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
            yAxis: [
                { type: 'value', name: '资产净值(元)', position: 'left' },
                { type: 'value', name: '回撤(%)', position: 'right', axisLabel: { formatter: '{value}%' } }
            ],
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
html_content = html_content.replace('STAMP_TAX_RATE', str(stamp_tax_rate))
html_content = html_content.replace('EVAL', strategy_eval)
html_content = html_content.replace('RISK_EVAL', risk_eval)

if trades:
    trade_table = f'<table class="trade-table"><thead><tr><th>日期</th><th>类型</th><th>价格(元)</th><th>数量(股)</th><th>金额(元)</th><th>佣金(元)</th><th>印花税(元)</th><th>盈亏(元)</th><th>交易后现金(元)</th></tr></thead><tbody>{"".join(trade_rows)}</tbody></table>'
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
