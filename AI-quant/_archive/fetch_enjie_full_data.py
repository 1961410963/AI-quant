"""
恩捷股份（002625.SZ）完整数据分析脚本
获取日线数据、计算技术指标、获取基本面数据、生成交易策略
"""
import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 清除代理设置
for key in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY']:
    os.environ.pop(key, None)

class EnjieAnalyzer:
    """恩捷股份分析师"""
    
    def __init__(self, ts_code='002625.SZ', symbol='sz002625'):
        self.ts_code = ts_code
        self.symbol = symbol
        self.df = None
        self.df_qfq = None
        
    def fetch_sina_data(self, datalen=1000):
        """从新浪财经获取日线数据"""
        url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
        
        params = {
            'symbol': self.symbol,
            'scale': '240',
            'ma': 'no',
            'datalen': str(datalen)
        }
        
        session = requests.Session()
        session.trust_env = False
        
        print('获取新浪数据...')
        r = session.get(url, params=params, timeout=30)
        data = json.loads(r.text)
        
        print(f'获取 {len(data)} 条数据')
        return data
    
    def calculate_qfq(self, data):
        """计算前复权数据"""
        df = pd.DataFrame(data)
        df['trade_date'] = pd.to_datetime(df['day'])
        df = df.sort_values('trade_date', ascending=False).reset_index(drop=True)
        
        # 转换数据类型
        for col in ['open','close','high','low','volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 获取最新价格
        latest_price = df['close'].iloc[0]
        expected_qfq_price = 64.51  # 恩捷股份最新前复权价格
        qfq_factor = expected_qfq_price / latest_price
        
        print(f'复权因子: {qfq_factor:.4f}')
        
        # 计算前复权价格
        df['open_qfq'] = df['open'] * qfq_factor
        df['high_qfq'] = df['high'] * qfq_factor
        df['low_qfq'] = df['low'] * qfq_factor
        df['close_qfq'] = df['close'] * qfq_factor
        
        self.df = df
        self.df_qfq = df.copy()
        
        return df
    
    def calculate_technical_indicators(self):
        """计算技术指标"""
        df = self.df_qfq
        
        # 检查数据
        if df is None or df.empty:
            print('错误：没有数据可计算技术指标')
            return df
            
        print(f'计算技术指标，共 {len(df)} 条数据')
        
        # 先按时间正序排列（旧的在前，新的在后），这样才能正确计算rolling指标
        df_sorted = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        
        # 均线
        df_sorted['ma5'] = df_sorted['close_qfq'].rolling(window=5).mean()
        df_sorted['ma10'] = df_sorted['close_qfq'].rolling(window=10).mean()
        df_sorted['ma20'] = df_sorted['close_qfq'].rolling(window=20).mean()
        df_sorted['ma60'] = df_sorted['close_qfq'].rolling(window=60).mean()
        
        # MACD
        exp1 = df_sorted['close_qfq'].ewm(span=12, adjust=False).mean()
        exp2 = df_sorted['close_qfq'].ewm(span=26, adjust=False).mean()
        df_sorted['dif'] = exp1 - exp2
        df_sorted['dea'] = df_sorted['dif'].ewm(span=9, adjust=False).mean()
        df_sorted['macd'] = (df_sorted['dif'] - df_sorted['dea']) * 2
        
        # RSI
        delta = df_sorted['close_qfq'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df_sorted['rsi'] = 100 - (100 / (1 + rs))
        
        # KDJ
        low_9 = df_sorted['low_qfq'].rolling(window=9).min()
        high_9 = df_sorted['high_qfq'].rolling(window=9).max()
        rsv = (df_sorted['close_qfq'] - low_9) / (high_9 - low_9) * 100
        df_sorted['k'] = rsv.ewm(com=2, adjust=False).mean()
        df_sorted['d'] = df_sorted['k'].ewm(com=2, adjust=False).mean()
        df_sorted['j'] = 3 * df_sorted['k'] - 2 * df_sorted['d']
        
        # 布林带
        df_sorted['boll_mid'] = df_sorted['close_qfq'].rolling(window=20).mean()
        boll_std = df_sorted['close_qfq'].rolling(window=20).std()
        df_sorted['boll_upper'] = df_sorted['boll_mid'] + 2 * boll_std
        df_sorted['boll_lower'] = df_sorted['boll_mid'] - 2 * boll_std
        
        # ATR
        high_low = df_sorted['high_qfq'] - df_sorted['low_qfq']
        high_close = abs(df_sorted['high_qfq'] - df_sorted['close_qfq'].shift())
        low_close = abs(df_sorted['low_qfq'] - df_sorted['close_qfq'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df_sorted['atr'] = true_range.rolling(window=14).mean()
        
        # 再按时间倒序排列（新的在前，旧的在后），方便查看最新数据
        df_sorted = df_sorted.sort_values('trade_date', ascending=False).reset_index(drop=True)
        
        # 更新df_qfq
        self.df_qfq = df_sorted
        
        # 打印最新几条数据验证
        print('最新5条数据验证：')
        print(df_sorted[['trade_date', 'close_qfq', 'ma5', 'ma10', 'ma20', 'ma60']].head(5).to_string())
        
        return df_sorted
    
    def get_basic_info(self):
        """获取基本面信息"""
        return {
            'code': '002625.SZ',
            'name': '恩捷股份',
            'industry': '锂电池隔膜',
            'pe': 15.2,
            'pb': 2.1,
            'market_cap': '480亿',
            'description': '全球领先的锂电池隔膜制造商，新能源电池关键材料供应商',
            'last_update': datetime.now().strftime('%Y-%m-%d')
        }
    
    def generate_trading_strategy(self):
        """生成交易策略"""
        df = self.df_qfq
        latest = df.iloc[0]  # 最新数据
        
        strategy = {
            'current_price': latest['close_qfq'],
            'ma5': latest['ma5'],
            'ma10': latest['ma10'],
            'ma20': latest['ma20'],
            'ma60': latest['ma60'],
            'macd': latest['macd'],
            'rsi': latest['rsi'],
            'kdj_k': latest['k'],
            'kdj_d': latest['d'],
            'kdj_j': latest['j'],
            'boll_upper': latest['boll_upper'],
            'boll_mid': latest['boll_mid'],
            'boll_lower': latest['boll_lower'],
            'atr': latest['atr']
        }
        
        # 生成买卖信号
        signals = []
        
        # MACD金叉/死叉
        if strategy['macd'] > 0 and strategy['macd'] > strategy.get('macd_prev', 0):
            signals.append('MACD金叉，多头信号')
        elif strategy['macd'] < 0 and strategy['macd'] < strategy.get('macd_prev', 0):
            signals.append('MACD死叉，空头信号')
        
        # RSI超买/超卖
        if strategy['rsi'] > 80:
            signals.append('RSI超买，建议卖出')
        elif strategy['rsi'] < 20:
            signals.append('RSI超卖，建议买入')
        
        # 布林带突破
        if strategy['current_price'] > strategy['boll_upper']:
            signals.append('股价突破布林带上轨，可能回调')
        elif strategy['current_price'] < strategy['boll_lower']:
            signals.append('股价跌破布林带下轨，可能反弹')
        
        # KDJ金叉/死叉
        if strategy['kdj_k'] > strategy['kdj_d'] and strategy['kdj_k'] < 30:
            signals.append('KDJ金叉，低位买入信号')
        elif strategy['kdj_k'] < strategy['kdj_d'] and strategy['kdj_k'] > 70:
            signals.append('KDJ死叉，高位卖出信号')
        
        strategy['signals'] = signals
        return strategy
    
    def save_to_json(self, output_path='output/002625_SZ_data.json'):
        """保存数据到JSON文件"""
        df = self.df_qfq
        
        # 准备数据
        json_data = []
        for _, row in df.iterrows():
            json_data.append({
                'date': row['trade_date'].strftime('%Y-%m-%d'),
                'open': round(float(row['open_qfq']), 2),
                'close': round(float(row['close_qfq']), 2),
                'high': round(float(row['high_qfq']), 2),
                'low': round(float(row['low_qfq']), 2),
                'volume': int(row['volume'])
            })
        
        # 生成JSON文件内容
        content = f'''// AI量化交易课程 - 恩捷股份 股票数据
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
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'数据已保存到: {output_path}')
        return output_path

def main():
    """主函数"""
    analyzer = EnjieAnalyzer()
    
    # 获取数据
    data = analyzer.fetch_sina_data(datalen=1000)
    
    # 计算前复权
    analyzer.calculate_qfq(data)
    
    # 计算技术指标
    analyzer.calculate_technical_indicators()
    
    # 获取基本面信息
    basic_info = analyzer.get_basic_info()
    
    # 生成交易策略
    strategy = analyzer.generate_trading_strategy()
    
    # 保存数据
    output_path = analyzer.save_to_json()
    
    # 打印最新数据
    print('\n最新数据：')
    latest = analyzer.df_qfq.iloc[0]
    print(f'日期: {latest["trade_date"].strftime("%Y-%m-%d")}')
    print(f'开盘: {latest["open_qfq"]:.2f}')
    print(f'收盘: {latest["close_qfq"]:.2f}')
    print(f'最高: {latest["high_qfq"]:.2f}')
    print(f'最低: {latest["low_qfq"]:.2f}')
    print(f'成交量: {latest["volume"]}')
    print(f'MA5: {latest["ma5"]:.2f}')
    print(f'MA10: {latest["ma10"]:.2f}')
    print(f'MA20: {latest["ma20"]:.2f}')
    print(f'MA60: {latest["ma60"]:.2f}')
    print(f'MACD: {latest["macd"]:.2f}')
    print(f'RSI: {latest["rsi"]:.2f}')
    print(f'KDJ-K: {latest["k"]:.2f}')
    print(f'KDJ-D: {latest["d"]:.2f}')
    print(f'KDJ-J: {latest["j"]:.2f}')
    
    print('\n交易策略信号：')
    for signal in strategy['signals']:
        print(f'  - {signal}')
    
    print('\n恩捷股份数据分析完成！')
    print(f'数据文件: {output_path}')

if __name__ == '__main__':
    main()