"""Constants, like geographical positions."""

import utm


# implied below
HEMISPHERE = 'north'
DATUM = 'WGS84'


# taken from cppm via kay
orca_northing = 4743000
orca_easting = 256500
orca_height = -2450  # m
orca_utm_zone_number = 32
orca_utm_zone_letter = 'T'
orca_utm_zone = '{num}{let}'.format(
    num=orca_utm_zone_number, let=orca_utm_zone_letter)
orca_latitude, orca_longitude = utm.to_latlon(orca_easting, orca_northing,
                                              orca_utm_zone_number,
                                              orca_utm_zone_letter)

# taken from detX v2
# sicily site
arca_northing = 4016800
arca_easting = 587600
arca_height = -3450  # m
arca_utm_zone_number = 33
arca_utm_zone_letter = 'N'
arca_utm_zone = '{num}{let}'.format(
    num=arca_utm_zone_number, let=arca_utm_zone_letter)
arca_latitude, arca_longitude = utm.to_latlon(arca_easting, arca_northing,
                                              arca_utm_zone_number,
                                              arca_utm_zone_letter)

# taken from http://antares.in2p3.fr/internal/dokuwiki/doku.php?id=astro_coordinatetransformation_howto
antares_northing = 4742381.9
antares_easting = 268221.6
antares_height = -2500  # m     (guessed, probably similar to orca)
antares_utm_zone_number = 32
antares_utm_zone_letter = 'N'
antares_utm_zone = '{num}{let}'.format(
    num=antares_utm_zone_number, let=antares_utm_zone_letter)
antares_latitude, antares_longitude = utm.to_latlon(
    antares_easting, antares_northing,
    antares_utm_zone_number, antares_utm_zone_letter)
