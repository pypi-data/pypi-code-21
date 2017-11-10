import os
import sys

import clinical_research_study_manager as rsm


def load_project(project_path: str, project_name: str):
    """
    Load a project to be managed for study tasks
    :param project_path: pathway to project
    :param project_name: name of the project
    :return:
    """
    if os.path.isdir(project_path):
        print("Opening {}".format(project_name))
        manage_project(project_path, project_name)
    else:
        print("{} does not exist")
        sys.exit(1)


def manage_project(project_path: str, project_name: str):
    """
    Perform basic tasks for a given project including entering patients on screening log, enrollment log
    follow up log, and master linking log.
    :param project_path: pathway to project
    :param project_name: naame of project
    :return:
    """
    choices = {'1': manage_logs,
               '2': manage_queries,
               }
    while True:
        print("1. Manage Logs")
        print("2. Query Logs")
        choice = input("Please choose what actions you would like to take, q to quit. ")

        if choice is not None and choice.strip() and choices.get(choice) is not None:
            choices[choice](project_path, project_name)
        elif choice is not None and choice.strip() and choice.lower() == 'q':
            break
        else:
            print("Please pick a valid option")


def manage_logs(project_path: str, project_name: str):
    while True:
        # Ask for what the user would like to do
        print("1. Enter Patients on Screening Log")
        print("2. Enter Patients on Enrollment Log")
        print("3. Enter Patients on Follow Up Log")
        print("4. Enter Patients on Master Linking Log")
        choice = input("What actions would you like to take, q to quit ")

        choices = {'1': rsm.enter_patient_on_log.enter_screened_patient,
                   '2': rsm.enter_patient_on_log.enter_enrolled_patient,
                   '3': rsm.enter_patient_on_log.enter_follow_up_patient,
                   '4': rsm.enter_patient_on_log.enter_linking_log_patient,
                   }

        if choice is not None and choice.strip() and choices.get(choice) is not None:
            choices[choice](project_path, project_name)

        elif choice is not None and choice.strip() and choice.lower() == 'q':
            break
        # Bad Entry
        else:
            print("Please enter a valid choice")


def manage_queries(project_path: str, project_name: str):
    project_log_path = os.path.join(project_path, 'logs')
    while True:
        # Ask for what the user would like to do
        print("1. Screening Queries")
        print("2. Enrollment Queries")
        print("3. Follow Up Queries")
        choice = input("What actions would you like to take, q to quit ")

        choices = {'1': (rsm.screening_queries.choose_query,
                         os.path.join(project_log_path, 'Screening_Log.xlsx')),
                   '2': (rsm.enrollment_queries.choose_query,
                         os.path.join(project_log_path, 'Enrollment_Log.xlsx')),
                   '3': (rsm.follow_up_queries.choose_query,
                         os.path.join(project_log_path, 'Follow_Up_Log.xlsx')),
                   }

        if choice is not None and choice.strip() and choices.get(choice) is not None:
            log_pathway = choices[choice][1]
            choices[choice][0](log_pathway)

        elif choice is not None and choice.strip() and choice.lower() == 'q':
            break
        # Bad Entry
        else:
            print("Please enter a valid choice")
