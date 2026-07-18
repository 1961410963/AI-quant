"""
TASK5 AI交易引擎：机器学习算法与场景应用
使用 model_data_stock.csv 完成分类模型训练、评估与 ROC 曲线绘制
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 无交互后端，适合后台运行
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
)

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ----------------------------
# 1. 加载数据
# ----------------------------
DATA_PATH = 'model_data_stock.csv'
df = pd.read_csv(DATA_PATH)

print("数据形状:", df.shape)
print("\n前5行:")
print(df.head())
print("\n列名:")
print(df.columns.tolist())

# ----------------------------
# 2. 数据预处理
# ----------------------------
# 目标变量 Y 是布尔值，转换为 0/1
df['Y'] = df['Y'].astype(int)

# 去除非特征列：Date、Code
feature_cols = [c for c in df.columns if c not in ['Date', 'Code', 'Y']]
X = df[feature_cols].copy()
y = df['Y'].copy()

# 处理无穷大和缺失值（金融指标常出现极端值）
X = X.replace([np.inf, -np.inf], np.nan)
X = X.fillna(X.median())

print("\n目标变量分布:")
print(y.value_counts())
print("\n特征描述统计:")
print(X.describe())

# ----------------------------
# 3. 数据划分：时间序列划分 70% 训练 / 30% 测试
# ----------------------------
# 按日期排序，前 70% 作为训练集，后 30% 作为测试集，避免未来函数
df_sorted = df.sort_values('Date').reset_index(drop=True)
X_sorted = df_sorted[feature_cols].replace([np.inf, -np.inf], np.nan)
X_sorted = X_sorted.fillna(X_sorted.median())
y_sorted = df_sorted['Y']

split_idx = int(len(df_sorted) * 0.7)
X_train, X_test = X_sorted.iloc[:split_idx], X_sorted.iloc[split_idx:]
y_train, y_test = y_sorted.iloc[:split_idx], y_sorted.iloc[split_idx:]

print(f"\n训练集样本数: {len(X_train)}, 测试集样本数: {len(X_test)}")
print(f"训练集时间范围: {df_sorted['Date'].iloc[0]} ~ {df_sorted['Date'].iloc[split_idx-1]}")
print(f"测试集时间范围: {df_sorted['Date'].iloc[split_idx]} ~ {df_sorted['Date'].iloc[-1]}")

# ----------------------------
# 4. 特征标准化（仅逻辑回归需要）
# ----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ----------------------------
# 5. 构建并训练分类模型
# ----------------------------
models = {
    'Logistic Regression': {
        'model': LogisticRegression(max_iter=1000, random_state=42),
        'need_scale': True,
    },
    'Decision Tree': {
        'model': DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=50,
            min_samples_leaf=20,
            random_state=42,
        ),
        'need_scale': False,
    },
    'Random Forest': {
        'model': RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        ),
        'need_scale': False,
    },
}

results = []
roc_data = {}

for name, cfg in models.items():
    model = cfg['model']
    if cfg['need_scale']:
        model.fit(X_train_scaled, y_train)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_proba = model.predict_proba(X_test)[:, 1]
        y_pred = model.predict(X_test)

    # 计算评估指标
    auc = roc_auc_score(y_test, y_proba)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    results.append({
        '模型': name,
        'Accuracy': round(acc, 4),
        'Precision': round(prec, 4),
        'Recall': round(rec, 4),
        'F1 Score': round(f1, 4),
        'ROC-AUC': round(auc, 4),
    })

    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    roc_data[name] = (fpr, tpr, auc)

    print(f"\n{name} 混淆矩阵:")
    print(confusion_matrix(y_test, y_pred))
    print(f"\n{name} 分类报告:")
    print(classification_report(y_test, y_pred, zero_division=0))

# ----------------------------
# 6. 模型评估汇总
# ----------------------------
results_df = pd.DataFrame(results)
print("\n========== 模型性能对比汇总 ==========")
print(results_df.to_string(index=False))

best_model = results_df.loc[results_df['ROC-AUC'].idxmax(), '模型']
print(f"\n最佳模型（按 ROC-AUC）: {best_model}")

# ----------------------------
# 7. 绘制 ROC 曲线
# ----------------------------
plt.figure(figsize=(10, 8))
for name, (fpr, tpr, auc) in roc_data.items():
    plt.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {auc:.4f})')

plt.plot([0, 1], [0, 1], 'k--', lw=1, label='Random Guess (AUC = 0.5)')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)', fontsize=12)
plt.ylabel('True Positive Rate (TPR)', fontsize=12)
plt.title('Stock Return Classification - ROC Curve', fontsize=14)
plt.legend(loc='lower right', fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('task5_roc_curve.png', dpi=200)
print("\nROC 曲线已保存至: task5_roc_curve.png")

# ----------------------------
# 8. 特征重要性可视化（以随机森林为例）
# ----------------------------
rf_model = models['Random Forest']['model']
importances = pd.Series(rf_model.feature_importances_, index=feature_cols)
top_features = importances.sort_values(ascending=False).head(15)

plt.figure(figsize=(10, 8))
top_features.plot(kind='barh', color='forestgreen', alpha=0.8)
plt.title('Random Forest - Top-15 特征重要性', fontsize=14)
plt.xlabel('特征重要性', fontsize=12)
plt.ylabel('特征', fontsize=12)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('task5_feature_importance.png', dpi=200)
print("\n特征重要性图已保存至: task5_feature_importance.png")

# 保存结果
results_df.to_csv('task5_model_comparison.csv', index=False)
print("\n模型对比结果已保存至: task5_model_comparison.csv")
