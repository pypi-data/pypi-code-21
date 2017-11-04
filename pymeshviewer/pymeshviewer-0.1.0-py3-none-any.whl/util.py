import math


def calculate_distance(latitude1, longitude1, latitude2, longitude2):
    """
    Calculates the distance between two coordinates in kilometers
    :param latitude1: Latitude of first point
    :param longitude1: Longitude of first point
    :param latitude2: Latitude of second point
    :param longitude2: Longitude of second point
    :return: Distance between points in kilometers
    """
    r = 6373.0

    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)
    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c
