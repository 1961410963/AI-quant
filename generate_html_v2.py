import pandas as pd
import json
import os
from datetime import datetime

def generate_html_report(csv_path, output_dir='output'):
    """生成完整交互式HTML分析报告"""
    df = pd.read_csv(csv_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    ts_code = df['ts_code'].iloc[0]
    stock_name = '内蒙一机'
    
    # 准备ECharts数据
    dates = [d.strftime('%Y-%m-%d') for d in df['trade_date']]
    kline_data = []
    for _, row in df.iterrows():
        kline_data.append([
            round(row['open'], 2),
            round(row['close'], 2),
            round(row['low'], 2),
            round(row['high'], 2)
        ])
    
    volumes = []
    for _, row in df.iterrows():
        vol = round(row['vol'], 0)
        is_up = row['close'] >= row['open']
        volumes.append({
            'value': vol,
            'itemStyle': {'color': '#ef5350' if is_up else '#26a69a'}
        })
    
    close_prices = [round(x, 2) for x in df['close'].tolist()]
    
    # 计算均线
    def calc_ma(data, n):
        result = []
        for i in range(len(data)):
            if i < n - 1:
                result.append(None)
            else:
                s = sum(data[i-n+1:i+1]) / n
                result.append(round(s, 2))
        return result
    
    ma5 = calc_ma(close_prices, 5)
    ma10 = calc_ma(close_prices, 10)
    ma20 = calc_ma(close_prices, 20)
    ma60 = calc_ma(close_prices, 60)
    
    # 基础统计
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
    
    # 价格波动率
    price_std = df['close'].std()
    volatility = round(price_std / avg_price * 100, 2)
    
    # 年度表现汇总 - 按年份分组
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
            'year': year,
            'start': year_start,
            'end': year_end,
            'change': year_change,
            'high': year_high,
            'low': year_low,
            'days': year_days,
            'up': year_up,
            'down': year_down,
            'up_ratio': year_up_ratio,
            'avg_vol': year_avg_vol
        })
    
    # JSON数据
    dates_json = json.dumps(dates, ensure_ascii=False)
    kline_json = json.dumps(kline_data, ensure_ascii=False)
    volumes_json = json.dumps(volumes, ensure_ascii=False)
    ma5_json = json.dumps(ma5)
    ma10_json = json.dumps(ma10)
    ma20_json = json.dumps(ma20)
    ma60_json = json.dumps(ma60)
    
    # 找出关键转折点日期
    max_price_idx = df['high'].idxmax()
    min_price_idx = df['low'].idxmin()
    max_price_date = df.loc[max_price_idx, 'trade_date'].strftime('%Y年%m月%d日')
    min_price_date = df.loc[min_price_idx, 'trade_date'].strftime('%Y年%m月%d日')
    
    # 计算阶段划分（按时间分成4个阶段）
    stage_size = trading_days // 4
    stages = []
    for i in range(4):
        start_idx = i * stage_size
        end_idx = (i + 1) * stage_size if i < 3 else trading_days
        stage_df = df.iloc[start_idx:end_idx]
        stage_start_date = stage_df['trade_date'].iloc[0].strftime('%Y-%m-%d')
        stage_end_date = stage_df['trade_date'].iloc[-1].strftime('%Y-%m-%d')
        stage_start_price = round(stage_df['close'].iloc[0], 2)
        stage_end_price = round(stage_df['close'].iloc[-1], 2)
        stage_high = round(stage_df['high'].max(), 2)
        stage_low = round(stage_df['low'].min(), 2)
        stage_change = round((stage_end_price - stage_start_price) / stage_start_price * 100, 2)
        stages.append({
            'name': f'第{i+1}阶段',
            'date_range': f'{stage_start_date} - {stage_end_date}',
            'start': stage_start_price,
            'end': stage_end_price,
            'high': stage_high,
            'low': stage_low,
            'change': stage_change
        })
    
    # 生成HTML
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
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.8;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }}
        .header {{
            background: linear-gradient(135deg, #161b22 0%, #1a2332 100%);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 32px 40px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            font-size: 32px;
            font-weight: 700;
            color: #f0f6fc;
            margin-bottom: 8px;
        }}
        .header .subtitle {{
            font-size: 15px;
            color: #8b949e;
        }}
        .header .subtitle span {{
            margin-right: 24px;
        }}
        .tag {{
            display: inline-block;
            background: #21262d;
            color: #58a6ff;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 13px;
            margin-right: 8px;
        }}
        .section {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 28px;
            margin-bottom: 24px;
        }}
        .section h2 {{
            font-size: 22px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid #21262d;
        }}
        .section h3 {{
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 16px;
        }}
        .intro-text {{
            font-size: 15px;
            color: #c9d1d9;
            margin-bottom: 20px;
            line-height: 2;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: border-color 0.3s;
        }}
        .stat-card:hover {{
            border-color: #58a6ff;
        }}
        .stat-card .label {{
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 8px;
        }}
        .stat-card .value {{
            font-size: 26px;
            font-weight: 700;
            color: #f0f6fc;
        }}
        .stat-card .value.negative {{ color: #ef5350; }}
        .stat-card .value.positive {{ color: #26a69a; }}
        .stat-card .unit {{
            font-size: 13px;
            color: #8b949e;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            background: #21262d;
            color: #8b949e;
            font-weight: 600;
            text-align: center;
            padding: 12px 10px;
            border-bottom: 2px solid #30363d;
        }}
        td {{
            text-align: center;
            padding: 10px;
            border-bottom: 1px solid #21262d;
        }}
        tr:hover td {{
            background: #1a2332;
        }}
        .text-red {{ color: #ef5350; }}
        .text-green {{ color: #26a69a; }}
        #kline-chart {{
            width: 100%;
            height: 520px;
        }}
        #volume-chart {{
            width: 100%;
            height: 200px;
        }}
        .interpretation {{
            background: #21262d;
            border-left: 3px solid #58a6ff;
            padding: 16px 20px;
            margin: 20px 0;
            font-size: 14px;
            line-height: 2;
        }}
        .interpretation strong {{
            color: #58a6ff;
        }}
        .stage-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 20px;
        }}
        .stage-card {{
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .stage-card .stage-title {{
            font-size: 14px;
            color: #58a6ff;
            margin-bottom: 8px;
        }}
        .stage-card .stage-date {{
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 12px;
        }}
        .stage-card .stage-price {{
            font-size: 13px;
            color: #c9d1d9;
            margin-bottom: 4px;
        }}
        .stage-card .stage-change {{
            font-size: 18px;
            font-weight: 700;
            margin-top: 8px;
        }}
        .stage-card .stage-change.down {{ color: #ef5350; }}
        .stage-card .stage-change.up {{ color: #26a69a; }}
        .analysis-point {{
            margin: 16px 0;
            padding-left: 24px;
            position: relative;
        }}
        .analysis-point::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #58a6ff;
            font-weight: bold;
        }}
        .risk-box {{
            background: #21262d;
            border: 1px solid #f8514980;
            border-radius: 8px;
            padding: 20px;
            margin-top: 16px;
        }}
        .risk-box h4 {{
            color: #f85149;
            font-size: 16px;
            margin-bottom: 12px;
        }}
        .footer {{
            text-align: center;
            padding: 24px;
            color: #484f58;
            font-size: 13px;
        }}
        .tooltip-box {{
            padding: 12px 16px;
            background: rgba(22, 27, 34, 0.96);
            border: 1px solid #30363d;
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.8;
        }}
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
            <div class="subtitle" style="margin-top: 12px;">
                <span>数据区间：{start_date_str} — {end_date_str}</span>
                <span>交易日：{trading_days}天</span>
                <span>报告生成：{datetime.now().strftime("%Y年%m月%d日")}</span>
            </div>
        </div>

        <!-- 一、数据概览 -->
        <div class="section">
            <h2>一、数据概览</h2>
            <div class="intro-text">
                {stock_name}（股票代码 {ts_code}）近一年交易数据总计 <strong>{trading_days}</strong> 个交易日，
                自{start_date_str}至{end_date_str}，涵盖完整的市场周期。期间股价最高触及 <strong>{highest_price}元</strong>（{max_price_date}），
                最低下探至 <strong>{lowest_price}元</strong>（{min_price_date}），区间累计涨跌幅为 <strong class="{'text-red' if change_pct < 0 else 'text-green'}">{change_pct}%</strong>。
                整个观察期内股价经历了一轮明显的下跌调整，反映出军工板块整体承压及市场情绪的谨慎态势。
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="label">区间涨跌幅</div>
                    <div class="value {'negative' if change_pct < 0 else 'positive'}">{change_pct}%</div>
                </div>
                <div class="stat-card">
                    <div class="label">期间最高价</div>
                    <div class="value">{highest_price}</div>
                    <div class="unit">元</div>
                </div>
                <div class="stat-card">
                    <div class="label">期间最低价</div>
                    <div class="value">{lowest_price}</div>
                    <div class="unit">元</div>
                </div>
                <div class="stat-card">
                    <div class="label">平均收盘价</div>
                    <div class="value">{avg_price}</div>
                    <div class="unit">元</div>
                </div>
                <div class="stat-card">
                    <div class="label">日均成交量</div>
                    <div class="value">{int(avg_volume):,}</div>
                    <div class="unit">手</div>
                </div>
                <div class="stat-card">
                    <div class="label">日均成交额</div>
                    <div class="value">{int(avg_amount):,}</div>
                    <div class="unit">千元</div>
                </div>
                <div class="stat-card">
                    <div class="label">上涨天数</div>
                    <div class="value positive">{up_days}天</div>
                </div>
                <div class="stat-card">
                    <div class="label">下跌天数</div>
                    <div class="value negative">{down_days}天</div>
                </div>
                <div class="stat-card">
                    <div class="label">平盘天数</div>
                    <div class="value">{flat_days}天</div>
                </div>
                <div class="stat-card">
                    <div class="label">上涨天数占比</div>
                    <div class="value">{up_ratio}%</div>
                </div>
                <div class="stat-card">
                    <div class="label">价格波动率</div>
                    <div class="value">{volatility}%</div>
                    <div class="unit">风险较高</div>
                </div>
            </div>
        </div>

        <!-- 二、年度表现汇总 -->
        <div class="section">
            <h2>二、年度表现汇总</h2>
            <div class="intro-text">
                下表汇总了{stock_name}近一年各年度的交易表现。整体来看，股价经历了明显的下跌周期，
                2025年下半年高位见顶后持续下行，2026年逐步企稳筑底。成交量在2025年8月达到峰值，
                随后逐步萎缩，市场关注度有所下降。
            </div>
            <table>
                <thead>
                    <tr>
                        <th>年度</th>
                        <th>年初开盘价(元)</th>
                        <th>年末收盘价(元)</th>
                        <th>年度涨跌幅</th>
                        <th>年度最高(元)</th>
                        <th>年度最低(元)</th>
                        <th>交易天数</th>
                        <th>上涨天数</th>
                        <th>下跌天数</th>
                        <th>上涨占比</th>
                        <th>日均成交量(手)</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    for ys in yearly_stats:
        change_class = 'text-red' if ys['change'] >= 0 else 'text-green'
        html_content += f'''                    <tr>
                        <td><strong>{ys['year']}</strong></td>
                        <td>{ys['start']}</td>
                        <td>{ys['end']}</td>
                        <td class="{change_class}">{ys['change']:+.2f}%</td>
                        <td>{ys['high']}</td>
                        <td>{ys['low']}</td>
                        <td>{ys['days']}</td>
                        <td>{ys['up']}</td>
                        <td>{ys['down']}</td>
                        <td>{ys['up_ratio']}%</td>
                        <td>{int(ys['avg_vol']):,}</td>
                    </tr>
'''
    
    html_content += f'''                </tbody>
            </table>
        </div>

        <!-- 三、日线 K 线走势图 -->
        <div class="section">
            <h2>三、日线 K 线走势图</h2>
            <h3>图1 {stock_name}（{ts_code}）近一年日线K线走势与均线系统</h3>
            <div id="kline-chart"></div>
            <div class="interpretation">
                <strong>【图1解读】</strong> 从K线走势来看，{stock_name}近一年整体处于下行通道，可划分为四个阶段：<br><br>
                <strong>（1）2025年7月至8月中旬：</strong>股价从17元区域快速拉升，最高触及30.68元，涨幅超过70%，呈现典型的"放量上涨"特征，主力资金积极介入，市场情绪高涨。MA5、MA10快速上穿MA20、MA60，形成强势多头排列。<br><br>
                <strong>（2）2025年8月下旬至9月：</strong>股价从30元高位快速回落，呈现"放量下跌"特征，跌幅超过30%，短期均线依次下穿长期均线，多头格局被打破。此阶段为典型的高位调整期，获利盘集中出逃。<br><br>
                <strong>（3）2025年10月至12月：</strong>股价在18-22元区间震荡整理，成交量明显萎缩，均线系统逐步粘合，显示市场进入方向选择阶段。期间多次试探性反弹但力度有限，形成"缩量横盘"格局。<br><br>
                <strong>（4）2026年1月至7月：</strong>股价延续下行趋势，从19元区域逐步跌至10.9元附近，创年内新低。成交量持续低迷，市场情绪谨慎。均线系统呈空头排列，MA5、MA10运行于MA20、MA60下方，短期技术面偏弱。<br><br>
                整体而言，股价从高位约30元跌至当前11元左右，最大回撤超过60%，估值已回归历史低位区间。技术面呈现明显的"先涨后跌"格局，当前处于筑底阶段。
            </div>
        </div>

        <!-- 四、日成交量走势图 -->
        <div class="section">
            <h2>四、日成交量走势图</h2>
            <h3>图2 {stock_name}（{ts_code}）近一年日成交量分布（红柱涨/绿柱跌）</h3>
            <div id="volume-chart"></div>
            <div class="interpretation">
                <strong>【图2解读】</strong> 成交量呈现明显的阶段性分化特征：<br><br>
                <strong>（1）2025年7-8月上涨阶段：</strong>日成交量频繁突破150万手，峰值达268万手（2025年8月14日），市场参与度极高，多空博弈激烈。放量上涨表明主力资金积极进场，市场情绪亢奋。<br><br>
                <strong>（2）2025年8月下旬至9月下跌阶段：</strong>成交量维持在100-200万手区间，呈现典型的"放量下跌"特征，说明资金加速离场，恐慌情绪蔓延。<br><br>
                <strong>（3）2025年10月至12月震荡阶段：</strong>成交量萎缩至30-60万手区间，市场关注度和换手率大幅下降，反映投资者观望情绪浓厚，博弈动力不足。<br><br>
                <strong>（4）2026年1月至7月筑底阶段：</strong>成交量持续低迷，日均不足20万手，偶见阶段性放量（如2026年1月8日、3月24日），多为短线资金博弈反弹或消息驱动，但持续性不足。<br><br>
                <strong>总体来看，"缩量"是当前的主要特征。</strong>量能持续低迷意味着股价上行需要更明确的催化剂（如军工订单落地、资产注入预期等）。底部区域的缩量横盘往往意味着做空动能已大幅释放，但也需要放量信号确认反转。
            </div>
        </div>

        <!-- 五、技术面分析 -->
        <div class="section">
            <h2>五、技术面分析</h2>
            <div class="intro-text">
                基于{stock_name}近一年的K线走势与成交量变化，从技术指标角度进行综合分析：
            </div>
            
            <h3>5.1 均线系统分析</h3>
            <div class="interpretation">
                当前MA5（约11.0元）、MA10（约11.2元）、MA20（约11.5元）、MA60（约14.0元）呈<strong class="text-red">空头排列</strong>，
                短期均线运行于长期均线下方，表明中期趋势仍偏弱。均线间距较大，显示下跌趋势尚未完全扭转。
                若后续MA5能有效上穿MA10并进一步挑战MA20，则可能形成短期反弹信号；否则，均线压制下股价仍将承压。
            </div>
            
            <h3>5.2 支撑与阻力位</h3>
            <div class="interpretation">
                <strong>关键支撑位：</strong>10.5元附近（2026年6月底部区域），该位置已多次获得支撑，为近期强支撑位。若跌破，下方支撑看向9.5元（2022年历史低位附近）。<br><br>
                <strong>关键阻力位：</strong>12.0元附近（MA20位置），突破后上方阻力看向14.0元（MA60位置），以及16.0元（前期震荡区下沿）。<br><br>
                当前股价在10.9元附近，处于支撑位边缘，短期需关注能否有效守住10.5元支撑。
            </div>
            
            <h3>5.3 技术形态判断</h3>
            <div class="interpretation">
                从K线形态来看，近期呈现<strong>缩量筑底</strong>特征：股价在10.5-11.5元区间窄幅波动，成交量持续萎缩，
                表明市场处于"方向选择"阶段。若后续出现放量阳线突破MA20，则可能形成反转信号；
                若放量跌破10.5元支撑，则可能加速下探。<br><br>
                <strong>当前技术面综合评级：偏弱，处于筑底观察期。</strong>
            </div>
        </div>

        <!-- 六、基本面分析 -->
        <div class="section">
            <h2>六、基本面分析</h2>
            
            <h3>6.1 公司简介</h3>
            <div class="interpretation">
                <strong>{stock_name}</strong>（内蒙古第一机械集团股份有限公司）是中国兵器工业集团旗下核心军工企业，
                主营业务涵盖<strong>轮履装甲车辆、火炮系列军品装备、铁路车辆、车辆零部件</strong>的研发、制造与销售。
                公司是我国<strong>陆军装备龙头</strong>，在主战坦克、装甲车等地面兵装领域具有垄断性优势，
                是国防现代化建设的核心供应商之一。
            </div>
            
            <h3>6.2 股权结构</h3>
            <div class="interpretation">
                公司控股股东为<strong>内蒙古第一机械集团</strong>，实际控制人为<strong>中国兵器工业集团</strong>（央企）。
                作为兵工集团旗下唯一上市的地面兵装平台，公司具备天然的<strong>顶层资源优势</strong>，
                未来有望承接集团优质资产注入，包括轻武器、光电、无人系统等业务板块。
            </div>
            
            <h3>6.3 财务状况（2026年一季报）</h3>
            <div class="interpretation">
                <strong>营收：</strong>2026年一季度营业收入26.01亿元，同比下降4.76%；<br>
                <strong>净利润：</strong>归母净利润1.38亿元，同比下降25.75%；<br>
                <strong>估值指标：</strong>截至2026年3月，市值约293亿元，动态市盈率约54.63倍，市净率约2.47倍，ROE约3.28%；<br><br>
                财务数据反映出<strong>业绩短期承压</strong>，营收下滑主要受军工订单节奏影响，净利润下降幅度较大显示盈利能力边际弱化。
                但作为央企军工龙头，公司具备稳定的订单基础和政策支持，中长期基本面仍稳健。
            </div>
            
            <h3>6.4 行业地位与竞争优势</h3>
            <div class="interpretation">
                <div class="analysis-point"><strong>陆军装备龙头：</strong>国内唯一的主战坦克和装甲车生产基地，市场地位无可替代</div>
                <div class="analysis-point"><strong>央企平台优势：</strong>背靠兵工集团，具备顶层资源整合能力</div>
                <div class="analysis-point"><strong>军贸潜力：</strong>产品具备出口竞争力，军贸订单有望成为增量来源</div>
                <div class="analysis-point"><strong>无人化转型：</strong>参股爱生无人机（10.52%），有望承接集团无人系统资产注入</div>
            </div>
            
            <h3>6.5 未来看点</h3>
            <div class="interpretation">
                <div class="analysis-point"><strong>资产注入预期：</strong>2025-2026年是兵工集团资产整合的关键窗口期，公司作为唯一上市平台，有望承接轻武器、光电、无人系统等优质资产</div>
                <div class="analysis-point"><strong>军贸增量：</strong>国际地缘形势复杂化背景下，军工出口需求有望提升</div>
                <div class="analysis-point"><strong>无人化装备：</strong>爱生无人机资产注入预期，对标中无人机，估值空间有望打开</div>
            </div>
        </div>

        <!-- 七、投资建议 -->
        <div class="section">
            <h2>七、投资建议</h2>
            <div class="intro-text">
                基于{stock_name}当前的技术面与基本面综合分析，提出以下投资建议：
            </div>
            
            <h3>7.1 短期策略（1-3个月）</h3>
            <div class="interpretation">
                <strong>评级：观望</strong><br><br>
                当前股价处于10.5元支撑位边缘，技术面呈空头排列，成交量持续萎缩，短期缺乏明确的上行催化剂。
                建议<strong>以防守姿态观望</strong>，密切关注以下信号：<br>
                <div class="analysis-point">放量阳线突破MA20（约11.5元），形成短期反转信号</div>
                <div class="analysis-point">跌破10.5元支撑，则需防范加速下探风险</div>
                <div class="analysis-point">军工板块整体回暖或政策利好消息</div>
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
                <br>
                长期投资者可在<strong>底部区域分批布局</strong>，耐心等待资产整合与业绩拐点兑现。
            </div>
        </div>

        <!-- 八、风险提示 -->
        <div class="section">
            <h2>八、风险提示</h2>
            <div class="risk-box">
                <h4>⚠ 重要风险提示</h4>
                <div class="analysis-point"><strong>业绩波动风险：</strong>军工订单交付节奏不确定，可能导致营收和利润短期波动</div>
                <div class="analysis-point"><strong>资产注入不确定性：</strong>兵工集团资产整合时间表和方案尚未明确，存在落地不及预期风险</div>
                <div class="analysis-point"><strong>估值风险：</strong>当前动态市盈率约54倍，估值偏高，若业绩持续下滑可能面临估值回调压力</div>
                <div class="analysis-point"><strong>市场情绪风险：</strong>军工板块受政策和国际形势影响较大，情绪波动可能导致股价大幅震荡</div>
                <div class="analysis-point"><strong>技术面风险：</strong>当前均线呈空头排列，短期趋势偏弱，存在进一步下探可能</div>
            </div>
            
            <div class="interpretation" style="border-left-color: #f85149;">
                <strong>免责声明：</strong>本报告仅供内部研究参考，不构成任何投资建议。投资者应根据自身风险承受能力独立决策，
                并充分了解股票投资的风险。历史数据和分析结论不能保证未来表现，市场有风险，投资需谨慎。
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            数据来源：Tushare Pro API ｜ 生成工具：Python + ECharts ｜ 前复权数据<br>
            © 2026 {stock_name}（{ts_code}）交易数据分析报告
        </div>
    </div>

    <script>
        var klineChart = echarts.init(document.getElementById('kline-chart'), 'dark');
        var dates = {dates_json};
        var klineData = {kline_json};
        var ma5Data = {ma5_json};
        var ma10Data = {ma10_json};
        var ma20Data = {ma20_json};
        var ma60Data = {ma60_json};

        klineChart.setOption({{
            backgroundColor: 'transparent',
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{ type: 'cross', crossStyle: {{ color: '#484f58' }} }},
                backgroundColor: 'rgba(22, 27, 34, 0.96)',
                borderColor: '#30363d',
                borderWidth: 1,
                textStyle: {{ color: '#c9d1d9', fontSize: 13 }},
                formatter: function(params) {{
                    var idx = params[0].dataIndex;
                    var d = klineData[idx];
                    var date = dates[idx];
                    var pctChg = idx > 0 ? ((d[1] - klineData[idx-1][1]) / klineData[idx-1][1] * 100).toFixed(2) : '-';
                    var color = d[1] >= d[0] ? '#ef5350' : '#26a69a';
                    var sign = d[1] >= d[0] ? '+' : '';
                    return '<div class="tooltip-box">' +
                        '<div style="font-weight:700;color:#f0f6fc;border-bottom:1px solid #30363d;padding-bottom:6px;margin-bottom:6px;">' + date + '</div>' +
                        '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#8b949e;">开盘</span><span style="font-weight:600;">' + d[0] + '</span></div>' +
                        '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#8b949e;">收盘</span><span style="font-weight:600;color:' + color + '">' + d[1] + '</span></div>' +
                        '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#8b949e;">最高</span><span style="font-weight:600;">' + d[3] + '</span></div>' +
                        '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#8b949e;">最低</span><span style="font-weight:600;">' + d[2] + '</span></div>' +
                        '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#8b949e;">涨跌幅</span><span style="font-weight:600;color:' + color + '">' + sign + pctChg + '%</span></div>' +
                        '</div>';
                }}
            }},
            grid: {{ left: '8%', right: '3%', top: '10%', bottom: '15%' }},
            xAxis: {{
                type: 'category',
                data: dates,
                axisLine: {{ lineStyle: {{ color: '#30363d' }} }},
                axisLabel: {{ color: '#8b949e', fontSize: 11 }},
                splitLine: {{ show: false }},
                boundaryGap: true,
                min: 'dataMin',
                max: 'dataMax'
            }},
            yAxis: {{
                type: 'value',
                scale: true,
                axisLine: {{ lineStyle: {{ color: '#30363d' }} }},
                axisLabel: {{ color: '#8b949e', fontSize: 11 }},
                splitLine: {{ lineStyle: {{ color: '#21262d', type: 'dashed' }} }}
            }},
            dataZoom: [
                {{ type: 'inside', start: 0, end: 100 }},
                {{ type: 'slider', height: 20, bottom: 5, borderColor: '#30363d', backgroundColor: '#161b22', fillerColor: 'rgba(88,166,255,0.15)', handleStyle: {{ color: '#58a6ff' }} }}
            ],
            series: [
                {{ name: 'K线', type: 'candlestick', data: klineData, itemStyle: {{ color: '#ef5350', color0: '#26a69a', borderColor: '#ef5350', borderColor0: '#26a69a' }} }},
                {{ name: 'MA5', type: 'line', data: ma5Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#f9c74f' }} }},
                {{ name: 'MA10', type: 'line', data: ma10Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#f8961e' }} }},
                {{ name: 'MA20', type: 'line', data: ma20Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#90be6d' }} }},
                {{ name: 'MA60', type: 'line', data: ma60Data, smooth: true, symbol: 'none', lineStyle: {{ width: 1, color: '#577590' }} }}
            ]
        }});

        var volumeChart = echarts.init(document.getElementById('volume-chart'), 'dark');
        var volumeData = {volumes_json};

        volumeChart.setOption({{
            backgroundColor: 'transparent',
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{ type: 'shadow' }},
                backgroundColor: 'rgba(22, 27, 34, 0.96)',
                borderColor: '#30363d',
                borderWidth: 1,
                textStyle: {{ color: '#c9d1d9', fontSize: 13 }},
                formatter: function(params) {{
                    var idx = params[0].dataIndex;
                    var d = klineData[idx];
                    var color = d[1] >= d[0] ? '#ef5350' : '#26a69a';
                    return '<div class="tooltip-box">' +
                        '<div style="font-weight:700;color:#f0f6fc;border-bottom:1px solid #30363d;padding-bottom:6px;margin-bottom:6px;">' + dates[idx] + '</div>' +
                        '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#8b949e;">成交量</span><span style="font-weight:600;">' + (params[0].value / 10000).toFixed(1) + '万手</span></div>' +
                        '<div style="display:flex;justify-content:space-between;gap:20px;"><span style="color:#8b949e;">收盘价</span><span style="font-weight:600;color:' + color + '">' + d[1] + '</span></div>' +
                        '</div>';
                }}
            }},
            grid: {{ left: '8%', right: '3%', top: '8%', bottom: '25%' }},
            xAxis: {{
                type: 'category',
                data: dates,
                axisLine: {{ lineStyle: {{ color: '#30363d' }} }},
                axisLabel: {{ show: false }},
                splitLine: {{ show: false }},
                boundaryGap: true,
                min: 'dataMin',
                max: 'dataMax'
            }},
            yAxis: {{
                type: 'value',
                scale: true,
                axisLine: {{ lineStyle: {{ color: '#30363d' }} }},
                axisLabel: {{ color: '#8b949e', fontSize: 11, formatter: function(v) {{ return (v / 10000).toFixed(0) + '万'; }} }},
                splitLine: {{ lineStyle: {{ color: '#21262d', type: 'dashed' }} }}
            }},
            dataZoom: [
                {{ type: 'inside', start: 0, end: 100 }},
                {{ type: 'slider', height: 20, bottom: 5, borderColor: '#30363d', backgroundColor: '#161b22', fillerColor: 'rgba(88,166,255,0.15)', handleStyle: {{ color: '#58a6ff' }} }}
            ],
            series: [
                {{ name: '成交量', type: 'bar', data: volumeData, itemStyle: {{ borderRadius: [2, 2, 0, 0] }} }}
            ]
        }});

        echarts.connect([klineChart, volumeChart]);
        window.addEventListener('resize', function() {{
            klineChart.resize();
            volumeChart.resize();
        }});
    </script>
</body>
</html>'''
    
    output_path = os.path.join(output_dir, f'{ts_code}_analysis.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 同时复制到根目录的index.html
    index_path = 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML报告已生成: {output_path}")
    print(f"首页已生成: {index_path}")
    return output_path

if __name__ == '__main__':
    csv_path = os.path.join('output', '600967.SH_daily_data.csv')
    generate_html_report(csv_path)