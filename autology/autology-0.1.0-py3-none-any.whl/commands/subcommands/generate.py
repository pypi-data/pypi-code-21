"""Sub command that will generate the content of the static site."""
import datetime
import pathlib

from autology import topics
from autology.configuration import get_configuration


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    generator_parser = subparser.add_parser('generate', help='Generate the static content')
    generator_parser.set_defaults(func=_main)


def _main(args):
    configuration_settings = get_configuration()

    sorted_files = {}

    # Need to find all of the files that are stored in the input_files directories in order to start building the
    # reports that will be used to generate the static log files.
    for input_path in configuration_settings.processing.inputs:
        search_path = pathlib.Path(input_path)

        # Currently going to make the assumption that everyone is using the path naming convention that I'm dictating
        # which is YYYY/MM/DD/file.ext
        for file_component in search_path.glob('*/*/*/*'):
            # Store all of the files into a dictionary containing the keys and a list of the files that are associated
            # with that day
            year, month, day = file_component.parent.relative_to(search_path).parts

            storage = sorted_files.setdefault(int(year), {})
            storage = storage.setdefault(int(month), {})
            storage.setdefault(int(day), []).append(file_component)

    dates = []

    topics.Processing.BEGIN.publish()

    # Now need to process each of the files in order, and build up a master static page for the content.
    for year in sorted(sorted_files.keys()):
        month_files = sorted_files[year]

        for month in sorted(month_files.keys()):
            day_files = month_files[month]

            for day in sorted(day_files.keys()):
                time_files = day_files[day]

                date_to_process = datetime.date(year, month, day)
                topics.Processing.DAY_START.publish(date=date_to_process)

                for content_file in time_files:
                    try:
                        topics.Processing.PROCESS_FILE.publish(file=content_file, date=date_to_process)
                    except:
                        print('Exception raised while processing: {}'.format(content_file))

                dates.append(date_to_process)
                topics.Processing.DAY_END.publish(date=date_to_process)

    topics.Processing.END.publish()

    topics.Reporting.BUILD_MASTER.publish()
