from . import parser
from . import io

__version__ = "0.1.7"


def mingled(files):
    """ Generator to mingle several log files by returning their lines out in respective time order. """
    with io.DictFileOpener(files) as file_data:
        while True:
            positions = {filename: file_data[filename].tell() for filename in files}
            lines = {filename: file_data[filename].readline() for filename in files}

            if all(line.strip() == '' for line in lines.values()):
                break

            times = {filename: parser.parseline(lines[filename]) for filename in files if lines[filename].strip()}
            first_file = sorted(times.items(), key=lambda x: x[1])[0][0]

            for unused_file in [filename for filename in times.keys() if filename is not first_file]:
                file_data[unused_file].seek(positions[unused_file])

            yield lines[first_file], first_file


def cat(files, label=True):
    """ Print all the lines out from the provided files, in the time order they occurred. """
    prev_filename = None

    for line, filename in mingled(files):
        if filename != prev_filename and label:
            if prev_filename is not None:
                print("")
            print("==> {} <==".format(filename))
        print(line.strip())
        prev_filename = filename
