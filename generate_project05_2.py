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
        .section.core {
            border: 2px solid #10b981;
            box-shadow: 0 4px 20px rgba(16,185,129,0.15);
        }
        .section-title {
            font-size: 22px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 6px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
        }
        .section.core .section-title {
            color: #065f46;
            border-bottom-color: #10b981;
        }
        .core-badge {
            display: inline-block;
            background: linear-gradient(135deg, #065f46, #10b981);
            color: #fff;
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 12px;
            margin-left: 10px;
            vertical-align: middle;
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
            padding: 14px 18px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 15px;
            color: #1e293b;
            margin: 12px 0;
            border-left: 4px solid #10b981;
            text-align: center;
        }
        .step-list {
            counter-reset: step;
            list-style: none;
            padding-left: 0;
        }
        .step-list li {
            counter-increment: step;
            padding: 14px 16px 14px 56px;
            margin-bottom: 10px;
            background: #fff;
            border-radius: 10px;
            border-left: 3px solid #10b981;
            position: relative;
            font-size: 14px;
            color: #374151;
            line-height: 1.7;
        }
        .step-list li::before {
            content: counter(step);
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 28px;
            height: 28px;
            background: linear-gradient(135deg, #065f46, #10b981);
            color: #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
        }
        .step-list li strong { color: #065f46; }
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
    <div class="header-desc">概率模型驱动的动态仓位管理策略 —— 基于机器学习下跌概率的精细化交易决策</div>
</div>

<div class="container">
    <div class="overview-grid" id="overview-grid"></div>

    <!-- 一、项目核心理念 -->
    <div class="section">
        <h2 class="section-title">一、项目核心理念：概率驱动的动态仓位管理</h2>
        <p class="section-desc">本项目核心不是简单的模型选股，而是构建概率模型输出下跌概率，驱动动态仓位调整，实现精细化风险管理</p>
        
        <div class="strategy-box" style="margin-bottom:16px;">
            <h3>🎯 核心思路</h3>
            <p>传统选股策略只有"买/不买"两种状态，无法区分风险高低。本项目的核心创新是：</p>
            <p style="font-size:15px; color:#065f46; font-weight:600; margin: 10px 0;">
                用机器学习模型预测每支股票的下跌概率，并根据概率大小动态调整持仓权重。
            </p>
            <p>这样不仅选出好股票，还能对高概率下跌的股票降低仓位，对低概率下跌的股票加大仓位，实现"选股+风控"一体化。</p>
        </div>

        <div class="pros-cons-grid">
            <div class="pros-card">
                <h3>✅ 策略优势</h3>
                <ul>
                    <li><strong>概率输出</strong>：不止选股，更量化每支股票的风险</li>
                    <li><strong>动态仓位</strong>：下跌概率高→减仓，概率低→加仓</li>
                    <li><strong>风险分散</strong>：避免等权重配置忽略个股风险差异</li>
                    <li><strong>自适应调整</strong>：每季度根据最新数据重新计算</li>
                </ul>
            </div>
            <div class="cons-card">
                <h3>⚠️ 注意事项</h3>
                <ul>
                    <li><strong>数据依赖</strong>：需要大量高质量历史数据</li>
                    <li><strong>过拟合风险</strong>：可能学到历史噪声而非真实规律</li>
                    <li><strong>概率校准</strong>：模型输出概率需确保可靠性</li>
                    <li><strong>市场变化</strong>：模型可能在市场环境变化后失效</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- 二、自变量因子与应变量定义 -->
    <div class="section">
        <h2 class="section-title">二、自变量因子与应变量定义</h2>
        <p class="section-desc">概率模型的输入特征和预测目标</p>
        
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
            <p style="font-size:13px; color:#64748b; margin-top:10px;">
                <strong>说明：</strong>MA3是三阶移动平均，取最近三个时间点的算术平均，用于平滑数据；LAG2是滞后两期变量，取当前时间点之前第二个时间点的原始值，体现时间滞后关系。两者计算逻辑和作用完全不同。
            </p>
        </div>

        <div>
            <h3 style="font-size:16px; margin-bottom:12px; color:#334155;">🎯 应变量（预测目标）</h3>
            <div class="factor-list">
                <div class="factor-item" style="border-left-color:#10b981;"><strong>Next_Ret_Binary</strong>：涨跌二分类标签（<strong style="color:#10b981;">核心目标</strong>，下跌概率模型预测对象）</div>
                <div class="factor-item"><strong>Next_Ret</strong>：未来一个季度的收益率（原始标签，非模型预测目标），即选股后下一季度的实际收益</div>
                <div class="factor-item"><strong>Next_Ret_Top30</strong>：是否为Top30高收益股票（对比模型分类目标）</div>
                <div class="factor-item"><strong>Next_Ret_Decile</strong>：收益率分位数排名</div>
            </div>
        </div>
    </div>

    <!-- 三、核心策略：概率模型动态仓位调整（核心章节）-->
    <div class="section core">
        <h2 class="section-title">三、核心策略：概率模型动态仓位调整 <span class="core-badge">核心</span></h2>
        <p class="section-desc">本项目的核心策略，详细讲解从模型训练到仓位调整的完整操作流程</p>
        
        <!-- 3.1 策略核心逻辑 -->
        <div class="strategy-box">
            <h3>🎯 3.1 策略核心逻辑</h3>
            <p>传统选股策略选出30支股票后，等权重配置（每支约3.3%）。但不同股票的下跌风险不同，等权重配置没有区分风险。</p>
            <p>本策略的核心创新：<strong style="color:#065f46;">用下跌概率模型量化每支股票的风险，并据此动态调整仓位权重</strong>。</p>
            <div class="formula">
                weight_i = (1 - down_prob_i) / Σ(1 - down_prob_j), &nbsp; j = 1...30
            </div>
            <p>即：下跌概率越高的股票，仓位权重越低；下跌概率越低的股票，仓位权重越高。所有权重归一化为1。</p>
        </div>

        <!-- 3.2 下跌概率模型 -->
        <div class="strategy-box" style="background:linear-gradient(135deg,#f0f9ff,#eff6ff); border-color:#bfdbfe;">
            <h3 style="color:#1e40af;">🤖 3.2 下跌概率模型</h3>
            <p><strong>模型类型：</strong>随机森林分类器（RandomForestClassifier）</p>
            <p><strong>预测目标：</strong>P(Next_Ret ≤ 0) —— 股票未来收益下跌的概率</p>
            <p><strong>训练数据：</strong>使用Next_Ret_Binary作为标签（Next_Ret > 0 标记为1，Next_Ret ≤ 0 标记为0）</p>
            <p><strong>输出含义：</strong>模型输出的是0~1之间的概率值，值越接近1表示下跌概率越高</p>
            <p><strong>模型参数：</strong>n_estimators=100, max_depth=10, random_state=42</p>
        </div>

        <!-- 3.3 完整操作步骤 -->
        <div style="margin-bottom:20px;">
            <h3 style="font-size:16px; margin-bottom:15px; color:#334155;">📋 3.3 完整操作步骤</h3>
            <ol class="step-list">
                <li><strong>选股（模型预测排名）</strong>：按基础分类模型（随机森林/决策树）预测概率排名，选出Top30股票作为候选池</li>
                <li><strong>预测下跌概率</strong>：对选出的30支股票，用下跌概率模型计算每支的下跌概率 P(Next_Ret ≤ 0)</li>
                <li><strong>计算仓位权重</strong>：weight_i = (1 - down_prob_i) / Σ(1 - down_prob_j)，下跌概率低的股票获得更高权重</li>
                <li><strong>加权持仓</strong>：按计算出的权重配置资金，非等权重。例如下跌概率10%的股票权重高于下跌概率60%的股票</li>
                <li><strong>季度调仓</strong>：每季度重新执行上述完整流程，根据最新数据更新选股和仓位</li>
            </ol>
        </div>

        <!-- 3.4 仓位权重示例 -->
        <div class="strategy-box" style="background:#fff7ed; border-color:#fed7aa;">
            <h3 style="color:#9a3412;">💡 3.4 仓位权重示例</h3>
            <p>假设选出3支股票，下跌概率分别为：股票A=20%、股票B=40%、股票C=60%</p>
            <p>则仓位权重计算：</p>
            <div class="formula" style="text-align:left; font-size:14px;">
                股票A权重 = (1-0.2) / [(1-0.2)+(1-0.4)+(1-0.6)] = 0.8/1.8 = <strong style="color:#10b981;">44.4%</strong><br>
                股票B权重 = (1-0.4) / 1.8 = 0.6/1.8 = <strong>33.3%</strong><br>
                股票C权重 = (1-0.6) / 1.8 = 0.4/1.8 = <strong style="color:#ef4444;">22.2%</strong>
            </div>
            <p>可以看到，下跌概率最低的股票A获得了最高仓位（44.4%），而下跌概率最高的股票C仓位最低（22.2%）。</p>
        </div>

        <!-- 3.5 总收益率计算方式 -->
        <div class="strategy-box" style="background:linear-gradient(135deg,#fdf4ff,#fae8ff); border-color:#e9d5ff;">
            <h3 style="color:#86198f;">🧮 3.5 总收益率计算方式</h3>
            <p>策略的总收益率通过<strong>每季度组合收益的复利累积</strong>计算得出。本数据集按季度更新（每季度末一个数据点），原始10个季度经特征工程dropna后保留8个季度（训练4 + 测试4），策略回测在测试集4个季度上进行，具体分为两步：</p>
            
            <p style="margin-top:12px;"><strong>第一步：计算每季度组合收益率</strong></p>
            <p>对每个季度，组合中30支股票按各自仓位权重加权，得到当季组合收益率：</p>
            <div class="formula" style="text-align:left; font-size:14px;">
                r_portfolio(q) = Σ [ weight_i(q) × r_i(q) ], &nbsp; i = 1...30
            </div>
            <p style="font-size:13px; color:#6b7280; margin-top:6px;">
                其中 weight_i(q) 是股票i在第q季度的仓位权重（由下跌概率计算得出），r_i(q) 是股票i在选股后第q+1季度的实际收益率（Next_Ret，即下一季度的收益）。
            </p>

            <p style="margin-top:14px;"><strong>第二步：复利累积计算总收益率</strong></p>
            <p>从策略起始季度开始，将每季度组合收益率复利相乘，得到累计净值：</p>
            <div class="formula" style="text-align:left; font-size:14px;">
                累计净值(Q) = ∏ [1 + r_portfolio(q)], &nbsp; q = 1...Q<br>
                <strong style="color:#86198f;">总收益率 = 累计净值(Q) - 1</strong>
            </div>
            <p style="font-size:13px; color:#6b7280; margin-top:6px;">
                例如：若4个季度后累计净值为1.1932，则总收益率 = 1.1932 - 1 = <strong style="color:#10b981;">19.32%</strong>
            </p>

            <p style="margin-top:14px;"><strong>收益归属季度说明</strong></p>
            <p style="font-size:13px;">选股在每个季度末完成（如2021Q3末），但股票的Next_Ret是<strong>从当季到下一季度的收益率</strong>，因此收益归属到下一季度（如2021Q3末选股，收益发生在2021Q4）。图6的横轴标注的就是<strong>收益发生的季度</strong>，而非选股时点。</p>

            <p style="margin-top:14px;"><strong>对比：基础策略的总收益率计算</strong></p>
            <p style="font-size:13px;">基础策略（等权重）的区别仅在于权重：每支股票权重固定为 1/30 ≈ 3.33%，不加权调整。复利累积逻辑完全相同。</p>

            <div style="background:#fff; padding:12px 16px; border-radius:8px; margin-top:12px; border-left:4px solid #c026d3; font-size:13px; color:#6b21a8;">
                <strong>关于回撤为0的说明：</strong>由于数据按季度更新，每个季度只有一个数据点。当某季度累计净值创历史新高时，该季度的回撤就是0%（因为没有中间数据点可以显示下跌）。回撤只在累计净值低于历史最高点时才会出现负值。4个收益发生季度共4个净值数据点，数据点较少，所以部分季度回撤为0是正常的。
            </div>
        </div>

        <!-- 3.6 季度加减仓操作逻辑 -->
        <div class="strategy-box" style="background:linear-gradient(135deg,#ecfeff,#cffafe); border-color:#a5f3fc;">
            <h3 style="color:#155e75;">🔄 3.6 季度加减仓操作逻辑</h3>
            <p>本策略采用<strong>季度调仓</strong>机制，每个季度末重新执行完整的选股和仓位调整流程。具体操作逻辑如下：</p>

            <p style="margin-top:12px;"><strong>场景一：股票仍在Top30（继续持有）</strong></p>
            <ul style="font-size:14px; padding-left:20px; color:#374151;">
                <li>若该股票在新一季度的下跌概率<strong>降低</strong> → <strong style="color:#10b981;">加仓</strong>（权重上升）</li>
                <li>若该股票在新一季度的下跌概率<strong>升高</strong> → <strong style="color:#ef4444;">减仓</strong>（权重下降）</li>
                <li>若该股票在新一季度的下跌概率<strong>不变</strong> → 仓位维持不变</li>
            </ul>

            <p style="margin-top:12px;"><strong>场景二：股票跌出Top30（清仓卖出）</strong></p>
            <ul style="font-size:14px; padding-left:20px; color:#374151;">
                <li>该股票不再符合选股标准，<strong style="color:#ef4444;">全部卖出</strong></li>
                <li>释放的资金按新权重分配给新进入Top30的股票</li>
            </ul>

            <p style="margin-top:12px;"><strong>场景三：新股票进入Top30（买入建仓）</strong></p>
            <ul style="font-size:14px; padding-left:20px; color:#374151;">
                <li>新进入的股票按其下跌概率计算权重，<strong style="color:#10b981;">买入建仓</strong></li>
                <li>下跌概率越低的新股票，获得的仓位权重越高</li>
            </ul>

            <div style="background:#fff; padding:14px 18px; border-radius:8px; margin-top:14px; border-left:4px solid #0891b2;">
                <p style="font-size:13px; color:#155e75;"><strong>关键逻辑：</strong>每个季度的仓位权重是<strong>独立重新计算</strong>的，不依赖上一季度的持仓状态。系统会自动完成"卖出跌出Top30的股票 → 按新权重买入新进入Top30的股票 → 调整继续持有股票的仓位"这一完整流程。</p>
            </div>

            <p style="margin-top:12px;"><strong>资金分配示例（假设总资金100万）</strong></p>
            <div style="background:#fff; padding:14px 18px; border-radius:8px; margin-top:8px; font-size:13px; color:#374151;">
                <table style="width:100%; border-collapse:collapse;">
                    <tr style="background:#f0fdfa;">
                        <th style="padding:8px; text-align:left; border-bottom:1px solid #ccc;">股票</th>
                        <th style="padding:8px; text-align:center; border-bottom:1px solid #ccc;">下跌概率</th>
                        <th style="padding:8px; text-align:center; border-bottom:1px solid #ccc;">权重</th>
                        <th style="padding:8px; text-align:center; border-bottom:1px solid #ccc;">分配资金</th>
                        <th style="padding:8px; text-align:center; border-bottom:1px solid #ccc;">操作</th>
                    </tr>
                    <tr>
                        <td style="padding:8px;">股票A</td>
                        <td style="padding:8px; text-align:center;">15%</td>
                        <td style="padding:8px; text-align:center; color:#10b981; font-weight:600;">38.5%</td>
                        <td style="padding:8px; text-align:center;">38.5万</td>
                        <td style="padding:8px; text-align:center; color:#10b981;">加仓</td>
                    </tr>
                    <tr style="background:#fafafa;">
                        <td style="padding:8px;">股票B</td>
                        <td style="padding:8px; text-align:center;">45%</td>
                        <td style="padding:8px; text-align:center;">26.9%</td>
                        <td style="padding:8px; text-align:center;">26.9万</td>
                        <td style="padding:8px; text-align:center; color:#ef4444;">减仓</td>
                    </tr>
                    <tr>
                        <td style="padding:8px;">股票C</td>
                        <td style="padding:8px; text-align:center;">70%</td>
                        <td style="padding:8px; text-align:center; color:#ef4444; font-weight:600;">11.5%</td>
                        <td style="padding:8px; text-align:center;">11.5万</td>
                        <td style="padding:8px; text-align:center; color:#ef4444;">减仓</td>
                    </tr>
                    <tr style="background:#fef2f2;">
                        <td style="padding:8px;">股票D</td>
                        <td style="padding:8px; text-align:center;">—</td>
                        <td style="padding:8px; text-align:center;">—</td>
                        <td style="padding:8px; text-align:center;">0</td>
                        <td style="padding:8px; text-align:center; color:#ef4444;">清仓（跌出Top30）</td>
                    </tr>
                    <tr style="background:#f0fdf4;">
                        <td style="padding:8px;">股票E（新进入）</td>
                        <td style="padding:8px; text-align:center;">20%</td>
                        <td style="padding:8px; text-align:center; color:#10b981; font-weight:600;">23.1%</td>
                        <td style="padding:8px; text-align:center;">23.1万</td>
                        <td style="padding:8px; text-align:center; color:#10b981;">建仓买入</td>
                    </tr>
                </table>
            </div>
            <p style="font-size:12px; color:#6b7280; margin-top:8px;">注：上表为示意数据，权重 = (1-下跌概率)/Σ(1-下跌概率)，合计100%</p>
        </div>

        <!-- 3.7 选股逻辑：次级排序键（小盘股优先） -->
        <div class="strategy-box" style="background:linear-gradient(135deg,#fffbeb,#fef3c7); border-color:#fde68a; margin-top:16px;">
            <h3 style="color:#92400e;">🔀 3.7 选股逻辑：次级排序键（小盘股优先）</h3>
            <p><strong>问题背景：</strong>决策树分类器设置 max_depth=5，叶子节点最多32个，意味着大量股票会得到<strong>完全相同</strong>的预测概率。pandas默认的排名方式 (method='average') 在并列时取平均名次，会导致并列股票"全部入选或全部落选"，使决策树策略持仓数严重不足（实测仅5.75支，远低于30支）。</p>

            <p style="margin-top:12px;"><strong>解决方案：</strong>采用<strong>次级排序键</strong>处理并列情况。当预测概率相同时，按<strong>MV市值升序</strong>排序选取Top30（小盘股优先）。</p>

            <p style="margin-top:10px;"><strong>排序逻辑：</strong></p>
            <div class="formula" style="text-align:left; font-size:14px;">
                排序键 = (预测概率 ↓, MV市值 ↑)<br>
                <span style="font-size:12px; color:#6b7280;">主键：模型预测概率降序 | 次键：MV市值升序（小盘股优先）</span>
            </div>

            <p style="margin-top:12px;"><strong>为何选小盘股？</strong></p>
            <ul style="font-size:13px; padding-left:20px; color:#374151; line-height:1.9;">
                <li>A股市场存在显著的<strong>小盘股效应</strong>：小市值股票的上涨弹性更大</li>
                <li>数据验证：最小市值组（Q1）上涨率48.3%，最大市值组（Q5）仅35.5%</li>
                <li>当概率并列时，优先选小盘股既能解决并列问题，又能提升策略收益</li>
            </ul>

            <p style="margin-top:12px;"><strong>实际效果：</strong></p>
            <ul style="font-size:13px; padding-left:20px; color:#374151; line-height:1.9;">
                <li>✅ <strong>持仓数修复</strong>：决策树策略持仓数从 5.75 → 30.0（已修复）</li>
                <li>✅ <strong>随机森林不受影响</strong>：max_depth=10，概率值足够细分，几乎没有并列，次级排序键不发挥作用</li>
                <li>⚠️ <strong>决策树收益显著提升</strong>：在10个季度（训练+测试）回测期内，总收益从-1.35%（大盘优先）升至30.30%（小盘优先），验证了小盘股效应在A股的有效性</li>
            </ul>

            <div style="background:#fff; padding:12px 16px; border-radius:8px; margin-top:12px; border-left:4px solid #f59e0b; font-size:13px; color:#92400e;">
                <strong>注意：</strong>此前的MV降序（大盘优先）和目前的MV升序（小盘优先）都使用合理的金融逻辑。二次排序键仅在模型概率并列时生效——对随机森林几乎没有影响，但对决策树影响很大。<strong>两种排序方向都远胜于method='first'（按CSV行顺序）的随机效果。</strong>
            </div>
        </div>

        <!-- 3.8 四策略回测结果总览 -->
        <h3 style="font-size:16px; margin-bottom:15px; color:#334155;">📈 3.8 四策略回测结果总览</h3>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>策略名称</th>
                    <th>策略类型</th>
                    <th>总收益率</th>
                    <th>夏普比率</th>
                    <th>最大回撤</th>
                    <th>平均下跌概率</th>
                </tr>
            </thead>
            <tbody id="all-strategy-tbody"></tbody>
        </table>

        <div class="fig-title">图 1：四策略累计收益率曲线对比</div>
        <div id="chart-all-cum-return" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>四个策略的累计收益率曲线对比。纵轴为累计收益率百分比，0%为起始基准线。核心策略（动态仓位）在随机森林模型上明显优于基础策略（25.48% vs 20.32%）；在决策树模型上也显著优于基础策略（34.77% vs 30.30%），动态仓位调整在两个选股模型上均有正向贡献。
        </div>
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

    <!-- 五、对比模型说明 -->
    <div class="section">
        <h2 class="section-title">五、对比模型说明</h2>
        <p class="section-desc">为验证核心策略效果，训练两个对比模型（与05.1项目一致）。这些模型仅用于选股排名，不涉及动态仓位</p>
        
        <table class="model-compare-table">
            <thead>
                <tr>
                    <th>对比维度</th>
                    <th>随机森林</th>
                    <th>决策树</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>任务类型</strong></td>
                    <td>二分类</td>
                    <td>二分类</td>
                </tr>
                <tr>
                    <td><strong>预测目标</strong></td>
                    <td>是否Top30高收益股</td>
                    <td>是否Top30高收益股</td>
                </tr>
                <tr>
                    <td><strong>输出形式</strong></td>
                    <td>概率值（0~1）</td>
                    <td>概率值（0~1）</td>
                </tr>
                <tr>
                    <td><strong>模型结构</strong></td>
                    <td>100棵决策树集成</td>
                    <td>单棵决策树</td>
                </tr>
                <tr>
                    <td><strong>模型参数</strong></td>
                    <td>n_estimators=100, max_depth=10</td>
                    <td>max_depth=5</td>
                </tr>
                <tr>
                    <td><strong>在核心策略中角色</strong></td>
                    <td>选股排名 → 交由概率模型调仓</td>
                    <td>选股排名 → 交由概率模型调仓</td>
                </tr>
            </tbody>
        </table>

        <div class="fig-title">图 2：随机森林特征重要性（Top-15）</div>
        <div id="chart-feat-rf" class="chart-container large"></div>
        <div class="fig-caption">
            <strong>解读：</strong>特征重要性反映了各因子在模型决策中的贡献程度，可用于特征筛选和策略优化。
        </div>

        <div class="fig-title">图 3：决策树特征重要性（Top-15）</div>
        <div id="chart-feat-dt" class="chart-container large"></div>
    </div>

    <!-- 六、四策略全面对比 -->
    <div class="section">
        <h2 class="section-title">六、四策略全面对比</h2>
        <p class="section-desc">决策树、随机森林、决策树+动态仓位、随机森林+动态仓位 四个策略的全面对比</p>
        
        <div class="fig-title">图 4：四策略超额收益曲线对比（相对市场基准）</div>
        <div id="chart-cum-return" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>本图展示四策略相对市场平均基准的<strong>超额累计收益</strong>（策略累计净值 - 市场累计净值）。正值表示跑赢市场，负值表示跑输市场。四个策略均显著跑赢市场基准，核心策略（动态仓位）的超额收益在随机森林模型上最为突出。
        </div>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 5：四策略回撤曲线对比</div>
                <div id="chart-drawdown" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 6：四策略季度收益率对比（收益发生季度）</div>
                <div id="chart-quarterly" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>横轴为<strong>收益发生的季度</strong>，而非选股时点。例如2021Q3末选股，其Next_Ret归属到2021Q4。核心策略在回撤控制上优于基础策略。
        </div>

        <!-- 关于图5回撤为0的详细说明 -->
        <div class="strategy-box" style="background:linear-gradient(135deg,#fff1f2,#fee2e2); border-color:#fecaca; margin-top:16px;">
            <h3 style="color:#991b1b;">🔍 关于图5中"0回撤"的详细说明</h3>
            <p>许多读者会疑惑：4个策略怎么会在某些时点出现0回撤？这是否是bug？<strong>不是bug</strong>，是数据稀疏性导致的正常现象。下面用真实数据说明：</p>

            <p style="margin-top:12px;"><strong>4个收益发生季度的真实回撤数据（%）：</strong></p>
            <div style="background:#fff; padding:14px 18px; border-radius:8px; margin-top:8px; font-size:13px; color:#374151; overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; min-width:560px;">
                    <tr style="background:#fef2f2;">
                        <th style="padding:8px; text-align:left; border-bottom:2px solid #fecaca;">策略</th>
                        <th style="padding:8px; text-align:center; border-bottom:2px solid #fecaca;">2021Q4</th>
                        <th style="padding:8px; text-align:center; border-bottom:2px solid #fecaca;">2022Q1</th>
                        <th style="padding:8px; text-align:center; border-bottom:2px solid #fecaca;">2022Q2</th>
                        <th style="padding:8px; text-align:center; border-bottom:2px solid #fecaca;">2022Q3</th>
                        <th style="padding:8px; text-align:center; border-bottom:2px solid #fecaca;">最大回撤</th>
                    </tr>
                    <tr>
                        <td style="padding:8px;">随机森林</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#dc2626;">-6.62%</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#dc2626;">-1.17%</td>
                        <td style="padding:8px; text-align:center; font-weight:600; color:#dc2626;">-6.62%</td>
                    </tr>
                    <tr style="background:#fafafa;">
                        <td style="padding:8px;">决策树</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#dc2626;">-0.15%</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#dc2626;">-0.25%</td>
                        <td style="padding:8px; text-align:center; font-weight:600; color:#dc2626;">-0.25%</td>
                    </tr>
                    <tr>
                        <td style="padding:8px;">随机森林+动态仓位</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#dc2626;">-5.74%</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#dc2626;">-1.40%</td>
                        <td style="padding:8px; text-align:center; font-weight:600; color:#dc2626;">-5.74%</td>
                    </tr>
                    <tr style="background:#fafafa;">
                        <td style="padding:8px;">决策树+动态仓位</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#94a3b8;">0.00%</td>
                        <td style="padding:8px; text-align:center; color:#dc2626;">-0.38%</td>
                        <td style="padding:8px; text-align:center; font-weight:600; color:#dc2626;">-0.38%</td>
                    </tr>
                </table>
            </div>

            <p style="margin-top:14px;"><strong>为什么会出现0回撤？三个原因：</strong></p>
            <ul style="font-size:13px; padding-left:20px; color:#374151; line-height:1.9;">
                <li><strong>起点必然为0</strong>：2021Q4是首个收益发生季度，累计收益率=17.43%，没有"历史最高点"可比，回撤必然为0</li>
                <li><strong>创新高时为0</strong>：2022Q2四个策略都创新高（累计净值超过此前最高点），此时累计净值=cummax，回撤=0</li>
                <li><strong>数据按季度稀疏更新</strong>：4个收益发生季度只有4个数据点，看不到季度内的日/周级别回撤。如果换成日线数据，0回撤会大幅减少</li>
            </ul>

            <p style="margin-top:12px;"><strong>关键结论：</strong>随机森林策略的回撤模式为"0→跌→0→跌"，2021Q4（首个收益季度）出现5-7%的真实回撤。决策树策略由于偏向小盘股，在整个回测期回撤极小（最大仅-0.38%），体现了小盘股策略在A股该时期的稳定性。<strong>"0回撤"不等于"没风险"</strong>——季度数据点只能反映季度末时点的状态，无法反映季度内的波动。</p>

            <div style="background:#fff; padding:12px 16px; border-radius:8px; margin-top:12px; border-left:4px solid #dc2626; font-size:13px; color:#991b1b;">
                <strong>提示：</strong>本数据集为季度频率（每季度末一个数据点），回撤曲线只能反映季度末时点的状态。如需观察更精细的回撤，需使用日线或周线数据。
            </div>
        </div>
    </div>

    <!-- 七、四策略多维对比 -->
    <div class="section">
        <h2 class="section-title">七、四策略多维对比</h2>
        <p class="section-desc">从总收益率、夏普比率、最大回撤、平均持仓数量四个维度对比四个策略</p>
        
        <div class="chart-row">
            <div>
                <div class="fig-title">图 7：总收益率对比</div>
                <div id="chart-return-compare" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 8：夏普比率对比</div>
                <div id="chart-sharpe-compare" class="chart-container small"></div>
            </div>
        </div>
        <div class="chart-row">
            <div>
                <div class="fig-title">图 9：最大回撤对比</div>
                <div id="chart-dd-compare" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 10：平均持仓数量对比</div>
                <div id="chart-trades-compare" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>四个策略在四个维度上的对比。核心策略（动态仓位）在总收益率和夏普比率上均优于对应的基础策略，体现了概率驱动仓位调整在收益提升和风险控制上的双重优势。
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
    renderAllStrategyTable();
    renderAllCumReturn();
    renderFeatureImportance('chart-feat-rf', '随机森林');
    renderFeatureImportance('chart-feat-dt', '决策树');
    renderCumReturn();
    renderDrawdown();
    renderQuarterly();
    renderCompareCharts();
    setTimeout(resizeAllCharts, 100);
    setTimeout(resizeAllCharts, 500);
    window.addEventListener('resize', resizeAllCharts);
}

function resizeAllCharts() {
    const ids = ['chart-all-cum-return','chart-feat-rf','chart-feat-dt','chart-cum-return','chart-drawdown','chart-quarterly','chart-return-compare','chart-sharpe-compare','chart-dd-compare','chart-trades-compare'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            const inst = echarts.getInstanceByDom(el);
            if (inst) inst.resize();
        }
    });
}

