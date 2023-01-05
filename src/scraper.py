import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_main_url() -> str:
    return "http://cab.inta-csic.es/rems/en/"


def get_selenium_driver() -> webdriver:
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    return driver


def download_weather_today() -> str:
    with get_selenium_driver() as wd:
        wd.get(get_main_url())

        return WebDriverWait(wd, 20).until(EC.visibility_of_element_located((By.ID, "main-slide"))).text


def download_weather_historical() -> list[str]:
    with get_selenium_driver() as wd:
        wd.get(get_main_url())

        historical_data = []
        slide = WebDriverWait(wd, 20).until(EC.visibility_of_element_located((By.ID, "main-slide")))
        historical_data.append(slide.text)
        while True:
            wd.find_element(By.ID, "mw-previous").click()
            time.sleep(0.25)
            daily_data = wd.find_element(By.ID, "main-slide").text

            # There is no way of knowing if we reached the end, other than comparing with the previous day
            if daily_data == historical_data[-1]:
                break

            historical_data.append(wd.find_element(By.ID, "main-slide").text)

    return historical_data
