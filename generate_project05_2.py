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
                <div class="factor-item"><strong>Next_Ret</strong>：未来收益率（原始标签，非模型预测目标）</div>
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
            <p>策略的总收益率通过<strong>每日组合收益的复利累积</strong>计算得出，具体分为两步：</p>
            
            <p style="margin-top:12px;"><strong>第一步：计算每日组合收益率</strong></p>
            <p>对每个交易日，组合中30支股票按各自仓位权重加权，得到当日组合收益率：</p>
            <div class="formula" style="text-align:left; font-size:14px;">
                r_portfolio(t) = Σ [ weight_i(t) × r_i(t) ], &nbsp; i = 1...30
            </div>
            <p style="font-size:13px; color:#6b7280; margin-top:6px;">
                其中 weight_i(t) 是股票i在第t日的仓位权重（由下跌概率计算得出），r_i(t) 是股票i在第t日的收益率。
            </p>

            <p style="margin-top:14px;"><strong>第二步：复利累积计算总收益率</strong></p>
            <p>从策略起始日开始，将每日组合收益率复利相乘，得到累计净值：</p>
            <div class="formula" style="text-align:left; font-size:14px;">
                累计净值(T) = ∏ [1 + r_portfolio(t)], &nbsp; t = 1...T<br>
                <strong style="color:#86198f;">总收益率 = 累计净值(T) - 1</strong>
            </div>
            <p style="font-size:13px; color:#6b7280; margin-top:6px;">
                例如：若4个季度后累计净值为1.2548，则总收益率 = 1.2548 - 1 = <strong style="color:#10b981;">25.48%</strong>
            </p>

            <p style="margin-top:14px;"><strong>对比：基础策略的总收益率计算</strong></p>
            <p style="font-size:13px;">基础策略（等权重）的区别仅在于权重：每支股票权重固定为 1/30 ≈ 3.33%，不加权调整。复利累积逻辑完全相同。</p>
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

        <!-- 3.7 核心策略回测结果 -->
        <h3 style="font-size:16px; margin-bottom:15px; color:#334155;">📈 3.7 核心策略回测结果</h3>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>选股模型</th>
                    <th>策略类型</th>
                    <th>总收益率</th>
                    <th>夏普比率</th>
                    <th>最大回撤</th>
                    <th>平均下跌概率</th>
                </tr>
            </thead>
            <tbody id="risk-strategy-tbody"></tbody>
        </table>

        <div class="fig-title">图 1：核心策略累计收益率曲线（概率驱动动态仓位）</div>
        <div id="chart-risk-cum-return" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>核心策略（概率驱动动态仓位）的累计收益率曲线。纵轴为累计收益率百分比，0%为起始基准线。两个对比模型配合动态仓位策略后均显著跑赢市场。
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

    <!-- 六、策略对比与效果分析 -->
    <div class="section">
        <h2 class="section-title">六、策略对比与效果分析</h2>
        <p class="section-desc">核心策略（动态仓位）vs 基础策略（等权重）的全面对比</p>
        
        <!-- 基础策略回测结果 -->
        <h3 style="font-size:16px; margin-bottom:12px; color:#334155;">📊 基础策略回测结果（等权重Top30）</h3>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>选股模型</th>
                    <th>总收益率</th>
                    <th>市场收益率</th>
                    <th>超额收益</th>
                    <th>夏普比率</th>
                    <th>最大回撤</th>
                </tr>
            </thead>
            <tbody id="strategy-tbody"></tbody>
        </table>

        <!-- 核心vs基础对比 -->
        <h3 style="font-size:16px; margin:20px 0 12px; color:#334155;">⚖️ 核心策略 vs 基础策略对比</h3>
        
        <div class="fig-title">图 4：总收益率对比（核心策略 vs 基础策略）</div>
        <div id="chart-risk-compare-return" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>核心策略（概率驱动动态仓位）在两个对比模型上都提升了总收益率。具体提升幅度见图表数值。
        </div>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 5：夏普比率对比</div>
                <div id="chart-risk-compare-sharpe" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 6：最大回撤对比</div>
                <div id="chart-risk-compare-dd" class="chart-container small"></div>
            </div>
        </div>
        <div class="fig-caption">
            <strong>解读：</strong>核心策略在夏普比率和最大回撤两个风险指标上均有改善，体现了下跌概率加权在风险控制上的优势。
        </div>

        <!-- 基础策略累计收益 -->
        <div class="fig-title">图 7：基础策略累计收益率曲线（等权重对比）</div>
        <div id="chart-cum-return" class="chart-container"></div>
        <div class="fig-caption">
            <strong>解读：</strong>基础策略（等权重配置）的累计收益曲线，作为核心策略的对比基准。两个对比模型均跑赢市场。
        </div>

        <div class="chart-row">
            <div>
                <div class="fig-title">图 8：基础策略回撤曲线</div>
                <div id="chart-drawdown" class="chart-container small"></div>
            </div>
            <div>
                <div class="fig-title">图 9：季度收益率对比</div>
                <div id="chart-quarterly" class="chart-container small"></div>
            </div>
        </div>
    </div>

    <!-- 七、核心策略四维对比 -->
    <div class="section">
        <h2 class="section-title">七、核心策略四维对比</h2>
        <p class="section-desc">四个维度对比各选股模型配合核心策略的表现</p>
        
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
            <strong>解读：</strong>两个对比模型配合核心策略（动态仓位）后，在收益和风险调整后收益上均优于市场平均水平。具体表现见图表数值。
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
    renderRiskStrategyTable();
    renderRiskCumReturn();
    renderFeatureImportance('chart-feat-rf', '随机森林');
    renderFeatureImportance('chart-feat-dt', '决策树');
    renderStrategyTable();
    renderCumReturn();
    renderDrawdown();
    renderQuarterly();
    renderCompareCharts();
    renderRiskCompareCharts();
    setTimeout(resizeAllCharts, 100);
    setTimeout(resizeAllCharts, 500);
    window.addEventListener('resize', resizeAllCharts);
}

