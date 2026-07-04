from selenium.common.exceptions import TimeoutException

from src import scraper


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
