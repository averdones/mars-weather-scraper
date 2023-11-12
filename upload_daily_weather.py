import time
from pynamodb.exceptions import PutError

from src.loggers import setup_logger
from src.scraper import get_selenium_driver, download_weather_today, download_weather_last_n_days
from src.parser import parse_weather_day
from src.db_models import DailyWeather
from src.db_utils import get_item


logger = setup_logger("upload_daily_weather", "../logs/upload_daily_data.log")


def main():
    # Scrape
    driver = get_selenium_driver()
    weather_day_data = download_weather_today(driver)
    parsed_weather_day_data = parse_weather_day(weather_day_data)

    sol = parsed_weather_day_data["sol"]
    if get_item(sol, DailyWeather) is not None:
        print("Weather hasn't been updated in the webpage")
        return
    else:
        # Check if they updated more than one day
        n_last_days = 0
        sol -= 1
        while get_item(sol, DailyWeather) is None:
            n_last_days += 1
            sol -= 1

        if n_last_days == 0:
            # Upload only today's weather
            try:
                DailyWeather(**parsed_weather_day_data).save()
            except PutError as e:
                print(e)
        else:
            # Upload today's weather and the last n days
            driver = get_selenium_driver()
            weather_last_n_days_data = download_weather_last_n_days(driver, n_last_days)
            for weather_data in weather_last_n_days_data:
                parsed_weather_data = parse_weather_day(weather_data)
                for attempt in range(10):
                    try:
                        DailyWeather(**parsed_weather_data).save()
                    except PutError:
                        print("Sleeping...")
                        time.sleep(1)
                    else:
                        break
                else:
                    logger.error(f"Failed to upload data to DynamoDB. Data: {parsed_weather_data}")
                    raise


if __name__ == '__main__':
    main()
