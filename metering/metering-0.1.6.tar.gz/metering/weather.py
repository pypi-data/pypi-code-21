# -*- coding: utf-8 -*-
import GeoFunctions as geo
# import DataFunctions as data
import urllib
import sys
import pandas as pd
import numpy as np

# only for testing
import io
import gzip
import pickle
import urllib2
from pydap.client import open_url
import StringIO
import csv
import os
import requests
root = 'f:\\wylanpython'

"""
NOAA's API changed and the LCD API is under development and requires manual
download
"""


def get_stations(geo_name):
    """Locate nearest weather station designated as  TMY3, AWOS, ASOS, or METAR

       :param str geo_name: Geographic description of location (e.g. zip code,
                            town/city and state, etc.)
       :return: Matched station USAF and WBAN ids
       :rtype: tuple str
       """
    input_dir = str()
    for s in sys.path:
        if s.split('\\')[-1] == 'site-packages':
            input_dir = s + '\\metering\\data\\weather\\input'
    stations_file = input_dir + '\\stations.csv'
    options_file = input_dir + '\\options.csv'
    all_stations = geo.import_station_df(stations_file)
    x = np.nan
    addresses = pd.DataFrame(data=[['loc', x, x, x, x, x, x, geo_name, x,
                                    x, '2016-01-01', '2016-01-31',
                                    'hourly', x]],
                             columns=['Site ID', 'Unformatted Address',
                                      'Street Address', 'City', 'State',
                                      'ZIP', 'ZIP+4', 'Lookup Address',
                                      'Lat', 'Lon', 'Start Date', 'End Date',
                                      'Data Period', 'Preferred Station WBAN'])
    addresses['Start Date'] = pd.to_datetime(
        addresses['Start Date']).dt.tz_localize('US/Eastern')
    addresses['End Date'] = pd.to_datetime(
        addresses['End Date']).dt.tz_localize('US/Eastern')
    options = pd.read_csv(
        options_file, dtype={'Station Type': str, 'Include': bool})
    options.index = options['Station Type']
    del options['Station Type']
    options = options.iloc[0:6]['Include'].to_dict()
    # Initialize the geocoder
    geocoder = geo.initiate_geolocator()
    # Geocode the addresses and match to nearest station
    coded_addresses = geo.geocode_addresses(addresses, geocoder)
    match_stations = geo.get_eligible_stations(all_stations, options)
    coded_addresses = geo.find_stations(coded_addresses, match_stations)
    return (coded_addresses['TMY3 USAF ID'].iloc[0],
            coded_addresses['Matched WBAN'].iloc[0])


def download_tmy_weather_data(usaf_id, dst_path):
    """Download TMY3 weather data from NREL and save csv file

       :param str usaf_id: US Airforce weather station identifier
       :param str dst_path: Path do directory to write downloaded csv file
       """
    src_path = (
        'http://rredc.nrel.gov/solar/old_data/nsrdb/1991-2005/data/tmy3/' +
        usaf_id + 'TYA.csv')
    file_name = usaf_id + '.csv'
    dst_path = dst_path + '\\' + file_name
    urllib.urlretrieve(src_path, dst_path)

# Testing


def download_lcd_weather_data(wban_id, start_year, end_year, dst_path):
    """Testing from NOAA legacy applications, found here:
       https://www.ncdc.noaa.gov/cdo-web/datasets
       """
    year_range = range(start_year, end_year + 1, 1)
    for year in year_range:
        src_path = (  # noqa
            'https://www1.ncdc.noaa.gov/pub/data/noaa/' + year + '/')


def noaa_api_test():
    """Test NOAA API

       LCD dataset (historical) not available, test here with GSOY
       """
    r = requests.get(
        'https://www.ncdc.noaa.gov/cdo-web/api/v2/data?' +
        'datasetid=GSOY&startdate=2015-01-01&enddate=2015-01-03',
        headers={'token': 'pymRQhtPXzXFRynnQRCCHaDYUaixWqwc'})
    print r, r.json()


