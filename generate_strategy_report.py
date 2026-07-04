import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

def calc_ma(data, n):
    return data.rolling(window=n).mean().tolist()

def calc_ema(data, n):
    return data.ewm(span=n, adjust=False).mean().tolist()

def calc_macd(closes, fast=12, slow=26, signal=9):
    ema_fast = pd.Series(calc_ema(pd.Series(closes), fast))
    ema_slow = pd.Series(calc_ema(pd.Series(closes), slow))
    dif = (ema_fast - ema_slow).tolist()
    dea = pd.Series(calc_ema(pd.Series(dif), signal)).tolist()
    macd_bar = [(dif[i] - dea[i]) for i in range(len(dif))]
    return dif, dea, macd_bar

def calc_rsi(closes, n=14):
    deltas = pd.Series(closes).diff()
    gains = deltas.where(deltas > 0, 0)
    losses = -deltas.where(deltas < 0, 0)
    avg_gain = gains.ewm(alpha=1/n, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1/n, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.tolist()

def calc_kdj(data, n=9, k_smooth=3, d_smooth=3):
    high = pd.Series([d['high'] for d in data])
    low = pd.Series([d['low'] for d in data])
    close = pd.Series([d['close'] for d in data])
    
    rsv = ((close - low.rolling(n).min()) / (high.rolling(n).max() - low.rolling(n).min())) * 100
    rsv = rsv.fillna(50).tolist()
    
    k_alpha = 1 / k_smooth
    k = []
    for i in range(len(rsv)):
        if i == 0:
            k.append(50 * (1 - k_alpha) + rsv[i] * k_alpha)
        else:
            k.append(k[i-1] * (1 - k_alpha) + rsv[i] * k_alpha)
    
    d_alpha = 1 / d_smooth
    d = []
    for i in range(len(k)):
        if i == 0:
            d.append(50 * (1 - d_alpha) + k[i] * d_alpha)
        else:
            d.append(d[i-1] * (1 - d_alpha) + k[i] * d_alpha)
    
    j = [3 * k[i] - 2 * d[i] for i in range(len(k))]
    return k, d, j

def calc_boll(closes, n=20, mult=2, ddof=0):
    mid = pd.Series(closes).rolling(n).mean().tolist()
    std = pd.Series(closes).rolling(n).std(ddof=ddof).tolist()
    upper = [mid[i] + mult * std[i] if mid[i] is not None and std[i] is not None else None for i in range(len(mid))]
    lower = [mid[i] - mult * std[i] if mid[i] is not None and std[i] is not None else None for i in range(len(mid))]
    return upper, mid, lower

def calc_atr(data, n=14):
    tr_list = []
    for i in range(len(data)):
        if i == 0:
            tr = data[i]['high'] - data[i]['low']
        else:
            tr = max(
                data[i]['high'] - data[i]['low'],
                abs(data[i]['high'] - data[i-1]['close']),
                abs(data[i]['low'] - data[i-1]['close'])
            )
        tr_list.append(tr)
    
    atr = []
    for i in range(len(tr_list)):
        if i == 0:
            atr.append(tr_list[i])
        else:
            atr.append(atr[i-1] * (1 - 1/n) + tr_list[i] * (1/n))
    return tr_list, atr

def detect_signals(data, dif, dea, rsi, k, d, upper, mid, lower, atr, macd_bar):
    signals = []
    for i in range(len(data)):
        if i < 35:
            signals.append({'date': data[i]['date'], 'signals': []})
            continue
            
        date = data[i]['date']
        close = data[i]['close']
        sigs = []
        
        if dif[i] is not None and dea[i] is not None and dif[i-1] is not None and dea[i-1] is not None:
            if dif[i-1] <= dea[i-1] and dif[i] > dea[i]:
                sigs.append({'type': 'buy', 'indicator': 'MACD金叉', 'strength': '中等', 'price': round(close, 2)})
            if dif[i-1] >= dea[i-1] and dif[i] < dea[i]:
                sigs.append({'type': 'sell', 'indicator': 'MACD死叉', 'strength': '中等', 'price': round(close, 2)})
            if dif[i] is not None and dif[i] > 0 and dif[i-1] <= 0:
                sigs.append({'type': 'buy', 'indicator': 'MACD零轴上穿', 'strength': '强', 'price': round(close, 2)})
            if dif[i] is not None and dif[i] < 0 and dif[i-1] >= 0:
                sigs.append({'type': 'sell', 'indicator': 'MACD零轴下穿', 'strength': '强', 'price': round(close, 2)})
        
        if rsi[i] is not None:
            if rsi[i] < 30 and rsi[i-1] >= 30:
                sigs.append({'type': 'buy', 'indicator': 'RSI超卖', 'strength': '弱', 'price': round(close, 2)})
            if rsi[i] > 70 and rsi[i-1] <= 70:
                sigs.append({'type': 'sell', 'indicator': 'RSI超买', 'strength': '弱', 'price': round(close, 2)})
        
        if k[i] is not None and d[i] is not None and k[i-1] is not None and d[i-1] is not None:
            if k[i-1] <= d[i-1] and k[i] > d[i]:
                sigs.append({'type': 'buy', 'indicator': 'KDJ金叉', 'strength': '中等', 'price': round(close, 2)})
            if k[i-1] >= d[i-1] and k[i] < d[i]:
                sigs.append({'type': 'sell', 'indicator': 'KDJ死叉', 'strength': '中等', 'price': round(close, 2)})
        
        if lower[i] is not None and close <= lower[i]:
            sigs.append({'type': 'buy', 'indicator': '触及布林带下轨', 'strength': '弱', 'price': round(close, 2)})
        if upper[i] is not None and close >= upper[i]:
            sigs.append({'type': 'sell', 'indicator': '触及布林带上轨', 'strength': '弱', 'price': round(close, 2)})
        
        signals.append({'date': date, 'signals': sigs})
    
    return signals

def generate_strategy_report(ts_code, stock_name, csv_path, output_dir='output'):
    df = pd.read_csv(csv_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    dates = df['trade_date'].dt.strftime('%Y-%m-%d').tolist()
    opens = df['open'].tolist()
    highs = df['high'].tolist()
    lows = df['low'].tolist()
    closes = df['close'].tolist()
    vols = df['vol'].tolist()
    amounts = df['amount'].tolist() if 'amount' in df.columns else [0]*len(closes)
    
    data = [{'date': dates[i], 'open': opens[i], 'high': highs[i], 'low': lows[i], 'close': closes[i], 'vol': vols[i]} for i in range(len(dates))]
    
    ma5 = calc_ma(pd.Series(closes), 5)
    ma10 = calc_ma(pd.Series(closes), 10)
    ma20 = calc_ma(pd.Series(closes), 20)
    ma60 = calc_ma(pd.Series(closes), 60)
    
    dif, dea, macd_bar = calc_macd(closes)
    rsi = calc_rsi(closes)
    k, d, j = calc_kdj(data)
    upper_boll, mid_boll, lower_boll = calc_boll(closes)
    tr, atr = calc_atr(data)
    
    # 将所有NaN替换为None，并用json.dumps序列化为JS的null
    def clean_nan(lst):
        return [None if (x is None or (isinstance(x, float) and np.isnan(x))) else x for x in lst]
    
    def js(lst):
        return json.dumps(clean_nan(lst))
    
    ma5_js = js(ma5)
    ma10_js = js(ma10)
    ma20_js = js(ma20)
    ma60_js = js(ma60)
    dif_js = js(dif)
    dea_js = js(dea)
    macd_bar_js = js(macd_bar)
    rsi_js = js(rsi)
    k_js = js(k)
    d_js = js(d)
    j_js = js(j)
    upper_boll_js = js(upper_boll)
    mid_boll_js = js(mid_boll)
    lower_boll_js = js(lower_boll)
    tr_js = js(tr)
    atr_js = js(atr)
    
    signals = detect_signals(data, dif, dea, rsi, k, d, upper_boll, mid_boll, lower_boll, atr, macd_bar)
    
    latest_idx = len(data) - 1
    latest_dif = round(dif[latest_idx], 4) if dif[latest_idx] else 'N/A'
    latest_dea = round(dea[latest_idx], 4) if dea[latest_idx] else 'N/A'
    latest_macd_bar = round(macd_bar[latest_idx], 4) if macd_bar[latest_idx] else 'N/A'
    latest_rsi = round(rsi[latest_idx], 2) if rsi[latest_idx] else 'N/A'
    latest_k = round(k[latest_idx], 2) if k[latest_idx] else 'N/A'
    latest_d = round(d[latest_idx], 2) if d[latest_idx] else 'N/A'
    latest_j = round(j[latest_idx], 2) if j[latest_idx] else 'N/A'
    latest_atr = round(atr[latest_idx], 2) if atr[latest_idx] else 'N/A'
    
    highest_price = round(max(closes), 2)
    lowest_price = round(min(closes), 2)
    start_price = round(closes[0], 2)
    end_price = round(closes[-1], 2)
    total_return = round((end_price - start_price) / start_price * 100, 2)
    
    avg_amount = round(sum(amounts)/len(amounts)/100000000, 2)
    max_amount = round(max(amounts)/100000000, 2)
    
    recent_signals = []
    for s in signals[-30:]:
        if s['signals']:
            recent_signals.append(s)
    
    sig_html = ''
    if recent_signals:
        sig_rows = []
        for s in recent_signals:
            for sig in s['signals']:
                sig_rows.append(f'<tr><td>{s["date"]}</td><td class="{sig["type"]}">{sig["type"]}</td><td>{sig["indicator"]}</td><td>{sig["strength"]}</td><td>{sig["price"]}</td></tr>')
        sig_html = f"""
        <table class="signal-table">
            <thead><tr><th>日期</th><th>类型</th><th>指标</th><th>强度</th><th>价格</th></tr></thead>
            <tbody>{''.join(sig_rows)}</tbody>
        </table>"""
    else:
        sig_html = '<p style="color:#999;">近30个交易日无信号</p>'
    
    sl_price = round(end_price - 2*latest_atr, 2) if isinstance(latest_atr, (int, float)) else 'N/A'
    tp_price = round(end_price + 3*latest_atr, 2) if isinstance(latest_atr, (int, float)) else 'N/A'
    sl_price2 = round(end_price - latest_atr, 2) if isinstance(latest_atr, (int, float)) else 'N/A'
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_name}（{ts_code}）近三年交易策略报告</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; background: #fff; color: #333; line-height: 1.8; padding-bottom: 60px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 30px 0; text-align: center; margin-bottom: 40px; }}
        .header h1 {{ font-size: 28px; font-weight: 600; margin-bottom: 8px; }}
        .header p {{ opacity: 0.9; font-size: 15px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ font-size: 22px; color: #444; border-bottom: 3px solid #667eea; padding-bottom: 8px; margin-bottom: 20px; }}
        .section h3 {{ font-size: 18px; color: #555; margin-bottom: 15px; }}
        .data-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .data-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .data-card .label {{ font-size: 13px; color: #888; margin-bottom: 8px; }}
        .data-card .value {{ font-size: 22px; font-weight: 600; color: #333; }}
        .data-card .value.positive {{ color: #ec0000; }}
        .data-card .value.negative {{ color: #00da3c; }}
        .chart-box {{ width: 100%; height: 400px; margin-bottom: 20px; }}
        .interpretation {{ background: #f8f9fa; padding: 20px; border-radius: 8px; font-size: 14px; line-height: 2; }}
        .interpretation strong {{ color: #667eea; }}
        .signal-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .signal-table th, .signal-table td {{ padding: 10px 12px; border: 1px solid #ddd; text-align: left; }}
        .signal-table th {{ background: #667eea; color: #fff; font-weight: 600; }}
        .signal-table tr:nth-child(even) {{ background: #f8f9fa; }}
        .signal-table .buy {{ color: #ec0000; font-weight: 600; }}
        .signal-table .sell {{ color: #00da3c; font-weight: 600; }}
        .strategy-box {{ background: #fff; border: 2px solid #667eea; border-radius: 10px; padding: 25px; margin-bottom: 20px; }}
        .strategy-box .title {{ font-size: 18px; font-weight: 600; color: #667eea; margin-bottom: 15px; }}
        .strategy-box .price {{ font-size: 16px; margin: 10px 0; line-height: 2.2; }}
        .strategy-box .entry {{ color: #ec0000; font-weight: 600; }}
        .strategy-box .exit {{ color: #00da3c; font-weight: 600; }}
        .strategy-box .stoploss {{ color: #f56c6c; font-weight: 600; }}
        .risk-box {{ background: #fff5f5; border: 1px solid #feb2b2; border-radius: 8px; padding: 15px; margin-top: 10px; }}
        .risk-box strong {{ color: #c53030; }}
        .tactic-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        .tactic-table th, .tactic-table td {{ padding: 12px; border: 1px solid #ddd; }}
        .tactic-table th {{ background: #f0f0f0; font-weight: 600; }}
        .tactic-table .condition {{ width: 40%; }}
        .tactic-table .action {{ width: 30%; }}
        .tactic-table .position {{ width: 30%; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{stock_name}（{ts_code}）近三年交易策略报告</h1>
        <p>数据周期：{dates[0]} ~ {dates[-1]} | 共 {len(dates)} 个交易日</p>
    </div>

    <div class="container">
        <div class="section">
            <h2>一、数据概览</h2>
            <div class="data-grid">
                <div class="data-card"><div class="label">起始价</div><div class="value">{start_price}</div></div>
                <div class="data-card"><div class="label">最新价</div><div class="value">{end_price}</div></div>
                <div class="data-card"><div class="label">最高价</div><div class="value">{highest_price}</div></div>
                <div class="data-card"><div class="label">最低价</div><div class="value">{lowest_price}</div></div>
                <div class="data-card"><div class="label">累计涨幅</div><div class="value {'positive' if total_return > 0 else 'negative'}">{total_return}%</div></div>
                <div class="data-card"><div class="label">日均成交额</div><div class="value">{avg_amount}亿</div></div>
                <div class="data-card"><div class="label">最大成交额</div><div class="value">{max_amount}亿</div></div>
                <div class="data-card"><div class="label">当前ATR</div><div class="value">{latest_atr}</div></div>
            </div>
        </div>

        <div class="section">
            <h2>二、技术指标分析</h2>
            
            <h3>1. K线与均线系统</h3>
            <div class="chart-box" id="kline-chart"></div>
            
            <h3>2. MACD指标</h3>
            <div class="chart-box" id="macd-chart"></div>
            
            <h3>3. RSI相对强弱指标</h3>
            <div class="chart-box" id="rsi-chart"></div>
            
            <h3>4. KDJ随机指标</h3>
            <div class="chart-box" id="kdj-chart"></div>
            
            <h3>5. 布林带</h3>
            <div class="chart-box" id="boll-chart"></div>
            
            <h3>6. ATR平均真实波幅</h3>
            <div class="chart-box" id="atr-chart"></div>
        </div>

        <div class="section">
            <h2>三、近期信号汇总（最近30个交易日）</h2>
            {sig_html}
        </div>

        <div class="section">
            <h2>四、详细交易策略方案</h2>
            
            <div class="strategy-box">
                <div class="title">📈 策略一：MACD趋势跟随策略</div>
                <p><strong>策略逻辑：</strong>以MACD金叉/死叉作为主要进出信号，配合零轴过滤提高胜率</p>
                <div class="price">
                    <span class="entry">⏰ 进场条件：</span>DIF上穿DEA且位于零轴上方（强信号）<br>
                    <span class="entry">⏰ 进场条件：</span>DIF上穿DEA且位于零轴下方（弱信号，需其他指标确认）<br>
                    <span class="exit">⏹️ 出场条件：</span>DIF下穿DEA形成死叉<br>
                    <span class="stoploss">🛡️ 止损：</span>入场价 - 2×ATR（约{sl_price}元）<br>
                    <span class="stoploss">🎯 止盈：</span>入场价 + 3×ATR（约{tp_price}元）或MACD死叉
                </div>
                <div class="risk-box"><strong>⚠️ 风险提示：</strong>震荡行情中金叉死叉频繁出现，需配合零轴过滤和成交量确认</div>
            </div>

            <div class="strategy-box">
                <div class="title">📈 策略二：RSI均值回归策略</div>
                <p><strong>策略逻辑：</strong>利用RSI超买超卖进行高抛低吸，适合震荡行情</p>
                <div class="price">
                    <span class="entry">⏰ 进场条件：</span>RSI从下方穿越30线（超卖反弹）<br>
                    <span class="exit">⏹️ 出场条件：</span>RSI从下方穿越70线（超买回落）<br>
                    <span class="stoploss">🛡️ 止损：</span>跌破近期低点或RSI再次跌破30<br>
                    <span class="stoploss">🎯 止盈：</span>布林带上轨或RSI到达70
                </div>
                <div class="risk-box"><strong>⚠️ 风险提示：</strong>强趋势中RSI可能长期处于超买/超卖区域，单独使用容易被套</div>
            </div>

            <div class="strategy-box">
                <div class="title">📈 策略三：布林带突破策略</div>
                <p><strong>策略逻辑：</strong>价格突破布林带上轨且带宽扩大时追涨，突破下轨时追跌</p>
                <div class="price">
                    <span class="entry">⏰ 进场条件：</span>收盘价突破布林带上轨且成交量放大<br>
                    <span class="exit">⏹️ 出场条件：</span>收盘价跌破布林带中轨或回到上轨内侧<br>
                    <span class="stoploss">🛡️ 止损：</span>入场价 - 1×ATR（约{sl_price2}元）<br>
                    <span class="stoploss">🎯 止盈：</span>突破后涨幅达到布林带带宽的1.5倍
                </div>
                <div class="risk-box"><strong>⚠️ 风险提示：</strong>假突破概率较高，需确认带宽是否同步扩大</div>
            </div>

            <div class="strategy-box">
                <div class="title">📈 策略四：多指标共振策略（推荐）</div>
                <p><strong>策略逻辑：</strong>综合MACD、RSI、KDJ三个指标的信号，提高交易胜率</p>
                <div class="price">
                    <span class="entry">⏰ 进场条件：</span><br>
                    • MACD：DIF&gt;DEA且位于零轴上方（或零轴附近上穿）<br>
                    • RSI：从30-50区间向上突破，未进入超买<br>
                    • KDJ：K线上穿D线形成金叉，K值在20-50区间<br><br>
                    <span class="exit">⏹️ 出场条件：</span><br>
                    • MACD形成死叉（主信号）<br>
                    • RSI突破70进入超买区域<br>
                    • KDJ形成死叉<br><br>
                    <span class="stoploss">🛡️ 止损：</span>入场价 - 2×ATR（约{sl_price}元）<br>
                    <span class="stoploss">🎯 止盈：</span>目标涨幅10%-15%或三个指标中有两个发出卖出信号
                </div>
                <div class="risk-box"><strong>⚠️ 风险提示：</strong>多指标共振信号出现频率较低，需耐心等待</div>
            </div>
        </div>

        <div class="section">
            <h2>五、当前持仓管理建议</h2>
            <table class="tactic-table">
                <thead><tr><th class="condition">当前条件</th><th class="action">操作建议</th><th class="position">仓位比例</th></tr></thead>
                <tbody>
                    <tr><td>MACD金叉+RSI&gt;50+KDJ金叉</td><td>加仓买入</td><td>70%-80%</td></tr>
                    <tr><td>MACD金叉但RSI&lt;30</td><td>谨慎买入</td><td>30%-50%</td></tr>
                    <tr><td>MACD零轴下方死叉</td><td>减仓观望</td><td>0%-30%</td></tr>
                    <tr><td>MACD零轴上方死叉但RSI&gt;50</td><td>减仓持有</td><td>50%-60%</td></tr>
                    <tr><td>RSI&gt;70且价格触及布林带上轨</td><td>止盈卖出</td><td>减至50%</td></tr>
                    <tr><td>价格跌破布林带下轨且成交量放大</td><td>止损卖出</td><td>减至20%</td></tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>六、风险提示</h2>
            <div class="interpretation">
                <strong>市场风险：</strong>有色金属板块受宏观经济、政策调控、美元汇率等因素影响较大，股价波动可能超出技术指标预测范围。<br><br>
                <strong>技术风险：</strong>技术指标存在滞后性，历史表现不代表未来收益。多指标共振也可能失效。<br><br>
                <strong>操作风险：</strong>本报告仅供学习参考，不构成投资建议。实际操作需结合个人风险承受能力和市场环境，建议先进行模拟盘验证。<br><br>
                <strong>止损纪律：</strong>任何策略都必须严格执行止损，单次亏损不应超过账户资金的2%-3%。
            </div>
        </div>
    </div>

    <script>
        const dates = {dates};
        const opens = {opens};
        const highs = {highs};
        const lows = {lows};
        const closes = {closes};
        const ma5 = {ma5_js};
        const ma10 = {ma10_js};
        const ma20 = {ma20_js};
        const ma60 = {ma60_js};
        const dif = {dif_js};
        const dea = {dea_js};
        const macdBar = {macd_bar_js};
        const rsi = {rsi_js};
        const kLine = {k_js};
        const dLine = {d_js};
        const jLine = {j_js};
        const upperBoll = {upper_boll_js};
        const midBoll = {mid_boll_js};
        const lowerBoll = {lower_boll_js};
        const tr = {tr_js};
        const atr = {atr_js};

        const baseX = {{type: 'category', data: dates, boundaryGap: true, axisLabel: {{fontSize: 10}}, axisLine: {{lineStyle: {{color: '#ccc'}}}}}};

        const klineChart = echarts.init(document.getElementById('kline-chart'));
        klineChart.setOption({{
            tooltip: {{trigger: 'axis', axisPointer: {{type: 'cross'}}}},
            legend: {{data: ['MA5', 'MA10', 'MA20', 'MA60'], top: 4}},
            grid: {{left: 60, right: 20, top: 30, bottom: 40}},
            xAxis: baseX,
            yAxis: {{scale: true, splitLine: {{lineStyle: {{color: '#f0f0f0'}}}}}},
            dataZoom: [{{type: 'inside'}}, {{type: 'slider', bottom: 0, height: 20}}],
            series: [
                {{type: 'candlestick', data: dates.map((_,i) => [opens[i], closes[i], lows[i], highs[i]]), itemStyle: {{color: '#ec0000', color0: '#00da3c'}}}},
                {{type: 'line', name: 'MA5', data: ma5, smooth: true, symbol: 'none', lineStyle: {{width: 1, color: '#e6a23c'}}}},
                {{type: 'line', name: 'MA10', data: ma10, smooth: true, symbol: 'none', lineStyle: {{width: 1, color: '#409eff'}}}},
                {{type: 'line', name: 'MA20', data: ma20, smooth: true, symbol: 'none', lineStyle: {{width: 1, color: '#f56c6c'}}}},
                {{type: 'line', name: 'MA60', data: ma60, smooth: true, symbol: 'none', lineStyle: {{width: 1, color: '#909399'}}}}
            ]
        }});

        const macdChart = echarts.init(document.getElementById('macd-chart'));
        macdChart.setOption({{
            tooltip: {{trigger: 'axis', axisPointer: {{type: 'cross'}}}},
            legend: {{data: ['DIF', 'DEA', 'MACD'], top: 4}},
            grid: {{left: 60, right: 20, top: 30, bottom: 40}},
            xAxis: baseX,
            yAxis: {{splitLine: {{lineStyle: {{color: '#f0f0f0'}}}}}},
            dataZoom: [{{type: 'inside'}}, {{type: 'slider', bottom: 0, height: 20}}],
            series: [
                {{type: 'line', name: 'DIF', data: dif, symbol: 'none', lineStyle: {{width: 1, color: '#409eff'}}}},
                {{type: 'line', name: 'DEA', data: dea, symbol: 'none', lineStyle: {{width: 1, color: '#e6a23c'}}}},
                {{type: 'bar', name: 'MACD', data: macdBar.map(v => ({{value: v, itemStyle: {{color: v >= 0 ? '#ec0000' : '#00da3c'}}}}))}}
            ]
        }});

        const rsiChart = echarts.init(document.getElementById('rsi-chart'));
        rsiChart.setOption({{
            tooltip: {{trigger: 'axis'}},
            legend: {{data: ['RSI14'], top: 4}},
            grid: {{left: 60, right: 20, top: 30, bottom: 40}},
            xAxis: baseX,
            yAxis: {{min: 0, max: 100, splitLine: {{lineStyle: {{color: '#f0f0f0'}}}}}},
            dataZoom: [{{type: 'inside'}}, {{type: 'slider', bottom: 0, height: 20}}],
            series: [
                {{type: 'line', name: 'RSI14', data: rsi, symbol: 'none', lineStyle: {{width: 1, color: '#409eff'}}}},
                {{type: 'line', name: '70', data: dates.map(() => 70), symbol: 'none', lineStyle: {{width: 1, type: 'dashed', color: '#f56c6c'}}}},
                {{type: 'line', name: '30', data: dates.map(() => 30), symbol: 'none', lineStyle: {{width: 1, type: 'dashed', color: '#00da3c'}}}}
            ]
        }});

        const kdjChart = echarts.init(document.getElementById('kdj-chart'));
        kdjChart.setOption({{
            tooltip: {{trigger: 'axis'}},
            legend: {{data: ['K', 'D', 'J'], top: 4}},
            grid: {{left: 60, right: 20, top: 30, bottom: 40}},
            xAxis: baseX,
            yAxis: {{splitLine: {{lineStyle: {{color: '#f0f0f0'}}}}}},
            dataZoom: [{{type: 'inside'}}, {{type: 'slider', bottom: 0, height: 20}}],
            series: [
                {{type: 'line', name: 'K', data: kLine, symbol: 'none', lineStyle: {{width: 1, color: '#409eff'}}}},
                {{type: 'line', name: 'D', data: dLine, symbol: 'none', lineStyle: {{width: 1, color: '#e6a23c'}}}},
                {{type: 'line', name: 'J', data: jLine, symbol: 'none', lineStyle: {{width: 1, color: '#f56c6c'}}}}
            ]
        }});

        const bollChart = echarts.init(document.getElementById('boll-chart'));
        bollChart.setOption({{
            tooltip: {{trigger: 'axis', axisPointer: {{type: 'cross'}}}},
            legend: {{data: ['收盘价', '上轨', '中轨', '下轨'], top: 4}},
            grid: {{left: 60, right: 20, top: 30, bottom: 40}},
            xAxis: baseX,
            yAxis: {{scale: true, splitLine: {{lineStyle: {{color: '#f0f0f0'}}}}}},
            dataZoom: [{{type: 'inside'}}, {{type: 'slider', bottom: 0, height: 20}}],
            series: [
                {{type: 'line', name: '收盘价', data: closes, symbol: 'none', lineStyle: {{width: 1, color: '#333'}}}},
                {{type: 'line', name: '上轨', data: upperBoll, symbol: 'none', lineStyle: {{width: 1, color: '#f56c6c'}}}},
                {{type: 'line', name: '中轨', data: midBoll, symbol: 'none', lineStyle: {{width: 1, color: '#409eff'}}}},
                {{type: 'line', name: '下轨', data: lowerBoll, symbol: 'none', lineStyle: {{width: 1, color: '#00da3c'}}}}
            ]
        }});

        const atrChart = echarts.init(document.getElementById('atr-chart'));
        atrChart.setOption({{
            tooltip: {{trigger: 'axis', axisPointer: {{type: 'cross'}}}},
            legend: {{data: ['TR', 'ATR'], top: 4}},
            grid: {{left: 60, right: 20, top: 30, bottom: 40}},
            xAxis: baseX,
            yAxis: {{splitLine: {{lineStyle: {{color: '#f0f0f0'}}}}}},
            dataZoom: [{{type: 'inside'}}, {{type: 'slider', bottom: 0, height: 20}}],
            series: [
                {{type: 'bar', name: 'TR', data: tr, itemStyle: {{color: 'rgba(144,147,153,0.4)'}}}},
                {{type: 'line', name: 'ATR', data: atr, symbol: 'none', lineStyle: {{width: 1.5, color: '#409eff'}}}}
            ]
        }});

        window.addEventListener('resize', () => {{
            klineChart.resize(); macdChart.resize(); rsiChart.resize();
            kdjChart.resize(); bollChart.resize(); atrChart.resize();
        }});
    </script>
</body>
</html>"""

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{ts_code}_strategy_report.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    report_path = f'{ts_code}_strategy_report.html'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f'策略报告已生成: {output_path}')
    print(f'根目录报告: {report_path}')
    return output_path

if __name__ == '__main__':
    generate_strategy_report('601899.SH', '紫金矿业', 'output/601899.SH_daily_data.csv')
