#! /usr/bin/env python
"""
Determine the dates for a day of the week for each month in the year.
For example, determine the dates for the first Tuesday of every month,
by running the command:

  > date_query 2017 1
"""

import calendar as cal
import argparse

calendar = cal.Calendar(0)  # 0=Mon


def get_dates(year, day_of_the_week):
    for m in range(1, 13):
        day_lists = calendar.monthdayscalendar(year, m)
        for dl in day_lists:
            if dl[day_of_the_week] > 0:
                print("%s/%s/%s") % (m, dl[day_of_the_week], year)
                break
def main():
    parser = argparse.ArgumentParser(
        description='Get the first specified day in each month of the year',
        epilog='example: date_query 2017 1')
    parser.add_argument(
        'year',
        type=int,
        help='The year to search, e.g. 2017')
    parser.add_argument(
        'day',
        type=int,
        help='A number between 0 and 6 which represents Monday-Sunday')

    args = parser.parse_args()
    year = args.year
    day_of_the_week = args.day

    if day_of_the_week < 0 or day_of_the_week > 6:
        print("Valid values for day are: 0 to 6")
    elif year < 1:
        print("Year must be great than zero")
    else:
        get_dates(year, day_of_the_week)

if __name__ == '__main__':
    main()
