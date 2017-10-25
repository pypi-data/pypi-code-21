'''
A Sinbad plug-in for CSV-based data sources (supports TSV also)
'''

import csv
import io

from sinbad.plugin_base import *
from sinbad import util

HEADER_OPT = "header"
SKIP_ROWS_OPT = "skip-rows"
DELIMITER_OPT = "delimiter"

class CSV_Infer(Base_Infer):
    
    def __init__(self, delim = None):
        super().__init__()
        if delim: self.options[DELIMITER_OPT] = delim
    
    def matched_by(self, path):
        path = path.lower()
        if path.endswith("csv"): return True
        for ptrn in [".csv", "=csv", "/csv"]:
            if ptrn in path: return True
        
        is_tsv = False
        if path.endswith("tsv"): is_tsv = True
        for ptrn in [".tsv", "=tsv", "/tsv"]:
            if ptrn in path: is_tsv = True
        if is_tsv:
            self.options[DELIMITER_OPT] = '\t'
            return True
        
        return False



class CSV_Data_Factory(Base_Data_Factory):
    
    def __init__(self):
        super().__init__()
        self.field_names = None
        self.delimiter = None
        self.skip_rows = 0
    
    
    def load_data(self, fp, encoding = None):
        byts = fp.read()
        if byts.startswith(b'\xef\xbb\xbf'): byts = byts[3:] # clear BOM header  
        
        if encoding: str_data = byts.decode(encoding, 'ignore')
        else: str_data = byts.decode(errors='ignore')
        
        has_double_newlines = str_data.find("\n\n") >= 0
        str_data = str_data.replace('\r', '\n')
        if not has_double_newlines and str_data.find("\n\n") >= 0:
            str_data = str_data.replace('\n\n', '\n')
            
        if self.skip_rows > 0:
            str_data = util.drop_lines(str_data, self.skip_rows)
                    
        sample = str_data[:10000]
        snuffy = csv.Sniffer()
        if not snuffy.has_header(sample) and not self.field_names:
            # see how many columns there are and provide auto-numbered names
            if self.delimiter: rdr = csv.reader(io.StringIO(str_data), delimiter=self.delimiter)
            else: rdr = csv.reader(io.StringIO(str_data))
            self.field_names = [ self.__fix_heading(i, '') for i in range(len(rdr.__next__())) ]
            
        if not self.delimiter: self.delimiter = snuffy.sniff(sample).delimiter
        
        sfp = io.StringIO(str_data)
        if self.delimiter:
            data = csv.DictReader(sfp, fieldnames = self.field_names, delimiter = self.delimiter, restkey='_extra_', restval='')

        if data.fieldnames:
            data.fieldnames = [ self.__fix_heading(i, n) for i, n in enumerate(data.fieldnames)]
        
        self.field_names = data.fieldnames
            
        stuff = [x for x in data]
        if isinstance(stuff, list) and len(stuff) == 1:
            return stuff[0]
        else:
            return stuff
        
        
    def get_options(self):
        return [ HEADER_OPT, DELIMITER_OPT, SKIP_ROWS_OPT ]
# TODO: quote option
    
    
    def get_option(self, name):
        if name == HEADER_OPT and self.field_names:
            return ",".join(self.field_names)
        elif name == DELIMITER_OPT and self.delimiter:
            return self.delimiter
        elif name == SKIP_ROWS_OPT:
            return self.skip_rows
        else:
            return None


    def set_option(self, name, value):
        if name == HEADER_OPT:   # value could be a list or a string of comma-separated column names
            if isinstance(value, str):
                values = value.split(",")
            elif isinstance(value, list):
                values = value
            else:
                raise ValueError("header value must be provided as a comma-separated string or a list of strings")
            self.field_names = [v.strip().strip("\"'").strip() for v in values]
        elif name == DELIMITER_OPT:
            self.delimiter = value
        elif name == SKIP_ROWS_OPT:
            self.skip_rows = int(value)
    
    
    def __fix_heading(self, i, s):
        '''Strip trailing whitespace, and then provide names for any unnamed columns.
        Also replace spaces with underscores.'''
        s = s.strip().replace(' ', '_')
        if s == '':
            s = '_col_{}'.format(i)
        if s[0].isdigit():      # normalize to identifier naming rules because jsonpath_rw is picky
            s = '_' + s
        return s
        
        


        
