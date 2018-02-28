# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from bole.items import JobBoleArticleItem,ArticleItemLoader
from bole.utils.commmon import get_md5
from scrapy.loader import ItemLoader
import datetime
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import time


class CommentSpider(scrapy.Spider):
    name = 'comment'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']
        # def __init__(self):
    #     self.browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    #     super(CommentSpider,self).__init__()
    #     dispatcher.connect(self.spider_closed,signals.spider_closed)
    #
    # def spider_closed(self,spider):
    #     # 当爬虫退出的时候关闭chrome
    #     print('Spider closed')
    #     self.browser.quit()
    # 收集伯乐在线所有404的url及404页面数
    handle_httpstatus_list = [404]

    def __init__(self, **kwargs):
        self.fail_url  = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

    def handle_spider_closed(self,spider,reason):
        self.crawler.stats.set_value('failed_urls',','.join(self.fail_url))
        pass

    def parse(self, response):
        if response.status == 404:
            self.fail_url.append(response.url)
            self.crawler.stats.inc_value("failed_url")
        post_urls = response.css('.post.floated-thumb .post-thumb a:nth-child(1)')
        for post_url in post_urls:
            url = post_url.css('::attr(href)').extract_first('')
            image_url = post_url.css('img::attr(src)').extract()
            yield Request(url = parse.urljoin(response.url,url),meta={'front_image_url':image_url},callback=self.parse_detail)
        next_url = response.css('.next.page-numbers::attr(href)').extract_first()
        if next_url:
            yield Request(url = next_url,callback=self.parse)
    def parse_detail(self,response):
        # article_item = JobBoleArticleItem()
        #提取页面具体字段
        front_image_url = response.meta.get("front_image_url",'')
        # title= response.xpath('//h1/text()').extract_first('')
        # create_date= response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first().strip().split(' ')[0]
        # try:
        #     praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # except:
        #     praise_nums = 0
        # content = response.css('.entry').extract_first('')
        # try:
        #     fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').re(r'.*?(\d+?).*?')[0]
        # except:
        #     fav_nums = 0
        # try:
        #     comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').re(r'.*?(\d+?).*?')[0]
        # except:
        #     comment_nums = 0
        # tags = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a[1]/text()').extract_first()
        # article_item['title'] = title
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['url']=response.url
        # try:
        #     create_date = datetime.datetime.strptime(create_date,'%Y%m%d').date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item['create_date']=create_date
        # article_item['front_image_url'] = front_image_url
        # article_item['praise_nums'] = praise_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['tags'] = tags
        # article_item['content'] = content
        # article_item['comment_nums'] = comment_nums

        # 通过item loader 加载item
        item_loader = ArticleItemLoader(item =JobBoleArticleItem(),response=response)
        item_loader.add_xpath('title','//h1/text()')
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_xpath('create_date','//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value('front_image_url',front_image_url)
        item_loader.add_xpath('praise_nums','//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath('fav_nums','//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath('tags','//p[@class="entry-meta-hide-on-mobile"]/a[1]/text()')
        item_loader.add_css('content','.entry')
        item_loader.add_xpath('comment_nums','//a[@href="#article-comment"]/span/text()')
        article_item = item_loader.load_item()
        yield article_item
