# -*- coding: utf-8 -*-
import pandas as pd
from plot import qc_plots


class MeasurementGroup():
    """Class for merging arbitrary groups of Measurement objects
       """

    def __init__(self):
        self.name = str()
        self.meas_list = list()  # List of Measurement objects
        self.dataframe_list = list()  # List of DataFrames form Export objects
        self.meas_df = pd.DataFrame()  # DataFrame of series from Measurements
        self.meas_grp = str()  # MeasurementGroup subclass
        self.concat_method = str()

    def concat_measurements(self, w, tz):
        """Identify and concatenate Measurement objects representing the same
           physical measurement

           :param str w: Sampling frequency of concatenated Measurements
           :param str tz: Time zone of index of concatenated Measurements
           """
        to_del = list()
        for m1 in self.meas_list:
            for m2 in self.meas_list:
                if ((m1 != m2) and (m1.meas_des == m2.meas_des) and
                   (m1 not in to_del) and (m2 not in to_del)):
                    m1.data = m1.data.combine_first(m2.data)
                    m1.data = m1.data.resample(w).mean()
                    m1.data.index = m1.data.index.tz_convert(tz)
                    to_del.append(m2)
        for m in to_del:
            del self.meas_list[self.meas_list.index(m)]
        self.concat_method = 'concat_measurements'

    def concat_dataframes(self):
        """Concatenate DataFrames from list of Export objects, method assumes
           equal number of columns constant ordering of labels for all
           DataFrames being combind
           """
        if len(self.dataframe_list) > 1:
            self.meas_df = pd.concat(self.dataframe_list)
            self.meas_df.sort_index(inplace=True)
            self.meas_df = self.meas_df.groupby(self.meas_df.index).first()
            self.concat_method = 'concat_dataframes'
        elif len(self.dataframe_list) == 1:
            self.meas_df = self.dataframe_list[0]
            self.meas_df.sort_index(inplace=True)
            self.meas_df = self.meas_df.groupby(self.meas_df.index).first()
            self.concat_method = 'concat_dataframes'
        else:
            print 'No data present'

    def to_df(self):
        """Combine Measurements in measurement list into DataFrame
           """
        data = list()
        for m in self.meas_list:
            data.append(m.data)
        if len(data) > 0:
            self.meas_df = pd.concat(data, axis=1)
            self.meas_df.sort_index(inplace=True)
        else:
            print 'No data present'

    def qc_plots(self, output_dir, start_date, end_date):
        """Plot data of Measurement objects and write to PDF

           :param str output_dir: Path to directory to write file
           :param str start_date: Left x-axis bound of time series
           :param str end_date: Right x-axis bound of time series
           :param str concat_method: Method used to concatenate Export data
           """
        qc_plots(self, output_dir, start_date, end_date)


class Location(MeasurementGroup):
    """MeasurementGroup subclass, implements methods specific to groupings of
       data sharing a geographic location
       """

    def __init__(self):
        MeasurementGroup.__init__(self)
        self.meas_grp = Location  # MeasurementGroup subclass
        self.address = str()

    @staticmethod
    def make(export_list, location_id, concat_method, w, tz):
        """Static way of calling all routine methods of Location class

           :param list export_list: List of Export objects
           :param str location_id: Location object ID
           :param str concat_method: Method used to concatenate Export data
           :return: Location object with merged Export data
           :rtype: Location
           """
        loc = Location()
        for e in export_list:
            loc.meas_list.extend(e.meas_list)
            loc.dataframe_list.append(e.meas_df)
        if concat_method == 'concat_measurements':
            loc.concat_measurements(w, tz)
            loc.to_df()
        elif concat_method == 'concat_dataframes':
            loc.concat_dataframes()
        loc.name = location_id
        return loc


