from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

import settings as s


class DailyWeather(Model):
    class Meta:
        table_name = "mars-weather"
        region = "us-east-2"
        aws_access_key_id = s.AWS_ACCESS_KEY_ID
        aws_secret_access_key = s.AWS_SECRET_ACCESS_KEY

    sol = NumberAttribute(hash_key=True)
    max_air_temp = NumberAttribute()
    min_air_temp = NumberAttribute()
    max_ground_temp = NumberAttribute()
    min_ground_temp = NumberAttribute()
    pressure = NumberAttribute()
    dawn = UnicodeAttribute()
    dusk = UnicodeAttribute()
