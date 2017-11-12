import argparse
import os
import sys

from clinical_research_study_manager import create_directories, create_excel_files, load_project
from clinical_research_study_manager.tests import testing_input_types

parser = argparse.ArgumentParser(prog='Research Study Manager',
                                 description='Command line interface to manage some common research tasks')
parser.add_argument('-create_project', metavar='Project_Name',
                    help='Creates a new project titled Project_Name in the Projects directory')
parser.add_argument('-load_project', metavar='Project_Name',
                    help='Loads Project Project_Name from the Projects directory for study activities')
parser.add_argument('-list_projects', action='store_true', help='List available projects to load')
parser.add_argument('-run_tests', action='store_true', help='Run test for the module')


def main():
    start()


def get_base_project_directory():
    """
    Creates the default project directories if needed and returns them
    :return: base directory where projects will be stored
    """
    if sys.platform in ('linux', 'darwin'):
        base_program_dir = os.path.join(os.environ['HOME'], 'Clinical_Research_Manager_Projects')
        base_project_dir = os.path.join(base_program_dir, 'Projects')
        if not os.path.exists(base_program_dir):
            os.mkdir(base_program_dir)
        if not os.path.exists(base_project_dir):
            os.mkdir(base_project_dir)
        return base_project_dir

    if sys.platform == 'win32':
        base_program_dir = os.path.join(os.environ['USERPROFILE'], 'Clinical_Research_Manager_Projects')
        base_project_dir = os.path.join(base_program_dir, 'Projects')
        if not os.path.exists(base_program_dir):
            os.mkdir(base_program_dir)
        if not os.path.exists(base_project_dir):
            os.mkdir(base_project_dir)
        return base_project_dir

    print("Can not determine system type")
    sys.exit(1)


def start():
    project_directory = get_base_project_directory()
    args = parser.parse_args()
    # Create new project
    if args.create_project is not None and args.create_project.strip():
        project_name = args.create_project.strip()
        project_path = os.path.join(project_directory, project_name)
        print("Creating new project titled {}".format(project_name))
        create_directories.create_project_directories(project_path, project_name)
        print("Created log files for project {}".format(project_name))
        create_excel_files.create_project_excel_files(project_path, project_name)
    # Bad entry
    elif args.create_project is not None and not args.create_project.strip():
        print("You must supply a non empty string")
        sys.exit(1)
    # load specific project
    if args.load_project is not None and args.load_project.strip():
        project_name = args.load_project.strip()
        project_path = os.path.join(project_directory, project_name)
        if os.path.exists(project_path) and os.path.isdir(project_path):
            load_project.load_project(project_path, project_name)
        else:
            print('Project does not exist')
            sys.exit(1)
    # Bad Entry
    elif args.load_project is not None and not args.load_project.strip():
        print("You must supply a non empty string")

    # Load list of projects for user to choose from
    if args.list_projects is True:
        print(os.listdir(project_directory))
        current_projects = {pid + 1: project
                            for pid, project in enumerate(os.listdir(project_directory))
                            if os.path.isdir(os.path.join(project_directory, project))
                            }
        # Create dict of projects to
        if current_projects:
            while True:
                print('Current Projects are: ')
                for pid, project_title in current_projects.items():
                    print('{} : {}'.format(pid, project_title))

                choice = (input('Please choose a project, q to quit. '))
                choice = int(choice) if choice.isnumeric() else choice
                if current_projects.get(choice):
                    project_title = current_projects[choice]
                    project_path = os.path.join(project_directory, project_title)
                    load_project.load_project(project_path, project_title)
                    sys.exit(0)
                elif choice.lower() == 'q':
                    sys.exit(0)
                else:
                    print('Please enter a valid choice')
                    continue

    # Run test
    if args.run_tests is True:
        testing_input_types.run_tests()


if __name__ == '__main__':
    main()
