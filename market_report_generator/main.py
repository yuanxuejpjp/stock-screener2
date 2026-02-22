"""
每日市场分析报告生成器 - 主程序入口

使用方法:
    python main.py
    python main.py --mock  # 使用模拟数据
    python main.py --output reports/custom_report.md
"""

import argparse
import sys
from datetime import datetime

# 导入配置
from config import (
    AI_STOCKS, POWER_STOCKS, MARKET_INDICES,
    OUTPUT_DIR, get_current_date
)

# 导入工具模块
from utils.report_generator import report_generator


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='生成每日市场分析报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py                    # 生成今日报告（使用实时数据）
  python main.py --mock             # 使用模拟数据生成报告
  python main.py --output report.md # 指定输出文件名
        '''
    )
    
    parser.add_argument(
        '--mock', 
        action='store_true',
        help='使用模拟数据（用于测试或市场休市时）'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        default=None,
        help='指定输出文件名（默认: reports/daily_report_YYYYMMDD.md）'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='不保存到文件，仅打印到控制台'
    )
    
    return parser.parse_args()


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("📊 每日市场分析报告生成器")
    print("=" * 60)
    print(f"日期: {get_current_date()}")
    print("=" * 60)
    print()


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 打印横幅
    print_banner()
    
    # 检查是否是交易日
    today = datetime.now()
    is_weekend = today.weekday() >= 5
    
    if is_weekend:
        print("⚠️  今天是周末，美股市场休市")
        print("   将使用最近收盘数据或模拟数据")
        print()
        if not args.mock:
            response = input("是否继续使用实时数据？([y]/n): ").strip().lower()
            if response == 'n':
                args.mock = True
                print("   已切换到模拟数据模式")
                print()
    
    try:
        # 生成报告
        print("🚀 开始生成报告...")
        print("-" * 40)
        
        report = report_generator.generate_report(
            ai_stocks=AI_STOCKS,
            power_stocks=POWER_STOCKS,
            market_indices=MARKET_INDICES,
            use_mock_news=args.mock
        )
        
        print("-" * 40)
        print("✅ 报告生成完成!")
        print()
        
        # 保存或打印报告
        if args.no_save:
            print("=" * 60)
            print("📄 报告内容:")
            print("=" * 60)
            print()
            print(report)
        else:
            filepath = report_generator.save_report(report, args.output)
            print()
            print("=" * 60)
            print(f"📁 报告已保存: {filepath}")
            print("=" * 60)
            
    except KeyboardInterrupt:
        print()
        print("\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
