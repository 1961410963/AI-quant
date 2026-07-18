import json

with open('AI-quant/project-05-2-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_json = json.dumps(data, ensure_ascii=False)

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目05.2 智能决策者：机器学习定制专属策略</title>
    <script src="echarts.min.js"></script>
    <script>
    if (typeof echarts === 'undefined') {
        document.write('<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"><\/script>');
    }
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.8;
        }
        .page-header {
            background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
            color: #fff;
            padding: 50px 20px 70px;
            text-align: center;
        }
        .breadcrumb { font-size: 13px; opacity: 0.85; margin-bottom: 16px; }
        .breadcrumb a { color: #fff; text-decoration: none; }
        .header-title { font-size: 32px; font-weight: 700; margin-bottom: 10px; }
        .header-desc { font-size: 15px; opacity: 0.9; max-width: 800px; margin: 0 auto; }
        .container { max-width: 1100px; margin: -40px auto 0; padding: 0 20px 60px; }
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }
        .overview-card {
            background: #fff;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        .overview-card .num {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #065f46, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .overview-card .label { font-size: 13px; color: #64748b; margin-top: 4px; }
        .section {
            background: #fff;
            border-radius: 14px;
            padding: 30px;
            margin-bottom: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        }
        .section-title {
            font-size: 22px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 6px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
        }
        .section-desc { font-size: 14px; color: #64748b; margin-bottom: 20px; }
        .chart-container { width: 100%; height: 440px; margin-top: 8px; }
        .chart-container.small { height: 380px; }
        .chart-container.large { height: 520px; }
        .chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .fig-title { font-size: 15px; font-weight: 600; color: #334155; margin: 14px 0 6px; }
        .fig-caption {
            font-size: 13px;
            color: #64748b;
            line-height: 1.7;
            padding: 12px 16px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 3px solid #10b981;
            margin-bottom: 10px;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            margin-bottom: 16px;
        }
        .metrics-table th, .metrics-table td {
            padding: 10px 14px;
            border-bottom: 1px solid #e2e8f0;
            text-align: center;
        }
        .metrics-table th { background: #f8fafc; font-weight: 600; color: #475569; }
        .best-score { color: #059669; font-weight: 700; }
        .pros-cons-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .pros-card {
            background: #f0fdf4;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #10b981;
        }
        .cons-card {
            background: #fef2f2;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #dc2626;
        }
        .pros-card h3, .cons-card h3 { font-size: 15px; margin-bottom: 10px; }
        .pros-card ul, .cons-card ul { list-style: none; padding-left: 0; font-size: 13px; line-height: 1.8; }
        .pros-card li { color: #065f46; }
        .cons-card li { color: #991b1b; }
        .factor-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            font-size: 13px;
        }
        .factor-item {
            padding: 10px 14px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 3px solid #3b82f6;
        }
        .model-compare-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-bottom: 16px;
        }
        .model-compare-table th, .model-compare-table td {
            padding: 12px 14px;
            border: 1px solid #e2e8f0;
            text-align: left;
        }
        .model-compare-table th { background: #f0fdf4; color: #065f46; font-weight: 600; }
        .model-compare-table tr:nth-child(even) { background: #f8fafc; }
        .strategy-box {
            background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            border: 1px solid #d1fae5;
        }
        .strategy-box h3 { font-size: 16px; color: #065f46; margin-bottom: 12px; }
        .strategy-box p { font-size: 14px; color: #374151; line-height: 1.8; }
        .strategy-box .formula {
            background: #fff;
            padding: 12px 16px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #1e293b;
            margin: 10px 0;
            border-left: 3px solid #10b981;
        }
        .footer {
            text-align: center;
            padding: 30px 20px;
            color: #94a3b8;
            font-size: 13px;
        }
        .footer a { color: #6366f1; text-decoration: none; }
        @media (max-width: 768px) {
            .chart-row { grid-template-columns: 1fr; }
            .pros-cons-grid { grid-template-columns: 1fr; }
            .header-title { font-size: 24px; }
            .section { padding: 20px; }
        }
    </style>
</head>
<body>

<div class="page-header">
    <div class="breadcrumb"><a href="index.html">← 返回首页</a></div>
    <div class="header-title">项目05.2 · 智能决策者</div>
    <div class="header-desc">机器学习定制专属策略 —— 基于scikit-learn的股票收益率排序模型与交易策略回测</div>
</div>

<div class="container">
    <div class="overview-grid" id="overview-grid"></div>

    <!-- 一、ML交易策略核心理念 -->
    <div class="section">
        <h2 class="section-title">一、ML交易策略核心理念</h2>
        <p class="section-desc">基于机器学习模型的交易策略，核心是将模型预测转化为可执行的交易决策</p>
        
        <div class="pros-cons-grid">
            <div class="pros-card">
                <h3>✅ 四大优势</h3>
                <ul>
                    <li><strong>自适应性</strong>：能从数据中学习，适应市场变化</li>
                    <li><strong>多维决策</strong>：同时考虑多个特征的复杂关系</li>
                    <li><strong>概率输出</strong>：提供决策置信度，便于风险管理</li>
                    <li><strong>可优化性</strong>：通过调整模型和参数持续改进</li>
                </ul>
            </div>
            <div class="cons-card">
                <h3>⚠️ 五大局限</h3>
                <ul>
                    <li><strong>数据依赖</strong>：需要大量高质量历史数据</li>
                    <li><strong>过拟合风险</strong>：可能学到历史噪声而非真实规律</li>
                    <li><strong>黑盒问题</strong>：复杂模型难以解释，出问题难诊断</li>
                    <li><strong>计算成本</strong>：训练和预测需要较多计算资源</li>
                    <li><strong>市场变化</strong>：模型可能在市场环境变化后失效</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- 二、自变量因子与应变量定义 -->
    <div class="section">
        <h2 class="section-title">二、自变量因子与应变量定义</h2>
        <p class="section-desc">量化交易中机器学习模型的输入特征和预测目标</p>
        
        <div style="margin-bottom:20px;">
            <h3 style="font-size:16px; margin-bottom:12px; color:#334155;">📊 自变量因子（输入特征）</h3>
            <div class="factor-list">
                <div class="factor-item"><strong>估值因子</strong>：市盈率PE、市净率PB、市销率PS、市现率PCF、企业倍数</div>
                <div class="factor-item"><strong>成长因子</strong>：净利润同比增长率、营收同比增长率、利润总额同比增长率</div>
                <div class="factor-item"><strong>现金流因子</strong>：经营现金流、现金净流量同比增长率</div>
                <div class="factor-item"><strong>质量因子</strong>：总资产同比增长率、净资产同比增长率、基本每股收益增长率</div>
                <div class="factor-item"><strong>技术因子</strong>：滞后项(lag1/lag2)、移动平均(MA3)、变化量(delta)</div>
                <div class="factor-item"><strong>市场因子</strong>：市值MV、股息率</div>
            </div>
        </div>

        <div>
            <h3 style="font-size:16px; margin-bottom:12px; color:#334155;">🎯 应变量（预测目标）</h3>
            <div class="factor-list">
                <div class="factor-item"><strong>Next_Ret</strong>：未来收益率（回归任务目标）</div>
                <div class="factor-item"><strong>Next_Ret_Binary</strong>：涨跌二分类标签（下跌概率模型目标）</div>
                <div class="factor-item"><strong>Next_Ret_Top30</strong>：是否为Top30高收益股票（分类任务目标）</div>
                <div class="factor-item"><strong>Next_Ret_Decile</strong>：收益率分位数排名</div>
            </div>
        </div>
    </div>

    <!-- 三、四个模型差异对比 -->
    <div class="section">
        <h2 class="section-title">三、四个模型差异对比</h2>
        <p class="section-desc">本项目训练四种核心模型，分别从任务类型、预测目标、输出形式等维度对比</p>
        
        <table class="model-compare-table">
            <thead>
                <tr>
                    <th>对比维度</th>
                    <th>随机森林回归</th>
                    <th>决策树回归</th>
                    <th>随机森林分类</th>
                    <th>决策树分类</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>任务类型</strong></td>
                    <td>回归</td>
                    <td>回归</td>
                    <td>二分类</td>
                    <td>二分类</td>
                </tr>
                <tr>
                    <td><strong>预测目标</strong></td>
                    <td>未来收益率 Next_Ret</td>
                    <td>未来收益率 Next_Ret</td>
                    <td>是否Top30高收益股</td>
                    <td>是否Top30高收益股</td>
                </tr>
                <tr>
                    <td><strong>输出形式</strong></td>
                    <td>连续值（收益率预测值）</td>
                    <td>连续值（收益率预测值）</td>
                    <td>概率值（0~1）</td>
                    <td>概率值（0~1）</td>
                </tr>
                <tr>
                    <td><strong>模型结构</strong></td>
                    <td>100棵决策树集成</td>
                    <td>单棵决策树</td>
                    <td>100棵决策树集成</td>
                    <td>单棵决策树</td>
                </tr>
                <tr>
                    <td><strong>树深度</strong></td>
                    <td>max_depth=10</td>
                    <td>max_depth=5</td>
                    <td>max_depth=10</td>
                    <td>max_depth=5</td>
                </tr>
                <tr>
                    <td><strong>选股排序依据</strong></td>
                    <td>按预测收益率排序</td>
                    <td>按预测收益率排序</td>
                    <td>按Top30概率排序</td>
                    <td>按Top30概率排序</td>
                </tr>
                <tr>
                    <td><strong>优势</strong></td>
                    <td>抗过拟合，预测精度高</td>
                    <td>可解释性强，训练快</td>
                    <td>概率输出便于风控</td>
                    <td>规则清晰，易于理解</td>
                </tr>
                <tr>
                    <td><strong>劣势</strong></td>
                    <td>计算成本较高</td>
                    <td>容易过拟合</td>
                    <td>计算成本较高</td>
                    <td>决策边界较粗</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- 四、数据集拆分 -->
    <div class="section">
        <h2 class="section-title">四、数据集拆分（按季度）</h2>
        <p class="section-desc">按时间序列拆分，避免数据泄露。原始10个季度经特征工程后保留8个季度</p>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
            <div style="background:#f0fdf4; padding:20px; border-radius:10px; border-left:4px solid #10b981;">
                <h3 style="font-size:15px; color:#065f46; margin-bottom:10px;">📦 训练集</h3>
                <p style="font-size:13px; color:#374151;" id="train-info">--</p>
            </div>
            <div style="background:#fef3c7; padding:20px; border-radius:10px; border-left:4px solid #f59e0b;">
                <h3 style="font-size:15px; color:#92400e; margin-bottom:10px;">📊 测试集</h3>
                <p style="font-size:13px; color:#374151;" id="test-info">--</p>
            </div>
        </div>
        <div class="fig-caption" style="margin-top:12px;">
            <strong>说明：</strong>原始数据覆盖2020Q1-2022Q2共10个季度。由于特征工程计算滞后项(lag2)和移动平均(MA3)需要前置数据，dropna后2020Q1-Q2被丢弃，实际训练集为2020Q3-2021Q2（4个季度），测试集为2021Q3-2022Q2（4个季度）。
        </div>
    </div>

    <!-- 五、策略完整框架与参数 -->
    <div class="section">
        <h2 class="section-title">五、策略完整框架与核心参数</h2>
        <p class="section-desc">从模型预测到交易执行的完整工作流程</p>
        
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:14px; margin-bottom:20px;">
            <div style="background:linear-gradient(135deg,#065f46,#10b981); color:#fff; padding:18px; border-radius:12px; text-align:center;">
                <div style="font-size:26px; font-weight:700; margin-bottom:4px;">01</div>
                <div style="font-size:14px;">模型预测</div>
            </div>
            <div style="background:linear-gradient(135deg,#10b981,#84cc16); color:#fff; padding:18px; border-radius:12px; text-align:center;">
                <div style="font-size:26px; font-weight:700; margin-bottom:4px;">02</div>
                <div style="font-size:14px;">概率输出</div>
            </div>
            <div style="background:linear-gradient(135deg,#84cc16,#eab308); color:#fff; padding:18px; border-radius:12px; text-align:center;">
                <div style="font-size:26px; font-weight:700; margin-bottom:4px;">03</div>
                <div style="font-size:14px;">信号生成</div>
            </div>
            <div style="background:linear-gradient(135deg,#eab308,#f97316); color:#fff; padding:18px; border-radius:12px; text-align:center;">
                <div style="font-size:26px; font-weight:700; margin-bottom:4px;">04</div>
                <div style="font-size:14px;">风控过滤</div>
            </div>
            <div style="background:linear-gradient(135deg,#f97316,#ef4444); color:#fff; padding:18px; border-radius:12px; text-align:center;">
                <div style="font-size:26px; font-weight:700; margin-bottom:4px;">05</div>
                <div style="font-size:14px;">策略回测</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px,1fr)); gap:14px;">
            <div style="background:#f0fdf4; padding:16px; border-radius:10px; border-left:4px solid #10b981;">
                <div style="font-size:14px; font-weight:600; color:#065f46; margin-bottom:8px;">信号参数</div>
                <div style="font-size:13px; color:#475569;">买入阈值: 预测排名前30支</div>
                <div style="font-size:13px; color:#475569;">调仓频率: 按季度</div>
            </div>
            <div style="background:#fef3c7; padding:16px; border-radius:10px; border-left:4px solid #f59e0b;">
                <div style="font-size:14px; font-weight:600; color:#92400e; margin-bottom:8px;">风控参数</div>
                <div style="font-size:13px; color:#475569;">最大回撤: 动态监控</div>
                <div style="font-size:13px; color:#475569;">分散持仓: 每支约3%</div>
            </div>
            <div style="background:#f0f9ff; padding:16px; border-radius:10px; border-left:4px solid #3b82f6;">
                <div style="font-size:14px; font-weight:600; color:#1e40af; margin-bottom:8px;">策略逻辑</div>
                <div style="font-size:13px; color:#475569;">每季选预测收益最高30支</div>
                <div style="font-size:13px; color:#475569;">等权重配置 / 动态仓位</div>
            </div>
        </div>
    </div>

    <!-- 六、模型训练与评估 -->
    <div class="section">
        <h2 class="section-title">六、模型训练与评估</h2>
        <p class="section-desc">训练四种模型（随机森林/决策树的回归与分类版本）+ 下跌概率模型，对比效果</p>
        
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>模型</th>
                    <th>任务类型</th>
                    <th>RMSE</th>
                    <th>R²</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>随机森林回归</strong></td>
                    <td>回归</td>
                    <td id="rf-reg-rmse">--</td>
                    <td id="rf-reg-r2">--</td>
                </tr>
                <tr>
                    <td><strong>决策树回归</strong></td>
                    <td>回归</td>
                    <td id="dt-reg-rmse">--</td>
                    <td id="dt-reg-r2">--</td>
                </tr>
                <tr>
                    <td><strong>随机森林分类</strong></td>
                    <td>分类</td>
                    <td colspan="2">预测Top30概率，输出0~1之间概率值</td>
                </tr>
                <tr>
                    <td><strong>决策树分类</strong></td>
                    <td>分类</td>
                    <td colspan="2">预测Top30概率，输出0~1之间概率值</td>
                </tr>
                <tr>
                    <td><strong>下跌概率模型</strong></td>
                    <td>分类</td>
                    <td colspan="2">预测下跌概率P(Next_Ret≤0)，用于动态仓位调整</td>
                </tr>
            </tbody>
        </table>

        <div class="fig-title">图 1：随机森林特征重要性（Top-15）</div>
        <div id="chart-feat-rf" class="chart-container large"></div>
        <div class="fig-caption">
            <strong>解读：</strong>特征重要性反映了各因子在模型决策中的贡献程度。排名靠前的特征对预测收益率排序影响最大，可用于特征筛选和策略优化。从图中可以看出，哪些财务指标是模型认为最有预测价值的。
        </div>

        <div class="fig-title">图 2：决策树特征重要性（Top-15）</div>
        <div id="chart-feat-dt" class="chart-container large"></div>
    </div>

    <!-- 七、基础策略回测结果 -->
    <div class="section">
        <h2 class="section-title">七、基础策略回测结果（等权重Top30）</h2>
        <p class="section-desc">基于模型预测构建交易策略，每季挑选预测收益最好的30支股票，等权重配置</p>
        
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>模型策略</th>
                    <th>总收益率</th>
                    <th>市场收益率</th>
                    <th>超额收益</th>
                    <th>夏普比率</th>
                    <th>最大回撤</th>
                </tr>
            </thead>
            <tbody id="strategy-tbody"></tbody>
        </table>

        <div class="fig-title">图 3：各策略累计收益率曲线对比</div>
        <div id="chart-cum-return" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>所有ML策略均显著跑赢市场（市场收益率为-5.84%）。纵轴为累计收益率百分比，0%为起始基准线。决策树回归策略表现最佳（34.23%），其次是随机森林分类（20.32%）和随机森林回归（13.94%）。
        </div>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 4：各策略回撤曲线</div>
                <div id="chart-drawdown" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 5：季度收益率对比</div>
                <div id="chart-quarterly" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>回撤曲线显示各策略的风险水平，最大回撤均控制在8%以内，表现稳健。季度收益率对比展示了不同模型在各时间段的表现差异，可用于分析策略的稳定性和市场适应性。
        </div>
    </div>

    <!-- 八、基于下跌概率的动态仓位调整策略 -->
    <div class="section">
        <h2 class="section-title">八、基于下跌概率的动态仓位调整策略</h2>
        <p class="section-desc">利用下跌概率模型动态调整持仓权重，实现风险优化</p>
        
        <div class="strategy-box">
            <h3>🎯 策略核心逻辑</h3>
            <p>基础策略中，选出的30支股票等权重配置（每支约3.3%）。但不同股票的下跌风险不同，等权重配置没有区分风险。</p>
            <p>本策略引入<strong>下跌概率模型</strong>，对每支股票预测其下跌概率 P(Next_Ret ≤ 0)，并据此动态调整仓位：</p>
            <div class="formula">
                weight_i = (1 - down_prob_i) / Σ(1 - down_prob_j), &nbsp; j=1..30
            </div>
            <p>即：下跌概率越高的股票，仓位权重越低；下跌概率越低的股票，仓位权重越高。所有权重归一化为1。</p>
        </div>

        <div class="strategy-box" style="background:linear-gradient(135deg,#f0f9ff,#eff6ff); border-color:#bfdbfe;">
            <h3 style="color:#1e40af;">📋 操作步骤</h3>
            <p><strong>第1步 - 选股：</strong>按模型预测排名选Top30股票（与基础策略相同）</p>
            <p><strong>第2步 - 预测下跌概率：</strong>对选出的30支股票，用下跌概率模型计算每支的下跌概率</p>
            <p><strong>第3步 - 计算仓位权重：</strong>weight_i = (1 - down_prob_i) / Σ(1 - down_prob_j)</p>
            <p><strong>第4步 - 加权持仓：</strong>按计算出的权重配置资金，非等权重</p>
            <p><strong>第5步 - 季度调仓：</strong>每季度重新执行上述流程</p>
        </div>

        <table class="metrics-table">
            <thead>
                <tr>
                    <th>模型策略</th>
                    <th>策略类型</th>
                    <th>总收益率</th>
                    <th>夏普比率</th>
                    <th>最大回撤</th>
                    <th>平均下跌概率</th>
                </tr>
            </thead>
            <tbody id="risk-strategy-tbody"></tbody>
        </table>

        <div class="fig-title">图 6：基础策略 vs 动态仓位策略 — 总收益率对比</div>
        <div id="chart-risk-compare-return" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>动态仓位策略在所有模型上都提升了总收益率。决策树回归的提升最为显著，从34.23%提升至44.91%（提升10.68个百分点）。
        </div>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 7：夏普比率对比</div>
                <div id="chart-risk-compare-sharpe" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 8：最大回撤对比</div>
                <div id="chart-risk-compare-dd" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>动态仓位策略在夏普比率和最大回撤两个风险指标上均有改善。随机森林分类策略的夏普比率从7.06提升至7.87，最大回撤从-6.62%降至-5.74%，体现了下跌概率加权在风险控制上的优势。
        </div>

        <div class="fig-title">图 9：动态仓位策略累计收益率曲线</div>
        <div id="chart-risk-cum-return" class="chart-container"></div>
    </div>

    <!-- 九、策略对比可视化 -->
    <div class="section">
        <h2 class="section-title">九、基础策略四维对比</h2>
        <p class="section-desc">四大维度对比各基础策略表现：收益率、夏普比率、回撤、交易次数</p>
        
        <div class="chart-row">
            <div>
                <div class="fig-title">图 10：总收益率对比</div>
                <div id="chart-return-compare" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 11：夏普比率对比</div>
                <div id="chart-sharpe-compare" class="chart-container small"></div>
            </div>
        </div>
        <div class="chart-row">
            <div>
                <div class="fig-title">图 12：最大回撤对比</div>
                <div id="chart-dd-compare" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 13：平均持仓数量对比</div>
                <div id="chart-trades-compare" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>随机森林分类策略在风险调整后收益（夏普比率=7.06）上表现最优，体现了其在收益与风险之间的良好平衡。决策树回归策略收益率最高但稳定性稍弱。整体来看，ML策略在收益和风险调整后收益上均优于市场平均水平。
        </div>
    </div>

</div>

<div class="footer">
    <p>© 2026 北大光华AI量化交易课程 · 项目05.2</p>
    <p style="margin-top:6px;"><a href="https://github.com/1961410963/AI-quant" target="_blank">GitHub仓库</a></p>
</div>

<script>
const allData = ''' + data_json + r''';

document.addEventListener('DOMContentLoaded', function() {
    if (typeof echarts === 'undefined') {
        document.querySelector('.container').innerHTML =
            '<div style="padding:40px; text-align:center; background:#fff; border-radius:12px;">' +
            '<h3 style="color:#dc2626; margin-bottom:10px;">ECharts 加载失败</h3>' +
            '<p style="color:#64748b;">请检查网络连接，或确保 echarts.min.js 文件在同一目录下</p>' +
            '</div>';
        return;
    }
    initAll();
});

function initAll() {
    renderOverview();
    renderDataSplit();
    renderMetrics();
    renderFeatureImportance('chart-feat-rf', '随机森林');
    renderFeatureImportance('chart-feat-dt', '决策树');
    renderStrategyTable();
    renderRiskStrategyTable();
    renderCumReturn();
    renderDrawdown();
    renderQuarterly();
    renderCompareCharts();
    renderRiskCompareCharts();
    renderRiskCumReturn();
}

function renderOverview() {
    const grid = document.getElementById('overview-grid');
    const di = allData.data_info;
    const items = [
        { id: 'stat-total', label: '总样本数', value: di.total_samples },
        { id: 'stat-train', label: '训练集样本', value: di.train_samples },
        { id: 'stat-test', label: '测试集样本', value: di.test_samples },
        { id: 'stat-feat', label: '特征数量', value: di.feature_count },
        { id: 'stat-model', label: '对比模型数', value: 5 }
    ];
    grid.innerHTML = items.map(item =>
        '<div class="overview-card"><div class="num" id="' + item.id + '">' + item.value.toLocaleString() + '</div><div class="label">' + item.label + '</div></div>'
    ).join('');
}

function renderDataSplit() {
    const di = allData.data_info;
    const trainQuarters = di.train_quarters || [];
    const testQuarters = di.test_quarters || [];
    document.getElementById('train-info').innerHTML =
        '季度: ' + trainQuarters.join(', ') + '<br>' +
        '样本数: ' + di.train_samples.toLocaleString() + '<br>' +
        '占比: ' + (di.train_samples / di.total_samples * 100).toFixed(0) + '%';
    document.getElementById('test-info').innerHTML =
        '季度: ' + testQuarters.join(', ') + '<br>' +
        '样本数: ' + di.test_samples.toLocaleString() + '<br>' +
        '占比: ' + (di.test_samples / di.total_samples * 100).toFixed(0) + '%';
}

function renderMetrics() {
    const mr = allData.model_results;
    document.getElementById('rf-reg-rmse').textContent = mr['随机森林回归'].rmse.toFixed(4);
    document.getElementById('rf-reg-r2').textContent = mr['随机森林回归'].r2.toFixed(4);
    document.getElementById('dt-reg-rmse').textContent = mr['决策树回归'].rmse.toFixed(4);
    document.getElementById('dt-reg-r2').textContent = mr['决策树回归'].r2.toFixed(4);
}

function renderFeatureImportance(chartId, modelName) {
    const chart = echarts.init(document.getElementById(chartId));
    const fi = allData.feature_importance[modelName];
    const sorted = fi.features.map((f, i) => ({ name: f, value: fi.importance[i] }))
        .sort((a, b) => b.value - a.value).slice(0, 15);
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 260, right: 60, top: 10, bottom: 25 },
        xAxis: { type: 'value', name: '特征重要性', nameGap: 10, nameLocation: 'middle' },
        yAxis: { type: 'category', data: sorted.map(s => s.name).reverse(), axisLabel: { fontSize: 11, width: 240, overflow: 'truncate', ellipsis: '...' } },
        series: [{
            type: 'bar',
            data: sorted.map(s => s.value).reverse(),
            itemStyle: {
                color: modelName === '随机森林' ? '#10b981' : '#f97316',
                borderRadius: [0, 4, 4, 0]
            },
            label: { show: true, position: 'right', formatter: function(p) { return p.value.toFixed(4); }, fontSize: 11 }
        }]
    });
}

function renderStrategyTable() {
    const tbody = document.getElementById('strategy-tbody');
    const sr = allData.strategy_results;
    const bestSharpe = Math.max(...Object.values(sr).map(r => r.sharpe_ratio));
    tbody.innerHTML = Object.keys(sr).map(name => {
        const r = sr[name];
        const excess = (r.total_return - r.market_return) * 100;
        return '<tr>' +
            '<td style="font-weight:600;">' + name + '</td>' +
            '<td>' + (r.total_return * 100).toFixed(2) + '%</td>' +
            '<td>' + (r.market_return * 100).toFixed(2) + '%</td>' +
            '<td>' + excess.toFixed(2) + '%</td>' +
            '<td class="' + (r.sharpe_ratio === bestSharpe ? 'best-score' : '') + '">' + r.sharpe_ratio.toFixed(2) + '</td>' +
            '<td>' + (r.max_drawdown * 100).toFixed(2) + '%</td>' +
        '</tr>';
    }).join('');
}

function renderRiskStrategyTable() {
    const tbody = document.getElementById('risk-strategy-tbody');
    const rsr = allData.risk_strategy_results;
    const sr = allData.strategy_results;
    tbody.innerHTML = Object.keys(rsr).map(name => {
        const r = rsr[name];
        const base = sr[name];
        const tag = '<span style="font-size:11px; color:#64748b;">(基础: ' + (base.total_return * 100).toFixed(1) + '%)</span>';
        return '<tr>' +
            '<td style="font-weight:600;">' + name + '</td>' +
            '<td><span style="color:#10b981;">动态仓位</span></td>' +
            '<td>' + (r.total_return * 100).toFixed(2) + '% ' + tag + '</td>' +
            '<td>' + r.sharpe_ratio.toFixed(2) + '</td>' +
            '<td>' + (r.max_drawdown * 100).toFixed(2) + '%</td>' +
            '<td>' + (r.avg_down_prob * 100).toFixed(1) + '%</td>' +
        '</tr>';
    }).join('');
}

// 图3：累计收益率（百分比格式）
function renderCumReturn() {
    const chart = echarts.init(document.getElementById('chart-cum-return'));
    const sr = allData.strategy_results;
    const colors = ['#10b981', '#84cc16', '#3b82f6', '#f97316'];
    const series = Object.keys(sr).map((name, i) => ({
        name: name,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: colors[i] },
        itemStyle: { color: colors[i] },
        // 转为百分比：cumprod值减1再乘100
        data: sr[name].portfolio_cum.map(v => (v - 1) * 100)
    }));
    series.push({
        name: '市场平均',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', width: 2, color: '#94a3b8' },
        itemStyle: { color: '#94a3b8' },
        data: sr['随机森林回归'].market_cum.map(v => (v - 1) * 100)
    });
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let s = params[0].axisValue + '<br/>';
                params.forEach(p => {
                    s += p.marker + p.seriesName + ': ' + p.value.toFixed(2) + '%<br/>';
                });
                return s;
            }
        },
        legend: { bottom: 5 },
        grid: { left: 85, right: 30, top: 20, bottom: 75 },
        xAxis: { type: 'category', data: sr['随机森林回归'].dates, axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
        yAxis: {
            type: 'value',
            name: '累计收益率(%)',
            nameLocation: 'middle',
            nameGap: 55,
            axisLabel: { formatter: '{value}%' }
        },
        series: series
    });
}

function renderDrawdown() {
    const chart = echarts.init(document.getElementById('chart-drawdown'));
    const sr = allData.strategy_results;
    const colors = ['#10b981', '#84cc16', '#3b82f6', '#f97316'];
    const series = Object.keys(sr).map((name, i) => ({
        name: name,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: colors[i] },
        itemStyle: { color: colors[i] },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: colors[i] + '40' }, { offset: 1, color: colors[i] + '05' }]) },
        data: sr[name].drawdown.map(v => v * 100)
    }));
    chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 5 },
        grid: { left: 80, right: 20, top: 20, bottom: 75 },
        xAxis: { type: 'category', data: sr['随机森林回归'].dates, axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
        yAxis: { type: 'value', name: '回撤(%)', nameLocation: 'middle', nameGap: 50 },
        series: series
    });
}

