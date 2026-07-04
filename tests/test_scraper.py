from selenium.common.exceptions import TimeoutException

from src import scraper
from src.parser import parse_weather_day


class FakeSlide:
    text = "Sol 1\nTEMPERATURA DEL AIRE\n1\nMax.\n-1\nMin."


class FakeWait:
    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout

    def until(self, condition):
        return FakeSlide()


class DriverWithHungPageLoad:
    def __init__(self):
        self.urls = []
        self.scripts = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def get(self, url):
        self.urls.append(url)
        raise TimeoutException("page load did not finish")

    def execute_script(self, script):
        self.scripts.append(script)

    def quit(self):
        pass


API_SOLES = [
    {
        "terrestrial_date": "2026-06-30",
        "sol": "4941",
        "ls": "310",
        "season": "Month 11",
        "min_temp": "-70",
        "max_temp": "0",
        "pressure": "795",
        "sunrise": "06:40",
        "sunset": "18:53",
        "min_gts_temp": "-83",
        "max_gts_temp": "13",
    },
    {
        "terrestrial_date": "2026-06-29",
        "sol": "4940",
        "ls": "309",
        "season": "Month 11",
        "min_temp": "-69",
        "max_temp": "-1",
        "pressure": "800",
        "sunrise": "06:40",
        "sunset": "18:53",
        "min_gts_temp": "-81",
        "max_gts_temp": "12",
    },
]


def test_download_weather_today_uses_api_without_starting_browser(monkeypatch):
    monkeypatch.setattr(scraper, "_download_weather_api", lambda: API_SOLES)
    monkeypatch.setattr(
        scraper,
        "get_selenium_driver",
        lambda: (_ for _ in ()).throw(AssertionError("daily scrape should not start Chrome")),
    )

    weather_day = scraper.download_weather_today()

    assert parse_weather_day(weather_day) | {"last_updated": "ignored"} == {
        "sol": 4941,
        "max_air_temp": 0,
        "min_air_temp": -70,
        "max_ground_temp": 13,
        "min_ground_temp": -83,
        "pressure": 795,
        "dawn": "06:40",
        "dusk": "18:53",
        "last_updated": "ignored",
    }


def test_download_weather_last_n_days_uses_api(monkeypatch):
    monkeypatch.setattr(scraper, "_download_weather_api", lambda: API_SOLES)

    weather_days = scraper.download_weather_last_n_days(n_days=1)

    assert [parse_weather_day(weather_day)["sol"] for weather_day in weather_days] == [4941, 4940]


def test_download_weather_today_stops_loading_after_page_load_timeout(monkeypatch):
    monkeypatch.setattr(scraper, "WebDriverWait", FakeWait)
    driver = DriverWithHungPageLoad()

    assert scraper.download_weather_today(driver) == FakeSlide.text
    assert driver.urls == [scraper.get_main_url()]
    assert driver.scripts == ["window.stop();"]


def test_get_selenium_driver_uses_bounded_eager_page_load(monkeypatch):
    captured = {}

    class FakeChrome:
        capabilities = {
            "browserVersion": "150.0.0.0",
            "chrome": {"chromedriverVersion": "150.0.0.0"},
        }

        def set_page_load_timeout(self, timeout):
            captured["page_load_timeout"] = timeout

    def fake_chrome(service, options):
        captured["options"] = options
        return FakeChrome()

    monkeypatch.setattr(scraper.webdriver, "Chrome", fake_chrome)

    scraper.get_selenium_driver()

    assert captured["options"].page_load_strategy == "eager"
    assert captured["page_load_timeout"] == scraper.PAGE_LOAD_TIMEOUT_SECONDS
