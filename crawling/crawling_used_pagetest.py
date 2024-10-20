from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

url = "https://www.kbchachacha.com/public/search/main.kbc#!?countryOrder=1&page=1&sort=-orderDate&gas=004007&useCode=002002,002003,002001,002004,002005,002008"
driver.get(url)

first_tab = driver.window_handles[0]

wait = WebDriverWait(driver, 10)

current_page = 1

while True:
    try:
        pageList = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "#content > div.common-sub-content.fix-content > div > div.searchArea > div.searchArea__carList > div.__used-car-list > div.paginate.align-c.mg-t0.mg-b100"))
        )

        next_page = pageList.find_element(By.LINK_TEXT, str(current_page + 1))
        next_page.click()

        current_page += 1

        time.sleep(1)

    except NoSuchElementException:
        try:
            next_button = pageList.find_element(By.CLASS_NAME, 'next')
            next_button.click()

            current_page += 1

            time.sleep(1)

            continue

        except NoSuchElementException:

            print("더 이상 'next' 버튼이 없습니다. 마지막 페이지에 도달했을 수 있습니다.")
            break

driver.quit()