function renderQuarterly() {
    const chart = echarts.init(document.getElementById('chart-quarterly'));
    const qr = allData.quarterly_results;
    const quarters = [...new Set(qr.map(r => r.year_quarter))].sort();
    const models = [...new Set(qr.map(r => r.model))];
    const colors = ['#10b981', '#84cc16', '#3b82f6', '#f97316'];
    const series = models.map((m, i) => ({
        name: m,
        type: 'bar',
        data: quarters.map(q => {
            const r = qr.find(x => x.year_quarter === q && x.model === m);
            return r ? r.return * 100 : 0;
        }),
        itemStyle: { color: colors[i] }
    }));
    chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 5 },
        grid: { left: 80, right: 20, top: 20, bottom: 65 },
        xAxis: { type: 'category', data: quarters, axisLabel: { fontSize: 11 } },
        yAxis: { type: 'value', name: '收益率(%)', nameLocation: 'middle', nameGap: 50 },
        series: series
    });
}

function renderCompareCharts() {
    const sr = allData.strategy_results;
    const models = Object.keys(sr);
    const colors = ['#10b981', '#84cc16', '#3b82f6', '#f97316'];

    const commonGrid = { left: 80, right: 25, top: 25, bottom: 60 };
    const commonXAxis = { type: 'category', data: models, axisLabel: { fontSize: 11, interval: 0, rotate: 15 } };
    const commonYAxisBase = { type: 'value', nameLocation: 'middle', nameGap: 50 };

    const chartReturn = echarts.init(document.getElementById('chart-return-compare'));
    chartReturn.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '收益率(%)' }),
        series: [{ type: 'bar', data: models.map(m => sr[m].total_return * 100), itemStyle: { color: colors }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2); }, fontSize: 10 } }]
    });

    const chartSharpe = echarts.init(document.getElementById('chart-sharpe-compare'));
    chartSharpe.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '夏普比率' }),
        series: [{ type: 'bar', data: models.map(m => sr[m].sharpe_ratio), itemStyle: { color: colors }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2); }, fontSize: 10 } }]
    });

    const chartDD = echarts.init(document.getElementById('chart-dd-compare'));
    chartDD.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '回撤(%)' }),
        series: [{ type: 'bar', data: models.map(m => sr[m].max_drawdown * 100), itemStyle: { color: colors }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2); }, fontSize: 10 } }]
    });

    const chartTrades = echarts.init(document.getElementById('chart-trades-compare'));
    chartTrades.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '平均持仓数' }),
        series: [{ type: 'bar', data: models.map(m => sr[m].avg_trades), itemStyle: { color: colors }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2); }, fontSize: 10 } }]
    });
}

