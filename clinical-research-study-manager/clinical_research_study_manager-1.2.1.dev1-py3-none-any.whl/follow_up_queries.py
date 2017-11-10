import datetime

import pandas as pd

from clinical_research_study_manager.data_request_functions import get_date_info
from clinical_research_study_manager.stats_functions import create_dataframe_from_log


def follow_up_by_custom_dates(follow_up_log_path):
    """
    Find follow ups between a two dates
    :param follow_up_log_path: pathway to log
    :return: DataFrame filter on the two dates
    """
    start_date = get_date_info('Follow Up Start')
    end_date = get_date_info('Follow Up End')
    follow_up_df = follow_ups_scheduled_between_dates(follow_up_log_path, start_date=start_date, end_date=end_date)
    print("You have {} follow Ups scheduled between {} and {}".format(len(follow_up_df), start_date, end_date))
    print(follow_up_df.head())
    return follow_up_df


def follow_ups_scheduled_for_today(follow_up_log_path):
    """
    Get Follow Ups Scheduled for Today
    :param follow_up_log_path: pathway to log
    :return: DataFrame filtered on today
    """
    today = pd.to_datetime(datetime.date.today())
    type(today)
    follow_up_df = follow_up_scheduled_on_date(follow_up_log_path, follow_up_date=today)
    print("You have {} follow ups scheduled for today".format(len(follow_up_df)))
    print(follow_up_df)
    return follow_up_df


def follow_ups_scheduled_for_this_week(follow_up_log_path):
    """
    Get Follow Ups scheduled for this week
    :return:  DataFrame filtered on today
    """
    start_of_week = pd.to_datetime(datetime.date.today())
    end_of_week = pd.to_datetime(datetime.date.today() + datetime.timedelta(7))
    follow_up_df = follow_ups_scheduled_between_dates(follow_up_log_path)
    print("You have {} follow ups scheduled for this week".format(len(follow_up_df)))
    print(follow_up_df.head())
    return follow_up_df


def follow_up_scheduled_on_date(follow_up_log_path, follow_up_date=None):
    """
    Create follow up DataFrame filtered on a specific date
    :param follow_up_log_path: pathway to log
    :param follow_up_date: date to filter DataFram on if given
    :return: Filtered DataFrame
    """
    if follow_up_date is None:
        follow_up_date = get_date_info('Follow Up')
    follow_up_df = create_dataframe_from_log(log_path=follow_up_log_path,
                                             log_sheet='Follow_Up_Log',
                                             log_type='FollowUp')
    today_df = follow_up_df.loc[(follow_up_df.FollowUpDate == follow_up_date)]
    print("You have {} follow up scheduled on {}".format(len(today_df), follow_up_date))
    print(today_df.head())
    return today_df


def follow_ups_scheduled_between_dates(follow_up_log_path, start_date=None, end_date=None):
    """
    Create Follow up DataFrame filtered between two dates
    :param follow_up_log_path: pathway to log
    :param start_date: start date if given
    :param end_date: end date if given
    :return: Filtered DataFrame
    """
    if start_date is None and end_date is None:
        start_date = get_date_info('Start')
        end_date = get_date_info('End')
    follow_up_df = create_dataframe_from_log(log_path=follow_up_log_path,
                                             log_sheet='Follow_Up_Log',
                                             log_type='FollowUp')
    week_df = follow_up_df.loc[(follow_up_df.FollowUpDate >= start_date) & (follow_up_df.FollowUpDate <= end_date)]
    print("You have {} follow ups scheduled between {} and {}".format(len(week_df), start_date, end_date))
    print(week_df.head())
    return week_df


def patients_at_risk_of_being_lost(follow_up_log_path):
    """
    Create Follow up data frame for at risk subjects
    :return: DataFrame containing subjects at risks of being lost to follow up
    """
    today = pd.to_datetime(datetime.date.today())
    follow_up_df = create_dataframe_from_log(log_path=follow_up_log_path,
                                             log_sheet='Follow_Up_Log',
                                             log_type='FollowUp')
    at_risk_df = follow_up_df.loc[(follow_up_df.FollowUpDate < today) &
                                  (follow_up_df.FollowUpComplete == 'N')]
    print("There are {} subjects at risk of being lost".format(len(at_risk_df)))
    print(at_risk_df.head())
    return at_risk_df


def choose_query(follow_up_log_path: str):
    while True:
        # Ask for what the user would like to do
        print("1. Follow Ups Today)")
        print("2. Follow Ups This Week")
        print("3. Follow Ups on a specific Date")
        print("4. Follow Ups Between two Dates")
        print("5. Patients at Risk of being lost to follow up")
        choice = input("What actions would you like to take, q to quit ")

        choices = {'1': follow_ups_scheduled_between_dates,
                   '2': follow_ups_scheduled_for_this_week,
                   '3': follow_up_scheduled_on_date,
                   '4': follow_ups_scheduled_between_dates,
                   '5': patients_at_risk_of_being_lost,
                   }

        if choice is not None and choice.strip() and choices.get(choice) is not None:
            choices[choice](follow_up_log_path)

        elif choice is not None and choice.strip() and choice.lower() == 'q':
            break
        # Bad Entry
        else:
            print("Please enter a valid choice")

def main():
    pass

if __name__ == '__main__':
    main()
