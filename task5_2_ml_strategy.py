import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('model_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(['Code', 'Date']).reset_index(drop=True)

df['Next_Ret_Binary'] = (df['Next_Ret'] > 0).astype(int)

feature_cols = [
    '企业倍数(EV除EBITDA)', '市净率PB(MRQ)', '市现率PCF(现金净流量TTM)',
    '市现率PCF(经营现金流TTM)', '市盈率PE(TTM)', '市盈率PE(TTM,扣除非经常性损益)',
    '市销率PS(TTM)', '股息率(近12个月)', 'MV', '净利润同比增长率',
    '净资产同比增长率', '利润总额(同比增长率)', '基本每股收益(同比增长率)',
    '总资产同比增长率', '现金净流量同比增长率',
    '经营活动产生的现金流量净额(同比增长率)', '营业利润(同比增长率)',
    '营业总收入(同比增长率)', '营业收入(同比增长率)'
]

for col in feature_cols:
    df[col + '_lag1'] = df.groupby('Code')[col].shift(1)
    df[col + '_lag2'] = df.groupby('Code')[col].shift(2)
    df[col + '_ma3'] = df.groupby('Code')[col].rolling(3).mean().reset_index(0, drop=True)
    df[col + '_delta'] = df.groupby('Code')[col].diff(1)

df['Next_Ret_Decile'] = df.groupby('Date')['Next_Ret'].rank(pct=True).apply(lambda x: int(x * 10))
# Top30标签：使用method='first'处理并列，确保每天严格标30个正样本
df['Next_Ret_Top30'] = df.groupby('Date')['Next_Ret'].rank(ascending=False, method='first').apply(lambda x: 1 if x <= 30 else 0)

df = df.dropna().reset_index(drop=True)

df['Year'] = df['Date'].dt.year
df['Quarter'] = df['Date'].dt.quarter
df['YearQuarter'] = df['Year'].astype(str) + 'Q' + df['Quarter'].astype(str)

all_feature_cols = [col for col in df.columns 
                    if any(prefix in col for prefix in ['企业倍数', '市净率', '市现率', '市盈率', '市销率', '股息率', 
                                                        'MV', '净利润', '净资产', '利润总额', '基本每股收益', 
                                                        '总资产', '现金净流量', '经营活动产生', '营业利润', 
                                                        '营业总收入', '营业收入']) and 'Next_Ret' not in col]

# ============================================================
# 数据集拆分：按季度 6:4 比例
# 原始数据共10个季度(2020Q1-2022Q2)
# 前6个季度训练(2020Q1-2021Q2)，后4个季度测试(2021Q3-2022Q2)
# 由于特征工程计算lag2/ma3需要前置数据，训练集中2020Q1-Q2作为特征前置期
# 训练集实际有标签样本: 2020Q3-2021Q2（4个季度），测试集: 2021Q3-2022Q2（4个季度）
# ============================================================
split_date = '2021-06-30'
train_df = df[df['Date'] <= split_date].copy()
test_df = df[df['Date'] > split_date].copy()

print(f'训练集季度: {sorted(train_df["YearQuarter"].unique())}')
print(f'测试集季度: {sorted(test_df["YearQuarter"].unique())}')

X_train = train_df[all_feature_cols]
y_train_clf = train_df['Next_Ret_Top30']
y_train_binary = train_df['Next_Ret_Binary']

X_test = test_df[all_feature_cols]
y_test_clf = test_df['Next_Ret_Top30']
y_test_binary = test_df['Next_Ret_Binary']

X_train = X_train.replace([np.inf, -np.inf], np.nan).fillna(0)
X_test = X_test.replace([np.inf, -np.inf], np.nan).fillna(0)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# 模型训练
# 对比模型（与05.1项目一致）：随机森林分类、决策树分类
# 核心模型：下跌概率模型（用于动态仓位调整）
# ============================================================
models = {}

# 1. 随机森林分类（对比模型）：预测是否为Top30高收益股
models['随机森林'] = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
models['随机森林'].fit(X_train_scaled, y_train_clf)

# 2. 决策树分类（对比模型）：预测是否为Top30高收益股
models['决策树'] = DecisionTreeClassifier(max_depth=5, random_state=42)
models['决策树'].fit(X_train_scaled, y_train_clf)

# 3. 下跌概率模型（核心策略）：预测股票下跌概率(Next_Ret <= 0)，用于动态仓位调整
models['下跌概率模型'] = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
models['下跌概率模型'].fit(X_train_scaled, y_train_binary)

results = {}
for name, model in models.items():
    if name == '下跌概率模型':
        # 下跌概率模型：predict_proba[:, 0] = P(下跌)
        down_prob = model.predict_proba(X_test_scaled)[:, 0]
        results[name] = {'predictions': down_prob.tolist()}
    else:
        y_pred = model.predict_proba(X_test_scaled)[:, 1]
        results[name] = {'predictions': y_pred.tolist()}

test_df['RF_Pred'] = np.array(results['随机森林']['predictions'])
test_df['DT_Pred'] = np.array(results['决策树']['predictions'])
test_df['Down_Prob'] = np.array(results['下跌概率模型']['predictions'])

# ============================================================
# 策略一：基础策略（等权重选Top30）
# ============================================================
def calculate_strategy_metrics(df, pred_col):
    df_sorted = df.copy()
    # 次级排序键：预测概率降序为主，流动性代理(MV市值)降序为辅
    # 决策树max_depth=5叶子节点少、概率值大量重复，概率并列时优先选MV大(流动性好)的股票
    df_sorted = df_sorted.sort_values(['Date', pred_col, 'MV'], ascending=[True, False, False])
    df_sorted['Rank'] = df_sorted.groupby('Date').cumcount() + 1
    df_sorted['In_Portfolio'] = (df_sorted['Rank'] <= 30).astype(int)
    
    portfolio_daily = df_sorted[df_sorted['In_Portfolio'] == 1].groupby('Date')['Next_Ret'].mean()
    market_daily = df_sorted.groupby('Date')['Next_Ret'].mean()
    
    portfolio_cum = (1 + portfolio_daily).cumprod()
    market_cum = (1 + market_daily).cumprod()
    
    total_return = portfolio_cum.iloc[-1] - 1
    market_return = market_cum.iloc[-1] - 1
    
    daily_return = portfolio_daily
    # 数据按季度更新，年化因子为√4（一年4个季度）
    sharpe_ratio = np.sqrt(4) * daily_return.mean() / daily_return.std()
    
    rolling_max = portfolio_cum.cummax()
    drawdown = (portfolio_cum - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    num_trades = df_sorted.groupby('Date')['In_Portfolio'].sum().mean()
    
    return {
        'total_return': total_return,
        'market_return': market_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'avg_trades': num_trades,
        'portfolio_cum': portfolio_cum.values.tolist(),
        'market_cum': market_cum.values.tolist(),
        'dates': portfolio_cum.index.strftime('%Y-%m-%d').tolist(),
        'daily_return': daily_return.values.tolist(),
        'drawdown': drawdown.values.tolist()
    }

# ============================================================
# 策略二：基于下跌概率的动态仓位调整策略（核心策略）
# 核心逻辑：
#   1. 仍然按模型预测排名选Top30股票
#   2. 根据下跌概率动态调整每只股票的仓位权重
#   3. 下跌概率越高 → 仓位越低；下跌概率越低 → 仓位越高
#   4. 权重公式：weight_i = (1 - down_prob_i) / sum(1 - down_prob_j)
# ============================================================
def calculate_risk_weighted_strategy(df, pred_col, prob_col='Down_Prob'):
    df_sorted = df.copy()
    # 次级排序键：预测概率降序为主，流动性代理(MV市值)降序为辅
    df_sorted = df_sorted.sort_values(['Date', pred_col, 'MV'], ascending=[True, False, False])
    df_sorted['Rank'] = df_sorted.groupby('Date').cumcount() + 1
    df_sorted['In_Portfolio'] = (df_sorted['Rank'] <= 30).astype(int)
    
    portfolio = df_sorted[df_sorted['In_Portfolio'] == 1].copy()
    # 动态仓位权重：下跌概率越低，权重越高
    portfolio['Risk_Weight'] = (1 - portfolio[prob_col]).clip(lower=0.01)
    portfolio['Risk_Weight'] = portfolio.groupby('Date')['Risk_Weight'].transform(lambda x: x / x.sum())
    
    # 加权组合收益
    portfolio['Weighted_Ret'] = portfolio['Risk_Weight'] * portfolio['Next_Ret']
    portfolio_daily = portfolio.groupby('Date')['Weighted_Ret'].sum()
    market_daily = df_sorted.groupby('Date')['Next_Ret'].mean()
    
    portfolio_cum = (1 + portfolio_daily).cumprod()
    market_cum = (1 + market_daily).cumprod()
    
    total_return = portfolio_cum.iloc[-1] - 1
    market_return = market_cum.iloc[-1] - 1
    
    daily_return = portfolio_daily
    # 数据按季度更新，年化因子为√4（一年4个季度）
    sharpe_ratio = np.sqrt(4) * daily_return.mean() / daily_return.std()
    
    rolling_max = portfolio_cum.cummax()
    drawdown = (portfolio_cum - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    num_trades = df_sorted.groupby('Date')['In_Portfolio'].sum().mean()
    
    # 统计平均下跌概率和权重分散度
    avg_down_prob = portfolio[prob_col].mean()
    avg_weight_std = portfolio.groupby('Date')['Risk_Weight'].std().mean()
    
    return {
        'total_return': total_return,
        'market_return': market_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'avg_trades': num_trades,
        'portfolio_cum': portfolio_cum.values.tolist(),
        'market_cum': market_cum.values.tolist(),
        'dates': portfolio_cum.index.strftime('%Y-%m-%d').tolist(),
        'daily_return': daily_return.values.tolist(),
        'drawdown': drawdown.values.tolist(),
        'avg_down_prob': avg_down_prob,
        'avg_weight_std': avg_weight_std
    }

# 计算基础策略结果（对比模型）
strategy_results = {}
strategy_results['随机森林'] = calculate_strategy_metrics(test_df, 'RF_Pred')
strategy_results['决策树'] = calculate_strategy_metrics(test_df, 'DT_Pred')

# 计算动态仓位策略结果（核心策略）
risk_strategy_results = {}
risk_strategy_results['随机森林'] = calculate_risk_weighted_strategy(test_df, 'RF_Pred')
risk_strategy_results['决策树'] = calculate_risk_weighted_strategy(test_df, 'DT_Pred')

# ============================================================
# 构建4个策略的统一结构（用于所有对比图表同时展示）
# 策略1: 决策树（基础）
# 策略2: 随机森林（基础）
# 策略3: 决策树+动态仓位（核心）
# 策略4: 随机森林+动态仓位（核心）
# ============================================================
all_strategies = {}
all_strategies['决策树'] = {
    'type': '基础策略',
    'base_model': '决策树',
    **strategy_results['决策树'],
    'avg_down_prob': None,
    'avg_weight_std': None
}
all_strategies['随机森林'] = {
    'type': '基础策略',
    'base_model': '随机森林',
    **strategy_results['随机森林'],
    'avg_down_prob': None,
    'avg_weight_std': None
}
all_strategies['决策树+动态仓位'] = {
    'type': '核心策略',
    'base_model': '决策树',
    **risk_strategy_results['决策树']
}
all_strategies['随机森林+动态仓位'] = {
    'type': '核心策略',
    'base_model': '随机森林',
    **risk_strategy_results['随机森林']
}

# 季度收益（4个策略）
quarterly_results = []
col_map = {
    '随机森林': 'RF_Pred',
    '决策树': 'DT_Pred',
    '随机森林+动态仓位': 'RF_Pred',
    '决策树+动态仓位': 'DT_Pred'
}
for name in all_strategies:
    df_sorted = test_df.copy()
    # 次级排序键：预测概率降序为主，流动性代理(MV市值)降序为辅
    df_sorted = df_sorted.sort_values(['Date', col_map[name], 'MV'], ascending=[True, False, False])
    df_sorted['Rank'] = df_sorted.groupby('Date').cumcount() + 1
    df_sorted['In_Portfolio'] = (df_sorted['Rank'] <= 30).astype(int)
    
    # 核心策略需要按下跌概率加权计算季度收益
    if '动态仓位' in name:
        portfolio = df_sorted[df_sorted['In_Portfolio'] == 1].copy()
        portfolio['Risk_Weight'] = (1 - portfolio['Down_Prob']).clip(lower=0.01)
        portfolio['Risk_Weight'] = portfolio.groupby('Date')['Risk_Weight'].transform(lambda x: x / x.sum())
        portfolio['Weighted_Ret'] = portfolio['Risk_Weight'] * portfolio['Next_Ret']
        for yq, group in portfolio.groupby('YearQuarter'):
            quarterly_return = group['Weighted_Ret'].sum() / group['Date'].nunique()
            quarterly_results.append({
                'model': name,
                'year_quarter': yq,
                'return': quarterly_return
            })
    else:
        for yq, group in df_sorted[df_sorted['In_Portfolio'] == 1].groupby('YearQuarter'):
            quarterly_return = group['Next_Ret'].mean()
            quarterly_results.append({
                'model': name,
                'year_quarter': yq,
                'return': quarterly_return
            })

# 特征重要性
feature_importance = {}
rf_clf = models['随机森林']
feature_importance['随机森林'] = {
    'features': all_feature_cols,
    'importance': rf_clf.feature_importances_.tolist()
}

dt_clf = models['决策树']
feature_importance['决策树'] = {
    'features': all_feature_cols,
    'importance': dt_clf.feature_importances_.tolist()
}

results_dict = {
    'data_info': {
        'total_samples': len(df),
        'train_samples': len(train_df),
        'test_samples': len(test_df),
        'feature_count': len(all_feature_cols),
        'date_range': {
            'start': df['Date'].min().strftime('%Y-%m-%d'),
            'end': df['Date'].max().strftime('%Y-%m-%d')
        },
        'train_quarters_raw': ['2020Q1', '2020Q2', '2020Q3', '2020Q4', '2021Q1', '2021Q2'],
        'test_quarters_raw': ['2021Q3', '2021Q4', '2022Q1', '2022Q2'],
        'train_quarters': sorted(train_df['YearQuarter'].unique().tolist()),
        'test_quarters': sorted(test_df['YearQuarter'].unique().tolist()),
        'split_note': '训练集6个季度(2020Q1-2021Q2)，测试集4个季度(2021Q3-2022Q2)；特征工程lag2/ma3需前置数据，训练集实际有标签样本为2020Q3起'
    },
    'model_results': results,
    'strategy_results': strategy_results,
    'risk_strategy_results': risk_strategy_results,
    'all_strategies': all_strategies,
    'quarterly_results': quarterly_results,
    'feature_importance': feature_importance
}

import json
with open('AI-quant/project-05-2-data.json', 'w', encoding='utf-8') as f:
    json.dump(results_dict, f, ensure_ascii=False, indent=2)

print('✅ 数据生成完成')
print(f'   总样本: {len(df):,}')
print(f'   训练集: {len(train_df):,} ({len(train_df)/len(df)*100:.0f}%)')
print(f'   测试集: {len(test_df):,} ({len(test_df)/len(df)*100:.0f}%)')
print(f'   特征数: {len(all_feature_cols)}')
print()

print('=== 基础策略回测结果（等权重Top30，对比模型） ===')
for name, res in strategy_results.items():
    print(f'{name}:')
    print(f'   总收益率: {res["total_return"]:.2%}')
    print(f'   市场收益率: {res["market_return"]:.2%}')
    print(f'   夏普比率: {res["sharpe_ratio"]:.2f}')
    print(f'   最大回撤: {res["max_drawdown"]:.2%}')
    print()

print('=== 核心策略回测结果（下跌概率动态仓位） ===')
for name, res in risk_strategy_results.items():
    print(f'{name}+动态仓位:')
    print(f'   总收益率: {res["total_return"]:.2%}')
    print(f'   夏普比率: {res["sharpe_ratio"]:.2f}')
    print(f'   最大回撤: {res["max_drawdown"]:.2%}')
    print(f'   平均下跌概率: {res["avg_down_prob"]:.2%}')
    print()