function resizeAllCharts() {
    const ids = ['chart-risk-cum-return','chart-feat-rf','chart-feat-dt','chart-cum-return','chart-drawdown','chart-quarterly','chart-return-compare','chart-sharpe-compare','chart-dd-compare','chart-trades-compare','chart-risk-compare-return','chart-risk-compare-sharpe','chart-risk-compare-dd'];
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
    const trainQuarters = di.train_quarters_raw || [];
    const testQuarters = di.test_quarters_raw || [];
    document.getElementById('train-info').innerHTML =
        '季度: ' + trainQuarters.join(', ') + '<br>' +
        '数量: <strong style="color:#065f46;">' + trainQuarters.length + '个季度</strong><br>' +
        '占比: 60%<br>' +
        '<span style="color:#64748b; font-size:12px;">(特征工程前置期后实际有标签样本为2020Q3起)</span>';
    document.getElementById('test-info').innerHTML =
        '季度: ' + testQuarters.join(', ') + '<br>' +
        '数量: <strong style="color:#92400e;">' + testQuarters.length + '个季度</strong><br>' +
        '占比: 40%<br>' +
        '<span style="color:#64748b; font-size:12px;">(4个季度全部有完整特征)</span>';
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

// 图1：核心策略累计收益率（百分比格式）
function renderRiskCumReturn() {
    const chart = echarts.init(document.getElementById('chart-risk-cum-return'));
    const rsr = allData.risk_strategy_results;
    const colors = ['#10b981', '#f97316'];
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
        data: rsr['随机森林'].market_cum.map(v => (v - 1) * 100)
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
        xAxis: { type: 'category', data: rsr['随机森林'].dates, axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
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

// 图7：基础策略累计收益率（百分比格式）
function renderCumReturn() {
    const chart = echarts.init(document.getElementById('chart-cum-return'));
    const sr = allData.strategy_results;
    const colors = ['#10b981', '#f97316'];
    const series = Object.keys(sr).map((name, i) => ({
        name: name,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: colors[i] },
        itemStyle: { color: colors[i] },
        data: sr[name].portfolio_cum.map(v => (v - 1) * 100)
    }));
    series.push({
        name: '市场平均',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', width: 2, color: '#94a3b8' },
        itemStyle: { color: '#94a3b8' },
        data: sr['随机森林'].market_cum.map(v => (v - 1) * 100)
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
        xAxis: { type: 'category', data: sr['随机森林'].dates, axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
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
    const colors = ['#10b981', '#f97316'];
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
        xAxis: { type: 'category', data: sr['随机森林'].dates, axisLabel: { rotate: 45, fontSize: 10, hideOverlap: true } },
        yAxis: { type: 'value', name: '回撤(%)', nameLocation: 'middle', nameGap: 50 },
        series: series
    });
}

function renderQuarterly() {
    const chart = echarts.init(document.getElementById('chart-quarterly'));
    const qr = allData.quarterly_results;
    const quarters = [...new Set(qr.map(r => r.year_quarter))].sort();
    const models = [...new Set(qr.map(r => r.model))];
    const colors = ['#10b981', '#f97316'];
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
    const colors = ['#10b981', '#f97316'];

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

// 图4-6：核心策略 vs 基础策略对比
function renderRiskCompareCharts() {
    const sr = allData.strategy_results;
    const rsr = allData.risk_strategy_results;
    const models = Object.keys(sr);

    // 图4：总收益率对比（分组柱状图）
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
                name: '核心策略(动态仓位)',
                type: 'bar',
                data: models.map(m => +(rsr[m].total_return * 100).toFixed(2)),
                itemStyle: { color: '#10b981' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2) + '%'; } }
            }
        ]
    });

    // 图5：夏普比率对比
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
                name: '核心策略(动态仓位)',
                type: 'bar',
                data: models.map(m => +rsr[m].sharpe_ratio.toFixed(2)),
                itemStyle: { color: '#3b82f6' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2); } }
            }
        ]
    });

    // 图6：最大回撤对比
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
                name: '核心策略(动态仓位)',
                type: 'bar',
                data: models.map(m => +(rsr[m].max_drawdown * 100).toFixed(2)),
                itemStyle: { color: '#ef4444' },
                label: { show: true, position: 'top', fontSize: 10, formatter: function(p) { return p.value.toFixed(2) + '%'; } }
            }
        ]
    });
}
</script>

</body>
</html>
'''

with open('AI-quant/project-05-2.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ project-05-2.html 生成完成')
