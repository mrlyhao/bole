# -*- coding: utf-8 -*-
import scrapy
import re


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    def parse(self, response):
        pass

    def start_requsts(self):
        return [scrapy.Request('https://www.zhihu.com/#signin',callback=self.login)]

    def login(self,response):
        response_text = response.text.replace('&quot;','')[5000:]
        test = re.match(r'.*xsrf(.*?)xUDID', response_text)
        if test:
            xsrf = (test.group(1))
            return [scrapy.FormRequest(#scrapy.FormRequests相当于post
                url= 'https://www.zhihu.com/login//phone_num',
                formdata={
                    '_xsrf':xsrf,
                    'phone_num':'15538979313',
                    'password':'liyuanhao'
                }
            )
            ]