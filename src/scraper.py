import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_main_url() -> str:
    return "http://cab.inta-csic.es/rems/es/"


def get_selenium_driver() -> webdriver:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(), options=options)

    return driver


def download_weather_today(driver: webdriver) -> str:
    with driver as wd:
        wd.get(get_main_url())

        return WebDriverWait(wd, 20).until(EC.visibility_of_element_located((By.ID, "main-slide"))).text


def download_weather_historical(driver: webdriver) -> list[str]:
    with driver as wd:
        wd.get(get_main_url())

        historical_data = []
        slide = WebDriverWait(wd, 20).until(EC.visibility_of_element_located((By.ID, "main-slide")))
        historical_data.append(slide.text)
        while True:
            wd.find_element(By.ID, "mw-previous").click()
            time.sleep(1)
            daily_data = wd.find_element(By.ID, "main-slide").text

            # There is no way of knowing if we reached the end, other than comparing with the previous day
            if daily_data == historical_data[-1]:
                break

            daily_data_print = daily_data.replace("\n", " ")
            print(f"Downloaded {daily_data_print}", end="\n")
            historical_data.append(daily_data)

    return historical_data
