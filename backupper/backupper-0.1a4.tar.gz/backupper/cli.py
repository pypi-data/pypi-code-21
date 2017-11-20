"""
    backupper entrypoint.
"""

import sys
import os
import shutil
import getopt
import re
import yaml
import tarfile
import datetime

import backupper
from . import utils

def main():
    """
        Main entrypoint.

        .. todo:: Move configuration variables somewhere else, cut this big function into smaller chunks.
    """

    # Configuration variables
    configuration_file = "backupfile.yml"
    configuration = None
    command_name = os.path.basename(sys.argv[0])
    backup_datetime = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

    ## Initialisation ##

    # Fetch command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:hV", ["config-file=", "help", "version"])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: command line arguments: {}\n".format(e))
        sys.stderr.write("Try {} -h for help.\n".format(command_name))
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            sys.stdout.write(utils.get_help(command_name, configuration_file))
            sys.exit(0)
        if opt in ("-V", "--version"):
            sys.stdout.write("{}\n".format(utils.get_version()))
            sys.exit(0)
        if opt in ("-f", "--config-file"):
            configuration_file = str(arg)

    # Parse the configuration file
    print("Loading {}.".format(configuration_file))
    try:
        with open(configuration_file, "r") as f:
            configuration = yaml.load(f)
    except Exception as e:
        sys.stderr.write("Error: yaml parsing: {}\n".format(e))
        sys.exit(2)

    # Validate the configuration file
    try:
        utils.validate_configuration(configuration)
    except Exception as e:
        sys.stderr.write("Error: configuration validation: {}\n".format(e))
        sys.exit(3)

    # The configuration file directory sets the backup context, so if it's not in the current directory, let's change the working directory
    if os.path.dirname(configuration_file) != "":
        os.chdir(os.path.dirname(configuration_file))

    ## Actual backups ##

    # Our actual backup will take place in a timestampped subdir
    actual_backup_dir = os.path.join(configuration["backup_dir"], "backup_{}".format(backup_datetime))

    # We create our backup dir
    try:
        os.makedirs(actual_backup_dir)
    except OSError as e:
        sys.stderr.write("Error: backup dir creation: {}\n".format(e))
        sys.exit(4)


    # As we allow absolute path, we must absolutize all of them so that os.path.commonpath can work (but also to have a coherent backup dir structure)
    configuration["artifacts"] = [os.path.abspath(artifact) for artifact in configuration["artifacts"]]

    # We need to know the common path for artifacts to remove it from the backup output structure
    common_artifact_path = os.path.commonpath(configuration["artifacts"])

    # Backup each artifact
    print("Backupping artifacts.")
    for artifact in configuration["artifacts"]:
        if not os.path.exists(artifact):
            sys.stderr.write("Warning: backup: {} doesn't exist (skipping).\n".format(artifact))
            continue

        # If our artifact is a directory we must remove the trailing slash so that os.path.basename can properly work
        if os.path.isdir(artifact):
            if artifact.endswith('/'):
                artifact = artifact[:-1]

        # Build the output tar path
        output_tar = "{}.{}.tar.gz".format(os.path.join(actual_backup_dir, os.path.relpath(artifact, common_artifact_path)), backup_datetime)

        # Create subdirectories
        try:
            os.makedirs(os.path.dirname(output_tar))
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                sys.stderr.write("Error: backup: {}\n".format(e))
                sys.exit(4)

        # Write the actual tar file
        with tarfile.open(output_tar, "w:gz") as tar:
            tar.add(artifact, arcname=os.path.basename(artifact))

        sys.stdout.write("{} done.\n".format(output_tar))

    ## Old backups cleaning ##

    if configuration["delete_old_backups"]:
        has_cleaning_policy = not (all(configuration["cleaning_policy"][key] == 0 for key in configuration["cleaning_policy"]))
        sys.stdout.write("Cleaning old backups. Strategy:")

        if has_cleaning_policy:
            sys.stdout.write("\n")
            for policy in sorted(configuration["cleaning_policy"]):
                sys.stdout.write("    {}: {}\n".format(policy, configuration["cleaning_policy"][policy]))
        else:
            sys.stdout.write("all.\n")

        # Backup pattern: a backup created by this script should look like this
        backup_pattern = re.compile(r'backup_(?P<datetime_str>[0-9]{14})$')

        # We discard regular files and directories that don't match the expected backup pattern
        directories = [os.path.join(configuration["backup_dir"], f) for f in os.listdir(configuration["backup_dir"]) if os.path.isdir(os.path.join(configuration["backup_dir"], f))]
        backups_list = list(filter(backup_pattern.search, directories))

        # We always keep the current backup so we remove it from this list
        backups_list.remove(actual_backup_dir)

        # We can terminate the program if we have no old backup
        if len(backups_list) == 0:
            sys.exit(0)

        backups_to_keep = []

        # Skip some calculation if all cleaning policies are equal to 0
        if has_cleaning_policy:
            # We associate to each backup its corresponding datetime
            backups_datetime = [datetime.datetime.strptime(backup_pattern.search(elem).group("datetime_str"), '%Y%m%d%H%M%S') for elem in backups_list]

            # We sort files_datetime and selected_files accordingly
            backups_datetime, backups_list = (list(t) for t in zip(*sorted(zip(backups_datetime, backups_list))))

            # We also need the date of our current backup
            curr_backup_date = datetime.datetime.strptime(backup_pattern.search(actual_backup_dir).group("datetime_str"), '%Y%m%d%H%M%S').date()

            # Most recent backups
            most_recent_backups = backups_list[-configuration["cleaning_policy"]["most_recents"]:]
            backups_to_keep.extend(most_recent_backups)

            # First daily files
            backups_of_the_day = [backups_list[i] for i in range(0, len(backups_list)) if backups_datetime[i].date() == curr_backup_date][0:configuration["cleaning_policy"]["first_daily"]]
            backups_to_keep.extend(backups_of_the_day)

            # First weekly files
            backups_of_the_week = [backups_list[i] for i in range(0, len(backups_list)) if (abs(backups_datetime[i].date() - curr_backup_date) < datetime.timedelta(days=7) and backups_datetime[i].weekday() <= curr_backup_date.weekday())][0:configuration["cleaning_policy"]["first_weekly"]]
            backups_to_keep.extend(backups_of_the_week)

            # First monthly files
            backups_of_the_month = [backups_list[i] for i in range(0, len(backups_list)) if backups_datetime[i].date().replace(day=1) == curr_backup_date.replace(day=1)][0:configuration["cleaning_policy"]["first_monthly"]]
            backups_to_keep.extend(backups_of_the_month)

        for backup in backups_list:
            if backup not in backups_to_keep:
                shutil.rmtree(backup)
                sys.stdout.write("{} deleted.\n".format(backup))

    sys.exit(0)
