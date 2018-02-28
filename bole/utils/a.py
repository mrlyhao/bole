import requests
from bs4 import BeautifulSoup as BS
import time
from subprocess import Popen  # 打开图片
import http.cookiejar
import re
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
    gif = requests.get(gifUrl, headers=headers)
    gif = requests.put(gifUrl, headers=headers)
    print(gif,gif.text)
    # 保存图片
    with open('code.gif', 'wb') as f:
        f.write(gif.content)
        f.close()
    # 打开图片
    Popen('code.gif', shell=True)
    # 输入验证码
    captcha = input('captcha: ')
    return captcha
get_gif_url()