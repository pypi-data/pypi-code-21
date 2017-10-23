import os
import json
import stat
import sys


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
