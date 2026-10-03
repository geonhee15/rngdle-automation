import re
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

current_dir = os.path.dirname(os.path.abspath(__file__))
snapshots_dir = os.path.join(current_dir, 'Snapshots')
os.makedirs(snapshots_dir, exist_ok=True)

options = webdriver.ChromeOptions()
options.add_argument('--headless')  
options.add_argument('--disable-gpu')  
options.add_argument('--window-size=1920,1080') 

tb_filter = input("필터링 옵션 1: TOP부터 저장하기 위해선 TOP을, BOTTOM부터 저장하기 위해선 BOTTOM를 입력해주세요: ")
perc_filter = int(input("필터링 옵션 2: 이 확률부터 저장하기: "))

def process_and_save_screenshot(percentage_text, output_text, snapshots_dir, driver):
    print(f"Percentage text = {percentage_text}")
    percentage_image = percentage_text.replace("%", "").strip()
    
    if tb_filter in percentage_text.upper():
        digits = re.findall(r"\d+", percentage_text)
        if digits:
            percent_value = int(digits[0])
            if percent_value <= perc_filter:
                print(f'{tb_filter} {percent_value}% 감지! (5% 이하)')
                screenshot_path = os.path.join(snapshots_dir, f'{percentage_image}_{output_text}.png')
                driver.save_screenshot(screenshot_path)
                print(f'풀스크린 캡처 완료! ({screenshot_path})')
                return True
            else:
                print(f"{tb_filter} 결과이나 5% 초과 ({percentage_text}) -> 캡처 생략")
                return True
    else:
        print(f"{tb_filter} 결과가 아님 ({percentage_text}) -> 캡처 생략")
        return True
    return False

try:
    while True:
        driver = webdriver.Chrome(options=options)

        try:
            url = 'https://rngdle.com'
            driver.get(url)
            print("Chrome OK")

            wait = WebDriverWait(driver, 10)

            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//main//button")))
            button.click()

            driver.refresh()

            wait.until(EC.presence_of_element_located((By.XPATH, "//main//span")))

            all_spans = driver.find_elements(By.XPATH, "//main//span")
            visible_spans = [s for s in all_spans if s.is_displayed() and s.text.strip().isdigit()]

            if visible_spans:
                last_parent = visible_spans[-1].find_element(By.XPATH, "..")
                target_spans = last_parent.find_elements(By.XPATH, ".//span")

                output_text = "".join([span.text.strip() for span in target_spans if span.text.strip().isdigit()])
                print(f"number = {output_text}")

                percentage_xpath = (
                    "//main//span["
                    "contains(., 'TOP') or contains(., 'Top') or "
                    "contains(., 'BOTTOM') or contains(., 'Bottom')"
                    "]"
                )

                try:
                    percentage_element = wait.until(
                        EC.visibility_of_element_located((By.XPATH, percentage_xpath))
                    )
                    percentage_text = percentage_element.text.strip()
                    process_and_save_screenshot(percentage_text, output_text, snapshots_dir, driver)

                except Exception:
                    try:
                        time.sleep(0.5)
                        percentage_element = driver.find_element(By.XPATH, percentage_xpath)
                        percentage_text = percentage_element.text.strip()
                        print("(재시도 감지 중...)")
                        process_and_save_screenshot(percentage_text, output_text, snapshots_dir, driver)
                    except Exception:
                        print("Percentage 정보를 가져오지 못했습니다.")

            else:
                print("숫자를 찾지 못했습니다.")

        except Exception as e:
            print(f"요소 불러오기 실패: {e}")

        finally:
            driver.quit()

        time.sleep(3)
except KeyboardInterrupt:
    print("프로세스를 종료합니다")