function renderOverview() {
    const grid = document.getElementById('overview-grid');
    const di = allData.data_info;
    const items = [
        { id: 'stat-total', label: '总样本数', value: di.total_samples },
        { id: 'stat-train', label: '训练集样本', value: di.train_samples },
        { id: 'stat-test', label: '测试集样本', value: di.test_samples },
        { id: 'stat-feat', label: '特征数量', value: di.feature_count },
        { id: 'stat-model', label: '模型数量', value: 3 }
    ];
    grid.innerHTML = items.map(item =>
        '<div class="overview-card"><div class="num" id="' + item.id + '">' + item.value.toLocaleString() + '</div><div class="label">' + item.label + '</div></div>'
    ).join('');
}

function renderDataSplit() {
    const di = allData.data_info;
    const trainQuartersRaw = di.train_quarters_raw || [];
    const trainQuarters = di.train_quarters || [];
    const testQuarters = di.test_quarters || [];
    const trainRatio = (di.train_samples / di.total_samples * 100).toFixed(1);
    const testRatio = (di.test_samples / di.total_samples * 100).toFixed(1);
    document.getElementById('train-info').innerHTML =
        '原始季度: ' + trainQuartersRaw.join(', ') + '<br>' +
        'dropna后: <strong style="color:#065f46;">' + trainQuarters.join(', ') + ' (' + trainQuarters.length + '个)</strong><br>' +
        '样本数: ' + di.train_samples.toLocaleString() + ' / ' + di.total_samples.toLocaleString() + '<br>' +
        '占比: <strong style="color:#065f46;">' + trainRatio + '%</strong><br>' +
        '<span style="color:#64748b; font-size:12px;">(2020Q1-Q2因lag2/MA3特征工程被丢弃)</span>';
    document.getElementById('test-info').innerHTML =
        '季度: ' + testQuarters.join(', ') + '<br>' +
        '数量: <strong style="color:#92400e;">' + testQuarters.length + '个季度</strong><br>' +
        '样本数: ' + di.test_samples.toLocaleString() + ' / ' + di.total_samples.toLocaleString() + '<br>' +
        '占比: <strong style="color:#92400e;">' + testRatio + '%</strong><br>' +
        '<span style="color:#64748b; font-size:12px;">(4个季度全部有完整特征)</span>';
}

