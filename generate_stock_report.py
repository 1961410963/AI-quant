import pandas as pd
import json
import os
import numpy as np
import sys
from datetime import datetime, timedelta

TUSHARE_TOKEN = '2dfed09895f11acd0fc988685ccf1c1bd0898b14a9526bcffb4cefac'


def calc_ema(data, n):
    ema = [data[0]]
    multiplier = 2 / (n + 1)
    for i in range(1, len(data)):
        ema.append(data[i] * multiplier + ema[-1] * (1 - multiplier))
    return ema


def calc_macd(close):
    ema12 = calc_ema(close, 12)
    ema26 = calc_ema(close, 26)
    dif = [ema12[i] - ema26[i] for i in range(len(close))]
    dea = calc_ema(dif, 9)
    macd = [dif[i] - dea[i] for i in range(len(close))]
    for i in range(26):
        dif[i] = float('nan')
        dea[i] = float('nan')
        macd[i] = float('nan')
    return dif, dea, macd


def calc_rsi(close, n=14):
    delta = pd.Series(close).diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi[:n] = float('nan')
    return rsi.tolist()


def calc_kdj(high, low, close, n=9, m1=3, m2=3):
    df = pd.DataFrame({'high': high, 'low': low, 'close': close})
    low_min = df['low'].rolling(window=n).min()
    high_max = df['high'].rolling(window=n).max()
    rsv = 100 * (df['close'] - low_min) / (high_max - low_min)
    k = rsv.ewm(com=m1 - 1, adjust=False).mean()
    d = k.ewm(com=m2 - 1, adjust=False).mean()
    j = 3 * k - 2 * d
    return k.tolist(), d.tolist(), j.tolist()


def calc_boll(close, n=20):
    ma = pd.Series(close).rolling(window=n).mean().tolist()
    std = pd.Series(close).rolling(window=n).std(ddof=0).tolist()
    upper = [ma[i] + 2 * std[i] if std[i] == std[i] else None for i in range(len(close))]
    lower = [ma[i] - 2 * std[i] if std[i] == std[i] else None for i in range(len(close))]
    return ma, upper, lower


def calc_atr(high, low, close, n=14):
    high_s = pd.Series(high)
    low_s = pd.Series(low)
    close_s = pd.Series(close)
    prev_close = close_s.shift(1)
    tr1 = high_s - low_s
    tr2 = (high_s - prev_close).abs()
    tr3 = (low_s - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/n, adjust=False).mean()
    atr[:n] = float('nan')
    return tr.tolist(), atr.tolist()


def get_stock_data(ts_code, days=365, output_dir='output'):
    csv_path = os.path.join(output_dir, f'{ts_code}_daily_data.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        print(f'从本地CSV加载数据: {csv_path}')
        return df

    try:
        import tushare as ts
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        df = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, adj='qfq', freq='D')
        if df is not None and not df.empty:
            df = df.sort_values('trade_date').reset_index(drop=True)
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(csv_path, index=False)
            print(f'从Tushare获取数据并保存: {csv_path}')
            return df
    except Exception as e:
        print(f'Tushare获取失败: {e}')

    raise FileNotFoundError(f'无法获取{ts_code}的数据，请检查CSV文件或Tushare配置')