class Measurement():
    """Class for operating on a single column of time series data
       """

    def __init__(self, data, name, w):
        self.data = data
        self.label = str()  # appears in legend of qc plot (from tech)
        self.quant = str()  # Quantity being measured
        self.dim = str()  # Dimensions of quantity
        self.name = name  # appears as title in qc plot
        self.w = w  # Sampling frequency
        self.meas_des = str()  # Unique measurment description
        self.state_logger_labels = list()  # List of labels of state loggers

    # TODO: Finish documentation of this method
    def interpolate_count(self):
        """Pulse count interpolation method

           Notes
           -----
           Method calculates time delta between values
           """
        df = pd.DataFrame()
        df['count'] = self.data
        df['time'] = self.data.index
        # Calculate time difference between values in minutes
        df['diff'] = df['time'].diff()
        # Use of 'diff int' is a misnomer, values are not always integers
        df['diff int'] = df['diff'].astype('timedelta64[s]') / 60.0
        del df['time'], df['diff']
        df = df[pd.notnull(df['diff int'])]
        # Sampling interval dictionary
        # Three cases for interpolation
        #    1. Sampling frequency is equal to desired frequency
        #    2. Sampling frequency is higher than desired
        #    3. Sampling frequency is lower than desired
        # Typical sampling intervals used
        sd = {'1Min': 1, '30S': 0.5, 'H': 60, 'S': 1 / 60.}
        # Case 1
        df0 = df[df['diff int'] == sd[self.w]]
        df0 = df0.resample(self.w).last()
        # Case 2
        df1 = df[df['diff int'] > sd[self.w]]
        df1 = df1.resample(self.w).last()
        # Limit interpolation based on sampling frequency
        if self.w == '1Min':
            inter_lim = 16
        elif self.w == '1S':  # TODO: Account for multiple representations of w
            inter_lim = 60
        else:
            inter_lim = 1
        # Case 2
        if df1.empty == False:
            df1.fillna(method='backfill', limit=inter_lim, inplace=True)
        df1['scaled count'] = df1['count'] / df1['diff int']
        # Case 3
        df2 = df[df['diff int'] < sd[self.w]]
        df2 = df2.resample(self.w).sum()
        del df['count']
        df = df.resample(self.w).last()
        df['df0'] = df0['count']
        df['df1'] = df1['scaled count']
        df['df2'] = df2['count']
        self.data = df.df1.add(df.df2, fill_value=0).add(
            df.df0, fill_value=0)
        # Drop duplicates from index
        self.data = self.data.groupby(self.data.index).first()
        self.data.name = self.meas_des

    def interpolate_state(self):
        """Interpolate binary values from state loggers by resampling
           and filling forward, minimum resolution of sampling frequency
           """
        self.data = self.data.resample(self.w).last()
        self.data.fillna(method='ffill', inplace=True)
        # Drop duplicates from index
        self.data = self.data.groupby(self.data.index).first()

    def interpolate_linear(self):
        """Linear interpolation with built in limits
           """
        try:
            self.data = self.data.resample(self.w).last()
        except:
            # This resample throws an ambiguous time error when near Fall DST,
            # issue apperas to be closed on github (#8744) but I'm still
            # having to resolve with tz_convert to UTC
            self.data = self.data.tz_convert('UTC').resample(
                self.w).last()
        if self.w == '1Min':
            inter_lim = 61
        elif self.w == '15Min':
            inter_lim = 4
        elif self.w == '1S':
            inter_lim = 60
        else:
            inter_lim = 1
        self.data.interpolate(inplace=True,
                              limit=inter_lim, limit_direction='both')
        # TODO: why not use a dropna here?
        # Drop duplicates from index
        self.data = self.data.groupby(self.data.index).first()

    def interpolate(self):
        """Method to decide which type of interpolation to perform based on
           measurement quantity
           """
        if self.data.empty:
            print 'No data to interpolate'
        else:
            if self.quant == 'Counts':
                self.interpolate_count()
            elif (('State' in self.quant) or ('Light' in self.quant) or
                  (self.quant in self.state_logger_labels)):
                self.interpolate_state()
            else:
                self.interpolate_linear()


