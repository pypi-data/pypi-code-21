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

    #move to super, common with Charts
    @classmethod
    def from_apiresponse(cls, apiResponse, **options):
        return cls(apiResponse, **options)

    @classmethod
    def from_csv(cls, csvText, **options):
        return cls(csvText, **options)
       
    @classmethod
    def from_dataframe(cls, dataFrame, **options):
        csvText = dataFrame.to_csv(index=False)
        return cls.from_csv(csvText, **options)
        
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
    
    #will set a flag against any cell with country name match - allow per column/cell etc?
    def add_country_flags(self):
        for row in self.rows:
            for cell in row:
                cv = cell.get_cell_value()
                countryCode = get_country_code(cv)
                if countryCode is not None:
                    cell.set_icon('flag-icon flag-icon-'+countryCode.lower())
                    
        
    
        
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

#should really be somewhere else as a utility method
def get_country_code(countryName):
    dict = {"Aruba":"AW",
"Afghanistan":"AF",
"Angola":"AO",
"Anguilla":"AI",
"Albania":"AL",
"Andorra":"AD",
"United Arab Emirates":"AE",
"Argentina":"AR",
"Armenia":"AM",
"American Samoa":"AS",
"Antarctica":"AQ",
"French Southern Territories":"TF",
"Antigua and Barbuda":"AG",
"Australia":"AU",
"Austria":"AT",
"Azerbaijan":"AZ",
"Burundi":"BI",
"Belgium":"BE",
"Benin":"BJ",
"Bonaire, Sint Eustatius and Saba":"BQ",
"Burkina Faso":"BF",
"Bangladesh":"BD",
"Bulgaria":"BG",
"Bahrain":"BH",
"Bahamas":"BS",
"Bosnia and Herzegovina":"BA",
"Belarus":"BY",
"Belize":"BZ",
"Bermuda":"BM",
"Bolivia, Plurinational State of":"BO",
"Brazil":"BR",
"Barbados":"BB",
"Brunei Darussalam":"BN",
"Bhutan":"BT",
"Bouvet Island":"BV",
"Botswana":"BW",
"Central African Republic":"CF",
"Canada":"CA",
"Cocos (Keeling) Islands":"CC",
"Switzerland":"CH",
"Chile":"CL",
"China":"CN",
"Cameroon":"CM",
"Congo, The Democratic Republic of the":"CD",
"Congo":"CG",
"Cook Islands":"CK",
"Colombia":"CO",
"Comoros":"KM",
"Cabo Verde":"CV",
"Costa Rica":"CR",
"Cuba":"CU",
"Christmas Island":"CX",
"Cayman Islands":"KY",
"Cyprus":"CY",
"Czechia":"CZ",
"Germany":"DE",
"Djibouti":"DJ",
"Dominica":"DM",
"Denmark":"DK",
"Dominican Republic":"DO",
"Algeria":"DZ",
"Ecuador":"EC",
"Egypt":"EG",
"Eritrea":"ER",
"Western Sahara":"EH",
"Spain":"ES",
"Estonia":"EE",
"Ethiopia":"ET",
"Finland":"FI",
"Fiji":"FJ",
"Falkland Islands (Malvinas)":"FK",
"France":"FR",
"Faroe Islands":"FO",
"Micronesia, Federated States of":"FM",
"Gabon":"GA",
"United Kingdom":"GB",
"Georgia":"GE",
"Guernsey":"GG",
"Ghana":"GH",
"Gibraltar":"GI",
"Guinea":"GN",
"Guadeloupe":"GP",
"Gambia":"GM",
"Guinea-Bissau":"GW",
"Equatorial Guinea":"GQ",
"Greece":"GR",
"Grenada":"GD",
"Greenland":"GL",
"Guatemala":"GT",
"French Guiana":"GF",
"Guam":"GU",
"Guyana":"GY",
"Hong Kong":"HK",
"Heard Island and McDonald Islands":"HM",
"Honduras":"HN",
"Croatia":"HR",
"Haiti":"HT",
"Hungary":"HU",
"Indonesia":"ID",
"Isle of Man":"IM",
"India":"IN",
"British Indian Ocean Territory":"IO",
"Ireland":"IE",
"Iran, Islamic Republic of":"IR",
"Iraq":"IQ",
"Iceland":"IS",
"Israel":"IL",
"Italy":"IT",
"Jamaica":"JM",
"Jersey":"JE",
"Jordan":"JO",
"Japan":"JP",
"Kazakhstan":"KZ",
"Kenya":"KE",
"Kyrgyzstan":"KG",
"Cambodia":"KH",
"Kiribati":"KI",
"Saint Kitts and Nevis":"KN",
"Korea, Republic of":"KR",
"Kuwait":"KW",
"Lao People's Democratic Republic":"LA",
"Lebanon":"LB",
"Liberia":"LR",
"Libya":"LY",
"Saint Lucia":"LC",
"Liechtenstein":"LI",
"Sri Lanka":"LK",
"Lesotho":"LS",
"Lithuania":"LT",
"Luxembourg":"LU",
"Latvia":"LV",
"Macao":"MO",
"Saint Martin (French part)":"MF",
"Morocco":"MA",
"Monaco":"MC",
"Moldova, Republic of":"MD",
"Madagascar":"MG",
"Maldives":"MV",
"Mexico":"MX",
"Marshall Islands":"MH",
"Macedonia, Republic of":"MK",
"Mali":"ML",
"Malta":"MT",
"Myanmar":"MM",
"Montenegro":"ME",
"Mongolia":"MN",
"Northern Mariana Islands":"MP",
"Mozambique":"MZ",
"Mauritania":"MR",
"Montserrat":"MS",
"Martinique":"MQ",
"Mauritius":"MU",
"Malawi":"MW",
"Malaysia":"MY",
"Mayotte":"YT",
"Namibia":"NA",
"New Caledonia":"NC",
"Niger":"NE",
"Norfolk Island":"NF",
"Nigeria":"NG",
"Nicaragua":"NI",
"Niue":"NU",
"Netherlands":"NL",
"Norway":"NO",
"Nepal":"NP",
"Nauru":"NR",
"New Zealand":"NZ",
"Oman":"OM",
"Pakistan":"PK",
"Panama":"PA",
"Pitcairn":"PN",
"Peru":"PE",
"Philippines":"PH",
"Palau":"PW",
"Papua New Guinea":"PG",
"Poland":"PL",
"Puerto Rico":"PR",
"Korea, Democratic People's Republic of":"KP",
"Portugal":"PT",
"Paraguay":"PY",
"Palestine, State of":"PS",
"French Polynesia":"PF",
"Qatar":"QA",
"Romania":"RO",
"Russian Federation":"RU",
"Rwanda":"RW",
"Saudi Arabia":"SA",
"Sudan":"SD",
"Senegal":"SN",
"Singapore":"SG",
"South Georgia and the South Sandwich Islands":"GS",
"Saint Helena, Ascension and Tristan da Cunha":"SH",
"Svalbard and Jan Mayen":"SJ",
"Solomon Islands":"SB",
"Sierra Leone":"SL",
"El Salvador":"SV",
"San Marino":"SM",
"Somalia":"SO",
"Saint Pierre and Miquelon":"PM",
"Serbia":"RS",
"South Sudan":"SS",
"Sao Tome and Principe":"ST",
"Suriname":"SR",
"Slovakia":"SK",
"Slovenia":"SI",
"Sweden":"SE",
"Swaziland":"SZ",
"Sint Maarten (Dutch part)":"SX",
"Seychelles":"SC",
"Syrian Arab Republic":"SY",
"Turks and Caicos Islands":"TC",
"Chad":"TD",
"Togo":"TG",
"Thailand":"TH",
"Tajikistan":"TJ",
"Tokelau":"TK",
"Turkmenistan":"TM",
"Timor-Leste":"TL",
"Tonga":"TO",
"Trinidad and Tobago":"TT",
"Tunisia":"TN",
"Turkey":"TR",
"Tuvalu":"TV",
"Taiwan, Province of China":"TW",
"Tanzania, United Republic of":"TZ",
"Uganda":"UG",
"Ukraine":"UA",
"United States Minor Outlying Islands":"UM",
"Uruguay":"UY",
"United States":"US",
"Uzbekistan":"UZ",
"Holy See (Vatican City State)":"VA",
"Saint Vincent and the Grenadines":"VC",
"Venezuela, Bolivarian Republic of":"VE",
"Virgin Islands, British":"VG",
"Virgin Islands, U.S.":"VI",
"Viet Nam":"VN",
"Vanuatu":"VU",
"Wallis and Futuna":"WF",
"Samoa":"WS",
"Yemen":"YE",
"South Africa":"ZA",
"Zambia":"ZM",
"Zimbabwe":"ZW"}
    return dict.get(countryName)