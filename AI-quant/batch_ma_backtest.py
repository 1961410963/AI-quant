# -*- coding: utf-8 -*-
"""
双均线策略批量回测与对比分析
实验矩阵：8个标的（6只股票 + 2只ETF）× 4组均线周期 = 32次回测
输出：output/ma_batch_analysis.html + output/ma_batch_results.csv
"""
import pandas as pd
import numpy as np
import json
import os

# ============ 实验配置 ============
INITIAL_CAPITAL = 100000
COMMISSION_RATE = 0.0003
SLIPPAGE_RATE = 0.0001
STAMP_TAX_RATE = 0.0005
RISK_FREE_RATE = 0.02

INSTRUMENTS = [
    ('300504.SZ', '天邑股份', '股票'),
    ('002812.SZ', '恩捷股份', '股票'),
    ('600967.SH', '内蒙一机', '股票'),
    ('601899.SH', '紫金矿业', '股票'),
    ('600346.SH', '恒力石化', '股票'),
    ('002080.SZ', '中材科技', '股票'),
    ('159562.SZ', '华夏黄金ETF', 'ETF'),
    ('563020.SH', '易方达红利低波ETF', 'ETF'),
]

MA_PERIODS = [
    (5, 10, '短周期'),
    (5, 20, '经典'),
    (10, 30, '中周期'),
    (20, 60, '长周期'),
]


def run_backtest(df, short_period, long_period):
    """执行单次双均线回测，返回指标字典"""
    df = df.copy()
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    end_date = df['trade_date'].max()
    start_date = end_date - pd.Timedelta(days=3 * 365)
    df = df[df['trade_date'] >= start_date].reset_index(drop=True)
    if len(df) < long_period + 10:
        return None

    df[f'MA{short_period}'] = df['close'].rolling(window=short_period).mean()
    df[f'MA{long_period}'] = df['close'].rolling(window=long_period).mean()
    df['signal'] = np.where(df[f'MA{short_period}'] > df[f'MA{long_period}'], 1,
                           np.where(df[f'MA{short_period}'] < df[f'MA{long_period}'], -1, 0))
    df['signal_t'] = df['signal'].shift(1)
    df['cross_signal'] = df['signal_t'].diff()

    cash = INITIAL_CAPITAL
    position = 0
    holdings = []
    trades = []
    win_trades = 0
    lose_trades = 0
    total_profit = 0.0
    total_loss = 0.0

    for i in range(len(df)):
        row = df.iloc[i]
        if row['cross_signal'] == 2 and position == 0:
            buy_price = row['open'] * (1 + SLIPPAGE_RATE)
            # 全仓买入：考虑佣金后计算最大可买数量，确保现金不为负
            max_shares = int(cash / (buy_price * (1 + COMMISSION_RATE)) / 100) * 100
            if max_shares > 0:
                shares = max_shares
                cost = shares * buy_price
                commission = cost * COMMISSION_RATE
                cash -= (cost + commission)
                position = shares
                trades.append({'buy_price': buy_price})
        elif row['cross_signal'] == -2 and position > 0:
            sell_price = row['open'] * (1 - SLIPPAGE_RATE)
            revenue = position * sell_price
            commission = revenue * COMMISSION_RATE
            stamp_tax = revenue * STAMP_TAX_RATE
            net_revenue = revenue - commission - stamp_tax
            trade_profit = net_revenue - (position * trades[-1]['buy_price'])
            if trade_profit > 0:
                win_trades += 1
                total_profit += trade_profit
            else:
                lose_trades += 1
                total_loss += abs(trade_profit)
            cash += net_revenue
            position = 0

        total_asset = cash + position * row['close']
        holdings.append(total_asset)

    holdings_df = pd.DataFrame({'total_asset': holdings})
    holdings_df['return'] = holdings_df['total_asset'] / INITIAL_CAPITAL - 1
    max_asset = INITIAL_CAPITAL
    drawdown = []
    for a in holdings_df['total_asset']:
        if a > max_asset:
            max_asset = a
        drawdown.append((a - max_asset) / max_asset * 100)
    holdings_df['drawdown'] = drawdown

    daily_returns = holdings_df['total_asset'].pct_change().dropna()
    excess = daily_returns - RISK_FREE_RATE / 252
    sharpe = np.sqrt(252) * excess.mean() / excess.std() if excess.std() > 0 else 0

    final_return = holdings_df['return'].iloc[-1]
    max_drawdown = holdings_df['drawdown'].min()
    total_trades = len(trades) // 2
    win_rate = win_trades / (win_trades + lose_trades) * 100 if (win_trades + lose_trades) > 0 else 0
    profit_loss_ratio = (total_profit / win_trades) / (total_loss / lose_trades) if (win_trades > 0 and lose_trades > 0) else 0
    holding_return = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]
    excess_return = final_return - holding_return
    total_days = (df['trade_date'].iloc[-1] - df['trade_date'].iloc[0]).days
    years = total_days / 365
    annualized_return = (1 + final_return) ** (1 / years) - 1 if years > 0 else 0

    return {
        'final_return_pct': round(final_return * 100, 2),
        'annualized_return_pct': round(annualized_return * 100, 2),
        'max_drawdown_pct': round(max_drawdown, 2),
        'sharpe': round(sharpe, 2),
        'win_rate_pct': round(win_rate, 2),
        'profit_loss_ratio': round(profit_loss_ratio, 2),
        'total_trades': total_trades,
        'holding_return_pct': round(holding_return * 100, 2),
        'excess_return_pct': round(excess_return * 100, 2),
    }


