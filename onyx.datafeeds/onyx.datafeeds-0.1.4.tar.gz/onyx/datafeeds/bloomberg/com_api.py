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
"""
Library of functions and classes for using the bloomberg COM API v3. Derived
from the code written by Brian P. Smith (brian.p.smith@gmail.com).
"""
from onyx.core import Date, RDate, Curve, GCurve, HlocvCurve
from ..exceptions import DatafeedError, DatafeedFatal
from ..exceptions import SecurityError, FieldError

from . import com_helpers as bbgcom

import win32com.client
import pythoncom
import collections
import datetime
import sys

__all__ = ["BloombergApiInit", "BbgBDP", "BbgBDH"]

sec_err_fmt = "({0.security:s}, {0.category:s}, {0.message:s})"
fld_err_fmt = "({0.security:s}, {0.field:s}, {0.category:s}, {0.message:s}"


# -------------------------------------------------------------------------
def BloombergApiInit():
    pythoncom.CoInitialize()


###############################################################################
class ResponseHandler(object):
    # -------------------------------------------------------------------------
    def do_init(self, handler):
        """
        will be called prior to waiting for the message
        """
        self.waiting = True
        self.exc_info = None
        self.handler = handler

    # -------------------------------------------------------------------------
    def OnProcessEvent(self, evt):
        try:
            evt = win32com.client.CastTo(evt, "Event")
            if not self.handler:
                bbgcom.debug_event(evt)

            if evt.EventType == win32com.client.constants.RESPONSE:
                self.handler.on_event(evt, is_final=True)
                self.waiting = False
            elif evt.EventType == win32com.client.constants.PARTIAL_RESPONSE:
                self.handler.on_event(evt, is_final=False)
            else:
                self.handler.on_admin_event(evt)
        except:
            self.waiting = False
            self.exc_info = sys.exc_info()

    # -------------------------------------------------------------------------
    @property
    def has_deferred_exception(self):
        return self.exc_info is not None

    # -------------------------------------------------------------------------
    def raise_deferred_exception(self):
        raise self.exc_info[0].with_traceback(self.exc_info[1],
                                              self.exc_info[2])

    # -------------------------------------------------------------------------
    def do_cleanup(self):
        self.waiting = False
        self.exc_info = None
        self.handler = None


###############################################################################
class Request(object):
    # -------------------------------------------------------------------------
    def __init__(self, ignore_sec_err=False, ignore_fld_err=False):
        self.fld_errs = []
        self.sec_errs = []
        self.ignore_sec_err = ignore_sec_err
        self.ignore_fld_err = ignore_fld_err

    # -------------------------------------------------------------------------
    @property
    def has_exception(self):
        if not self.ignore_sec_err and len(self.sec_errs) > 0:
            return True
        if not self.ignore_fld_err and len(self.fld_errs) > 0:
            return True

    # -------------------------------------------------------------------------
    def raise_exception(self):
        if not self.ignore_sec_err and len(self.sec_errs) > 0:
            msgs = [sec_err_fmt.format(s) for s in self.sec_errs]
            raise SecurityError("{0:s}".format(",".join(msgs)))

        if not self.ignore_fld_err and len(self.fld_errs) > 0:
            msgs = [fld_err_fmt.format(s) for s in self.fld_errs]
            raise FieldError("{0:s}".format(",".join(msgs)))

        raise DatafeedError("Programmer Error: No exception to raise")

    # -------------------------------------------------------------------------
    def get_bbg_request(self, svc, session):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    def get_bbg_service_name(self):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    def on_event(self, evt, is_final):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    def on_admin_event(self, evt):
        pass

    # -------------------------------------------------------------------------
    def execute(self):
        session_name = "blpapicom.ProviderSession.1"
        session = win32com.client.DispatchWithEvents(session_name,
                                                     ResponseHandler)
        session.Start()
        try:
            svcname = self.get_bbg_service_name()
            if not session.OpenService(svcname):
                raise DatafeedFatal("failed to "
                                    "open service {0:s}".format(svcname))

            svc = session.GetService(svcname)
            asbbg = self.get_bbg_request(svc, session)
            session.SendRequest(asbbg)
            session.do_init(self)
            while session.waiting:
                pythoncom.PumpWaitingMessages()
            if session.has_deferred_exception:
                session.raise_deferred_exception()
            if self.has_exception:
                self.raise_exception()

        finally:
            session.Stop()
            session.do_cleanup()

        return self


