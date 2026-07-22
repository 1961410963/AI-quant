# 📊 AI 量化交易课程作品集

> 北京大学光华管理学院 · 量化投资与智能交易实战  
> Created by **Eric Zhao**

<div align="center">

| 📈 技术指标研究 | 🤖 AI辅助决策 | 🐍 Python数据分析 |
|---|---|---|
| ECharts 可视化 | MCP 工具链 | Tushare 金融数据 |

</div>

---

## 🗂️ 项目结构

```
北大光华AI交易课程/
├── index.html                # 📄 作品集入口（重定向）
├── AI-quant/                 # 📁 作品集与分析报告
│   ├── index.html            #    作品集首页
│   ├── technical-indicators-guide.html #  技术指标计算方法与作用说明（项目02.1）
│   ├── stock-analysis-600967.html     #    内蒙一机分析报告
│   ├── stock-indicator-visualizer.html #    可交互指标可视化工具（项目02.2）
│   ├── output/               #    📊 数据输出目录
│   │   ├── 002812.SZ_analysis.html    #    恩捷股份分析报告
│   │   ├── 300504.SZ_analysis.html    #    天邑股份分析报告（项目01.4）
│   │   ├── 002812.SZ_daily_data.csv   #    恩捷股份数据
│   │   ├── 601899.SH_strategy_report.html #    紫金矿业策略报告
│   │   ├── 300504.SZ_ma_strategy.html #    天邑股份双均线策略回测报告（项目03.1）
│   │   ├── 300504.SZ_daily_data.csv   #    天邑股份数据
│   │   ├── ma_batch_analysis.html     #    双均线策略批量回测对比报告（项目03.2）
│   │   ├── ma_batch_results.csv       #    批量回测结果数据（项目03.2）
│   │   └── ...其他数据文件
│   ├── scripts/              #    🔧 辅助脚本
│   │   ├── fetch_600967_3y.py        #    内蒙一机数据获取
│   │   ├── fetch_601899_3y.py        #    紫金矿业数据获取
│   │   └── ...其他工具脚本
│   ├── fetch_enjie_qfq.py    #    恩捷股份数据获取（核心）
│   ├── generate_tianyi_analysis.py   #    天邑股份报告生成（项目01.4）
│   ├── fetch_tianyi_qfq.py   #    天邑股份数据获取
│   ├── generate_enjie_analysis.py   #    恩捷股份报告生成（核心）
│   ├── generate_ma_strategy.py  #    天邑股份双均线策略报告生成（项目03.1）
│   ├── batch_ma_backtest.py     #    双均线策略批量回测与对比分析（项目03.2）
│   ├── update_visualizer_data.py #    可视化工具数据更新脚本
│   ├── generate_strategy_report.py  #    策略报告生成（核心）
│   ├── project-05.html            #    AI交易引擎：机器学习算法与场景应用（项目05.1）
│   ├── project-05-2.html          #    智能决策者：机器学习定制专属策略（项目05.2）
│   ├── project-05-2-data.json     #    项目05.2回测数据
│   ├── task5_ml_stock_classification.py #  机器学习分类模型训练（项目05.1）
│   ├── task5_2_ml_strategy.py     #    机器学习策略回测（项目05.2）
│   └── generate_project05_2.py    #    项目05.2 HTML报告生成
│
├── tushare_MCP/              # 📁 MCP 数据服务器
│   ├── server.py             #    Stdio 模式入口
│   ├── server_http.py        #    HTTP 模式入口
│   ├── strategies/           #    📈 T+1 尾盘选股策略
│   ├── scripts/              #    分析脚本
│   ├── tests/                #    测试文件
│   ├── tools/                #    13+ 金融数据工具模块
│   ├── cache/                #    SQLite 版本化缓存
│   ├── config/               #    Token 管理与配置
│   └── prompts/              #    提示模板
│
└── .gitignore
```

---

## ✨ 核心功能

### 1️⃣ 股票分析报告生成

自动生成包含 **8 个 ECharts 图表** 的完整 HTML 分析报告：