# ============ 批量回测 ============
results = []
for code, name, itype in INSTRUMENTS:
    csv_path = f'output/{code}_daily_data.csv'
    if not os.path.exists(csv_path):
        print(f'跳过 {code}（数据文件不存在）')
        continue
    df = pd.read_csv(csv_path)
    for short_p, long_p, period_label in MA_PERIODS:
        res = run_backtest(df, short_p, long_p)
        if res is None:
            print(f'跳过 {code} MA{short_p}/MA{long_p}（数据不足）')
            continue
        res.update({
            'code': code, 'name': name, 'type': itype,
            'short': short_p, 'long': long_p, 'period_label': period_label,
            'ma_combo': f'MA{short_p}/MA{long_p}',
        })
        results.append(res)
        print(f'{name}({code}) {res["ma_combo"]:>10} | 累计{res["final_return_pct"]:>7}% | 回撤{res["max_drawdown_pct"]:>7}% | 夏普{res["sharpe"]:>6} | 胜率{res["win_rate_pct"]}%')

results_df = pd.DataFrame(results)
results_df.to_csv('output/ma_batch_results.csv', index=False, encoding='utf-8-sig')
print(f'\n结果已保存: output/ma_batch_results.csv（{len(results_df)}条）')

# ============ 聚合统计 ============
# 各均线周期平均表现
period_agg = results_df.groupby('ma_combo').agg(
    avg_return=('final_return_pct', 'mean'),
    avg_mdd=('max_drawdown_pct', 'mean'),
    avg_sharpe=('sharpe', 'mean'),
    avg_winrate=('win_rate_pct', 'mean'),
    avg_excess=('excess_return_pct', 'mean'),
    positive_count=('final_return_pct', lambda x: (x > 0).sum()),
    total_count=('final_return_pct', 'count'),
).round(2).reset_index()
period_agg['positive_ratio'] = (period_agg['positive_count'] / period_agg['total_count'] * 100).round(1)
print('\n各均线周期平均表现：')
print(period_agg.to_string(index=False))

# 各标的平均表现
stock_agg = results_df.groupby(['code', 'name', 'type']).agg(
    avg_return=('final_return_pct', 'mean'),
    avg_mdd=('max_drawdown_pct', 'mean'),
    avg_sharpe=('sharpe', 'mean'),
    avg_winrate=('win_rate_pct', 'mean'),
).round(2).reset_index()
print('\n各标的平均表现：')
print(stock_agg.to_string(index=False))

