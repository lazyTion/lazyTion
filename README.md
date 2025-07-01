# 青岛黄岛美食爬虫

这是一个用于爬取青岛黄岛区美食餐厅信息的爬虫工具，包含Web界面展示功能。

## 功能特点

- 支持从多个来源爬取餐厅数据（大众点评、美团）
- 提供Web界面进行数据展示和交互
- 支持按类别、评分、来源等条件筛选餐厅
- 提供数据统计和可视化图表
- 支持导出CSV和JSON格式数据

## 技术栈

- Python 3.x
- Flask (Web框架)
- BeautifulSoup4 (HTML解析)
- Pandas (数据处理)
- Chart.js (数据可视化)
- Bootstrap 5 (前端UI)

## 项目结构

```
qingdao_food_crawler/
├── crawler.py      # 爬虫核心代码
├── app.py          # Flask Web应用
├── templates/      # HTML模板
│   └── index.html  # 主页面
└── data/           # 爬取的数据存储目录
```

## 安装与使用

### 安装依赖

```bash
pip install requests beautifulsoup4 pandas flask
```

### 运行爬虫

```bash
cd qingdao_food_crawler
python crawler.py
```

### 启动Web界面

```bash
cd qingdao_food_crawler
python app.py
```

启动后，访问 http://localhost:12000 即可打开Web界面。

## 爬虫使用说明

爬虫支持从大众点评和美团两个来源获取数据。在Web界面中，您可以：

1. 点击"开始爬取"按钮，选择数据来源和爬取页数
2. 等待爬取完成后，页面会自动刷新显示最新数据
3. 使用筛选功能按类别、评分或来源筛选餐厅
4. 点击"查看详情"查看餐厅的详细信息
5. 使用"下载数据"功能导出CSV或JSON格式的数据

## 注意事项

- 爬虫使用随机延迟和User-Agent轮换来避免被网站封禁
- 请合理设置爬取页数，避免对目标网站造成过大压力
- 爬取的数据仅用于个人学习和研究，请勿用于商业用途
- 由于目标网站可能有反爬虫措施，在实际使用时可能需要：
  - 使用代理IP轮换
  - 添加验证码识别功能
  - 使用Selenium或Playwright等工具模拟真实浏览器行为
  - 考虑使用API接口而非直接爬取网页

## 许可证

MIT