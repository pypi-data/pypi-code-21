from clinical_research_study_manager import data_request_functions, stats_functions


def get_screening_log_stats_by_date(screening_log_path: str):
    """
    Get basic stats from patients screened between two given dates
    :param screening_log_path: pathway to log
    :return: df filtered on the requested dates
    """
    start_date = data_request_functions.get_date_info('Start')
    end_date = data_request_functions.get_date_info('End')
    df = stats_functions.get_basic_stats_by_date(
        screening_log_path, 'Screening_Log', 'Screening', start_date, end_date)
    stats_functions.get_basic_plot(df, screening_log_path, 'Screening')
    return df


def get_screening_log_basic_stats(screening_log_path: str):
    """
    Get basic stats from the screening log including total screened, total by sex, age ranges,
    total eligible and reasons not eligible, total enrolled and reasons not enrolled.
    :param screening_log_path: pathway to log
    :return: No return
    """
    stats_functions.get_stats(log_path=screening_log_path, log_sheet='Screening_Log', log_type='Screening')


def get_screening_log_stats_by_time(screening_log_path: str):
    """
    Get basic stats based on morning, afternoon, evening and night
    :param screening_log_path: pathway to log
    :return: No Return
    """
    stats_functions.get_stats_by_time(screening_log_path, 'Screening_Log', 'Screening')


def choose_query(screening_log_path: str):
    while True:
        # Ask for what the user would like to do
        print("1. Basic Screening Log Stats")
        print("2. Get basic stats between two dates")
        print("3. Get basic stats by time of day")
        choice = input("What actions would you like to take, q to quit ")

        choices = {'1': get_screening_log_basic_stats,
                   '2': get_screening_log_stats_by_date,
                   '3': get_screening_log_stats_by_time,
                   }

        if choice is not None and choice.strip() and choices.get(choice) is not None:
            choices[choice](screening_log_path)

        elif choice is not None and choice.strip() and choice.lower() == 'q':
            break
        # Bad Entry
        else:
            print("Please enter a valid choice")


def main():
    pass


if __name__ == '__main__':
    main()