| 图表 | 指标 | 说明 |
|------|------|------|
| 📈 K线图 | MA5/10/20/60 | 四均线系统 |
| 📊 成交量 | MA Volume | 成交量均线 |
| 🔄 MACD | DIF/DEA/柱状图 | 趋势跟随 |
| ⚡ RSI | 超买/超卖线可调 | 动量指标 |
| 🎯 KDJ | K/D/J 三线 | 随机指标 |
| 📐 布林带 | 上轨/中轨/下轨 | 波动率通道 |
| 📏 ATR | 真实波动幅度 | 风险管理 |
| 🧠 基本面 | PE/PB/总市值 | 价值分析 |

**支持标的：**
- 恩捷股份（002812.SZ）— 锂电池隔膜龙头
- 内蒙一机（600967.SH）— 军工龙头
- 紫金矿业（601899.SH）— 有色金属龙头
- 天邑股份（300504.SZ）— 光纤网络设备制造商

### 2️⃣ 技术指标系列

#### 2.1 股票技术指标计算方法与作用说明

七大经典技术指标的计算方法与实战作用详解：

- 📐 **计算公式** — 每个指标的完整数学公式与参数说明
- 📊 **指标作用** — 趋势判断、超买超卖、波动率、动量等核心用途
- 🎯 **策略角色** — 在各类交易策略中承担的功能定位

**涵盖指标：** 均线系统(MA)、MACD、RSI、KDJ、布林带(BOLL)、ATR

#### 2.2 交互式指标可视化工具

可实时调节参数的股票指标分析工具：

- 🎛️ **参数可调** — 均线周期、MACD 参数、RSI 超买超卖线、布林带倍数
- 🔄 **实时重绘** — 参数变更即时更新所有图表
- 🔗 **图表联动** — 7 个图表同步缩放、同步十字光标
- 🌗 **主题切换** — 深色/浅色模式一键切换
- 📱 **响应式布局** — 桌面端与移动端自适应

**支持标的（7只，前复权数据）：**

| 类型 | 代码 | 名称 |
|------|------|------|
| 股票 | 600967.SH | 内蒙一机 |
| 股票 | 600346.SH | 恒力石化 |
| 股票 | 002080.SZ | 中材科技 |
| 股票 | 002812.SZ | 恩捷股份 |
| 股票 | 601899.SH | 紫金矿业 |
| ETF | 159562.SZ | 华夏黄金ETF |
| ETF | 563020.SH | 易方达红利低波ETF |

### 3️⃣ 双均线策略回测系列

#### 3.1 天邑股份双均线策略回测

天邑股份（300504.SZ）双均线策略回测报告，基于 MA5/MA20 金叉死叉信号进行趋势跟踪：

- 📊 **策略规则** — 金叉买入（MA5上穿MA20）、死叉卖出（MA5下穿MA20）
- 📈 **回测指标** — 累计回报、回撤曲线（MDD）、夏普比率
- 📉 **可视化** — 股价+均线走势、交易信号标记、资产净值曲线、回撤曲线
- 📋 **交易明细** — 完整的买入/卖出记录，含价格、数量、金额

#### 3.2 双均线策略批量回测与对比分析

8个标的（6只股票+2只ETF）× 4组均线周期（MA5/MA10、MA5/MA20、MA10/MA30、MA20/MA60）= 32次回测的系统性对比分析：

- 🔬 **实验矩阵** — 覆盖不同资产类型与参数组合，量化策略敏感度
- 📊 **5个统计图表** — 各标的收益对比、周期风险收益、风险-收益散点、夏普比率、股票vs ETF
- 💡 **应用心得** — 适用场景、周期选择、胜率与盈亏比关系、仓位管理、策略组合建议

### 4️⃣ 多策略交易方案

紫金矿业专项策略报告，涵盖 **4 种交易策略**：

| 策略 | 类型 | 核心逻辑 |
|------|------|----------|
| MACD 趋势跟随 | 趋势跟踪 | DIF 金叉/死叉 + 柱状图确认 |
| RSI 均值回归 | 逆势反转 | 超卖买入 / 超卖卖出 |
| 布林带突破 | 突破交易 | 上下轨突破 + ATR 止损 |
| 多指标共振 | 综合信号 | ≥3 个指标同时发出同向信号 |