// 图6-8：基础策略 vs 动态仓位策略对比
function renderRiskCompareCharts() {
    const sr = allData.strategy_results;
    const rsr = allData.risk_strategy_results;
    const models = Object.keys(sr);
    const colors = ['#10b981', '#84cc16', '#3b82f6', '#f97316'];

    // 图6：总收益率对比（分组柱状图）
    const chartReturn = echarts.init(document.getElementById('chart-risk-compare-return'));
    chartReturn.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 5 },
        grid: { left: 85, right: 25, top: 20, bottom: 65 },
        xAxis: { type: 'category', data: models, axisLabel: { fontSize: 11, interval: 0, rotate: 15 } },
        yAxis: { type: 'value', name: '总收益率(%)', nameLocation: 'middle', nameGap: 55 },
        series: [
            {
                name: '基础策略',
                type: 'bar',
                data: models.map(m => +(sr[m].total_return * 100).toFixed(2)),
                itemStyle: { color: '#94a3b8' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2) + '%'; } }
            },
            {
                name: '动态仓位',
                type: 'bar',
                data: models.map(m => +(rsr[m].total_return * 100).toFixed(2)),
                itemStyle: { color: '#10b981' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2) + '%'; } }
            }
        ]
    });

    // 图7：夏普比率对比
    const chartSharpe = echarts.init(document.getElementById('chart-risk-compare-sharpe'));
    chartSharpe.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 5 },
        grid: { left: 80, right: 20, top: 20, bottom: 65 },
        xAxis: { type: 'category', data: models, axisLabel: { fontSize: 11, interval: 0, rotate: 15 } },
        yAxis: { type: 'value', name: '夏普比率', nameLocation: 'middle', nameGap: 50 },
        series: [
            {
                name: '基础策略',
                type: 'bar',
                data: models.map(m => +sr[m].sharpe_ratio.toFixed(2)),
                itemStyle: { color: '#94a3b8' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2); } }
            },
            {
                name: '动态仓位',
                type: 'bar',
                data: models.map(m => +rsr[m].sharpe_ratio.toFixed(2)),
                itemStyle: { color: '#3b82f6' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2); } }
            }
        ]
    });

    // 图8：最大回撤对比
    const chartDD = echarts.init(document.getElementById('chart-risk-compare-dd'));
    chartDD.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 5 },
        grid: { left: 80, right: 20, top: 20, bottom: 65 },
        xAxis: { type: 'category', data: models, axisLabel: { fontSize: 11, interval: 0, rotate: 15 } },
        yAxis: { type: 'value', name: '回撤(%)', nameLocation: 'middle', nameGap: 50 },
        series: [
            {
                name: '基础策略',
                type: 'bar',
                data: models.map(m => +(sr[m].max_drawdown * 100).toFixed(2)),
                itemStyle: { color: '#94a3b8' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2) + '%'; } }
            },
            {
                name: '动态仓位',
                type: 'bar',
                data: models.map(m => +(rsr[m].max_drawdown * 100).toFixed(2)),
                itemStyle: { color: '#ef4444' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2) + '%'; } }
            }
        ]
    });
}

