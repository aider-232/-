#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

#1.创建Chrome或Firefox浏览器对象，这会在电脑上在打开一个浏览器窗口
options = webdriver.EdgeOptions()
# 不加载图片
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
# 使用headless无界面浏览器模式和禁用gpu加速
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
service = EdgeService(executable_path=r"C:\Users\Administrator\msedgedriver.exe")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)


# In[2]:


browser = webdriver.Edge(service=service, options=options)


# In[3]:


#2.通过浏览器向服务器发送URL请求。如果能打开百度网站，说明安装成功。
browser.get("https://www.amazon.com/Best-Sellers-Automotive-Automobile-Cargo-Covers/zgbs/automotive/78990712011/ref=zg_bs_nav_automotive_3_15735551")


# In[4]:


# 判断页面是进入了狗页面还是验证码页面,并尝试解除
# 验证码页面通过验证码识别技术解除，验证失败就刷新页面重新尝试，尝试次数为5次，根据别人的试验得知准确率为0.95，每次识别可以认为是独立的，因此5次失败的概率极小。
# 狗页面通过刷新解除，尝试刷新的次数为5次，不行就返回值“检查链接是否正常”
def refresh_url(browser, a = 0):
    xpath = '//*[@id="g"]/div/a/img'
    xpath1 = '/html/body/div/div[1]/div[3]/div/div/form/div[1]/div/div/div[1]/img'
    while a < 6:
        try:
            b = browser.find_element(By.XPATH,xpath).get_attribute('alt') # 获取狗页面特征
        except:
            try:
                b = browser.find_element(By.XPATH,xpath1).get_attribute('src') # 获取验证码页面特征
            except:
                b = 1 # 若以上两个特征都获取失败，则赋值b为1
        # print(b)

        
        if b == "Sorry! Something went wrong. Please go back and try again or go to Amazon's home page.":
            browser.refresh()
            # 判断狗页面特征是否正确；若正确就刷新页面
        elif b == 1:
            a == 10000
            # 若b为1，则说明页面正常跳转，直接赋值a一个大数来跳出循环
        else:
            from amazoncaptcha import AmazonCaptcha
            captcha = AmazonCaptcha.fromlink(b) # 识别链接或路径表示的验证码
            solution = captcha.solve()#识别后返回的结果，字符型
            print(solution)
            browser.find_element(By.XPATH,'//*[@id="captchacharacters"]').send_keys(solution) # 输入验证码
            browser.find_element(By.XPATH,'/html/body/div/div[1]/div[3]/div/div/form/div[2]/div/span/span/button').click()
            # 顺便下载验证码图片...不需要的时候下面这段可以注释掉
            import requests
            from time import time
            html = requests.get(b)
            with open(fr"C:\Users\Administrator\Desktop\亚马逊验证码\{time()}.jpg", 'wb') as file:
                file.write(html.content)
        a = a + 1 # 限定重复次数为5次
    # 不知道为什么好像通过了验证码后网页都有点不正常，要刷新一下页面才行
    browser.refresh()
refresh_url(browser)


# In[5]:


# 在搜索框输入需要搜索的内容
def search_content(browser, search_text):
    browser.find_element(By.XPATH,'//*[@id="twotabsearchtextbox"]').clear()
    browser.find_element(By.XPATH,'//*[@id="twotabsearchtextbox"]').send_keys(search_text)
    browser.find_element(By.XPATH,'//*[@id="nav-search-submit-button"]').click()


# In[6]:


'''
选择亚马逊排序的方式，有
Featured:relevanceblender,
Price:Low to High:price-asc-rank,
Price:High to Low:price-desc-rank,
Avg.Customer Review:review-rank,
Newest Arrivals:date-desc-rank, 
Best Sellers:exact-aware-popularity-rank
'''
def Selection_sort(browser, xpath, sort_by):
    from selenium.webdriver.support.select import Select
    from time import sleep
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By
    sel = browser.find_element(By.XPATH,xpath)
    Select(sel).select_by_value(sort_by)
    try:
        wait = WebDriverWait(browser, 10) 
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[1]/div/span/div/div/h2'))) # 等待重新排序完成
    except:
        browser.refresh()
# xpath = '//*[@id="s-result-sort-select"]'
# sort_by = "exact-aware-popularity-rank"
# Selection_sort(browser, xpath, sort_by)


# In[7]:


