from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime
import re

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")

driver = webdriver.Chrome(options=chrome_options)

url = "https://www.kbchachacha.com/public/search/main.kbc#!?countryOrder=1&page=1&sort=-orderDate&gas=004007&useCode=002002,002003,002001,002004,002005,002008"
driver.get(url)

first_tab = driver.window_handles[0]

wait = WebDriverWait(driver, 10)
current_page = 1

def convert_birth(birth):
    birth_data = re.search(r"(\d{4})년 (\d{1,2})월", birth)
    if birth_data:
        year, month = birth_data.groups()
        return f"{year}-{month.zfill(2)}"
    return None

def convert_km(km):
    km_data = re.sub(r'[^0-9]', '', km)
    return int(km_data)

def convert_price(price):
    price_data = price.replace(",", "").replace("만원", "")
    return int(price_data) * 10000

while True:
    try:
        # 페이지에서 차량 리스트 로드
        list = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content > div.common-sub-content.fix-content > div > div.searchArea > div.searchArea__carList > div.__used-car-list > div.cs-list02.cs-list02--ratio.small-tp.generalRegist > div.list-in"))
        )
        areas = list.find_elements(By.CLASS_NAME, "area")

        for area in areas:
            # 차량 정보 추출
            item = area.find_element(By.CSS_SELECTOR, "a.item")
            name = area.find_element(By.CSS_SELECTOR, "strong.tit").text
            birth = area.find_element(By.CSS_SELECTOR, "div.first").text
            km = area.find_element(By.CSS_SELECTOR, "div.data-in span").text
            price_all = area.find_element(By.CSS_SELECTOR, "strong.pay")
            del_tags = price_all.find_elements(By.TAG_NAME, "del")

            birth = convert_birth(birth)
            km = convert_km(km)

            if del_tags:
                del_text = del_tags[0].text
                price = price_all.text.replace(del_text, "").strip()
            else:
                price = price_all.text.strip()

            price = convert_price(price)

            # 차량 상세 페이지로 이동
            item.click()
            second_tab = driver.window_handles[-1]
            driver.switch_to.window(window_name=second_tab)

            # 상세 페이지에서 데이터 수집
            detail = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#content > div:nth-child(19) > div.common-sub-content.common-container.fix-content > div.cmm-cardt-area.adj1740.adj1670 > div.car-detail-info'))
            )
            car_type = detail.find_element(By.CSS_SELECTOR, "#content > div:nth-child(19) > div.common-sub-content.common-container.fix-content > div.cmm-cardt-area.adj1740.adj1670 > div.car-detail-info > div > div.detail-info01 > table > tbody > tr:nth-child(4) > td:nth-child(2)").text

            graph = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#divMarketPriceWrap > div > div.m-price-list02'))
            )
            og_price = graph.find_element(By.CSS_SELECTOR, "#divMarketPriceNewCarGraph > div > div > svg > g:nth-child(13) > g > text:nth-child(1) > tspan").text

            og_price = convert_price(og_price)

            print(f"{name} / {birth} / {km} / {price} / {car_type} / {og_price}")

            # 상세 페이지 닫고 메인 페이지로 돌아가기
            driver.close()
            driver.switch_to.window(window_name=first_tab)

            time.sleep(5)

        # 다음 페이지로 이동
        try:
            next_page = driver.find_element(By.LINK_TEXT, str(current_page + 1))
            next_page.click()
            current_page += 1
            time.sleep(1)
        except NoSuchElementException:
            try:
                next_button = driver.find_element(By.CLASS_NAME, 'next')
                next_button.click()
                current_page += 1
                time.sleep(1)
                continue
            except NoSuchElementException:
                print("더 이상 'next' 버튼이 없습니다. 마지막 페이지에 도달했을 수 있습니다.")
                break

    except Exception as e:
        print("오류 발생:", e)
        break

# 웹 드라이버 종료
driver.quit()
