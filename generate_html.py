import pandas as pd
import json
import os
from datetime import datetime

def generate_html_report(csv_path, output_dir='output'):
    """生成交互式HTML分析报告"""
    df = pd.read_csv(csv_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    ts_code = df['ts_code'].iloc[0]
    stock_name = '内蒙一机'
    
    # 准备ECharts数据
    dates = [d.strftime('%Y-%m-%d') for d in df['trade_date']]
    # K线数据: [open, close, low, high]
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
            'itemStyle': {
                'color': '#ef5350' if is_up else '#26a69a'
            }
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
    
    # 统计数据
    start_date_str = df['trade_date'].min().strftime('%Y年%m月%d日')
    end_date_str = df['trade_date'].max().strftime('%Y年%m月%d日')
    trading_days = len(df)
    highest_price = round(df['high'].max(), 2)
    lowest_price = round(df['low'].min(), 2)
    start_price = round(df['close'].iloc[0], 2)
    end_price = round(df['close'].iloc[-1], 2)
    change_pct = round((end_price - start_price) / start_price * 100, 2)
    avg_volume = round(df['vol'].mean(), 0)
    up_days = len(df[df['close'] > df['open']])
    down_days = len(df[df['close'] < df['open']])
    flat_days = len(df[df['close'] == df['open']])
    up_ratio = round(up_days / trading_days * 100, 1)
    
    # JSON数据
    dates_json = json.dumps(dates, ensure_ascii=False)
    kline_json = json.dumps(kline_data, ensure_ascii=False)
    volumes_json = json.dumps(volumes, ensure_ascii=False)
    close_json = json.dumps(close_prices, ensure_ascii=False)
    ma5_json = json.dumps(ma5)
    ma10_json = json.dumps(ma10)
    ma20_json = json.dumps(ma20)
    ma60_json = json.dumps(ma60)
    
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
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        /* Header */
        .header {{
            background: linear-gradient(135deg, #161b22 0%, #1a2332 100%);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 32px 40px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #f0f6fc;
            margin-bottom: 8px;
        }}
        .header .subtitle {{
            font-size: 14px;
            color: #8b949e;
        }}
        .header .subtitle span {{
            margin-right: 20px;
        }}
        /* Stats Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
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
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        .stat-card .value {{
            font-size: 24px;
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
        /* Chart Container */
        .chart-section {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .chart-section h2 {{
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #21262d;
        }}
        #kline-chart {{
            width: 100%;
            height: 600px;
        }}
        #volume-chart {{
            width: 100%;
            height: 220px;
        }}
        /* Table Section */
        .table-section {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .table-section h2 {{
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #21262d;
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
            padding: 12px 8px;
            border-bottom: 2px solid #30363d;
        }}
        td {{
            text-align: center;
            padding: 10px 8px;
            border-bottom: 1px solid #21262d;
        }}
        tr:hover td {{
            background: #1a2332;
        }}
        .text-red {{ color: #ef5350; }}
        .text-green {{ color: #26a69a; }}
        /* Footer */
        .footer {{
            text-align: center;
            padding: 24px;
            color: #484f58;
            font-size: 13px;
        }}
        .footer a {{
            color: #58a6ff;
            text-decoration: none;
        }}
        /* Tooltip custom */
        .custom-tooltip {{
            padding: 12px 16px;
            background: rgba(22, 27, 34, 0.96);
            border: 1px solid #30363d;
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.8;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}
        .custom-tooltip .tt-date {{
            font-weight: 700;
            color: #f0f6fc;
            font-size: 14px;
            margin-bottom: 6px;
            padding-bottom: 6px;
            border-bottom: 1px solid #30363d;
        }}
        .custom-tooltip .tt-row {{
            display: flex;
            justify-content: space-between;
            gap: 24px;
        }}
        .custom-tooltip .tt-label {{
            color: #8b949e;
        }}
        .custom-tooltip .tt-val {{
            font-weight: 600;
            color: #f0f6fc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{stock_name}（{ts_code}）近一年交易数据全景报告</h1>
            <div class="subtitle">
                <span>数据区间：{start_date_str} — {end_date_str}</span>
                <span>交易日：{trading_days}天</span>
                <span>报告生成：{datetime.now().strftime("%Y年%m月%d日")}</span>
            </div>
        </div>

        <!-- Stats Grid -->
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
                <div class="label">日均成交量</div>
                <div class="value">{int(avg_volume):,}</div>
                <div class="unit">手</div>
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
        </div>

        <!-- K线图 -->
        <div class="chart-section">
            <h2>日线 K 线走势图</h2>
            <div id="kline-chart"></div>
        </div>

        <!-- 成交量图 -->
        <div class="chart-section">
            <h2>日成交量分布</h2>
            <div id="volume-chart"></div>
        </div>

        <!-- 数据表 -->
        <div class="table-section">
            <h2>交易数据明细（最近20个交易日）</h2>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>开盘价</th>
                        <th>收盘价</th>
                        <th>最高价</th>
                        <th>最低价</th>
                        <th>涨跌幅</th>
                        <th>成交量(手)</th>
                        <th>成交额(千元)</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # 最近20个交易日的数据表
    for _, row in df.tail(20).iterrows():
        pct = row['pct_chg']
        pct_class = 'text-red' if pct >= 0 else 'text-green'
        html_content += f'''                    <tr>
                        <td>{row['trade_date'].strftime('%Y-%m-%d')}</td>
                        <td>{row['open']:.2f}</td>
                        <td class="{pct_class}">{row['close']:.2f}</td>
                        <td>{row['high']:.2f}</td>
                        <td>{row['low']:.2f}</td>
                        <td class="{pct_class}">{pct:+.2f}%</td>
                        <td>{int(row['vol']):,}</td>
                        <td>{row['amount']:,.1f}</td>
                    </tr>
'''
    
    html_content += f'''                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div class="footer">
            数据来源：Tushare Pro API ｜ 生成工具：Python + ECharts ｜ 前复权数据<br>
            © 2026 {stock_name} 交易数据分析报告
        </div>
    </div>

    <script>
        // K线图
        var klineChart = echarts.init(document.getElementById('kline-chart'), 'dark');
        var dates = {dates_json};
        var klineData = {kline_json};
        var closeData = {close_json};
        var ma5Data = {ma5_json};
        var ma10Data = {ma10_json};
        var ma20Data = {ma20_json};
        var ma60Data = {ma60_json};

        klineChart.setOption({{
            backgroundColor: 'transparent',
            animation: true,
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{
                    type: 'cross',
                    crossStyle: {{ color: '#484f58' }},
                    lineStyle: {{ color: '#484f58', type: 'dashed' }}
                }},
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
                    return '<div class="custom-tooltip">' +
                        '<div class="tt-date">' + date + '</div>' +
                        '<div class="tt-row"><span class="tt-label">开盘</span><span class="tt-val">' + d[0] + '</span></div>' +
                        '<div class="tt-row"><span class="tt-label">收盘</span><span class="tt-val" style="color:' + color + '">' + d[1] + '</span></div>' +
                        '<div class="tt-row"><span class="tt-label">最高</span><span class="tt-val">' + d[3] + '</span></div>' +
                        '<div class="tt-row"><span class="tt-label">最低</span><span class="tt-val">' + d[2] + '</span></div>' +
                        '<div class="tt-row"><span class="tt-label">涨跌幅</span><span class="tt-val" style="color:' + color + '">' + sign + pctChg + '%</span></div>' +
                        '</div>';
                }}
            }},
            grid: {{
                left: '8%',
                right: '3%',
                top: '8%',
                bottom: '12%'
            }},
            xAxis: {{
                type: 'category',
                data: dates,
                axisLine: {{ lineStyle: {{ color: '#30363d' }} }},
                axisLabel: {{ color: '#8b949e', fontSize: 11, rotate: 0 }},
                splitLine: {{ show: false }},
                boundaryGap: true,
                min: 'dataMin',
                max: 'dataMax'
            }},
            yAxis: {{
                type: 'value',
                scale: true,
                axisLine: {{ lineStyle: {{ color: '#30363d' }} }},
                axisLabel: {{ color: '#8b949e', fontSize: 11, formatter: '{{value}}' }},
                splitLine: {{ lineStyle: {{ color: '#21262d', type: 'dashed' }} }}
            }},
            dataZoom: [
                {{
                    type: 'inside',
                    start: 0,
                    end: 100
                }},
                {{
                    type: 'slider',
                    height: 20,
                    bottom: 10,
                    borderColor: '#30363d',
                    backgroundColor: '#161b22',
                    fillerColor: 'rgba(88,166,255,0.15)',
                    handleStyle: {{ color: '#58a6ff', borderColor: '#58a6ff' }},
                    textStyle: {{ color: '#8b949e' }},
                    dataBackground: {{
                        lineStyle: {{ color: '#30363d' }},
                        areaStyle: {{ color: '#21262d' }}
                    }}
                }}
            ],
            series: [
                {{
                    name: 'K线',
                    type: 'candlestick',
                    data: klineData,
                    itemStyle: {{
                        color: '#ef5350',
                        color0: '#26a69a',
                        borderColor: '#ef5350',
                        borderColor0: '#26a69a'
                    }},
                    emphasis: {{
                        itemStyle: {{
                            color: '#ff6b6b',
                            color0: '#4db6ac',
                            borderColor: '#ff6b6b',
                            borderColor0: '#4db6ac'
                        }}
                    }}
                }},
                {{
                    name: 'MA5',
                    type: 'line',
                    data: ma5Data,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{ width: 1, color: '#f9c74f' }}
                }},
                {{
                    name: 'MA10',
                    type: 'line',
                    data: ma10Data,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{ width: 1, color: '#f8961e' }}
                }},
                {{
                    name: 'MA20',
                    type: 'line',
                    data: ma20Data,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{ width: 1, color: '#90be6d' }}
                }},
                {{
                    name: 'MA60',
                    type: 'line',
                    data: ma60Data,
                    smooth: true,
                    symbol: 'none',
                    lineStyle: {{ width: 1, color: '#577590' }}
                }}
            ]
        }});

        // 成交量图
        var volumeChart = echarts.init(document.getElementById('volume-chart'), 'dark');
        var volumeData = {volumes_json};

        volumeChart.setOption({{
            backgroundColor: 'transparent',
            animation: true,
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
                    return '<div class="custom-tooltip">' +
                        '<div class="tt-date">' + dates[idx] + '</div>' +
                        '<div class="tt-row"><span class="tt-label">成交量</span><span class="tt-val">' + (params[0].value / 10000).toFixed(1) + '万手</span></div>' +
                        '<div class="tt-row"><span class="tt-label">收盘价</span><span class="tt-val" style="color:' + color + '">' + d[1] + '</span></div>' +
                        '</div>';
                }}
            }},
            grid: {{
                left: '8%',
                right: '3%',
                top: '8%',
                bottom: '20%'
            }},
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
                axisLabel: {{
                    color: '#8b949e', fontSize: 11,
                    formatter: function(v) {{ return (v / 10000).toFixed(0) + '万'; }}
                }},
                splitLine: {{ lineStyle: {{ color: '#21262d', type: 'dashed' }} }}
            }},
            dataZoom: [
                {{
                    type: 'inside',
                    start: 0,
                    end: 100
                }},
                {{
                    type: 'slider',
                    height: 20,
                    bottom: 5,
                    borderColor: '#30363d',
                    backgroundColor: '#161b22',
                    fillerColor: 'rgba(88,166,255,0.15)',
                    handleStyle: {{ color: '#58a6ff', borderColor: '#58a6ff' }},
                    textStyle: {{ color: '#8b949e' }}
                }}
            ],
            series: [
                {{
                    name: '成交量',
                    type: 'bar',
                    data: volumeData,
                    itemStyle: {{
                        borderRadius: [2, 2, 0, 0]
                    }}
                }}
            ]
        }});

        // 联动
        echarts.connect([klineChart, volumeChart]);

        // 自适应
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
    
    print(f"HTML报告已生成: {output_path}")
    return output_path

if __name__ == '__main__':
    csv_path = os.path.join('output', '600967.SH_daily_data.csv')
    generate_html_report(csv_path)