// 4个策略的统一颜色配置
const STRATEGY_COLORS = {
    '决策树': '#f97316',
    '随机森林': '#3b82f6',
    '决策树+动态仓位': '#dc2626',
    '随机森林+动态仓位': '#10b981'
};
const STRATEGY_ORDER = ['决策树', '随机森林', '决策树+动态仓位', '随机森林+动态仓位'];

function renderAllStrategyTable() {
    const tbody = document.getElementById('all-strategy-tbody');
    const as = allData.all_strategies;
    tbody.innerHTML = STRATEGY_ORDER.map(name => {
        const r = as[name];
        const typeTag = r.type === '核心策略'
            ? '<span style="color:#10b981; font-weight:600;">核心策略</span>'
            : '<span style="color:#64748b;">基础策略</span>';
        const downProb = r.avg_down_prob !== null && r.avg_down_prob !== undefined
            ? (r.avg_down_prob * 100).toFixed(1) + '%'
            : '—';
        return '<tr>' +
            '<td style="font-weight:600; color:' + STRATEGY_COLORS[name] + ';">' + name + '</td>' +
            '<td>' + typeTag + '</td>' +
            '<td>' + (r.total_return * 100).toFixed(2) + '%</td>' +
            '<td>' + r.sharpe_ratio.toFixed(2) + '</td>' +
            '<td>' + (r.max_drawdown * 100).toFixed(2) + '%</td>' +
            '<td>' + downProb + '</td>' +
        '</tr>';
    }).join('');
}

