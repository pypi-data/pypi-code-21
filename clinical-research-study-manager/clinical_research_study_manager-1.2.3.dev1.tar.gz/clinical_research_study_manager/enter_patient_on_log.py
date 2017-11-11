import os

import clinical_research_study_manager as rsm


def enter_screened_patient(project_path: str, project_name: str):
    """
    Enter a patient on the screening log for the project
    :param project_path: pathway to project
    :param project_name: project name
    :return:
    """
    # Get Screening Log
    screening_log_path = os.path.join(project_path, 'logs', 'Screening_Log.xlsx')

    while True:
        choice = input("Would you like to enter a new patient onto the screening log [Y/N]? ")

        if choice and choice.strip() and choice.lower() == 'y':
            patient_data = rsm.get_data_from_user.get_screened_patient_data()
            rsm.add_patient_to_excel_file.add_patient(screening_log_path,
                                                      patient_data,
                                                      'Screening_Log')
            print("Successfully added patient to {} screening log".format(project_name))

        elif choice and choice.strip() and choice.lower() == 'n':
            break
        else:
            print("Please enter Y or N")


def enter_enrolled_patient(project_path: str, project_name: str):
    """
    Enter patient onto enrollment log for project
    :param project_path: pathway to project
    :param project_name: project name
    :return:
    """
    # Get Enrollment Log
    enrollment_log_path = os.path.join(project_path, 'logs', 'Enrollment_Log.xlsx')

    while True:
        choice = input("Would you like to enter a new patient onto the Enrollment log [Y/N]? ")

        if choice and choice.strip() and choice.lower() == 'y':
            patient_data = rsm.get_data_from_user.get_enrolled_patient_data()
            rsm.add_patient_to_excel_file.add_patient(enrollment_log_path,
                                                      patient_data,
                                                      'Enrollment_Log')
            print("Successfully added patient to {} Enrollment log".format(project_name))

        elif choice and choice.strip() and choice.lower() == 'n':
            break
        else:
            print("Please enter Y or N")


def enter_follow_up_patient(project_path: str, project_name: str):
    """
    Enter patient onto the follow up log for the project
    :param project_path: pathway to project
    :param project_name: project name
    :return:
    """
    # Get Follow Up Log
    follow_up_log_path = os.path.join(project_path, 'logs', 'Follow_Up_Log.xlsx')

    while True:
        choice = input("Would you like to enter a new patient onto the Follow Up log [Y/N]? ")

        if choice and choice.strip() and choice.lower() == 'y':
            patient_data = rsm.get_data_from_user.get_follow_up_data()
            rsm.add_patient_to_excel_file.add_patient(follow_up_log_path,
                                                      patient_data,
                                                      'Follow_Up_Log')
            print("Successfully added patient to {} Follow Up log".format(project_name))

        elif choice and choice.strip() and choice.lower() == 'n':
            break
        else:
            print("Please enter Y or N")


def enter_linking_log_patient(project_path: str, project_name: str):
    """
    Enter patient onto the linking log for project
    :param project_path: pathway to project
    :param project_name: project name
    :return:
    """
    # Get Linking Log
    linking_log_path = os.path.join(project_path, 'logs', 'logs_with_phi', 'Master_Linking_Log.xlsx')

    while True:
        choice = input("Would you like to enter a new patient onto the Linking log log [Y/N]? ")

        if choice and choice.strip() and choice.lower() == 'y':
            patient_data = rsm.get_data_from_user.get_master_linking_log_data()
            rsm.add_patient_to_excel_file.add_patient(linking_log_path,
                                                      patient_data,
                                                      'Master_Linking_Log')
            print("Successfully added patient to {} Master Linking log".format(project_name))

        elif choice and choice.strip() and choice.lower() == 'n':
            break
        else:
            print("Please enter Y or N")
