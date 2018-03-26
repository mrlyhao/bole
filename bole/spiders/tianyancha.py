# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class TianyanchaSpider(CrawlSpider):
    name = 'tianyancha'
    allowed_domains = ['m.tianyacha.com']
    start_urls = ['http://m.tianyacha.com/']

    rules = (
        Rule(LinkExtractor(allow=r'company/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        i = {}
        company = response.xpath('//div[@class="over-hide"]/div[1]/text()').extract_first()#公司名称

        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
#解析HTML转义符
from html.parser import HTMLParser
html_parser = HTMLParser()
a='&#x8BA1;&#x7B97;&#x673A;&#x8F6F;&#x786C;&#x4EF6;&#x6280;&#x672F;&#x5F00;&#x53D1;&#x3001;&#x6280;&#x672F;&#x670D;&#x52A1;&#x3001;&#x6280;&#x672F;&#x63A8;&#x5E7F;&#xFF1B;&#x8F6F;&#x4EF6;&#x5F00;&#x53D1;&#x3001;&#x8BBE;&#x8BA1;&#x670D;&#x52A1;&#xFF1B;&#x5E7F;&#x544A;&#x8BBE;&#x8BA1;&#x3001;&#x5236;&#x4F5C;&#x3001;&#x4EE3;&#x7406;&#x3001;&#x53D1;&#x5E03;&#xFF1B;&#x4FE1;&#x606F;&#x6280;&#x672F;&#x54A8;&#x8BE2;&#x670D;&#x52A1;&#xFF1B;&#x8BA1;&#x7B97;&#x673A;&#x7F51;&#x7EDC;&#x7CFB;&#x7EDF;&#x5DE5;&#x7A0B;&#x8BBE;&#x8BA1;&#x4E0E;&#x65BD;&#x5DE5;&#xFF1B;&#x4F01;&#x4E1A;&#x8425;&#x9500;&#x7B56;&#x5212;&#xFF1B;&#x4F53;&#x80B2;&#x8D5B;&#x4E8B;&#x7B56;&#x5212;&#xFF1B;&#x4F1A;&#x8BAE;&#x53CA;&#x5C55;&#x89C8;&#x670D;&#x52A1;&#xFF1B;&#x591A;&#x5A92;&#x4F53;&#x8BBE;&#x8BA1;&#xFF1B;&#x52A8;&#x6F2B;&#x8BBE;&#x8BA1;&#xFF1B;&#x56FE;&#x6587;&#x8BBE;&#x8BA1;&#x3001;&#x5236;&#x4F5C;&#xFF1B;&#x4EBA;&#x5DE5;&#x667A;&#x80FD;&#x4EA7;&#x54C1;&#x3001;&#x865A;&#x62DF;&#x73B0;&#x5B9E;&#x53CA;&#x589E;&#x5F3A;&#x73B0;&#x5B9E;&#x8F6F;&#x786C;&#x4EF6;&#x4EA7;&#x54C1;&#x53CA;&#x56FE;&#x5F62;&#x53EF;&#x89C6;&#x5316;&#x5F00;&#x53D1;&#x3001;&#x5E94;&#x7528;&#x53CA;&#x5176;&#x4EA7;&#x54C1;&#x6279;&#x96F6;&#x517C;&#x8425;&#x3002;&#xFF08;&#x4F9D;&#x6CD5;&#x987B;&#x7ECF;&#x5BA1;&#x6279;&#x7684;&#x9879;&#x76EE;&#xFF0C;&#x7ECF;&#x76F8;&#x5173;&#x90E8;&#x95E8;&#x5BA1;&#x6279;&#x540E;&#x65B9;&#x53EF;&#x5F00;&#x5C55;&#x7ECF;&#x8425;&#x6D3B;&#x52A8;&#xFF09;'
s = html_parser.unescape(a)
print(s)
'''
公司名称
法定代表人
经营状态
注册时间
注册资本
行业
企业类型
工商注册号
组织结构代码
统一信用代码
纳税人识别号
经营期限
核准日期
登记机关
注册地址
经营范围
股东信息
'''