**每套策略包含：**
- ✅ 进场/出场规则
- ✅ 仓位管理（金字塔加仓法）
- ✅ 止损止盈方案（ATR + 百分比）
- ✅ 风险评估（5 类风险）

### 5️⃣ 机器学习量化交易系列

#### 5.1 AI交易引擎：机器学习算法与场景应用

基于scikit-learn的股票收益二分类模型训练与评估：

- 🤖 **三种算法对比** — 逻辑回归、决策树、随机森林
- 📊 **模型评估** — 混淆矩阵、ROC曲线、AUC指标
- 🔍 **特征工程** — 19个财务因子 × 4种衍生方式 = 76个特征
- 📈 **9个ECharts图表** — 可视化模型性能与特征重要性

#### 5.2 智能决策者：机器学习定制专属策略

基于机器学习模型的股票收益率排序策略与动态仓位调整：

- 🎯 **四策略对比** — 决策树/随机森林 × 基础等权重/动态仓位
- 📉 **下跌概率模型** — 预测股票下跌概率，动态调整持仓权重
- ⚖️ **四策略全面对比** — 基础等权重策略 vs 下跌概率加权策略
- 📊 **10个ECharts图表** — 累计收益、回撤、季度收益、特征重要性等
- 📏 **4:4季度拆分（dropna后）** — 原始10个季度经特征工程dropna后保留8个季度，前4训练后4测试

### 6️⃣ 聚宽量化策略优化（项目06.1）

基于聚宽（JoinQuant）平台的小市值轮动策略优化全流程：

- 🔄 **多轮迭代** — 从模板策略出发，经过扩大选股池、质量筛选、每日轮动等优化
- 📊 **5年回测验证** — 年化收益从10.84%提升至21.57%，夏普比率从0.216提升至0.602
- 📈 **可视化报告** — ECharts累计收益曲线、回撤对比图、全方位数据对比表

详见 [project-06-1/index.html](聚宽项目/project-06-1/index.html)

### 7️⃣ Tushare MCP 数据服务器

