import requests
try:
    import cookielib#python2获取本地cookie
except:
    import http.cookiejar as cookielib#python3获取本地cookie

import re
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookies未能加载成功')


agent = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"
headers = {
    'host':'www.zhihu.com',
    'Referer':"https://www.zhihu.com/signup?next=%2F",
    'User-Agent': agent
}

def get_xsrf():
    # 获取xsrf code
    response = session.get('https://www.zhihu.com',headers=headers)
    html = response.text.replace('&quot;','')[5000:]
    html1 = 'token:{xsrf:5a50e677-6958-44ab-9506-ad41761bb1d4,xUDID:ABAtD-xbCA2PTo316H0m2oLVh_xzxnDTb54=}'
    test = re.match(r'.*xsrf(.*?)xUDID',html)
    if test:
        return(test.group(1))
    else:
        return ''

def get_index():
    response = session.get('https://www.zhihu.com', headers=headers)
    with open('index_page.html','wb') as f:
        f.write(response.content)
    print('ok')

def zhihu_login(account,password):
    print('手机号码登录')
    post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    post_data = {
        '_xsrf':get_xsrf(),
        'username':account,
        'password':password
    }
    a = requests.post(post_url,data=post_data,headers=headers)
    response = session.post(post_url,data=post_data,headers=headers)
    print(a)
    session.cookies.save()
zhihu_login('807552114@qq.com','liyuanhao9286A')
# get_index()