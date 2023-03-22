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
    max_air_temp = NumberAttribute(null=True)
    min_air_temp = NumberAttribute(null=True)
    max_ground_temp = NumberAttribute(null=True)
    min_ground_temp = NumberAttribute(null=True)
    pressure = NumberAttribute(null=True)
    dawn = UnicodeAttribute(null=True)
    dusk = UnicodeAttribute(null=True)
    last_updated = UnicodeAttribute(null=True)
