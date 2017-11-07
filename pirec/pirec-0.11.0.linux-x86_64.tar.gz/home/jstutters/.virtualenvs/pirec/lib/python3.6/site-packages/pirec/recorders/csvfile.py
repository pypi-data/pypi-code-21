"""Exposes the CSVFile result recorder."""
import os
import csv


class CSVFile(object):
    """Records results to a CSV file.

    Args:
        path (str): The file to which results should be written
        values (dict): a mapping from table columns to values
    """

    def __init__(self, path, values):
        """Initialize the recorder."""
        self.path = path
        self.values = values

    def write(self, results):
        """Write results to the file specified.

        Args:
            results (dict): A dictionary of results to record

        Note:
            If the specified does not exist it will be created and a
            header will be written , otherwise the new result is appended.

        """
        field_names = self.values.keys()
        write_header = not os.path.exists(self.path)
        with open(self.path, 'a') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=field_names)
            if write_header:
                writer.writeheader()
            row = {}
            for field in self.values:
                row[field] = self.values[field](results)
            writer.writerow(row)
