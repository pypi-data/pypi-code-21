from keen import KeenClient
from keen_csv.container import KeenCSV

class KeenCSVClient(KeenClient):
    wrapped_methods = [ 'count',
                        'count_unique',
                        'minimum',
                        'maximum',
                        'sum',
                        'average',
                        'median',
                        'percentile',
                        'select_unique',
                        'multi_analysis'
                        'extraction'
                      ]

    def __getattribute__(self, attr):
        """Wraps the above wrapped_methods in _wrap"""
        attribute = super(KeenCSVClient, self).__getattribute__(attr)
        if attr in KeenClient.__getattribute__(self, 'wrapped_methods'):
            return(self._wrap(attribute))
        else:
            return(attribute)

    def _wrap(self, attribute):
        """Wraps an instance method and converts its response to CSV"""
        def _wrapper(*args, **kwargs):
            options = kwargs.pop("csv", {})
            raw_response = attribute(*args, **kwargs)
            keen_csv_response = KeenCSV(raw_response, **options)
            return keen_csv_response.generate_csv()
        return _wrapper