class HOBOWareMeasurement(Measurement):
    """Measurement subclass, specific to data exported from HOBOWare
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def scale_mV(self):
        """If a logger wasn't configured properly, the output from HOBOWare
           may contain dimensions of mV instead of A when measuring current,
           the data can be 'scaled' by dividing by 333.0
           """
        if 'mV' in self.data.name.split(',')[0]:
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('mV', 'Current')

    def scale_Voltage_RMS(self):
        """Same issue as in scale_mV method can occur as
           'Voltage RMS,' corrected in same way
           """
        if 'Voltage RMS, A' in self.data.name.split('(')[0]:
            self.data.name = self.data.name.replace('Voltage RMS', 'Current')
        elif 'Voltage RMS, mV' in self.data.name.split('(')[0]:
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('Voltage RMS', 'Current')

    def get_lable(self):
        """When launching a logger with HOBOWare, an optional label field is
           provided to describe what is being measured, this method parses that
           input if present
           """
        if 'LBL' in self.data.name:
            self.label = self.data.name.split('LBL:')[1].split(')')[0].strip()

    def get_quant(self):
        """Parse the quantity measured from column label, if the logger was
           measuring state (on/off) then HOBOWare allows this value to be
           manually changed by the individual launching the logger, in these
           cases, the manually entered labels must be combiled into a list so
           the correct for of interpolation is applied, this list is inputted
           using the kwarg 'state_logger_labels'
           """
        self.state_logger_labels.append('Hawkeye')
        self.state_logger_labels.append('Light')
        if (self.data.name.split('(')[0].split(',')[0].rstrip() in
           self.state_logger_labels):
            self.quant = 'State'
            self.label = (self.label + ', ' +
                          self.data.name.split('(')[0].split(',')[0].rstrip())
        else:
            self.quant = self.data.name.split('(')[0].split(',')[0].rstrip()

    def get_dim(self):
        """Parse dimensions of quantity measured from column label
           """
        if ('State' in self.quant):
            self.dim = 'On/Off'
        else:
            try:
                self.dim = unicode(
                    self.data.name.split('(')[0].split(',')[1].strip(),
                    errors='replace')
            except IndexError:
                print ("Couldn't parse measurement dimensions: " +
                       self.data.name)
                self.dim = 'could not parse'

    # TODO: Figure out how name attribute is used by other functions
    def get_name(self):
        """
           """
        self.name = (self.name + '_' +
                     self.data.name.split('LGR S/N: ')[1].split(',')[0] + '_' +
                     self.data.name.split('SEN S/N: ')[1].split(',')[0].split(
                         ')')[0])

    def get_meas_des(self):
        """Unique identifier for a specific measurement, allows for
           measurements to be merged across multiply files
           """
        self.meas_des = self.name + ' ' + self.quant
        self.data.name = self.meas_des + ' ' + self.label

    @staticmethod
    def make(data, name, w, **kwargs):
        """Static way of calling all routine methods and returning instance
           """
        m = HOBOWareMeasurement(data, name, w)
        if 'state_logger_labels' in kwargs:
            m.state_logger_labels = kwargs['state_logger_labels']
        m.scale_mV()
        m.scale_Voltage_RMS()
        m.get_lable()
        m.get_quant()
        m.get_dim()
        m.get_name()
        m.get_meas_des()
        m.interpolate()
        return m


class HOBOLinkMeasurement(Measurement):
    """Measurement subclass, specific to data exported from HOBOLink
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def scale_mV(self):
        """If a logger wasn't configured properly, the output from HOBOLink
           may contain dimensions of mV instead of A when measuring current,
           the data can be 'scaled' by dividing by 333.0
           """
        if 'mV' in self.data.name.split('(')[0]:
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('mV', 'Current')

    def scale_Voltage_RMS(self):
        """Same issue as in scale_mV method can occur as
           'Voltage RMS,' corrected in same way
           """
        if (('Voltage RMS' in self.data.name.split('(')[0]) and
           ('mV' in self.data.name.split(',')[1])):
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('Voltage RMS', 'Current')

    def get_label(self):
        """When launching a logger with HOBOLink, an optional label field is
           provided to describe what is being measured, this method parses that
           input if present
           """
        self.label = self.data.name.split(',')[-1].strip()

    def get_quant(self):
        """Parse the quantity measured from column label
           """
        self.quant = self.data.name.split('(')[0].strip()
        if self.quant == 'A':
            self.quant = 'Current'

    def get_dim(self):
        """Parse dimensions of quantity measured from column label
           """
        self.dim = self.data.name.split(',')[1].strip()

    def get_name(self):
        """
           """
        self.name = (self.name + '_' +
                     self.data.name.split(':')[0].split(' ')[-1] + '_' +
                     self.data.name.split(':')[1].split(')')[0])
        # TODO: Using Cool Smart convention for now, need to reevaluate
        if self.quant != 'Current':
            self.name = self.name.split('-')[0]
        else:
            self.name = self.name.replace('-', 'x')

    def get_meas_des(self):
        """Unique identifier for a specific measurement, allows for
           measurements to be merged across multiply files
           """
        self.meas_des = self.name + ' ' + self.quant
        self.data.name = self.meas_des + ' ' + self.label

    @staticmethod
    def make(data, name, w):
        """Static way of calling all routine methods and returning instance
           """
        m = HOBOLinkMeasurement(data, name, w)
        m.scale_mV()
        m.scale_Voltage_RMS()
        m.get_label()
        m.get_quant()
        m.get_dim()
        m.get_name()
        m.get_meas_des()
        m.interpolate()
        return m


