import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from urllib3.exceptions import ReadTimeoutError


PAGE_LOAD_TIMEOUT_SECONDS = 45
WEATHER_WIDGET_TIMEOUT_SECONDS = 20
PAGE_LOAD_RECOVERY_EXCEPTIONS = (TimeoutException, ReadTimeoutError)
SCRAPE_RETRY_EXCEPTIONS = (TimeoutException, WebDriverException, ReadTimeoutError)


def get_main_url() -> str:
    return "http://cab.inta-csic.es/rems/es/"


def get_selenium_driver() -> WebDriver:
    options = Options()
    options.page_load_strategy = "eager"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SECONDS)

    print(f"Chrome Version: {driver.capabilities['browserVersion']}")
    print(f"ChromeDriver Version: {driver.capabilities['chrome']['chromedriverVersion']}")

    return driver


def _stop_page_load(driver: WebDriver, original_error: Exception) -> None:
    try:
        driver.execute_script("window.stop();")
    except SCRAPE_RETRY_EXCEPTIONS:
        raise original_error


def _open_weather_page(driver: WebDriver) -> None:
    try:
        driver.get(get_main_url())
    except PAGE_LOAD_RECOVERY_EXCEPTIONS as exc:
        _stop_page_load(driver, exc)


def _get_weather_slide_text(driver: WebDriver) -> str:
    return WebDriverWait(driver, WEATHER_WIDGET_TIMEOUT_SECONDS).until(
        EC.visibility_of_element_located((By.ID, "main-slide"))
    ).text


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(SCRAPE_RETRY_EXCEPTIONS),
    reraise=True,
)
def download_weather_today(driver: WebDriver | None = None) -> str:
    owns_driver = driver is None
    wd = driver or get_selenium_driver()
    try:
        _open_weather_page(wd)
        return _get_weather_slide_text(wd)
    finally:
        if owns_driver:
            wd.quit()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(SCRAPE_RETRY_EXCEPTIONS),
    reraise=True,
)
def download_weather_last_n_days(driver: WebDriver | None = None, n_days: int = 0) -> list[str]:
    owns_driver = driver is None
    wd = driver or get_selenium_driver()
    try:
        _open_weather_page(wd)
        last_n_days_data = []
        last_n_days_data.append(_get_weather_slide_text(wd))
        for _ in range(n_days):
            wd.find_element(By.ID, "mw-previous").click()
            time.sleep(1)
            daily_data = wd.find_element(By.ID, "main-slide").text
            last_n_days_data.append(daily_data)

        return last_n_days_data
    finally:
        if owns_driver:
            wd.quit()


def download_weather_historical(driver: WebDriver | None = None) -> list[str]:
    owns_driver = driver is None
    wd = driver or get_selenium_driver()
    try:
        _open_weather_page(wd)
        historical_data = []
        historical_data.append(_get_weather_slide_text(wd))
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
    finally:
        if owns_driver:
            wd.quit()