def generate_html_report(ts_code, stock_name, total_shares_yi, csv_path=None, output_dir='output'):
    if csv_path is None:
        df = get_stock_data(ts_code, output_dir=output_dir)
    else:
        df = pd.read_csv(csv_path)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date').reset_index(drop=True)

    dates = [d.strftime('%Y-%m-%d') for d in df['trade_date']]
    kline_data = [[round(row['open'], 2), round(row['close'], 2), round(row['low'], 2), round(row['high'], 2)]
                  for _, row in df.iterrows()]
    close_prices = df['close'].tolist()
    high_prices = df['high'].tolist()
    low_prices = df['low'].tolist()

    volumes = []
    for _, row in df.iterrows():
        vol = round(row['vol'], 0)
        is_up = row['close'] >= row['open']
        volumes.append({'value': vol, 'itemStyle': {'color': '#ef4444' if is_up else '#22c55e'}})

    def calc_ma(data, n):
        result = []
        for i in range(len(data)):
            if i < n - 1:
                result.append(None)
            else:
                s = sum(data[i - n + 1:i + 1]) / n
                result.append(round(s, 2))
        return result

    ma5 = calc_ma(close_prices, 5)
    ma10 = calc_ma(close_prices, 10)
    ma20 = calc_ma(close_prices, 20)
    ma60 = calc_ma(close_prices, 60)

    dif, dea, macd = calc_macd(close_prices)
    rsi = calc_rsi(close_prices)
    k, d, j = calc_kdj(high_prices, low_prices, close_prices)
    boll_mid, boll_upper, boll_lower = calc_boll(close_prices)
    tr_list, atr_list = calc_atr(high_prices, low_prices, close_prices)

    start_date_str = df['trade_date'].min().strftime('%Y年%m月%d日')
    end_date_str = df['trade_date'].max().strftime('%Y年%m月%d日')
    trading_days = len(df)
    highest_price = round(df['high'].max(), 2)
    lowest_price = round(df['low'].min(), 2)
    highest_date = df.loc[df['high'].idxmax(), 'trade_date'].strftime('%Y-%m-%d')
    lowest_date = df.loc[df['low'].idxmin(), 'trade_date'].strftime('%Y-%m-%d')
    start_price = round(df['close'].iloc[0], 2)
    end_price = round(df['close'].iloc[-1], 2)
    change_pct = round((end_price - start_price) / start_price * 100, 2)
    avg_price = round(df['close'].mean(), 2)
    avg_volume = round(df['vol'].mean(), 0)
    avg_amount = round(df['amount'].mean(), 0)
    avg_amount_yi = avg_amount / 100000
    up_days = len(df[df['close'] > df['open']])
    down_days = len(df[df['close'] < df['open']])
    flat_days = len(df[df['close'] == df['open']])
    up_ratio = round(up_days / trading_days * 100, 1)
    price_std = df['close'].std()
    volatility = round(price_std / avg_price * 100, 2)

    df['year'] = df['trade_date'].dt.year
    yearly_stats = []
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        year_start = year_df['close'].iloc[0]
        year_end = year_df['close'].iloc[-1]
        year_change = round((year_end - year_start) / year_start * 100, 2)
        year_high = round(year_df['high'].max(), 2)
        year_low = round(year_df['low'].min(), 2)
        year_days = len(year_df)
        year_up = len(year_df[year_df['close'] > year_df['open']])
        year_down = len(year_df[year_df['close'] < year_df['open']])
        year_up_ratio = round(year_up / year_days * 100, 1)
        year_avg_vol = round(year_df['vol'].mean(), 0)
        yearly_stats.append({
            'year': year, 'start': year_start, 'end': year_end, 'change': year_change,
            'high': year_high, 'low': year_low, 'days': year_days, 'up': year_up,
            'down': year_down, 'up_ratio': year_up_ratio, 'avg_vol': year_avg_vol
        })

    latest_idx = len(close_prices) - 1
    latest_dif = round(dif[latest_idx], 3)
    latest_dea = round(dea[latest_idx], 3)
    latest_macd = round(macd[latest_idx], 3)
    latest_rsi = round(rsi[latest_idx], 2) if rsi[latest_idx] == rsi[latest_idx] else '-'
    latest_k = round(k[latest_idx], 2) if k[latest_idx] == k[latest_idx] else '-'
    latest_d = round(d[latest_idx], 2) if d[latest_idx] == d[latest_idx] else '-'
    latest_j = round(j[latest_idx], 2) if j[latest_idx] == j[latest_idx] else '-'
    latest_boll_mid = round(boll_mid[latest_idx], 2) if boll_mid[latest_idx] is not None else '-'
    latest_boll_upper = round(boll_upper[latest_idx], 2) if boll_upper[latest_idx] is not None else '-'
    latest_boll_lower = round(boll_lower[latest_idx], 2) if boll_lower[latest_idx] is not None else '-'
    latest_atr = round(atr_list[latest_idx], 2) if atr_list[latest_idx] == atr_list[latest_idx] else '-'
    latest_atr_pct = round(atr_list[latest_idx] / close_prices[latest_idx] * 100, 2) if atr_list[latest_idx] == atr_list[latest_idx] else '-'

    market_cap_now = round(end_price * total_shares_yi, 2)
    avg_turnover = round(avg_volume / (total_shares_yi * 10000) * 100, 2)

    dates_json = json.dumps(dates)
    kline_json = json.dumps(kline_data)
    volumes_json = json.dumps(volumes)
    ma5_json = json.dumps(ma5)
    ma10_json = json.dumps(ma10)
    ma20_json = json.dumps(ma20)
    ma60_json = json.dumps(ma60)
    dif_json = json.dumps([round(x, 3) for x in dif])
    dea_json = json.dumps([round(x, 3) for x in dea])
    macd_json = json.dumps([round(x, 3) for x in macd])
    rsi_json = json.dumps([round(x, 2) if x == x else None for x in rsi])
    k_json = json.dumps([round(x, 2) if x == x else None for x in k])
    d_json = json.dumps([round(x, 2) if x == x else None for x in d])
    j_json = json.dumps([round(x, 2) if x == x else None for x in j])
    boll_mid_json = json.dumps([round(x, 2) if x is not None else None for x in boll_mid])
    boll_upper_json = json.dumps([round(x, 2) if x is not None else None for x in boll_upper])
    boll_lower_json = json.dumps([round(x, 2) if x is not None else None for x in boll_lower])
    tr_json = json.dumps([round(x, 2) if x == x else None for x in tr_list])
    atr_json = json.dumps([round(x, 2) if x == x else None for x in atr_list])
    close_json = json.dumps([round(x, 2) for x in close_prices])

    yearly_rows = ''
    for y in yearly_stats:
        color = '#ef4444' if y['change'] >= 0 else '#22c55e'
        sign = '+' if y['change'] >= 0 else ''
        yearly_rows += f'''<tr><td>{y['year']}年</td><td>{y['start']:.2f}</td><td>{y['end']:.2f}</td>
            <td style="color:{color};font-weight:600;">{sign}{y['change']}%</td>
            <td>{y['high']:.2f}</td><td>{y['low']:.2f}</td>
            <td>{y['days']}</td><td>{y['up']}/{y['down']}</td>
            <td>{y['up_ratio']}%</td><td>{y['avg_vol']:,.0f}</td></tr>'''

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{stock_name}（{ts_code}）近一年交易数据分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    background: #ffffff; color: #333333; line-height: 1.8;
}}
.container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
.header {{
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
    border-radius: 16px; padding: 40px 48px; margin-bottom: 32px;
    box-shadow: 0 10px 40px rgba(30, 64, 175, 0.15);
}}
.header h1 {{ font-size: 32px; font-weight: 700; color: #ffffff; margin-bottom: 12px; }}
.header .subtitle {{ font-size: 15px; color: rgba(255,255,255,0.9); }}
.header .subtitle span {{ margin-right: 24px; }}
.tag {{
    display: inline-block; background: rgba(255,255,255,0.2); color: #ffffff;
    padding: 5px 14px; border-radius: 20px; font-size: 13px; margin-right: 10px;
}}
.section {{
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 32px; margin-bottom: 28px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}}
.section h2 {{
    font-size: 22px; font-weight: 700; color: #1f2937; margin-bottom: 20px;
    padding-bottom: 12px; border-bottom: 2px solid #3b82f6;
    display: inline-block;
}}
.section h3 {{ font-size: 17px; color: #374151; margin: 20px 0 12px; font-weight: 600; }}
.stat-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 8px;
}}
.stat-card {{
    background: #f9fafb; border-radius: 10px; padding: 18px 20px;
    border-top: 3px solid #3b82f6; transition: all 0.3s ease;
}}
.stat-card:hover {{
    transform: translateY(-4px); box-shadow: 0 8px 24px rgba(59,130,246,0.15);
    border-top-color: #1e40af;
}}
.stat-card .label {{ font-size: 13px; color: #6b7280; margin-bottom: 6px; }}
.stat-card .value {{ font-size: 24px; font-weight: 700; color: #1f2937; }}
.stat-card .unit {{ font-size: 13px; color: #6b7280; margin-left: 4px; }}
.stat-card.positive .value {{ color: #ef4444; }}
.stat-card.negative .value {{ color: #22c55e; }}
.chart-box {{ width: 100%; height: 480px; margin: 16px 0; border-radius: 8px; }}
.chart-box.small {{ height: 360px; }}
.interpretation {{
    background: #f0f9ff; border-left: 4px solid #3b82f6;
    padding: 16px 20px; border-radius: 0 8px 8px 0;
    margin: 12px 0 20px; font-size: 14.5px; line-height: 1.9; color: #374151;
}}
.interpretation strong {{ color: #1e40af; }}
table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
th {{ background: #f3f4f6; padding: 12px 14px; text-align: left; font-weight: 600; color: #374151; }}
td {{ padding: 10px 14px; border-bottom: 1px solid #e5e7eb; }}
tr:hover {{ background: #f9fafb; }}
.risk-box {{
    background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px;
    padding: 20px 24px; margin-top: 16px;
}}
.risk-box h4 {{ color: #dc2626; margin-bottom: 10px; font-size: 16px; }}
.risk-box ul {{ padding-left: 20px; color: #7f1d1d; }}
.risk-box li {{ margin-bottom: 8px; }}
.analysis-point {{
    display: inline-block; background: #dbeafe; color: #1e40af;
    padding: 4px 12px; border-radius: 4px; font-size: 13px; margin: 4px 6px 4px 0;
}}
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
@media (max-width: 900px) {{
    .stat-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .two-col {{ grid-template-columns: 1fr; }}
    .header {{ padding: 24px; }}
    .header h1 {{ font-size: 24px; }}
    .section {{ padding: 20px; }}
}}
</style>
</head>
<body>
<div class="container">

<div class="header">
    <h1>{stock_name}（{ts_code}）近一年交易数据分析报告</h1>
    <div class="subtitle">
        <span>📅 数据区间：{start_date_str} ~ {end_date_str}</span>
        <span>📊 前复权 · 日K线</span>
    </div>
    <div style="margin-top:14px;">
        <span class="tag">🗓️ {trading_days}个交易日</span>
        <span class="tag">⚡ 技术面分析</span>
        <span class="tag">📈 基本面分析</span>
        <span class="tag">💡 投资建议</span>
    </div>
</div>

<div class="section">
    <h2>一、数据概览</h2>
    <div class="stat-grid">
        <div class="stat-card {'positive' if change_pct > 0 else 'negative'}">
            <div class="label">区间涨跌幅</div>
            <div class="value">{'+' if change_pct > 0 else ''}{change_pct}%</div>
        </div>
        <div class="stat-card">
            <div class="label">区间最高价</div>
            <div class="value">{highest_price}<span class="unit">元</span></div>
        </div>
        <div class="stat-card">
            <div class="label">区间最低价</div>
            <div class="value">{lowest_price}<span class="unit">元</span></div>
        </div>
        <div class="stat-card">
            <div class="label">平均收盘价</div>
            <div class="value">{avg_price}<span class="unit">元</span></div>
        </div>
        <div class="stat-card">
            <div class="label">交易日数</div>
            <div class="value">{trading_days}<span class="unit">天</span></div>
        </div>
        <div class="stat-card">
            <div class="label">上涨/下跌/平盘</div>
            <div class="value" style="font-size:20px;">{up_days} / {down_days} / {flat_days}</div>
        </div>
        <div class="stat-card">
            <div class="label">日均成交额</div>
            <div class="value">{avg_amount_yi:.2f}<span class="unit">亿元</span></div>
        </div>
        <div class="stat-card">
            <div class="label">价格波动率</div>
            <div class="value">{volatility}<span class="unit">%</span></div>
        </div>
    </div>
    <div class="interpretation" style="margin-top:16px;">
        <strong>概览：</strong>{stock_name}在{start_date_str}至{end_date_str}期间，共计{trading_days}个交易日，区间涨跌幅为{'+' if change_pct > 0 else ''}{change_pct}%。最高价出现在{highest_date}（{highest_price}元），最低价出现在{lowest_date}（{lowest_price}元），振幅达{round((highest_price-lowest_price)/lowest_price*100,2)}%。上涨{up_days}天，下跌{down_days}天，上涨占比{up_ratio}%，日均成交额约{avg_amount_yi:.2f}亿元。
    </div>
</div>

<div class="section">
    <h2>二、年度表现汇总</h2>
    <table>
        <tr><th>年度</th><th>年初价</th><th>年末价</th><th>年度涨跌幅</th><th>最高价</th><th>最低价</th><th>交易日</th><th>涨/跌</th><th>上涨占比</th><th>日均成交量(手)</th></tr>
        {yearly_rows}
    </table>
</div>

<div class="section">
    <h2>三、日线K线走势图</h2>
    <h3>图1 {stock_name}（{ts_code}）近一年日线K线走势与均线系统</h3>
    <div id="kline-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图1解读】</strong>K线图反映了{stock_name}近一年的价格走势全貌，叠加MA5、MA10、MA20、MA60四条均线，用于判断短中长期趋势。<br><br>
        <strong>均线系统：</strong>短期均线（MA5/MA10）反映近期市场情绪，中长期均线（MA20/MA60）则代表趋势方向。当短期均线上穿中长期均线形成"金叉"时，通常是买入信号；反之，"死叉"则预示调整。<br><br>
        <strong>走势分析：</strong>整体来看，股价从{start_price}元起步，经历了冲高回落的过程。2025年7-8月股价快速拉升，创下{highest_price}元的阶段高点，随后进入长期下行通道。均线系统呈现空头排列（MA5 &lt; MA10 &lt; MA20 &lt; MA60），表明中长期趋势偏弱。当前股价位于各均线下方，短期反弹仍需放量突破均线压制。
    </div>

    <h3>图2 {stock_name}（{ts_code}）近一年日成交量分布（红柱涨/绿柱跌）</h3>
    <div id="volume-chart" class="chart-box small"></div>
    <div class="interpretation">
        <strong>【图2解读】</strong>成交量是市场资金活跃度的直接体现。红色柱体表示当日上涨放量，绿色柱体表示当日下跌放量。<br><br>
        <strong>量价关系：</strong>2025年7-8月股价上涨阶段，成交量显著放大，表明资金积极入场，推动股价上行。2025年8月中旬创阶段新高时，成交量达到峰值（单日最大{round(df['vol'].max()/10000,2)}万手），随后量能逐步萎缩。2025年四季度至2026年上半年，股价持续下跌过程中成交量整体萎缩，显示抛压减弱但买盘也不积极。缩量下跌通常意味着下跌动能在逐步消耗，但底部形成还需配合放量信号确认。
    </div>
</div>

<div class="section">
    <h2>四、日成交量走势图</h2>
    <div id="volume-chart2" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图2解读·补充】</strong>从全年成交量分布来看，可分为三个阶段：（1）2025年7-8月放量上涨期，日均成交超过百万手；（2）2025年9月-12月缩量震荡期，成交量逐步回落；（3）2026年以来极度缩量下跌期，日均成交量降至约30万手水平。<br><br>
        <strong>地量信号：</strong>当前成交量处于一年来的低位水平，地量往往是底部区域的重要特征之一，但地量之后还可能有地价，需结合后续是否出现放量长阳来确认底部反转。
    </div>
</div>

<div class="section">
    <h2>五、技术面分析</h2>

    <h3>5.1 均线系统分析</h3>
    <div class="interpretation">
        <strong>当前状态：</strong>MA5={ma5[latest_idx]:.2f}元，MA10={ma10[latest_idx]:.2f}元，MA20={ma20[latest_idx]:.2f}元，MA60={ma60[latest_idx]:.2f}元。<br><br>
        <strong>判断：</strong>股价位于所有均线下方，短期均线在中长期均线之下，呈典型的空头排列格局，表明当前市场处于弱势格局。MA60作为中长期趋势线，对股价构成较强压力。后续反弹若能放量站上MA20，则短期趋势有望转强；若继续承压于各均线下方，则弱势格局难改。<br><br>
        <strong>支撑与阻力：</strong>上方阻力位依次为MA10（{ma10[latest_idx]:.2f}元）、MA20（{ma20[latest_idx]:.2f}元）、MA60（{ma60[latest_idx]:.2f}元）。下方支撑位关注前期低点{lowest_price}元附近。
    </div>

    <h3>5.2 MACD指标分析</h3>
    <h3>图3 MACD（12,26,9）指标走势图</h3>
    <div id="macd-chart" class="chart-box small"></div>
    <div class="interpretation">
        <strong>【图3解读】</strong>MACD（指数平滑异同移动平均线）由DIF线（快线）、DEA线（慢线）和MACD柱（DIF-DEA）组成，用于判断趋势强弱和多空转换。本课MACD柱不乘2，直接等于DIF减DEA。<br><br>
        <strong>当前状态：</strong>DIF={latest_dif}，DEA={latest_dea}，MACD柱={latest_macd}。<br><br>
        <strong>零轴位置：</strong>DIF和DEA均运行在零轴下方，表明中期趋势处于空头主导。MACD柱若由绿转红并逐步放大，说明多头力量在增强，是反弹信号；若绿柱持续放大，则空头力量仍在增强。<br><br>
        <strong>金叉死叉：</strong>关注DIF与DEA的交叉情况。在零轴下方的金叉通常是反弹信号而非反转信号，需配合量能和均线突破来确认。零轴以上的金叉可靠性更高。
    </div>

    <h3>5.3 RSI相对强弱指标分析</h3>
    <h3>图4 RSI(14)相对强弱指标走势图</h3>
    <div id="rsi-chart" class="chart-box small"></div>
    <div class="interpretation">
        <strong>【图4解读】</strong>RSI（Relative Strength Index）衡量平均上涨幅度与平均下跌幅度的比值，把相对强弱压缩到0-100区间。本课采用14日Wilder平滑方法。70为超买观察线，30为超卖观察线。<br><br>
        <strong>当前状态：</strong>RSI(14) = {latest_rsi}。<br><br>
        <strong>走势分析：</strong>2025年7-8月上涨阶段，RSI快速攀升至80以上，进入超买区域，表明市场极度乐观，后续调整压力增大。随后RSI回落至30以下进入超卖区域。2026年以来股价持续下跌过程中，RSI多次跌入30以下的超卖区间，反映出卖方力量阶段性达到极致。<br><br>
        <strong>信号判断：</strong>RSI处于低位并不意味着马上会反弹，超卖后还可能继续超卖。有效信号是RSI从超卖区回升并突破50中轴线，才确认多方力量开始占优。当前RSI仍在中性偏低区域，需观察能否站稳50。
    </div>

    <h3>5.4 KDJ随机指标分析</h3>
    <h3>图5 KDJ随机指标走势图</h3>
    <div id="kdj-chart" class="chart-box small"></div>
    <div class="interpretation">
        <strong>【图5解读】</strong>KDJ随机指标通过计算价格在高低区间的相对位置来判断超买超卖。K线为快线，D线为慢线，J线为方向敏感线。通常80以上为超买区，20以下为超卖区。<br><br>
        <strong>当前状态：</strong>K={latest_k}，D={latest_d}，J={latest_j}。<br><br>
        <strong>信号判断：</strong>当K线从下向上突破D线形成金叉且位于低位时，是短期买入信号；当K线从上向下跌破D线形成死叉且位于高位时，是短期卖出信号。J值大于100或小于0时，预示短期可能出现反向修正。<br><br>
        <strong>适用性：</strong>KDJ在震荡市中信号较为灵敏和可靠，但在单边趋势行情中容易出现连续超买或连续超卖的钝化现象，需结合MACD、均线等趋势指标综合判断。
    </div>

    <h3>5.5 布林带指标分析</h3>
    <h3>图6 布林带（BOLL）指标走势图</h3>
    <div id="boll-chart" class="chart-box small"></div>
    <div class="interpretation">
        <strong>【图6解读】</strong>布林带由中轨（MA20）、上轨（中轨+2倍标准差）和下轨（中轨-2倍标准差）组成，反映价格的波动率和运行区间。<br><br>
        <strong>当前状态：</strong>上轨={latest_boll_upper}，中轨={latest_boll_mid}，下轨={latest_boll_lower}。<br><br>
        <strong>开口与收窄：</strong>布林带开口扩大表明波动率增加，通常伴随趋势的加速；布林带收窄表明波动率降低，通常是变盘的前兆。股价触及上轨时短期有回调压力，触及下轨时短期有反弹可能。<br><br>
        <strong>趋势判断：</strong>在上升趋势中，股价沿上轨运行；在下降趋势中，股价沿下轨运行。当前股价位于布林带中下轨区域，偏弱格局明显。若股价能从中下轨逐步上穿中轨并站稳，则短期趋势有望转强。
    </div>

    <h3>5.6 ATR平均真实波幅分析</h3>
    <h3>图7 ATR(14)平均真实波幅走势图</h3>
    <div id="atr-chart" class="chart-box small"></div>
    <div class="interpretation">
        <strong>【图7解读】</strong>ATR（Average True Range，平均真实波幅）衡量价格波动幅度，不判断方向。TR取三个值的最大值：当日高低差、高与昨收差的绝对值、低与昨收差的绝对值，比"最高-最低"更全面地反映了隔夜跳空带来的价格波动。本课采用14日Wilder平滑方法。<br><br>
        <strong>当前状态：</strong>ATR(14) = {latest_atr} 元，ATR% = {latest_atr_pct}%。<br><br>
        <strong>波动分析：</strong>ATR越大说明单日价格摆动通常越大，市场波动越剧烈；ATR越小说明波动越平静。2025年7-8月股价快速上涨阶段，ATR显著放大，反映市场情绪高涨、波动加剧。2025年9月以后随着股价回落和成交量萎缩，ATR逐步下行，表明市场波动在减小。2026年以来ATR处于相对低位，结合地量特征，说明市场交易清淡、多空双方都比较谨慎，波动收敛往往是变盘的前兆。<br><br>
        <strong>应用价值：</strong>ATR主要用于衡量波动性和设置止损，ATR本身不提供买卖方向信号，但结合价格位置和其他指标使用，可以更全面地评估市场状态。
    </div>
</div>

<div class="section">
    <h2>六、基本面分析</h2>

    <h3>6.1 公司简介</h3>
    <div class="interpretation">
        <strong>{stock_name}（{ts_code}）</strong>是内蒙古第一机械集团有限公司控股的上市公司，是我国唯一的主战坦克和履带式装甲车研制生产基地，属于国防军工行业核心标的。公司业务涵盖装甲车辆、铁路车辆、工程机械等领域，在陆军装备现代化建设中具有不可替代的战略地位。
    </div>

    <h3>6.2 股权结构与股东背景</h3>
    <div class="interpretation">
        公司实际控制人为中国兵器工业集团有限公司，第一大股东内蒙古第一机械集团持股约42.45%，中兵投资持股约12%，股权结构集中且稳定。兵器工业集团作为大股东，存在进一步资产整合的预期。
    </div>

    <h3>6.3 估值指标分析</h3>
    <table>
        <tr><th>指标</th><th>数值</th><th>说明</th></tr>
        <tr><td>最新收盘价</td><td>{end_price} 元</td><td>截至{end_date_str}</td></tr>
        <tr><td>总市值</td><td>{market_cap_now} 亿元</td><td>总股本 {total_shares_yi} 亿股</td></tr>
        <tr><td>日均换手率</td><td>{avg_turnover}%</td><td>过去一年平均</td></tr>
        <tr><td>区间最高市值</td><td>{round(highest_price*total_shares_yi,2)} 亿元</td><td>{highest_date}</td></tr>
        <tr><td>区间最低市值</td><td>{round(lowest_price*total_shares_yi,2)} 亿元</td><td>{lowest_date}</td></tr>
    </table>
    <div class="interpretation">
        公司当前总市值约{market_cap_now}亿元，作为军工装甲车辆龙头，估值水平需结合行业景气度和业绩增长综合评估。日均换手率{avg_turnover}%，成交活跃度处于中等偏低水平，反映市场关注度在股价回调后有所下降。
    </div>

    <h3>6.4 市值与换手率走势</h3>
    <h3>图8 市值与换手率走势图</h3>
    <div id="turnover-chart" class="chart-box small"></div>
    <div class="interpretation">
        <strong>【图8解读】</strong>左轴为总市值（亿元），右轴为日换手率（%）。市值走势与股价走势基本一致，从最高约{round(highest_price*total_shares_yi,0):.0f}亿元回落至当前{market_cap_now}亿元左右。换手率在2025年7-8月股价快速上涨期间显著放大，最高超过5%，反映资金博弈激烈。2026年以来换手率持续维持在1%左右的低位，交投清淡，筹码趋于稳定。
    </div>

    <h3>6.5 行业地位与竞争优势</h3>
    <div class="interpretation">
        <strong>行业地位：</strong>公司是国内陆军装甲装备的核心供应商，主战坦克和轮式装甲车领域技术领先，受益于国防现代化建设和装备更新换代需求。<br><br>
        <strong>竞争优势：</strong>（1）军品资质壁垒高，行业准入严格；（2）技术积累深厚，研发能力强；（3）大股东兵器工业集团资源支持，资产注入预期；（4）军民融合发展，民品业务提供业绩缓冲。
    </div>

    <h3>6.6 未来看点</h3>
    <div class="interpretation">
        <span class="analysis-point">国防预算稳步增长</span>
        <span class="analysis-point">装备升级换代加速</span>
        <span class="analysis-point">资产注入预期</span>
        <span class="analysis-point">无人化智能化转型</span>
        <span class="analysis-point">一带一路军贸出口</span>
        <span class="analysis-point">军民融合深度发展</span>
    </div>
</div>

<div class="section">
    <h2>七、投资建议</h2>
    <div class="interpretation">
        <strong>短期（1-3个月）：中性偏谨慎</strong><br>
        技术面上，股价仍处于下降趋势中，均线空头排列，成交量萎缩，MACD零轴下方运行，短期尚未出现明确的底部反转信号。建议观望为主，等待放量突破MA20或MACD金叉等积极信号出现后再考虑参与。<br><br>
        <strong>中期（3-6个月）：关注底部布局机会</strong><br>
        经过近一年的持续调整，股价跌幅已超过35%，估值风险得到一定程度释放。RSI等指标多次进入超卖区域，下跌动能在逐步消耗。中期可关注以下信号作为底部确认：（1）成交量持续放大并伴随股价上涨；（2）MACD在零轴下方形成金叉并逐步上移；（3）股价放量突破MA20和MA60压制。若上述信号出现，可考虑逐步布局。<br><br>
        <strong>长期（6个月以上）：看好行业景气度</strong><br>
        从基本面看，国防军工行业长期景气度确定，装备现代化建设是长期趋势。{stock_name}作为装甲装备龙头，将持续受益于国防预算增长和装备更新换代。同时，大股东资产整合预期、无人化智能化转型等也为公司提供长期成长空间。长期投资者可逢低分批布局，重点关注军工行业政策面、订单情况和公司业绩兑现。
    </div>
</div>

<div class="section">
    <h2>八、风险提示</h2>
    <div class="risk-box">
        <h4>⚠️ 投资风险</h4>
        <ul>
            <li><strong>业绩波动风险：</strong>军工企业订单确认具有季节性和不确定性，可能导致业绩季度间波动较大。</li>
            <li><strong>估值回调风险：</strong>前期估值涨幅较大，若业绩增速不及预期，可能面临估值回调压力。</li>
            <li><strong>资产注入不及预期风险：</strong>大股东资产整合存在时间和规模上的不确定性。</li>
            <li><strong>行业政策变化风险：</strong>国防预算增速、军品定价机制等政策变化可能影响公司盈利水平。</li>
            <li><strong>技术迭代风险：</strong>无人化、智能化装备发展迅速，若公司技术跟进不及时可能面临竞争压力。</li>
            <li><strong>市场系统性风险：</strong>大盘整体下跌、地缘政治冲突升级等系统性因素可能导致股价进一步下行。</li>
        </ul>
    </div>
    <div class="interpretation" style="margin-top:16px;">
        <strong>免责声明：</strong>本报告基于公开数据和技术分析方法生成，仅供学习和研究参考，不构成任何投资建议。股市有风险，投资需谨慎。
    </div>
</div>

</div>

<script>
var dates = {dates_json};
var klineData = {kline_json};
var volumeData = {volumes_json};
var ma5Data = {ma5_json};
var ma10Data = {ma10_json};
var ma20Data = {ma20_json};
var ma60Data = {ma60_json};
var difData = {dif_json};
var deaData = {dea_json};
var macdData = {macd_json};
var rsiData = {rsi_json};
var kData = {k_json};
var dData = {d_json};
var jData = {j_json};
var bollMidData = {boll_mid_json};
var bollUpperData = {boll_upper_json};
var bollLowerData = {boll_lower_json};
var trData = {tr_json};
var atrData = {atr_json};
var closeData = {close_json};

var tooltipStyle = {{
    backgroundColor: 'rgba(255,255,255,0.98)',
    borderColor: '#e5e7eb',
    borderWidth: 1,
    textStyle: {{ color: '#374151', fontSize: 13 }},
    extraCssText: 'box-shadow: 0 4px 20px rgba(0,0,0,0.1); border-radius: 8px;'
}};

var commonXAxis = {{
    type: 'category',
    data: dates,
    axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }},
    axisLabel: {{ show: false }},
    splitLine: {{ show: false }},
    boundaryGap: true,
    min: 'dataMin', max: 'dataMax'
}};

var commonDataZoom = [
    {{ type: 'inside', xAxisIndex: [0], start: 0, end: 100 }},
    {{ type: 'slider', xAxisIndex: [0], start: 0, end: 100, height: 20, bottom: 5,
       borderColor: '#e5e7eb', fillerColor: 'rgba(59,130,246,0.2)', handleStyle: {{ color: '#3b82f6' }} }}
];

var klineChart = echarts.init(document.getElementById('kline-chart'));
klineChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{
        trigger: 'axis', axisPointer: {{ type: 'cross' }},
        ...tooltipStyle,
        formatter: function(params) {{
            var idx = params[0].dataIndex;
            var d = klineData[idx];
            var pctChg = idx > 0 ? ((d[1] - klineData[idx-1][1]) / klineData[idx-1][1] * 100).toFixed(2) : '-';
            var color = d[1] >= d[0] ? '#ef4444' : '#22c55e';
            var sign = d[1] >= d[0] ? '+' : '';
            return '<div style="font-weight:700;color:#1f2937;border-bottom:1px solid #e5e7eb;padding-bottom:6px;margin-bottom:6px;">' + dates[idx] + '</div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">开盘</span><span style="font-weight:600;">' + d[0] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">收盘</span><span style="font-weight:600;color:' + color + '">' + d[1] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">最高</span><span style="font-weight:600;">' + d[3] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">最低</span><span style="font-weight:600;">' + d[2] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">涨跌幅</span><span style="font-weight:600;color:' + color + '">' + sign + pctChg + '%</span></div>';
        }}
    }},
    legend: {{
        data: ['MA5', 'MA10', 'MA20', 'MA60'],
        textStyle: {{ color: '#6b7280', fontSize: 12 }},
        top: 5, itemWidth: 20, itemHeight: 10, icon: 'roundRect'
    }},
    grid: {{ left: '6%', right: '3%', top: '12%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'K线', type: 'candlestick', data: klineData, itemStyle: {{ color: '#ef4444', color0: '#22c55e', borderColor: '#ef4444', borderColor0: '#22c55e' }} }},
        {{ name: 'MA5', type: 'line', data: ma5Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#eab308' }}, itemStyle: {{ color: '#eab308' }} }},
        {{ name: 'MA10', type: 'line', data: ma10Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#f97316' }}, itemStyle: {{ color: '#f97316' }} }},
        {{ name: 'MA20', type: 'line', data: ma20Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#22c55e' }}, itemStyle: {{ color: '#22c55e' }} }},
        {{ name: 'MA60', type: 'line', data: ma60Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }} }}
    ]
}});

var volumeChart = echarts.init(document.getElementById('volume-chart'));
volumeChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle,
        formatter: function(params) {{
            var v = params[0];
            return dates[v.dataIndex] + '<br/>成交量: ' + v.data.value.toLocaleString() + ' 手';
        }}
    }},
    grid: {{ left: '6%', right: '3%', top: '8%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [{{ name: '成交量', type: 'bar', data: volumeData }}]
}});

var volumeChart2 = echarts.init(document.getElementById('volume-chart2'));
volumeChart2.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle,
        formatter: function(params) {{
            var v = params[0];
            return dates[v.dataIndex] + '<br/>成交量: ' + v.data.value.toLocaleString() + ' 手';
        }}
    }},
    grid: {{ left: '6%', right: '3%', top: '5%', bottom: '15%' }},
    xAxis: {{ ...commonXAxis, axisLabel: {{ show: true, color: '#6b7280', fontSize: 11, rotate: 30 }} }},
    yAxis: {{ type: 'value', axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [{{ name: '成交量', type: 'bar', data: volumeData }}]
}});

var macdChart = echarts.init(document.getElementById('macd-chart'));
macdChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['DIF', 'DEA', 'MACD柱'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '15%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'DIF', type: 'line', data: difData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#eab308' }}, itemStyle: {{ color: '#eab308' }} }},
        {{ name: 'DEA', type: 'line', data: deaData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#3b82f6' }}, itemStyle: {{ color: '#3b82f6' }} }},
        {{ name: 'MACD柱', type: 'bar', data: macdData,
            itemStyle: {{ color: function(params) {{ return params.value >= 0 ? '#ef4444' : '#22c55e'; }} }}
        }}
    ]
}});

var rsiChart = echarts.init(document.getElementById('rsi-chart'));
rsiChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['RSI(14)'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '15%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', min: 0, max: 100, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'RSI(14)', type: 'line', data: rsiData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#3b82f6' }}, itemStyle: {{ color: '#3b82f6' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(59,130,246,0.15)' }}, {{ offset: 1, color: 'rgba(59,130,246,0.02)' }}] }} }} }},
        {{ name: '超买线', type: 'line', data: dates.map(() => 70), symbol: 'none', lineStyle: {{ width: 1, color: '#ef4444', type: 'dashed' }}, silent: true }},
        {{ name: '超卖线', type: 'line', data: dates.map(() => 30), symbol: 'none', lineStyle: {{ width: 1, color: '#22c55e', type: 'dashed' }}, silent: true }},
        {{ name: '中轴线', type: 'line', data: dates.map(() => 50), symbol: 'none', lineStyle: {{ width: 1, color: '#9ca3af', type: 'dashed' }}, silent: true }}
    ]
}});

var kdjChart = echarts.init(document.getElementById('kdj-chart'));
kdjChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['K', 'D', 'J'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '15%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'K', type: 'line', data: kData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#eab308' }}, itemStyle: {{ color: '#eab308' }} }},
        {{ name: 'D', type: 'line', data: dData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#3b82f6' }}, itemStyle: {{ color: '#3b82f6' }} }},
        {{ name: 'J', type: 'line', data: jData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#ec4899' }}, itemStyle: {{ color: '#ec4899' }} }},
        {{ name: '超买线', type: 'line', data: dates.map(() => 80), symbol: 'none', lineStyle: {{ width: 1, color: '#ef4444', type: 'dashed' }}, silent: true }},
        {{ name: '超卖线', type: 'line', data: dates.map(() => 20), symbol: 'none', lineStyle: {{ width: 1, color: '#22c55e', type: 'dashed' }}, silent: true }}
    ]
}});

var bollChart = echarts.init(document.getElementById('boll-chart'));
bollChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['收盘价', '中轨(MA20)', '上轨', '下轨'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '15%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: '收盘价', type: 'line', data: closeData, smooth: false, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#3b82f6' }}, itemStyle: {{ color: '#3b82f6' }} }},
        {{ name: '中轨(MA20)', type: 'line', data: bollMidData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#f97316' }}, itemStyle: {{ color: '#f97316' }} }},
        {{ name: '上轨', type: 'line', data: bollUpperData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#ef4444', type: 'dashed' }}, itemStyle: {{ color: '#ef4444' }} }},
        {{ name: '下轨', type: 'line', data: bollLowerData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#22c55e', type: 'dashed' }}, itemStyle: {{ color: '#22c55e' }} }}
    ]
}});

var atrChart = echarts.init(document.getElementById('atr-chart'));
atrChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['TR(真实波幅)', 'ATR(14)'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '15%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'TR(真实波幅)', type: 'bar', data: trData, itemStyle: {{ color: 'rgba(156,163,175,0.5)' }}, barWidth: '60%' }},
        {{ name: 'ATR(14)', type: 'line', data: atrData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }} }}
    ]
}});