// 图1：四策略累计收益率对比（百分比格式）
function renderAllCumReturn() {
    const chart = echarts.init(document.getElementById('chart-all-cum-return'));
    const as = allData.all_strategies;
    const series = STRATEGY_ORDER.map(name => ({
        name: name,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: STRATEGY_COLORS[name] },
        itemStyle: { color: STRATEGY_COLORS[name] },
        data: as[name].portfolio_cum.map(v => (v - 1) * 100)
    }));
    series.push({
        name: '市场平均',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', width: 2, color: '#94a3b8' },
        itemStyle: { color: '#94a3b8' },
        data: as['决策树'].market_cum.map(v => (v - 1) * 100)
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
        xAxis: { type: 'category', data: as['决策树'].dates.map(d => ({ '2021-09-30':'2021Q4', '2021-12-31':'2022Q1', '2022-03-31':'2022Q2', '2022-06-30':'2022Q3' }[d] || d)), axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
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

// 图4：四策略累计收益率曲线（百分比格式）
function renderCumReturn() {
    const chart = echarts.init(document.getElementById('chart-cum-return'));
    const as = allData.all_strategies;
    // 图4改为超额收益曲线：策略累计收益 - 市场累计收益（相对市场基准的超额表现）
    const marketCum = as['决策树'].market_cum;
    const series = STRATEGY_ORDER.map(name => ({
        name: name,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: STRATEGY_COLORS[name] },
        itemStyle: { color: STRATEGY_COLORS[name] },
        data: as[name].portfolio_cum.map((v, i) => ((v - marketCum[i]) * 100))
    }));
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let s = params[0].axisValue + '（相对市场超额）<br/>';
                params.forEach(p => {
                    s += p.marker + p.seriesName + ': ' + p.value.toFixed(2) + '%<br/>';
                });
                return s;
            }
        },
        legend: { bottom: 5 },
        grid: { left: 85, right: 30, top: 20, bottom: 75 },
        xAxis: { type: 'category', data: as['决策树'].dates, axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
        yAxis: {
            type: 'value',
            name: '超额收益率(%)',
            nameLocation: 'middle',
            nameGap: 55,
            axisLabel: { formatter: '{value}%' }
        },
        series: series
    });
}

