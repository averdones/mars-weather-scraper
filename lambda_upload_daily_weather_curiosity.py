from src.upload_aws import upload_daily_weather
from src.scraper import get_selenium_driver


def lambda_handler(event, context):
    driver = get_selenium_driver("/opt/chromedriver/chromedriver", "/opt/chromedriver/headless-chromium")
    upload_daily_weather("mars-weather", driver)
