from datetime import date, timedelta
import dateutil.relativedelta
import urllib
import urllib2
import os
from io import StringIO
from collections import OrderedDict
import GeoFunctions as geo
import pandas as pd
from geopy.distance import vincenty


class ConnectionError(Exception):
    pass


class NOAADataError(Exception):
    """
    Custom exception for errors retrieving data from the NOAA website.
    """
    pass


class DataMismatchError(Exception):
    pass


def get_weather_data_raw(station_id, month, year, period="hourly"):
    """
    Retrieve raw CSV data from NOAA NCDC webpage for the specified
    month/year. Download hourly or daily data. If daily data is unavailable,
    no data is available for date, or station ID is invalid, a
    NOAADataError exception will be raised.
    """
    if period == "daily":
        which = "ASCII Download (Daily Summ.) (10B)"
    elif period == "hourly":
        which = "ASCII Download (Hourly Obs.) (10A)"
    else:
        raise AttributeError("Data period must be \"hourly\" or \"daily\".")
    url = "https://www.ncdc.noaa.gov/qclcd/QCLCD"
    varval = "%s%04d%02d" % (station_id, year, month)
    values = {"reqday": "E",
              "which": which,
              "prior": "N",
              "VARVALUE": varval}
    data = urllib.urlencode(values)
    try:
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        result = response.read()
    except urllib2.HTTPError as e:
        raise NOAADataError("The server returned an error message: %s" % e)
    except Exception as e:
        raise ConnectionError("Error encountered while trying to open webpage. "
                            "Check your internet connection, and try browsing "
                            "to https://ncdc.noaa.gov/qclcd/QCLCD?prior=N in a "
                            "browser to ensure the service is available.\n\n%s" % e)
        
    if result[0:6] == "<HTML>":
        raise NOAADataError("The response contained a webpage, not a data file." 
        "\nCheck that you entered a valid date range and station ID.\n\n" + 
        result)
    
    return (result, response)
    
def get_weather_data_range(station_id, start_month, start_year, end_month, end_year, period='hourly'):
    if (start_year > end_year) or (start_year == end_year and end_month < start_month):
        raise AttributeError("Invalid start/end dates. Start date must be before end date.")
    if any([type(d) is not int for d in [start_month, start_year, end_month, end_year]]):
        raise AttributeError("Invalid start/end dates. All values must be integers.")
    if start_month > 12 or start_month < 1 or end_month > 12 or end_month < 1:
        raise AttributeError("Invalid start/end dates. Months must be whole integers between 1 and 12 inclusive.")
    if start_year < 2005 or end_year < 2005:
        raise AttributeError("Invalid start/end dates. Year must be after 2005 and no later than current year.")
    if (end_year > date.today().year or 
        (end_year == date.today().year and end_month > date.today().month)):
        raise AttributeError("Invalid start/end dates. End month cannot be later than current month of current year.")
    if end_year == date.today().year and end_month == date.today().month and date.today().day <= 7:
        raise AttributeError("Invalid start/end dates. Data for current month is not available for at least one week.")
    
    print "Getting %s data for %s from %2d/%4d to %2d/%4d" % (period, station_id, start_month, start_year, end_month, end_year)
    all_weather_data = OrderedDict()
    
    for year in range(start_year, end_year + 1):
        for month in range(1,13):
            if ( (year == start_year and month < start_month) or 
                 (year == end_year and month > end_month) or 
                 ((year, month) in all_weather_data.keys())):
                continue
            
            print "  Downloading %02d/%04d" % (month, year)
            all_weather_data[(year, month)] = get_weather_data_raw(station_id, month, year, period)[0]


    return all_weather_data    

def _get_prev_month(timestamp):
    return timestamp.replace(day=1) - timedelta(days=1)

def _get_next_month(timestamp):
    return timestamp + dateutil.relativedelta.relativedelta(months=1)


