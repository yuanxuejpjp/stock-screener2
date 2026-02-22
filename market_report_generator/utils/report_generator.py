"""
报告生成模块 - 生成每日市场分析报告
"""

from datetime import datetime
from typing import Dict, List, Optional
import os
from .data_fetcher import data_fetcher
from .news_scraper import news_scraper


class ReportGenerator:
    """市场分析报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.fetcher = data_fetcher
        self.scraper = news_scraper
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_report(self, 
                       ai_stocks: Dict[str, str],
                       power_stocks: Dict[str, str],
                       market_indices: Dict[str, str],
                       use_mock_news: bool = False) -> str:
        """
        生成完整的市场分析报告
        
        Args:
            ai_stocks: AI板块股票字典 {代码: 名称}
            power_stocks: 电力板块股票字典 {代码: 名称}
            market_indices: 市场指数字典 {代码: 名称}
            use_mock_news: 是否使用模拟新闻数据
            
        Returns:
            str: 生成的报告文本（Markdown格式）
        """
        print("正在获取市场数据...")
        
        # 获取市场数据
        market_data = self._get_market_data(market_indices)
        ai_data = self._get_sector_data(ai_stocks)
        power_data = self._get_sector_data(power_stocks)
        fear_greed = self.fetcher.get_fear_greed_index()
        vix = self.fetcher.get_vix()
        
        print("正在抓取新闻资讯...")
        
        # 获取新闻
        news = self.scraper.fetch_all_news(use_mock=use_mock_news)
        
        print("正在生成报告...")
        
        # 生成报告各部分
        report = self._build_report(
            market_data=market_data,
            ai_data=ai_data,
            power_data=power_data,
            fear_greed=fear_greed,
            vix=vix,
            news=news
        )
        
        return report
    
    def _get_market_data(self, indices: Dict[str, str]) -> Dict[str, Dict]:
        """获取市场指数数据"""
        data = {}
        for symbol, name in indices.items():
            index_data = self.fetcher.get_index_data(symbol)
            if index_data:
                data[symbol] = index_data
        return data
    
    def _get_sector_data(self, stocks: Dict[str, str]) -> Dict[str, Dict]:
        """获取板块股票数据"""
        return self.fetcher.batch_get_stocks(list(stocks.keys()))
    
    def _build_report(self,
                     market_data: Dict[str, Dict],
                     ai_data: Dict[str, Dict],
                     power_data: Dict[str, Dict],
                     fear_greed: Optional[Dict],
                     vix: Optional[Dict],
                     news: Dict[str, List[Dict]]) -> str:
        """构建报告内容"""
        
        # 当前日期
        today = datetime.now()
        date_str = today.strftime('%Y年%m月%d日')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()]
        full_date = f"{date_str} {weekday}"
        
        # 判断市场状态
        market_open = self.fetcher.is_market_open()
        market_status = "🟢 交易中" if market_open else "⚪ 休市"
        
        # 构建报告
        report_lines = [
            f"# 📊 每日市场分析报告",
            f"",
            f"**报告日期**: {full_date}  ",
            f"**生成时间**: {today.strftime('%H:%M:%S')}  ",
            f"**市场状态**: {market_status}",
            f"",
            f"---",
            f"",
        ]
        
        # 市场概览
        report_lines.extend(self._build_market_overview(market_data, fear_greed, vix))
        
        # AI板块
        report_lines.extend(self._build_ai_section(ai_data, news.get('ai', [])))
        
        # 电力板块
        report_lines.extend(self._build_power_section(power_data, news.get('power', [])))
        
        # 资讯要点
        report_lines.extend(self._build_news_section(news))
        
        # 总结
        report_lines.extend(self._build_summary(market_data, ai_data, power_data, fear_greed))
        
        # 免责声明
        report_lines.extend([
            f"",
            f"---",
            f"",
            f"*免责声明：本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*",
            f"*数据来源：Yahoo Finance, CNN Fear & Greed Index, 各大财经媒体*",
            f"*报告生成时间: {today.strftime('%Y-%m-%d %H:%M:%S')}*",
        ])
        
        return '\n'.join(report_lines)
    
    def _build_market_overview(self, 
                               market_data: Dict[str, Dict],
                               fear_greed: Optional[Dict],
                               vix: Optional[Dict]) -> List[str]:
        """构建市场概览部分"""
        lines = [
            f"## 📈 市场概览",
            f"",
            f"### 大盘指数",
            f"",
            f"| 指数 | 当前点位 | 日涨跌 | 涨跌幅 |",
            f"|------|----------|--------|--------|",
        ]
        
        # 指数数据表
        for symbol, data in market_data.items():
            name = data.get('name', symbol)
            current = data.get('current', 'N/A')
            change = data.get('change', 0)
            change_pct = data.get('change_pct', 0)
            
            if current != 'N/A':
                current_str = f"{current:,.2f}" if isinstance(current, (int, float)) else str(current)
                change_str = f"{change:+.2f}" if isinstance(change, (int, float)) else "N/A"
                change_pct_str = f"{change_pct:+.2f}%" if isinstance(change_pct, (int, float)) else "N/A"
                
                # 涨跌颜色标记
                if isinstance(change, (int, float)):
                    emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                else:
                    emoji = "⚪"
                    
                lines.append(f"| {name} | {current_str} | {emoji} {change_str} | {change_pct_str} |")
        
        lines.extend([
            f"",
            f"### 市场情绪指标",
            f"",
        ])
        
        # 恐惧贪婪指数
        if fear_greed:
            score = fear_greed.get('score', 'N/A')
            level = fear_greed.get('level', 'N/A')
            lines.append(f"- **CNN 恐惧贪婪指数**: {score} ({level})")
        else:
            lines.append(f"- **CNN 恐惧贪婪指数**: 数据获取失败")
        
        # VIX
        if vix and vix.get('current'):
            vix_value = vix.get('current', 'N/A')
            lines.append(f"- **VIX 波动率指数**: {vix_value}")
        else:
            lines.append(f"- **VIX 波动率指数**: 数据获取失败")
        
        lines.append(f"")
        
        return lines
    
    def _build_ai_section(self, ai_data: Dict[str, Dict], news: List[Dict]) -> List[str]:
        """构建AI板块分析部分"""
        lines = [
            f"## 🤖 AI 板块分析",
            f"",
            f"### 重点股票表现",
            f"",
            f"| 股票 | 公司名称 | 当前价格 | 日涨跌 | RSI | 趋势 |",
            f"|------|----------|----------|--------|-----|------|",
        ]
        
        # 股票数据表
        for ticker in ['NVDA', 'MSFT', 'GOOGL', 'AMD', 'TSLA', 'TSM']:
            data = ai_data.get(ticker, {})
            if data:
                name = data.get('name', ticker)
                price = data.get('current_price', 'N/A')
                change_pct = data.get('change_pct', 0)
                rsi = data.get('rsi', 'N/A')
                
                price_str = f"${price:.2f}" if isinstance(price, (int, float)) else str(price)
                change_str = f"{change_pct:+.2f}%" if isinstance(change_pct, (int, float)) else "N/A"
                rsi_str = f"{rsi:.1f}" if isinstance(rsi, (int, float)) else str(rsi)
                
                # 趋势判断
                if isinstance(rsi, (int, float)):
                    if rsi > 70:
                        trend = "超买"
                    elif rsi < 30:
                        trend = "超卖"
                    else:
                        trend = "中性"
                else:
                    trend = "N/A"
                
                lines.append(f"| {ticker} | {name} | {price_str} | {change_str} | {rsi_str} | {trend} |")
        
        lines.extend([
            f"",
            f"### 板块动态",
            f"",
        ])
        
        # 计算板块平均涨跌幅
        changes = [d.get('change_pct', 0) for d in ai_data.values() if d.get('change_pct') is not None]
        if changes:
            avg_change = sum(changes) / len(changes)
            lines.append(f"- AI板块今日平均涨跌幅: **{avg_change:+.2f}%**")
        
        # 板块强势股
        if ai_data:
            best = max(ai_data.items(), key=lambda x: x[1].get('change_pct', -999) if x[1] else -999)
            worst = min(ai_data.items(), key=lambda x: x[1].get('change_pct', 999) if x[1] else 999)
            if best[1] and best[1].get('change_pct') is not None:
                lines.append(f"- 板块最强: **{best[0]}** ({best[1].get('change_pct', 0):+.2f}%)")
            if worst[1] and worst[1].get('change_pct') is not None:
                lines.append(f"- 板块最弱: **{worst[0]}** ({worst[1].get('change_pct', 0):+.2f}%)")
        
        lines.append(f"")
        
        return lines
    
    def _build_power_section(self, power_data: Dict[str, Dict], news: List[Dict]) -> List[str]:
        """构建电力板块分析部分"""
        lines = [
            f"## ⚡ 电力板块分析",
            f"",
            f"### 重点股票表现",
            f"",
            f"| 股票 | 公司名称 | 当前价格 | 日涨跌 | RSI | 趋势 |",
            f"|------|----------|----------|--------|-----|------|",
        ]
        
        # 股票数据表
        for ticker in ['CEG', 'VST']:
            data = power_data.get(ticker, {})
            if data:
                name = data.get('name', ticker)
                price = data.get('current_price', 'N/A')
                change_pct = data.get('change_pct', 0)
                rsi = data.get('rsi', 'N/A')
                
                price_str = f"${price:.2f}" if isinstance(price, (int, float)) else str(price)
                change_str = f"{change_pct:+.2f}%" if isinstance(change_pct, (int, float)) else "N/A"
                rsi_str = f"{rsi:.1f}" if isinstance(rsi, (int, float)) else str(rsi)
                
                if isinstance(rsi, (int, float)):
                    if rsi > 70:
                        trend = "超买"
                    elif rsi < 30:
                        trend = "超卖"
                    else:
                        trend = "中性"
                else:
                    trend = "N/A"
                
                lines.append(f"| {ticker} | {name} | {price_str} | {change_str} | {rsi_str} | {trend} |")
        
        lines.extend([
            f"",
            f"### 板块动态",
            f"",
        ])
        
        # 计算板块平均涨跌幅
        changes = [d.get('change_pct', 0) for d in power_data.values() if d.get('change_pct') is not None]
        if changes:
            avg_change = sum(changes) / len(changes)
            lines.append(f"- 电力板块今日平均涨跌幅: **{avg_change:+.2f}%**")
        
        # 新闻驱动的分析
        if news:
            lines.append(f"- 受数据中心电力需求增长驱动，核能及电力供应商关注度提升")
        
        lines.append(f"")
        
        return lines
    
    def _build_news_section(self, news: Dict[str, List[Dict]]) -> List[str]:
        """构建资讯要点部分"""
        lines = [
            f"## 📰 市场资讯要点",
            f"",
        ]
        
        # AI板块资讯
        ai_news = news.get('ai', [])
        if ai_news:
            lines.extend([
                f"### 🤖 AI 板块相关",
                f"",
            ])
            for i, article in enumerate(ai_news[:3], 1):
                title = article.get('title', '')
                summary = article.get('summary', '')
                source = article.get('source', 'Unknown')
                
                # 简化摘要
                if summary:
                    # 清理HTML标签
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)
                    # 限制长度
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                
                lines.append(f"**{i}. {title}**")
                lines.append(f"")
                lines.append(f"> {summary if summary else title}")
                lines.append(f"> ")
                lines.append(f"> *来源: {source}*")
                lines.append(f"")
        
        # 电力板块资讯
        power_news = news.get('power', [])
        if power_news:
            lines.extend([
                f"### ⚡ 电力板块相关",
                f"",
            ])
            for i, article in enumerate(power_news[:2], 1):
                title = article.get('title', '')
                summary = article.get('summary', '')
                source = article.get('source', 'Unknown')
                
                if summary:
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                
                lines.append(f"**{i}. {title}**")
                lines.append(f"")
                lines.append(f"> {summary if summary else title}")
                lines.append(f"> ")
                lines.append(f"> *来源: {source}*")
                lines.append(f"")
        
        # 宏观市场资讯
        market_news = news.get('market', [])
        if market_news:
            lines.extend([
                f"### 📊 宏观市场相关",
                f"",
            ])
            for i, article in enumerate(market_news[:2], 1):
                title = article.get('title', '')
                summary = article.get('summary', '')
                source = article.get('source', 'Unknown')
                
                if summary:
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                
                lines.append(f"**{i}. {title}**")
                lines.append(f"")
                lines.append(f"> {summary if summary else title}")
                lines.append(f"> ")
                lines.append(f"> *来源: {source}*")
                lines.append(f"")
        
        return lines
    
    def _build_summary(self,
                      market_data: Dict[str, Dict],
                      ai_data: Dict[str, Dict],
                      power_data: Dict[str, Dict],
                      fear_greed: Optional[Dict]) -> List[str]:
        """构建总结部分"""
        lines = [
            f"## 💡 今日要点总结",
            f"",
        ]
        
        # 市场情绪
        if fear_greed:
            level = fear_greed.get('level', 'N/A')
            score = fear_greed.get('score', 0)
            if isinstance(score, (int, float)):
                if score > 75:
                    lines.append(f"- **市场情绪**: 极度贪婪 ({score})，需警惕短期回调风险")
                elif score > 55:
                    lines.append(f"- **市场情绪**: 贪婪 ({score})，市场乐观情绪高涨")
                elif score > 45:
                    lines.append(f"- **市场情绪**: 中性 ({score})，建议观望或逢低布局")
                elif score > 25:
                    lines.append(f"- **市场情绪**: 恐惧 ({score})，可能存在超跌机会")
                else:
                    lines.append(f"- **市场情绪**: 极度恐惧 ({score})，反向操作窗口期")
        
        # 大盘总结
        spx = market_data.get('^GSPC', {})
        nasdaq = market_data.get('^IXIC', {})
        
        if spx and nasdaq:
            spx_change = spx.get('change_pct', 0)
            nasdaq_change = nasdaq.get('change_pct', 0)
            
            if isinstance(spx_change, (int, float)) and isinstance(nasdaq_change, (int, float)):
                if spx_change > 0 and nasdaq_change > 0:
                    lines.append(f"- **大盘走势**: 美股全线上涨，S&P 500 ({spx_change:+.2f}%) 与纳斯达克 ({nasdaq_change:+.2f}%) 同步走高")
                elif spx_change < 0 and nasdaq_change < 0:
                    lines.append(f"- **大盘走势**: 美股全线下跌，S&P 500 ({spx_change:+.2f}%) 与纳斯达克 ({nasdaq_change:+.2f}%) 同步走低")
                else:
                    lines.append(f"- **大盘走势**: 美股分化，S&P 500 ({spx_change:+.2f}%) vs 纳斯达克 ({nasdaq_change:+.2f}%)")
        
        # AI板块总结
        ai_changes = [d.get('change_pct', 0) for d in ai_data.values() if d and d.get('change_pct') is not None]
        if ai_changes:
            avg_change = sum(ai_changes) / len(ai_changes)
            if avg_change > 1:
                lines.append(f"- **AI板块**: 表现强势，平均涨幅 {avg_change:+.2f}%，AI基础设施建设需求持续驱动")
            elif avg_change < -1:
                lines.append(f"- **AI板块**: 出现调整，平均跌幅 {avg_change:.2f}%，关注支撑位的承接力度")
            else:
                lines.append(f"- **AI板块**: 窄幅震荡，平均涨跌幅 {avg_change:+.2f}%，等待方向选择")
        
        # 电力板块总结
        power_changes = [d.get('change_pct', 0) for d in power_data.values() if d and d.get('change_pct') is not None]
        if power_changes:
            avg_change = sum(power_changes) / len(power_changes)
            if avg_change > 1:
                lines.append(f"- **电力板块**: 表现活跃，平均涨幅 {avg_change:+.2f}%，受益于数据中心电力需求预期")
            elif avg_change < -1:
                lines.append(f"- **电力板块**: 出现回调，平均跌幅 {avg_change:.2f}%")
            else:
                lines.append(f"- **电力板块**: 走势平稳，平均涨跌幅 {avg_change:+.2f}%")
        
        lines.append(f"")
        
        return lines
    
    def save_report(self, report: str, filename: Optional[str] = None) -> str:
        """
        保存报告到文件
        
        Args:
            report: 报告内容
            filename: 文件名（可选，默认使用日期）
            
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"daily_report_{date_str}.md"
            
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"报告已保存至: {filepath}")
        return filepath


# 全局报告生成器实例
report_generator = ReportGenerator()