###############################################################################
class ReferenceDataRequest(Request):
    # -------------------------------------------------------------------------
    def __init__(self, symbols, fields, overrides=None,
                 ignore_sec_err=False, ignore_fld_err=False):

        super().__init__(ignore_sec_err, ignore_fld_err)

        self.syms = [symbols] if isinstance(symbols, str) else symbols
        self.flds = [fields] if isinstance(fields, str) else fields
        self.overrides = overrides or {}

        # --- look for any date-override and convert it to its correct string
        #     representation
        for k, v in self.overrides.items():
            if isinstance(v, datetime.datetime):
                self.overrides[k] = v.strftime("%Y%m%d")

        # --- response related
        self.response = {}

    # -------------------------------------------------------------------------
    def get_bbg_service_name(self):
        return "//blp/refdata"

    # -------------------------------------------------------------------------
    def get_bbg_request(self, svc, session):
        # --- create the bloomberg request object
        req = svc.CreateRequest("ReferenceDataRequest")
        for sec in self.syms:
            req.GetElement("securities").AppendValue(sec)
        for fld in self.flds:
            req.GetElement("fields").AppendValue(fld)
        for field, value in self.overrides.items():
            ovd = req.GetElement("overrides").AppendElment()
            ovd.SetElement("fieldId", field)
            ovd.SetElement("value", value)
        return req

    # -------------------------------------------------------------------------
    def on_security_node(self, node):
        sid = bbgcom.get_child_value(node, "security")
        farr = node.GetElement("fieldData")
        fdata = bbgcom.get_child_values(farr, self.flds)
        if len(fdata) != len(self.flds):
            raise ValueError("field length must match data length")

        self.response[sid] = dict(zip(self.flds, fdata))

        ferrors = bbgcom.get_field_errors(node)
        if ferrors:
            self.fld_errs.extend(ferrors)

    # -------------------------------------------------------------------------
    def on_event(self, evt, is_final):
        """
        this is invoked from in response to
        COM PumpWaitingMessages - different thread
        """
        for msg in bbgcom.message_iter(evt):
            elm = msg.GetElement("securityData")
            for node, error in bbgcom.security_iter(elm):
                if error:
                    self.sec_errs.append(error)
                else:
                    self.on_security_node(node)


###############################################################################
class HistoricalDataRequest(Request):
    # -------------------------------------------------------------------------
    def __init__(self, symbols, fields,
                 start=None, end=None, period="DAILY", overrides=None,
                 ignore_sec_err=False, ignore_fld_err=False, **kwds):
        """Historical data request for bloomberg.

        Parameters
        ----------
        symbols : string or list
        fields : string or list
        start : start date (if None then use 1 year ago)
        end : end date (if None then use today)
        period : ("DAILY", "WEEKLY", "MONTHLY",
                  "QUARTERLY", "SEMI-ANNUAL", "YEARLY")
        overrides : dict
        ignore_fld_errs : bool
        ignore_sec_errs : bool
        """
        super().__init__(ignore_sec_err, ignore_fld_err)

        self.syms = [symbols] if isinstance(symbols, str) else symbols
        self.flds = [fields] if isinstance(fields, str) else fields
        self.start = start or Date.today() + RDate("-1y")
        self.end = end or Date.today()
        self.period = period
        self.overrides = overrides or {}
        self.kwds = kwds

        # --- look for any date-override and convert it to its correct string
        #     representation
        for k, v in self.overrides.items():
            if isinstance(v, datetime.datetime):
                self.overrides[k] = v.strftime("%Y%m%d")

        # --- response related
        self.response = {}

    # -------------------------------------------------------------------------
    def get_bbg_service_name(self):
        return "//blp/refdata"

    # -------------------------------------------------------------------------
    def get_bbg_request(self, svc, session):
        # --- create the bloomberg request object
        req = svc.CreateRequest("HistoricalDataRequest")
        for sec in self.syms:
            req.GetElement("securities").AppendValue(sec)
        for fld in self.flds:
            req.GetElement("fields").AppendValue(fld)
        req.Set("startDate", self.start.strftime("%Y%m%d"))
        req.Set("endDate", self.end.strftime("%Y%m%d"))
        req.Set("periodicitySelection", self.period)
        for field, value in self.overrides.items():
            ovd = req.GetElement("overrides").AppendElment()
            ovd.SetElement("fieldId", field)
            ovd.SetElement("value", value)
        for k, v in self.kwds.items():
            req.Set(k, v)
        return req

    # -------------------------------------------------------------------------
    def on_security_data_node(self, node):
        """
        process a securityData node - FIXME: currently not handling
        relateDate node
        """
        sid = bbgcom.get_child_value(node, "security")
        farr = node.GetElement("fieldData")

        dates, data = [], []
        for i in range(farr.NumValues):
            pt = farr.GetValue(i)
            dates.append(bbgcom.get_child_value(pt, "date"))
            values = [bbgcom.get_child_value(pt, f) for f in self.flds]
            data.append(dict(zip(self.flds, values)))

        self.response[sid] = GCurve(dates, data)

    # -------------------------------------------------------------------------
    def on_event(self, evt, is_final):
        """
        this is invoked from in response to
        COM PumpWaitingMessages - different thread
        """
        for msg in bbgcom.message_iter(evt):
            # Single security element in historical request
            node = msg.GetElement("securityData")
            if node.HasElement("securityError"):
                secid = bbgcom.get_child_value(node, "security")
                elm = node.GetElement("securityError")
                self.sec_errs.append(bbgcom.as_security_error(elm, secid))
            else:
                self.on_security_data_node(node)


