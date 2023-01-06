import io
from datetime import date
from selenium import webdriver

from src.aws import upload_object_to_s3
from src.scraper import download_weather_today


def upload_daily_weather(bucket: str, driver: webdriver) -> None:
    weather_today = download_weather_today(driver)
    weather_obj = io.BytesIO(bytes(weather_today, encoding="utf-8"))
    file_name = date.today().strftime("%Y-%m-%d") + ".txt"
    upload_object_to_s3(weather_obj, bucket, file_name)
