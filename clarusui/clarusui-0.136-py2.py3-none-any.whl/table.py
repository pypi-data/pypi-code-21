from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from csv import DictReader
from io import StringIO
from clarusui.layout import Element
from numbers import Number
from clarus.models import ApiResponse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    #loader=FileSystemLoader('/templates/'),
    autoescape=select_autoescape(['html', 'xml'])
)

tableTemplate = env.get_template('table.html')
divTemplate = env.get_template('div.html')

class Table(Element):
    def __init__(self, response, **options):
        super(self.__class__, self).__init__(response,**options)
        
        if response is None:
            raise ValueError("Table should be initialised with CSV data or ApiResponse")
        if isinstance(response, ApiResponse):
            csvData = response.text
        else:
            csvData = response
        self.dicts = DictReader(StringIO(csvData))
        #number_formats = 
        self.columnDisplayFormats = options.pop('columnDisplayFormats', None)
        colFilter = options.pop('colFilter', None)
        if colFilter is not None:
            if not isinstance(colFilter, list):
                colFilter = [colFilter]
            
            for filterCol in colFilter:
                if filterCol not in self.dicts.fieldnames:
                    raise ValueError(filterCol +" column not found in results")
            if colFilter[0] != self.dicts.fieldnames[0]:
                colFilter.insert(0, self.dicts.fieldnames[0])
            self._set_headers(colFilter)
        else:
            self._set_headers(self.dicts.fieldnames)
        
        self._set_rows(list(self.dicts))
        
        self.set_header_css_class(options.pop('headerCssClass', None))
        
    def set_header_css_class(self, headerCssClass):        
        if (headerCssClass is not None):
            for header in self.headers:
                header.set_css_class(headerCssClass)
                #bug in bootstrap package, header text stays dark even on dark backgroung
                #header.add_custom_css({"color":"white"}) #fixed in beta
                
    def get_column_display_format(self, columnName):
        defaultDisplayFormat = '{:,.0f}'
        displayFormat = None
        if self.columnDisplayFormats is not None:
            displayFormat = self.columnDisplayFormats.get(columnName)
        
        if displayFormat is not None:
            return displayFormat
        else:
            return defaultDisplayFormat
               
    def _set_headers(self, headers):
        self.headers = []
       
        for header in headers:
            headerCell = Cell(header)
            self.headers.append(headerCell)
    
    def _set_rows(self, rows):
        self.rows = []
        count = 0
        for row in rows:
            r = []
            for header in self.headers:
                cell = Cell(row.get(header.cellvalue), numberFormat=self.get_column_display_format(header.cellvalue))
                r.append(cell)
                #align header using first row
                if count == 0:
                    if cell._is_numeric():
                        header.add_custom_css({'text-align':'right'})
            count += 1
            self.rows.append(r)
    
    
    def get_cell(self, row, column):
        return self.rows[row][column]
    
    def _render(self):
        return tableTemplate.render(table=self)
    
    def toDiv(self):
        return divTemplate.render(element=self)
    
        
class Cell(Element):
    def __init__(self, cellvalue, **options):
        super(self.__class__, self).__init__(None,**options)
        self.numberFormat = options.pop('numberFormat', '{:,.0f}')
        self.cellvalue = cellvalue
        self.iconName = None
        self.iconAlignment = 'left'
        if self._is_numeric():
            self.add_custom_css({'text-align':'right'})
    
    def _is_numeric(self):
        if isinstance(self.cellvalue, Number) or self.cellvalue.isdigit():
            return True
        else:
            return False
    
    def set_number_format(self, numberFormat):
        self.numberFormat = numberFormat;
    
    def set_icon(self, iconName, iconAlignment='left'):
        self.iconName = iconName
        self.iconAlignment = iconAlignment
    
    def _iconify_cell(self, cellValue):
        if self.iconName is None:
            return cellValue
        iconCode = '<i class="'+self.iconName+'" aria-hidden="true"></i>'
        if self.iconAlignment == 'left':
            cellValue = iconCode + ' ' +cellValue
        else: 
            cellValue = cellValue + ' ' +iconCode
        return cellValue
            
    
    def get_cell_value(self):
        cv = ''
        if self._is_numeric():
            cv = self.numberFormat.format(round(float(self.cellvalue)))
        else:
            cv = self.cellvalue
        
        return self._iconify_cell(cv)
            
    def toDiv(self):
        raise NotImplementedError("Table cell not suitable for standalone usage")
