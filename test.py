import requests 
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

# carrer: 통신사, discount:할인기한, speed: 데이터 소진시 속도, data: 데이터 제공량, title: 요금제 명, call: 통화제공, sms: 문자제공, video: 부가통화제공,
# original_price: 원래가격, discounted_price: 할인가격(실가격), description: 상세설명
class Plan: 
    def __init__(self, carrier, discount, speed, data, title, call, sms, video, original_price, discounted_price, description):
        self.carrier = carrier
        self.discount = discount
        self.speed = speed
        self.data = data 
        self.title = title
        self.call = call
        self.sms = sms
        self.video = video
        self.original_price = original_price
        self.discounted_price = discounted_price
        self.description = description
    def introduce(self): 
        for attribute, value in self.__dict__.items():
            print(f"{attribute}: {value}")
        print()

# ex
plan = Plan('SKT', '7개월할인', '+ 소진시 최대 3Mbps 무제한', '10GB', '[S]무한10GB+', '기본제공', '기본제공', 300, 35200, 3300, '8월 접수 > 9월 개통건은 9월 이벤트 적용')

# 통신사 목록
urls = {
    'eyes': "https://eyes.co.kr/payplan/info", 
    'ktm': "https://www.ktmmobile.com/rate/rateList.do" 
}

res = requests.get(urls['eyes'])
# 에러 체크, 정상일 경우만 진행, 에러 있을 경우 중단.
res.raise_for_status()

driver = webdriver.Chrome()
driver.get(urls['eyes'])

while True:
    # 더보기 버튼이 존재하면 계속 클릭
    more_button = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "더보기")]'))
    )
    if more_button.is_displayed():
        more_button.click()
        # 1초의 시간동안 로딩 대기
        # time.sleep(1)
        time.sleep(0.5)
    else:
        break  # Button is not displayed, exit the loop

expanded = driver.page_source
driver.quit()

# 응답 결과를 BeautifulSoup 객체로 변환, 제공되는 여러가지 메소드 사용 가능.
# soup = BeautifulSoup(res.text, 'html.parser')
soup = BeautifulSoup(expanded, 'html.parser')

print("---------- Data ----------")

# Plan 객체를 넣을 리스트 생성
list = []

# Find all the <div> elements with class "group"
group_divs = soup.find_all("div", class_="group")
for group_div in group_divs:
    slt_box = group_div.find("div", class_="slt-box")

    # Find the buttons within slt_box
    buttons = slt_box.find_all("button")
    # Extract information from the buttons
    button_info = [button.get_text(strip=True) for button in buttons]
    if len(button_info)==2:
        carrier = button_info[0]
        if button_info[-1]=='+':
            discount = None
            speed = button_info[-1]
        else:
            discount = button_info[-1]
            speed = None
    elif len(button_info)==3:
        carrier = button_info[0]
        discount = button_info[1]
        speed = button_info[2]

    info_box = group_div.find("div", class_="info-box")
    data = info_box.find("div", class_="txt").get_text(strip=True)
    title = info_box.find("div", class_="tit").get_text(strip=True)
    call = info_box.find("li", class_="call").get_text(strip=True)
    sms = info_box.find("li", class_="sms").get_text(strip=True)
    video = info_box.find("li", class_="video").get_text(strip=True)

    side_box = group_div.find("div", class_="side-box")
    original_price_element = side_box.find(class_="origin-price")
    if original_price_element:
        original_price = original_price_element.get_text(strip=True)
    else:
        original_price = None
    discounted_price = side_box.find("strong").get_text(strip=True)

    description_element = group_div.find("div", class_="description").find("li")
    if description_element:
        description = group_div.find("div", class_="description").find("li").get_text(strip=True)
    else: 
        description = None
    plan = Plan(carrier, discount, speed, data, title, call, sms, video, original_price, discounted_price, description)
    list.append(plan)

for item in list:
    item.introduce()
print(len(list))
