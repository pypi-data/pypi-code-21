import datetime

from clinical_research_study_manager.exceptions import InputException


def get_date_info(time_point: str):
    """
    Get date information for enrolled subject from user(i.e. follow up time)
    :param time_point: time point requested for user(i.e. enrollment vs follow up)
    :return: Screening date as datetime object
    """
    while True:
        try:
            value_from_user = input("What is the {} date MM/DD/YYYY [Leave Blank for Today] ".format(time_point))
            # TODO: add validation for correct date input
            if value_from_user and value_from_user.strip():  # Need better validation
                month, day, year = value_from_user.split("/")
                value_from_user = datetime.date(int(year), int(month), int(day))
                break
            if not value_from_user:
                value_from_user = datetime.date.today()
                break
            if not value_from_user.strip():  # Bad entry
                raise InputException(
                    "Please enter a valid {} date in the format MM/DD/YYYY or leave blank for today".format(time_point),
                    time_point)
        except ValueError:
            # TODO: add better error messages to show why this failed
            print("Please enter a valid {} date in the format MM/DD/YYYY".format(time_point))
            continue
    return value_from_user


def get_time_info(time_point: str):
    """
    Get time information for enrolled subject from user(i.e. enrollment)
    :param time_point: time point requested from user(enrollment vs follow up)
    :return: time point as datetime object
    """
    while True:
        try:
            value_from_user = input("What is the {} time HH:MM [Leave Blank for Today] ".format(time_point))
            # TODO: add validation for correct time input
            if value_from_user and value_from_user.strip():  # Need better validation
                hour, minute = value_from_user.split(":")
                value_from_user = datetime.time(int(hour), int(minute))
                return value_from_user
            if not value_from_user:
                string_time = datetime.datetime.now().strftime("%H:%M")
                hour, minute = string_time.split(":")
                value_from_user = datetime.time(int(hour), int(minute))
                return value_from_user
            if not value_from_user.strip():  # Bad entry
                raise InputException(
                    'Please enter a valid {} time in the format HH:MM or leave blank for now'.format(time_point),
                    time_point)
        except InputException as e:
            print(e)
        except ValueError:
            print("Please enter a valid {} time in the format HH:MM or leave blank for now".format(time_point))
            continue


# TODO: Add a validation dictionary for each type of input


def get_info_from_user(requested_info: str):
    """
    Get requested info for enrolled patient from user(i.e. subject_initials)
    :param requested_info: name of variable requested as str
    :return: value given by user as str
    """
    validators = dict()
    greater_than_zero = lambda x: int(x) > 0 if x.isnumeric() else False
    male_female = lambda x: x.lower() in ('m', 'f') if x.isalpha() else False
    yes_no = lambda x: x.lower() in ('y', 'n') if x.isalpha() else False

    validators['age'] = greater_than_zero
    validators['sex'] = male_female
    validators['enrollment status'] = yes_no
    validators['eligibility status'] = yes_no
    validators['follow up complete'] = yes_no

    while True:
        try:
            value_from_user = input("What is the {} for subject ".format(requested_info))
            # TODO: add validation for correct type input
            value_from_user = value_from_user.strip()
            if value_from_user:
                # Check to see if we need to do special validation
                if validators.get(requested_info) is not None:
                    if validators[requested_info](value_from_user):
                        return value_from_user
                    else:
                        raise InputException('Please enter a valid {} for subject'.format(requested_info),
                                             requested_info)
                else:
                    return value_from_user
            if not value_from_user:  # Bad entry
                raise InputException("Please enter a valid {} for subject".format(requested_info), requested_info)
        except InputException as e:
            print(e)
            continue
