# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
import MySQLdb
from scrapy.exporters import JsonItemExporter

class BolePipeline(object):
    def process_item(self, item, spider):
        return item
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost','root','liyuanhao9286A','lyh',charset='utf8',use_unicode = True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_acticle(title,url,create_date,fav_nums)       
             VALUES (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['create_date'],item['fav_nums']))
        self.conn.commit()

class JsonExporterPipleline(object):
    def __init__(self):
        # 调用scrapy 提供的json export 导出josn文件
        self.file = open('articleexport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding = 'utf-8',ensure_ascii = False)
        self.exporter.start_exporting()

    def sclosed_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

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
    def item_completed(self, results, item, info):
        for ok,value in results:
            image_file_path = value['path']
        item['front_image_path'] = image_file_path
        return item