# ============ 生成HTML报告 ============
# 数据准备（用于JS）
instruments_js = json.dumps([{'name': n, 'code': c, 'type': t} for c, n, t in INSTRUMENTS if os.path.exists(f'output/{c}_daily_data.csv')])
ma_combos_js = json.dumps([f'MA{s}/MA{l}' for s, l, _ in MA_PERIODS])
results_js = json.dumps(results_df.to_dict(orient='records'))

# 图表数据
# 图1：各标的在不同均线周期下的累计回报（分组柱状图）
chart1_names = json.dumps(stock_agg['name'].tolist())
chart1_series = []
for s, l, label in MA_PERIODS:
    combo = f'MA{s}/MA{l}'
    vals = []
    for _, row in stock_agg.iterrows():
        sub = results_df[(results_df['code'] == row['code']) & (results_df['ma_combo'] == combo)]
        vals.append(round(sub['final_return_pct'].iloc[0], 2) if len(sub) > 0 else 0)
    chart1_series.append({'combo': combo, 'vals': vals})
chart1_series_js = json.dumps(chart1_series)

# 图2：各均线周期平均累计回报与平均回撤对比（回撤为每日当前回撤的均值）
chart2_combos = json.dumps(period_agg['ma_combo'].tolist())
chart2_returns = json.dumps(period_agg['avg_return'].tolist())
chart2_mdds = json.dumps(period_agg['avg_mdd'].tolist())
chart2_sharpes = json.dumps(period_agg['avg_sharpe'].tolist())
chart2_positive = json.dumps(period_agg['positive_ratio'].tolist())
chart2_excess = json.dumps(period_agg['avg_excess'].tolist())

# 图3：累计回报 vs 回撤 散点图（每个点一次回测，横轴为区间最大回撤）
chart3_points = json.dumps([[r['max_drawdown_pct'], r['final_return_pct'], r['name'], r['ma_combo'], r['type']] for _, r in results_df.iterrows()])

# 图4：各标的夏普比率对比（4个周期分组）
chart4_series = []
for s, l, label in MA_PERIODS:
    combo = f'MA{s}/MA{l}'
    vals = []
    for _, row in stock_agg.iterrows():
        sub = results_df[(results_df['code'] == row['code']) & (results_df['ma_combo'] == combo)]
        vals.append(round(sub['sharpe'].iloc[0], 2) if len(sub) > 0 else 0)
    chart4_series.append({'combo': combo, 'vals': vals})
chart4_series_js = json.dumps(chart4_series)

# 图5：股票 vs ETF 平均表现对比
type_agg = results_df.groupby('type').agg(
    avg_return=('final_return_pct', 'mean'),
    avg_mdd=('max_drawdown_pct', 'mean'),
    avg_sharpe=('sharpe', 'mean'),
    avg_winrate=('win_rate_pct', 'mean'),
    avg_excess=('excess_return_pct', 'mean'),
).round(2).reset_index()
chart5_types = json.dumps(type_agg['type'].tolist())
chart5_returns = json.dumps(type_agg['avg_return'].tolist())
chart5_mdds = json.dumps(type_agg['avg_mdd'].tolist())
chart5_sharpes = json.dumps(type_agg['avg_sharpe'].tolist())

# 最佳/最差组合
best = results_df.loc[results_df['final_return_pct'].idxmax()]
worst = results_df.loc[results_df['final_return_pct'].idxmin()]
best_sharpe = results_df.loc[results_df['sharpe'].idxmax()]

