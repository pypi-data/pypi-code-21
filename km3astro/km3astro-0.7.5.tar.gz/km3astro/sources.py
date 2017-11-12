from astropy.units import hourangle, deg
from astropy.coordinates import SkyCoord

# (right ascension, declination)
SIRIUS = SkyCoord('06 45 08.9 -16 42 58', unit=(hourangle, deg))
CANOPUS = SkyCoord('06 23 57.1 -52 41 45', unit=(hourangle, deg))
ARCTURUS = SkyCoord('14 15 39.7 +19 10 57', unit=(hourangle, deg))
ANTARES = SkyCoord('16 29 24.4 -26 25 55', unit=(hourangle, deg))

RX_J1713 = SkyCoord('17 17 33.6 -39 45 36.4', unit=(hourangle, deg))
VELA_X = SkyCoord('08 35 00 -45 36 00', unit=(hourangle, deg))

# Sagittarius A* (sagittarius a-star)
# GALACTIC_CENTER = SkyCoord(0 * deg, 0 * deg, frame='galactic').icrs
SAGITTARIUS_A_STAR = SkyCoord('17 45 40.0409 -29 0 28.118', unit=(hourangle, deg))      # noqa
GALACTIC_CENTER = SAGITTARIUS_A_STAR
