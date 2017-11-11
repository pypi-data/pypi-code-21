import os
from collections import namedtuple

from clinical_research_study_manager import add_patient_to_excel_file, data_request_functions

# TODO: Create test to make sure tuple fields match header fields in all areas of program

ScreenedPatient = namedtuple("ScreenedPatient", ",".join(['ScreeningDate', 'ScreeningTime SubjectInitials',
                                                          'MedicalRecordNumber', 'Age', 'Sex', 'Eligible',
                                                          'ReasonIneligible', 'Enrolled',
                                                          'ReasonNotEnrolled', 'ResearchAssistantInitials'
                                                          ]))
EnrolledPatient = namedtuple("EnrolledPatient",
                             ",".join(['SubjectID', 'EnrollmentDate', 'EnrollmentTime', 'Age', 'Sex',
                                       'EnrollmentArm', 'ResearchAssistantInitials'
                                       ]))
LinkedPatient = namedtuple("LinkedPatient", ",".join(['SubjectID', 'MedicalRecordNumber', 'EnrollmentDate',
                                                      'EnrollmentTime', 'SubjectName', 'Age', 'Sex',
                                                      'ResearchAssistantInitials'
                                                      ]))
FollowUpPatient = namedtuple("FollowUpPatient", ",".join(['SubjectID', 'EnrollmentDate', 'EnrollmentTime',
                                                          'FollowUpDate', 'FollowUpTime', 'FollowUpComplete',
                                                          'Notes'
                                                          ]))


def to_dict(func: namedtuple):
    """Converts a named tuple to its order dictionary form"""

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)._asdict()

    return wrapper


@to_dict
def get_screened_patient_data() -> ScreenedPatient:
    """
    Get screening data for a single screened subject
    :return: Named Tuple with subjects data
    """
    patient_data = dict()
    patient_data['ScreeningDate'] = data_request_functions.get_date_info('screening')
    patient_data['ScreeningTime'] = data_request_functions.get_time_info('screening')
    patient_data['SubjectInitials'] = data_request_functions.get_info_from_user('subject initials')
    patient_data['MedicalRecordNumber'] = data_request_functions.get_info_from_user('medical record number')
    patient_data['Age'] = data_request_functions.get_info_from_user('age')
    patient_data['Sex'] = data_request_functions.get_info_from_user('sex')
    patient_data['Eligible'] = data_request_functions.get_info_from_user('eligibility status')
    patient_data['ReasonIneligible'] = data_request_functions.get_info_from_user('reason ineligible')
    patient_data['Enrolled'] = data_request_functions.get_info_from_user('enrollment status')
    patient_data['ReasonNotEnrolled'] = data_request_functions.get_info_from_user('reason not enrolled')
    patient_data['ResearchAssistantInitials'] = data_request_functions.get_info_from_user(
        'research assistant initials')

    return ScreenedPatient(**patient_data)


@to_dict
def get_enrolled_patient_data() -> EnrolledPatient:
    """
    Get enrollment data for an enrolled subject
    :return: Named Tuple with subjects data
    """
    patient_data = dict()
    patient_data['SubjectID'] = data_request_functions.get_info_from_user('subject id')
    patient_data['EnrollmentDate'] = data_request_functions.get_date_info('enrollment')
    patient_data['EnrollmentTime'] = data_request_functions.get_time_info('enrollment')
    patient_data['Age'] = data_request_functions.get_info_from_user('age')
    patient_data['Sex'] = data_request_functions.get_info_from_user('sex')
    patient_data['EnrollmentArm'] = data_request_functions.get_info_from_user('enrollment arm')
    patient_data['ResearchAssistantInitials'] = data_request_functions.get_info_from_user(
        'research assistant initials')

    return EnrolledPatient(**patient_data)


@to_dict
def get_master_linking_log_data() -> LinkedPatient:
    """
    Get master linking data for an enrolled subject
    :return: Named Tuple with subjects data
    """
    patient_data = dict()
    patient_data['SubjectID'] = data_request_functions.get_info_from_user('subject_id')
    patient_data['MedicalRecordNumber'] = data_request_functions.get_info_from_user('medical_record_number')
    patient_data['EnrollmentDate'] = data_request_functions.get_date_info('enrollment')
    patient_data['EnrollmentTime'] = data_request_functions.get_time_info('enrollment')
    patient_data['SubjectName'] = data_request_functions.get_info_from_user('subject_name')
    patient_data['Age'] = data_request_functions.get_info_from_user('age')
    patient_data['Sex'] = data_request_functions.get_info_from_user('sex')
    patient_data['ResearchAssistantInitials'] = data_request_functions.get_info_from_user(
        'research assistant initials')

    return LinkedPatient(**patient_data)


@to_dict
def get_follow_up_data() -> FollowUpPatient:
    """
    Get follow up data for a single enrolled subject
    :return: Named Tuple with subjects data
    """
    patient_data = dict()
    patient_data['SubjectID'] = data_request_functions.get_info_from_user('subject id')
    patient_data['EnrollmentDate'] = data_request_functions.get_date_info('enrollment')
    patient_data['EnrollmentTime'] = data_request_functions.get_time_info('enrollment')
    patient_data['FollowUpDate'] = data_request_functions.get_date_info('follow up')
    patient_data['FollowUpTime'] = data_request_functions.get_time_info('follow up')
    patient_data['FollowUpComplete'] = data_request_functions.get_info_from_user('follow up complete')
    patient_data['Notes'] = data_request_functions.get_info_from_user('notes')
    return FollowUpPatient(**patient_data)


def main():
    screened_patient_data = get_screened_patient_data()
    add_patient_to_excel_file.add_patient(os.path.join('logs', 'Screening_Log.xlsx'), screened_patient_data,
                                          'Screening_Log')


if __name__ == '__main__':
    main()