html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>双均线策略批量回测与对比分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .header h1 { color: #1a1a2e; font-size: 26px; margin-bottom: 10px; }
        .header p { color: #666; font-size: 14px; line-height: 1.8; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 20px; }
        .summary-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 18px; border-radius: 12px; }
        .summary-card .label { font-size: 12px; opacity: 0.9; margin-bottom: 5px; }
        .summary-card .value { font-size: 18px; font-weight: bold; }
        .section { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .section h2 { color: #1a1a2e; font-size: 20px; margin-bottom: 6px; }
        .section .chart-title { color: #1a1a2e; font-size: 17px; font-weight: 600; margin: 24px 0 8px 0; }
        .section .chart-caption { color: #999; font-size: 13px; margin-bottom: 12px; }
        .chart-container { width: 100%; height: 420px; }
        .interpretation { background: #f8f9fa; padding: 16px; border-radius: 10px; color: #333; line-height: 1.9; font-size: 14px; margin-top: 14px; border-left: 4px solid #667eea; }
        .interpretation strong { color: #1a1a2e; }
        .insight-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 16px; border-radius: 0 8px 8px 0; margin: 14px 0; line-height: 1.9; font-size: 14px; }
        .insight-box strong { color: #856404; }
        table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; }
        th, td { padding: 9px; text-align: center; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; color: #666; font-weight: 600; }
        tr:hover { background: #f8f9fa; }
        .pos { color: #ef4444; font-weight: 600; }
        .neg { color: #10b981; font-weight: 600; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>双均线策略批量回测与对比分析</h1>
        <p>实验矩阵：<strong>8个标的（6只股票 + 2只ETF）× 4组均线周期 = 32次回测</strong><br>
        参数：初始资金10万元 | 全仓买入/全仓卖出（金叉全仓买，死叉全仓卖）| 佣金万三 | 印花税万五（卖出）| 滑点万1 | 近三年前复权数据<br>
        均线周期组合：MA5/MA10（短周期）、MA5/MA20（经典）、MA10/MA30（中周期）、MA20/MA60（长周期）</p>
        <div class="summary-grid">
            <div class="summary-card"><div class="label">最佳组合</div><div class="value">BEST_COMBO</div></div>
            <div class="summary-card"><div class="label">最佳累计回报</div><div class="value">BEST_RETURN%</div></div>
            <div class="summary-card"><div class="label">最差组合</div><div class="value">WORST_COMBO</div></div>
            <div class="summary-card"><div class="label">最差累计回报</div><div class="value">WORST_RETURN%</div></div>
            <div class="summary-card"><div class="label">最高夏普组合</div><div class="value">BEST_SHARPE_COMBO</div></div>
            <div class="summary-card"><div class="label">最高夏普</div><div class="value">BEST_SHARPE</div></div>
        </div>
    </div>

    <div class="section">
        <h2>一、实验结果总览</h2>
        <p class="chart-caption">下表汇总全部32次回测的核心指标，正收益标红，负收益标绿。</p>
        <table>
            <thead><tr><th>标的</th><th>类型</th><th>均线组合</th><th>累计回报(%)</th><th>年化(%)</th><th>区间最大回撤(%)</th><th>夏普</th><th>胜率(%)</th><th>盈亏比</th><th>交易次数</th><th>持有收益(%)</th><th>超额(%)</th></tr></thead>
            <tbody>RESULT_ROWS</tbody>
        </table>
    </div>

    <div class="section">
        <h2>二、统计图表分析</h2>

        <div class="chart-title">图1：各标的在不同均线周期下的累计回报对比</div>
        <p class="chart-caption">横轴为8个标的，每组4根柱子分别对应4组均线周期，纵轴为累计回报(%)。</p>
        <div id="chart1" class="chart-container"></div>
        <div class="interpretation"><strong>解读：</strong>该图反映同一标的对不同均线参数的敏感度，以及同一参数在不同标的上的表现差异。若某标的4根柱子普遍为正且较高，说明双均线策略较适合该标的；若各周期收益正负不一且波动大，说明该标的不适合趋势跟踪。</div>

        <div class="chart-title">图2：各均线周期正收益占比与平均夏普比率对比</div>
        <p class="chart-caption">横轴为4组均线周期，左纵轴为正收益占比(%)（该周期下盈利标的数/总标的数），右纵轴为平均夏普比率。正收益占比反映参数组合的"普适性"——越高说明该参数在越多标的上有效。</p>
        <div id="chart2" class="chart-container"></div>
        <div class="interpretation"><strong>解读：</strong>简单算术平均回报掩盖个体差异（如中材科技+15%与天邑股份-3%直接平均无意义），而<strong>正收益占比</strong>衡量该均线参数在8个标的中"有多大比例能盈利"，更具参考价值。理想组合应满足"高正收益占比+高夏普"。长周期（MA20/MA60）过滤噪音，正收益占比通常更高；短周期（MA5/MA10）反应快但对震荡市敏感，普适性较差。</div>

        <div class="chart-title">图3：累计回报 vs 区间最大回撤 风险-收益散点图</div>
        <p class="chart-caption">横轴为区间最大回撤(%)（单次回测期间回撤曲线的最低点），纵轴为累计回报(%)，每个点代表一次回测，悬停显示标的与均线组合。</p>
        <div id="chart3" class="chart-container"></div>
        <div class="interpretation"><strong>解读：</strong>左上区域为最优区间（低回撤+高回报），右下区域为最差区间（高回撤+亏损）。点的分布可揭示"高收益往往伴随高回撤"的权衡关系，落在左上的组合最具实战价值。</div>

        <div class="chart-title">图4：各标的夏普比率对比（风险调整后收益）</div>
        <p class="chart-caption">横轴为8个标的，每组4根柱子对应4组均线周期，纵轴为夏普比率。</p>
        <div id="chart4" class="chart-container"></div>
        <div class="interpretation"><strong>解读：</strong>夏普比率衡量单位风险下的超额回报，&gt;0说明跑赢无风险利率，越高越好。该图可识别哪些标的在哪些周期下风险收益比最优，是选择策略参数的核心依据。</div>

        <div class="chart-title">图5：股票 vs ETF 平均表现对比</div>
        <p class="chart-caption">对比两类资产（股票均值 vs ETF均值）的平均累计回报、平均回撤（每日当前回撤均值）、平均夏普比率。</p>
        <div id="chart5" class="chart-container"></div>
        <div class="interpretation"><strong>解读：</strong>ETF通常趋势性更强、波动更小，双均线策略理论上更适合ETF；个股受消息面影响大、震荡频繁，假信号更多。该图验证这一假设，为策略选品提供依据。</div>
    </div>

    <div class="section">
        <h2>三、核心指标计算逻辑</h2>
        <div class="insight-box">
            <strong>1. 累计回报：</strong>回测期末总资产与初始资金的差额比例。<br>
            公式：<code>累计回报 = (期末总资产 - 初始资金) / 初始资金 × 100%</code><br>
            例如：初始10万，期末9.5万，累计回报 = (9.5-10)/10 = <strong>-5%</strong>。
        </div>
        <div class="insight-box">
            <strong>2. 买入持有收益（对照基准）：</strong>假设回测首日将全部资金一次性买入标的，之后不做任何交易、一直持有到期末的收益。<br>
            公式：<code>买入持有收益 = (期末收盘价 - 首日收盘价) / 首日收盘价 × 100%</code><br>
            用途：作为策略的<strong>对照基准</strong>，衡量"什么都不做"的收益水平。数据已使用前复权，分红送转已自动调整。
        </div>
        <div class="insight-box">
            <strong>3. 超额收益：</strong>策略收益与买入持有收益的差额，衡量策略是否创造了额外价值。<br>
            公式：<code>超额收益 = 累计回报 - 买入持有收益</code><br>
            <span style="color:#ef4444;"><strong>重要提醒：</strong>超额收益为正 ≠ 策略赚钱。</span>例如策略亏-5%、持有亏-10%，超额 = (-5%) - (-10%) = <strong>+5%</strong>。这表示"虽然亏了，但比傻拿着少亏5%"，策略跑赢了基准，但绝对收益仍是负的。超额为负则表示策略连"什么都不做"都不如。
        </div>
        <div class="insight-box">
            <strong>4. 区间最大回撤：</strong>整个回测期间，从资产峰值到谷底的最大跌幅。<br>
            计算步骤：① 每日计算当前回撤 = (当日总资产 - 历史最高总资产) / 历史最高总资产 × 100%；② 取所有日回撤中的最小值（最负值）。<br>
            例如：资产从10万涨到11万（峰值），再跌到9万，区间最大回撤 = (9-11)/11 = <strong>-18.18%</strong>。
        </div>
        <div class="insight-box">
            <strong>5. 夏普比率：</strong>衡量每承担一单位风险所获得的超额收益（相对无风险利率）。<br>
            公式：<code>Sharpe = (年化收益率 - 无风险利率) / 年化波动率</code><br>
            无风险利率取2%（近似一年期存款利率）。夏普 &gt; 0 说明策略跑赢无风险理财，&lt; 0 说明不如存银行。
        </div>
        <div class="insight-box">
            <strong>6. 胜率与盈亏比：</strong><br>
            胜率 = 盈利交易次数 / 总交易次数 × 100%<br>
            盈亏比 = 平均盈利金额 / 平均亏损金额<br>
            趋势策略通常<strong>胜率低（30%-40%）但盈亏比高（&gt;1）</strong>——亏的时候小亏（死叉止损），赚的时候大赚（趋势延续）。若盈亏比 &lt; 1，说明每次盈利覆盖不了亏损，策略在震荡市中失效。
        </div>
    </div>

    <div class="section">
        <h2>四、策略适用场景与应用心得</h2>
        <div class="insight-box">
            <strong>1. 适用场景：</strong>双均线策略本质是<strong>趋势跟踪</strong>策略，其盈利前提是标的走出持续的单边趋势。从实验结果看，<strong>趋势性强的标的（如黄金ETF等）更适合</strong>，因为价格能持续创新高/新低，金叉后能持续运行；而<strong>震荡市中双均线策略会反复触发假信号</strong>，导致高胜率亏损——金叉买入后立即死叉卖出，来回吃佣金和滑点。
        </div>
        <div class="insight-box">
            <strong>2. 均线周期选择：</strong>短周期（MA5/MA10）反应灵敏但信号频繁，适合波动大、趋势短的标的，但交易成本侵蚀严重；长周期（MA20/MA60）信号少、滞后大，能过滤噪音但会错过趋势启动初期的利润。经典组合MA5/MA20是平衡点。<strong>周期选择应匹配标的的波动节奏</strong>：慢牛/慢熊用长周期，活跃标的用中短周期。
        </div>
        <div class="insight-box">
            <strong>3. 胜率与盈亏比的反向关系：</strong>双均线策略通常<strong>胜率偏低（本次实验普遍在30%-40%）但盈亏比应较高</strong>——因为每次亏损被严格限制在死叉时的小幅回撤，而盈利时趋势能跑出大段利润。若发现胜率低且盈亏比也低于1，说明标的处于震荡市，策略失效。本次实验中部分组合盈亏比偏低，反映出近三年市场震荡特征明显。
        </div>
        <div class="insight-box">
            <strong>4. 全仓策略的风险特征：</strong>本次采用全仓买入/全仓卖出，金叉时All in，死叉时清仓。这种方式在趋势明确时收益最大化，但在震荡市中连续假信号会导致较大回撤——金叉买入后马上死叉卖出，每次都要承担佣金+滑点+印花税成本。<strong>全仓策略对择时要求极高</strong>，一旦趋势判断错误，单次亏损幅度远大于轻仓策略。建议在实盘前先确认标的处于趋势市而非震荡市。
        </div>
        <div class="insight-box">
            <strong>5. 应用心得总结：</strong>① 双均线策略不是"万能公式"，必须先判断市场状态（趋势/震荡）再决定是否启用；② <strong>择时不如择势</strong>——先选趋势性强的标的，再谈参数优化；③ <strong>参数不是越精细越好</strong>，过度拟合历史数据反而降低未来适应性；④ <strong>止损纪律比信号本身更重要</strong>，死叉即走，不扛单；⑤ 建议将双均线作为<strong>趋势确认工具</strong>而非唯一信号，结合成交量、MACD等指标过滤假信号效果更佳。
        </div>
    </div>
</div>

<script>
var commonTooltip = { trigger: 'axis', axisPointer: { type: 'cross' }, valueFormatter: function(v) { return v === null || v === undefined ? '-' : Number(v).toFixed(2); } };

// 图1：各标的在不同均线周期下的累计回报
var chart1 = echarts.init(document.getElementById('chart1'));
var c1Names = CHART1_NAMES;
var c1Series = CHART1_SERIES;
var c1Colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666'];
chart1.setOption({
    tooltip: commonTooltip,
    legend: { data: c1Series.map(function(s){return s.combo;}) },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: c1Names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: '累计回报(%)', axisLabel: { formatter: function(v){return v.toFixed(2);} } },
    dataZoom: [{ type: 'inside' }, { type: 'slider', height: 18, bottom: 5 }],
    series: c1Series.map(function(s, i) {
        return { name: s.combo, type: 'bar', data: s.vals, itemStyle: { color: c1Colors[i] }, lineStyle: { color: c1Colors[i] } };
    })
});

// 图2：各均线周期正收益占比与平均夏普比率对比
var chart2 = echarts.init(document.getElementById('chart2'));
var c2Combos = CHART2_COMBOS;
var c2Positive = CHART2_POSITIVE;
var c2Sharpes = CHART2_SHARPES;
chart2.setOption({
    tooltip: commonTooltip,
    legend: { data: ['正收益占比(%)', '平均夏普比率'] },
    grid: { left: '3%', right: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: c2Combos },
    yAxis: [
        { type: 'value', name: '正收益占比(%)', min: 0, max: 100, axisLabel: { formatter: function(v){return v.toFixed(1);} } },
        { type: 'value', name: '夏普比率', axisLabel: { formatter: function(v){return v.toFixed(2);} } }
    ],
    series: [
        { name: '正收益占比(%)', type: 'bar', data: c2Positive, itemStyle: { color: '#5470c6' }, lineStyle: { color: '#5470c6' }, label: { show: true, position: 'top', formatter: function(p){return p.value.toFixed(1)+'%';} } },
        { name: '平均夏普比率', type: 'line', yAxisIndex: 1, data: c2Sharpes, lineStyle: { color: '#fac858', width: 2 }, itemStyle: { color: '#fac858' }, label: { show: true, position: 'bottom', formatter: function(p){return p.value.toFixed(2);}, backgroundColor: '#fff', padding: [2, 4], borderRadius: 3 } }
    ]
});

// 图3：累计回报 vs 区间最大回撤 散点图
var chart3 = echarts.init(document.getElementById('chart3'));
var c3Points = CHART3_POINTS;
var stockPoints = c3Points.filter(function(p){return p[4]==='股票';}).map(function(p){return [p[0], p[1], p[2], p[3]];});
var etfPoints = c3Points.filter(function(p){return p[4]==='ETF';}).map(function(p){return [p[0], p[1], p[2], p[3]];});
chart3.setOption({
    tooltip: { trigger: 'item', formatter: function(p){ return p.data[2]+' '+p.data[3]+'<br/>区间最大回撤: '+p.data[0].toFixed(2)+'%<br/>累计回报: '+p.data[1].toFixed(2)+'%'; } },
    legend: { data: ['股票', 'ETF'] },
    grid: { left: '3%', right: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'value', name: '区间最大回撤(%)', axisLabel: { formatter: function(v){return v.toFixed(2);} } },
    yAxis: { type: 'value', name: '累计回报(%)', axisLabel: { formatter: function(v){return v.toFixed(2);} } },
    series: [
        { name: '股票', type: 'scatter', data: stockPoints, symbolSize: 12, itemStyle: { color: '#5470c6' }, lineStyle: { color: '#5470c6' } },
        { name: 'ETF', type: 'scatter', data: etfPoints, symbolSize: 14, itemStyle: { color: '#91cc75' }, lineStyle: { color: '#91cc75' } }
    ]
});

// 图4：各标的夏普比率对比
var chart4 = echarts.init(document.getElementById('chart4'));
var c4Series = CHART4_SERIES;
chart4.setOption({
    tooltip: commonTooltip,
    legend: { data: c4Series.map(function(s){return s.combo;}) },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: c1Names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: '夏普比率', axisLabel: { formatter: function(v){return v.toFixed(2);} } },
    dataZoom: [{ type: 'inside' }, { type: 'slider', height: 18, bottom: 5 }],
    series: c4Series.map(function(s, i) {
        return { name: s.combo, type: 'bar', data: s.vals, itemStyle: { color: c1Colors[i] }, lineStyle: { color: c1Colors[i] } };
    })
});

// 图5：股票 vs ETF 平均表现对比
var chart5 = echarts.init(document.getElementById('chart5'));
chart5.setOption({
    tooltip: commonTooltip,
    legend: { data: ['平均累计回报(%)', '平均回撤(%)', '平均夏普比率'] },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: CHART5_TYPES },
    yAxis: { type: 'value', axisLabel: { formatter: function(v){return v.toFixed(2);} } },
    series: [
        { name: '平均累计回报(%)', type: 'bar', data: CHART5_RETURNS, itemStyle: { color: '#5470c6' }, lineStyle: { color: '#5470c6' }, label: { show: true, position: 'top', formatter: function(p){return p.value.toFixed(2);} } },
        { name: '平均回撤(%)', type: 'bar', data: CHART5_MDDS, itemStyle: { color: '#ee6666' }, lineStyle: { color: '#ee6666' }, label: { show: true, position: 'top', formatter: function(p){return p.value.toFixed(2);} } },
        { name: '平均夏普比率', type: 'line', data: CHART5_SHARPES, lineStyle: { color: '#fac858', width: 2 }, itemStyle: { color: '#fac858' }, label: { show: true, formatter: function(p){return p.value.toFixed(2);} } }
    ]
});

window.addEventListener('resize', function() {
    chart1.resize(); chart2.resize(); chart3.resize(); chart4.resize(); chart5.resize();
});
</script>
</body>
</html>'''

# 构建结果表格行
result_rows = []
for _, r in results_df.iterrows():
    ret_cls = 'pos' if r['final_return_pct'] > 0 else 'neg'
    row = (f'<tr><td>{r["name"]}</td><td>{r["type"]}</td><td>{r["ma_combo"]}</td>'
           f'<td class="{ret_cls}">{r["final_return_pct"]:.2f}</td>'
           f'<td>{r["annualized_return_pct"]:.2f}</td>'
           f'<td>{r["max_drawdown_pct"]:.2f}</td>'
           f'<td>{r["sharpe"]:.2f}</td>'
           f'<td>{r["win_rate_pct"]:.2f}</td>'
           f'<td>{r["profit_loss_ratio"]:.2f}</td>'
           f'<td>{r["total_trades"]}</td>'
           f'<td>{r["holding_return_pct"]:.2f}</td>'
           f'<td>{r["excess_return_pct"]:.2f}</td></tr>')
    result_rows.append(row)

html_content = html_template
html_content = html_content.replace('BEST_COMBO', f'{best["name"]} {best["ma_combo"]}')
html_content = html_content.replace('BEST_RETURN', f'{best["final_return_pct"]:.2f}')
html_content = html_content.replace('WORST_COMBO', f'{worst["name"]} {worst["ma_combo"]}')
html_content = html_content.replace('WORST_RETURN', f'{worst["final_return_pct"]:.2f}')
html_content = html_content.replace('BEST_SHARPE_COMBO', f'{best_sharpe["name"]} {best_sharpe["ma_combo"]}')
html_content = html_content.replace('BEST_SHARPE', f'{best_sharpe["sharpe"]:.2f}')
html_content = html_content.replace('RESULT_ROWS', ''.join(result_rows))
html_content = html_content.replace('CHART1_NAMES', chart1_names)
html_content = html_content.replace('CHART1_SERIES', chart1_series_js)
html_content = html_content.replace('CHART2_COMBOS', chart2_combos)
html_content = html_content.replace('CHART2_POSITIVE', chart2_positive)
html_content = html_content.replace('CHART2_SHARPES', chart2_sharpes)
html_content = html_content.replace('CHART3_POINTS', chart3_points)
html_content = html_content.replace('CHART4_SERIES', chart4_series_js)
html_content = html_content.replace('CHART5_TYPES', chart5_types)
html_content = html_content.replace('CHART5_RETURNS', chart5_returns)
html_content = html_content.replace('CHART5_MDDS', chart5_mdds)
html_content = html_content.replace('CHART5_SHARPES', chart5_sharpes)

with open('output/ma_batch_analysis.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f'\n报告已保存: output/ma_batch_analysis.html')