class SmartThingsMeasurement(Measurement):
    """Measurement subclass, specific to data exported from SmartThings

       May need to rename ThinkSpeak, not sure yet, also need to pull in API
       from James, Chase, and Alex, this class only works with data manually
       pulled from the website
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def scale_power(self):
        """Convert W to kW
           """
        self.data = self.data / 1000.0  # W to kW

    def get_quant(self):
        """Set measurement quantity
           """
        self.quant = 'Power'

    def get_dim(self):
        """Set measurement dimensions
           """
        self.dim = 'kW'

    def get_label(self):
        """
           """
        self.label = ' '.join(self.name.split(' ')[1:]).split('(')[0].strip()

    def get_name(self):
        """
           """
        self.name = self.name.split(' ')[0]

    def get_meas_des(self):
        """Unique identifier for a specific measurement, allows for
           measurements to be merged across multiply files
           """
        self.meas_des = self.name + ' ' + self.label + ' ' + self.quant
        self.data.name = self.meas_des

    @staticmethod
    def make(data, name, w):
        """Static way of calling all routine methods and returning instance
           """
        m = SmartThingsMeasurement(data, name, w)
        m.scale_power()
        m.get_quant()
        m.get_dim()
        m.get_label()
        m.get_name()
        m.get_meas_des()
        m.interpolate()
        return m


class LCDMeasurement(Measurement):
    """Local Climatological Data (LCD) measurement class
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def get_quant(self):
        if 'TEMP' in self.data.name:
            self.quant = 'Temp'
        elif 'Humidity' in self.data.name:
            self.quant = 'RH'
        elif 'Wind' in self.data.name:
            self.quant = 'WndSpd'

    def get_dim(self):
        if 'TEMP' in self.data.name:
            self.dim = 'F'
        elif 'Humidity' in self.data.name:
            self.dim = '%'
        elif 'Wind' in self.data.name:
            self.dim = 'm/h'

    def get_name(self):
        self.name = self.name + '_' + self.quant

    def get_meas_des(self):
        self.meas_des = 'LCD_' + self.quant

    def get_label(self):
        self.label = self.meas_des
        self.data.name = 'LCD_' + self.quant

    @staticmethod
    def make(data, name, w):
        m = LCDMeasurement(data, name, w)
        m.get_quant()
        m.get_dim()
        m.get_name()
        m.get_meas_des()
        m.get_label()
        m.interpolate()
        return m


class TMYMeasurement(Measurement):
    """Typical Meteorological Year 3 (TMY/TMY3) measurement class
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def get_quant(self):
        if 'Tdb' in self.data.name:
            self.quant = 'Temp'
        elif 'RH' in self.data.name:
            self.quant = 'RH'
        elif 'Wind Speed' in self.data.name:
            self.quant = 'WndSpd'

    def get_dim(self):
        if 'Tdb' in self.data.name:
            self.dim = 'F'
        elif 'RH' in self.data.name:
            self.dim = '%'
        elif 'Wind Speed' in self.data.name:
            self.dim = 'm/h'

    def get_name(self):
        self.name = self.name + '_' + self.quant

    def get_meas_des(self):
        self.meas_des = 'TMY_' + self.quant

    def get_label(self):
        self.label = self.meas_des
        self.data.name = 'TMY_' + self.quant

    @staticmethod
    def make(data, name, w):
        m = TMYMeasurement(data, name, w)
        m.get_quant()
        m.get_dim()
        m.get_name()
        m.get_meas_des()
        m.get_label()
        m.interpolate()
        return m
