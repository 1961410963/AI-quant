"""
AI量化交易课程网站数据更新脚本
从本地CSV数据生成网站所需的JSON文件
用法: python update_website.py [--stocks 600967.SH,601899.SH] [--all]
"""
import os
import sys
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
DATA_DIR = OUTPUT_DIR  # CSV数据在同一目录下

# 股票代码映射
STOCK_MAP = {
    "600967.SH": {
        "name": "内蒙一机",
        "industry": "国防军工",
        "pe": 12.8,
        "pb": 1.5,
        "market_cap": "138亿",
        "description": "中国兵器工业集团旗下核心装甲车辆研发制造基地，国内地面兵装行业龙头企业"
    },
    "601899.SH": {
        "name": "紫金矿业",
        "industry": "有色金属",
        "pe": 18.2,
        "pb": 2.8,
        "market_cap": "5200亿",
        "description": "中国最大的黄金生产商之一，全球领先的铜矿企业，矿产资源储备丰富"
    },
    "000001.SZ": {
        "name": "平安银行",
        "industry": "银行",
        "pe": 5.2,
        "pb": 0.6,
        "market_cap": "2100亿",
        "description": "中国第一家全国性商业银行，零售业务领先"
    }
}

def load_csv_data(ts_code):
    """从CSV文件加载数据"""
    csv_file = DATA_DIR / f"{ts_code}_daily_data.csv"
    if not csv_file.exists():
        return None
    
    df = pd.read_csv(csv_file, parse_dates=['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    return df

def calculate_indicators(df):
    """计算技术指标"""
    if df is None or df.empty:
        return df
    
    # 均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['dif'] = exp1 - exp2
    df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
    df['macd'] = (df['dif'] - df['dea']) * 2
    
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # KDJ
    low_9 = df['low'].rolling(window=9).min()
    high_9 = df['high'].rolling(window=9).max()
    rsv = (df['close'] - low_9) / (high_9 - low_9) * 100
    df['k'] = rsv.ewm(com=2, adjust=False).mean()
    df['d'] = df['k'].ewm(com=2, adjust=False).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']
    
    # 布林带
    df['boll_mid'] = df['close'].rolling(window=20).mean()
    boll_std = df['close'].rolling(window=20).std()
    df['boll_upper'] = df['boll_mid'] + 2 * boll_std
    df['boll_lower'] = df['boll_mid'] - 2 * boll_std
    
    # ATR
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()
    
    return df

def generate_stock_json(ts_code, df):
    """生成股票数据JSON"""
    if df is None or df.empty:
        return ""
    
    data = []
    for _, row in df.iterrows():
        data.append({
            "date": row['trade_date'].strftime('%Y-%m-%d'),
            "open": round(float(row['open']), 2),
            "close": round(float(row['close']), 2),
            "high": round(float(row['high']), 2),
            "low": round(float(row['low']), 2),
            "volume": int(row['vol']),
            "ma5": round(float(row['ma5']), 2) if pd.notna(row['ma5']) else None,
            "ma10": round(float(row['ma10']), 2) if pd.notna(row['ma10']) else None,
            "ma20": round(float(row['ma20']), 2) if pd.notna(row['ma20']) else None,
            "ma60": round(float(row['ma60']), 2) if pd.notna(row['ma60']) else None,
            "dif": round(float(row['dif']), 2) if pd.notna(row['dif']) else None,
            "dea": round(float(row['dea']), 2) if pd.notna(row['dea']) else None,
            "macd": round(float(row['macd']), 2) if pd.notna(row['macd']) else None,
            "rsi": round(float(row['rsi']), 2) if pd.notna(row['rsi']) else None,
            "k": round(float(row['k']), 2) if pd.notna(row['k']) else None,
            "d": round(float(row['d']), 2) if pd.notna(row['d']) else None,
            "j": round(float(row['j']), 2) if pd.notna(row['j']) else None,
            "boll_upper": round(float(row['boll_upper']), 2) if pd.notna(row['boll_upper']) else None,
            "boll_mid": round(float(row['boll_mid']), 2) if pd.notna(row['boll_mid']) else None,
            "boll_lower": round(float(row['boll_lower']), 2) if pd.notna(row['boll_lower']) else None,
            "atr": round(float(row['atr']), 2) if pd.notna(row['atr']) else None
        })
    
    return f"const stockData = {repr(data)};"

def update_stock_file(ts_code, stock_info, df):
    """更新股票数据文件"""
    output_path = DATA_DIR / f"{ts_code.replace('.', '_')}_data.json"
    
    json_content = generate_stock_json(ts_code, df)
    
    content = f"""// AI量化交易课程 - {stock_info['name']} 股票数据
// 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 数据来源: Tushare Pro API
// 最后更新: {datetime.now().strftime('%Y-%m-%d')}

{json_content}

const stockInfo = {{
    code: "{ts_code}",
    name: "{stock_info['name']}",
    industry: "{stock_info['industry']}",
    pe: {stock_info['pe']},
    pb: {stock_info['pb']},
    marketCap: "{stock_info['market_cap']}",
    description: "{stock_info['description']}",
    lastUpdate: "{datetime.now().strftime('%Y-%m-%d')}"
}};
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='更新网站股票数据')
    parser.add_argument('--stocks', type=str, help='股票代码列表，逗号分隔，如: 600967.SH,601899.SH')
    parser.add_argument('--all', action='store_true', help='更新所有股票')
    args = parser.parse_args()
    
    # 确定要更新的股票
    if args.stocks:
        ts_codes = [code.strip() for code in args.stocks.split(',')]
    elif args.all:
        ts_codes = list(STOCK_MAP.keys())
    else:
        ts_codes = ['600967.SH', '601899.SH']
    
    print(f"开始更新 {len(ts_codes)} 只股票数据...")
    
    for ts_code in ts_codes:
        if ts_code not in STOCK_MAP:
            print(f"跳过未知股票: {ts_code}")
            continue
            
        stock_info = STOCK_MAP[ts_code]
        print(f"\n正在更新 {stock_info['name']} ({ts_code})...")
        
        try:
            # 从CSV加载数据
            df = load_csv_data(ts_code)
            
            if df is None or df.empty:
                print(f"  未找到CSV数据文件，跳过")
                continue
            
            print(f"  加载 {len(df)} 条数据")
            
            # 计算指标
            df = calculate_indicators(df)
            
            # 更新文件
            output_path = update_stock_file(ts_code, stock_info, df)
            print(f"  已更新: {output_path.name}")
            
        except Exception as e:
            print(f"  更新失败: {e}")
    
    print("\n数据更新完成！")

if __name__ == '__main__':
    main()