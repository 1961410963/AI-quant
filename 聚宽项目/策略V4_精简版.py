'''
V4精简版（中间对比版本）：
- 市值范围10~50亿
- 持股8只
- 排除ST/*ST
- ROE > 5% + 资产负债率 < 70%
- 单只不超过总资金20%
- 每天调仓
- 无综合打分，纯市值排序
- 无止损止盈
'''

## 初始化函数
def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True) 
    set_option('order_volume_ratio', 1)
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    
    g.stocknum = 8
    run_daily(trade, 'every_bar')

## 选出小市值股票（纯市值排序）
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

    return buylist[:g.stocknum]

## 交易函数
def trade(context):
    target_stocks = check_stocks(context)
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