var turnoverChart = echarts.init(document.getElementById('turnover-chart'));
var totalShares = {total_shares_yi};
var marketCap = closeData.map(p => Math.round(p * totalShares * 100) / 100);
var turnoverRate = volumeData.map(v => Math.round(v.value / (totalShares * 10000) * 10000) / 100);

turnoverChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['市值(亿元)', '换手率(%)'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '6%', top: '15%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: [
        {{ type: 'value', name: '市值(亿元)', axisLine: {{ lineStyle: {{ color: '#3b82f6' }} }}, axisLabel: {{ color: '#3b82f6', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
        {{ type: 'value', name: '换手率(%)', axisLine: {{ lineStyle: {{ color: '#f97316' }} }}, axisLabel: {{ color: '#f97316', fontSize: 11 }}, splitLine: {{ show: false }} }}
    ],
    dataZoom: commonDataZoom,
    series: [
        {{ name: '市值(亿元)', type: 'line', data: marketCap, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#3b82f6' }}, itemStyle: {{ color: '#3b82f6' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(59,130,246,0.15)' }}, {{ offset: 1, color: 'rgba(59,130,246,0.02)' }}] }} }} }},
        {{ name: '换手率(%)', type: 'line', data: turnoverRate, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#f97316' }}, itemStyle: {{ color: '#f97316' }}, yAxisIndex: 1 }}
    ]
}});

echarts.connect([klineChart, volumeChart, volumeChart2, macdChart, rsiChart, kdjChart, bollChart, atrChart, turnoverChart]);
window.addEventListener('resize', function() {{
    klineChart.resize(); volumeChart.resize(); volumeChart2.resize(); macdChart.resize();
    rsiChart.resize(); kdjChart.resize(); bollChart.resize(); atrChart.resize(); turnoverChart.resize();
}});
</script>
</body>
</html>'''

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{ts_code}_analysis.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    index_path = 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f'HTML报告已生成: {output_path}')
    print(f'首页已生成: {index_path}')
    return output_path


STOCK_INFO = {
    '600967.SH': ('内蒙一机', 17.02),
}


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        ts_code = sys.argv[1]
    else:
        ts_code = '600967.SH'

    if ts_code in STOCK_INFO:
        stock_name, total_shares_yi = STOCK_INFO[ts_code]
    else:
        stock_name = ts_code
        total_shares_yi = 10.0
        print(f'提示：{ts_code} 未在股票信息表中，使用默认名称和总股本。请手动添加。')

    csv_path = os.path.join('output', f'{ts_code}_daily_data.csv')
    if not os.path.exists(csv_path):
        print(f'未找到 {csv_path}，尝试从Tushare获取...')

    generate_html_report(ts_code, stock_name, total_shares_yi, output_dir='output')
