"""
新闻抓取模块 - RSS + 网页抓取
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import time
from urllib.parse import urljoin

class NewsScraper:
    """新闻抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        
    def fetch_rss_feed(self, url: str, source_name: str = "") -> List[Dict]:
        """
        抓取 RSS 订阅源
        
        Args:
            url: RSS 订阅地址
            source_name: 来源名称
            
        Returns:
            List[Dict]: 新闻条目列表
        """
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:10]:  # 只取前10条
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': entry.get('published', ''),
                    'source': source_name or feed.feed.get('title', 'Unknown'),
                }
                articles.append(article)
                
            return articles
            
        except Exception as e:
            print(f"抓取 RSS {url} 失败: {e}")
            return []
    
    def fetch_multiple_rss(self, feeds: Dict[str, str]) -> List[Dict]:
        """
        批量抓取多个 RSS 源
        
        Args:
            feeds: {来源名称: RSS地址} 的字典
            
        Returns:
            List[Dict]: 合并后的新闻列表
        """
        all_articles = []
        for name, url in feeds.items():
            articles = self.fetch_rss_feed(url, name)
            all_articles.extend(articles)
            time.sleep(0.5)  # 礼貌性延迟
        return all_articles
    
    def scrape_web_page(self, url: str, selectors: Dict[str, str]) -> List[Dict]:
        """
        抓取网页内容
        
        Args:
            url: 网页地址
            selectors: CSS选择器字典 {'articles': '', 'title': '', 'link': ''}
            
        Returns:
            List[Dict]: 提取的文章列表
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 查找文章容器
            article_tags = soup.select(selectors.get('articles', 'article'))
            
            for tag in article_tags[:10]:  # 只取前10条
                # 提取标题
                title_tag = tag.select_one(selectors.get('title', 'h2, h3'))
                title = title_tag.get_text(strip=True) if title_tag else ''
                
                # 提取链接
                link_tag = tag.select_one(selectors.get('link', 'a'))
                link = ''
                if link_tag and link_tag.get('href'):
                    link = urljoin(url, link_tag['href'])
                    
                # 提取摘要
                summary_tag = tag.select_one('p, .summary, .description')
                summary = summary_tag.get_text(strip=True) if summary_tag else ''
                
                if title and link:
                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': summary,
                        'source': url,
                        'published': '',
                    })
                    
            return articles
            
        except Exception as e:
            print(f"抓取网页 {url} 失败: {e}")
            return []
    
    def search_news_by_keywords(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        根据关键词过滤新闻
        
        Args:
            articles: 新闻列表
            keywords: 关键词列表
            
        Returns:
            List[Dict]: 匹配的新闻列表
        """
        matched = []
        keyword_pattern = re.compile(
            '|'.join(re.escape(kw) for kw in keywords), 
            re.IGNORECASE
        )
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            if keyword_pattern.search(text):
                matched.append(article)
                
        return matched
    
    def deduplicate_news(self, articles: List[Dict]) -> List[Dict]:
        """
        去重新闻（根据标题相似度）
        """
        seen_titles = set()
        unique = []
        
        for article in articles:
            # 简化标题用于去重
            title = article.get('title', '').lower().strip()
            title_key = re.sub(r'[^\w]', '', title)[:50]
            
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique.append(article)
                
        return unique
    
    def summarize_news(self, article: Dict, max_sentences: int = 3) -> str:
        """
        简单新闻摘要（提取前几句）
        
        Args:
            article: 新闻字典
            max_sentences: 最大句数
            
        Returns:
            str: 摘要文本
        """
        text = article.get('summary', article.get('title', ''))
        
        # 清理 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 分句
        sentences = re.split(r'[.!?。！？]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # 取前几句
        summary = '. '.join(sentences[:max_sentences])
        
        return summary if summary else article.get('title', '')
    
    def get_mock_news(self) -> Dict[str, List[Dict]]:
        """
        获取模拟新闻数据（用于测试或当抓取失败时）
        """
        return {
            'ai': [
                {
                    'title': 'NVIDIA股价创新高，AI芯片需求持续强劲',
                    'summary': 'NVIDIA第四季度营收超预期，数据中心业务增长强劲。分析师普遍上调目标价，认为AI基础设施建设仍处于早期阶段。CEO黄仁勋表示，生成式AI正在推动计算需求的结构性转变。',
                    'source': 'Yahoo Finance',
                    'author': 'Market Analyst',
                    'link': '#'
                },
                {
                    'title': 'Microsoft AI业务增长迅速，Copilot用户突破新高',
                    'summary': 'Microsoft最新财报显示，AI相关收入已成为增长主要驱动力。Copilot for Microsoft 365订阅数持续攀升，Azure AI服务使用量同比翻倍。公司预计下一季度AI业务将继续保持高速增长。',
                    'source': 'Seeking Alpha',
                    'author': 'Tech Investor',
                    'link': '#'
                },
                {
                    'title': 'Google发布新一代Gemini模型，挑战OpenAI领先地位',
                    'summary': 'Google DeepMind发布Gemini Ultra版本，在多项基准测试中超越GPT-4。分析师认为这是Google在AI竞赛中的重要里程碑，有助于提升其云业务竞争力。股价盘后上涨2%。',
                    'source': 'CNBC',
                    'author': 'Tech Reporter',
                    'link': '#'
                },
            ],
            'power': [
                {
                    'title': '数据中心电力需求激增，核能股受追捧',
                    'summary': '随着AI数据中心建设加速，电力需求预测大幅上调。Constellation Energy和Vistra等核能及电力供应商股价近期表现亮眼。分析师预计这一趋势将持续到2030年。',
                    'source': 'MarketWatch',
                    'author': 'Energy Analyst',
                    'link': '#'
                },
                {
                    'title': 'CEG获大型数据中心供电合同，订单积压创新高',
                    'summary': 'Constellation Energy宣布与多家科技巨头签署长期供电协议，为公司核电机组提供稳定收入。CEO表示这是公司历史上最大的订单增长期，预计未来将加大在核电重启方面的投资。',
                    'source': 'Bloomberg',
                    'author': 'Energy Desk',
                    'link': '#'
                },
            ],
            'market': [
                {
                    'title': '美联储暗示年内可能降息，市场情绪回暖',
                    'summary': '最新美联储会议纪要显示，多数委员认为如果通胀继续回落，年内启动降息是合适的。市场对此反应积极，科技股领涨，标普500指数逼近历史高点。',
                    'source': 'Financial Times',
                    'author': 'Fed Watcher',
                    'link': '#'
                },
                {
                    'title': '纳斯达克突破关键阻力位，技术分析师看好后市',
                    'summary': '纳斯达克指数突破17000点关口，成交量配合放大。技术分析师指出，AI热潮和流动性改善是主要推动力，建议关注半导体和软件板块的配置机会。',
                    'source': 'Barron\'s',
                    'author': 'Technical Analyst',
                    'link': '#'
                },
            ]
        }
    
    def fetch_all_news(self, use_mock: bool = False) -> Dict[str, List[Dict]]:
        """
        抓取所有相关新闻
        
        Args:
            use_mock: 是否使用模拟数据（用于测试）
            
        Returns:
            Dict[str, List[Dict]]: 按类别分类的新闻
        """
        if use_mock:
            return self.get_mock_news()
            
        # RSS 源配置
        rss_feeds = {
            'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
            'MarketWatch': 'https://feeds.marketwatch.com/marketwatch/topstories',
        }
        
        # 抓取所有 RSS
        all_articles = self.fetch_multiple_rss(rss_feeds)
        
        # 关键词配置
        ai_keywords = ['NVIDIA', 'NVDA', 'AI', 'artificial intelligence', 'Microsoft', 'MSFT', 
                      'Google', 'GOOGL', 'AMD', 'Tesla', 'TSLA', 'TSMC', 'TSM', 'OpenAI', 
                      'chatgpt', 'GPU', 'data center']
        
        power_keywords = ['nuclear', 'energy', 'power', 'CEG', 'VST', 'Constellation', 
                         'Vistra', 'electricity', 'utility', 'grid']
        
        market_keywords = ['S&P 500', 'SPX', 'nasdaq', 'fed', 'federal reserve', 
                          'interest rate', 'inflation', 'market', 'stock']
        
        # 分类新闻
        ai_news = self.search_news_by_keywords(all_articles, ai_keywords)
        power_news = self.search_news_by_keywords(all_articles, power_keywords)
        market_news = self.search_news_by_keywords(all_articles, market_keywords)
        
        # 去重
        ai_news = self.deduplicate_news(ai_news)[:5]
        power_news = self.deduplicate_news(power_news)[:5]
        market_news = self.deduplicate_news(market_news)[:5]
        
        # 如果没有抓取到足够新闻，补充模拟数据
        mock = self.get_mock_news()
        if len(ai_news) < 3:
            ai_news.extend(mock['ai'][:3-len(ai_news)])
        if len(power_news) < 2:
            power_news.extend(mock['power'][:2-len(power_news)])
        if len(market_news) < 2:
            market_news.extend(mock['market'][:2-len(market_news)])
            
        return {
            'ai': ai_news,
            'power': power_news,
            'market': market_news,
        }


# 全局新闻抓取器实例
news_scraper = NewsScraper()


if __name__ == "__main__":
    # 测试
    scraper = NewsScraper()
    
    print("测试抓取 RSS...")
    articles = scraper.fetch_rss_feed('https://finance.yahoo.com/news/rssindex', 'Yahoo Finance')
    print(f"获取到 {len(articles)} 条新闻")
    if articles:
        print(f"第一条: {articles[0]['title']}")
    
    print("\n测试获取所有新闻（使用模拟数据）...")
    news = scraper.fetch_all_news(use_mock=True)
    for category, items in news.items():
        print(f"\n{category}: {len(items)} 条")
        for item in items[:2]:
            print(f"  - {item['title'][:50]}...")