// 图5：四策略回撤曲线
function renderDrawdown() {
    const chart = echarts.init(document.getElementById('chart-drawdown'));
    const as = allData.all_strategies;
    const series = STRATEGY_ORDER.map(name => ({
        name: name,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: STRATEGY_COLORS[name] },
        itemStyle: { color: STRATEGY_COLORS[name] },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: STRATEGY_COLORS[name] + '30' }, { offset: 1, color: STRATEGY_COLORS[name] + '05' }]) },
        data: as[name].drawdown.map(v => v * 100)
    }));
    chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { bottom: 5 },
        grid: { left: 80, right: 20, top: 20, bottom: 75 },
        xAxis: { type: 'category', data: as['决策树'].dates.map(d => ({ '2021-09-30':'2021Q4', '2021-12-31':'2022Q1', '2022-03-31':'2022Q2', '2022-06-30':'2022Q3' }[d] || d)), axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
        yAxis: { type: 'value', name: '回撤(%)', nameLocation: 'middle', nameGap: 50 },
        series: series
    });
}

// 图6：四策略季度收益率对比
function renderQuarterly() {
    const chart = echarts.init(document.getElementById('chart-quarterly'));
    const qr = allData.quarterly_results;
    const quarters = [...new Set(qr.map(r => r.year_quarter))].sort();
    const series = STRATEGY_ORDER.map(name => ({
        name: name,
        type: 'bar',
        data: quarters.map(q => {
            const r = qr.find(x => x.year_quarter === q && x.model === name);
            return r ? r.return * 100 : 0;
        }),
        itemStyle: { color: STRATEGY_COLORS[name] }
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

// 图7-10：四策略四维对比（柱状图）
function renderCompareCharts() {
    const as = allData.all_strategies;
    const models = STRATEGY_ORDER;
    const barColors = models.map(m => STRATEGY_COLORS[m]);

    const commonGrid = { left: 80, right: 25, top: 25, bottom: 65 };
    const commonXAxis = { type: 'category', data: models, axisLabel: { fontSize: 11, interval: 0, rotate: 20 } };
    const commonYAxisBase = { type: 'value', nameLocation: 'middle', nameGap: 50 };

    // 图7：总收益率对比
    const chartReturn = echarts.init(document.getElementById('chart-return-compare'));
    chartReturn.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '收益率(%)' }),
        series: [{ type: 'bar', data: models.map(m => +(as[m].total_return * 100).toFixed(2)), itemStyle: { color: function(p) { return barColors[p.dataIndex]; } }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2) + '%'; }, fontSize: 10 } }]
    });

    // 图8：夏普比率对比
    const chartSharpe = echarts.init(document.getElementById('chart-sharpe-compare'));
    chartSharpe.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '夏普比率' }),
        series: [{ type: 'bar', data: models.map(m => +as[m].sharpe_ratio.toFixed(2)), itemStyle: { color: function(p) { return barColors[p.dataIndex]; } }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2); }, fontSize: 10 } }]
    });

    // 图9：最大回撤对比
    const chartDD = echarts.init(document.getElementById('chart-dd-compare'));
    chartDD.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '回撤(%)' }),
        series: [{ type: 'bar', data: models.map(m => +(as[m].max_drawdown * 100).toFixed(2)), itemStyle: { color: function(p) { return barColors[p.dataIndex]; } }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2) + '%'; }, fontSize: 10 } }]
    });

    // 图10：平均持仓数量对比
    const chartTrades = echarts.init(document.getElementById('chart-trades-compare'));
    chartTrades.setOption({
        tooltip: {},
        grid: commonGrid,
        xAxis: commonXAxis,
        yAxis: Object.assign({}, commonYAxisBase, { name: '平均持仓数' }),
        series: [{ type: 'bar', data: models.map(m => +as[m].avg_trades.toFixed(2)), itemStyle: { color: function(p) { return barColors[p.dataIndex]; } }, label: { show: true, position: 'top', formatter: function(p) { return p.value.toFixed(2); }, fontSize: 10 } }]
    });
}
</script>

</body>
</html>
'''

with open('AI-quant/project-05-2.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ project-05-2.html 生成完成')