基于 [Model Context Protocol](https://modelcontextprotocol.io/) 的金融数据 AI 助手扩展。

#### 工具覆盖

| 类别 | 工具 | 接口数 |
|------|------|--------|
| 📋 基础数据 | 股票搜索、基本信息、交易日历 | 3 |
| 📈 行情数据 | 日线/周线/月线、复权因子 | 4 |
| 💰 财务数据 | 利润表、资产负债表、现金流量表、财务指标 | 4 |
| 🏛️ 指数数据 | 国内指数、国际指数、指数分类 | 4 |
| 🏷️ 概念板块 | 概念搜索、成分股、行情、资金流向 | 4 |
| 📊 行业数据 | 申万行业、行业指数、行业成交量 | 3 |
| 💹 资金分析 | 融资融券、股东增减持、大宗交易 | 3 |
| 🔍 Alpha 策略 | 相对强度模型、行业轮动、概念动量 | 3 |
| 🏦 机构数据 | 机构调研追踪 | 1 |
| 📰 公告扫描 | 业绩预告、分红送配、高管持股 | 3 |
| 🌍 宏观数据 | GDP、CPI、PMI、货币供应 | 4 |
| 💱 外汇期货 | 外汇日线、期货基础数据 | 2 |
| 📦 缓存管理 | 缓存统计、过期清理 | 2 |

**总计：30+ 专业金融数据工具**

#### 架构亮点

- 🔄 **自动工具发现** — 基于 `pkgutil` 的动态模块加载
- 💾 **版本化缓存** — SQLite + WAL 模式，支持历史版本回溯
- 🚀 **双模式支持** — Stdio（Claude Desktop）+ HTTP（Cursor/VS Code）
- 🛡️ **智能风控** — 异步包装 + 线程池 + 异常中间件
- 📝 **提示模板** — 内置 Token 配置与利润表查询模板

### 7️⃣ T+1 尾盘选股策略

自适应多模式选股策略，支持 **熊市 / 震荡市 / 牛市** 三种市场环境：

| 模式 | 涨幅区间 | 换手率上限 | 策略风格 |
|------|----------|-----------|----------|
| 🐻 熊市 | 0% ~ 2.5% | 5% | 极度保守，潜伏超跌反弹 |
| 📊 震荡市 | 0.5% ~ 4.2% | 8% | 防御潜伏，吃鱼身不吃鱼尾 |
| 🐂 牛市 | 3% ~ 8.5% | 15% | 进攻型，追涨抓动量 |

**筛选漏斗：**
```
全市场 → 涨幅/VWAP/尾盘强度 → 自适应换手率风控 → 筹码Tier分级 → 加权评分 → Top N
```

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 🎨 可视化 | ECharts 5.x, CSS Grid, Flexbox |
| 🐍 后端 | Python 3.14+, Tushare Pro API |
| 🤖 AI 集成 | MCP (FastMCP), Claude Desktop, Cursor |
| 💾 缓存 | SQLite (WAL 模式), python-dotenv |
| 🌐 服务器 | Starlette, Uvicorn, uvicorn |
| 📦 构建 | 纯静态 HTML, 无框架依赖 |

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Tushare Pro 账号（[注册](https://tushare.pro/register)）
- Claude Desktop 或 Cursor IDE

### 安装 MCP 服务器

```bash
cd tushare_MCP
pip install -r requirements.txt

# 配置 Token（方式一：手动）
echo "TUSHARE_TOKEN=your_token_here" > .env

# 配置 Token（方式二：对话配置）
# 在 Claude Desktop 中对我说："请帮我配置Tushare token"
```

### 启动服务

```bash
# Stdio 模式 — 适用于 Claude Desktop
python server.py --stdio

# HTTP 模式 — 适用于 Cursor / VS Code
python server_http.py
# 服务地址: http://localhost:8000/mcp
```

### 配置 MCP 客户端

**Claude Desktop** — 编辑 `%APPDATA%\Claude\claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "tushare": {
      "command": "python",
      "args": ["D:\\path\\to\\tushare_MCP\\server.py"]
    }
  }
}
```

**Cursor** — Settings → Features → MCP → Add New MCP Server：
- Type: `Streamable HTTP`
- URL: `http://localhost:8000/mcp`

### 生成分析报告

```bash
cd AI-quant

# 获取恩捷股份前复权数据
python fetch_enjie_qfq.py

# 生成恩捷股份分析报告（项目01.2）
python generate_enjie_analysis.py

# 生成策略报告
python generate_strategy_report.py
```

---

## 📸 截图

### 作品集首页

作品集首页采用卡片式布局，展示三个核心项目，紫色渐变主题。

### 股票分析报告

内含 8 个 ECharts 图表，支持图表联动、十字光标、数据缩放。

### 可交互可视化工具

实时调节参数，即时重绘所有图表，支持深色/浅色主题切换。

---

## 🔒 安全说明

- ⚠️ **Token 管理** — Tushare Token 存储在 `.env` 文件中，已加入 `.gitignore`
- 🔐 **环境变量** — 所有脚本通过 `os.getenv("TUSHARE_TOKEN")` 读取
- 🛡️ **SQL 安全** — 所有数据库查询使用参数化，防止 SQL 注入
- 🔒 **CORS 配置** — HTTP 服务器仅允许 localhost 跨域访问

---

## 📄 License

[MIT License](./tushare_MCP/LICENSE)

---

## 👤 About

| 项目 | 信息 |
|------|------|
| 📚 课程 | 北京大学光华管理学院 · 量化投资与智能交易实战 |
| 👨‍💻 作者 | Eric Zhao |
| 📧 邮箱 | [1961410963@qq.com](mailto:1961410963@qq.com) |
| 🐙 GitHub | [@1961410963](https://github.com/1961410963) |
| 📅 创建 | 2026 |

---

<div align="center">

⭐ Star this repo if you find it useful!

</div>
