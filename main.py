from src.scraper import get_selenium_driver, download_weather_today
from src.parser import parse_weather_day
from src.db_models import DailyWeather


def main():
    # Scrape
    driver = get_selenium_driver()
    weather_day_data = download_weather_today(driver)

    # Upload to DynamoDB
    DailyWeather(**parse_weather_day(weather_day_data)).save()


if __name__ == '__main__':
    main()
