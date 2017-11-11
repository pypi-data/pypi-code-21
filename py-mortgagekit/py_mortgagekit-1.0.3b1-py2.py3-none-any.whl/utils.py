# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
import math
from dateutil.relativedelta import relativedelta
from moneyed import Money, USD
from moneyed.localization import format_money
from mortgagekit.constants import *


__author__ = "Bartlomiej Mika"
__copyright__ = "Copyright (c) 2017, Mika Software Corporation"
__credits__ = ["Bartlomiej Mika", "David Stubbs"]
__license__ = "BSD 2-Clause License"
__version__ = "1.0.3b1"
__maintainer__ = "Mika Software Corporation"
__email = "bart@mikasoftware.com"
__status__ = "Production"


def get_mortgage_payment_per_frequency_to_per_month(mortgage_payment, frequency):
    assert isinstance(mortgage_payment, Money), 'mortgage_payment is not a Money class: %r' % mortgage_payment
    assert isinstance(frequency, Decimal), 'frequency is not a Decimal class: %r' % frequency

    if frequency == MORTGAGEKIT_ANNUAL:  # Annual
        return mortgage_payment / Decimal(MORTGAGEKIT_MONTH)

    elif frequency == MORTGAGEKIT_SEMI_ANNUAL:  # Semi-annual
        return mortgage_payment / Decimal(MORTGAGEKIT_BI_MONTH)

    elif frequency == MORTGAGEKIT_QUARTER:  # Quarterly
        return mortgage_payment / Decimal(MORTGAGEKIT_QUARTER)

    elif frequency == MORTGAGEKIT_BI_MONTH:
        return mortgage_payment / Decimal(MORTGAGEKIT_SEMI_ANNUAL)

    elif frequency == MORTGAGEKIT_MONTH:
        return mortgage_payment

    elif frequency == MORTGAGEKIT_BI_WEEK:
        return mortgage_payment * Decimal(MORTGAGEKIT_BI_WEEK) / Decimal(MORTGAGEKIT_MONTH)

    elif frequency == MORTGAGEKIT_WEEK:
        return mortgage_payment * Decimal(MORTGAGEKIT_WEEK) / Decimal(MORTGAGEKIT_MONTH)

    else:
        raise Exception("ERROR: Unsupported payment frequency type!")


def get_mortgage_payment_per_frequency_to_per_annual(mortgage_payment, frequency):
    """
    Function will return the amount paid per payment standardized to
    a per annual bases based on the "mortgage_payment" and "frequency"
    parameters. In essence this function will take the mortgage payment at
    the specific frequency to be per annual.
    """
    assert isinstance(mortgage_payment, Money), 'mortgage_payment is not a Money class: %r' % mortgage_payment
    assert isinstance(frequency, Decimal), 'frequency is not a Decimal class: %r' % frequency

    # mortgage_payment - amount paid per payment based on the frequency.

    if frequency == MORTGAGEKIT_ANNUAL:
        return mortgage_payment

    elif frequency == MORTGAGEKIT_SEMI_ANNUAL:
        return mortgage_payment * Decimal(MORTGAGEKIT_SEMI_ANNUAL)

    elif frequency == MORTGAGEKIT_QUARTER:
        return mortgage_payment * Decimal(MORTGAGEKIT_QUARTER)

    elif frequency == MORTGAGEKIT_BI_MONTH:
        return mortgage_payment * Decimal(MORTGAGEKIT_BI_MONTH)

    elif frequency == MORTGAGEKIT_MONTH:
        return mortgage_payment * Decimal(MORTGAGEKIT_MONTH)

    elif frequency == MORTGAGEKIT_BI_WEEK:
        return mortgage_payment * Decimal(MORTGAGEKIT_BI_WEEK)

    elif frequency == MORTGAGEKIT_WEEK:
        return mortgage_payment * Decimal(MORTGAGEKIT_WEEK)

    else:
        raise Exception("ERROR: Unsupported payment frequency type!")


def get_next_date_by_frequency(current_payment_date, frequency):
    # Calculate the current payment date according to the year/ month/ etc
    # that the computation is currently on.
    if frequency is MORTGAGEKIT_ANNUAL:
        current_payment_date += relativedelta(years=1)
    elif frequency is MORTGAGEKIT_SEMI_ANNUAL:
        current_payment_date += relativedelta(months=6)
    elif frequency is MORTGAGEKIT_QUARTER:
        current_payment_date += relativedelta(months=4)
    elif frequency is MORTGAGEKIT_BI_MONTH:
        current_payment_date += relativedelta(months=2)
    elif frequency is MORTGAGEKIT_MONTH:
        current_payment_date += relativedelta(months=1)
    elif frequency is MORTGAGEKIT_BI_WEEK:
        current_payment_date += relativedelta(weeks=2)
    elif frequency is MORTGAGEKIT_WEEK:
        current_payment_date += relativedelta(weeks=1)
    else:
        raise Exception("ERROR: Unsupported payment frequency type!")
    return current_payment_date
