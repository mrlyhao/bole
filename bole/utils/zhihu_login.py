# -*- coding: utf-8 -*-
""" 知乎登录分为两种登录
    一是手机登录 API : https://www.zhihu.com/login/phone_num
    二是邮箱登录 API : https://www.zhihu.com/login/email

    第一步、打开首页获取_xref值，验证图片
    第二步、输入账号密码
    第三步、看是否需要验证、要则下载验证码图片，手动输入
    第四步、判断是否登录成功、登录成功后获取页面值。

    requests 与 http.cookiejar 相结合使用
    session = requests.session()
    session.cookies = http.cookiejar.LWPCookies(filename='abc')
    ...
    请求网址后
    ...
    session.cookies.save()  保存cookies

    加载cookies
    try:
        session.cookies.load(ignore_discard=True)
    except:
        print('没有cookies')
"""

import requests
from bs4 import BeautifulSoup as BS
import time
from subprocess import Popen  # 打开图片
import http.cookiejar
import re

# 模拟浏览器访问
headers = {
    'host':'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36',
    'Referer':"https://www.zhihu.com/signup?next=%2F"
}
home_url = "https://www.zhihu.com"
base_login = "https://www.zhihu.com/api/v3/oauth/sign_in"  # 一定不能写成http,否则无法登录

session = requests.session()
session.cookies = http.cookiejar.LWPCookieJar(filename='ZhiHuCookies')
# try:
#     # 加载Cookies文件
#     session.cookies.load(ignore_discard=True)
# except:
#     print("cookie未保存或cookie已过期")
# 第一步 获取_xsrf
def get_xsrf():
    # 获取xsrf code
    response = session.get('https://www.zhihu.com', headers=headers)
    html = response.text.replace('&quot;', '')[5000:]
    # html1 = 'token:{xsrf:5a50e677-6958-44ab-9506-ad41761bb1d4,xUDID:ABAtD-xbCA2PTo316H0m2oLVh_xzxnDTb54=}'
    test = re.match(r'.*xsrf(.*?)xUDID', html)
    if test:
        return (test.group(1))
    else:
        return ''
# # 第二步 根据账号判断登录方式
#     account = input("请输入您的账号：")
#     password = input("请输入您的密码：")

# 第三步 获取验证码图片
def get_gif_url():
    headers = {
        'Host': "www.zhihu.com",
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        'Accept':"application/json, text/plain, */*",
        'Accept-Language':"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        'Accept - Encoding': "gzip, deflate, br",
        'Authorization': "oauth c3cef7c66a1843f8b3a9e6a1e3160e20",
        'x - xsrftoken': "3ad2388b-1619-40bf-90e9-39044ba5c2d8",
        'x - udid': "AHCr8XlMCA2PTpfi_fmSBcHsn5hNtIRXQws=",
        'Origin': "https://www.zhihu.com",
        'Cookie': '"q_c1=af7a91997d25450d86fa8888c42c4983|1516245576000|1516245576000; capsion_ticket="2|1:0|10:1516693531|14:capsion_ticket|44:MThkYjlkODA4ZTllNGM4N2JjODBkMzNkM2VkYTQwNjM=|f9e25f6e75b470742f7a900467beaabe1007567ef06288146d21387a609a1cdb"; _zap=cdbf3626-fc53-46b1-a594-b443b4e08947; aliyungf_tc=AQAAAF/s6DZ6zA0AI/Tr3ZYgkqnYUWcu; d_c0="AHCr8XlMCA2PTpfi_fmSBcHsn5hNtIRXQws=|1516675218"; _xsrf=3ad2388b-1619-40bf-90e9-39044ba5c2d8',
        'Connection':"keep-alive",
        'Content - Length': "0"

    }
    gifUrl = "https://www.zhihu.com/api/v3/oauth/captcha?lang=cn"
    gif = session.get(gifUrl, headers=headers)
    print(gif)
    # 保存图片
    with open('code.gif', 'wb') as f:
        f.write(gif.content)
        f.close()
    # 打开图片
    Popen('code.gif', shell=True)
    # 输入验证码
    captcha = input('captcha: ')
    return captcha

def zhihu_login(username, password):
    data = {
        "username": username,
        "password": password,
        "_xsrf": get_xsrf(),
        "captcha":get_gif_url()
    }

    # # 第四步 判断account类型是手机号还是邮箱
    # if re.match("^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$", account):
    #     # 邮箱
    #     data["email"] = account
    #     base_login = base_login + "email"
    # else:
    #     # 手机号
    #     data["phone_num"] = account
    #     base_login = base_login + "phone_num"
    #
    # print(data)

    # 第五步 登录
    response = session.post(base_login, data=data, headers=headers)
    print(response.content.decode("utf-8"))

    # 第六步 保存cookie
    session.cookies.save()
try:
    # 加载Cookies文件
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未保存或cookie已过期")
    zhihu_login('807552114@qq.com','liyuanhao9286A')
finally:
    # 获取首页信息
    resp = session.get(home_url, headers=headers, allow_redirects=False)
    print(resp.content.decode("utf-8"))
