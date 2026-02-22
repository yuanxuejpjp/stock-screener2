"""
数据获取模块 - 获取股价、指数、宏观指标等
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from typing import Dict, Optional, Tuple, List
import time

class DataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 缓存5分钟
        
    def _get_from_cache(self, key: str):
        """从缓存获取数据"""
        if key in self.cache and key in self.cache_time:
            if time.time() - self.cache_time[key] < self.cache_duration:
                return self.cache[key]
        return None
    
    def _set_cache(self, key: str, value):
        """设置缓存"""
        self.cache[key] = value
        self.cache_time[key] = time.time()
        
    def get_stock_data(self, ticker: str) -> Optional[Dict]:
        """
        获取单个股票数据
        
        Returns:
            Dict: 包含股票各项数据的字典
        """
        cache_key = f"stock_{ticker}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 获取历史数据计算技术指标
            hist = stock.history(period="1mo")
            
            # 计算RSI
            rsi = self._calculate_rsi(hist)
            
            # 计算移动平均线
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
            
            # 当前价格
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            prev_close = info.get('previousClose')
            
            # 计算涨跌幅
            change = None
            change_pct = None
            if current_price and prev_close and prev_close > 0:
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
            data = {
                'ticker': ticker,
                'name': info.get('shortName') or info.get('longName'),
                'current_price': current_price,
                'previous_close': prev_close,
                'change': change,
                'change_pct': change_pct,
                'volume': info.get('volume') or info.get('regularMarketVolume'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'rsi': rsi,
                'ma20': ma20,
                'ma50': ma50,
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'beta': info.get('beta'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'timestamp': datetime.now(),
            }
            
            self._set_cache(cache_key, data)
            return data
            
        except Exception as e:
            print(f"获取 {ticker} 数据失败: {e}")
            return None
    
    def get_index_data(self, symbol: str) -> Optional[Dict]:
        """
        获取指数数据
        
        Args:
            symbol: 指数代码，如 '^GSPC', '^IXIC'
        """
        cache_key = f"index_{symbol}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        try:
            index = yf.Ticker(symbol)
            info = index.info
            
            current = info.get('regularMarketPrice') or info.get('previousClose')
            prev_close = info.get('previousClose')
            
            change = None
            change_pct = None
            if current and prev_close and prev_close > 0:
                change = current - prev_close
                change_pct = (change / prev_close) * 100
                
            data = {
                'symbol': symbol,
                'name': info.get('shortName') or info.get('longName'),
                'current': current,
                'previous_close': prev_close,
                'change': change,
                'change_pct': change_pct,
                'timestamp': datetime.now(),
            }
            
            self._set_cache(cache_key, data)
            return data
            
        except Exception as e:
            print(f"获取指数 {symbol} 数据失败: {e}")
            return None
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """
        获取 CNN 恐惧贪婪指数
        """
        cache_key = "fear_greed"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            response = requests.get(
                'https://production.dataviz.cnn.io/index/fearandgreed/graphdata',
                headers=headers,
                timeout=10
            )
            data = response.json()
            
            score = None
            if 'fear_and_greed' in data:
                score = data['fear_and_greed'].get('score')
            elif 'score' in data:
                score = data['score']
                
            if score is not None:
                level = self._interpret_fear_greed(score)
                result = {
                    'score': score,
                    'level': level,
                    'timestamp': datetime.now(),
                }
                self._set_cache(cache_key, result)
                return result
                
        except Exception as e:
            print(f"获取恐惧贪婪指数失败: {e}")
            
        return None
    
    def get_vix(self) -> Optional[Dict]:
        """获取 VIX 波动率指数"""
        return self.get_index_data('^VIX')
    
    def batch_get_stocks(self, tickers: List[str]) -> Dict[str, Dict]:
        """
        批量获取股票数据
        
        Args:
            tickers: 股票代码列表
            
        Returns:
            Dict: 股票代码到数据的映射
        """
        results = {}
        for ticker in tickers:
            data = self.get_stock_data(ticker)
            if data:
                results[ticker] = data
            time.sleep(0.2)  # 避免请求过快
        return results
    
    def get_sector_performance(self) -> Dict[str, float]:
        """
        获取板块表现（使用板块ETF作为代理）
        """
        sector_etfs = {
            'Technology': 'XLK',
            'Financial': 'XLF',
            'Healthcare': 'XLV',
            'Energy': 'XLE',
            'Utilities': 'XLU',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Communication': 'XLC',
        }
        
        performance = {}
        for sector, etf in sector_etfs.items():
            data = self.get_stock_data(etf)
            if data and data.get('change_pct') is not None:
                performance[sector] = data['change_pct']
                
        return performance
    
    def _calculate_rsi(self, hist: pd.DataFrame, period: int = 14) -> Optional[float]:
        """计算 RSI 指标"""
        try:
            if len(hist) < period + 1:
                return None
                
            closes = hist['Close'].values
            deltas = closes[1:] - closes[:-1]
            
            gains = deltas.copy()
            losses = deltas.copy()
            gains[gains < 0] = 0
            losses[losses > 0] = 0
            losses = -losses
            
            avg_gain = gains[:period].mean()
            avg_loss = losses[:period].mean()
            
            for i in range(period, len(gains)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                return 100
                
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return round(rsi, 1)
            
        except:
            return None
    
    def _interpret_fear_greed(self, score: float) -> str:
        """解读恐惧贪婪指数"""
        if score < 25:
            return "极度恐惧"
        elif score < 45:
            return "恐惧"
        elif score <= 55:
            return "中性"
        elif score <= 75:
            return "贪婪"
        else:
            return "极度贪婪"
    
    def is_market_open(self) -> bool:
        """
        判断美股市场是否开盘（简化判断）
        """
        now = datetime.now()
        # 美股开盘时间：周一到周五，9:30 - 16:00 ET
        # 这里简化判断，实际需要根据时区转换
        if now.weekday() >= 5:  # 周六周日
            return False
        return True


# 全局数据获取器实例
data_fetcher = DataFetcher()


if __name__ == "__main__":
    # 测试
    fetcher = DataFetcher()
    
    print("测试获取股票数据...")
    nvda = fetcher.get_stock_data('NVDA')
    print(f"NVDA: {nvda}")
    
    print("\n测试获取指数数据...")
    spx = fetcher.get_index_data('^GSPC')
    print(f"S&P 500: {spx}")
    
    print("\n测试获取恐惧贪婪指数...")
    fg = fetcher.get_fear_greed_index()
    print(f"Fear & Greed: {fg}")
