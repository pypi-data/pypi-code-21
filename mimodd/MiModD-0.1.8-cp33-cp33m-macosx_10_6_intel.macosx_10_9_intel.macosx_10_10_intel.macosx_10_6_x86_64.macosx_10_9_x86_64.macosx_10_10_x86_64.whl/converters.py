class Record_Converter (object):
    """Base class for format converters.

    A format converter converts a record into some string representation.
    It also knows how to format optional header and footer objects so that,
    together, with the record representation they form valid output in a
    converter-dependent format.
    """
    
    def __init__ (self, header=None, footer=None):
        self.header = header
        self.footer = footer

    def format_header (self):
        if self.header is None:
            return ''
        else:
            return str(self.header)

    def format_footer (self):
        if self.footer is None:
            return ''
        else:
            return str(self.footer)

    def convert (self, record):
        return str(record)
