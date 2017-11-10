from clinical_research_study_manager import stats_functions, data_request_functions


def get_enrollment_log_stats_by_date(enrollment_log_path: str):
    """
    Get basic enrollment stats for subjects enrolled between two dates
    :return: DataFrame filtered on the two dates
    """
    start_date = data_request_functions.get_date_info('Start')
    end_date = data_request_functions.get_date_info('End')
    df = stats_functions.get_basic_stats_by_date(
        enrollment_log_path, 'Enrollment_Log', 'Enrollment', start_date, end_date)
    stats_functions.get_basic_plot(df, enrollment_log_path, 'Enrollment')


def get_enrollment_log_basic_stats(enrollment_log_path: str):
    """Get basic stats on enrolled patients including number enrolled, number by sex, age,
    """
    stats_functions.get_stats(log_path=enrollment_log_path, log_sheet='Enrollment_Log', log_type='Enrollment')


def get_enrollment_log_stats_by_time(enrollment_log_path: str):
    """Get basic stats on enrolled patients by morning, afternoon, evening and night."""
    stats_functions.get_stats_by_time(enrollment_log_path, 'Enrollment_Log', 'Enrollment')


def choose_query(enrollment_log_path: str):
    while True:
        # Ask for what the user would like to do
        print("1. Basic Enrollment Log Stats")
        print("2. Get basic Enrollment stats between two dates")
        print("3. Get basic Enrollment stats by time of day")
        choice = input("What actions would you like to take, q to quit ")

        choices = {'1': get_enrollment_log_basic_stats,
                   '2': get_enrollment_log_stats_by_date,
                   '3': get_enrollment_log_stats_by_time,
                   }

        if choice is not None and choice.strip() and choices.get(choice) is not None:
            choices[choice](enrollment_log_path)

        elif choice is not None and choice.strip() and choice.lower() == 'q':
            break
        # Bad Entry
        else:
            print("Please enter a valid choice")


def main():
    pass


if __name__ == '__main__':
    main()
