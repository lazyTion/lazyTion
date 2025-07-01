#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

# Add the current directory to the path so we can import the modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from crawler import QingdaoFoodCrawler
from app import app

def main():
    """
    Main function to run either the crawler or the web interface.
    """
    parser = argparse.ArgumentParser(description='青岛黄岛美食爬虫')
    parser.add_argument('--mode', choices=['crawl', 'web'], default='web',
                        help='运行模式: crawl (仅爬取数据) 或 web (启动Web界面)')
    parser.add_argument('--sources', nargs='+', choices=['dianping', 'meituan'], default=['dianping', 'meituan'],
                        help='数据来源: dianping (大众点评) 和/或 meituan (美团)')
    parser.add_argument('--pages', type=int, default=3,
                        help='每个来源爬取的页数 (默认: 3)')
    parser.add_argument('--port', type=int, default=12000,
                        help='Web服务器端口 (默认: 12000)')
    
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    if args.mode == 'crawl':
        # Run crawler only
        print(f"开始爬取数据，来源: {', '.join(args.sources)}，每个来源爬取 {args.pages} 页")
        crawler = QingdaoFoodCrawler(output_dir=data_dir)
        csv_path, json_path = crawler.run(sources=args.sources, pages_per_source=args.pages)
        
        print(f"爬取完成！共获取 {len(crawler.restaurants)} 家餐厅信息")
        print(f"数据已保存至:")
        print(f"CSV: {csv_path}")
        print(f"JSON: {json_path}")
    else:
        # Run web interface
        print(f"启动Web界面，访问 http://localhost:{args.port} 查看")
        app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == "__main__":
    main()