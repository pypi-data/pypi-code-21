import pandas as pd
import os, sys
import numpy as np

class Trade:
    """
    This class contains the information
    about a trade
    """

    def __init__(self):
        """
        constructor for the class
        """
        self.direction = None
        self.shares = 0
        self.entry_date = None
        self.entry_px = None
        self.best_px = None
        self.current_px = None
        self.prev_px = None
        self.close_px = None
        self.close_date = None
        self.today_pl = 0
        self.total_pl = 0
        self.starting_value = 0
        self.entry_value = 0
        self.current_value = 0
        self.closed = False
        self.increase = 0
        self.transaction_cost = 0.0003

    def initiate_trade(self, value, px, direction, date):
        """
        initiliaze the trade with entry price and
        shrares, values
        """
        self.entry_date = date
        self.entry_px = px
        self.best_px = px
        self.prev_px = px
        self.direction = direction
        # apply transaction cost
        self.entry_value = value * (1 - self.transaction_cost)
        self.starting_value = value * (1 - self.transaction_cost)
        self.shares = value * (1 - self.transaction_cost) / px

    def calc_current_value(self, px):
        """
        calculate the current value of the trade
        """
        self.current_px = px
        if self.direction == 'long':
            self.best_px = max(self.current_px, self.best_px)
            self.today_pl = self.shares * (self.current_px - self.prev_px)
            self.total_pl = self.shares * (self.current_px - self.entry_px)
        else:
            self.best_px = min(self.current_px, self.best_px)
            self.today_pl = self.shares * (self.prev_px - self.current_px)
            self.total_pl = self.shares * (self.entry_px - self.current_px)
        self.prev_px = self.current_px
        self.current_value = self.entry_value + self.total_pl

    def close_position(self, date):
        """
        close the position
        """
        self.closed = True
        self.close_date = date
        self.close_px = self.current_px