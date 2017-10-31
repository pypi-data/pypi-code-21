import os
import json
import stat
import sys
import csv

import yaml


# ============================================================================
# INTERNAL HELPERS
# ============================================================================


def _get_cfg_file_path():
    user_home = os.environ["HOME"]
    return os.path.join(user_home, ".jira", "config")


# ============================================================================
# CONFIG FUNCTIONS
# ============================================================================


def cfg_read_config():
    """
    Reads the configuration from the config file, usually $HOME/.jira/config

    :return: The configuration dict.
    """
    cfg_file_path = _get_cfg_file_path()
    if not os.path.isfile(cfg_file_path):
        print("ERROR: Config file not found. Invoke the script with 'init'.")
        sys.exit(-1)
    return json.load(open(_get_cfg_file_path(), "r", encoding='utf-8'))


def save_config(config):
    """
    Saves the configuration to the disk.

    :param config: The config dict object to save
    :return: None
    """
    cfg_file_path = _get_cfg_file_path()
    cfg_file_dir = os.path.dirname(cfg_file_path)
    if not os.path.isdir(cfg_file_dir):
        perms_dir = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
        os.mkdir(cfg_file_dir)
        os.chmod(cfg_file_dir, perms_dir)
    perms_file = stat.S_IRUSR | stat.S_IWUSR
    with open(cfg_file_path, "w") as cfgfile:
        cfgfile.write(json.dumps(config))
    # always, just because we can :)
    os.chmod(cfg_file_path, perms_file)


def cfg_save_search(search_alias, search_query):
    config = cfg_read_config()
    if not "saved_searches" in config:
        config["saved_searches"] = {}
    config["saved_searches"][search_alias] = search_query
    save_config(config)
    print("Search alias '{}' saved.".format(search_alias))


# ============================================================================
# MISC HELPERS
# ============================================================================


def check_file_present(filename):
    if not os.path.isfile(filename):
        print("File not found: '{}'.".format(filename))
        sys.exit(-1)


def get_hour_min(seconds):
    """
    Takes seconds and returns an (hours, minutes) tuple.
    :param seconds: The seconds to convert
    :return: The (hours, minutes) tuple
    """
    return (
        seconds // 3600,
        (seconds % 3600) // 60
    )


def print_table_from_dict(thedict, header=None):
    """
    Prints a formatted table from a dict.

    :param thedict: The dict to print as table
    :param header: Optional print a header for the columns. Must be a 2-tuple.
    :return:
    """
    max_col_len = max(map(lambda x: len(x), thedict.keys()))
    if header:
        max_col_len = max(len(header[0]) + 2, max_col_len)
        print("# {:<{width}}    {}"
              .format(header[0], header[1], width=max_col_len - 2))
    for a, t in sorted(thedict.items(), key=lambda x: x[0]):
        print("{:<{width}}    {}".format(a, t, width=max_col_len))


def load_and_parse_any(filename, filetype=None, csv_dialect='excel'):
    """
    Loads any given filename and returns the result. The file must be one of
    a supported structured data file types, currently:

    * Yaml
    * CSV
    * JSON

    :param filename: the path to the file to read
    :param filetype: you can specify the file type if it has a non-typical
    extension
    :param csv_dialect: In case of CSV files, you can specify the python
    csv module dialect to use.
    :return: The parsed file, in case of CSV always an array of dicts.
    """
    retval = None
    if not filetype:
        filetypes = {"yml": "yaml", "yaml": "yaml", "json": "json", "csv": "csv"}
        filetype = filetypes.get(filename.lower().split(".")[-1], None)
        if not filetype:
            print("Unable to determine file type from extension.")
            sys.exit(-1)
    if not filetype in ("yaml", "json", "csv"):
        print("Unsupported input file type: '{}'".format(filetype))
    with open(filename, "r") as infile:
        if filetype == "yaml":
            try:
                retval = yaml.load(infile)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError) as error:
                print("Error: Invalid YAML file.\nError message: {}"
                      .format(str(error)))
                sys.exit(-1)
        elif filetype == "json":
            retval = json.load(infile)
        elif filetype == "csv":
            reader = csv.DictReader(infile, dialect=csv_dialect)
            retval = [dict(row) for row in reader]
    return retval
