from utilib.core import http
import math
import json

x_pi = 3.14159265358979324 * 3000.0 / 180.0


def convert_gcj02_to_bd09(lat, lng):
    x = lng
    y = lat
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi)
    lat = z * math.sin(theta) + 0.006
    lng = z * math.cos(theta) + 0.0065
    return lat, lng


def convert_bd09_to_gcj02(lat, lng):
    x = lng - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    lat = z * math.sin(theta)
    lng = z * math.cos(theta)
    return lat, lng


async def get_district_by_adcode(key, adcode):
    _r = await http.async_fetch_url(
        'http://restapi.amap.com/v3/config/district',
        'GET',
        {},
        True,
        key=key,
        keywords=adcode
        )
    return json.loads(_r.body)
