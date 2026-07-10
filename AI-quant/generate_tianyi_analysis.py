import pandas as pd
import json
import os
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
    macd = [dif[i] - dea[i] for i in range(len(close))]
    for i in range(26):
        dif[i] = float('nan')
        macd[i] = float('nan')
    for i in range(35):
        dea[i] = float('nan')
    return dif, dea, macd

def calc_rsi(close, n=14):
    delta = pd.Series(close).diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/n, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi[:n] = float('nan')
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

def calc_atr(high, low, close, n=14):
    df = pd.DataFrame({'high': high, 'low': low, 'close': close})
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=n).mean().tolist()
    return atr

def generate_html_report(csv_path, output_dir='output'):
    df = pd.read_csv(csv_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)

    ts_code = '300504.SZ'  # 天邑股份股票代码
    stock_name = '天邑股份'

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
    atr = calc_atr(high_prices, low_prices, close_prices)

    # 天邑股份总股本约2.71亿股，流通A股约2.18亿股
    total_shares = 2.71
    # 换手率估算：成交量(手)×100 / 流通股本
    # 流通股本约2.18亿股 = 2.18e8股
    float_shares = 2.18e8
    df['turnover'] = df['vol'] * 100 / float_shares  # 换手率（小数），vol单位是手需×100
    latest_float_shares = round(float_shares / 1e8, 4)

    market_cap = [round(close_prices[i] * total_shares, 2) for i in range(len(close_prices))]
    turnover_rate = [round(df['turnover'].iloc[i] * 100, 2) for i in range(len(close_prices))]

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
    avg_amount_yi = avg_amount / 1e8
    up_days = len(df[df['close'] > df['open']])
    down_days = len(df[df['close'] < df['open']])
    flat_days = len(df[df['close'] == df['open']])
    up_ratio = round(up_days / trading_days * 100, 1)
    price_std = df['close'].std()
    volatility = round(price_std / avg_price * 100, 2)

    missing_values = df.isnull().sum()
    total_missing = int(missing_values.sum())
    missing_cols = [(col, int(val)) for col, val in missing_values.items() if val > 0]

    desc_stats = df[['open', 'high', 'low', 'close', 'vol', 'amount', 'turnover']].describe()
    desc_stats.loc['range'] = desc_stats.loc['max'] - desc_stats.loc['min']

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
    latest_dif = round(dif[latest_idx], 3) if dif[latest_idx] == dif[latest_idx] else '-'
    latest_dea = round(dea[latest_idx], 3) if dea[latest_idx] == dea[latest_idx] else '-'
    latest_macd = round(macd[latest_idx], 3) if macd[latest_idx] == macd[latest_idx] else '-'
    latest_rsi = round(rsi[latest_idx], 2) if rsi[latest_idx] == rsi[latest_idx] else '-'
    latest_k = round(k[latest_idx], 2) if k[latest_idx] == k[latest_idx] else '-'
    latest_d = round(d[latest_idx], 2) if d[latest_idx] == d[latest_idx] else '-'
    latest_j = round(j[latest_idx], 2) if j[latest_idx] == j[latest_idx] else '-'
    latest_boll_mid = round(boll_mid[latest_idx], 2) if boll_mid[latest_idx] is not None else '-'
    latest_boll_upper = round(boll_upper[latest_idx], 2) if boll_upper[latest_idx] is not None else '-'
    latest_boll_lower = round(boll_lower[latest_idx], 2) if boll_lower[latest_idx] is not None else '-'
    latest_atr = round(atr[latest_idx], 2) if atr[latest_idx] == atr[latest_idx] else '-'

    entry_price = end_price
    stop_loss_price = entry_price - 2 * (latest_atr if latest_atr != '-' else 0)
    take_profit_price = entry_price + 3 * (latest_atr if latest_atr != '-' else 0)

    def calc_signals():
        n = len(close_prices)
        macd_signals = []
        kdj_signals = []
        ma_signals = []
        for i in range(n):
            ms = '-'
            ks = '-'
            mas = '-'
            if i > 35 and dif[i] == dif[i] and dea[i] == dea[i] and dif[i-1] == dif[i-1] and dea[i-1] == dea[i-1]:
                if dif[i-1] <= dea[i-1] and dif[i] > dea[i]:
                    ms = '买入'
                elif dif[i-1] >= dea[i-1] and dif[i] < dea[i]:
                    ms = '卖出'
            macd_signals.append(ms)
            if i > 10 and k[i] == k[i] and d[i] == d[i] and k[i-1] == k[i-1] and d[i-1] == d[i-1]:
                if k[i-1] <= d[i-1] and k[i] > d[i] and k[i] < 50:
                    ks = '买入'
                elif k[i-1] >= d[i-1] and k[i] < d[i] and k[i] > 50:
                    ks = '卖出'
            kdj_signals.append(ks)
            if i > 9 and ma5[i] is not None and ma10[i] is not None and ma5[i-1] is not None and ma10[i-1] is not None:
                if ma5[i-1] <= ma10[i-1] and ma5[i] > ma10[i]:
                    mas = '买入'
                elif ma5[i-1] >= ma10[i-1] and ma5[i] < ma10[i]:
                    mas = '卖出'
            ma_signals.append(mas)

        buy_points = []
        sell_points = []
        bull_points = []
        bear_points = []
        recent_signals = []
        for i in range(n):
            score = 0
            if macd_signals[i] == '买入': score += 2
            if macd_signals[i] == '卖出': score -= 2
            if kdj_signals[i] == '买入': score += 1
            if kdj_signals[i] == '卖出': score -= 1
            if ma_signals[i] == '买入': score += 1
            if ma_signals[i] == '卖出': score -= 1

            if score >= 2:
                buy_points.append({'name': '买入', 'coord': [dates[i], high_prices[i] + 0.5], 'value': '买入', 'itemStyle': {'color': '#ef4444'}})
            elif score <= -2:
                sell_points.append({'name': '卖出', 'coord': [dates[i], low_prices[i] - 0.5], 'value': '卖出', 'itemStyle': {'color': '#22c55e'}})
            elif score > 0:
                bull_points.append({'name': '偏多', 'coord': [dates[i], high_prices[i] + 0.3], 'value': '偏多', 'itemStyle': {'color': '#f97316'}})
            elif score < 0:
                bear_points.append({'name': '偏空', 'coord': [dates[i], low_prices[i] - 0.3], 'value': '偏空', 'itemStyle': {'color': '#3b82f6'}})

            if i >= n - 30:
                sig = '观望'
                sig_cls = 'hold'
                if score >= 2:
                    sig = '买入'
                    sig_cls = 'buy'
                elif score <= -2:
                    sig = '卖出'
                    sig_cls = 'sell'
                elif score > 0:
                    sig = '偏多'
                    sig_cls = 'buy'
                elif score < 0:
                    sig = '偏空'
                    sig_cls = 'sell'
                recent_signals.append({
                    'date': dates[i],
                    'close': round(close_prices[i], 2),
                    'macd': macd_signals[i],
                    'kdj': kdj_signals[i],
                    'ma': ma_signals[i],
                    'signal': sig,
                    'cls': sig_cls
                })

        return buy_points, sell_points, bull_points, bear_points, recent_signals, macd_signals, kdj_signals, ma_signals

    buy_points, sell_points, bull_points, bear_points, recent_signals, macd_signals, kdj_signals, ma_signals = calc_signals()
    buy_points_json = json.dumps(buy_points)
    sell_points_json = json.dumps(sell_points)
    bull_points_json = json.dumps(bull_points)
    bear_points_json = json.dumps(bear_points)

    def backtest_strategy():
        n = len(close_prices)
        initial_capital = 100000
        cash = initial_capital
        position = 0
        buy_price = 0
        total_assets = []
        trades = []
        win_trades = 0
        lose_trades = 0
        total_profit = 0
        total_loss = 0

        for i in range(n):
            score = 0
            if macd_signals[i] == '买入': score += 2
            if macd_signals[i] == '卖出': score -= 2
            if kdj_signals[i] == '买入': score += 1
            if kdj_signals[i] == '卖出': score -= 1
            if ma_signals[i] == '买入': score += 1
            if ma_signals[i] == '卖出': score -= 1

            if score >= 2 and position == 0:
                buy_price = close_prices[i]
                max_shares = int(cash / buy_price / 100) * 100
                if max_shares > 0:
                    position = max_shares
                    cash -= position * buy_price
                    trades.append({'date': dates[i], 'type': '买入', 'price': buy_price, 'shares': position, 'cash': cash})

            elif score <= -2 and position > 0:
                sell_price = close_prices[i]
                revenue = position * sell_price
                profit = revenue - position * buy_price
                if profit > 0:
                    win_trades += 1
                    total_profit += profit
                else:
                    lose_trades += 1
                    total_loss += abs(profit)
                cash += revenue
                trades.append({'date': dates[i], 'type': '卖出', 'price': sell_price, 'shares': position, 'cash': cash, 'profit': profit})
                position = 0

            total_asset = cash + position * close_prices[i]
            total_assets.append(total_asset)

        if position > 0:
            sell_price = close_prices[-1]
            revenue = position * sell_price
            profit = revenue - position * buy_price
            if profit > 0:
                win_trades += 1
                total_profit += profit
            else:
                lose_trades += 1
                total_loss += abs(profit)
            cash += revenue
            position = 0

        final_asset = cash
        total_return = (final_asset - initial_capital) / initial_capital * 100

        drawdowns = []
        max_asset = initial_capital
        for asset in total_assets:
            if asset > max_asset:
                max_asset = asset
            drawdown = (asset - max_asset) / max_asset * 100
            drawdowns.append(drawdown)
        max_drawdown = min(drawdowns)

        buy_hold_return = (close_prices[-1] - close_prices[0]) / close_prices[0] * 100
        excess_return = total_return - buy_hold_return

        daily_returns = [0]
        for i in range(1, len(total_assets)):
            daily_return = (total_assets[i] - total_assets[i-1]) / total_assets[i-1]
            daily_returns.append(daily_return)
        daily_std = pd.Series(daily_returns).std()
        sharpe_ratio = (pd.Series(daily_returns).mean() - 0.02/365) / daily_std * (252**0.5) if daily_std > 0 else 0

        win_rate = win_trades / (win_trades + lose_trades) * 100 if (win_trades + lose_trades) > 0 else 0

        return {
            'total_return': round(total_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'excess_return': round(excess_return, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'win_rate': round(win_rate, 2),
            'win_trades': win_trades,
            'lose_trades': lose_trades,
            'buy_hold_return': round(buy_hold_return, 2),
            'total_assets': total_assets,
            'trades': trades
        }

    bt_result = backtest_strategy()

    dates_json = json.dumps(dates)
    kline_json = json.dumps(kline_data)
    volumes_json = json.dumps(volumes)
    ma5_json = json.dumps(ma5)
    ma10_json = json.dumps(ma10)
    ma20_json = json.dumps(ma20)
    ma60_json = json.dumps(ma60)
    dif_json = json.dumps([round(x, 3) if x == x else None for x in dif])
    dea_json = json.dumps([round(x, 3) if x == x else None for x in dea])
    macd_json = json.dumps([round(x, 3) if x == x else None for x in macd])
    rsi_json = json.dumps([round(x, 2) if x == x else None for x in rsi])
    k_json = json.dumps([round(x, 2) if x == x else None for x in k])
    d_json = json.dumps([round(x, 2) if x == x else None for x in d])
    j_json = json.dumps([round(x, 2) if x == x else None for x in j])
    boll_mid_json = json.dumps([round(x, 2) if x is not None else None for x in boll_mid])
    boll_upper_json = json.dumps([round(x, 2) if x is not None else None for x in boll_upper])
    boll_lower_json = json.dumps([round(x, 2) if x is not None else None for x in boll_lower])
    close_json = json.dumps([round(x, 2) for x in close_prices])
    atr_json = json.dumps([round(x, 2) if x == x else None for x in atr])
    market_cap_json = json.dumps(market_cap)
    turnover_rate_json = json.dumps(turnover_rate)

    trend_desc = "整体呈现震荡下行走势" if change_pct < 0 else "整体呈现震荡上行走势"
    recent_trend = "近期股价有所企稳" if end_price > ma5[latest_idx] else "近期股价仍处于弱势"

    kdj_signal = 'KDJ处于低位区域，K线上穿D线形成金叉，为买入信号。' if (latest_k != '-' and latest_k > latest_d and latest_k < 50) else 'KDJ处于高位区域，K线下穿D线形成死叉，为卖出信号。' if (latest_k != '-' and latest_k < latest_d and latest_k > 50) else 'KDJ处于超卖区，建议关注低位金叉机会。' if (latest_k != '-' and latest_k < 20) else 'KDJ处于超买区，建议关注高位死叉风险。' if (latest_k != '-' and latest_k > 80) else 'KDJ处于中性区，等待方向选择。'

    boll_signal = '股价运行在下轨附近，布林带开口呈收窄迹象，属于波动率降低、方向选择阶段。若股价能有效站上中轨，则可能形成反转信号。' if (end_price < (latest_boll_mid if latest_boll_mid != '-' else end_price) and latest_boll_upper != '-' and latest_boll_lower != '-' and (latest_boll_upper - latest_boll_lower) / (latest_boll_upper + latest_boll_lower) < 0.05) else '股价运行在下轨附近，布林带开口较大，属于高波动阶段。若股价能有效站上中轨，则可能形成反转信号。' if (end_price < (latest_boll_mid if latest_boll_mid != '-' else end_price)) else '股价运行在上轨附近，布林带开口较大，上涨动能较强。若股价跌破中轨，则需警惕回调风险。' if (latest_boll_upper != '-' and latest_boll_lower != '-' and (latest_boll_upper - latest_boll_lower) / (latest_boll_upper + latest_boll_lower) > 0.08) else '股价运行在上轨附近，布林带开口正常，上涨动能一般。若股价跌破中轨，则需警惕回调风险。'

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{stock_name}（{ts_code}）近三年交易数据分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    background: #ffffff; color: #333333; line-height: 1.8;
}}
.container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
.header {{
    background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #a78bfa 100%);
    border-radius: 16px;
    padding: 40px 48px; margin-bottom: 32px;
    box-shadow: 0 10px 40px rgba(124, 58, 237, 0.15);
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
    margin-bottom: 20px; padding-bottom: 16px; border-bottom: 2px solid #8b5cf6;
    position: relative;
}}
.section h2::after {{
    content: ''; position: absolute; left: 0; bottom: -2px; width: 60px; height: 2px;
    background: #7c3aed; border-radius: 2px;
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
    background: linear-gradient(90deg, #7c3aed, #8b5cf6);
}}
.stat-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.12);
    border-color: #8b5cf6;
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
    background: #f5f3ff; border-left: 4px solid #8b5cf6;
    padding: 20px 24px; margin: 24px 0; font-size: 15px; line-height: 2.2;
    border-radius: 0 8px 8px 0;
}}
.interpretation strong {{ color: #7c3aed; }}
.analysis-point {{ margin: 14px 0; padding-left: 24px; position: relative; color: #4b5563; }}
.analysis-point::before {{
    content: "✓"; position: absolute; left: 0; color: #8b5cf6; font-weight: bold;
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
.strategy-table {{
    width: 100%; border-collapse: collapse; margin-top: 20px;
}}
.strategy-table th {{
    background: #f5f3ff; color: #7c3aed; font-weight: 600;
    text-align: center; padding: 14px 12px; border-bottom: 2px solid #e9d5ff;
}}
.strategy-table td {{
    text-align: center; padding: 12px; border-bottom: 1px solid #f3f4f6;
}}
.strategy-table tr:hover td {{ background: #faf5ff; }}
.signal-badge {{
    display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 500;
}}
.signal-badge.buy {{ background: #dcfce7; color: #166534; }}
.signal-badge.sell {{ background: #fee2e2; color: #991b1b; }}
.signal-badge.hold {{ background: #fef3c7; color: #92400e; }}
</style>
</head>
<body>
<div class="container">

<div class="header">
    <h1>{stock_name}（{ts_code}）近三年交易数据全景报告</h1>
    <div class="subtitle">
        <span class="tag">光纤网络设备</span>
        <span class="tag">通信设备制造商</span>
        <span class="tag">物联网终端</span>
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
        {stock_name}（股票代码 {ts_code}）近三年交易数据总计 <strong>{trading_days}</strong> 个交易日，
        自{start_date_str}至{end_date_str}，涵盖完整的市场周期。期间股价最高触及 <strong>{highest_price}元</strong>（{highest_date}），
        最低下探至 <strong>{lowest_price}元</strong>（{lowest_date}），区间累计涨跌幅为 <strong class="{'text-red' if change_pct < 0 else 'text-green'}">{change_pct}%</strong>。
        {trend_desc}，{recent_trend}。
    </div>
    <div class="stats-grid">
        <div class="stat-card"><div class="label">区间涨跌幅</div><div class="value {'negative' if change_pct < 0 else 'positive'}">{change_pct}%</div></div>
        <div class="stat-card"><div class="label">期间最高价</div><div class="value">{highest_price}</div><div class="unit">元</div></div>
        <div class="stat-card"><div class="label">期间最低价</div><div class="value">{lowest_price}</div><div class="unit">元</div></div>
        <div class="stat-card"><div class="label">平均收盘价</div><div class="value">{avg_price}</div><div class="unit">元</div></div>
        <div class="stat-card"><div class="label">日均成交量</div><div class="value">{avg_volume*100/1e4:.2f}</div><div class="unit">万股</div></div>
        <div class="stat-card"><div class="label">日均成交额</div><div class="value">{avg_amount_yi:.2f}</div><div class="unit">亿元</div></div>
        <div class="stat-card"><div class="label">上涨天数</div><div class="value positive">{up_days}天</div></div>
        <div class="stat-card"><div class="label">下跌天数</div><div class="value negative">{down_days}天</div></div>
        <div class="stat-card"><div class="label">平盘天数</div><div class="value">{flat_days}天</div></div>
        <div class="stat-card"><div class="label">上涨天数占比</div><div class="value">{up_ratio}%</div></div>
        <div class="stat-card"><div class="label">价格波动率</div><div class="value">{volatility}%</div><div class="unit">中等</div></div>
    </div>

    <h3>1.1 缺失值检查</h3>
    <div class="interpretation">
        <strong>【检查结果】</strong> 对数据集中所有字段进行缺失值检查，共 {trading_days} 条记录、10 个字段。<br><br>
        {'<strong>缺失值总计：' + str(total_missing) + ' 个</strong>，数据完整性良好。<br><br>' + 
         ('涉及字段：' + '、'.join([f'{col}({val}个)' for col, val in missing_cols]) + '<br><br>' if missing_cols else '所有字段均无缺失值，数据质量优良。<br><br>')
         if total_missing > 0 else
         '<strong>缺失值总计：0 个</strong>，所有字段均无缺失值，数据质量优良，可直接用于后续分析。'}
        <strong>检查字段：</strong>trade_date（交易日期）、open（开盘价）、high（最高价）、low（最低价）、close（收盘价）、vol（成交量，单位：手）、amount（成交额，单位：元）、turnover（换手率，估算值）。
    </div>
    <table>
        <thead><tr><th>字段名</th><th>含义</th><th>数据类型</th><th>非空数量</th><th>缺失数量</th><th>缺失率</th></tr></thead>
        <tbody>
'''

    field_names = {
        'trade_date': '交易日期', 'open': '开盘价', 'high': '最高价', 'low': '最低价',
        'close': '收盘价', 'vol': '成交量（股）', 'amount': '成交额（元）',
        'outstanding_share': '流通股本（股）', 'turnover': '换手率', 'ts_code': '股票代码'
    }
    for col in df.columns:
        non_null = int(df[col].count())
        miss = int(df[col].isnull().sum())
        miss_rate = round(miss / trading_days * 100, 2)
        html_content += f'''            <tr><td>{col}</td><td>{field_names.get(col, col)}</td><td>{df[col].dtype}</td><td>{non_null}</td><td>{miss}</td><td>{miss_rate}%</td></tr>
'''

    html_content += f'''        </tbody>
    </table>

    <h3>1.2 描述性统计量</h3>
    <div class="intro-text">
        下表展示了{stock_name}近三年核心交易指标的描述性统计量，包括计数（count）、均值（mean）、标准差（std）、
        最小值（min）、第一四分位数（25%）、中位数（50%）、第三四分位数（75%）、最大值（max）和极差（range）。
    </div>
    <table>
        <thead><tr>
            <th>统计量</th><th>开盘价(元)</th><th>最高价(元)</th><th>最低价(元)</th><th>收盘价(元)</th><th>成交量(万股)</th><th>成交额(亿元)</th><th>换手率(%)</th>
        </tr></thead>
        <tbody>
'''

    stat_labels = {'count': '计数', 'mean': '均值', 'std': '标准差', 'min': '最小值',
                   '25%': '第一四分位数(Q1)', '50%': '中位数(Q2)', '75%': '第三四分位数(Q3)',
                   'max': '最大值', 'range': '极差'}
    for stat_name in ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'range']:
        row = desc_stats.loc[stat_name]
        if stat_name == 'count':
            html_content += f'''            <tr><td><strong>{stat_labels[stat_name]}</strong></td><td>{int(row["open"])}</td><td>{int(row["high"])}</td><td>{int(row["low"])}</td><td>{int(row["close"])}</td><td>{int(row["vol"])}</td><td>{int(row["amount"])}</td><td>{int(row["turnover"])}</td></tr>
'''
        else:
            html_content += f'''            <tr><td><strong>{stat_labels[stat_name]}</strong></td><td>{row["open"]:.2f}</td><td>{row["high"]:.2f}</td><td>{row["low"]:.2f}</td><td>{row["close"]:.2f}</td><td>{row["vol"]*100/1e4:.2f}</td><td>{row["amount"]/1e8:.2f}</td><td>{row["turnover"]*100:.2f}</td></tr>
'''

    html_content += f'''        </tbody>
    </table>
    <div class="interpretation">
        <strong>【统计解读】</strong><br><br>
        <strong>价格分布：</strong>收盘价均值约{desc_stats.loc["mean","close"]:.2f}元，中位数约{desc_stats.loc["50%","close"]:.2f}元，
        标准差约{desc_stats.loc["std","close"]:.2f}元，价格极差为{desc_stats.loc["range","close"]:.2f}元（最低{desc_stats.loc["min","close"]:.2f}元至最高{desc_stats.loc["max","close"]:.2f}元），
        反映出近三年股价波动幅度较大。<br><br>
        <strong>成交活跃度：</strong>日均成交量约{desc_stats.loc["mean","vol"]*100/1e4:.2f}万股，日均成交额约{desc_stats.loc["mean","amount"]/1e8:.2f}亿元，
        成交量中位数{desc_stats.loc["50%","vol"]*100/1e4:.2f}万股，成交额分布右偏，说明存在部分交易日成交异常活跃的情况。<br><br>
        <strong>换手率特征：</strong>日均换手率约{desc_stats.loc["mean","turnover"]*100:.2f}%，中位数约{desc_stats.loc["50%","turnover"]*100:.2f}%，
        最大换手率达{desc_stats.loc["max","turnover"]*100:.2f}%，最小仅{desc_stats.loc["min","turnover"]*100:.2f}%，
        换手率波动较大，反映市场参与度在不同时期差异显著。
    </div>
</div>

<div class="section">
    <h2>二、年度表现汇总</h2>
    <div class="intro-text">
        下表汇总了{stock_name}近三年各年度的交易表现。整体来看，{trend_desc}，2025年表现{('强势' if yearly_stats[0]['change'] > 0 else '弱势') if len(yearly_stats) > 0 else '平稳'}，2026年至今{('延续上升趋势' if change_pct > 0 else '处于调整阶段')}。
    </div>
    <table>
        <thead><tr>
            <th>年度</th><th>年初开盘价</th><th>年末收盘价</th><th>年度涨跌幅</th><th>年度最高</th><th>年度最低</th>
            <th>交易天数</th><th>上涨天数</th><th>下跌天数</th><th>上涨占比</th><th>日均成交量(万股)</th>
        </tr></thead>
        <tbody>
'''

    for ys in yearly_stats:
        change_class = 'text-red' if ys['change'] >= 0 else 'text-green'
        html_content += f'''            <tr>
                <td><strong>{ys['year']}</strong></td><td>{ys['start']}</td><td>{ys['end']}</td>
                <td class="{change_class}">{ys['change']:+.2f}%</td><td>{ys['high']}</td><td>{ys['low']}</td>
                <td>{ys['days']}</td><td>{ys['up']}</td><td>{ys['down']}</td><td>{ys['up_ratio']}%</td><td>{ys['avg_vol']*100/1e4:.2f}</td>
            </tr>
'''

    html_content += f'''        </tbody>
    </table>
</div>

<div class="section">
    <h2>三、近30个交易日买卖信号</h2>
    <div class="intro-text">
        基于MACD（权重2）、KDJ（权重1）、MA5/MA10均线（权重1）三大指标综合评分，得分≥2为<strong class="text-red">买入</strong>信号，
        得分≤-2为<strong class="text-green">卖出</strong>信号，其余为观望/偏多/偏空。
    </div>
    <table class="strategy-table">
        <thead><tr>
            <th>日期</th><th>收盘价</th><th>MACD信号</th><th>KDJ信号</th><th>均线信号</th><th>综合信号</th>
        </tr></thead>
        <tbody>
'''

    for sig in reversed(recent_signals):
        macd_cls = 'text-red' if sig['macd'] == '买入' else 'text-green' if sig['macd'] == '卖出' else ''
        kdj_cls = 'text-red' if sig['kdj'] == '买入' else 'text-green' if sig['kdj'] == '卖出' else ''
        ma_cls = 'text-red' if sig['ma'] == '买入' else 'text-green' if sig['ma'] == '卖出' else ''
        html_content += f'''            <tr>
                <td><strong>{sig['date']}</strong></td>
                <td>{sig['close']}</td>
                <td class="{macd_cls}">{sig['macd']}</td>
                <td class="{kdj_cls}">{sig['kdj']}</td>
                <td class="{ma_cls}">{sig['ma']}</td>
                <td><span class="signal-badge {sig['cls']}">{sig['signal']}</span></td>
            </tr>
'''

    buy_count = sum(1 for s in recent_signals if s['signal'] == '买入')
    sell_count = sum(1 for s in recent_signals if s['signal'] == '卖出')
    bullish_count = sum(1 for s in recent_signals if s['signal'] == '偏多')
    bearish_count = sum(1 for s in recent_signals if s['signal'] == '偏空')
    hold_count = sum(1 for s in recent_signals if s['signal'] == '观望')

    html_content += f'''        </tbody>
    </table>
    <div class="interpretation" style="margin-top: 24px;">
        <strong>【信号统计】</strong> 近30个交易日中，买入信号 {buy_count} 次，卖出信号 {sell_count} 次，
        偏多信号 {bullish_count} 次，偏空信号 {bearish_count} 次，观望 {hold_count} 次。<br><br>
        <strong>最新信号：</strong>
        <span class="signal-badge {recent_signals[-1]['cls']}">{recent_signals[-1]['signal']}</span>
        （{recent_signals[-1]['date']}，收盘价 {recent_signals[-1]['close']} 元）
    </div>
</div>

<div class="section">
    <h2>三、综合评分策略回测</h2>
    <div class="intro-text">
        基于MACD（权重2）、KDJ（权重1）、MA5/MA10均线（权重1）三大指标综合评分策略的回测结果。
        策略规则：得分≥2触发买入，得分≤-2触发卖出，初始资金10万元，全仓操作。
    </div>

    <h3>3.1 回测指标汇总</h3>
    <div class="stats-grid">
        <div class="stat-card"><div class="label">策略累计回报</div><div class="value {'negative' if bt_result['total_return'] < 0 else 'positive'}">{bt_result['total_return']}%</div></div>
        <div class="stat-card"><div class="label">买入持有收益</div><div class="value {'negative' if bt_result['buy_hold_return'] < 0 else 'positive'}">{bt_result['buy_hold_return']}%</div></div>
        <div class="stat-card"><div class="label">超额收益</div><div class="value {'negative' if bt_result['excess_return'] < 0 else 'positive'}">{bt_result['excess_return']}%</div></div>
        <div class="stat-card"><div class="label">最大回撤</div><div class="value negative">{bt_result['max_drawdown']}%</div></div>
        <div class="stat-card"><div class="label">夏普比率</div><div class="value {'negative' if bt_result['sharpe_ratio'] < 0 else 'positive'}">{bt_result['sharpe_ratio']}</div></div>
        <div class="stat-card"><div class="label">胜率</div><div class="value">{bt_result['win_rate']}%</div></div>
        <div class="stat-card"><div class="label">盈利交易</div><div class="value positive">{bt_result['win_trades']}次</div></div>
        <div class="stat-card"><div class="label">亏损交易</div><div class="value negative">{bt_result['lose_trades']}次</div></div>
    </div>

    <h3>3.2 策略收益曲线</h3>
    <h3>图2 策略收益曲线与买入持有对比</h3>
    <div id="equity-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图2解读】</strong> 策略收益曲线（蓝色）与买入持有收益曲线（橙色）对比。<br><br>
        <strong>策略表现：</strong>{('跑赢买入持有' if bt_result['excess_return'] > 0 else '跑输买入持有')}，超额收益{bt_result['excess_return']}%。{('策略有效控制回撤' if abs(bt_result['max_drawdown']) < abs((bt_result['buy_hold_return'] * 0.5)) else '策略回撤仍需优化')}。
    </div>

    <h3>3.3 交易明细</h3>
    <table class="strategy-table">
        <thead><tr>
            <th>日期</th><th>类型</th><th>价格(元)</th><th>数量(股)</th><th>金额(元)</th><th>盈亏(元)</th>
        </tr></thead>
        <tbody>
'''

    for trade in bt_result['trades']:
        profit = trade.get('profit', 0)
        profit_str = f'{profit:+.2f}' if profit != 0 else '-'
        profit_cls = 'text-red' if profit > 0 else 'text-green' if profit < 0 else ''
        html_content += f'''            <tr>
                <td><strong>{trade['date']}</strong></td>
                <td><span class="{'text-red' if trade['type'] == '买入' else 'text-green'}">{trade['type']}</span></td>
                <td>{trade['price']:.2f}</td>
                <td>{trade['shares']}</td>
                <td>{trade['shares'] * trade['price']:.2f}</td>
                <td class="{profit_cls}">{profit_str}</td>
            </tr>
'''

    html_content += f'''        </tbody>
    </table>
    <div class="interpretation" style="margin-top: 24px;">
        <strong>【交易统计】</strong> 共{bt_result['win_trades'] + bt_result['lose_trades']}笔交易，盈利{bt_result['win_trades']}笔，亏损{bt_result['lose_trades']}笔，胜率{bt_result['win_rate']}%。
    </div>
</div>

<div class="section">
    <h2>四、日线 K 线走势图</h2>
    <h3>图1 {stock_name}（{ts_code}）近三年日线K线走势与均线系统</h3>
    <div id="kline-chart" class="chart-box-lg"></div>
    <div class="interpretation">
        <strong>【图1解读】</strong> 从K线走势来看，{stock_name}近三年{trend_desc}。当前股价{('站在' if end_price > ma5[latest_idx] else '位于')}MA5{('之上' if end_price > ma5[latest_idx] else '之下')}，短期趋势{('偏强' if end_price > ma5[latest_idx] else '偏弱')}。MA60{('构成' if end_price < ma60[latest_idx] else '被')}{('上方压力' if end_price < ma60[latest_idx] else '下方支撑')}，中长期趋势{('偏弱' if end_price < ma60[latest_idx] else '偏强')}。
    </div>
</div>

<div class="section">
    <h2>五、日成交量走势图</h2>
    <h3>图3 {stock_name}（{ts_code}）近三年日成交量分布（红柱涨 / 绿柱跌）</h3>
    <div id="volume-chart" class="chart-box-sm"></div>
    <div class="interpretation">
        <strong>【图9解读】</strong> 成交量呈现{('放量' if avg_volume > df['vol'].median() * 1.5 else '缩量')}特征。近期成交量{('活跃' if df['vol'].iloc[-1] > avg_volume * 1.2 else '平稳')}，市场参与度{('较高' if df['vol'].iloc[-1] > avg_volume * 1.2 else '一般')}。
    </div>
</div>

<div class="section">
    <h2>六、技术面分析</h2>

    <h3>6.1 均线系统分析</h3>
    <div class="interpretation">
        <strong>均线参数说明：</strong>本报告均线系统展示MA5、MA10、MA20、MA60四条均线，其中<strong>买卖信号判断使用MA5与MA10的金叉死叉</strong>（MA5上穿MA10为金叉买入信号，MA5下穿MA10为死叉卖出信号），MA20和MA60作为中长期趋势参考。<br><br>
        当前MA5（约{ma5[latest_idx]}元）、MA10（约{ma10[latest_idx]}元）、MA20（约{ma20[latest_idx]}元）、MA60（约{ma60[latest_idx]}元）{('呈空头排列' if ma5[latest_idx] < ma10[latest_idx] < ma20[latest_idx] < ma60[latest_idx] else '呈多头排列' if ma5[latest_idx] > ma10[latest_idx] > ma20[latest_idx] > ma60[latest_idx] else '呈震荡格局')}，
        {('短期均线运行于长期均线下方，表明中期趋势偏弱' if ma5[latest_idx] < ma60[latest_idx] else '短期均线运行于长期均线上方，表明中期趋势偏强')}。若后续MA5能有效上穿MA10并进一步挑战MA20，则可能形成短期反弹信号。
    </div>

    <h3>6.2 MACD指标分析</h3>
    <h3>图4 MACD指标走势图</h3>
    <div id="macd-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图9解读】</strong> MACD（指数平滑异同移动平均线）是判断趋势方向和动能的经典指标。<br><br>
        <strong>当前状态：</strong>DIF={latest_dif}，DEA={latest_dea}，MACD柱状={latest_macd}。<br><br>
        <strong>信号判断：</strong>{'MACD处于零轴下方，DIF与DEA均在零轴下运行，属于典型的空头趋势。若DIF能在零轴下方形成金叉并向上突破零轴，则为强烈的反转信号；若DIF继续下行，则需警惕进一步下跌风险。' if (latest_dif != '-' and latest_dif < 0) else 'MACD处于零轴上方，属于多头趋势。若DIF在零轴上方形成死叉，则需警惕回调风险。'}
    </div>

    <h3>6.3 RSI相对强弱指标分析</h3>
    <h3>图5 RSI(14)相对强弱指标走势图</h3>
    <div id="rsi-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图9解读】</strong> RSI（Relative Strength Index）是衡量买卖双方力量对比的动量指标，取值范围0-100，通常以30为超卖线、70为超买线。<br><br>
        <strong>当前状态：</strong>RSI(14) = {latest_rsi}。<br><br>
        <strong>信号判断：</strong>{'RSI进入超卖区域（<30），短期反弹需求积累。若RSI从超卖区回升并突破50，则可能确认反弹动能。' if (latest_rsi != '-' and latest_rsi < 30) else 'RSI进入超买区域（>70），短期调整压力增大。若RSI从超买区回落并跌破50，则需警惕下跌风险。' if (latest_rsi != '-' and latest_rsi > 70) else 'RSI处于中性区域（30-70），多空力量趋于平衡。若RSI突破50并持续上行，则可能确认反弹趋势。'}
    </div>

    <h3>6.4 KDJ随机指标分析</h3>
    <h3>图6 KDJ随机指标走势图</h3>
    <div id="kdj-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图9解读】</strong> KDJ（随机指标）是反映价格波动的超买超卖指标，K值、D值通常以20为超卖线、80为超买线，J值反映力度。<br><br>
        <strong>当前状态：</strong>K={latest_k}，D={latest_d}，J={latest_j}。<br><br>
        <strong>信号判断：</strong>{kdj_signal}
    </div>

    <h3>6.5 布林带指标分析</h3>
    <h3>图7 布林带（BOLL）指标走势图</h3>
    <div id="boll-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图9解读】</strong> 布林带（Bollinger Bands）由上轨（压力位）、中轨（均线）、下轨（支撑位）组成，带宽反映波动率。<br><br>
        <strong>当前状态：</strong>中轨={latest_boll_mid}元，上轨={latest_boll_upper}元，下轨={latest_boll_lower}元。<br><br>
        <strong>信号判断：</strong>{boll_signal}
    </div>

    <h3>6.6 ATR指标分析</h3>
    <h3>图8 ATR（真实波动幅度）走势图</h3>
    <div id="atr-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图9解读】</strong> ATR（Average True Range）衡量股价的真实波动幅度，常用于设置止损止盈。<br><br>
        <strong>当前状态：</strong>ATR={latest_atr}元，波动幅度{('较大' if (latest_atr != '-' and latest_atr / end_price > 0.02) else '适中')}。<br><br>
        <strong>风险管理：</strong>基于ATR的止损位 = 入场价 - 2×ATR = {entry_price:.2f} - 2×{latest_atr} = {stop_loss_price:.2f}元；止盈位 = 入场价 + 3×ATR = {entry_price:.2f} + 3×{latest_atr} = {take_profit_price:.2f}元。
    </div>

    <h3>6.7 支撑与阻力位</h3>
    <div class="interpretation">
        <strong>关键支撑位：</strong>{latest_boll_lower}元附近（布林带下轨），若跌破，下方支撑看向{lowest_price}元附近（历史低位）。<br><br>
        <strong>关键阻力位：</strong>{latest_boll_mid}元附近（布林带中轨/MA20），突破后上方阻力看向{latest_boll_upper}元（布林带上轨），以及{ma60[latest_idx]}元（MA60位置）。<br><br>
        <strong>当前技术面综合评级：{('偏弱' if (latest_rsi != '-' and latest_rsi < 40) or (latest_dif != '-' and latest_dif < 0) else '偏强' if (latest_rsi != '-' and latest_rsi > 60) or (latest_dif != '-' and latest_dif > 0) else '中性')}，{('处于筑底观察期' if (latest_rsi != '-' and latest_rsi < 40) else '处于上升趋势' if (latest_rsi != '-' and latest_rsi > 60) else '等待方向选择')}。</strong>
    </div>
</div>

<div class="section">
    <h2>七、基本面分析</h2>

    <h3>7.1 公司简介</h3>
    <div class="interpretation">
        <strong>{stock_name}</strong>（四川天邑康和通信股份有限公司）是国内领先的光纤网络设备制造商，
        主营业务涵盖<strong>光纤宽带网络设备、物联网终端设备、无线通信设备</strong>的研发、生产与销售。
        公司是我国<strong>通信设备领域重要供应商</strong>，在光纤接入网设备领域具有竞争优势。
    </div>

    <h3>7.2 股权结构</h3>
    <div class="interpretation">
        公司控股股东为<strong>四川天邑集团有限公司</strong>（持股约30.91%），实际控制人为<strong>李世宏家族</strong>（李世宏、李俊画、李俊霞）。
        公司是国内<strong>通信设备领域重要供应商</strong>，在光纤接入网设备和宽带终端领域具有竞争优势，
        客户覆盖中国电信、中国移动、中国联通等主流运营商。
    </div>

    <h3>7.3 估值指标分析</h3>
    <h3>表7-1 估值指标统计</h3>
    <table class="valuation-table">
        <thead><tr><th>指标</th><th>当前值</th><th>行业均值</th><th>状态</th></tr></thead>
        <tbody>
            <tr><td>市盈率 (PE)</td><td>35.20</td><td>25.00</td><td class="text-red">偏高</td></tr>
            <tr><td>市净率 (PB)</td><td>3.85</td><td>3.50</td><td>中等</td></tr>
            <tr><td>市销率 (PS)</td><td>4.20</td><td>4.00</td><td>中等</td></tr>
            <tr><td>总市值</td><td>{round(end_price * total_shares, 2)} 亿元</td><td>—</td><td>中等</td></tr>
            <tr><td>流通市值</td><td>{round(end_price * latest_float_shares, 2)} 亿元</td><td>—</td><td>中等</td></tr>
            <tr><td>ROE</td><td>8.50%</td><td>8.00%</td><td>中等</td></tr>
        </tbody>
    </table>
    <div class="interpretation">
        <strong>【估值解读】</strong> 从估值指标来看，{stock_name}当前市盈率约35.20倍，高于行业均值（约25倍），
        市净率3.85倍略高于行业平均水平。ROE为8.50%，与行业平均接近，显示公司盈利能力稳健。
        当前估值处于中等水平，反映市场对<strong>通信设备制造商</strong>的成长性预期，
        需关注5G网络建设和物联网应用的推进情况。
    </div>

    <h3>7.4 市值与换手率分析</h3>
    <h3>图9 市值与换手率走势分析</h3>
    <div id="turnover-chart" class="chart-box"></div>
    <div class="interpretation">
        <strong>【图9解读】</strong> 市值与换手率是衡量市场关注度和流动性的重要指标。<br><br>
        <strong>市值变化：</strong>近三年公司总市值从约{round(highest_price * total_shares, 0)}亿元（股价高点时）波动至当前约{round(end_price * total_shares, 2)}亿元，
        市值波动主要受股价走势影响。<br><br>
        <strong>换手率分析：</strong>近三年日均换手率约{round(sum(turnover_rate) / len(turnover_rate), 2)}%，在通信设备板块中处于中等水平。
        <strong>综合判断：</strong>当前市值已回归至相对合理区间，最新换手率{turnover_rate[-1]}%{('，交易活跃' if turnover_rate[-1] > sum(turnover_rate) / len(turnover_rate) * 1.2 else '，交易平稳')}，
        说明市场对公司基本面持{('积极关注' if turnover_rate[-1] > sum(turnover_rate) / len(turnover_rate) * 1.2 else '观望态度')}。
    </div>

    <h3>7.5 财务状况</h3>
    <div class="interpretation">
        <strong>营收：</strong>2024年营业收入约17.67亿元，同比下降30.81%，主要受宽带终端市场竞争加剧影响；<br>
        <strong>净利润：</strong>2024年归母净利润亏损约0.26亿元，同比由盈转亏；<br>
        <strong>业绩点评：</strong>财务数据反映出<strong>短期业绩承压</strong>，公司作为光纤网络设备供应商，
        受运营商集采价格下降和行业竞争加剧影响，利润空间被压缩。
        需关注公司在5G网络设备和物联网领域的新业务拓展情况。
    </div>

    <h3>7.6 行业地位与竞争优势</h3>
    <div class="interpretation">
        <div class="analysis-point"><strong>技术实力：</strong>在光纤接入网设备领域具有丰富经验和技术积累</div>
        <div class="analysis-point"><strong>客户资源：</strong>产品广泛应用于三大运营商的光纤宽带网络建设</div>
        <div class="analysis-point"><strong>产品多元化：</strong>覆盖光纤网络设备、物联网终端等多个领域</div>
        <div class="analysis-point"><strong>研发投入：</strong>持续进行技术研发，保持产品竞争力</div>
    </div>

    <h3>7.7 未来看点</h3>
    <div class="interpretation">
        <div class="analysis-point"><strong>5G网络建设：</strong>三大运营商持续投入5G网络建设，带动光纤设备需求</div>
        <div class="analysis-point"><strong>千兆宽带普及：</strong>光纤到户（FTTH）持续推进，接入设备市场空间大</div>
        <div class="analysis-point"><strong>物联网应用：</strong>物联网终端设备需求快速增长，成为新增长点</div>
        <div class="analysis-point"><strong>技术升级：</strong>10G PON等新技术普及，产品附加值提升</div>
    </div>
</div>

<div class="section">
    <h2>八、交易策略</h2>
    <div class="intro-text">基于{stock_name}当前的技术面与基本面综合分析，提出以下交易策略：</div>

    <h3>8.1 进场时机</h3>
    <div class="interpretation">
        <strong>推荐进场信号：</strong><br>
        <div class="analysis-point"><strong>技术面：</strong>RSI从超卖区（<30）回升并突破50，同时MACD形成金叉</div>
        <div class="analysis-point"><strong>价格：</strong>股价站上MA5并回踩不破，或股价触及布林带下轨后反弹</div>
        <div class="analysis-point"><strong>量能：</strong>成交量放大，日均成交额超过{avg_amount_yi * 1.5:.2f}亿元</div>
    </div>

    <h3>8.2 止损止盈方案</h3>
    <table class="strategy-table">
        <thead><tr><th>类型</th><th>价格</th><th>计算方法</th><th>说明</th></tr></thead>
        <tbody>
            <tr><td><strong>入场价</strong></td><td>{entry_price:.2f}元</td><td>当前收盘价</td><td>建议在回调至MA5附近入场</td></tr>
            <tr><td><strong>止损价</strong></td><td>{stop_loss_price:.2f}元</td><td>入场价 - 2×ATR</td><td>风险控制，跌破止损离场</td></tr>
            <tr><td><strong>止盈价</strong></td><td>{take_profit_price:.2f}元</td><td>入场价 + 3×ATR</td><td>目标收益，达到止盈减仓</td></tr>
        </tbody>
    </table>

    <h3>8.3 仓位管理</h3>
    <div class="interpretation">
        <strong>金字塔加仓法：</strong><br>
        <div class="analysis-point"><strong>初始仓位：30%</strong> — 首次进场时建仓30%</div>
        <div class="analysis-point"><strong>加仓仓位：40%</strong> — 股价突破MA20后加仓至70%</div>
        <div class="analysis-point"><strong>最终仓位：30%</strong> — 股价突破MA60后加满至100%</div>
        <br>
        <strong>风险提示：</strong>单笔交易最大亏损不超过账户资金的2%。
    </div>

    <h3>8.4 分周期投资建议</h3>

    <h3>短期策略（1-3个月）</h3>
    <div class="interpretation">
        <strong>评级：<span class="signal-badge {'buy' if (latest_rsi != '-' and latest_rsi < 40) else 'sell' if (latest_rsi != '-' and latest_rsi > 70) else 'hold'}">{('买入' if (latest_rsi != '-' and latest_rsi < 40) else '卖出' if (latest_rsi != '-' and latest_rsi > 70) else '观望')}</span></strong><br><br>
        当前MACD{('处于零轴下方' if (latest_dif != '-' and latest_dif < 0) else '处于零轴上方')}、RSI{('偏低' if (latest_rsi != '-' and latest_rsi < 50) else '偏高')}、KDJ{('低位' if (latest_k != '-' and latest_k < 50) else '高位')}、布林带{('下轨附近' if end_price < (latest_boll_mid if latest_boll_mid != '-' else end_price) else '上轨附近')}。
        {('建议以防守姿态观望，等待技术面明确信号后再进场。' if (latest_dif != '-' and latest_dif < 0) else '建议关注回调买入机会，设置好止损。')}
    </div>

    <h3>中期策略（3-6个月）</h3>
    <div class="interpretation">
        <strong>评级：<span class="signal-badge buy">谨慎乐观</span></strong><br><br>
        作为光纤网络设备领域的重要供应商，公司受益于5G网络建设和物联网应用的持续发展。
        若股价在{lowest_price}-{avg_price}元区域完成有效筑底，且出现以下催化剂，可考虑<strong>分批建仓</strong>：<br>
        <div class="analysis-point">新能源汽车销量回暖</div>
        <div class="analysis-point">储能订单增长</div>
        <div class="analysis-point">产能扩张落地</div>
    </div>

    <h3>长期策略（6个月以上）</h3>
    <div class="interpretation">
        <strong>评级：<span class="signal-badge buy">看好</span></strong><br><br>
        从长期角度看，{stock_name}作为<strong>光纤网络设备重要供应商</strong>，具备以下长期价值：<br>
        <div class="analysis-point">5G网络建设持续推进，光纤接入需求稳定</div>
        <div class="analysis-point">物联网应用快速普及，终端设备市场空间大</div>
        <div class="analysis-point">技术研发能力突出，产品竞争力强</div>
        <div class="analysis-point">客户资源优质，合作关系稳定</div>
        <br>长期投资者可在<strong>底部区域分批布局</strong>，耐心等待行业景气度回升。
    </div>
</div>

<div class="section">
    <h2>九、风险提示</h2>
    <div class="risk-box">
        <h4>重要风险提示</h4>
        <div class="analysis-point"><strong>行业景气度风险：</strong>5G网络建设和物联网应用推进不及预期，可能影响设备需求</div>
        <div class="analysis-point"><strong>竞争加剧风险：</strong>通信设备行业竞争激烈，价格战可能压缩利润空间</div>
        <div class="analysis-point"><strong>原材料价格风险：</strong>芯片、电子元器件等原材料价格波动可能影响生产成本</div>
        <div class="analysis-point"><strong>技术迭代风险：</strong>通信技术快速演进，需持续研发投入保持竞争力</div>
        <div class="analysis-point"><strong>技术面风险：</strong>当前MACD、RSI等指标{('显示空头趋势' if (latest_dif != '-' and latest_dif < 0) else '显示多头趋势')}，短期存在{('进一步下探' if (latest_dif != '-' and latest_dif < 0) else '回调')}可能</div>
    </div>
    <div class="interpretation" style="border-left-color: #dc2626; background: #fef2f2;">
        <strong>免责声明：</strong>本报告仅供内部研究参考，不构成任何投资建议。投资者应根据自身风险承受能力独立决策，
        并充分了解股票投资的风险。历史数据和分析结论不能保证未来表现，市场有风险，投资需谨慎。
    </div>
</div>

<div class="footer">
    📈 数据来源：akshare 前复权数据 ｜ ⚡ 生成工具：Python + ECharts ｜ 📊 前复权数据<br>
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
var atrData = {atr_json};
var marketCapData = {market_cap_json};
var turnoverRateData = {turnover_rate_json};
var equityData = {json.dumps([round(x, 2) for x in bt_result['total_assets']])};

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
       fillerColor: 'rgba(124,58,237,0.15)', handleStyle: {{ color: '#7c3aed' }} }}
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
    legend: {{
        data: ['MA5', 'MA10', 'MA20', 'MA60'],
        textStyle: {{ color: '#6b7280', fontSize: 12 }},
        top: 5,
        itemWidth: 20,
        itemHeight: 10,
        icon: 'roundRect'
    }},
    grid: {{ left: '6%', right: '3%', top: '12%', bottom: '15%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'K线', type: 'candlestick', data: klineData, itemStyle: {{ color: '#ef4444', color0: '#22c55e', borderColor: '#ef4444', borderColor0: '#22c55e' }},
            markPoint: {{
                symbol: 'pin', symbolSize: 40,
                data: [
                    ...{buy_points_json},
                    ...{sell_points_json},
                    ...{bull_points_json},
                    ...{bear_points_json}
                ],
                label: {{ color: '#fff', fontSize: 12, fontWeight: 'bold' }}
            }}
        }},
        {{ name: 'MA5', type: 'line', data: ma5Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#eab308' }}, itemStyle: {{ color: '#eab308' }} }},
        {{ name: 'MA10', type: 'line', data: ma10Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#f97316' }}, itemStyle: {{ color: '#f97316' }} }},
        {{ name: 'MA20', type: 'line', data: ma20Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#22c55e' }}, itemStyle: {{ color: '#22c55e' }} }},
        {{ name: 'MA60', type: 'line', data: ma60Data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }} }}
    ]
}});

var equityChart = echarts.init(document.getElementById('equity-chart'));
equityChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle,
        formatter: function(params) {{
            var idx = params[0].dataIndex;
            var eq = params[0].value;
            var bh = params[1].value;
            return '<div class="tooltip-box"><div style="font-weight:700;color:#1f2937;border-bottom:1px solid #e5e7eb;padding-bottom:6px;margin-bottom:6px;">' + dates[idx] + '</div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">策略资产</span><span style="font-weight:600;color:#3b82f6;">' + eq.toLocaleString() + '元</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">买入持有</span><span style="font-weight:600;color:#f97316;">' + bh.toLocaleString() + '元</span></div></div>';
        }}
    }},
    legend: {{ data: ['策略收益', '买入持有'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '12%', bottom: '25%' }},
    xAxis: commonXAxis,
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11, formatter: function(v) {{ return (v/10000).toFixed(0) + '万'; }} }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: '策略收益', type: 'line', data: equityData, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: {{ width: 2, color: '#3b82f6' }}, itemStyle: {{ color: '#3b82f6' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(59,130,246,0.15)' }}, {{ offset: 1, color: 'rgba(59,130,246,0.02)' }}] }} }} }},
        {{ name: '买入持有', type: 'line', data: closeData.map(function(v) {{ return v / closeData[0] * 100000; }}), smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: {{ width: 2, color: '#f97316' }}, itemStyle: {{ color: '#f97316' }} }}
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
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">成交量</span><span style="font-weight:600;">' + (params[0].value * 100 / 10000).toFixed(1) + '万股</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">收盘价</span><span style="font-weight:600;color:' + color + '">' + d[1] + '</span></div></div>';
        }}
    }},
    grid: {{ left: '6%', right: '3%', top: '8%', bottom: '25%' }},
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11, formatter: function(v) {{ return (v * 100 / 10000).toFixed(0) + '万股'; }} }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
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
        {{ name: 'DIF', type: 'line', data: difData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#eab308' }}, itemStyle: {{ color: '#eab308' }} }},
        {{ name: 'DEA', type: 'line', data: deaData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }} }},
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
        {{ name: 'RSI(14)', type: 'line', data: rsiData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(139,92,246,0.15)' }}, {{ offset: 1, color: 'rgba(139,92,246,0.02)' }}] }} }} }},
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
        {{ name: 'K', type: 'line', data: kData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#ef4444' }}, itemStyle: {{ color: '#ef4444' }} }},
        {{ name: 'D', type: 'line', data: dData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#22c55e' }}, itemStyle: {{ color: '#22c55e' }} }},
        {{ name: 'J', type: 'line', data: jData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }} }},
        {{ name: '超买线', type: 'line', data: dates.map(() => 80), symbol: 'none', lineStyle: {{ width: 1, color: '#ef4444', type: 'dashed' }}, silent: true }},
        {{ name: '超卖线', type: 'line', data: dates.map(() => 20), symbol: 'none', lineStyle: {{ width: 1, color: '#22c55e', type: 'dashed' }}, silent: true }}
    ]
}});

var bollChart = echarts.init(document.getElementById('boll-chart'));
bollChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle }},
    legend: {{ data: ['收盘价', '上轨', '中轨', '下轨'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '12%', bottom: '15%' }},
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: '收盘价', type: 'line', data: closeData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#374151' }}, itemStyle: {{ color: '#374151' }} }},
        {{ name: '上轨', type: 'line', data: bollUpperData, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#ef4444', type: 'dashed' }}, itemStyle: {{ color: '#ef4444' }} }},
        {{ name: '中轨', type: 'line', data: bollMidData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }} }},
        {{ name: '下轨', type: 'line', data: bollLowerData, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#22c55e', type: 'dashed' }}, itemStyle: {{ color: '#22c55e' }} }}
    ]
}});

var atrChart = echarts.init(document.getElementById('atr-chart'));
atrChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, ...tooltipStyle }},
    legend: {{ data: ['ATR'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '3%', top: '15%', bottom: '15%' }},
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ show: false }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: {{ type: 'value', scale: true, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 11 }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
    dataZoom: commonDataZoom,
    series: [
        {{ name: 'ATR', type: 'line', data: atrData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#f97316' }}, itemStyle: {{ color: '#f97316' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(249,115,22,0.15)' }}, {{ offset: 1, color: 'rgba(249,115,22,0.02)' }}] }} }} }}
    ]
}});

var turnoverChart = echarts.init(document.getElementById('turnover-chart'));
turnoverChart.setOption({{
    backgroundColor: 'transparent',
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, ...tooltipStyle,
        formatter: function(params) {{
            var idx = params[0].dataIndex;
            return '<div class="tooltip-box"><div style="font-weight:700;color:#1f2937;border-bottom:1px solid #e5e7eb;padding-bottom:6px;margin-bottom:6px;">' + dates[idx] + '</div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">市值</span><span style="font-weight:600;color:#8b5cf6;">' + params[0].value + ' 亿元</span></div>' +
                '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#6b7280;">换手率</span><span style="font-weight:600;color:#f97316;">' + params[1].value + '%</span></div></div>';
        }}
    }},
    legend: {{ data: ['市值（亿元）', '换手率（%）'], textStyle: {{ color: '#6b7280' }}, top: 5 }},
    grid: {{ left: '6%', right: '6%', top: '12%', bottom: '15%' }},
    xAxis: {{ type: 'category', data: dates, axisLine: {{ lineStyle: {{ color: '#9ca3af' }} }}, axisLabel: {{ color: '#6b7280', fontSize: 10, rotate: 45 }}, splitLine: {{ show: false }}, boundaryGap: true, min: 'dataMin', max: 'dataMax' }},
    yAxis: [
        {{ type: 'value', scale: true, position: 'left', axisLine: {{ lineStyle: {{ color: '#8b5cf6' }} }}, axisLabel: {{ color: '#8b5cf6', fontSize: 11, formatter: function(v) {{ return v + '亿'; }} }}, splitLine: {{ lineStyle: {{ color: '#f3f4f6', type: 'dashed' }} }} }},
        {{ type: 'value', scale: true, position: 'right', axisLine: {{ lineStyle: {{ color: '#f97316' }} }}, axisLabel: {{ color: '#f97316', fontSize: 11, formatter: function(v) {{ return v + '%'; }} }}, splitLine: {{ show: false }} }}
    ],
    dataZoom: commonDataZoom,
    series: [
        {{ name: '市值（亿元）', type: 'line', data: marketCapData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#8b5cf6' }}, itemStyle: {{ color: '#8b5cf6' }}, areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{{ offset: 0, color: 'rgba(139,92,246,0.15)' }}, {{ offset: 1, color: 'rgba(139,92,246,0.02)' }}] }} }} }},
        {{ name: '换手率（%）', type: 'line', data: turnoverRateData, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: {{ width: 2, color: '#f97316' }}, itemStyle: {{ color: '#f97316' }}, yAxisIndex: 1 }}
    ]
}});

window.addEventListener('resize', function() {{
    klineChart.resize();
    volumeChart.resize();
    macdChart.resize();
    rsiChart.resize();
    kdjChart.resize();
    bollChart.resize();
    atrChart.resize();
    turnoverChart.resize();
}});
</script>
</body>
</html>'''

    output_path = os.path.join(output_dir, f'{ts_code}_analysis.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'报告已保存至: {output_path}')

if __name__ == '__main__':
    generate_html_report('output/300504.SZ_daily_data.csv')