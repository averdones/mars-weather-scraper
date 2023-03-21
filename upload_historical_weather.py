import pickle
from pynamodb.exceptions import PutError
import time

from src.loggers import setup_logger
from src.scraper import get_selenium_driver, download_weather_historical
from src.parser import parse_weather_day
from src.db_models import DailyWeather


logger = setup_logger("upload_historical_weather", "../logs/parser.log")


def main(load_weather_hist_data_from_file: bool = False):
    """This is a one time process that is run locally.

    It downloads the historical weather data and uploads it to DynamoDB.

    """
    # Scrape
    driver = get_selenium_driver()

    if load_weather_hist_data_from_file:
        with open("weather_hist_data.pickle", "r") as f:
            weather_hist_data = pickle.load(f)
    else:
        weather_hist_data = download_weather_historical(driver)

    # Pickle in case the upload process fails
    if not load_weather_hist_data_from_file:
        with open("weather_hist_data.pickle", "w") as f:
            pickle.dump(weather_hist_data, f)

    # Upload to DynamoDB
    for weather_day_data in weather_hist_data:
        parsed_day_data = parse_weather_day(weather_day_data)
        for attempt in range(10):
            try:
                DailyWeather(**parsed_day_data).save()
            except PutError:
                time.sleep(1)
            else:
                break
        else:
            logger.error(f"Failed to upload data to DynamoDB. Data: {parsed_day_data}")
            raise


if __name__ == '__main__':
    main()
