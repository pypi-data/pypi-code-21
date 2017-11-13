import os
from datetime import time

import matplotlib as plt
import pandas as pd

plt.rcParams['figure.figsize'] = (15, 15)


def print_stats(stat_type: str, patient_dict: dict):
    """
    Helper function for printing the stats from the patient data in a nice format
    :param stat_type: Stat type to print (Age, Race, Etc)
    :param patient_dict: dictionary containing stat data
    :return: No return
    """
    print("{} stats".format(stat_type), end="\n---------------------------\n")
    for stat, value in patient_dict.items():
        print(stat, value, sep=":")
    print()


def get_stats(log_path=None, log_sheet=None, log_type=None, data_frame=None):
    """
    Gets basic statistics for a log or a filtered DataFrame if given
    :param log_path: pathway to log to create stats from  (i.e. Screening, Enrollment)
    :param log_sheet: name of the sheet in the log that contains data (i.e. Screening_Loo, Enrollment_Log)
    :param log_type: type of log (i.e. Screening, Enrollment)
    :param data_frame: pre-filtered DataFrame generate stats for
    :return: No return
    """
    if log_path is not None and log_sheet is not None and log_type is not None:
        df = create_dataframe_from_log(log_path, log_sheet, log_type)
    else:
        df = data_frame
    # Total subjects
    if len(df) > 0:
        total_subjects_in_log = len(df)
        print("You have screened {} patients in total ".format(total_subjects_in_log))
        # Total by Sex
        get_stat_type(df, 'Sex')
        # Total by Age
        get_stat_type(df, 'Age')
        # Total Eligible
        get_stat_type(df, 'Eligible')
        # Reasons Ineligible
        get_stat_type(df, 'Reason_Ineligible')
        # Enrolled
        get_stat_type(df, 'Enrolled')
        # Reason Not Enrolled
        get_stat_type(df, 'Reason_Not_Enrolled')
    else:
        print("No subjects in log for that date")


def get_stat_type(df, stat_type):
    """
    Get statistics from a data frame for the given type if DataFrame contains that column
    :param df: DataFrame to get stats from
    :param stat_type: stat type to look for (i.e. Age, Gender)
    :return: No return
    """
    if stat_type == 'Age':
        if df.get('Age') is not None:
            age_stats = df['Age'].describe().to_dict()
            print_stats('Age', age_stats)
    elif df.get(stat_type) is not None:
        stat_value_counts = (df[stat_type].value_counts())
        print_stats(stat_type, stat_value_counts.to_dict())


