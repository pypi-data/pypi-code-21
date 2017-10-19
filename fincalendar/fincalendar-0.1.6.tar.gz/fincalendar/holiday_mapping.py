"""  This file shouldn't be necessary, but there is currently no good mapping from country code to calendar """
"""  Remove this once workalendar supports country code to calendar mappings """
from workalendar.africa import Algeria
from workalendar.africa import Benin
from workalendar.africa import IvoryCoast
from workalendar.africa import SaoTomeAndPrincipe
from workalendar.africa import SouthAfrica
from workalendar.america import Brazil
from workalendar.america import Chile
from workalendar.america import Colombia
from workalendar.america import Mexico
from workalendar.america import Panama
from workalendar.asia import HongKong
from workalendar.asia import Japan
from workalendar.asia import Malaysia
from workalendar.asia import Qatar
from workalendar.asia import Singapore
from workalendar.asia import SouthKorea
from workalendar.asia import Taiwan
from workalendar.oceania import Australia
from workalendar.canada import Canada
from workalendar.europe import Austria
from workalendar.europe import Belgium
from workalendar.europe import Bulgaria
from workalendar.europe import Croatia
from workalendar.europe import Cyprus
from workalendar.europe import CzechRepublic
from workalendar.europe import Denmark
from workalendar.europe import Estonia
from workalendar.europe import EuropeanCentralBank
from workalendar.europe import Finland
from workalendar.europe import France
from workalendar.europe import Germany
from workalendar.europe import Greece
from workalendar.europe import Hungary
from workalendar.europe import Iceland
from workalendar.europe import Ireland
from workalendar.europe import Italy
from workalendar.europe import Latvia
from workalendar.europe import Luxembourg
from workalendar.europe import Malta
from workalendar.europe import Netherlands
from workalendar.europe import Norway
from workalendar.europe import Poland
from workalendar.europe import Portugal
from workalendar.europe import Romania
from workalendar.europe import Slovakia
from workalendar.europe import Slovenia
from workalendar.europe import Spain
from workalendar.europe import Sweden
from workalendar.europe import Switzerland
from workalendar.europe import UnitedKingdom
from workalendar.usa import UnitedStates
from workalendar.core import WesternCalendar  # This becomes a (poor) default

MAPPING = {'AUS': Australia,
           'AUT': Austria,
           'BEL': Belgium,
           'BEN': Benin,
           'BGR': Bulgaria,
           'BRA': Brazil,
           'CAN': Canada,
           'CHE': Switzerland,
           'CHL': Chile,
           'CIV': IvoryCoast,
           'COL': Colombia,
           'CYP': Cyprus,
           'CZE': CzechRepublic,
           'DEU': Germany,
           'DNK': Denmark,
           'DZA': Algeria,
           'ESP': Spain,
           'EST': Estonia,
           'EUR': EuropeanCentralBank,
           'FIN': Finland,
           'FRA': France,
           'GBR': UnitedKingdom,
           'GRC': Greece,
           'HRV': Croatia,
           'HUN': Hungary,
           'IRL': Ireland,
           'ISL': Iceland,
           'ITA': Italy,
           'JPN': Japan,
           'KOR': SouthKorea,
           'LUX': Luxembourg,
           'LVA': Latvia,
           'MEX': Mexico,
           'MLT': Malta,
           'MYS': Malaysia,
           'NLD': Netherlands,
           'NOR': Norway,
           'PAN': Panama,
           'POL': Poland,
           'PRT': Portugal,
           'ROU': Romania,
           'QAT': Qatar,
           'STP': SaoTomeAndPrincipe,
           'SVK': Slovakia,
           'SVN': Slovenia,
           'SWE': Sweden,
           'TWN': Taiwan,
           'USA': UnitedStates,
           'SGP': Singapore,
           'ZAF': SouthAfrica}


def get_calendar(alpha_3_country_code):
    calendar = MAPPING.get(alpha_3_country_code, WesternCalendar)
    return calendar()
