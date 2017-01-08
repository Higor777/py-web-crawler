# py-web-crawler
工程实践训练课程作业 <人物信息采集系统>

##1、系统构成
    此次人物信息采集系统使用 Python 2.7 实现，模块构成如下。
        日志系统 logging；
        Excel 写入模块 xlwt；	
        网络爬虫框架 Scrapy；
        HTTP 请求库 requests；
        SHELL 命令库 commands；
        关系型数据库管理系统 MySQLdb；
        HTML/XML 解析器 BeautifulSoup。

    数据源：互动百科。

##2、使用过程
    安装依赖
        sudo apt-get install python-dev libxml2-dev libxslt-dev -y
        sudo apt-get install python-twisted python-simplejson -y
        sudo pip install w3lib
  
        # /usr/bin/ld: cannot find -lz
        apt-get install zlib1g-dev

        pip install lxml
        pip install scrapy==1.0.0
        pip install beautifulsoup4

        pip  install xlwt

        pip install requests

        sudo apt-get install libmysqld-dev
        pip install MySQL-Python
        注：程序需连接MySQL数据库，程序内设定密码为“higor1234567.”，请结合实际情况在database.py内修改
        
    定义数据
        在 Reference_Data.py 中定义需要爬取的目标分类，及其相应的数据表名（英文），现举例如下，定义 12 个基本分类。
        
        categoryList = ['政治人物','中国人民解放军人物','皇帝','诗人','书法家','国家元首','各时代军事人物','科学家','内地明星','港台明星','博士生导师','诸子百家']

        categoryDict = {'政治人物':'politician','中国人民解放军人物':'GeneralofPLA','皇帝':'emperor','诗人':'poet','书法家':'calligrapher','国家元首':'head_of_the_state','各时代军事人物':'ancient_general','科学家':'scientist','内地明星':'mainland_star','港台明星':'hktw_star','博士生导师':'professor','诸子百家':'ancient_thinker'}

    程序执行
        Scrapy_Module.py [reset|export|tar]

    参数说明：
	    如果未传入参数，默认开始本次爬取，继续下面的流程。
	    如果传入 reset 参数，则重置数据库、结果文件夹。即删除数据库和结构文件夹，以及不必要的垃圾文件。结果文件夹下包含 Excel 文件、SQL 文件与 RecordedURL。之后立即结束程序。
	    如果传入 export 参数，则整理数据库现有的数据，并导出为 Excel 文件和 SQL 文件，保存在结果文件夹下。之后立即结束程序。
	    如果传入 tar 参数，则将项目文件打包。档案内容包括整个项目的代码和数据文件，其文件名称为 person_hudongbaike.tar。之后立即结束程序。

##3、文件结构
    本系统的文件结构如下。
        person_hudongbaike/ # 项目总文件夹
        ├── install.txt # 项目依赖环境
        └── Scrapy_Module # Scrapy 模块文件夹
            ├── __init__.py
            ├── scrapy.cfg # Scrapy 项目
            ├── Scrapy_Module.py # Scrapy 项目入口
            └── Scrapy_Project # Scrapy 项目文件夹
                ├── database.py # mySQL 数据库操作
                ├── __init__.py
                ├── items.py # Scrapy 项目数据项定义
                ├── pipelines.py # Scrapy 项目管道
                ├── Reference_Data.py # 相关公共数据
                ├── result # 爬取结果文件夹
                │   ├── personInfoXls # Excel 文件夹
                │   │   ├── junshirenwu.xls # 军事人物
                │   │   ├── kexuejia.xls # 科学家
                │   │   ├── mingxing.xls # 明星
                │   │   ├── shiren.xls # 诗人
                │   │   ├── zhengzhirenwu.xls # 政治人物
                │   │   └── zhuzibaijia.xls # 诸子百家
                │   ├── RecordedURL # 已记录 URL 文件夹
                │   │   └── RecordedURL # 已记录URL
                │   ├── Scrapy_Module_Person.log # 项目日志
                │   └── sql # SQL 文件夹
                │       ├── personMySQL.sql # mySQL的 SQL
                │       └── personSQLServer.sql # SQLServer的 SQL
                ├── settings.py # Scrapy 项目配置文件
                └── spiders # 蜘蛛文件
                    ├── category.py # 获取目标分类初始URL接口
                    ├── __init__.py
                    └── Scrapy_ModuleSpider.py # Scrapy 蜘蛛