###############################################################################
class IntrdayBarRequest(Request):
    # -------------------------------------------------------------------------
    def __init__(self, symbol, interval,
                 start=None, end=None, event="TRADE"):
        """Intraday bar request for bloomberg

        Parameters
        ----------
        symbols : string
        interval : number of minutes
        start : start date
        end : end date (if None then use today)
        event : (TRADE, BID, ASK, BEST_BID, BEST_ASK)
        """
        super().__init__()

        self.symbol = symbol
        self.interval = interval
        self.start = start or Date.today() + RDate("-30b")
        self.end = end or Date.today()
        self.event = event

        # --- response related
        self.response = collections.defaultdict(list)

    # -------------------------------------------------------------------------
    def get_bbg_service_name(self):
        return "//blp/refdata"

    # -------------------------------------------------------------------------
    def get_bbg_request(self, svc, session):
        # --- create the bloomberg request object
        start, end = self.start, self.end
        start = session.CreateDatetime(start.year, start.month,
                                       start.day, start.hour, start.minute)
        end = session.CreateDatetime(end.year, end.month,
                                     end.day, end.hour, end.minute)
        request = svc.CreateRequest("IntradayBarRequest")
        request.Set("security", self.symbol)
        request.Set("interval", self.interval)
        request.Set("eventType", self.event)
        request.Set("startDateTime", start)
        request.Set("endDateTime", end)
        return request

    # -------------------------------------------------------------------------
    def on_event(self, evt, is_final):
        """
        this is invoked from in response to
        COM PumpWaitingMessages - different thread
        """
        response = self.response

        for msg in bbgcom.message_iter(evt):
            bars = msg.GetElement("barData").GetElement("barTickData")
            for i in range(bars.NumValues):
                bar = bars.GetValue(i)
                ts = bar.GetElement(0).Value
                response["time"].append(Date(ts.year, ts.month,
                                             ts.day, ts.hour, ts.minute))
                response["value"].append({
                    "open": bar.GetElement(1).Value,
                    "high": bar.GetElement(2).Value,
                    "low": bar.GetElement(3).Value,
                    "close": bar.GetElement(4).Value,
                    "volume": bar.GetElement(5).Value,
                    "events": bar.GetElement(6).Value,
                })

        if is_final:
            self.response = GCurve(response["time"], response["value"])


# -----------------------------------------------------------------------------
def BbgBDP(securities, fields, overrides=None):
    """
    Description:
        Interface to a ReferenceDataRequest.
    Inputs:
        securities - one or more valid Bloomberg tickers
        fields     - one or more valid Bloomberg fields
        overrides  - an optional dictionary of overrides (or a tuple
                     of key, value tuples)
    Returns:
        A dictionary.
    """
    if overrides is not None and isinstance(overrides, tuple):
        overrides = dict(overrides)
    req = ReferenceDataRequest(securities, fields, overrides)
    req.execute()
    return req.response


# -----------------------------------------------------------------------------
def BbgBDH(security, fields, start, end, adj=True, overrides=None, **kwds):
    """
    Description:
        Interface to HistoricalDataRequest.
    Inputs:
        secirity  - a valid Bloomberg ticker
        fields    - one or more valid Bloomberg fields. "HLOCV" is a special
                    field type.
        start     - start date
        end       - end date
        adj       - True for dividend/split adjusted data
        overrides - an optional dictionary of overrides (or a tuple
                    of key, value tuples)
    Returns:
        A Curve.
    """
    if fields == "HLOCV":
        fields = ("PX_HIGH", "PX_LOW", "PX_OPEN", "PX_LAST", "VOLUME")
        is_hlocv = True
    else:
        is_hlocv = False
        fields = [fields] if isinstance(fields, str) else fields

    if overrides is not None and isinstance(overrides, tuple):
        overrides = dict(overrides)

    req = HistoricalDataRequest(security, fields, start, end,
                                overrides=overrides,
                                adjustmentNormal=adj,
                                adjustmentAbnormal=adj,
                                adjustmentSplit=adj, **kwds)
    req.execute()
    crv = req.response[security]

    if is_hlocv:
        if len(crv):
            # --- remove knots without a close value (should be extremely rare)
            knots = [(d, [v[fld] for fld in fields])
                     for d, v in crv if v["PX_LAST"] is not None]
            return HlocvCurve([d for d, v in knots], [v for d, v in knots])

        else:
            return HlocvCurve()

    elif len(fields) == 1:
        if len(crv):
            fld = fields[0]
            try:
                float(crv.front.value[fld])
            except ValueError:
                return crv
            else:
                return Curve(crv.dates, [val[fld] for val in crv.values])
        else:
            return Curve()
    else:
        return crv
