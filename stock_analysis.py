import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def get_stock_data(ts_code, days=365):
    """
    获取股票过去一年的前复权交易数据
    
    参数:
        ts_code: 股票代码，如 '600967.SH'
        days: 过去多少天的数据，默认365天
        
    返回:
        DataFrame: 包含前复权交易数据
    """
    token = '2dfed09895f11acd0fc988685ccf1c1bd0898b14a9526bcffb4cefac'
    ts.set_token(token)
    pro = ts.pro_api()
    
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    df = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, 
                   adj='qfq', freq='D')
    
    if df is not None and not df.empty:
        df = df.sort_values('trade_date').reset_index(drop=True)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        
    return df

def plot_close_price(df, ts_code, output_dir='output'):
    """
    绘制每日收盘价曲线图
    
    参数:
        df: 股票交易数据
        ts_code: 股票代码
        output_dir: 输出目录
    """
    if df is None or df.empty:
        print("数据为空，无法绘图")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(16, 8))
    plt.plot(df['trade_date'], df['close'], label='收盘价', color='#E63946', linewidth=2)
    
    plt.title(f'{ts_code} 近一年每日收盘价走势', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('收盘价 (元)', fontsize=14)
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, f'{ts_code}_close_price.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"收盘价曲线图已保存至: {output_path}")
    return output_path

def save_to_csv(df, ts_code, output_dir='output'):
    """
    将数据保存为CSV格式
    
    参数:
        df: 股票交易数据
        ts_code: 股票代码
        output_dir: 输出目录
    """
    if df is None or df.empty:
        print("数据为空，无法保存")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f'{ts_code}_daily_data.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"数据已保存至: {output_path}")
    return output_path

def generate_report(df, ts_code, output_dir='output'):
    """
    生成分析报告
    
    参数:
        df: 股票交易数据
        ts_code: 股票代码
        output_dir: 输出目录
    """
    if df is None or df.empty:
        print("数据为空，无法生成报告")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    
    start_date = df['trade_date'].min().strftime('%Y年%m月%d日')
    end_date = df['trade_date'].max().strftime('%Y年%m月%d日')
    trading_days = len(df)
    
    highest_price = df['high'].max()
    lowest_price = df['low'].min()
    start_price = df['close'].iloc[0]
    end_price = df['close'].iloc[-1]
    change = end_price - start_price
    change_pct = (change / start_price) * 100
    
    avg_volume = df['vol'].mean()
    
    up_days = len(df[df['close'] > df['open']])
    down_days = len(df[df['close'] < df['open']])
    flat_days = len(df[df['close'] == df['open']])
    up_ratio = (up_days / trading_days) * 100
    
    report_content = f"""# {ts_code} 近一年交易数据分析报告

**数据区间**：{start_date} — {end_date} 
**交易日**：{trading_days}天 
**报告生成**：{datetime.now().strftime('%Y年%m月%d日')}

## 一、数据概览

| 指标 | 数值 |
|------|------|
| 区间涨跌幅 | {change_pct:.2f}% |
| 期间最高价 | {highest_price:.2f}元 |
| 期间最低价 | {lowest_price:.2f}元 |
| 期初收盘价 | {start_price:.2f}元 |
| 期末收盘价 | {end_price:.2f}元 |
| 日均成交量 | {avg_volume:.0f}手 |
| 上涨天数 | {up_days}天 |
| 下跌天数 | {down_days}天 |
| 平盘天数 | {flat_days}天 |
| 上涨天数占比 | {up_ratio:.1f}% |

## 二、每日收盘价走势图

![收盘价走势]({ts_code}_close_price.png)

## 三、数据分析

### 3.1 价格走势分析

近一年来，{ts_code}股价从{start_price:.2f}元{'' if change >= 0 else '下跌'}至{end_price:.2f}元，{'' if change >= 0 else '跌幅'}达{abs(change_pct):.2f}%。期间最高价{highest_price:.2f}元，最低价{lowest_price:.2f}元，振幅较大。

### 3.2 市场表现

上涨天数占比{up_ratio:.1f}%，显示市场{'' if up_ratio > 50 else '偏弱'}。日均成交量{avg_volume:.0f}手，交投{'' if avg_volume > 500000 else '相对清淡'}。

## 四、总结

{ts_code}近一年整体表现{'' if change >= 0 else '不佳'}，{'' if change >= 0 else '受市场环境和公司基本面影响，股价承压'}。投资者可结合更多指标进行综合分析。

---

**数据来源**：Tushare Pro API  
**分析工具**：Python + Pandas + Matplotlib
"""
    
    output_path = os.path.join(output_dir, f'{ts_code}_analysis_report.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"分析报告已保存至: {output_path}")
    return output_path

def load_from_csv(csv_path):
    """从CSV文件加载数据"""
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df
    return None

if __name__ == '__main__':
    ts_code = '600967.SH'
    stock_name = '内蒙一机'
    
    print(f"正在获取 {stock_name} ({ts_code}) 近一年交易数据...")
    
    df = None
    output_dir = 'output'
    csv_path = os.path.join(output_dir, f'{ts_code}_daily_data.csv')
    
    try:
        df = get_stock_data(ts_code, days=365)
        print(f"成功获取 {len(df)} 条交易数据")
    except Exception as e:
        print(f"Tushare API调用失败: {e}")
        print("尝试从本地CSV文件加载数据...")
        df = load_from_csv(csv_path)
        if df is not None:
            print(f"从本地CSV加载成功，共 {len(df)} 条数据")
    
    if df is not None and not df.empty:
        csv_path = save_to_csv(df, ts_code)
        plot_path = plot_close_price(df, ts_code)
        report_path = generate_report(df, ts_code)
        
        print("\n" + "="*50)
        print("任务完成！")
        print(f"CSV数据: {csv_path}")
        print(f"收盘价曲线图: {plot_path}")
        print(f"分析报告: {report_path}")
        print("="*50)
    else:
        print(f"获取 {ts_code} 数据失败，请检查网络连接和Token配置")