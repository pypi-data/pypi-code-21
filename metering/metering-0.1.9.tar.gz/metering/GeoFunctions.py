# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 19:09:43 2016

@author: Nathan.Hinkle

Provides functions used for downloading and parsing NOAA Weather Data

"""

import sys
import pandas as pd
sys.path.insert(1, 'C:\\Users\\nathan.hinkle\\python\\oss-devel\\geopy')
import geopy
from geopy.distance import vincenty


def ordinal(n):
    """Takes an integer and returns a string with the ordinal, e.g.
       1 -> "1st", 2 -> "2nd", 10 -> "10th".
       """
    return ("%d%s" %
            (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]))


def bool_convert(var):
    """Convert string to boolean. Matches string "true" for True in any case,
       all others match to False.
       """
    return str(var).lower() == "true"


def initiate_geolocator(auth_api=False):
    """Creates a GeoPy geolocator instance for the ArcGIS Geocoding service.
       If auth_api is true, uses ArcGIS credentials as saved in
       arcgis_credentials.py.
       """

    if auth_api:
        # Get credentials
        import arcgis_credentials as creds

        # Initiate geolocator
        geolocator = geopy.geocoders.ArcGIS(
            client_id=creds.ARCGIS_CLIENT_ID,
            client_secret=creds.ARCGIS_CLIENT_SECRET)
    else:
        geolocator = geopy.geocoders.ArcGIS()

    return geolocator


def import_station_df(path):
    """Import the list of stations from the specified CSV file.
       """
    df = pd.read_csv(
        path,
        converters={
            'WBAN': str, 'WMO': str, 'CallSign': str,
            'ClimateDivisionCode': str, 'ClimateDivisionStateCode': str,
            "TMY3": bool_convert, "AWOS": bool_convert,
            "ASOS": bool_convert, "METAR": bool_convert,
            "CRN": bool_convert, "Known": bool_convert,
            "Unknown": bool_convert, "Any Except CRN": bool_convert,
            'TMY3 USAF ID': str,})
    return df


def _filter_stations(stations, include_types, tmy_only=False):
    if tmy_only:
        return stations[stations.apply(
            lambda r: any([r[s] for s in include_types]) and
            r['TMY3'] is True, axis=1)]
    else:
        return stations[stations.apply(
            lambda r: any([r[s] for s in include_types]), axis=1)]


def get_eligible_stations(stations, options):
    """Given a dataframe of stations and selected weather station options,
       return a dataframe of only stations which meet the option criteria.
       Options should be retrieved using import_address_workbook.
       """
    tmy3 = options.pop("TMY3")
    types = [o for o, v in options.iteritems() if v]
    return _filter_stations(stations, types, tmy3)


def import_address_workbook(path):
    """Import the addresses and station type selections from the address
       template workbook. Return tuple of dataframes, (addresses, options)
       """
    lower_str = lambda x: str(x).lower()

    addresses = pd.read_excel(
        path,
        sheetname="Locations",
        parse_dates=['Start Date', 'End Date'],
        converters={'Site ID': str, 'Unformatted Address': str,
                    'Street Address': str, 'City': str, 'State': str,
                    'ZIP': str, 'ZIP+4': str, 'Lookup Address': str,
                    'Data Period': lower_str, 'Preferred Station WBAN': str})
    options = pd.read_excel(path,
                            sheetname="ValidationOptions",
                            converters={
                                'Station Type': str, 'Include': bool_convert},
                            index_col=0, parse_cols="I:J")
    options = options.ix[0:6]['Include'].to_dict()
    return (addresses, options)


def _annotate_distance(row, cols):
    lat1 = row[cols['lat1']]
    lat2 = row[cols['lat2']]
    lon1 = row[cols['lon1']]
    lon2 = row[cols['lon2']]
    if any(pd.isnull([lat1, lat2, lon1, lon2])):
        return row
    distance = vincenty((lat1, lon1), (lat2, lon2)).miles
    row[cols['out']] = distance
    return row


def get_nearest_station(coords, stations, n=1):
    """Find nth nearest NOAA weather station to given coordinates. Return
       station details from the stations CSV file.

       :coords: tuple of coordinates, (latitude, longitude), as floats
       :stations: Pandas DataFrame of stations
       :n: nth closest station to get; defaults to 1st
       """
    distances = stations.apply(
        lambda x: vincenty(
            coords, (x['Latitude'], x['Longitude'])).miles, axis=1)
    closest_row_id = distances.nsmallest(n).idxmax()
    closest_dist = distances.ix[closest_row_id]
    closest_station_df = stations.ix[closest_row_id]
    closest_station = closest_station_df.to_dict()
    closest_station['Distance'] = closest_dist
    if len(str(closest_station['WBAN'])) < 5:
        closest_station['WBAN'] = (
            5 - len(str("183"))) * '0' + str(closest_station['WBAN'])
    if n > 1:
        nth = ordinal(n) + " "
    else:
        nth = ""
    print "Found %snearest station %.1f miles away at (%.4f, %.4f) - %s, %s" % (nth, closest_station['Distance'], closest_station['Latitude'], closest_station['Longitude'], closest_station['Location'], closest_station['State'])
    return closest_station


def _geocode_address(address, geolocator, retry=0):
    try:
        if type(address) is tuple and len(address) == 2 and type(address[0]) is float and type(address[1]) is float:
            site_location = geolocator.reverse(address, True)
        else:
            site_location = geolocator.geocode(str(address))
    except geopy.exc.GeopyError as e:
        retry = retry + 1
        if retry > 3:
            print "Tried 3 times, aborting attempt for this address"
            return None
        else:
            print 'Trying to encode address: "%s"' % address
            print "Error occurred during encoding: %s" % e
            print "Retrying 3 times: attempt %i" % retry
            return _geocode_address(address, geolocator, retry)
    if site_location is None:
        print "Unable to geocode address."
    else:
        print "Found address location: %s is at (%.4f, %.4f)" % (site_location.address, site_location.latitude, site_location.longitude)
    return site_location


def _geocode_row(row, sleep, geolocator):
    if (pd.isnull(row['Lookup Address']) or
       row['Lookup Address'][0:11] == "[WARNING:] " or
       not pd.isnull(row['Preferred Station WBAN']) or
       not (pd.isnull(row['Lat']) and pd.isnull(row['Lon']))):
        return row
    geocode_result = _geocode_address(row['Lookup Address'], geolocator)
    if geocode_result is None:
        return row
    row['Lat'] = geocode_result.latitude
    row['Lon'] = geocode_result.longitude
    return row


def geocode_addresses(addresses, geolocator, batch=False, pause=1):
    """Geocode all valid addresses in DataFrame addresses, using geolocator
       GeoPy object. Optionally batch process if the geolocator supports
       batch processing. If not batch processing, pause between each
       geocode request to avoid hitting API limits or service rate limiting.
       """
    if batch:
        raise NotImplementedError(
            "Batch processing has not yet been implemented")
    return addresses.apply(
        _geocode_row, axis=1, sleep=pause, geolocator=geolocator)


def _find_station_row(row, stations, n=1):
    if not pd.isnull(row['Preferred Station WBAN']):
        print "Preferred WBAN station was specified"
        row['Matched WBAN'] = row['Preferred Station WBAN']
        return row
    if pd.isnull(row['Lat'] or pd.isnull(row['Lon'])):
        print "Lat or Lon was not specified"
        return row
    coords = (row['Lat'], row['Lon'])
    match = get_nearest_station(coords, stations, n)
    row['Matched WBAN'] = match['WBAN']
    row['Matched Name'] = match['Location']
    row['Matched Latitude'] = match['Latitude']
    row['Matched Longitude'] = match['Longitude']
    row['Distance to Station'] = match['Distance']
    row['TMY3 USAF ID'] = match['TMY3 USAF ID']
    return row


def find_stations(addresses, stations, n=1):
    """Use DataFrame of geocoded addresses and DataFrame of eligible stations
       to determine nearest station to each address.
       """
    return addresses.apply(_find_station_row, axis=1, stations=stations, n=n)
