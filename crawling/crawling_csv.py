from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import re
import time
import csv

# 크롬 옵션 설정 (브라우저 자동 종료 방지)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-agent=Googlebot")
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)

# 크롬 드라이버 실행
driver = webdriver.Chrome(options=chrome_options)

# 초기 URL 열기
url = "https://auto.danawa.com/newcar/?&page=1"
driver.get(url)

# 처음 페이지 저장
first_tab = driver.window_handles[0]

# 파일저장 순서 번호
index = 1

# 페이지 번호
n = 1

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#container_newcarlist"))
)

# 현재 판매중인 모델만
now = driver.find_element(By.CSS_SELECTOR, "#container_newcarlist > div.top > div.tabHead > ul > li:nth-child(2)")
driver.execute_script("arguments[0].click();", now)

time.sleep(3)

# 100개 씩 보기
select_button2 = driver.find_element(By.CSS_SELECTOR, "#listCount > option:nth-child(3)")
select_button2.click()

try:
    while True:

        time.sleep(3)

        # 첫번째 페이지에서 ul(전체) 가져오기
        ul_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#container_newcarlist > div.contents > ul"))
        )

        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        # ul 에서 li 가져오기
        li_elements2 = [li for li in li_elements if "list_banner" not in li.get_attribute("class")]

        for li in li_elements2:
            # 링크 찾기
            a_tag = li.find_element(By.CSS_SELECTOR, "div.detail a.name")

            # 링크 텍스트 가져오기
            a_name = a_tag.text.strip()

            # 브랜드와 모델명 나누기
            a_name_list = a_name.split(" ", 1)
            brand_name = a_name_list[0]
            model_name = a_name_list[1]

            # 링크 누르기
            a_tag.click()

            # 누른 링크 (2번째 탭)으로 전환하기
            second_tab = driver.window_handles[-1]
            driver.switch_to.window(window_name=second_tab)

            # 2번째 탭에서 dl 가져오기
            dl_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "#autodanawa_gridC > div.gridMain > article > main > div.modelSection.container_modelprice > div.price_contents.on > dl"))
            )

            # 차종 가져오기 예) 중형SUV, 대형  등
            car_type = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "div.spec span"))
            ).text

            # dl에서 dt 가져오기
            dt_elements = dl_element.find_elements(By.TAG_NAME, "dt")

            for dt in dt_elements:
                # 세부 모델명 가져오기
                model2_strong = WebDriverWait(dt, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                        "div.name strong"))
                )

                model_name2 = model2_strong.text.strip()

                # 스펙 정보 팝업 버튼 가져오고 클릭
                spec_button = WebDriverWait(dt, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "div.info a.button")
                    )
                )
                spec_button.click()

                # 팝업 탭으로 전환
                popup_tab = driver.window_handles[-1]
                driver.switch_to.window(window_name=popup_tab)

                # 스펙 정보 버튼 누르기
                spec_button2 = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@data-type='spec']/a"))
                )
                spec_button2.click()

                # 위쪽 칼럼 tbody 가져오기
                top_col = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "#modelinfo > div.modelinfo-compare > div > div.compare__right > table.compare__table.compare__header > tbody"))
                )

                # 위쪽 칼럼에서 트림, 가격 가져오기
                trim_list = ["트림명"]
                price_list = ["가격"]
                brand = ["브랜드"]
                model = ["모델명"]
                model2 = ["세부모델명"]
                car_type_list = ["차종"]
                for th in top_col.find_elements(By.TAG_NAME, "th"):
                    trim = th.find_element(By.CSS_SELECTOR, "span.trim").text.strip()
                    price = th.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                    trim_list.append(trim)
                    price_list.append(price)

                    brand.append(brand_name)
                    model.append(model_name)
                    model2.append(model_name2)
                    car_type_list.append(car_type)

                # 왼쪽 칼럼 tbody 가져오기
                left_col = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "#modelinfo > div.modelinfo-compare > div > div.compare__left > table.compare__table.compare__body > tbody"))
                )

                # 왼쪽 칼럼 가져오기
                left = left_col.find_elements(By.TAG_NAME, "tr")
                left2 = [row for row in left if not row.text.strip().startswith("[")]

                # 스펙 가져오기
                spec_tbody = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "#modelinfo > div.modelinfo-compare > div > div.compare__right > table.compare__table.compare__body > tbody"))
                )
                spec = spec_tbody.find_elements(By.TAG_NAME, "tr")
                spec2 = [row for row in spec if not row.get_attribute("class").startswith("group groupType_")]

                file_name = f'{index}_{brand_name}_{model_name}.csv'
                # CSV 파일로 저장
                with open(file_name, mode='w', newline='', encoding='utf-8-sig') as file:
                    csv.writer(file).writerow(brand)
                    csv.writer(file).writerow(model)
                    csv.writer(file).writerow(model2)
                    csv.writer(file).writerow(car_type_list)
                    csv.writer(file).writerow(trim_list)
                    csv.writer(file).writerow(price_list)

                    for idx, (l, row) in enumerate(zip(left2, spec2)):
                        left_data = l.text.strip()  # 왼쪽 데이터를 추출
                        row_data = [col.text.strip() for col in
                                    row.find_elements(By.TAG_NAME, "td")]
                        csv.writer(file).writerow([left_data] + row_data)
                index += 1

                driver.close()
                driver.switch_to.window(window_name=second_tab)

            driver.close()
            driver.switch_to.window(window_name=first_tab)

        # 페이지 이동
        if (n >= 4):
            break

        ul = driver.find_element(By.CSS_SELECTOR,
                                 "#container_newcarlist > div.contents > div.common-pagination-basic > div.pagination-basic > ul")

        li = [item for item in ul.find_elements(By.TAG_NAME, "li") if
              "list-item--prev" not in item.get_attribute("class")]

        page_button = li[n].find_element(By.TAG_NAME, "a")

        # 다음 페이지 클릭
        page_button.click()

        n += 1

except Exception as e:
    print(f"Error: {e}")

finally:
    # 브라우저 종료
    driver.quit()