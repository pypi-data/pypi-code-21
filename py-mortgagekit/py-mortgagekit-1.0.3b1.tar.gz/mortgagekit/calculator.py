# -*- coding: utf-8 -*-
"""
API library for mortgage calculations.
See README for more details.
"""

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
from mortgagekit.utils import *


__author__ = "Bartlomiej Mika"
__copyright__ = "Copyright (c) 2017, Mika Software Corporation"
__credits__ = ["Bartlomiej Mika", "David Stubbs"]
__license__ = "BSD 2-Clause License"
__version__ = "1.0.3b1"
__maintainer__ = "Mika Software Corporation"
__email = "bart@mikasoftware.com"
__status__ = "Production"


class MortgageCalculator(object):
    """
    Class used to calculate mortgage payments schedule.
    """
    def __init__(self, total_amount, down_payment_amount, amortization_year,
                 annual_interest_rate, payment_frequency, compounding_period,
                 first_payment_date, currency='USD'):

        # Perform assertions to ensure input is standardized by programmers
        # who use this library.
        assert isinstance(total_amount, Money), 'total_amount is not a Money class: %r' % total_amount
        assert isinstance(down_payment_amount, Money), 'down_payment_amount is not a Money class: %r' % down_payment_amount
        assert isinstance(amortization_year, int), 'amortization_year is not a Integer class: %r' % amortization_year
        assert isinstance(annual_interest_rate, Decimal), 'annual_interest_rate is not a Decimal class: %r' % annual_interest_rate
        assert isinstance(payment_frequency, Decimal), 'payment_frequency is not a Decimal class: %r' % payment_frequency
        assert isinstance(compounding_period, Decimal), 'compounding_period is not a Money class: %r' % compounding_period

        # Convert the date input into python "Date" object.
        first_payment_date_obj = None
        if not isinstance(first_payment_date, datetime):
            if not isinstance(first_payment_date, str):
                raise("first_payment_date is not String nor Datetime object.")
            else:
                first_payment_date_obj = datetime.strptime(first_payment_date, "%Y-%m-%d").date()
        else:
            first_payment_date_obj = first_payment_date

        # Save to class member variables.
        self._currency = currency
        self._total_amount = total_amount
        self._down_payment_amount = down_payment_amount
        self._loan_amount = self._total_amount - self._down_payment_amount
        self._amortization_year = amortization_year
        self._annual_interest_rate = annual_interest_rate
        self._payment_frequency = payment_frequency
        self._compounding_period = compounding_period
        self._first_payment_date = first_payment_date_obj

    def get_payment_frequency(self):
        return self._payment_frequency

    def get_percent_of_loan_financed(self):
        loan_purchase_amount = self._total_amount
        down_payment = self._down_payment_amount

        if loan_purchase_amount is 0:  # Defensive Code: Prevent division by zero error.
            return Decimal(0)

        # Calculate our loan princinple.
        loan_amount = loan_purchase_amount - down_payment
        amount_financed_percent = loan_amount.amount / loan_purchase_amount.amount
        return Decimal(amount_financed_percent * 100)

    def get_interest_rate_per_payment_frequency(self):
        compounding_period = self._compounding_period
        annual_interest_rate = self._annual_interest_rate
        payment_frequency = self._payment_frequency

        y = compounding_period / payment_frequency
        x = annual_interest_rate / compounding_period
        x = x + 1

        #WARNING: Precision loss
        z = math.pow(x, y)
        z = z - 1.0;
        return z

    def get_total_number_of_payments_per_frequency(self):
        amort_year = self._amortization_year
        payment_frequency = self._payment_frequency
        total_payments = amort_year * payment_frequency
        return total_payments

    def get_mortgage_payment_per_payment_frequency(self):
        """
        Function will return the amount paid per payment based on the frequency.
        """
        # Calculate the interest rate per the payment parameters:
        r = self.get_interest_rate_per_payment_frequency()

        # Calculate the total number of payments given the parameters:
        n = self.get_total_number_of_payments_per_frequency()

        # Variables used as number holders.
        p = self._loan_amount
        mortgage = None
        top = None
        bottom = None

        top = r + 1
        top = math.pow(top, n)
        top = r * top

        bottom = r + 1
        bottom = math.pow(bottom, n)
        bottom = bottom - 1

        if bottom == 0:
            return Money(amount=0.00, currency=self._currency)

        mortgage = (top / bottom)
        mortgage = mortgage * p

        return mortgage

    def get_mortgage_payment_schedule(self):
        # Initialize the payment schedule which will include all necessary data.
        payment_schedule = []
        mortgage_payment = self.get_mortgage_payment_per_payment_frequency()
        interest_rate_per_payment = Decimal(self.get_interest_rate_per_payment_frequency())
        loan_balance = self._loan_amount
        total_paid_to_interest = Money(amount=0, currency=self._currency)
        total_paid_to_bank = Money(amount=0, currency=self._currency)
        current_payment_date = self._first_payment_date

        # Go through all the years of the loan.
        for amortization_year in range(1, self._amortization_year+1):

            # Go through all the payments in that year.
            for payment in range(1, int(self._payment_frequency)+1):

                # Calculate amount going to pay off interest.
                interest_amount = loan_balance * interest_rate_per_payment

                # Calculate amount going to pay off principle.
                principle_amount = mortgage_payment - interest_amount

                # Calculate the remaining loan balance.
                loan_balance = loan_balance - principle_amount
                total_paid_to_interest = interest_amount + total_paid_to_interest
                total_paid_to_bank = mortgage_payment + total_paid_to_bank

                # Calculate the next payment date according to the year/ month/ etc
                # that the computation is currently on.
                current_payment_date = get_next_date_by_frequency(current_payment_date, self._payment_frequency)

                # Save the computation we've generated.
                payment_schedule.append({
                    'year': amortization_year,
                    'interval': payment,
                    'payment': mortgage_payment,
                    'interest': interest_amount,
                    'principle': principle_amount,
                    'loan_balance': loan_balance,
                    'total_paid_to_interest': total_paid_to_interest,
                    'total_paid_to_bank': total_paid_to_bank,
                    'paymentData': current_payment_date
                })

        return payment_schedule

    def get_monthly_mortgage_payment(self):
        """
        Function will return the amount paid per payment standardized to
        a per monthly bases.
        """
        return get_mortgage_payment_per_frequency_to_per_month(
            mortgage_payment = self.get_mortgage_payment_per_payment_frequency(),
            frequency = self._payment_frequency
        )

    def get_annual_mortgage_payment(self):
        """
        Function will return the amount paid per payment standardized to
        a per annual bases.
        """
        return get_mortgage_payment_per_frequency_to_per_annual(
            mortgage_payment = self.get_mortgage_payment_per_payment_frequency(),
            frequency = self._payment_frequency
        )
