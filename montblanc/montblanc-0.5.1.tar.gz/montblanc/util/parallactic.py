#!/usr/bin/env python
from __future__ import print_function
from casacore import measures, quanta
from astropy import coordinates, time, units
import katpoint
import ephem
import numpy as np


raw_time = 57683.6256944      # MJD
raw_position = (5108971.535438437, 2007109.5496348273, -3239327.1585932253)  # ITRF metres
raw_target = (-52.5, -35.0)   # Ra, Dec in degrees, J2000


def pa_astropy():
    t = time.Time(raw_time, format='mjd', scale='utc')
    pos = coordinates.EarthLocation.from_geocentric(*raw_position, unit='m')
    target = coordinates.SkyCoord(ra=raw_target[0], dec=raw_target[1], unit=units.deg, frame='fk5',
                                  location=pos, obstime=t)
    #pole = coordinates.SkyCoord(longitude=0, latitude=90, unit=units.deg, frame='itrs', location=pos, obstime=t)
    #pole = coordinates.SkyCoord(ra=0, dec=90, unit=units.deg, frame='cirs', location=pos, obstime=t)
    pole = coordinates.SkyCoord(ra=0, dec=90, unit=units.deg, frame='fk5', location=pos, obstime=t)
    pa = target.altaz.position_angle(pole.altaz)
    return pa.value


def pa_meqtrees():
    dm = measures.measures()
    t = dm.epoch('UTC', quanta.quantity(raw_time, 'd'))
    target = dm.direction('J2000', *(quanta.quantity(x, 'deg') for x in raw_target))
    pos = dm.position('itrf', *(quanta.quantity(x, 'm') for x in raw_position))
    zenith = dm.direction('AZELGEO', '0deg', '90deg')
    dm.do_frame(pos)
    dm.do_frame(t)
    zenith_radec = dm.measure(zenith, 'J2000')
    pa = dm.posangle(target, zenith_radec).get_value('rad')
    return pa


def pa_casa():
    dm = measures.measures()
    t = dm.epoch('UTC', quanta.quantity(raw_time, 'd'))
    pos = dm.position('itrf', *(quanta.quantity(x, 'm') for x in raw_position))
    dm.do_frame(pos)
    dm.do_frame(t)

    target = dm.direction('J2000', *(quanta.quantity(x, 'deg') for x in raw_target))
    pole = dm.direction('HADEC', '0deg', '90deg')
    pole_azel = dm.measure(pole, 'AZELGEO')
    target_azel = dm.measure(target, 'AZELGEO')
    pa = dm.posangle(target_azel, pole_azel).get_value('rad')
    return pa


def pa_katpoint():
    # Convert MJD to DJD
    t = katpoint.Timestamp(ephem.Date(raw_time - 2415020 + 2400000.5))
    lla = katpoint.ecef_to_lla(*raw_position)
    pos = katpoint.Antenna('ant', *lla)
    target = katpoint.construct_radec_target(*(np.deg2rad(x) for x in raw_target))
    pa = target.parallactic_angle(timestamp=t, antenna=pos)
    return pa


pa_a = coordinates.Angle(pa_astropy() * units.rad).wrap_at(180 * units.deg)
pa_c = coordinates.Angle(pa_casa() * units.rad).wrap_at(180 * units.deg)
pa_m = coordinates.Angle(pa_meqtrees() * units.rad).wrap_at(180 * units.deg)
pa_k = coordinates.Angle(pa_katpoint() * units.rad).wrap_at(180 * units.deg)
print("astropy:", pa_a.to_string(unit=units.degree))
print("casa (with AZELGEO):", pa_c.to_string(unit=units.degree))
print("meqtrees (with AZELGEO):", pa_m.to_string(unit=units.degree))
print("katpoint:", pa_k.to_string(unit=units.degree))
print("astropy - casa:", (pa_a - pa_c).wrap_at(180 * units.deg).to_string(unit=units.degree))
print("astropy - meqtrees:", (pa_a - pa_m).wrap_at(180 * units.deg).to_string(unit=units.degree))
print("astropy - katpoint:", (pa_a - pa_k).wrap_at(180 * units.deg).to_string(unit=units.degree))
print("casa - katpoint:", (pa_c - pa_k).wrap_at(180 * units.deg).to_string(unit=units.degree))
