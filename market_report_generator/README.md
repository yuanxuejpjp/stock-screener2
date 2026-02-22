# 📊 每日市场分析报告生成器

基于 Python 的自动化市场分析报告生成工具，支持股票数据获取、新闻抓取和 Markdown 报告生成。

## 🚀 功能特点

### 数据获取
- **实时股价数据**: 通过 Yahoo Finance API 获取
- **大盘指数**: S&P 500、纳斯达克、道琼斯、VIX
- **技术指标**: RSI、移动平均线、Beta 等
- **市场情绪**: CNN 恐惧贪婪指数

### 新闻抓取
- **RSS 订阅**: 支持多个主流财经媒体 RSS
- **网页抓取**: 可扩展的网页内容提取
- **关键词过滤**: 自动分类 AI/电力/宏观新闻

### 报告生成
- **板块分析**: AI 板块、电力板块专项分析
- **个股追踪**: NVDA、MSFT、GOOGL、AMD、TSLA、TSM、CEG、VST
- **Markdown 格式**: 便于阅读和分享
- **自动保存**: 按日期命名保存到 reports 目录

## 📁 项目结构

```
market_report_generator/
├── config.py              # 配置文件（股票列表、RSS源等）
├── main.py                # 主程序入口
├── requirements.txt       # Python 依赖
├── README.md             # 项目说明
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── data_fetcher.py   # 数据获取模块
│   ├── news_scraper.py   # 新闻抓取模块
│   └── report_generator.py # 报告生成模块
├── data/                 # 数据缓存目录
└── reports/              # 报告输出目录
```

## 🛠️ 安装与配置

### 1. 安装依赖

```bash
cd market_report_generator
pip install -r requirements.txt
```

### 2. 运行程序

```bash
# 生成今日报告（使用实时数据）
python main.py

# 使用模拟数据（测试或市场休市时）
python main.py --mock

# 指定输出文件名
python main.py --output my_report.md
```

## 📊 报告内容

生成的报告包含以下部分：

1. **市场概览**
   - S&P 500、纳斯达克、道琼斯指数
   - CNN 恐惧贪婪指数
   - VIX 波动率指数

2. **AI 板块分析**
   - NVDA、MSFT、GOOGL、AMD、TSLA、TSM 表现
   - RSI 技术指标
   - 板块动态分析

3. **电力板块分析**
   - CEG、VST 表现
   - 数据中心电力需求相关资讯

4. **市场资讯要点**
   - AI 板块相关新闻（2-3条）
   - 电力板块相关新闻（2条）
   - 宏观市场相关新闻（2条）

5. **今日要点总结**
   - 市场情绪判断
   - 板块表现总结
   - 投资建议提示

## ⚙️ 配置文件

编辑 `config.py` 可自定义：

- **股票列表**: 添加/删除关注的股票
- **RSS 源**: 添加新的新闻源
- **关键词**: 调整新闻分类关键词
- **报告模板**: 自定义报告格式

## 📝 示例报告

生成的报告格式示例：

```markdown
# 📊 每日市场分析报告

**报告日期**: 2026年02月22日 周日  
**生成时间**: 09:30:00  
**市场状态**: ⚪ 休市

---

## 📈 市场概览

### 大盘指数

| 指数 | 当前点位 | 日涨跌 | 涨跌幅 |
|------|----------|--------|--------|
| S&P 500 | 5,800.00 | 🟢 +25.00 | +0.43% |
| 纳斯达克 | 17,500.00 | 🟢 +100.00 | +0.57% |

### 市场情绪指标

- **CNN 恐惧贪婪指数**: 65 (贪婪)
- **VIX 波动率指数**: 15.5

...
```

## 🔧 高级用法

### 作为模块导入

```python
from utils.data_fetcher import data_fetcher
from utils.report_generator import report_generator

# 获取单只股票数据
nvda = data_fetcher.get_stock_data('NVDA')
print(f"NVDA 当前价格: ${nvda['current_price']}")

# 批量获取
stocks = data_fetcher.batch_get_stocks(['NVDA', 'MSFT', 'GOOGL'])

# 生成自定义报告
report = report_generator.generate_report(
    ai_stocks={'NVDA': 'NVIDIA', 'MSFT': 'Microsoft'},
    power_stocks={'CEG': 'Constellation'},
    market_indices={'^GSPC': 'S&P 500'},
    use_mock_news=True
)
```

### 扩展新闻源

在 `config.py` 中添加新的 RSS 源：

```python
RSS_FEEDS = {
    'My Source': 'https://example.com/feed.xml',
    # ...
}
```

## ⚠️ 注意事项

1. **数据延迟**: Yahoo Finance 数据可能有 15-20 分钟延迟
2. **API 限制**: 频繁请求可能导致临时限制
3. **RSS 可用性**: 部分 RSS 源可能随时变更
4. **周末/假日**: 市场休市时建议使用 `--mock` 参数

## 📄 免责声明

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

## 📧 联系方式

如有问题或建议，欢迎反馈。

---

**最后更新**: 2026-02-22
