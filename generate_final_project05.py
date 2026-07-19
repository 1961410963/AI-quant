import json

with open('AI-quant/project-05-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_json = json.dumps(data, ensure_ascii=False)

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目05.1 AI交易引擎：机器学习算法与场景应用</title>
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
            background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
            color: #fff;
            padding: 50px 20px 70px;
            text-align: center;
        }
        .breadcrumb {
            font-size: 13px;
            opacity: 0.85;
            margin-bottom: 16px;
        }
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
            background: linear-gradient(135deg, #1e3a8a, #7c3aed);
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
        .chart-container {
            width: 100%;
            height: 420px;
            margin-top: 8px;
        }
        .chart-container.small { height: 340px; }
        .chart-container.large { height: 500px; }
        .chart-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .fig-title {
            font-size: 15px;
            font-weight: 600;
            color: #334155;
            margin: 14px 0 6px;
        }
        .fig-caption {
            font-size: 13px;
            color: #64748b;
            line-height: 1.7;
            padding: 12px 16px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 3px solid #7c3aed;
            margin-bottom: 10px;
        }
        .algo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 18px;
        }
        .algo-card {
            background: #f8fafc;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e2e8f0;
        }
        .algo-card h3 {
            font-size: 16px;
            margin-bottom: 8px;
            color: #1e293b;
        }
        .type-tag {
            display: inline-block;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 12px;
            background: #ede9fe;
            color: #6d28d9;
            font-weight: 500;
            margin-left: 6px;
        }
        .algo-card p { font-size: 13px; color: #475569; margin-bottom: 12px; }
        .algo-pros-cons { display: flex; gap: 12px; }
        .algo-pros-cons > div { flex: 1; font-size: 12px; }
        .pros-title { color: #059669; font-weight: 600; margin-bottom: 4px; }
        .cons-title { color: #dc2626; font-weight: 600; margin-bottom: 4px; }
        .algo-pros-cons ul { list-style: none; padding-left: 0; }
        .algo-pros-cons li { padding: 2px 0; color: #475569; }
        .confusion-matrix {
            display: grid;
            grid-template-columns: auto 1fr 1fr;
            gap: 4px;
            font-size: 13px;
        }
        .cm-cell {
            padding: 14px 10px;
            text-align: center;
            border-radius: 6px;
            font-size: 13px;
        }
        .cm-header { background: #e2e8f0; font-weight: 600; }
        .cm-label { background: #e2e8f0; font-weight: 600; display: flex; align-items: center; justify-content: center; }
        .cm-tp { background: #10b981; color: #fff; font-weight: 600; }
        .cm-fn { background: #f59e0b; color: #fff; font-weight: 600; }
        .cm-fp { background: #f97316; color: #fff; font-weight: 600; }
        .cm-tn { background: #3b82f6; color: #fff; font-weight: 600; }
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
        .step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
        }
        .step-card {
            color: #fff;
            padding: 18px;
            border-radius: 12px;
            text-align: center;
        }
        .step-card .num { font-size: 26px; font-weight: 700; margin-bottom: 4px; }
        .step-card .label { font-size: 14px; }
        .warn-box {
            margin-top: 20px;
            padding: 16px 20px;
            background: #fef3c7;
            border-radius: 10px;
            border-left: 4px solid #f59e0b;
            font-size: 14px;
            color: #92400e;
        }
        .info-box {
            padding: 16px 20px;
            border-radius: 10px;
            font-size: 14px;
            line-height: 1.8;
        }
        .info-box.blue { background: #f0f9ff; border-left: 4px solid #3b82f6; color: #1e40af; }
        .info-box.green { background: #f0fdf4; border-left: 4px solid #10b981; color: #065f46; }
        .footer {
            text-align: center;
            padding: 30px 20px;
            color: #94a3b8;
            font-size: 13px;
        }
        .footer a { color: #6366f1; text-decoration: none; }
        @media (max-width: 768px) {
            .chart-row { grid-template-columns: 1fr; }
            .header-title { font-size: 24px; }
            .section { padding: 20px; }
        }
    </style>
</head>
<body>

<div class="page-header">
    <div class="breadcrumb"><a href="index.html">← 返回首页</a></div>
    <div class="header-title">项目05.1 · AI交易引擎</div>
    <div class="header-desc">机器学习算法与场景应用 —— 基于scikit-learn的股票收益二分类模型训练与评估</div>
</div>

<div class="container">

    <!-- 概览卡片 -->
    <div class="overview-grid" id="overview-grid"></div>

    <!-- 一、完整实战流程 -->
    <div class="section">
        <h2 class="section-title">一、完整实战流程</h2>
        <p class="section-desc">机器学习在量化交易中的标准9步工作流，涵盖从数据准备到结果保存的全流程</p>
        <div class="step-grid">
            <div class="step-card" style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);"><div class="num">01</div><div class="label">准备数据</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#3b82f6,#06b6d4);"><div class="num">02</div><div class="label">构造标签</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#06b6d4,#10b981);"><div class="num">03</div><div class="label">选择特征</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#10b981,#84cc16);"><div class="num">04</div><div class="label">时间序列划分</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#84cc16,#eab308);"><div class="num">05</div><div class="label">训练模型</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#eab308,#f97316);"><div class="num">06</div><div class="label">预测</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#f97316,#ef4444);"><div class="num">07</div><div class="label">评估</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#ef4444,#ec4899);"><div class="num">08</div><div class="label">特征重要性</div></div>
            <div class="step-card" style="background:linear-gradient(135deg,#ec4899,#7c3aed);"><div class="num">09</div><div class="label">保存结果</div></div>
        </div>
        <div class="warn-box">
            <strong>⚠️ 关键注意：</strong>
            金融时间序列数据不能随机打乱划分，必须按时间顺序切分，否则会产生"未来函数"（用未来数据预测过去），导致模型表现被严重高估。本实验严格按日期排序后取前70%为训练集、后30%为测试集。
        </div>
    </div>

    <!-- 二、分类型机器学习算法 -->
    <div class="section">
        <h2 class="section-title">二、分类型机器学习算法</h2>
        <p class="section-desc">本项目使用三种经典分类算法进行对比实验，遵循"先简单后复杂"的策略逐步提升</p>
        <div class="algo-grid">
            <div class="algo-card">
                <h3>逻辑回归 <span class="type-tag">线性分类</span></h3>
                <p>通过Sigmoid函数将线性输出转换为0~1概率值，用于二分类。可解释性强，训练速度快，通常作为基线模型。</p>
                <div class="algo-pros-cons">
                    <div>
                        <div class="pros-title">✓ 优点</div>
                        <ul>
                            <li>输出概率，便于设阈值</li>
                            <li>训练快速</li>
                            <li>可解释性好</li>
                        </ul>
                    </div>
                    <div>
                        <div class="cons-title">✗ 缺点</div>
                        <ul>
                            <li>只能处理线性可分</li>
                            <li>对特征尺度敏感</li>
                            <li>需标准化</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="algo-card">
                <h3>决策树 <span class="type-tag">非线性</span></h3>
                <p>通过一系列if-else规则递归分裂样本，形成树状结构。可解释性强，能捕捉非线性关系，但单棵树不稳定。</p>
                <div class="algo-pros-cons">
                    <div>
                        <div class="pros-title">✓ 优点</div>
                        <ul>
                            <li>可解释性强可可视化</li>
                            <li>捕捉非线性关系</li>
                            <li>不需标准化</li>
                        </ul>
                    </div>
                    <div>
                        <div class="cons-title">✗ 缺点</div>
                        <ul>
                            <li>容易过拟合</li>
                            <li>对数据变化敏感</li>
                            <li>单棵树不稳定</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="algo-card">
                <h3>随机森林 <span class="type-tag">集成学习</span></h3>
                <p>多棵决策树通过Bagging集成，样本随机+特征随机，最后投票/平均输出。准确率高，泛化能力强，是本项目的主力模型。</p>
                <div class="algo-pros-cons">
                    <div>
                        <div class="pros-title">✓ 优点</div>
                        <ul>
                            <li>准确率高</li>
                            <li>泛化能力强</li>
                            <li>能处理高维数据</li>
                        </ul>
                    </div>
                    <div>
                        <div class="cons-title">✗ 缺点</div>
                        <ul>
                            <li>训练预测较慢</li>
                            <li>模型占内存大</li>
                            <li>可解释性差（黑盒）</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 三、模型评价指标 -->
    <div class="section">
        <h2 class="section-title">三、模型评价指标</h2>
        <p class="section-desc">混淆矩阵、ROC曲线与AUC是分类模型最核心的评估工具</p>
        <div class="chart-row">
            <div>
                <h3 style="font-size:16px; margin-bottom:12px; color:#334155;">混淆矩阵示意</h3>
                <div class="confusion-matrix">
                    <div class="cm-cell"></div>
                    <div class="cm-cell cm-header">预测: 涨(1)</div>
                    <div class="cm-cell cm-header">预测: 跌(0)</div>
                    <div class="cm-cell cm-label">实际: 涨(1)</div>
                    <div class="cm-cell cm-tp">真正例<br>（实际涨·预测涨）</div>
                    <div class="cm-cell cm-fn">假反例<br>（实际涨·预测跌）</div>
                    <div class="cm-cell cm-label">实际: 跌(0)</div>
                    <div class="cm-cell cm-fp">假正例<br>（实际跌·预测涨）</div>
                    <div class="cm-cell cm-tn">真反例<br>（实际跌·预测跌）</div>
                </div>
            </div>
            <div>
                <h3 style="font-size:16px; margin-bottom:12px; color:#334155;">指标计算公式</h3>
                <div style="background:#f8fafc; border-radius:10px; padding:18px; font-size:13.5px;">
                    <p style="margin-bottom:8px;"><strong>准确率</strong> = (真正例+真反例) / 总数</p>
                    <p style="margin-bottom:8px;"><strong>精确率</strong> = 真正例 / (真正例+假正例)</p>
                    <p style="margin-bottom:8px;"><strong>召回率</strong> = 真正例 / (真正例+假反例)</p>
                    <p style="margin-bottom:8px;"><strong>F1分数</strong> = 2 × 精确率 × 召回率 / (精确率+召回率)</p>
                    <p style="margin-bottom:8px;"><strong>真阳性率</strong> = 真正例 / (真正例+假反例)（ROC纵轴）</p>
                    <p><strong>假阳性率</strong> = 假正例 / (假正例+真反例)（ROC横轴）</p>
                </div>
            </div>
        </div>

        <div class="chart-row" style="margin-top:20px;">
            <div class="info-box blue">
                <h3 style="font-size:15px; margin-bottom:10px;">📖 什么是 ROC 曲线？</h3>
                <p style="font-size:13.5px; line-height:1.9;">
                    <strong>ROC（受试者工作特征曲线）</strong>是评估二分类模型性能的经典图形工具。
                    横轴是<strong>假阳性率</strong>（把跌误判为涨的比例），纵轴是<strong>真阳性率</strong>（把涨正确判为涨的比例）。
                    通过从低到高调整分类阈值，得到一系列(FPR, TPR)坐标点并连成曲线。
                    曲线越靠左上角，说明模型在较低误报率下能获得较高的命中率，性能越好。
                </p>
            </div>
            <div class="info-box green">
                <h3 style="font-size:15px; margin-bottom:10px;">📖 什么是 AUC？</h3>
                <p style="font-size:13.5px; line-height:1.9;">
                    <strong>AUC（ROC曲线下面积）</strong>即ROC曲线下方与横轴围成的面积，取值0~1。
                    AUC越大模型整体排序能力越强。通俗理解：AUC表示"随机抽取一个正样本和一个负样本，模型给正样本打高分的概率"。
                    <br>• AUC = 1：完美分类
                    <br>• AUC > 0.8：模型良好
                    <br>• AUC > 0.7：模型有效
                    <br>• AUC = 0.5：随机猜测，完全无效
                </p>
            </div>
        </div>
    </div>

    <!-- 四、数据分布 -->
    <div class="section">
        <h2 class="section-title">四、数据分布</h2>
        <p class="section-desc">目标变量涨跌标签分布与训练集/测试集时间划分</p>

        <div class="fig-title">图 1：目标变量（涨/跌）分布</div>
        <div id="chart-label-dist" class="chart-container small"></div>
        <div class="fig-caption">
            <strong>解读：</strong>数据集中跌(0)样本约12,383个（占59.6%），涨(1)样本约8,389个（占40.4%），类别存在一定不平衡。
            这意味着不能仅看准确率来判断模型好坏——如果模型全部预测"跌"，也能达到约60%的准确率，但实际没有任何预测能力。
            因此需要重点关注精确率、召回率和AUC等指标。
        </div>

        <div class="fig-title">图 2：数据集时间划分</div>
        <div id="chart-data-split" class="chart-container small"></div>
        <div class="fig-caption">
            <strong>解读：</strong>按时间顺序将数据划分为训练集（前70%，14,540个样本，2021-06-30 至 2022-03-31）和测试集（后30%，6,232个样本，2022-03-31 至 2022-06-30）。
            严格遵循金融时间序列数据的划分原则——只用过去的数据训练模型，用未来的数据检验效果，避免未来函数导致的结果虚高。
        </div>
    </div>

    <!-- 五、逻辑回归模型结果 -->
    <div class="section">
        <h2 class="section-title">五、逻辑回归模型结果</h2>
        <p class="section-desc">逻辑回归是最简单的线性分类模型，作为基线模型使用，便于评估更复杂模型的提升效果</p>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 3：逻辑回归混淆矩阵</div>
                <div id="chart-lr-confusion" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 4：逻辑回归评估指标</div>
                <div id="chart-lr-metrics" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>逻辑回归的准确率为70.3%，但AUC仅0.509，几乎等同于随机猜测。这说明虽然准确率看起来不错，
            但主要是因为类别不平衡（跌的样本多）带来的"虚高"——模型倾向于把大多数样本都预测为"跌"。
            召回率仅7.4%，说明模型几乎没能把真正上涨的样本识别出来。这符合逻辑回归作为线性模型在复杂金融数据上的局限性。
        </div>

        <div class="fig-title" style="margin-top:24px;">图 5：逻辑回归 Top-15 特征系数</div>
        <div id="chart-lr-coef" class="chart-container large"></div>
        <div class="fig-caption">
            <strong>解读：</strong>特征系数的正负表示该特征对上涨概率的影响方向，绝对值越大表示影响越强。
            绿色（正向系数）会提高上涨概率，红色（负向系数）会降低上涨概率。
            三个用户重点关注的负向系数均有明确的金融逻辑：<br>
            • <strong>MV（市值）负系数</strong>：A股市场存在显著的小盘股效应，市值越小越容易上涨（Q1最小市值组上涨率48.3%，Q5最大市值组仅35.5%）<br>
            • <strong>市净率PB(MRQ)负系数</strong>：PB越低（估值越低）的股票反而更有上涨空间（Q1最低PB组上涨率45.4%，Q5最高PB组仅35.6%），符合低估值策略逻辑<br>
            • <strong>市现率PCF负系数</strong>：PCF越高（现金流估值越贵）上涨概率越低，逻辑与PB一致
            但需注意整体AUC很低（约0.55），这些系数的统计显著性有限。
        </div>
    </div>

    <!-- 六、决策树模型结果 -->
    <div class="section">
        <h2 class="section-title">六、决策树模型结果</h2>
        <p class="section-desc">决策树通过if-else规则分裂样本，能捕捉非线性关系，但容易过拟合</p>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 6：决策树混淆矩阵</div>
                <div id="chart-dt-confusion" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 7：决策树评估指标</div>
                <div id="chart-dt-metrics" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>决策树的准确率为59.0%，低于逻辑回归，但AUC为0.550，优于逻辑回归。
            召回率达到40.4%，说明决策树能识别出更多上涨的样本，但代价是精确率较低（30.7%）——误报较多。
            这体现了非线性模型在捕捉复杂模式上的优势，也反映了单棵决策树的不稳定性。
            模型参数设置：max_depth=5，min_samples_split=50，min_samples_leaf=20，用于控制过拟合。
        </div>
        <div style="margin-top:16px; padding:16px 20px; background:#f0f9ff; border-radius:10px; border-left:4px solid #3b82f6; font-size:14px; color:#1e40af;">
            <strong>📌 模型参数：</strong>
            max_depth=5（最大深度，限制树的生长）· min_samples_split=50（节点分裂最小样本数）· min_samples_leaf=20（叶子节点最小样本数）
        </div>
    </div>

    <!-- 七、随机森林模型结果 -->
    <div class="section">
        <h2 class="section-title">七、随机森林模型结果</h2>
        <p class="section-desc">随机森林是多棵决策树的集成模型，通过Bagging降低方差，是本项目表现最佳的模型</p>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 8：随机森林混淆矩阵</div>
                <div id="chart-rf-confusion" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 9：随机森林评估指标</div>
                <div id="chart-rf-metrics" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>随机森林的AUC为0.581，是三个模型中最高的，说明其整体排序能力最强。
            准确率64.8%，精确率35.5%，召回率35.7%，F1分数35.6%，各项指标较为均衡。
            相比单棵决策树，随机森林通过"多棵树投票"的方式有效降低了过拟合风险，提升了模型的稳定性和泛化能力。
            但AUC仅0.58，说明仅用当前这些财务指标预测短期涨跌的效果仍然有限，金融市场的噪声很大。
        </div>

        <div class="fig-title" style="margin-top:24px;">图 10：随机森林 Top-15 特征重要性</div>
        <div id="chart-feat-importance" class="chart-container large"></div>
        <div class="fig-caption">
            <strong>解读：</strong>特征重要性反映了各个财务指标在随机森林模型中对预测涨跌的贡献程度。
            排名靠前的特征对模型的决策影响最大，可用于特征筛选和业务解读。
            可以看到，排名前几位的特征通常与盈利能力、估值水平、成长能力等核心财务维度相关。
            特征重要性是树模型的重要输出，帮助我们理解"模型到底在用什么信息做决策"。
        </div>
        <div style="margin-top:16px; padding:16px 20px; background:#f0fdf4; border-radius:10px; border-left:4px solid #10b981; font-size:14px; color:#065f46;">
            <strong>📌 模型参数：</strong>
            n_estimators=100（决策树数量）· max_depth=10（最大深度）· random_state=42（随机种子，保证可复现）
        </div>
    </div>

    <!-- 八、三模型综合对比 -->
    <div class="section">
        <h2 class="section-title">八、三模型综合对比</h2>
        <p class="section-desc">三个模型在测试集上的性能横向对比，全面评估各模型优劣</p>

        <table class="metrics-table" id="metrics-table">
            <thead>
                <tr>
                    <th>模型</th>
                    <th>准确率</th>
                    <th>精确率</th>
                    <th>召回率</th>
                    <th>F1分数</th>
                    <th>ROC-AUC</th>
                </tr>
            </thead>
            <tbody id="metrics-tbody"></tbody>
        </table>

        <div class="fig-title">图 11：模型性能雷达图对比</div>
        <div id="chart-model-compare" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>雷达图从五个维度同时对比三个模型的性能。面积越大表示综合性能越好。
            可以看到随机森林在大多数指标上都领先，是三个模型中综合表现最好的。
            逻辑回归虽然准确率不低，但AUC和召回率很低，实际预测能力有限。
            决策树在召回率上表现不错，但精确率和准确率偏低。
            整体而言，三个模型的AUC都不高（0.51~0.58），说明仅用财务指标预测短期股价涨跌是一个非常困难的任务。
        </div>

        <div class="fig-title" style="margin-top:20px;">图 12：三模型 ROC 曲线对比</div>
        <div id="chart-roc" class="chart-container large"></div>
        <div class="fig-caption">
            <strong>解读：</strong>ROC曲线展示了三个模型在不同阈值下的假阳性率与真阳性率权衡。
            随机森林的曲线最靠上（AUC=0.581），说明其整体排序能力最强；
            决策树次之（AUC=0.550）；
            逻辑回归几乎贴近对角线（AUC=0.509），接近随机猜测水平。
            右侧色条为AUC评分等级参考，可以直观对照当前模型所处的性能区间。
            三个模型的AUC均低于0.7，说明仅用财务指标预测短期涨跌的效果有限，真实交易中还需结合技术指标、市场情绪等多维度信息。
        </div>
    </div>

</div>

<div class="footer">
    <p>© 2026 北大光华AI量化交易课程 · 项目05.1</p>
    <p style="margin-top:6px;">
        <a href="https://github.com/1961410963/AI-quant" target="_blank">GitHub仓库</a>
    </p>
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
    document.getElementById('stat-total').textContent = allData.date_range.total_samples.toLocaleString();
    document.getElementById('stat-train').textContent = allData.date_range.train_samples.toLocaleString();
    document.getElementById('stat-test').textContent = allData.date_range.test_samples.toLocaleString();
    document.getElementById('stat-feat').textContent = allData.feature_cols.length;
    document.getElementById('stat-model').textContent = allData.model_results.length;

    renderLabelDist();
    renderDataSplit();
    renderConfusion('chart-lr-confusion', '逻辑回归');
    renderMetricsBar('chart-lr-metrics', '逻辑回归');
    renderLRCoef();
    renderConfusion('chart-dt-confusion', '决策树');
    renderMetricsBar('chart-dt-metrics', '决策树');
    renderConfusion('chart-rf-confusion', '随机森林');
    renderMetricsBar('chart-rf-metrics', '随机森林');
    renderFeatureImportance();
    renderMetricsTable();
    renderModelCompare();
    renderROC();

    window.addEventListener('resize', function() {
        const charts = document.querySelectorAll('[id^="chart-"]');
        charts.forEach(el => {
            const inst = echarts.getInstanceByDom(el);
            if (inst) inst.resize();
        });
    });
}

// 概览卡片
(function renderOverview() {
    const grid = document.getElementById('overview-grid');
    const items = [
        { id: 'stat-total', label: '总样本数' },
        { id: 'stat-train', label: '训练集样本' },
        { id: 'stat-test', label: '测试集样本' },
        { id: 'stat-feat', label: '特征数量' },
        { id: 'stat-model', label: '对比模型数' }
    ];
    grid.innerHTML = items.map(item =>
        '<div class="overview-card"><div class="num" id="' + item.id + '">--</div><div class="label">' + item.label + '</div></div>'
    ).join('');
})();

function renderLabelDist() {
    const chart = echarts.init(document.getElementById('chart-label-dist'));
    const data = allData.label_distribution;
    chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 5 },
        series: [{
            type: 'pie',
            radius: ['42%', '70%'],
            center: ['50%', '45%'],
            itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
            label: { show: true, formatter: '{b}\n{d}%', fontSize: 12 },
            data: [
                { value: data['1'], name: '涨(1)', itemStyle: { color: '#10b981' } },
                { value: data['0'], name: '跌(0)', itemStyle: { color: '#ef4444' } }
            ]
        }]
    });
}

function renderDataSplit() {
    const chart = echarts.init(document.getElementById('chart-data-split'));
    const dr = allData.date_range;
    chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 60, right: 20, top: 20, bottom: 40 },
        xAxis: {
            type: 'category',
            data: ['训练集 (70%)', '测试集 (30%)'],
            axisLabel: { fontSize: 12 }
        },
        yAxis: { type: 'value', name: '样本数', nameGap: 10 },
        series: [{
            type: 'bar',
            barWidth: '50%',
            data: [
                { value: dr.train_samples, itemStyle: { color: '#7c3aed' } },
                { value: dr.test_samples, itemStyle: { color: '#f97316' } }
            ],
            label: { show: true, position: 'top', formatter: '{c}', fontSize: 12 }
        }]
    });
}

function renderMetricsTable() {
    const tbody = document.getElementById('metrics-tbody');
    const results = allData.model_results;
    const bestAUC = Math.max(...results.map(r => r.auc));
    tbody.innerHTML = results.map(r =>
        '<tr>' +
            '<td style="font-weight:600;">' + r.model + '</td>' +
            '<td>' + r.accuracy.toFixed(4) + '</td>' +
            '<td>' + r.precision.toFixed(4) + '</td>' +
            '<td>' + r.recall.toFixed(4) + '</td>' +
            '<td>' + r.f1.toFixed(4) + '</td>' +
            '<td class="' + (r.auc === bestAUC ? 'best-score' : '') + '">' + r.auc.toFixed(4) + '</td>' +
        '</tr>'
    ).join('');
}

function renderModelCompare() {
    const chart = echarts.init(document.getElementById('chart-model-compare'));
    const results = allData.model_results;
    const indicators = [
        { name: '准确率', max: 1 },
        { name: '精确率', max: 1 },
        { name: '召回率', max: 1 },
        { name: 'F1分数', max: 1 },
        { name: 'ROC-AUC', max: 1 }
    ];
    const colors = ['#7c3aed', '#f97316', '#10b981'];
    chart.setOption({
        tooltip: {},
        legend: { bottom: 5, data: results.map(r => r.model) },
        radar: {
            indicator: indicators,
            center: ['50%', '52%'],
            radius: '62%',
            splitArea: { areaStyle: { color: ['#f8fafc', '#f1f5f9'] } }
        },
        series: [{
            type: 'radar',
            data: results.map((r, i) => ({
                value: [r.accuracy, r.precision, r.recall, r.f1, r.auc],
                name: r.model,
                itemStyle: { color: colors[i] },
                areaStyle: { opacity: 0.18 },
                lineStyle: { width: 2 }
            }))
        }]
    });
}

function renderROC() {
    const chart = echarts.init(document.getElementById('chart-roc'));
    const roc = allData.roc_curves;
    const colors = ['#7c3aed', '#f97316', '#10b981'];

    // 生成统一的FPR采样点（0~1均匀分布，200个点），确保4条曲线x轴对齐
    const uniformFpr = [];
    for (let i = 0; i <= 200; i++) {
        uniformFpr.push(i / 200);
    }

    // 对单条ROC曲线做线性插值，得到统一FPR采样点上的TPR值
    function interpolateROC(fprArr, tprArr, targetFpr) {
        const result = [];
        let j = 0;
        for (let i = 0; i < targetFpr.length; i++) {
            const x = targetFpr[i];
            while (j < fprArr.length - 1 && fprArr[j + 1] < x) j++;
            if (j >= fprArr.length - 1) {
                result.push(tprArr[tprArr.length - 1]);
            } else if (x <= fprArr[j]) {
                result.push(tprArr[j]);
            } else {
                const ratio = (x - fprArr[j]) / (fprArr[j + 1] - fprArr[j]);
                result.push(tprArr[j] + ratio * (tprArr[j + 1] - tprArr[j]));
            }
        }
        return result;
    }

    const series = Object.keys(roc).map((name, i) => {
        const tprInterp = interpolateROC(roc[name].fpr, roc[name].tpr, uniformFpr);
        const data = uniformFpr.map((fpr, idx) => [fpr, tprInterp[idx]]);
        return {
            name: name + ' (AUC=' + roc[name].auc.toFixed(4) + ')',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 0,
            showSymbol: false,
            itemStyle: { color: colors[i] },
            lineStyle: { width: 3, color: colors[i] },
            data: data
        };
    });

    // 随机猜测对角线也用统一采样点
    series.push({
        name: '随机猜测 (AUC=0.5)',
        type: 'line',
        symbol: 'none',
        itemStyle: { color: '#94a3b8' },
        lineStyle: { type: 'dashed', color: '#94a3b8', width: 1 },
        data: uniformFpr.map(x => [x, x])
    });

    chart.setOption({
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            formatter: function(params) {
                let result = '<b>假阳性率: ' + params[0].value[0].toFixed(4) + '</b><br/>';
                params.forEach(function(p) {
                    result += '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:' + p.color + ';margin-right:6px;"></span>' + p.seriesName + ': <b>真阳性率=' + p.value[1].toFixed(4) + '</b><br/>';
                });
                return result;
            }
        },
        legend: { bottom: 5 },
        grid: { left: 70, right: 30, top: 20, bottom: 60 },
        xAxis: { type: 'value', name: '假阳性率', nameLocation: 'middle', nameGap: 28, min: 0, max: 1 },
        yAxis: { type: 'value', name: '真阳性率', nameLocation: 'middle', nameGap: 40, min: 0, max: 1 },
        series: series
    });
}

function renderConfusion(chartId, modelName) {
    const chart = echarts.init(document.getElementById(chartId));
    const cm = allData.confusion_matrices[modelName];
    const data = [];
    for (let i = 0; i < 2; i++) {
        for (let j = 0; j < 2; j++) {
            data.push([j, i, cm[i][j]]);
        }
    }
    chart.setOption({
        tooltip: {
            position: 'top',
            formatter: function(p) {
                const labels = [['真反例（实际跌·预测跌）', '假正例（实际跌·预测涨）'], ['假反例（实际涨·预测跌）', '真正例（实际涨·预测涨）']];
                return labels[p.value[1]][p.value[0]] + ': ' + p.value[2];
            }
        },
        grid: { left: 85, right: 15, top: 15, bottom: 30 },
        xAxis: {
            type: 'category',
            data: ['预测: 跌(0)', '预测: 涨(1)'],
            splitArea: { show: true },
            axisLabel: { fontSize: 11 }
        },
        yAxis: {
            type: 'category',
            data: ['实际: 跌(0)', '实际: 涨(1)'],
            splitArea: { show: true },
            axisLabel: { fontSize: 11 }
        },
        visualMap: {
            show: false,
            min: 0,
            max: Math.max.apply(null, cm.flat()),
            inRange: { color: ['#dbeafe', '#1e40af'] }
        },
        series: [{
            type: 'heatmap',
            data: data,
            label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#fff' },
            emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
        }]
    });
}

function renderMetricsBar(chartId, modelName) {
    const result = allData.model_results.find(function(r) { return r.model === modelName; });
    const chart = echarts.init(document.getElementById(chartId));
    const items = [
        { name: '准确率', value: result.accuracy },
        { name: '精确率', value: result.precision },
        { name: '召回率', value: result.recall },
        { name: 'F1分数', value: result.f1 },
        { name: 'ROC-AUC', value: result.auc }
    ];
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 85, right: 30, top: 15, bottom: 20 },
        xAxis: { type: 'value', max: 1, axisLabel: { fontSize: 10 } },
        yAxis: {
            type: 'category',
            data: items.map(function(i) { return i.name; }).reverse(),
            axisLabel: { fontSize: 12 }
        },
        series: [{
            type: 'bar',
            data: items.map(function(i) { return i.value; }).reverse(),
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#7c3aed' },
                    { offset: 1, color: '#a78bfa' }
                ]),
                borderRadius: [0, 4, 4, 0]
            },
            label: { show: true, position: 'right', formatter: function(p) { return p.value.toFixed(3); }, fontSize: 11 }
        }]
    });
}

