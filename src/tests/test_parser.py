import pytest

from src.parser import parse_sol, parse_air_temperatures, parse_ground_temperatures, parse_pressure, parse_dawn_dusk, \
    parse_weather_day


@pytest.mark.parametrize(
    "data,expected",
    [
        ("Sol 0", 0),
        ("Sol 1123", 1123),
        ("Sol", None),
        ("Asd 45", None),
    ]
)
def test_parse_sol(data, expected):
    assert parse_sol(data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ("TEMPERATURA DEL AIRE-23Max.12Min.", [-23, 12]),
        ("TEMPERATURA EL AIRE-23Max.12Min.", [None, None]),
        ("TEMPERATURA EL AIREMax.12Min.", [None, None]),
    ]
)
def test_parse_air_temperatures(data, expected):
    assert parse_air_temperatures(data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ("TEMPERATURA DEL SUELO-23Max.12Min.", [-23, 12]),
        ("TEMPERATURA EL SUELO-23Max.12Min.", [None, None]),
        ("TEMPERATURA EL SUELOMax.12Min.", [None, None]),
    ]
)
def test_parse_ground_temperatures(data, expected):
    assert parse_ground_temperatures(data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ("PRESIÓN123", 123),
        ("PRESIÓN 123", None),
        ("PRESIÓN", None),
        ("PRESIÓN,123", None),
    ]
)
def test_parse_pressure(data, expected):
    assert parse_pressure(data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ("AMANECER Y ATARDECER10:30Amanecer16:12Atardecer", ["10:30", "16:12"]),
        ("AMANECER Y ATARDECER 10:30Amanecer16:12Atardecer", [None, None]),
    ]
)
def test_parse_dawn_dusk(data, expected):
    assert parse_dawn_dusk(data) == expected


def test_parse_weather_day():
    assert parse_weather_day(
        "Tierra, 2023-03-15 UTC\nMarte, Mes 2 - LS 37°\n««\n«\nSol 3770\n»»\n»\nTEMPERATURA DEL AIRE\n-17\nMax.\n-78"
        "\nMin.\n°C\nTEMPERATURA DEL SUELO\n-3\nMax.\n-89\nMin.\n°C\nPRESIÓN\n840\n Media\nPa\nVIENTO\nValor no "
        "disponible\n Vientos dominantes\nKm/h\nHUMEDAD RELATIVA\nValor no disponible\n Media\n%\nAMANECER Y "
        "ATARDECER\n06:19\nAmanecer\n18:09\nAtardecer\nRADIACIÓN ULTRAVIOLETA\n Nivel del índice\nOPACIDAD "
        "ATMOSFÉRICA\nSoleado "
    ) == {
            "sol": 3770,
            "max_air_temp": -17,
            "min_air_temp": -78,
            "max_ground_temp": -3,
            "min_ground_temp": -89,
            "pressure": 840,
            "dawn": "06:19",
            "dusk": "18:09",
    }
