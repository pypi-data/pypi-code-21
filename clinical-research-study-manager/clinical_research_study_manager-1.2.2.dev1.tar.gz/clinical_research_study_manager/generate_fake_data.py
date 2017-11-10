import os
import random
from collections import OrderedDict

from clinical_research_study_manager.add_patient_to_excel_file import add_patient
from clinical_research_study_manager.study_manager import get_base_project_directory


def get_int(x, y):
    return random.randint(x, y)


options = dict()
options['sex'] = ['M', 'F', 'U']
options['yes_no_unknown'] = ['Y', 'N', 'U']
options['yes_no_na'] = ['Y', 'N', 'NA']
options['reasons_not_eligible'] = ['unconsentable', 'does_not_meet_criteria', 'previously_enrolled', 'NA']
options['reasons_not_enrolled'] = ['declined', 'NA']
options['mrn'] = list(range(10000000, 20000000))
options['age'] = list(range(1, 100))
options['enrollment_arm'] = ['arm1', 'arm2']
options['name'] = ['jane', 'doe', 'bob', 'marley']


def get_options(options_dict=options):
    options_dict['date'] = ['{}/{}/{}'.format(get_int(1, 12),
                                              get_int(1, 28),
                                              get_int(2016, 2018)
                                              )
                            ]
    options_dict['time'] = ['{}:{}'.format(get_int(0, 23),
                                           get_int(0, 59)
                                           )
                            ]
    options_dict['initials'] = ['{}{}{}'.format(chr(get_int(97, 122)),
                                                chr(get_int(97, 122)),
                                                chr(get_int(97, 122))
                                                )
                                ]
    options['subject_id'] = [get_int(1, 1000)]
    return options


def get_screening_headers():
    screening_headers = OrderedDict()
    screening_headers['ScreeningDate'] = 'date'
    screening_headers['ScreeningTime'] = 'time'
    screening_headers['SubjectInitials'] = 'initials'
    screening_headers['MedicalRecordNumber'] = 'mrn'
    screening_headers['Age'] = 'age'
    screening_headers['Sex'] = 'sex'
    screening_headers['Eligible'] = 'yes_no_unknown'
    screening_headers['ReasonIneligible'] = 'reasons_not_eligible'
    screening_headers['Enrolled'] = 'yes_no_na'
    screening_headers['ReasonNotEnrolled'] = 'reasons_not_enrolled'
    screening_headers['ResearchAssistantInitials'] = 'initials'
    return screening_headers


def get_enrollment_headers():
    enrollment_headers = OrderedDict()
    enrollment_headers['SubjectID'] = 'subject_id'
    enrollment_headers['EnrollmentDate'] = 'date'
    enrollment_headers['EnrollmentTime'] = 'time'
    enrollment_headers['Age'] = 'age'
    enrollment_headers['Sex'] = 'sex'
    enrollment_headers['EnrollmentArm'] = 'enrollment_arm'
    enrollment_headers['ResearchAssistantInitials'] = 'initials'
    return enrollment_headers


def get_follow_up_headers():
    follow_up_headers = OrderedDict()
    follow_up_headers['SubjectID'] = 'subject_id'
    follow_up_headers['EnrollmentDate'] = 'date'
    follow_up_headers['EnrollmentTime'] = 'time'
    follow_up_headers['FollowUpDate'] = 'date'
    follow_up_headers['FollowUpTime'] = 'time'
    follow_up_headers['FollowUpComplete'] = 'yes_no_na'
    follow_up_headers['Notes'] = 'yes_no_na'
    return follow_up_headers


def get_linking_log_headers():
    linking_headers = OrderedDict()
    linking_headers['SubjectID'] = 'subject_id'
    linking_headers['MedicalRecordNumber'] = 'mrn'
    linking_headers['EnrollmentDate'] = 'date'
    linking_headers['EnrollmentTime'] = 'time'
    linking_headers['SubjectName'] = 'name'
    linking_headers['Age'] = 'age'
    linking_headers['Sex'] = 'sex'
    linking_headers['ResearchAssistantInitials'] = 'initials'
    return linking_headers


def generate_patient_dict(data_headers: OrderedDict) -> OrderedDict:
    options = get_options()
    patient_dict = OrderedDict()
    for header, data_type in data_headers.items():
        patient_dict[header] = random.choice(options[data_type])
    return patient_dict


def main():
    BASE_DIR = get_base_project_directory()
    BASE_DIR = os.path.join(BASE_DIR, 'Testing')
    screening_log_path = os.path.join(BASE_DIR, 'logs', 'Screening_Log.xlsx')
    enrollment_log_path = os.path.join(BASE_DIR, 'logs', 'Enrollment_Log.xlsx')
    follow_up_log = os.path.join(BASE_DIR, 'logs', 'Follow_Up_Log.xlsx')
    master_linking_log = os.path.join(BASE_DIR, 'logs', 'logs_with_phi', 'Master_Linking_Log.xlsx')

    data_files = [(screening_log_path, 'Screening_Log', get_screening_headers),
                  (enrollment_log_path, 'Enrollment_Log', get_enrollment_headers),
                  (follow_up_log, 'Follow_Up_Log', get_follow_up_headers),
                  (master_linking_log, 'Master_Linking_Log', get_linking_log_headers)
                  ]
    for data_file, data_sheet, data_func in data_files:
        print("writing {} file".format(data_file))
        for _ in range(100):
            patient_dict = generate_patient_dict(data_func())
            add_patient(data_file, patient_dict, data_sheet)


if __name__ == '__main__':
    main()
