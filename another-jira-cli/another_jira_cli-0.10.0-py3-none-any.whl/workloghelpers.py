import re
import csv
from datetime import date

import yaml

from .jirahelpers import *
from .tools import *


def parse_special_date_str(date_str_in=None):
    """
    Let arrow parse the date_str_in. On any error return todays date at 09:00h.
    date_str_in should be in the format "YYYY-MM-DD HH:MM"

    :param: date_str_in: The date string to be parsed
    :return: date.datetime object
    """
    arr = arrow.get(None).datetime
    if not date_str_in:
        return arr
    try:
        arr = arrow.get(date_str_in)
        if arr.datetime.hour == 0:
            arr = arr.replace(hour=+9)
        arr = arr.replace(hours=-2).datetime
    except arrow.parser.ParserError as e:
        arr = arrow.get(None).datetime
        print("wrong date time, set to today")
    return arr


def parse_yaml(data):
    """
    parse yaml line
    :param data: lines read in from yaml
    :return: dict of task: {'issue': , 'date': , 'log-time': ,'comment': }
    """
    dict_out = {}
    daytime = date.today().__str__()
    if 'date' in data.keys():
        daytime = data['date'].__str__()
        data.pop('date')
    for detail in data.values():
        detail_list = [x.strip() for x in detail.split(',')]
        dict_out['date'] = daytime + ' ' + '09:00'
        t1 = re.findall(r'\d{2}:\d{2}', detail)
        if t1:
            dict_out['date'] = daytime + ' ' + t1[0]
            detail_list.remove(t1[0])
        dict_out.update({'issue': detail_list[0],
                         'log-time': detail_list[1],
                         'comment': 'no comment'})
        if len(detail_list) > 2:
            dict_out.update({'comment': detail_list[2]})
    return dict_out


def calculate_logged_time_for(tickets_and_logs):
    """
    Takes the output of get_worklogs_for_date_and_user and calculates the
    logged seconds for the day.

    :param tickets_and_logs: Return value of get_worklogs_for_date_and_user
    :return: The logged seconds
    """
    worklogs = []
    for info_tuple in tickets_and_logs:
        worklogs += info_tuple[1]
    return sum(map(lambda x: x.timeSpentSeconds, worklogs))


def log_csv(csv_file, jira, delimiter):
    """
    log work from csv file
    :param: csv_file:
                issue;date;log-time;comment
                ticket1;;'30m';comment1
                ticket2;2017-01-01 09:00;'1h 30m';comment2
    :param: jira: jira interface
    """
    with open(csv_file, "r", encoding='utf-8') as file:
        dict_lines = csv.DictReader(file, delimiter=delimiter)
        for num_row, row_in in enumerate(dict_lines, start=1):
            row = {key: value.strip() for key, value in row_in.items()}
            add_worklog(row['issue'], parse_special_date_str(row['date']),
                        row['log-time'], row['comment'])


def log_yaml(yaml_file, jira):
    """
    log work from yaml file
    :param: yaml_file:
                date1:  ! the default date is today
                    task1: ticket-1, 30m, 11:00, comment 1 ! ticket, log-time, started time, comment
                    task2: ticket-1, 1h 30m, comment 2    ! without started time, default 09:00
                    task3: ticket-2, 2h, 13:00   ! without comment, default 'no comment'
                date2:
                    date: 2017-01-01    ! add this if you want to define the date
                    task1: ticket-1, 1h, coment 3
    :param: jira: jira interface
    """
    f = open(yaml_file)
    data_map = yaml.safe_load(f)
    for key, line in data_map.items():
        parse_line = parse_yaml(line)
        add_worklog(parse_line['issue'], parse_special_date_str(parse_line['date']),
                    parse_line['log-time'], parse_line['comment'])