function renderFeatureImportance() {
    const chart = echarts.init(document.getElementById('chart-feat-importance'));
    const fi = allData.feature_importance;
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 170, right: 40, top: 10, bottom: 25 },
        xAxis: { type: 'value', name: '特征重要性', nameGap: 10 },
        yAxis: {
            type: 'category',
            data: fi.features.slice().reverse(),
            axisLabel: { fontSize: 11 }
        },
        series: [{
            type: 'bar',
            data: fi.values.slice().reverse(),
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#10b981' },
                    { offset: 1, color: '#059669' }
                ]),
                borderRadius: [0, 4, 4, 0]
            },
            label: { show: true, position: 'right', formatter: '{c}', fontSize: 11 }
        }]
    });
}

function renderLRCoef() {
    const chart = echarts.init(document.getElementById('chart-lr-coef'));
    const lr = allData.lr_coefficients;
    const features = lr.features.slice().reverse();
    const values = lr.values.slice().reverse();
    const colors = values.map(function(v) { return v > 0 ? '#10b981' : '#ef4444'; });

    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 170, right: 40, top: 10, bottom: 25 },
        xAxis: { type: 'value', name: '回归系数', nameGap: 10 },
        yAxis: {
            type: 'category',
            data: features,
            axisLabel: { fontSize: 11 }
        },
        series: [{
            type: 'bar',
            data: values.map(function(v, i) {
                return {
                    value: v,
                    itemStyle: { color: colors[i], borderRadius: v > 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] }
                };
            }),
            label: { show: true, position: 'right', formatter: '{c}', fontSize: 11 }
        }]
    });
}
</script>

</body>
</html>
'''

with open('AI-quant/project-05.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ project-05.html 生成完成')
print(f'   文件大小: {len(html):,} 字节')
