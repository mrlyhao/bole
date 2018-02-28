from selenium import webdriver
from scrapy.selector import Selector
import time

# browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
# browser.get('https://weibo.com/login.php')
# time.sleep(2)
# browser.find_element_by_css_selector('#loginname').send_keys('liyuanhaode@sina.cn')
# browser.find_element_by_css_selector('.info_list.password input[node-type="password"]').send_keys('zxcvbn')
# browser.find_element_by_css_selector('.info_list.login_btn a[node-type="submitBtn"]').click()
# for i in range(3):
#     # 使用js下拉网页到最底部
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
#     time.sleep(3)
# # browser.quit()

#设置chromedriver不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images":2}
# chrome_opt.add_experimental_option("prefs", prefs)
# browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe',chrome_options=chrome_opt)
# browser.get('https://www.taobao.com')


#phantomjs, 无界面的浏览器， 多进程情况下phantomjs性能会下降很严重

browser = webdriver.PhantomJS(executable_path=r"D:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.3.yYBVG6&id=538286972599&cm_id=140105335569ed55e27b&abbucket=15&sku_properties=10004:709990523;5919063:6536025")

print (browser.page_source)
browser.quit()

