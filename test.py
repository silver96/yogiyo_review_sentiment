from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import json
import requests
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome(executable_path='../chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

def scroll_down():
    pre_height = driver.execute_script("return document.body.scrollHeight") # 현재 스크롤 위치 저장
    try_num = 0
    while True :
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # 스크롤을 가장 아래로 내린다
        time.sleep(1)
        cur_height = driver.execute_script("return document.body.scrollHeight")  # 현재 스크롤을 저장한다.
        try_num += 1
        # print(try_num)
        if pre_height == cur_height :
            break
        else:
            pre_height = cur_height
    driver.implicitly_wait(100)
    
    

def go_page(region):
    # url입력
    url = "https://www.yogiyo.co.kr/mobile/#" # 사이트 입력
    driver.get(url) # 사이트 오픈
    driver.maximize_window() # 전체장
    driver.implicitly_wait(1) # 2초 지연

    # 검색창 선택
    xpath = '''//*[@id="search"]/div/form/input'''  # 검색창
    element = driver.find_element_by_xpath(xpath)
    element.clear()
    driver.implicitly_wait(1)

    # 검색창 입력

    # value = input("지역을 입력하세요")
    value = region
    element.send_keys(value)
    driver.implicitly_wait(1)

    # 검색버튼 클릭
    search_xpath = '''//*[@id="button_search_address"]/button[2]'''
    search = driver.find_element_by_xpath(search_xpath)
    driver.execute_script("arguments[0].click();", search)


    # 검색 콤보상자 선택
    search_result_selector = '#search > div > form > ul > li:nth-child(3) > a'
    search_result = driver.find_element_by_css_selector(search_result_selector)
    driver.execute_script("arguments[0].click();", search_result)
    driver.implicitly_wait(3)

    errors = 0
    # 페이지 소스 출력
    html = driver.page_source
    html_source = BeautifulSoup(html, 'html.parser')
    # print(html_source)
    store_list = []
    stores = driver.find_elements_by_class_name('col-sm-6')
    stores_num = len(list(set(html_source.find_all('div', class_='restaurant-name ng-binding'))))
    for s in stores:
        store_list.append(s)
        # print(s.text)
    # print(len(store_list))
    stores_num = len(list(set(stores)))
    stores_num = list(range(stores_num))
    print('stores_num : ', stores_num)
    scroll_down()
    return stores_num

def goto_store(num):
    cnt_error = 0
    try:
        scroll_down()
        #상점 이동
        in_store_xpath = f'''//*[@id="content"]/div/div[4]/div/div[2]/div[{num+1}]/div/table/tbody/tr/td[2]'''
        in_store = driver.find_element_by_xpath(in_store_xpath)
        time.sleep(2)
        store_name = in_store.text
        store_name = store_name.split()[0]
        print('store_name :', store_name)
        # in_store.click()
        driver.execute_script("arguments[0].click();", in_store)
        # ActionChains(driver).double_click(in_store)
        driver.implicitly_wait(3)
        #리뷰 탭 들어가기
        review_btn_xpath = '//*[@id="content"]/div[2]/div[1]/ul/li[2]/a'
        review_btn = driver.find_element_by_xpath(review_btn_xpath)
        driver.execute_script("arguments[0].click();", review_btn)
        driver.implicitly_wait(3)
        print(f'{store_name} get review btn')
        #리뷰 더보기
        i = 0
        review_errors = 0
        while True:
            i += 1
            var = i*10 + 2
            plus_btn_xpath = f'/html/body/div[6]/div[2]/div[1]/div[5]/ul/li[{var}]/a'
            # print(plus_btn_xpath)
            try:
                plus_btn = driver.find_element_by_xpath(plus_btn_xpath)
                # plus_btn.click()
                driver.execute_script("arguments[0].click();", plus_btn)
                print(i)
            except Exception as error:
                review_error_string = str(error)
                print(review_error_string)
                review_errors += 1
            if review_errors > 2:
                break
    except Exception as error:
        error_string = str(error)
        print(error_string)
    return store_name
        
def get_reviews(store_name):
    store_name = store_name
    html = driver.page_source
    html_source = BeautifulSoup(html, 'html.parser')
    reviews = html_source.find_all('p', attrs={'ng-show':'review.comment',
                                              'ng-bind-html':'review.comment|strip_html'})
    reviews = [r.text for r in reviews]
    taste_star = html_source.find_all('span', attrs={'class':'points ng-binding',
                                                       'ng-show':"review.rating_taste > 0"})
    taste_star = [t.text for t in taste_star]
    quantity_star = html_source.find_all('span', attrs={'class':'points ng-binding',
                                                       'ng-show':"review.rating_quantity > 0"})
    quantity_star = [q.text for q in quantity_star]
    delivery_star = html_source.find_all('span', attrs={'class':'points ng-binding',
                                                       'ng-show':"review.rating_delivery > 0"})
    delivery_star = [d.text for d in delivery_star]
    stars = {'taste':taste_star, 'quantity':quantity_star, 'delivery':delivery_star}
    driver.implicitly_wait(2)
      
    return reviews, stars


def before_get_review(region):
    store_num = go_page(region)
    return store_num


def get_total_data(parameter):
    region = parameter[0]
    num = parameter[1]
    driver.implicitly_wait(2)
    before_get_review(region)
    store_name=goto_store(num)
    print(f"{num+1} go to store completed")
    reviews, stars = get_reviews(store_name)
    driver.back()
    driver.implicitly_wait(3)
    print(num+1, '뒤로가기 완료')
    print(f'finish {store_name} job completed') 
    return store_name, reviews, stars
