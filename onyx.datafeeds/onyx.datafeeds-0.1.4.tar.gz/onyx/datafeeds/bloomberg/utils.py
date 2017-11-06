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

from onyx.core import GetVal
from ..exceptions import FieldError

__all__ = [
    "get_bbg_ticker",
    "get_bbg_composite",
    "ticker_active",
    "MissingBbgCode",
    "MissingBbgTicker"
]

INACTIVE = {"NONE", "INEG"}


###############################################################################
class MissingBbgCode(Exception):
    pass


###############################################################################
class MissingBbgTicker(Exception):
    pass


# -----------------------------------------------------------------------------
def get_bbg_ticker(sec):
    """
    Description:
        Return the Bloomberg ticker for a given security (if available).
    Inputs:
        sec - the security name
    Returns:
        A string.
    """
    obj_type = GetVal(sec, "ObjType")

    try:
        bbg_ticker = GetVal(sec, "Ticker", platform="Bloomberg")
    except KeyError:
        raise MissingBbgTicker("missing Bloomberg ticker "
                               "for {0:s} {0:s}".format(obj_type, sec))

    if obj_type in ("EquityAsset", "DepositaryReceipt"):
        exchange = GetVal(sec, "Exchange")

        try:
            bbg_exch_code = GetVal(exchange, "Code", platform="Bloomberg")
        except KeyError:
            raise MissingBbgCode("missing Bloomberg code "
                                 "for Exchange {0:s}".format(exchange))

        return "{0:s} {1:s} EQUITY".format(bbg_ticker, bbg_exch_code)

    elif obj_type in ("EquityIndex", "EquityIndexCnt"):
        return "{0:s} INDEX".format(bbg_ticker)

    elif obj_type in ("CommodAsset", "CommodCnt"):
        return "{0:s} COMDTY".format(bbg_ticker)

    elif obj_type in {"BbgSecurity", "CurrencyCross"}:
        return bbg_ticker

    else:
        raise NotImplementedError("function not implemented for "
                                  "{0:s}".format(GetVal(sec, "ObjType")))


# -----------------------------------------------------------------------------
def get_bbg_composite(bbg_ticker, bbg_clt):
    """
    Description:
        Return the Bloomberg composite ticker for a given ticker, if
        available
    Inputs:
        bbg_ticker - the Bloomberg ticker.
        bbg_clt    - an instance of the bloomberg datafeed client
    Returns:
        A string.
    """
    try:
        ticker = bbg_clt.BDP(bbg_ticker, "EU_COMPOSITE_TICKER")
    except FieldError:
        return bbg_ticker
    else:
        if ticker is None:
            return bbg_ticker
        else:
            return ticker


# -----------------------------------------------------------------------------
def ticker_active(bbg_ticker, bbg_clt):
    """
    Description:
        Check if a Bloomberg ticker is currently active (as opposed to
        inactive, expired, etc).
    Inputs:
        bbg_ticker - the Bloomberg ticker.
        bbg_clt    - an instance of the bloomberg datafeed client
    Returns:
        A tuple (active, status), where:
            active - a bool, True if the ticker is inactive
            status - a string, current market status

    The possible values for stats are:

        ABAL - auction order book balancing
        AUCT - auction call phase
        CAUC - continuous auction pre-call or call phase dependent on market
               makers or specialists
        CLOS - market closed
        HALT - temporary halt from trading
        HLTA - temporary halt and auction call phase
        INEG - ineligible to trade, e.g. pending listing, delisted, private
               company, expired, called, etc.
        MOC  - market-on-close order collection for eventual execution at the
               determined closing price
        MOCB - market-on-close order balancing to try and maximize execution at
               the determined closing price
        NONE - the current status of the security is undefined
        NOTR - not presently available for trading
        OUT  - trading in an out-of-hours trading phase
        POST - post-close session
        PREO - pre-open session
        PRPO - pre-open/post-close session
        NOTR - not presently available for trading
        OUT  - trading in an out-of-hours trading phase
        POST - post-close session
        PREO - pre-open session
        PRPO - pre-open/post-close session
        SUSP - presently suspended from trading
        TALC - trade-at-last or trade-at-close trading phase
        TMCB - actively trading, but with market-on-close order balancing
               operating in parallel
        TMOC - actively trading, but with market-on-close order collection
               operating in parallel
        TRAD - actively trading, e.g. continuous trading, mandatory quotation
               period, etc.
        TRAU - actively trading, with an auction call running in parallel
        UNCR - auction uncrossing phase

    If you are looking to track the status of a security in simplistic terms,
    then you make wish to make use of the following generalizations:

    - A security has an unknown status when it returns a value of NONE.
    - A security is ineligible to trade when it returns a value of INEG.
    - A security is closed for trading when it returns a value of CLOS (if
      QUOTE_STATUS/RT_QUOTE_STATUS is also equal to 'N').
    - A security is available and open for trading (e.g. continuous trading)
      when it returns a value of CAUC, TMCB, TMOC, TRAD or TRAU.
    - A security is available for trade-at-last or trade-at-close order
      executions only when it returns a value of TALC.
    - A security is available for out-of-hours trading when it returns a value
      of OUT.
    - A security is in an auction call when it returns a value of AUCT, HLTA
      or TRAU. If IN_AUCTION/IN_AUCTION_RT returns a value of 'NO' then the
      order executions (the uncrossing) has already taken place at the end of
      that auction call.
    - A security is executing orders from an auction call when it returns a
      value of UNCR (not supported on all markets).
    - A security is offering an opportunity to offset an outstanding imbalance
      from an auction call when it returns a value of ABAL.
    - A security is operating a distinct market-on-close (MOC) order book when
      it returns a value of TMOC or MOC.
    - A security is offering an opportunity to offset an outstanding imbalance
      on a market-on-close.
    - A security is operating a distinct market-on-close (MOC) order book when
      it returns a value of TMOC or MOC.
    - A security is offering an opportunity to offset an outstanding imbalance
      on a market-on-close (MOC) book when it returns a value of MOCB or TMCB.
    - A security is halted or suspended from trading when it returns a value
      of HALT, HLTA or SUSP. If the value is HLTA then the security is
      participating in an auction call to facilitate a resumption of trading.
    - A security is temporarily unavailable for trading - but not halted or
      suspended - when it returns a value of NOTR.
    - A security is in a pre-trading or post-trading phase (auction calls
      excepted), but with no trading via the primary market mechanism (e.g.
      continuous trading), when it returns a value of CLOS (if
      QUOTE_STATUS/RT_QUOTE_STATUS is also equal to 'Y'), POST, PREO or POST.

    Note that there is a distinction between what we understand to be most
    likely temporary halts (HALT and HLTA), and what we understand may be
    longer term suspensions (SUSP). All three values nevertheless represent an
    unscheduled interruption to trading.
    """
    ticker = bbg_ticker.upper()
    status = bbg_clt.BDP(ticker, "SIMP_SEC_STATUS")
    return status not in INACTIVE, status
