from pynamodb.exceptions import PutError

from src.scraper import get_selenium_driver, download_weather_historical
from src.parser import parse_weather_day
from src.db_models import DailyWeather


def main():
    # Scrape
    driver = get_selenium_driver()
    weather_hist_data = download_weather_historical(driver)

    # Upload to DynamoDB
    for weather_day_data in weather_hist_data:
        try:
            DailyWeather(**parse_weather_day(weather_day_data)).save()
        except PutError as e:
            print(e)


if __name__ == '__main__':
    main()
