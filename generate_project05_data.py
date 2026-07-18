"""
生成项目05.1所需的JSON数据文件
"""
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, classification_report

# 加载数据
df = pd.read_csv('model_data_stock.csv')
df['Y'] = df['Y'].astype(int)
feature_cols = [c for c in df.columns if c not in ['Date', 'Code', 'Y']]

# 预处理
df_sorted = df.sort_values('Date').reset_index(drop=True)
X = df_sorted[feature_cols].replace([np.inf, -np.inf], np.nan)
X = X.fillna(X.median())
y = df_sorted['Y']

split_idx = int(len(df_sorted) * 0.7)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 模型训练
models = {
    '逻辑回归': LogisticRegression(max_iter=1000, random_state=42),
    '决策树': DecisionTreeClassifier(max_depth=5, min_samples_split=50, min_samples_leaf=20, random_state=42),
    '随机森林': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
}

results = []
roc_data = {}
confusion_data = {}
feature_importance_data = []

for name, model in models.items():
    if name == '逻辑回归':
        model.fit(X_train_scaled, y_train)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = model.predict(X_test_scaled)
        # 逻辑回归系数
        coefs = model.coef_[0]
        coef_df = pd.Series(coefs, index=feature_cols)
        top_coef = coef_df.reindex(coef_df.abs().sort_values(ascending=False).index).head(15)
        lr_coef_data = {
            'features': top_coef.index.tolist(),
            'values': top_coef.values.tolist()
        }
    else:
        model.fit(X_train, y_train)
        y_proba = model.predict_proba(X_test)[:, 1]
        y_pred = model.predict(X_test)

    auc = roc_auc_score(y_test, y_proba)
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    results.append({
        'model': name,
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1': round(f1, 4),
        'auc': round(auc, 4),
    })

    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    roc_data[name] = {
        'fpr': fpr.tolist(),
        'tpr': tpr.tolist(),
        'auc': round(auc, 4)
    }

    cm = confusion_matrix(y_test, y_pred)
    confusion_data[name] = cm.tolist()

    # 特征重要性（树模型）
    if hasattr(model, 'feature_importances_'):
        importances = pd.Series(model.feature_importances_, index=feature_cols)
        top_imp = importances.sort_values(ascending=False).head(15)
        if name == '随机森林':
            feature_importance_data = {
                'features': top_imp.index.tolist(),
                'values': top_imp.values.tolist()
            }

# 数据分布
label_dist = y.value_counts().to_dict()
label_dist = {str(k): int(v) for k, v in label_dist.items()}

date_range = {
    'train_start': str(df_sorted['Date'].iloc[0]),
    'train_end': str(df_sorted['Date'].iloc[split_idx-1]),
    'test_start': str(df_sorted['Date'].iloc[split_idx]),
    'test_end': str(df_sorted['Date'].iloc[-1]),
    'train_samples': int(len(X_train)),
    'test_samples': int(len(X_test)),
    'total_samples': int(len(df_sorted)),
}

# 输出所有数据
output = {
    'date_range': date_range,
    'label_distribution': label_dist,
    'model_results': results,
    'roc_curves': roc_data,
    'confusion_matrices': confusion_data,
    'feature_importance': feature_importance_data,
    'lr_coefficients': lr_coef_data,
    'feature_cols': feature_cols,
}

with open('AI-quant/project-05-data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("数据文件已生成: AI-quant/project-05-data.json")
print(f"训练集: {date_range['train_samples']} 样本")
print(f"测试集: {date_range['test_samples']} 样本")
print(f"特征数: {len(feature_cols)}")
