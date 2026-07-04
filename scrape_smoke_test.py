import json

from src.parser import parse_weather_day
from src.scraper import download_weather_last_n_days, download_weather_today


def main() -> None:
    today = parse_weather_day(download_weather_today())
    recent_sols = [parse_weather_day(day)["sol"] for day in download_weather_last_n_days(n_days=2)]

    print(
        json.dumps(
            {
                "today": today,
                "recent_sols": recent_sols,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