def get_basic_stats_by_date(log_path, log_sheet, log_type, start_date, end_date):
    """
    Get basic statistics for a log filtered by date
    :param log_path: pathway to log to create stats from  (i.e. Screening, Enrollment)
    :param log_sheet: name of the sheet in the log that contains data (i.e. Screening_Loo, Enrollment_Log)
    :param log_type: type of log (i.e. Screening, Enrollment)
    :param start_date: initial date
    :param end_date: end date
    :return: data frame filtered on start_date and end_date
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    log_date = '{}Date'.format(log_type)
    df = create_dataframe_from_log(log_path, log_sheet, log_type)
    df[log_date] = df[log_date].apply(pd.to_datetime)
    df = df.loc[(df[log_date] >= start_date) & (df[log_date] <= end_date)]
    get_stats(data_frame=df)
    return df


def get_stats_by_time(log_path, log_sheet, log_type):
    """
    Get basic stats from a log by filtered by morning(7am-12pm), afternoon(12pm-4pm), evening(4pm-11pm),
    overnight(11pm-7am).
    :param log_path: pathway to log
    :param log_sheet: sheet in log where date is stored (i.e. Screening_Log)
    :param log_type: type of log your are searching (i.e. screening or enrollment)
    :return:
    """
    df = create_dataframe_from_log(log_path, log_sheet, log_type)
    morning = pd.to_datetime(str(time(7, 00).strftime('%H:%M')), format='%H:%M')
    afternoon = pd.to_datetime(str(time(12, 00).strftime('%H:%M')), format='%H:%M')
    evening = pd.to_datetime(str(time(16, 00).strftime('%H:%M')), format='%H:%M')
    night = pd.to_datetime(str(time(23, 00).strftime('%H:%M')), format='%H:%M')
    log_time = '{}Time'.format(log_type)
    df[log_time] = df[log_time].apply(pd.to_datetime, format='%H:%M')
    df_morning = df.loc[(df[log_time] >= morning) & (df[log_time] < afternoon)]
    df_afternoon = df.loc[(df[log_time] >= afternoon) & (df[log_time] < evening)]
    df_evening = df.loc[(df[log_time] >= evening) & (df[log_time] < night)]
    df_night = df.loc[(df[log_time] >= night) | (df[log_time] < morning)]
    # Morning Stats
    print("Stats for 07:00 to 12:00[Morning]")
    get_stats(data_frame=df_morning)
    print("-----------------------------", end="\n")
    print("Stats for 12:00 to 16:00[Afternoon]")
    get_stats(data_frame=df_afternoon)
    print("-----------------------------", end="\n")
    print("Stats for 16:00 to 23:00[Evening]")
    get_stats(data_frame=df_evening)
    print("-----------------------------", end="\n")
    print("Stats for 23:00 - 07:00[Overnight")
    get_stats(data_frame=df_night)
    return df_morning, df_afternoon, df_evening, df_night


def create_dataframe_from_log(log_path, log_sheet, log_type):
    """
    Create  a DataFrame from a given log
    :param log_path: pathway to log to create stats from  (i.e. Screening, Enrollment)
    :param log_sheet: name of the sheet in the log that contains data (i.e. Screening_Loo, Enrollment_Log)
    :param log_type: type of log (i.e. Screening, Enrollment)
    :return:
    """
    print("Created DataFrame using {} log with sheet {} located at {}".format(log_type, log_sheet, log_path))
    df = pd.read_excel(log_path)
    return df


def get_basic_plot(df, log_pathway, log_type):
    """
    Created basic bar graph plots for a log filtered on Months, Weeks, and WeekDays and saves them in
    projects Data_Visualization directory
    :param df: DataFrame to plot
    :param log_pathway: Pathway to log DataFrame was created from
    :param log_type: Type of Log (i.e. Screening, Enrollment, Follow Up
    :return:
    """
    if len(df) > 0:
        # Get the date column we will use for various counts
        column_for_grouping = '{}Date'.format(log_type)
        # Add a date index to df
        df.set_index(df[column_for_grouping].apply(pd.to_datetime), inplace=True, drop=False)
        # Add Month, week and weekday columns
        df['Month'] = df.index.month
        df['Week'] = df.index.week  # Should we use week of year here?
        df['WeekDay'] = df.index.weekday_name
        # Create groups for plotting
        month = df.groupby('Month').size()
        # month.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        week = df.groupby('Week').size()
        weekday = df.groupby('WeekDay').size()

        # Month
        data_viz_pathway = os.path.dirname(log_pathway).replace('logs', 'data_visualization')
        month_plot = month.plot(kind='bar')
        month_fig = month_plot.get_figure()
        month_figure_pathway = os.path.join(data_viz_pathway, '{}output_month.png'.format(log_type))
        month_fig.savefig(month_figure_pathway)
        print('Basic {} log by month chart saved to {}'.format(log_type, month_figure_pathway))

        # Week
        week_plot = week.plot(kind='bar')
        week_fig = week_plot.get_figure()
        week_figure_pathway = os.path.join(data_viz_pathway, '{}output_week.png'.format(log_type))
        week_fig.savefig(week_figure_pathway)
        print('Basic {} log by month chart saved to {}'.format(log_type, week_figure_pathway))

        # Weekday
        weekday_plot = weekday.plot(kind='bar')
        weekday_fig = weekday_plot.get_figure()
        weekday_figure_pathway = os.path.join(data_viz_pathway, '{}output_weekday.png'.format(log_type))
        weekday_fig.savefig(weekday_figure_pathway)
        print('Basic {} log by month chart saved to {}'.format(log_type, weekday_figure_pathway))


def main():
    pass


if __name__ == '__main__':
    main()
