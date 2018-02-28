# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import redis
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
import re
from w3lib.html import remove_tags
from bole.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

class BoleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def add_jobbole(value):
    return value + '-bobby'

def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, '%Y%m%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date

def get_nums(value):
    match_re = re.match(r'.*?(\d+?).*?',value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

def remove_comment_tags(value):
    #去掉tag中的评论
    if '评论' in value:
        return ''
    else:
        return value

class ArticleItemLoader(ItemLoader):
    #自定义itemloader，并在spider引用代替ItemLoader
    default_output_processor = TakeFirst()

def returen_value(value):
    return value

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date =  scrapy.Field(
        input_processor=MapCompose(date_convert),#可以传入任意数量处理函数，名称固定
   )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # output_processor=MapCompose(returen_value)  # 设置一个函数返回原值
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(',')
    )
    content = scrapy.Field()


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

class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    title = scrapy.Field()#标题
    url =scrapy.Field()#网址
    url_object_id =scrapy.Field()#md5网址
    salary =scrapy.Field()#薪资
    job_city =scrapy.Field(
        input_processor=MapCompose(remove_splash),
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