# 搜集此页上的所有产品信息，并能根据需要来搜集需要的页面数
def collect_page_information(browser):
    # 创建八个空列表，来储存需要的数据
    empty_lists = []
    for _ in range(8):
        empty_lists.append([])
    
    # 先来获取这次搜索可以到达的最后页面数以及next的点击
    # page_item = browser.find_elements(By.XPATH,'//*[contains(@class, "s-pagination-item")]')
    # page_last = int(page_item[-2].text) # 显示的可以点击的最大页数
    
    from time import sleep
    # 默认的方法是爬取所有页面，想要自定义页面数量的话，自己修改page循环里面的range即可
    for page in range(1):
        print(page)
        try:
            wait = WebDriverWait(browser, 2) 
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")))
        except:
            sleep(1)
        
        # 爬取每一页中的基本产品信息
        goods = browser.find_elements(By.XPATH,'//div[@role = "listitem"]')
        # print(len(goods))
        for i in range(len(goods)):
            try:
                asin = goods[i].get_attribute('data-asin')
                print("ASIN：", asin)
            except:
                print("产品可能没有ASIN，请检查链接，ASIN已用空值代替")
                asin = ""
            empty_lists[0].append(asin)
            
            try:
                title = goods[i].find_element(By.XPATH,'.//*[@data-cy = "title-recipe"]').text
                print("产品标题：", title)
            except:
                print("产品可能没有标题，请检查链接，标题已用空值代替")
                title = ""
            empty_lists[1].append(title)
        
            # 爬取的url包含部分标题和asin可以用作核对是不是广告，但是暂时用不着了，因为有其他方式补充asin链接，可以注释掉
            #url = goods[i].find_element_by_xpath('.//a[@class = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute('href')
            #print(url)
            try:
                url = "https://www.amazon.com/dp/" + asin
                print("详情页链接：", url)
            except:
                print("产品可能没有详情页链接，请检查链接，详情页链接已用空值代替")
                url = ""
            empty_lists[2].append(url)
            
            try:
                image_url = goods[i].find_element(By.XPATH,'.//img[@class = "s-image"]').get_attribute("src")
                print("图片链接：", image_url)
            except:
                print("产品可能没有图片链接，请检查链接，图片链接已用空值代替")
                image_url = ""
            empty_lists[3].append(image_url)
        
            try: # 存在产品没有价格的情况
                price = goods[i].find_element(By.XPATH,'.//*[@data-cy = "price-recipe"]//span[@class="a-offscreen"]')
                price = browser.execute_script("return arguments[0].firstChild.textContent;", price) # 用这种方法来提取文本节点
                print("产品价格：", price)
            except:
                print("产品可能没有价格，请检查链接，价格已用空值代替")
                price = ""
            empty_lists[4].append(price)
            
            try:
                inner_text = " out of 5 stars, rating details"
                rating = goods[i].find_element(By.XPATH,'.//*[@data-cy = "reviews-block"]//a').get_attribute("aria-label")
                rating = rating.replace(inner_text, "")
                print("产品评分：", rating)
            except:
                print("产品评分：无，已用空值代替")
                rating = ""
            empty_lists[5].append(rating)
        
            try:
                n_comments = int(goods[i].find_element(By.XPATH,'.//div[@class = "a-row a-size-small"]').text)
                print("评分数量：", n_comments)
            except:
                print("评分数量：无，已用空值代替")
                n_comments = ""
            empty_lists[6].append(n_comments)
        
            try:
                n_sale = goods[i].find_element(By.XPATH,'.//*[@data-cy = "reviews-block"]/div[@class="a-row a-size-base"]').text
                print("产品销量:", n_sale)
            except:
                print("产品销量：无，已用空值代替")
                n_sale = ""
            empty_lists[7].append(n_sale)
            
            print('-'*80)
    
        # 最后再获取next的点击
        try:
            page_item = browser.find_elements(By.XPATH,'//*[contains(@class, "s-pagination-item")]')
            next = page_item[-1]
            next.click()
        except:
            pass
    
    # 创建数据框储存数据，输出xlsx格式
    import pandas as pd 
    data = {'ASIN':empty_lists[0],
            '产品标题':empty_lists[1],
           '详情页链接':empty_lists[2],
           '图片链接':empty_lists[3],
           '产品价格':empty_lists[4],
           '产品评分':empty_lists[5],
           '评分数量':empty_lists[6],
           '产品销量':empty_lists[7]}
    print(data)
    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    return df
# df = collect_page_information(browser)


# In[8]:


# 根据车型+关键词的形式来捕获商品（OS：一般倩姐会给好车型先的）
cars = pd.read_excel(r"C:\Users\Administrator\Desktop\车型.xlsx",sheet_name=0).iloc[:,0].tolist()
for i in cars:
    search_text = i + "_" + 'Side Sun Visor Replacement'
    search_content(browser, search_text)
    df = collect_page_information(browser)
    df["车型"] = search_text
    # 将数据框存储为 xlsx 文件
    df.to_excel(r"E:/Side Sun Visor Replacement/" + search_text + ".xlsx", index=False)


# In[9]:


import pandas as pd
from pathlib import Path

# 指定要遍历的文件夹路径
folder_path = Path(r"E:/Side Sun Visor Replacement/")
temp = []
# 遍历文件夹及其子文件夹中的所有文件
for file in folder_path.rglob('*'):
    if file.is_file():
        temp.append(file)

df1 = pd.read_excel(temp.pop(0))
for i in temp:
    print(i)
    df2 = pd.read_excel(i)
    df1 = pd.concat([df1, df2], ignore_index=True)
print(df1)
df1.to_excel(r"E:/Side Sun Visor Replacement/" + 'concat_df.xlsx')

