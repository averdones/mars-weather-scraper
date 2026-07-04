import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

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
WEATHER_API_TIMEOUT_SECONDS = 30
WEATHER_API_URLS = (
    "https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json",
    "https://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php",
    "http://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php",
)
PAGE_LOAD_RECOVERY_EXCEPTIONS = (TimeoutException, ReadTimeoutError)


class WeatherApiError(RuntimeError):
    pass


SCRAPE_RETRY_EXCEPTIONS = (TimeoutException, WebDriverException, ReadTimeoutError, URLError, OSError, WeatherApiError)


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


def _request_weather_api(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://mars.nasa.gov/msl/weather/",
        },
    )
    with urlopen(request, timeout=WEATHER_API_TIMEOUT_SECONDS) as response:
        raw_data = response.read().decode("utf-8", errors="replace")

    try:
        return json.loads(raw_data)
    except json.JSONDecodeError as exc:
        raise WeatherApiError("REMS weather API returned invalid JSON") from exc


def _download_weather_api() -> list[dict]:
    errors = []
    for url in WEATHER_API_URLS:
        try:
            data = _request_weather_api(url)
            break
        except (URLError, OSError, WeatherApiError) as exc:
            errors.append(f"{url}: {exc}")
    else:
        raise WeatherApiError("Could not connect to the REMS weather API. " + " | ".join(errors))

    soles = data.get("soles")
    if not isinstance(soles, list) or not soles:
        raise WeatherApiError("REMS weather API did not return any sols")

    try:
        return sorted(soles, key=lambda sol: int(sol["sol"]), reverse=True)
    except (KeyError, TypeError, ValueError) as exc:
        raise WeatherApiError("REMS weather API returned malformed sol data") from exc


def _format_api_value(weather_day: dict, key: str) -> str:
    value = weather_day.get(key)
    return "--" if value in (None, "") else str(value)


def _format_api_season(weather_day: dict) -> str:
    season = _format_api_value(weather_day, "season")
    if season.startswith("Month "):
        return season.replace("Month ", "Mes ", 1)
    return season


def _format_api_weather_day(weather_day: dict) -> str:
    return (
        f"Tierra, {_format_api_value(weather_day, 'terrestrial_date')} UTC\n"
        f"Marte, {_format_api_season(weather_day)} - LS {_format_api_value(weather_day, 'ls')}°\n"
        "««\n"
        "«\n"
        f"Sol {_format_api_value(weather_day, 'sol')}\n"
        "»»\n"
        "»\n"
        "TEMPERATURA DEL AIRE\n"
        f"{_format_api_value(weather_day, 'max_temp')}\n"
        "Max.\n"
        f"{_format_api_value(weather_day, 'min_temp')}\n"
        "Min.\n"
        "°C\n"
        "TEMPERATURA DEL SUELO\n"
        f"{_format_api_value(weather_day, 'max_gts_temp')}\n"
        "Max.\n"
        f"{_format_api_value(weather_day, 'min_gts_temp')}\n"
        "Min.\n"
        "°C\n"
        "PRESIÓN\n"
        f"{_format_api_value(weather_day, 'pressure')}\n"
        " Media\n"
        "Pa\n"
        "VIENTO\n"
        f"{_format_api_value(weather_day, 'wind_speed')}\n"
        " Vientos dominantes\n"
        "Km/h\n"
        "HUMEDAD RELATIVA\n"
        f"{_format_api_value(weather_day, 'abs_humidity')}\n"
        " Media\n"
        "%\n"
        "AMANECER Y ATARDECER\n"
        f"{_format_api_value(weather_day, 'sunrise')}\n"
        "Amanecer\n"
        f"{_format_api_value(weather_day, 'sunset')}\n"
        "Atardecer\n"
        "RADIACIÓN ULTRAVIOLETA\n"
        f"{_format_api_value(weather_day, 'local_uv_irradiance_index')}\n"
        " Nivel del índice\n"
        "OPACIDAD ATMOSFÉRICA\n"
        f"{_format_api_value(weather_day, 'atmo_opacity')}\n"
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(SCRAPE_RETRY_EXCEPTIONS),
    reraise=True,
)
def download_weather_today(driver: WebDriver | None = None) -> str:
    if driver is None:
        return _format_api_weather_day(_download_weather_api()[0])

    try:
        _open_weather_page(driver)
        return _get_weather_slide_text(driver)
    finally:
        driver.quit()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(SCRAPE_RETRY_EXCEPTIONS),
    reraise=True,
)
def download_weather_last_n_days(driver: WebDriver | None = None, n_days: int = 0) -> list[str]:
    if driver is None:
        return [_format_api_weather_day(weather_day) for weather_day in _download_weather_api()[:n_days + 1]]

    try:
        _open_weather_page(driver)
        last_n_days_data = []
        last_n_days_data.append(_get_weather_slide_text(driver))
        for _ in range(n_days):
            driver.find_element(By.ID, "mw-previous").click()
            time.sleep(1)
            daily_data = driver.find_element(By.ID, "main-slide").text
            last_n_days_data.append(daily_data)

        return last_n_days_data
    finally:
        driver.quit()


def download_weather_historical(driver: WebDriver | None = None) -> list[str]:
    if driver is None:
        return [_format_api_weather_day(weather_day) for weather_day in _download_weather_api()]

    try:
        _open_weather_page(driver)
        historical_data = []
        historical_data.append(_get_weather_slide_text(driver))
        while True:
            driver.find_element(By.ID, "mw-previous").click()
            time.sleep(1)
            daily_data = driver.find_element(By.ID, "main-slide").text

            # There is no way of knowing if we reached the end, other than comparing with the previous day
            if daily_data == historical_data[-1]:
                break

            daily_data_print = daily_data.replace("\n", " ")
            print(f"Downloaded {daily_data_print}", end="\n")
            historical_data.append(daily_data)

        return historical_data
    finally:
        driver.quit()
