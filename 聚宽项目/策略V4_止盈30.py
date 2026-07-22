'''
V4优化方案（基于V3）：
- 市值范围10~50亿
- 持股8只
- 排除ST/*ST
- ROE > 5% + 资产负债率 < 70%
- 单只10%止损 + 单只30%止盈
- 每天调仓
- 综合打分选股：市值50% + ROE 25% + 低波动25%
- 单只不超过总资金20%
- 止损/止盈后从排名后一位补入，保持满仓
'''

## 初始化函数
def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True) 
    set_option('order_volume_ratio', 1)
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    
    g.stocknum = 8                    # 持仓数量
    g.stop_loss_ratio = -0.10         # 止损线
    g.take_profit_ratio = 0.30        # 止盈线
    run_daily(trade, 'every_bar')

## 选出所有候选股票，按综合评分从高到低排序
def check_stocks(context):
    q = query(
            valuation.code,
            valuation.market_cap,
            indicator.roe,
            (balance.total_liability / balance.total_assets * 100).label('debt_ratio')
        ).filter(
            valuation.market_cap.between(10, 50),
            indicator.roe > 5,
            balance.total_liability / balance.total_assets * 100 < 70
        ).order_by(
            valuation.market_cap.asc()
        )

    df = get_fundamentals(q)
    if df.empty:
        return []
    
    buylist = list(df['code'])
    buylist = filter_paused_stock(buylist)
    buylist = filter_st_stock(buylist)
    
    if len(buylist) == 0:
        return []
    
    df = df[df['code'].isin(buylist)].copy()
    if df.empty:
        return []
    
    ## 获取20日波动率
    close_prices = history(21, '1d', 'close', security_list=buylist, df=True)
    vol_dict = {}
    if close_prices is not None and len(close_prices) >= 2:
        returns = close_prices.pct_change().dropna()
        vol_series = returns.std()
        vol_dict = vol_series.to_dict()
    
    ## 计算综合评分
    mcap_min = df['market_cap'].min()
    mcap_max = df['market_cap'].max()
    roe_min = df['roe'].min()
    roe_max = df['roe'].max()
    
    scores = []
    for _, row in df.iterrows():
        code = row['code']
        mcap = row['market_cap']
        roe = row['roe']
        vol = vol_dict.get(code, None)
        
        if mcap_max > mcap_min:
            mcap_score = 100 - (mcap - mcap_min) / (mcap_max - mcap_min) * 100
        else:
            mcap_score = 50
        
        if roe_max > roe_min:
            roe_score = (roe - roe_min) / (roe_max - roe_min) * 100
        else:
            roe_score = 50
        
        if vol is not None:
            vol_min = min(vol_dict.values())
            vol_max = max(vol_dict.values())
            if vol_max > vol_min:
                vol_score = 100 - (vol - vol_min) / (vol_max - vol_min) * 100
            else:
                vol_score = 50
        else:
            vol_score = 0
        
        total_score = mcap_score * 0.5 + roe_score * 0.25 + vol_score * 0.25
        scores.append((code, total_score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return [code for code, _ in scores]

## 交易函数
def trade(context):
    ## 止损止盈检查
    exclude_stocks = []
    for stock in list(context.portfolio.positions.keys()):
        cost = context.portfolio.positions[stock].avg_cost
        current_price = get_current_data()[stock].last_price
        if current_price is not None and cost > 0:
            pnl = (current_price - cost) / cost
            if pnl <= g.stop_loss_ratio:
                order_target_value(stock, 0)
                exclude_stocks.append(stock)
            elif pnl >= g.take_profit_ratio:
                order_target_value(stock, 0)
                exclude_stocks.append(stock)

    ## 获取完整排名，排除止损止盈股后取前N只
    full_ranked = check_stocks(context)
    target_stocks = [s for s in full_ranked if s not in exclude_stocks][:g.stocknum]
    if len(target_stocks) == 0:
        return

    ## 卖出不在目标持仓中的股票
    for stock in list(context.portfolio.positions.keys()):
        if stock not in target_stocks:
            order_target_value(stock, 0)

    ## 买入/调整到目标仓位
    target_per_stock = context.portfolio.total_value / len(target_stocks)
    max_per_stock = context.portfolio.total_value * 0.2
    target_value = min(target_per_stock, max_per_stock)
    
    for stock in target_stocks:
        order_target_value(stock, target_value)

## 过滤停牌
def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]

## 过滤ST
def filter_st_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].is_st]
