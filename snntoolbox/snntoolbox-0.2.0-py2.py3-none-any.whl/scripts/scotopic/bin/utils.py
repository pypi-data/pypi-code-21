import os

from snntoolbox.bin.utils import load_config


def update_setup(config_filepath):
    """Update default settings with user settings and check they are valid.

    Load settings from configuration file at ``config_filepath``, and check that
    parameter choices are valid. Non-specified settings are filled in with
    defaults.
    """

    # Load defaults.
    config = load_config(os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'config_defaults')))

    # Overwrite with user settings.
    config.read(config_filepath)

    if not os.path.exists(config.get('paths', 'data_dir')):
        os.makedirs(config.get('paths', 'data_dir'))