def export_data_for_addresses(addresses, address_groups, stations,
                              output_path, n=1, existing_files={}):
    failed_stations = pd.DataFrame()
    output_path = output_path.replace("\\", "/")
    for (wban, period), group in address_groups:
        min_date = group['Start Date'].min()
        max_date = group['End Date'].max()
        filename = os.path.join(output_path, wban)
        if (wban, period) in existing_files.keys():
            # We already have some data for this site
            (existing_start, existing_end, existing_info) = existing_files[
                (wban, period)]
            addresses.loc[addresses[addresses['Matched WBAN'] == wban].index,
                          "Chosen Station ID"] = existing_info['Location']
            addresses.loc[addresses[addresses['Matched WBAN'] == wban].index,
                          "Output Filename"] = wban + '.csv'
            addresses.loc[addresses[addresses['Matched WBAN'] == wban].index,
                          "Station Lat"] = existing_info['Lat']
            addresses.loc[addresses[addresses['Matched WBAN'] == wban].index,
                          "Station Lon"] = existing_info['Lon']
            addresses.loc[addresses[addresses['Matched WBAN'] == wban].index,
                          "Nth station from address"] = n
            if min_date < existing_start:
                try:
                    before_data = get_weather_data_range(
                        wban, min_date.month, min_date.year,
                        _get_prev_month(existing_start).month,
                        _get_prev_month(existing_start).year, period.lower())
                except NOAADataError as e:
                    print ("Error occurred while trying to get data"
                           "from NOAA: %s" % e)
                    failed_stations = failed_stations.append(
                        group, ignore_index=True)
                except ConnectionError as e:
                    print ("Error occurred while trying to connect"
                           " to internet. Aborting download.")
                    raise
                else:
                    print "Downloaded additional before data; need to splice"
                    station_info = output_data(
                        filename, before_data, period,
                        additional=("before", existing_info))
            if max_date > existing_end:
                # Need to add data to end of file
                try:
                    after_data = get_weather_data_range(
                        wban,
                        _get_next_month(existing_end).month,
                        _get_next_month(existing_end).year, max_date.month,
                        max_date.year, period.lower())
                except NOAADataError as e:
                    print ("Error occurred while trying to get data"
                           " from NOAA: %s" % e)
                    failed_stations = failed_stations.append(
                        group, ignore_index=True)
                except ConnectionError as e:
                    print ("Error occurred while trying to connect to"
                           " internet. Aborting download.")
                    raise
                else:
                    print "Downloaded additional after data; need to splice"
                    station_info = output_data(
                        filename, after_data, period,
                        additional=("after", existing_info))
        else:
            try:
                data = get_weather_data_range(
                    wban, min_date.month, min_date.year, max_date.month,
                    max_date.year, period.lower())
            except NOAADataError as e:
                print ("Error occurred while trying to get"
                       " data from NOAA: %s" % e)
                failed_stations = failed_stations.append(
                    group, ignore_index=True)
            except ConnectionError as e:
                print ("Error occurred while trying to connect"
                       " to internet. Aborting download.")
                raise
            else:
                station_info = output_data(filename, data, period)
                addresses.loc[
                    addresses[addresses['Matched WBAN'] == wban].index,
                    "Chosen Station ID"] = station_info['Location']
                addresses.loc[
                    addresses[addresses['Matched WBAN'] == wban].index,
                    "Output Filename"] = wban + ".csv"
                addresses.loc[
                    addresses[addresses['Matched WBAN'] == wban].index,
                    "Station Lat"] = station_info['Lat']
                addresses.loc[
                    addresses[addresses['Matched WBAN'] == wban].index,
                    "Station Lon"] = station_info['Lon']
                addresses.loc[
                    addresses[addresses['Matched WBAN'] == wban].index,
                    "Nth station from address"] = n
                existing_files[(wban, period)] = (
                    min_date, max_date, station_info)
    # Get addresses where files were retrieved
    summary_df = addresses[
        addresses.apply(
            lambda r: (r['Matched WBAN'], r['Data Period']) in
            existing_files.keys(), axis=1)]
    summary_df = summary_df.apply(
        geo._annotate_distance, axis=1,
        cols={'lat1': 'Lat', 'lon1': 'Lon', 'lat2': 'Station Lat',
              'lon2': 'Station Lon', 'out': 'Actual Distance to Station'})
    summary_df = summary_df[['Site ID', 'Matched WBAN', 'Chosen Station ID',
                             'TMY3 USAF ID', 'Station Lat', 'Station Lon',
                             'Actual Distance to Station',
                             'Nth station from address', 'Output Filename']]
    summary_file = os.path.join(output_path, 'SUMMARY.csv')
    if n == 1:
        # First time, export header
        summary_df.to_csv(summary_file, index=False)
    else:
        # Future times, don't
        sf = open(summary_file, 'a')
        summary_df.to_csv(sf, index=False, header=False)
        sf.close()
    if len(failed_stations) > 0:
        n = n + 1
        # Get next closest stations
        failed_stations = geo.find_stations(failed_stations, stations, n)
        # Regroup with new station IDs
        fail_group = failed_stations.groupby(['Matched WBAN', 'Data Period'])
        # Recursively call export for the new downloads required
        export_data_for_addresses(failed_stations, fail_group, stations,
                                  output_path, n, existing_files)