// 图9：动态仓位策略累计收益率曲线（百分比格式）
function renderRiskCumReturn() {
    const chart = echarts.init(document.getElementById('chart-risk-cum-return'));
    const rsr = allData.risk_strategy_results;
    const colors = ['#10b981', '#84cc16', '#3b82f6', '#f97316'];
    const series = Object.keys(rsr).map((name, i) => ({
        name: name + '(动态仓位)',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: colors[i] },
        itemStyle: { color: colors[i] },
        data: rsr[name].portfolio_cum.map(v => (v - 1) * 100)
    }));
    series.push({
        name: '市场平均',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', width: 2, color: '#94a3b8' },
        itemStyle: { color: '#94a3b8' },
        data: rsr['随机森林回归'].market_cum.map(v => (v - 1) * 100)
    });
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let s = params[0].axisValue + '<br/>';
                params.forEach(p => {
                    s += p.marker + p.seriesName + ': ' + p.value.toFixed(2) + '%<br/>';
                });
                return s;
            }
        },
        legend: { bottom: 5 },
        grid: { left: 85, right: 30, top: 20, bottom: 75 },
        xAxis: { type: 'category', data: rsr['随机森林回归'].dates, axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
        yAxis: {
            type: 'value',
            name: '累计收益率(%)',
            nameLocation: 'middle',
            nameGap: 55,
            axisLabel: { formatter: '{value}%' }
        },
        series: series
    });
}
</script>

</body>
</html>
'''

with open('AI-quant/project-05-2.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ project-05-2.html 生成完成')
