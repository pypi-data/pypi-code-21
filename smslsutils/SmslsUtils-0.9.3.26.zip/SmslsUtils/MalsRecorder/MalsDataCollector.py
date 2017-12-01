
from .MalsCard import MalsCard
from .MalsCard import MalsCard_DesignService
from SmslsUtils.DataTools import CsvLogger
import time, datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class MalsDataCollector:   
    sample_rate_ms = 500
    max_samples = 10 * 60 * (1000 / sample_rate_ms)
    csv_fields = ['Timestamp','ElapsedTime'] + MalsCard.output_format
    num_channels = MalsCard.num_channels

    # We must specify a port in order to collect data from hardware, otherwise read data from an existing file
    # If a port is specified and a filepath is also given, then save the collected data to that file.
    # If a port is specified but no filepath is given, then just show the data on the console but do not save it.
    def __init__(self, port=None, filepath=None):
        self.log_data = filepath is not None
        self.data = pd.DataFrame(columns = self.csv_fields)
        self.filepath = filepath

        if port is not None:
            self.mc = MalsCard(port)
        else:
            print('Reading data from file: {}'.format(self.filepath))
            self.mc = MalsCard_DesignService(filepath)
            self.log_data = False
            # NOTE: speed up "playback rate" when reading from file so we're not waiting for "new" data as long
            self.sample_rate_ms = 100

    def start(self):
        self.time_start = datetime.datetime.now()
        self.mc.open()
        
        if self.log_data:
            print('Saving data to file: {}'.format(self.filepath))
            self.logger = CsvLogger(buffer_count=100)
            self.logger.create_file(self.filepath, self.csv_fields)
            
    def stop(self):
        self.mc.close()

        if self.log_data:
            self.logger.close()

    def update_data(self):
        while True:
            sample_timestamp = datetime.datetime.now()
            sample_elapsedtime = (sample_timestamp - self.time_start).total_seconds()
            values = self.mc.read_data()
            
            if (len(values) > 0):
                values['Timestamp'] = sample_timestamp
                values['ElapsedTime'] = sample_elapsedtime

                # NOTE: to reduce memory usage, only keep the most recent data window in the dataframe
                self.data = self.data.append(values, ignore_index=True)
                if (len(self.data) > self.max_samples):
                    self.data.drop(self.data.index[[0]], inplace=True)

                # print the current values to the console
                # TODO: print column header with each value, so we know what the data means
                print(self.data.tail(1).to_string(header=False, index=False,
                    float_format=lambda x: "{:0.1f}".format(x)))

                if self.log_data:
                    self.logger.append_data(values)

                yield self.data

