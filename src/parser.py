from src.loggers import setup_logger
import re


logger = setup_logger("parser", "../logs/parser.log")


def parse_weather_day(data: str) -> dict:
    """Parses weather corresponding to a single day."""
    data_to_print = data.replace("\n", "")
    logger.info(f"Parsing weather data for a single day. Data to be parsed: '{data_to_print}'")
    data = data.replace("\n", "")

    sol = parse_sol(data)
    if sol == "":
        logger.error(f"Sol not found in data: '{data}'")
        raise

    max_air_temp, min_air_temp = parse_air_temperatures(data)
    if max_air_temp == "" or min_air_temp == "":
        logger.warning(f"Air temperatures not found in Sol: {sol}. Data: '{data}'")

    max_ground_temp, min_ground_temp = parse_ground_temperatures(data)
    if max_ground_temp == "" or min_ground_temp == "":
        logger.warning(f"Ground temperatures not found in Sol: {sol}. Data: '{data}'")

    pressure = parse_pressure(data)
    if pressure == "":
        logger.warning(f"Pressure not found in Sol: {sol}. Data: '{data}'")

    dawn, dusk = parse_dawn_dusk(data)
    if dawn == "" or dusk == "":
        logger.warning(f"Dawn and dusk not found in Sol: {sol}. Data: '{data}'")

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


def parse_sol(data: str) -> int | str:
    match = re.findall("Sol (\d+)", data)
    if match:
        return int(match[0])
    else:
        return ""


def parse_air_temperatures(data: str) -> list[int, int] | list[str, str]:
    match = re.findall("TEMPERATURA DEL AIRE(-?\d+)Max.(-?\d+)Min.", data)
    if match:
        return [int(x) for x in match[0]]
    else:
        return ["", ""]


def parse_ground_temperatures(data: str) -> list[int, int] | list[str, str]:
    match = re.findall("TEMPERATURA DEL SUELO(-?\d+)Max.(-?\d+)Min.", data)
    if match:
        return [int(x) for x in match[0]]
    else:
        return ["", ""]


def parse_pressure(data: str) -> int | str:
    match = re.findall("PRESIÓN(\d+)", data)
    if match:
        return int(match[0])
    else:
        return ""


def parse_dawn_dusk(data: str) -> list[str, str]:
    match = re.findall("AMANECER Y ATARDECER(\d+:\d+)Amanecer(\d+:\d+)Atardecer", data)
    if match:
        return [x for x in match[0]]
    else:
        return ["", ""]
