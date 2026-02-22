"""
配置文件 - 股票列表、RSS源、API配置等
"""

from datetime import datetime

# ==================== 报告配置 ====================
REPORT_TITLE = "每日市场分析报告"
AUTHOR = "量化研究助理"

# ==================== 股票配置 ====================
# AI 板块股票
AI_STOCKS = {
    'NVDA': 'NVIDIA',
    'MSFT': 'Microsoft',
    'GOOGL': 'Alphabet',
    'AMD': 'AMD',
    'TSLA': 'Tesla',
    'TSM': '台积电',
}

# 电力板块股票
POWER_STOCKS = {
    'CEG': 'Constellation Energy',
    'VST': 'Vistra',
}

# 大盘指数
MARKET_INDICES = {
    '^GSPC': 'S&P 500',
    '^IXIC': '纳斯达克',
    '^DJI': '道琼斯',
    '^VIX': 'VIX波动率',
}

# 所有关注股票（合并）
WATCHLIST = list(AI_STOCKS.keys()) + list(POWER_STOCKS.keys())

# ==================== RSS 新闻源 ====================
RSS_FEEDS = {
    'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
    'MarketWatch': 'https://feeds.marketwatch.com/marketwatch/topstories',
    'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
    'Investing.com': 'https://www.investing.com/rss/news.rss',
    'Financial Times': 'https://www.ft.com/?format=rss',
    'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
    'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
}

# ==================== 网页抓取配置 ====================
NEWS_SOURCES = {
    'yahoo_finance': {
        'url': 'https://finance.yahoo.com/news/',
        'selectors': {
            'articles': 'article',
            'title': 'h3',
            'link': 'a',
        }
    },
    'marketwatch': {
        'url': 'https://www.marketwatch.com/latest-news',
        'selectors': {
            'articles': '.article__content',
            'title': '.article__headline',
            'link': 'a',
        }
    },
    'barrons': {
        'url': 'https://www.barrons.com/livecoverage/stock-market-today',
        'selectors': {
            'articles': '.article-container',
            'title': '.headline',
            'link': 'a',
        }
    },
}

# ==================== X/Twitter 大V账号 ====================
# 由于 X API 需要认证，这里存储的是知名财经博主的用户名
# 实际抓取需要使用第三方服务或浏览器自动化
X_INFLUENCERS = {
    'tech': [
        '@RayDalio',
        '@michaeljburry',
        '@cathiewood',
        '@elonmusk',
        '@sama',
    ],
    'macro': [
        '@DiMartinoBooth',
        '@LizAnnSonders',
        '@ianbremmer',
        '@DavidRubenstein',
    ],
    'trading': [
        '@realadamcurry',
        '@chamath',
        '@BillAckman',
        '@Carl_C_Icahn',
    ]
}

# ==================== 关键词过滤 ====================
KEYWORDS_AI = [
    'AI', 'artificial intelligence', 'NVIDIA', 'NVDA', 'GPU', 'chatgpt',
    'openai', 'microsoft AI', 'google AI', 'bard', 'claude', 'llm',
    'machine learning', 'deep learning', 'neural network',
]

KEYWORDS_POWER = [
    'nuclear', 'energy', 'power', 'electricity', 'CEG', 'VST',
    'constellation', 'vistra', 'renewable', 'solar', 'wind',
    'data center power', 'grid', 'utility',
]

KEYWORDS_MARKET = [
    'S&P 500', 'SPX', 'nasdaq', 'stock market', 'federal reserve',
    'fed', 'interest rate', 'inflation', 'GDP', 'earnings',
    'bull market', 'bear market', 'correction', 'rally',
]

# ==================== 输出配置 ====================
OUTPUT_DIR = 'reports'
DATA_DIR = 'data'
ENCODING = 'utf-8'

# ==================== 报告模板 ====================
REPORT_TEMPLATE = """
# {title}

**日期**: {date}  
**作者**: {author}  
**市场状态**: {market_status}

---

## 📊 市场概览

### 大盘指数

| 指数 | 当前点位 | 日涨跌 | 涨跌幅 |
|------|----------|--------|--------|
{market_table}

### 市场情绪指标

- **CNN 恐惧贪婪指数**: {fear_greed} ({fear_greed_level})
- **VIX 波动率**: {vix}

---

## 🤖 AI 板块分析

### 重点股票表现

| 股票 | 公司名称 | 当前价格 | 日涨跌 | 技术指标 |
|------|----------|----------|--------|----------|
{ai_table}

### 板块动态
{ai_analysis}

---

## ⚡ 电力板块分析

### 重点股票表现

| 股票 | 公司名称 | 当前价格 | 日涨跌 | 技术指标 |
|------|----------|----------|--------|----------|
{power_table}

### 板块动态
{power_analysis}

---

## 📰 市场资讯要点

### AI 板块相关
{ai_news}

### 电力板块相关
{power_news}

### 宏观市场相关
{market_news}

---

## 💡 今日要点总结

{summary}

---

*免责声明：本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*
*数据来源：Yahoo Finance, CNN Fear & Greed, 各大财经媒体*
"""

def get_current_date():
    """获取当前日期（中文格式）"""
    return datetime.now().strftime('%Y年%m月%d日 %A')

def get_current_date_file():
    """获取当前日期（文件格式）"""
    return datetime.now().strftime('%Y%m%d')
