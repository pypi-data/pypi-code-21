
import csv
import os

class CsvLogger:

    def __init__(self, buffer_count=50):
        self.buffer_count = buffer_count
        self.buffer = []
        self.writer = None

    def create_file(self, filepath, header):
        self.filepath = filepath
        self.header = header

        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            
        with open(self.filepath, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, delimiter=',', fieldnames=self.header)
            writer.writeheader()

    def close(self):
        self.__flush_data()

    def append_data(self, data):
        self.buffer.append(data)

        # only write data once the buffer is "full"
        if (len(self.buffer) > self.buffer_count):
            self.__flush_data()

    def __flush_data(self):
        with open(self.filepath, 'a', newline='') as outfile:
            writer = csv.DictWriter(outfile, delimiter=',', fieldnames=self.header)
            for row in self.buffer:
                writer.writerow(row)
            self.buffer.clear()

