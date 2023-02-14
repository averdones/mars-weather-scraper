from src.scraper import get_selenium_driver, download_weather_today
from src.parser import parse_weather_day


def main():
    driver = get_selenium_driver("/usr/local/bin/chromedriver")
    weather_day_data = download_weather_today(driver)
    print(parse_weather_day(weather_day_data))


if __name__ == '__main__':
    main()
