#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from time import strptime

def add_zero(to_string):
    """Adds a zero to the beginning of string """
    return "0" + str(to_string)

def date_is_valid(dates):
    """Checks if dates (e.g. ["17", "11"] ) is valid and returns bool

    Checks if the first element is between 1 and 31
    and the second element is between 1 and 12.


    Keyword arguments:
    dates -- list of numbers

    Returns:
    True if the date is valid, False otherwise.
    """
    if (int(dates[0]) < 1 or
            int(dates[0]) > 31 or
            int(dates[1]) < 1 or
            int(dates[1]) > 12):

        return False
    return True

def get_simple_date(datestring):
    """Transforms a datestring into shorter date 7.9.2017 > 07.09

    Expects the datestring to be format 07.09.2017. If this is not the
    case, returns string "Failed".

    Keyword arguments:
    datestring -- a string

    Returns:
    String -- The date in format "dd.MM." or "Failed"
    """
    simple_date = re.compile(r"\d{1,2}(\.)\d{1,2}")
    date = simple_date.search(datestring)
    if date:
        dates = date.group().split(".")
        if len(dates[0]) == 1:
            dates[0] = add_zero(dates[0])
        if len(dates[1]) == 1:
            dates[1] = add_zero(dates[1])

        if date_is_valid(dates):
            return '.'.join(dates) + '.'
        return "Failed"


def get_month(datestring):
    """Transforms a written month into corresponding month number.

    E.g. November -> 11, or May -> 05.

    Keyword arguments:
    datestring -- a string

    Returns:
    String, or None if the transformation fails
    """
    convert_written = re.compile(r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", re.IGNORECASE)
    month = convert_written.search(datestring)
    month_number = None

    # If there's a match, convert the month to its corresponding number
    if month:
        month_number = strptime(month.group(), "%b").tm_mon
        if month_number < 10:
            month_number = add_zero(month_number)

    return str(month_number)

def get_day_of_month(datestring):
    """Transforms an ordinal number into plain number with padding zero.

    E.g. 3rd -> 03, or 12th -> 12

    Keyword arguments:
    datestring -- a string

    Returns:
    String, or None if the transformation fails
    """
    get_day = re.compile(r"\d{1,2}(st|nd|rd|th)?", re.IGNORECASE)
    day = get_day.search(datestring)
    the_day = None

    if day:
        if bool(re.search(r"[st|nd|rd|th]", day.group().lower())):
            the_day = day.group()[:-2]
        else:
            the_day = day.group()
        if int(the_day) < 10:
            the_day = add_zero(the_day)

    return str(the_day)


class Parser:

    def __init__(self):
        pass

    def strip_string(self, string, *args):
        """Strips matching regular expressions from string

        Keyword arguments:
        string -- The given string, that will be stripped
        *args -- List of regex strings, that are used in parsing

        Returns:
        String with *args removed from string
        """
        res = string
        for r in args:
            res = re.sub(r, "", res.strip(),
                         flags=re.IGNORECASE|re.MULTILINE)
        return res.strip()

    def strip_between(self, string, start, end):
        """Deletes everything between regexes start and end from string"""
        regex = start + r'.*?' + end + r'\s*'
        res = re.sub(regex, '', string,
                     flags=re.DOTALL|re.IGNORECASE|re.MULTILINE)
        return res

    def distance_between(self, string, start, end):
        """Returns number of lines between start and end"""
        count = 0
        started = False

        for line in string.split("\n"):

            if self.scan_line(line, start) and not started:
                started = True

            if self.scan_line(line, end):
                return count

            if started:
                count += 1

        return count

    def scan_line(self, line, regex):
        """Checks if regex is in line, returns bool"""
        return bool(re.search(regex, line, flags=re.IGNORECASE))

    def scan_message(self, message, regex):
        """Scans regex from msg and returns the line that matches

        Keyword arguments:
        message -- A (long) string, e.g. email body that will be
        scanned.

        regex -- A regular expression string that the message will be
        scanned against.

        Returns:
        Matching line or empty string
        """
        for line in message.split("\n"):
            if bool(re.search(
                    regex,
                    line,
                    flags=re.IGNORECASE|re.MULTILINE)):
                return line
        return ""

    def create_line(self, msg_number, *args):
        """Creates a TL;DR line in format: "1: Subject - DL: 12.11." """
        return str(msg_number) + ": " + " - ".join(args) + "\n"

    def format_date(self, dl_string):
        """Formats various date formats to dd.MM.

        Examples
        - January 15th      --> 15.01.
        - 15.01.2017        --> 15.01.
        - 15th of January   --> 15.01.
        - 15.1.             --> 15.01.

        Keyword arguments:
        dl_string -- a string to be formatted

        Returns:
        Date string in format dd.MM. or "None.None"
        """
        thedate = get_simple_date(dl_string)
        if thedate != "Failed" and thedate:
            return thedate

        day = get_day_of_month(dl_string)
        month = get_month(dl_string)

        return day + '.' + month + '.'
