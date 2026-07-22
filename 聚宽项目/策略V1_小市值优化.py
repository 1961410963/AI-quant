'''
V1优化方案：
- 市值范围10~50亿（原20~30亿）
- 持股5只（原3只）
- 排除ST/*ST
- ROE > 5% + 资产负债率 < 70%
- 单只15%止损
- 每天调仓
'''

## 初始化函数
def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True) 
    set_option('order_volume_ratio', 1)
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    
    g.stocknum = 5                    # 持仓数量
    g.stop_loss_ratio = -0.15         # 止损线
    run_daily(trade, 'every_bar')

## 选出小市值股票
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
    ## 止损检查
    for stock in list(context.portfolio.positions.keys()):
        cost = context.portfolio.positions[stock].avg_cost
        current_price = get_current_data()[stock].last_price
        if current_price is not None and cost > 0:
            if (current_price - cost) / cost <= g.stop_loss_ratio:
                order_target_value(stock, 0)

    ## 获取目标持仓
    target_stocks = check_stocks(context)

    ## 卖出不在目标持仓中的股票
    for stock in list(context.portfolio.positions.keys()):
        if stock not in target_stocks:
            order_target_value(stock, 0)

    ## 买入目标持仓中的股票
    if len(target_stocks) > 0 :
        Cash = context.portfolio.cash / len(target_stocks)
        for stock in target_stocks:
            if stock not in context.portfolio.positions:
                order_value(stock, Cash)

## 过滤停牌
def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]

## 过滤ST
def filter_st_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].is_st]
