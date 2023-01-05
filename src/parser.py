import re


def parse_weather_day(data: str) -> dict:
    """Parses weather corresponding to a single day."""
    data = data.replace("\n", "")

    sol = int(re.findall("Sol (\d+)", data)[0])
    max_air_temp, min_air_temp = [int(x) for x in re.findall("TEMPERATURA DEL AIRE(-?\d+)Max.(-?\d+)Min.", data)[0]]
    max_ground_temp, min_ground_temp = [int(x) for x in
                                        re.findall("TEMPERATURA DEL SUELO(-?\d+)Max.(-?\d+)Min.", data)[0]]
    pressure = int(re.findall("PRESIÓN(\d+)", data)[0])
    dawn, dusk = re.findall("AMANECER Y ATARDECER(\d+:\d+)Amanecer(\d+:\d+)Atardecer", data)[0]

    return {
        "sol": sol,
        "max_air_temp": max_air_temp,
        "min_air_temp": min_air_temp,
        "max_ground_temp": max_ground_temp,
        "min_ground_temp": min_ground_temp,
        "pressure": pressure,
        "dawn": dawn,
        "dusk": dusk
    }


def parse_sol(data: str):
    try:
        int(re.findall("Sol (\d+)", data)[0])
    except:
        pass


