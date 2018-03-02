# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
import pymysql
import pymysql.cursors
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

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

class BolePipeline(object):
    def process_item(self, item, spider):
        return item#返回item值，因为其余的管道还要使用item
class MysqlPipeline(object):
    # 采用同步的机制写入MySQL
    def __init__(self):
        #链接数据库
        self.conn = pymysql.connect('localhost','root','liyuanhao9286A','lyh',charset='utf8',use_unicode = True)#mysql使用的是gbk，而python使用的是ut8，所以鼻血设定后两个参数，后一个参数为是否使用字符集
        #创建数据库浮标
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # 设置需要插入的行的名称
        insert_sql = """
            insert into jobbole_acticle(title,url,create_date,fav_nums)       
             VALUES (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['create_date'],item['fav_nums']))
        # 完成插入后提交
        self.conn.commit()

class JsonExporterPipleline(object):
    def __init__(self):
        # 调用scrapy 提供的json export 导出josn文件
        self.file = open('articleexport.json','wb')
        #实例化item Export
        self.exporter = JsonItemExporter(self.file,encoding = 'utf-8',ensure_ascii = False)#ensuire_ascii的作用是让中文不乱码
        # 标识exporting过程的开始
        self.exporter.start_exporting()

    def sclosed_spider(self,spider):#
        # 标识exporting过程的结束
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        # 输入每一个item
        self.exporter.export_item(item)
        return item

class MysqlTwistedPipline(object):
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
    def do_insert(self,cursor,item):
        #执行具体的插入
        insert_sql = """
            insert into jobbole_acticle(title,url,url_object_id,create_date,front_image_url,praise_nums,fav_nums,tags,content,comment_nums)       
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(insert_sql, (item['title'], item['url'],item['url_object_id'],item['create_date'], item['front_image_url'],
                                    item['praise_nums'],item['fav_nums'],item['tags'],item['content'],item['comment_nums']))

class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')
    def process_item(self, item, spider):
        lines = json.dumps(dict(item),ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item
    def spider_closed(self,spider):
        self.file.close()

class BoleImagePipeline(ImagesPipeline):
    # 下载图片函数
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok,value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item
