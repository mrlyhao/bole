# 使用scrapy采集拉勾的职位数据并保存在mysql中
使用scrapy的crawlspider爬取拉勾的全站职位信息，提取后储存在mysql中。使用md5生成主键，并使用异步化接口储存。最终5小时爬取了17万条数据。

## 在middlewares中设置随机的UA
先使用fake_useragent引入随机UA库，然后应用在settings中
```
from fake_useragent import UserAgent
class RandomUserAgentMiddlware(object):
    # 随机更换user-agent
    def __init__(self,crawler):
        super(RandomUserAgentMiddlware,self).__init__()#super的作用是获取父类的初始方法，这里是获取一个类方法
        self.ua = UserAgent()#这里是引进的一个随机UA的模块
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE','random')

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)#获取crawler，其中包括setting

    def process_request(self,request,spider):
        def get_ua():
            return getattr(self.ua,self.ua_type)#getattr函数可以根据传递的后边参数的不同，获取前边函数的不同值方法，类似与'.'
        random_ua = get_ua()
        request.headers.setdefault('User_Agent',get_ua())
```

## 设置提取规则
使用scrapy的crawlspider全站爬虫爬取拉勾网，设置好start_urls,和headers。并且禁用cookies,和现在间隔。然后设置爬取规则，并且将简历信息页交由parse_job处理。从而遍历所有的简历页面。
```
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com']
    custom_settings = {
        "COOKIES_ENABLED": False,#不发送cookies
        "DOWNLOAD_DELAY": 0.01,#下载等待时间
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'user_trace_token=20171015132411-12af3b52-3a51-466f-bfae-a98fc96b4f90; LGUID=20171015132412-13eaf40f-b169-11e7-960b-525400f775ce; SEARCH_ID=070e82cdbbc04cc8b97710c2c0159ce1; ab_test_random_num=0; X_HTTP_TOKEN=d1cf855aacf760c3965ee017e0d3eb96; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DsXIrWUxpNGLE2g_bKzlUCXPTRJMHxfCs6L20RqgCpUq%26wd%3D%26eqid%3Dee53adaf00026e940000000559e354cc; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_hotjob; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAAFCAAEG50060B788C4EED616EB9D1BF30380575; _gat=1; _ga=GA1.2.471681568.1508045060; LGSID=20171015203008-94e1afa5-b1a4-11e7-9788-525400f775ce; LGRID=20171015204552-c792b887-b1a6-11e7-9788-525400f775ce',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
        }
    }

    rules = (
        Rule(LinkExtractor(allow=('zhaopin/.*',)),follow = True),#跟踪符合规则的网址
        Rule(LinkExtractor(allow=('gongsi/j\d+.html',)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback="parse_job",follow=True),#符合此规则的url交给parse——job处理
```

## 设置items和mysql插入规则
在items中设置好需要采集的页面信息属性。并使用网址的md5作为主键。将部分信息的预处理在items中完成。并使用ItemLoader提取第一个信息。然后在mysql中建立相应的表和列，设置好插入代码。

```
class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    title = scrapy.Field()#标题
    url =scrapy.Field()#网址
    url_object_id =scrapy.Field()#md5网址
    salary =scrapy.Field()#薪资
    job_city =scrapy.Field(
        input_processor=MapCompose(remove_splash),#MapCompose中为处理函数
    )#工作城市
    work_years =scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )#工作年限
    degree_need =scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )#最低学历
    job_type = scrapy.Field()#工作性质
    publish_time =scrapy.Field(
        input_processor=MapCompose(split_time),
    )#发布时间
    job_advantage =scrapy.Field()#职位诱惑
    job_desc =scrapy.Field()#工作要求
    job_addr =scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr)
    )#公司地址
    company_name =scrapy.Field()#公司名称
    company_url =scrapy.Field()#公司网址
    tags =scrapy.Field(
        input_processor=Join(',')
    )#标签
    crawl_time =scrapy.Field()#爬取时间

    def get_insert_sql(self):#插入mysql设置
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["tags"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params

def remove_splash(value):
    return value.replace('/', '')
def split_time(value):
    return value.split(' ',)[0]
def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() !='查看地图']
    return ''.join(addr_list)

class LagouJobItemLoader(ItemLoader):
    #自定义itemloader，并在spider引用代替ItemLoader
    default_output_processor = TakeFirst()
```

