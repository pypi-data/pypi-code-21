###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import Date, DateOffset
from ..bloomberg.com_api import IntrdayBarRequest
from ..bloomberg.com_api import ReferenceDataRequest, HistoricalDataRequest

d = DateOffset(Date.today(), "-4b")
m = DateOffset(Date.today(), "-1m+0J+0b")


def banner(msg):
    print('*' * 25)
    print(msg)
    print('*' * 25)

banner('ReferenceDataRequest: single security, single field')
req = ReferenceDataRequest('msft us equity', 'px_last')
print(req.execute().response)

banner('ReferenceDataRequest: multi-security, multi-field')
req = ReferenceDataRequest(['eurusd curncy', 'msft us equity'],
                           ['px_open', 'px_last'])
print(req.execute().response)

banner('ReferenceDataRequest: single security, '
       'multi-field (with bulk), frame response')
req = ReferenceDataRequest('eurusd curncy', ['px_last', 'fwd_curve'])
req.execute()
print(req.response)

banner('ReferenceDataRequest: multi security, multi-field, bad field')
req = ReferenceDataRequest(['eurusd curncy', 'msft us equity'],
                           ['px_last', 'fwd_curve'], ignore_fld_err=True)
req.execute()
print(req.response)

banner('HistoricalDataRequest: multi security, multi-field, daily data')
req = HistoricalDataRequest(['eurusd curncy', 'msft us equity'],
                            ['px_last', 'px_open'], start=d)
req.execute()
print(req.response)

banner('HistoricalDataRequest: multi security, multi-field, weekly data')
req = HistoricalDataRequest(['eurusd curncy', 'msft us equity'],
                            ['px_last', 'px_open'], start=m, period='WEEKLY')
req.execute()
print(req.response)

banner('IntrdayBarRequest: every hour')
req = IntrdayBarRequest('eurusd curncy', 60, start=d)
req.execute()
print(req.response)

#
# HOW TO
#
# - Retrieve an fx vol surface:
#       BbgReferenceDataRequest('eurusd curncy', 'DFLT_VOL_SURF_MID')
# - Retrieve a fx forward curve:
#       BbgReferenceDataRequest('eurusd curncy', 'FWD_CURVE')
# - Retrieve dividends:
#       BbgReferenceDataRequest('csco us equity',
#                               'BDVD_PR_EX_DTS_DVD_AMTS_W_ANN')
