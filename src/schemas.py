from pydantic import BaseModel


class WeaterData(BaseModel):
    sol = int
    max_air_temp = float
    min_air_temp = float
    max_ground_temp = float
    min_ground_temp = float
    pressure = float
    dawn = str
    dusk = str