## 使用parse_job提取标签并在item中完成后续处理
使用css和xpath提取页面标签信息，之后传入job_item中，并交给pipelines下载。
```
    def parse_job(self, response):
        # 解析拉勾网的职位
        item_loader = LagouJobItemLoader(item= LagouJobItem(),response = response)#itemloder传入item和response
        item_loader.add_css('title','.job-name::attr(title)')
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_css('salary','.job_request p .salary::text')
        item_loader.add_xpath('job_city','//*[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('work_years', '//*[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_need', '//*[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//*[@class="job_request"]/p/span[5]/text()')
        item_loader.add_css('tags','.position-label li::text')
        item_loader.add_css('publish_time','.publish_time::text')
        item_loader.add_css('job_advantage','.job-advantage p::text')
        item_loader.add_css('job_desc','.job_bt div')
        item_loader.add_css('job_addr', '.work_addr')
        item_loader.add_css('company_name', '.job_company a img::attr(alt)')
        item_loader.add_css('company_url', '.job_company a::attr(href)')
        item_loader.add_value('crawl_time',datetime.now())
        a = item_loader
        job_item = item_loader.load_item()

        return job_item
```

## 使用pipelines的异步化插件将数据保存在mysql中
使用Twisted的异步化接口异步插入数据。并将settings中的登录信息传递进来。
```
class LagouMysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):#调用settings值的固定函数，调用方法和字典一样
        # 将参数字典化方便传入
        dbparms = dict(
            host = settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWD'],
            charset= 'utf8',
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,

        )
        # from twisted.enterprise import adbapi  Twisted为数据库提供的一个异步化接口。
        dbpool = adbapi.ConnectionPool('pymysql',**dbparms)#第一个是需要的函数名称，后边是不定长的字典参数

        return  cls(dbpool)
    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error)#处理异常

    def handle_error(self,failure):
        #处理异步插入异常
        print(failure)
    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
```
![](https://github.com/mrlyhao/bole/blob/master/bole/tools/%E6%8B%89%E5%8B%BE%E6%95%B0%E6%8D%AE%E6%88%AA%E5%9B%BE.jpg)

# python文件合集


* 使用scrapy 批量采集MM图片 [点击查看](https://github.com/mrlyhao/mmscrapy)
* 使用scrapy爬取拉勾网职位信息，并异步保存在mysql中[点击查看](https://github.com/mrlyhao/bole/tree/master/bole)
* 使用scrapy-redis爬取拉勾，Windows为slave，linux为master。[点击下载](https://github.com/mrlyhao/lagou_redis)
* [爬取小说站](https://github.com/mrlyhao/lianxi/tree/master/test1)

* 使用两种方法模拟登录微博 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E5%BE%AE%E5%8D%9A%E6%A8%A1%E6%8B%9F%E7%99%BB%E5%BD%95.py)
* 模拟登录后爬取移动端微博大V数据[点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E7%88%AC%E5%8F%96%E5%BE%AE%E5%8D%9A%E4%B8%AA%E4%BA%BA%E9%A1%B5%E9%9D%A2.py)
* 使用beautifulsoup 批量抓取MM照片 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/mm%E7%85%A7%E7%89%87%E6%89%B9%E9%87%8F%E7%88%AC%E5%8F%96.py)
* 采集后台数据，分析每本书的情况 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E4%B9%A6%E4%B8%9B%E5%90%8E%E5%8F%B0%E6%95%B0%E6%8D%AE%E9%87%87%E9%9B%86.py)
* 采集京东数据并保存在表格中 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E4%BA%AC%E4%B8%9C%E7%88%AC%E8%99%AB.py)和[pandas版本](https://github.com/mrlyhao/lianxi/blob/master/%E4%BA%AC%E4%B8%9C%E7%88%AC%E8%99%ABpandas.py)
* 简单爬取淘宝数据 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E6%B7%98%E5%AE%9D%E5%95%86%E5%93%81%E4%BF%A1%E6%81%AF%E5%AE%9A%E5%90%91%E7%88%AC%E8%99%AB.py)
* 爬取网上ip验证后储存 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E5%A4%9AIP%E4%BB%A3%E7%90%86.py)
* 爬取妹子图，解决图片重定向问题 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E5%A6%B9%E5%AD%90%E5%9B%BE.py)
* 有道翻译输入查询词，并爬取结果 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E6%9C%89%E9%81%93%E7%BF%BB%E8%AF%91%E6%8F%90%E4%BA%A4.py)
* 简单爬取今日头条 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E7%88%AC%E5%8F%96%E4%BB%8A%E6%97%A5%E5%A4%B4%E6%9D%A1.py)`和今日头条美女图` [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E7%88%AC%E5%8F%96%E4%BB%8A%E6%97%A5%E5%A4%B4%E6%9D%A1%E7%BE%8E%E5%A5%B3%E5%9B%BE.py)
* 使用selenium爬取空间说说 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E7%88%AC%E5%8F%96%E5%A5%BD%E5%8F%8B%E7%A9%BA%E9%97%B4%E8%AF%B4%E8%AF%B4.py)
* 爬取微博热搜榜，清除干扰代码后，转换成中文 [点击查看](https://github.com/mrlyhao/lianxi/blob/master/%E7%88%AC%E5%8F%96%E5%BE%AE%E5%8D%9A%E7%83%AD%E6%90%9C%E6%A6%9C.py)

