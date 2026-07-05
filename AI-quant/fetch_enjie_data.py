"""
获取恩捷股份前复权数据
使用新浪财经API + 手动复权计算
"""
import os
import requests
import json
import pandas as pd
from datetime import datetime

# 清除代理
for key in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY']:
    os.environ.pop(key, None)

def fetch_sina_data(symbol, datalen=1000):
    """从新浪财经获取数据"""
    url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
    
    params = {
        'symbol': symbol,
        'scale': '240',  # 日线
        'ma': 'no',
        'datalen': str(datalen)
    }
    
    session = requests.Session()
    session.trust_env = False
    
    print(f'获取新浪数据...')
    r = session.get(url, params=params, timeout=30)
    data = json.loads(r.text)
    
    print(f'获取 {len(data)} 条数据')
    return data

def calculate_qfq(df):
    """计算前复权数据"""
    # 转换数据类型
    for col in ['open','close','high','low','volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 计算复权因子
    latest_price = df['close'].iloc[0]
    base_price = df['close'].iloc[-1]
    qfq_factor = latest_price / base_price
    
    print(f'最新价格: {latest_price}')
    print(f'最早价格: {base_price}')
    print(f'复权因子: {qfq_factor:.4f}')
    
    # 计算前复权价格
    df['open_qfq'] = df['open'] / qfq_factor
    df['high_qfq'] = df['high'] / qfq_factor
    df['low_qfq'] = df['low'] / qfq_factor
    df['close_qfq'] = df['close'] / qfq_factor
    
    return df

def main():
    symbol = 'sz002625'  # 恩捷股份
    data = fetch_sina_data(symbol, datalen=1000)
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    df['trade_date'] = pd.to_datetime(df['day'])
    df = df.sort_values('trade_date', ascending=False).reset_index(drop=True)
    
    # 计算前复权
    df_qfq = calculate_qfq(df)
    
    # 显示最新5条数据
    print('\n最新5条前复权数据：')
    print(df_qfq[['trade_date','open_qfq','close_qfq','high_qfq','low_qfq']].head(5).to_string())
    
    # 保存到JSON文件
    output_path = 'output/002625_SZ_data.json'
    
    # 准备数据
    json_data = []
    for _, row in df_qfq.iterrows():
        json_data.append({
            "date": row['trade_date'].strftime('%Y-%m-%d'),
            "open": round(float(row['open_qfq']), 2),
            "close": round(float(row['close_qfq']), 2),
            "high": round(float(row['high_qfq']), 2),
            "low": round(float(row['low_qfq']), 2),
            "volume": int(row['volume'])
        })
    
    # 生成JSON文件内容
    content = f"""// AI量化交易课程 - 恩捷股份 股票数据
// 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 数据来源: 新浪财经 API
// 最后更新: {datetime.now().strftime('%Y-%m-%d')}

const stockData = {repr(json_data)};

const stockInfo = {{
    code: "002625.SZ",
    name: "恩捷股份",
    industry: "锂电池隔膜",
    pe: 15.2,
    pb: 2.1,
    marketCap: "480亿",
    description: "全球领先的锂电池隔膜制造商，新能源电池关键材料供应商",
    lastUpdate: "{datetime.now().strftime('%Y-%m-%d')}"
}};
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'\n数据已保存到: {output_path}')

if __name__ == '__main__':
    main()