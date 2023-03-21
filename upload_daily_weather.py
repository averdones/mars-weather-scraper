from pynamodb.exceptions import PutError

from src.scraper import get_selenium_driver, download_weather_today
from src.parser import parse_weather_day
from src.db_models import DailyWeather


def main():
    # Scrape
    driver = get_selenium_driver()
    weather_day_data = download_weather_today(driver)
    parsed_weather_day_data = parse_weather_day(weather_day_data)

    # Upload to DynamoDB
    try:
        DailyWeather(**parsed_weather_day_data).save()
    except PutError as e:
        print(e)


if __name__ == '__main__':
    main()
