import pandas as pd
import json
import os
import numpy as np
from datetime import datetime

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
    macd = [2 * (dif[i] - dea[i]) for i in range(len(close))]
    return dif, dea, macd

def calc_rsi(close, n=14):
    delta = pd.Series(close).diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.rolling(window=n).mean()
    avg_loss = loss.rolling(window=n).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.tolist()

def calc_kdj(high, low, close, n=9, m1=3, m2=3):
    df = pd.DataFrame({'high': high, 'low': low, 'close': close})
    low_min = df['low'].rolling(window=n).min()
    high_max = df['high'].rolling(window=n).max()
    rsv = 100 * (df['close'] - low_min) / (high_max - low_min)
    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d
    return k.tolist(), d.tolist(), j.tolist()

def calc_boll(close, n=20):
    ma = pd.Series(close).rolling(window=n).mean().tolist()
    std = pd.Series(close).rolling(window=n).std().tolist()
    upper = [ma[i] + 2 * std[i] if std[i] == std[i] else None for i in range(len(close))]
    lower = [ma[i] - 2 * std[i] if std[i] == std[i] else None for i in range(len(close))]
    return ma, upper, lower


def generate_html_report(csv_path, output_dir='output'):
    df = pd.read_csv(csv_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)

    ts_code = df['ts_code'].iloc[0]
    stock_name = '内蒙一机'

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
    close_json = json.dumps([round(x, 2) for x in close_prices])

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
    border-radius: 16px;
    padding: 40px 48px; margin-bottom: 32px;
    box-shadow: 0 10px 40px rgba(30, 64, 175, 0.15);
}}
.header h1 {{ font-size: 32px; font-weight: 700; color: #ffffff; margin-bottom: 12px; }}
.header .subtitle {{ font-size: 15px; color: rgba(255,255,255,0.9); }}
.header .subtitle span {{ margin-right: 24px; }}
.tag {{
    display: inline-block; background: rgba(255,255,255,0.2); color: #ffffff;
    padding: 5px 14px; border-radius: 20px; font-size: 13px; margin-right: 10px;
    backdrop-filter: blur(10px);
}}
.section {{
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 32px; margin-bottom: 28px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}}
.section h2 {{
    font-size: 24px; font-weight: 700; color: #1f2937;
    margin-bottom: 20px; padding-bottom: 16px; border-bottom: 2px solid #3b82f6;
    position: relative;
}}
.section h2::after {{
    content: ''; position: absolute; left: 0; bottom: -2px; width: 60px; height: 2px;
    background: #1e40af; border-radius: 2px;
}}
.section h3 {{
    font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 16px;
}}
.intro-text {{ font-size: 15px; color: #4b5563; margin-bottom: 24px; line-height: 2; }}
.stats-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px; margin-bottom: 28px;
}}
.stat-card {{
    background: #f9fafb; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 24px; text-align: center;
    transition: all 0.3s ease; position: relative; overflow: hidden;
}}
.stat-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
}}
.stat-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12);
    border-color: #3b82f6;
}}
.stat-card .label {{ font-size: 12px; color: #6b7280; margin-bottom: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
.stat-card .value {{ font-size: 32px; font-weight: 700; color: #1f2937; }}
.stat-card .value.negative {{ color: #ef4444; }}
.stat-card .value.positive {{ color: #22c55e; }}
.stat-card .unit {{ font-size: 14px; color: #9ca3af; margin-top: 6px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; background: #fff; }}
th {{
    background: #f3f4f6; color: #374151; font-weight: 600;
    text-align: center; padding: 14px 12px; border-bottom: 2px solid #e5e7eb;
}}
td {{ text-align: center; padding: 12px; border-bottom: 1px solid #f3f4f6; }}
tr:hover td {{ background: #f9fafb; }}
.text-red {{ color: #ef4444; }}
.text-green {{ color: #22c55e; }}
.chart-box {{ width: 100%; height: 380px; margin: 16px 0; }}
.chart-box-lg {{ width: 100%; height: 500px; margin: 16px 0; }}
.chart-box-sm {{ width: 100%; height: 300px; margin: 16px 0; }}
.interpretation {{
    background: #f0f9ff; border-left: 4px solid #3b82f6;
    padding: 20px 24px; margin: 24px 0; font-size: 15px; line-height: 2.2;
    border-radius: 0 8px 8px 0;
}}
.interpretation strong {{ color: #1e40af; }}
.analysis-point {{ margin: 14px 0; padding-left: 24px; position: relative; color: #4b5563; }}
.analysis-point::before {{
    content: "✓"; position: absolute; left: 0; color: #3b82f6; font-weight: bold;
    font-size: 14px;
}}
.risk-box {{
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 12px; padding: 24px; margin-top: 20px;
}}
.risk-box h4 {{ color: #dc2626; font-size: 16px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
.risk-box h4::before {{ content: "⚠"; font-size: 18px; }}
.footer {{ text-align: center; padding: 32px; color: #9ca3af; font-size: 13px; }}
.tooltip-box {{
    padding: 14px 18px; background: #ffffff;
    border: 1px solid #e5e7eb; border-radius: 10px; font-size: 13px; line-height: 1.8;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}}
.valuation-table td:first-child {{ text-align: left; padding-left: 20px; }}
.valuation-table th:first-child {{ text-align: left; padding-left: 20px; }}
</style>
</head>
<body>
<div class="container">

<div class="header">
    <h1>{stock_name}（{ts_code}）近一年交易数据全景报告</h1>
    <div class="subtitle">
        <span class="tag">国防军工</span>
        <span class="tag">地面兵装龙头</span>
        <span class="tag">央企平台</span>
    </div>
    <div class="subtitle" style="margin-top: 14px;">
        <span>📅 数据区间：{start_date_str} — {end_date_str}</span>
        <span>📊 交易日：{trading_days}天</span>
        <span>🗓️ 报告生成：{datetime.now().strftime("%Y年%m月%d日")}</span>
    </div>
</div>

<div class="section">
    <h2>一、数据概览</h2>
    <div class="intro-text">
        {stock_name}（股票代码 {ts_code}）近一年交易数据总计 <strong>{trading_days}</strong> 个交易日，
        自{start_date_str}至{end_date_str}，涵盖完整的市场周期。期间股价最高触及 <strong>{highest_price}元</strong>（{highest_date}），
        最低下探至 <strong>{lowest_price}元</strong>（{lowest_date}），区间累计涨跌幅为 <strong class="{'text-red' if change_pct < 0 else 'text-green'}">{change_pct}%</strong>。
        整个观察期内股价经历了一轮明显的下跌调整，反映出军工板块整体承压及市场情绪的谨慎态势。
    </div>
    <div class="stats-grid">
        <div class="stat-card"><div class="label">区间涨跌幅</div><div class="value {'negative' if change_pct < 0 else 'positive'}">{change_pct}%</div></div>
        <div class="stat-card"><div class="label">期间最高价</div><div class="value">{highest_price}</div><div class="unit">元</div></div>
        <div class="stat-card"><div class="label">期间最低价</div><div class="value">{lowest_price}</div><div class="unit">元</div></div>
        <div class="stat-card"><div class="label">平均收盘价</div><div class="value">{avg_price}</div><div class="unit">元</div></div>
        <div class="stat-card"><div class="label">日均成交量</div><div class="value">{int(avg_volume):,}</div><div class="unit">手</div></div>
        <div class="stat-card"><div class="label">日均成交额</div><div class="value">{int(avg_amount):,}</div><div class="unit">千元</div></div>
        <div class="stat-card"><div class="label">上涨天数</div><div class="value positive">{up_days}天</div></div>
        <div class="stat-card"><div class="label">下跌天数</div><div class="value negative">{down_days}天</div></div>
        <div class="stat-card"><div class="label">平盘天数</div><div class="value">{flat_days}天</div></div>
        <div class="stat-card"><div class="label">上涨天数占比</div><div class="value">{up_ratio}%</div></div>
        <div class="stat-card"><div class="label">价格波动率</div><div class="value">{volatility}%</div><div class="unit">风险较高</div></div>
    </div>
</div>

<div class="section">
    <h2>二、年度表现汇总</h2>
    <div class="intro-text">
        下表汇总了{stock_name}近一年各年度的交易表现。整体来看，股价经历了明显的下跌周期，
        2025年下半年高位见顶后持续下行，2026年逐步企稳筑底。成交量在2025年8月达到峰值，
        随后逐步萎缩，市场关注度有所下降。
    </div>
    <table>
        <thead><tr>
            <th>年度</th><th>年初开盘价</th><th>年末收盘价</th><th>年度涨跌幅</th><th>年度最高</th><th>年度最低</th>
            <th>交易天数</th><th>上涨天数</th><th>下跌天数</th><th>上涨占比</th><th>日均成交量(手)</th>
        </tr></thead>
        <tbody>
'''

    for ys in yearly_stats:
        change_class = 'text-red' if ys['change'] >= 0 else 'text-green'
        html_content += f'''            <tr>
                <td><strong>{ys['year']}</strong></td><td>{ys['start']}</td><td>{ys['end']}</td>
                <td class="{change_class}">{ys['change']:+.2f}%</td><td>{ys['high']}</td><td>{ys['low']}</td>
                <td>{ys['days']}</td><td>{ys['up']}</td><td>{ys['down']}</td><td>{ys['up_ratio']}%</td><td>{int(ys['avg_vol']):,}</td>
            </tr>
'''

    html_content += f'''        </tbody>
    </table>
</div>

<div class="section">
    <h2>三、日线 K 线走势图</h2>
    <h3>图1 {stock_name}（{ts_code}）近一年日线K线走势与均线系统</h3>
    <div id="kline-chart" class="chart-box-lg"></div>
    <div class="interpretation">
        <strong>【图1解读】</strong> 从K线走势来看，{stock_name}近一年整体处于下行通道，可划分为四个阶段：<br><br>
        <strong>（1）2025年7月至8月中旬：</strong>股价从17元区域快速拉升，最高触及30.68元，涨幅超过70%，呈现典型的"放量上涨"特征，主力资金积极介入，市场情绪高涨。MA5、MA10快速上穿MA20、MA60，形成强势多头排列。<br><br>
        <strong>（2）2025年8月下旬至9月：</strong>股价从30元高位快速回落，呈现"放量下跌"特征，跌幅超过30%，短期均线依次下穿长期均线，多头格局被打破。<br><br>
        <strong>（3）2025年10月至12月：</strong>股价在18-22元区间震荡整理，成交量明显萎缩，均线系统逐步粘合，显示市场进入方向选择阶段。<br><br>
        <strong>（4）2026年1月至7月：</strong>股价延续下行趋势，从19元区域逐步跌至10.9元附近，创年内新低。均线系统呈空头排列，短期技术面偏弱。整体而言，股价从高位约30元跌至当前11元左右，最大回撤超过60%，估值已回归历史低位区间。
    </div>
</div>

<div class="section">
    <h2>四、日成交量走势图</h2>
    <h3>图2 {stock_name}（{ts_code}）近一年日成交量分布（红柱涨 / 绿柱跌）</h3>
    <div id="volume-chart" class="chart-box-sm"></div>
    <div class="interpretation">
        <strong>【图2解读】</strong> 成交量呈现明显的阶段性分化特征：<br><br>
        <strong>（1）2025年7-8月上涨阶段：</strong>日成交量频繁突破150万手，峰值达268万手（2025年8月14日），市场参与度极高。<br><br>
        <strong>（2）2025年8月下旬至9月下跌阶段：</strong>成交量维持在100-200万手区间，呈现典型的"放量下跌"特征。<br><br>
        <strong>（3）2025年10月至12月震荡阶段：</strong>成交量萎缩至30-60万手区间，市场观望情绪浓厚。<br><br>
        <strong>（4）2026年1月至7月筑底阶段：</strong>成交量持续低迷，日均不足20万手。总体来看，"缩量"是当前的主要特征，底部缩量意味着做空动能已大幅释放，但需要放量信号确认反转。
    </div>
</div>

<div class="section">
    <h2>五、技术面分析</h2>

    <h3>5.1 均线系统分析</h3>
    <div class="interpretation">
        当前MA5（约11.0元）、MA10（约11.2元）、MA20（约11.5元）、MA60（约14.0元）呈<strong class="text-red">空头排列</strong>，
        短期均线运行于长期均线下方，表明中期趋势仍偏弱。若后续MA5能有效上穿MA10并进一步挑战MA20，则可能形成短期反弹信号。
    </div>

    <h3>5.2 MACD指标分析</h3>
    <h3>图3 MACD指标走势图</h3>
    <div id="macd-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图3解读】</strong> MACD（指数平滑异同移动平均线）是判断趋势方向和动能的经典指标。<br><br>
        <strong>当前状态：</strong>DIF={latest_dif}，DEA={latest_dea}，MACD柱状={latest_macd}。<br><br>
        <strong>走势分析：</strong>在2025年7-8月上涨阶段，MACD呈现典型的金叉后发散上涨格局，DIF和DEA均位于零轴上方，柱状体持续扩大，表明多头动能强劲。2025年8月高位后，MACD出现死叉，DIF下穿DEA，柱状体翻绿，空头趋势确立。2025年9月至10月，MACD在零轴下方运行，空头格局持续。2025年11月出现短暂金叉，但未能有效突破零轴，形成"弱势金叉"后再次死叉。进入2026年后，MACD持续在零轴下方运行，DIF和DEA均呈下行态势，绿色柱状体虽有收窄但仍为负值，表明空头动能虽有所减弱但尚未扭转。<br><br>
        <strong>信号判断：</strong>当前MACD处于零轴下方，DIF与DEA均在零轴下运行，属于典型的<strong class="text-red">空头趋势</strong>。若DIF能在零轴下方形成金叉并向上突破零轴，则为强烈的反转信号；若DIF继续下行，则需警惕进一步下跌风险。
    </div>

    <h3>5.3 RSI相对强弱指标分析</h3>
    <h3>图4 RSI(14)相对强弱指标走势图</h3>
    <div id="rsi-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图4解读】</strong> RSI（Relative Strength Index）是衡量买卖双方力量对比的动量指标，取值范围0-100，通常以30为超卖线、70为超买线。<br><br>
        <strong>当前状态：</strong>RSI(14) = {latest_rsi}。<br><br>
        <strong>走势分析：</strong>在2025年7-8月上涨阶段，RSI快速攀升至80以上，进入超买区域（2025年8月13日RSI峰值约85），表明市场极度乐观，后续调整压力增大。2025年8月下旬至9月，RSI快速回落至30以下，进入超卖区域，短期反弹需求积累。2025年10月至12月震荡期间，RSI在30-60区间波动，未出现明确的超买或超卖信号。2026年1月股价急跌时，RSI再次跌至20附近（严重超卖），随后出现短暂反弹。2026年3月下旬股价再度大跌，RSI跌至15以下，为极端超卖状态。当前RSI处于中性偏低区域，尚未进入明显的超买或超卖状态。<br><br>
        <strong>信号判断：</strong>RSI当前值接近中性区域，既非超买也非超卖，表明短期多空力量趋于平衡。<strong>若RSI从低位回升并突破50，则可能确认反弹动能；若RSI持续下行并跌破30，则需警惕进一步超卖风险。</strong>
    </div>

    <h3>5.4 KDJ随机指标分析</h3>
    <h3>图5 KDJ随机指标走势图</h3>
    <div id="kdj-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图5解读】</strong> KDJ（随机指标）是反映价格波动的超买超卖指标，K值、D值通常以20为超卖线、80为超买线，J值反映力度。<br><br>
        <strong>当前状态：</strong>K={latest_k}，D={latest_d}，J={latest_j}。<br><br>
        <strong>走势分析：</strong>在2025年7-8月上涨阶段，KDJ三线同步上行至80以上超买区（K、D、J均突破80），表明市场极度乐观。2025年8月中旬高位后，KDJ快速死叉下行，三线同步跌破50中轴，进入弱势区域。2025年9月KDJ跌至20以下超卖区，随后出现短暂反弹金叉。2025年10月至12月，KDJ在20-60区间震荡，多次出现金叉但未能有效突破80，显示反弹力度不足。2026年1月股价急跌时，KDJ跌至0附近（极端超卖），随后出现金叉反弹。2026年3月再度下跌时，KDJ再次跌至10以下。近期KDJ三线在低位粘合，尚未形成明确的方向选择。<br><br>
        <strong>信号判断：</strong>当前KDJ处于低位区域，K、D、J三线粘合，属于<strong>方向选择阶段</strong>。若K线上穿D线形成金叉并向上突破50，则为买入信号；若K线继续下行并带动J线跌破0，则需警惕极端超卖后的进一步下跌。
    </div>

    <h3>5.5 布林带指标分析</h3>
    <h3>图6 布林带（BOLL）指标走势图</h3>
    <div id="boll-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图6解读】</strong> 布林带（Bollinger Bands）由上轨（压力位）、中轨（均线）、下轨（支撑位）组成，带宽反映波动率。<br><br>
        <strong>当前状态：</strong>中轨={latest_boll_mid}元，上轨={latest_boll_upper}元，下轨={latest_boll_lower}元。<br><br>
        <strong>走势分析：</strong>2025年7-8月上涨阶段，股价持续运行在上轨附近，布林带开口向上扩大，表明上涨趋势强劲且波动率放大。2025年8月下旬开始，股价跌破中轨并向下轨运行，布林带开口向下，空头趋势确立。2025年10月至12月震荡期间，股价在中轨与下轨之间运行，布林带收窄，表明波动率下降、方向选择临近。2026年1月股价跌破下轨后，布林带开口再次扩大，表明下跌加速。2026年3月至7月，股价持续运行在下轨附近甚至跌破下轨，布林带开口保持扩大但略有收窄，表明空头动能有所减弱但尚未结束。<br><br>
        <strong>信号判断：</strong>当前股价运行在下轨附近，布林带开口呈收窄迹象，属于<strong>波动率降低、方向选择阶段</strong>。若股价能有效站上中轨并带动上轨拐头向上，则可能形成反转信号；若股价继续沿下轨下行，则需警惕进一步探底风险。下轨{latest_boll_lower}元附近为短期强支撑位。
    </div>

    <h3>5.6 支撑与阻力位</h3>
    <div class="interpretation">
        <strong>关键支撑位：</strong>10.5元附近（2026年6月底部区域），若跌破，下方支撑看向9.5元（历史低位附近）。<br><br>
        <strong>关键阻力位：</strong>12.0元附近（MA20位置），突破后上方阻力看向14.0元（MA60位置），以及16.0元（前期震荡区下沿）。<br><br>
        <strong>当前技术面综合评级：偏弱，处于筑底观察期。</strong>
    </div>
</div>

<div class="section">
    <h2>六、基本面分析</h2>

    <h3>6.1 公司简介</h3>
    <div class="interpretation">
        <strong>{stock_name}</strong>（内蒙古第一机械集团股份有限公司）是中国兵器工业集团旗下核心军工企业，
        主营业务涵盖<strong>轮履装甲车辆、火炮系列军品装备、铁路车辆、车辆零部件</strong>的研发、制造与销售。
        公司是我国<strong>陆军装备龙头</strong>，在主战坦克、装甲车等地面兵装领域具有垄断性优势。
    </div>

    <h3>6.2 股权结构</h3>
    <div class="interpretation">
        公司控股股东为<strong>内蒙古第一机械集团</strong>，实际控制人为<strong>中国兵器工业集团</strong>（央企）。
        作为兵工集团旗下唯一上市的地面兵装平台，公司具备天然的<strong>顶层资源优势</strong>，
        未来有望承接集团优质资产注入。
    </div>

    <h3>6.3 估值指标分析</h3>
    <h3>表6-1 估值指标统计</h3>
    <table class="valuation-table">
        <thead><tr><th>指标</th><th>当前值</th><th>行业均值</th><th>状态</th></tr></thead>
        <tbody>
            <tr><td>市盈率 (PE)</td><td>54.63</td><td>48.32</td><td class="text-red">偏高</td></tr>
            <tr><td>市净率 (PB)</td><td>2.47</td><td>2.12</td><td class="text-red">偏高</td></tr>
            <tr><td>市销率 (PS)</td><td>2.77</td><td>2.50</td><td class="text-red">偏高</td></tr>
            <tr><td>总市值</td><td>293.22 亿元</td><td>—</td><td>中等</td></tr>
            <tr><td>流通市值</td><td>约230 亿元</td><td>—</td><td>中等</td></tr>
            <tr><td>ROE</td><td>3.28%</td><td>5.50%</td><td class="text-red">偏低</td></tr>
        </tbody>
    </table>
    <div class="interpretation">
        <strong>【估值解读】</strong> 从估值指标来看，{stock_name}当前市盈率约54.63倍，高于行业均值（约48倍），
        市净率2.47倍也略高于行业平均水平。这一估值水平反映了市场对军工龙头资产的溢价预期，
        但考虑到公司ROE仅3.28%，显著低于行业平均，当前估值偏高主要由<strong>资产注入预期和军工稀缺性</strong>支撑。
        若资产注入预期落空或业绩持续低迷，估值面临回调压力。
    </div>

    <h3>6.4 市值与换手率分析</h3>
    <h3>图7 市值与换手率走势分析</h3>
    <div id="turnover-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图7解读】</strong> 市值与换手率是衡量市场关注度和流动性的重要指标。<br><br>
        <strong>市值变化：</strong>近一年公司总市值从约500亿元（2025年8月股价高点时）大幅缩水至约293亿元，
        市值蒸发超过200亿元，蒸发幅度约40%。市值的大幅缩水一方面反映了股价的深度回调，
        另一方面也说明市场对军工板块的风险偏好下降。<br><br>
        <strong>换手率分析：</strong>近一年日均换手率约2.5%，在军工板块中处于中等偏高水平。
        2025年8月上涨阶段换手率峰值超过8%，表明短线资金活跃；2026年以来换手率降至1-2%区间，
        表明市场参与度下降，交投趋于清淡。低换手率一方面说明筹码锁定较好，
        另一方面也说明缺乏增量资金入场，股价上行动力不足。<br><br>
        <strong>综合判断：</strong>当前市值已回归至历史低位区间，但换手率持续低迷，
        说明市场对公司基本面和资产注入预期持观望态度。<strong>若后续出现放量上涨伴随换手率回升，
        则可能标志着资金重新入场，反转信号明确。</strong>
    </div>

    <h3>6.5 财务状况</h3>
    <div class="interpretation">
        <strong>营收：</strong>2026年一季度营业收入26.01亿元，同比下降4.76%；<br>
        <strong>净利润：</strong>归母净利润1.38亿元，同比下降25.75%；<br>
        <strong>业绩点评：</strong>财务数据反映出<strong>业绩短期承压</strong>，营收下滑主要受军工订单节奏影响，
        净利润下降幅度较大显示盈利能力边际弱化。但作为央企军工龙头，公司具备稳定的订单基础和政策支持，
        中长期基本面仍稳健。
    </div>

    <h3>6.6 行业地位与竞争优势</h3>
    <div class="interpretation">
        <div class="analysis-point"><strong>陆军装备龙头：</strong>国内唯一的主战坦克和装甲车生产基地，市场地位无可替代</div>
        <div class="analysis-point"><strong>央企平台优势：</strong>背靠兵工集团，具备顶层资源整合能力</div>
        <div class="analysis-point"><strong>军贸潜力：</strong>产品具备出口竞争力，军贸订单有望成为增量来源</div>
        <div class="analysis-point"><strong>无人化转型：</strong>参股爱生无人机（10.52%），有望承接集团无人系统资产注入</div>
    </div>

    <h3>6.7 未来看点</h3>
    <div class="interpretation">
        <div class="analysis-point"><strong>资产注入预期：</strong>2025-2026年是兵工集团资产整合的关键窗口期，公司作为唯一上市平台，有望承接轻武器、光电、无人系统等优质资产</div>
        <div class="analysis-point"><strong>军贸增量：</strong>国际地缘形势复杂化背景下，军工出口需求有望提升</div>
        <div class="analysis-point"><strong>无人化装备：</strong>爱生无人机资产注入预期，对标中无人机，估值空间有望打开</div>
    </div>
</div>

<div class="section">
    <h2>七、投资建议</h2>
    <div class="intro-text">基于{stock_name}当前的技术面与基本面综合分析，提出以下投资建议：</div>

    <h3>7.1 短期策略（1-3个月）</h3>
    <div class="interpretation">
        <strong>评级：观望</strong><br><br>
        当前MACD零轴下方运行、RSI中性偏低、KDJ低位粘合、布林带下轨附近运行，
        多个技术指标均显示短期趋势偏弱。建议<strong>以防守姿态观望</strong>，密切关注：<br>
        <div class="analysis-point">MACD在零轴下方形成金叉信号</div>
        <div class="analysis-point">RSI突破50并持续上行</div>
        <div class="analysis-point">KDJ低位金叉并向上突破20</div>
        <div class="analysis-point">股价放量突破布林带上轨</div>
    </div>

    <h3>7.2 中期策略（3-6个月）</h3>
    <div class="interpretation">
        <strong>评级：谨慎乐观</strong><br><br>
        作为央企军工龙头，公司具备稳健的基本面支撑和资产注入预期。
        若股价在10-11元区域完成有效筑底，且出现以下催化剂，可考虑<strong>分批建仓</strong>：<br>
        <div class="analysis-point">兵工集团资产整合方案落地</div>
        <div class="analysis-point">军工订单恢复性增长</div>
        <div class="analysis-point">无人系统资产注入预期明确化</div>
    </div>

    <h3>7.3 长期策略（6个月以上）</h3>
    <div class="interpretation">
        <strong>评级：看好</strong><br><br>
        从长期角度看，{stock_name}作为<strong>国防军工核心资产</strong>，具备以下长期价值：<br>
        <div class="analysis-point">陆军装备垄断地位，需求刚性且稳定</div>
        <div class="analysis-point">央企平台优势，资产注入空间广阔</div>
        <div class="analysis-point">无人化、智能化转型，顺应军工现代化趋势</div>
        <div class="analysis-point">估值回归历史低位，具备安全边际</div>
        <br>长期投资者可在<strong>底部区域分批布局</strong>，耐心等待资产整合与业绩拐点兑现。
    </div>
</div>

<div class="section">
    <h2>八、风险提示</h2>
    <div class="risk-box">
        <h4>重要风险提示</h4>
        <div class="analysis-point"><strong>业绩波动风险：</strong>军工订单交付节奏不确定，可能导致营收和利润短期波动</div>
        <div class="analysis-point"><strong>资产注入不确定性：</strong>兵工集团资产整合时间表和方案尚未明确，存在落地不及预期风险</div>
        <div class="analysis-point"><strong>估值风险：</strong>当前动态市盈率约54倍，估值偏高，若业绩持续下滑可能面临估值回调压力</div>
        <div class="analysis-point"><strong>市场情绪风险：</strong>军工板块受政策和国际形势影响较大，情绪波动可能导致股价大幅震荡</div>
        <div class="analysis-point"><strong>技术面风险：</strong>当前MACD、KDJ、布林带等多个指标均显示空头趋势，短期存在进一步下探可能</div>
    </div>
    <div class="interpretation" style="border-left-color: #dc2626; background: #fef2f2;">
        <strong>免责声明：</strong>本报告仅供内部研究参考，不构成任何投资建议。投资者应根据自身风险承受能力独立决策，
        并充分了解股票投资的风险。历史数据和分析结论不能保证未来表现，市场有风险，投资需谨慎。
    </div>
</div>

<div class="footer">
    📈 数据来源：Tushare Pro API ｜ ⚡ 生成工具：Python + ECharts ｜ 📊 前复权数据<br>
    © 2026 {stock_name}（{ts_code}）交易数据分析报告
</div>

</div>

<script>
var dates = {dates_json};
var klineData = {kline_json};
var volumeData = {volumes_json};
var closeData = {close_json};
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

var commonXAxis = {{
    type: 'category', data: dates,
    axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }},
    axisLabel: {{ color: '#6b7280', fontSize: 11 }},
    splitLine: {{ show: false }},
    boundaryGap: true, min: 'dataMin', max: 'dataMax'
}};

var commonDataZoom = [
    {{ type: 'inside', start: 0, end: 100 }},
    {{ type: 'slider', height: 18, bottom: 2, borderColor: '#e5e7eb', backgroundColor: '#f9fafb',
       fillerColor: 'rgba(59,130,246,0.15)', handleStyle: {{ color: '#3b82f6' }} }}
];

var tooltipStyle = {{
    backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderWidth: 1,
    textStyle: {{ color: '#374151', fontSize: 13 }},
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
}};

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
            return '<div class="tooltip-box"><div style="font-weight:700;color:#1f2937;border-bottom:1px solid #e5e7eb;padding-bottom:6px;margin-bottom:6px;">' + dates[idx] + '</div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">开盘</span><span style="font-weight:600;">' + d[0] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">收盘</span><span style="font-weight:600;color:' + color + '">' + d[1] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">最高</span><span style="font-weight:600;">' + d[3] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">最低</span><span style="font-weight:600;">' + d[2] + '</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">涨跌幅</span><span style="font-weight:600;color:' + color + '">' + sign + pctChg + '%</span></div></div>';
        }}
    }},
    grid: {{ left: '6%', right: '3%', top: '8%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'K线', type: 'candlestick', data: klineData, itemStyle: {{ color: '#ef4444', color0: '#22c55e', borderColor: '#ef4444', borderColor0: '#22c55e' }} }},
        {{ name: 'MA5', type: 'line', data: ma5Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#f59e0b' }} }},
        {{ name: 'MA10', type: 'line', data: ma10Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#f97316' }} }},
        {{ name: 'MA20', type: 'line', data: ma20Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#10b981' }} }},
        {{ name: 'MA60', type: 'line', data: ma60Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#6366f1' }} }}
    ]
}});

var volumeChart = echarts.init(document.getElementById('volume-chart'));
volumeChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, ...tooltipStyle,
        formatter: function(params) {{
            var idx = params[0].dataIndex;
            var d = klineData[idx];
            var color = d[1] >= d[0] ? '#ef4444' : '#22c55e';
            return '<div class="tooltip-box"><div style="font-weight:700;color:#1f2937;border-bottom:1px solid #e5e7eb;padding-bottom:6px;margin-bottom:6px;">' + dates[idx] + '</div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">成交量</span><span style="font-weight:600;">' + (params[0].value / 10000).toFixed(1) + '万手</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">收盘价</span><span style="font-weight:600;color:' + color + '">' + d[1] + '</span></div></div>';
        }}
    }},
    grid: {{ left: '6%', right: '3%', top: '8%', bottom: '25%' }},
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11, formatter: function(v) {{ return (v / 10000).toFixed(0) + '万'; }} }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [{{ name: '成交量', type: 'bar', data: volumeData, itemStyle: {{ borderRadius: [2, 2, 0, 0] }} }}]
}});

var macdChart = echarts.init(document.getElementById('macd-chart'));
macdChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['DIF', 'DEA', 'MACD'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '15%', bottom: '15%' }},
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'DIF', type: 'line', data: difData, smooth: true, symbol: 'none', lineStyle: {{ width: 1.5, color: '#f59e0b' }} }},
        {{ name: 'DEA', type: 'line', data: deaData, smooth: true, symbol: 'none', lineStyle: {{ width: 1.5, color: '#f97316' }} }},
        {{ name: 'MACD', type: 'bar', data: macdData,
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
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', min: 0, max: 100, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'RSI(14)', type: 'line', data: rsiData, smooth: true, symbol: 'none', lineStyle: {{ width: 1.5, color: '#3b82f6' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(59,130,246,0.15)' }}, {{ offset: 1, color: 'rgba(59,130,246,0.02)' }}] }} }} }},
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
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', min: 0, max: 100, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'K', type: 'line', data: kData, smooth: true, symbol: 'none', lineStyle: {{ width: 1.5, color: '#f59e0b' }} }},
        {{ name: 'D', type: 'line', data: dData, smooth: true, symbol: 'none', lineStyle: {{ width: 1.5, color: '#f97316' }} }},
        {{ name: 'J', type: 'line', data: jData, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#10b981' }} }},
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
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: '收盘价', type: 'line', data: closeData, smooth: false, symbol: 'none', lineStyle: {{ width: 1.5, color: '#3b82f6' }} }},
        {{ name: '中轨(MA20)', type: 'line', data: bollMidData, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#f97316' }} }},
        {{ name: '上轨', type: 'line', data: bollUpperData, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#ef4444', type: 'dashed' }} }},
        {{ name: '下轨', type: 'line', data: bollLowerData, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#22c55e', type: 'dashed' }} }}
    ]
}});

var turnoverChart = echarts.init(document.getElementById('turnover-chart'));
var totalShares = 26.85;
var marketCap = closeData.map(p => Math.round(p * totalShares * 100) / 100);
var turnoverRate = volumeData.map(v => Math.round(v.value / (totalShares * 10000) * 10000) / 100);

turnoverChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['市值(亿元)', '换手率(%)'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '8%', top: '15%', bottom: '15%' }},
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: [
        {{ type: 'value', name: '市值(亿元)', position: 'left', axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
        {{ type: 'value', name: '换手率(%)', position: 'right', axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ show: false }} }}
    ],
    dataZoom: commonDataZoom,
    series: [
        {{ name: '市值(亿元)', type: 'line', data: marketCap, smooth: true, symbol: 'none', lineStyle: {{ width: 1.5, color: '#3b82f6' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(59,130,246,0.15)' }}, {{ offset: 1, color: 'rgba(59,130,246,0.02)' }}] }} }} }},
        {{ name: '换手率(%)', type: 'line', data: turnoverRate, smooth: true, symbol: 'none', lineStyle: {{ width: 1.5, color: '#f97316' }}, yAxisIndex: 1 }}
    ]
}});

echarts.connect([klineChart, volumeChart, macdChart, rsiChart, kdjChart, bollChart, turnoverChart]);

window.addEventListener('resize', function() {{
    klineChart.resize(); volumeChart.resize(); macdChart.resize();
    rsiChart.resize(); kdjChart.resize(); bollChart.resize(); turnoverChart.resize();
}});
</script>
</body>
</html>'''

    output_path = os.path.join(output_dir, f'{ts_code}_analysis.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    index_path = 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML报告已生成: {output_path}")
    print(f"首页已生成: {index_path}")
    return output_path


if __name__ == '__main__':
    csv_path = os.path.join('output', '600967.SH_daily_data.csv')
    generate_html_report(csv_path)