def legacy_noaa_api_test():
    """Testing ish data set (should be same as LCD) from legacy api

       Useful References:
       https://www7.ncdc.noaa.gov/wsregistration/ws_home.html
       https://www7.ncdc.noaa.gov/rest/
       https://www7.ncdc.noaa.gov/wsregistration/CDOServices.html
       """
    wban_list = pickle.load(
        open(root + '\\data\\interim\\meta data\\uniq_wban_list.p', 'r+'))
    usaf_list = pickle.load(
        open(root + '\\data\\interim\\meta data\\uniq_usaf_list.p', 'r+'))
    token1 = 'wDBVzUxVUfmfKKmJKKm'
    # Site Request
    state = 'NH'
    r = requests.get(
        'https://www7.ncdc.noaa.gov/rest/' +
        'services/sites/ish/stateAbbrev/' + state + '/' +
        '?output=csv&token=' + token1)
    string = r.text
    f = StringIO.StringIO(string)
    reader = csv.reader(f, delimiter=',')
    ofile = open(root + '\\data\\api test\\' + state + '.csv', 'wb')
    writer = csv.writer(ofile)
    for row in reader:
        writer.writerow(row)
    ofile.close()
    # Variable Request
    r = requests.get(
        'https://www7.ncdc.noaa.gov/rest/' +
        'services/variables/ish/' +
        '?output=csv&token=' + token1)
    string = r.text
    f = StringIO.StringIO(string)
    reader = csv.reader(f, delimiter=',')
    ofile = open(root + '\\data\\api test\\' + 'Variables' + '.csv', 'wb')
    writer = csv.writer(ofile)
    for row in reader:
        writer.writerow(row)
    ofile.close()
    # Value Request
    # site_id = usaf_list[5] + wban_list[5]
    df = pd.read_csv(root + '\\data\\api test\\' + state + '.csv', header=None)
    site_label = str(df[1].iloc[0])
    start_date = '201701010000'
    end_date = '201701312359'
    r = requests.get(
        'https://www7.ncdc.noaa.gov/rest/' +
        'services/values/ish/' +
        site_label + '/TMP/' +
        start_date + '/' + end_date + '/' +
        '?output=csv&token=' + token1)
    string = r.text
    f = StringIO.StringIO(string)
    reader = csv.reader(f, delimiter=',')
    ofile = open(root + '\\data\\api test\\' + site_label + '.csv', 'wb')
    writer = csv.writer(ofile)
    for row in reader:
        writer.writerow(row)
    ofile.close()


def pydaptest():
    """
       """
    # setup the connection
    url = ('http://nomads.ncdc.noaa.gov/dods/NCEP_NARR_DAILY/197901/197901'
           '/narr-a_221_197901dd_hh00_000')
    modelconn = open_url(url)
    tmp2m = modelconn['tmp2m']

    # grab the data
    lat_index = 200    # you could tie this to tmp2m.lat[:]
    lon_index = 200    # you could tie this to tmp2m.lon[:]
    print tmp2m.array[:, lat_index, lon_index]


def isd_test():
    """
       """
    path = ('ftp://ftp.ncdc.noaa.gov/pub/data/noaa/2017/'
            '724036-03710-2017.gz')
    req = urllib2.Request(path)
    res = urllib2.urlopen(req)
    page = res.read()
    # with gzip.open(root + '\\data\\test.gz', 'wb') as f:
    #     f.write(page)
    # f = open('f:\\wylanpython\\data\\test.gz')
    # f.write(page)
    # f.close()
    # with open('f:\\wylanpython\\data\\test.gz', 'a') as f:
    #     f.write(page)
    # f_src = gzip.open('f:\\wylanpython\\data\\test.gz', 'rb')
    # contents = f_src.read()
    # f_src.close()

    def gunzip_bytes_obj(bytes_obj):
        in_ = io.BytesIO()
        in_.write(bytes_obj)
        in_.seek(0)
        with gzip.GzipFile(fileobj=in_, mode='rb') as fo:
            gunzipped_bytes_obj = fo.read()

        return gunzipped_bytes_obj.decode()


def isd_lite_convert():
    """Integrated survace data fom NOAA, downloaded manually as .gz file,
       unzipped and written as .csv

       This was working before, something appears different in the files
       comming from NOAA

       ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/
       """
    column_labels = ('Year,Month,Day,Hour,Temp,DewPt,'
                     'Pre,WndDir,WndSpd,SkyCov,Precip1H,Precip6H')
    dir_path = root + '\\data\\raw\\isd\\zipped'
    file_list = os.listdir(dir_path)
    i_1 = 0
    i_n = len(file_list)
    i = i_1
    for file_name in file_list[i_1:i_n]:
        i += 1
        print str(i) + ' of ' + str(i_n) + ', ' + file_name.split('.')[0]
        wban = file_name.split('-')[1]
        year = file_name.split('-')[2].split('.')[0]
        src = dir_path + '\\' + file_name
        dst = (root + '\\data\\raw\\isd\\unzipped\\' +
               wban + '-' + year + '.csv')
        f_src = gzip.open(src, 'rb')
        contents = f_src.read()
        f_src.close()
        contents_list = [
            ' '.join(j.split()).replace(' ', ',')
            for j in contents.splitlines()]
        contents_list.insert(0, column_labels)
        with open(dst, 'wb') as f_dst:
            wr = csv.writer(f_dst, delimiter=',')
            wr.writerows([j.split(',') for j in contents_list])