def output_data(basepath, data, period, additional=False):
        path = basepath + ".csv"
        month_summary_path = basepath + "_monthly_summary.csv"
        
        if additional is not False:
            (where, site_info) = additional
            has_data_started = True
            #mode = 'r'
            if where == 'before':
                mode = 'r'
            elif where == 'after':
                mode = 'a+'
            else:
            #if where not in ['before','after']:
                raise AttributeError("If adding additional data to file, must specify \"before\" or \"after\"")
        else:
            where = None
            mode = 'w'
            site_info = {}
            has_data_started = False
            
        f = open(path, mode)
        
        if where == 'before':
            file_lines = f.readlines()

        if additional and period == 'daily':
            daily_summary_df = pd.read_csv(month_summary_path)
        elif period == 'daily':
            daily_summary_df = pd.DataFrame()


        insertion_line = 1
        for entry, data_text in data.iteritems():            
            print "Parsing download of %s" % str(entry)
            # print type(entry)
            i_line = 0
            data_start_line = 0
            data_last_line = -1
            month_sumr_start_line = 0
            month_sumr_last_line = 0
            for line in data_text.splitlines():
                if line[0:18] == "Station Location: ":
                    location = line[18:]
                    if 'Location' in site_info.keys() and site_info['Location'] != location:
                        raise DataMismatchError("WARNING: Location doesn't match first file!\n" +
                                                "First file location: %s" % site_info['Location'] +
                                                "\nCurrent file location: %s" % location)
                    else:
                        print "Found station location: %s" % location
                        site_info['Location'] = location
            
                elif line[0:5] == "Lat: ":
                    lat = float(line[5:])
                    site_info['Lat'] = lat
                    if 'Lat' in site_info.keys() and site_info['Lat'] != lat:
                        raise DataMismatchError("WARNING: Latitude doesn't match previous file!" +
                                                "\nPrevious file lat: %.4f" % site_info['Lat'] +
                                                "\nCurrent file lat: %.4f" % lat)
                elif line[0:5] == "Lon: ":
                    lon = float(line[5:])
                    site_info['Lon'] = lon
                    if 'Lon' in site_info.keys() and site_info['Lon'] != lon:
                        raise DataMismatchError("WARNING: Longitude doesn't match previous file!" +
                                                "\nPrevious file lon: %.4f" % site_info['Lon'] +
                                                "\nCurrent file lon: %.4f" % lon)
                
                elif data_start_line == 0 and line.count(",") > 4 and 'WBAN' in line:
                    if 'Header' in site_info.keys() and site_info['Header'] != line:
                        raise DataMismatchError("WARNING: Data header does not match first file!" +
                                                "\nFirst header: \n%s" % site_info['Header'] +
                                                "\nCurrent header: \n%s" % line)
                    elif where is None:
                        #print "Found column headers: \n%s" % line
                        print "Found column headers"
                        site_info['Header'] = line
                        f.write(line + '\n')
                    else: 
                        # Check header against existing file
                        f.seek(0)                        
                        file_header = f.readline()
                        if file_header.strip() != line.strip():
                            raise DataMismatchError("WARNING: Data header does not match existing file on disk.\n" + 
                                                    "Existing header: \n\"%s\"" % file_header + 
                                                    "\nNew header: \n\"%s\"" % line)
                        else:
                            print "Header on disk matches download"
                            
                    has_data_started = True
                    data_start_line = i_line + 1
            
                if has_data_started and "</pre>" in line:
                    if period == 'hourly':
                        data_last_line = i_line
                        print "Found last line: %i" % data_last_line
                    elif period == 'daily':
                        month_sumr_last_line = i_line
                        print "Found last month summary line: %i" % month_sumr_last_line
                    else:
                        print "Invalid period specified: %s is not ne of daily or hourly" % period
                        
                    break
                
                if period == 'daily' and has_data_started and ':,' in line:
                    if month_sumr_start_line == 0:
                        month_sumr_start_line = i_line
                        data_last_line = i_line - 1
                        print "Found first line of month summary: %i" % month_sumr_start_line
                        print "Last line of main data: %i" % data_last_line
                    #else:
                    #    month_sumr_last_line = i_line
                    
                
            
                i_line = i_line + 1
            
            new_line = '\n'.join([line for line in data_text.splitlines()[data_start_line:data_last_line] if line != ''])
            if where is None or where=='after':
                f.flush()
                f.seek(0,2)
                f.write(new_line)
            elif where == 'before':
                file_lines.insert(insertion_line, new_line)
                insertion_line = insertion_line + 1
                
            if period == 'daily':
                # bring in the new daily chunk
                csv_summary_text = u'\n'.join([line for line in data_text.splitlines()[month_sumr_start_line:month_sumr_last_line] if line != ''])
                try:                    
                    datastream = StringIO(csv_summary_text)
                    new_summary_df = pd.read_csv(datastream, header=None, index_col=0, names=range(3))
                    new_summary_df = new_summary_df.drop([2], axis=1)
                    new_summary_df_T = new_summary_df.transpose()
                    new_summary_df_T['month'] = entry[1]
                    new_summary_df_T['year'] = entry[0]
                    new_summary_df_T.set_index(['year', 'month'], inplace=True)
                    daily_summary_df = pd.concat([daily_summary_df, new_summary_df_T])
                except Exception as e:
                    print "Error trying to read in daily summary data: %s" % e
                    print "Summary text: %s" % csv_summary_text
        f.close()
        if where == 'before':
            f = open(path, 'w')
            f.writelines(file_lines)
            f.close()
        
        if period == 'daily':
            # Output the daily summary file for the site
            daily_summary_df.sort_index(inplace=True)
            daily_summary_df.to_csv(month_summary_path)
        
        return site_info
#            f.writelines(data_text.splitlines()[data_start_line:data_last_line])
    
    # return all_data
    
