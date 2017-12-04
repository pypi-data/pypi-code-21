import ruamel.yaml as yaml
from typing import Any


def load_yaml(
    file: str,
    keep_order: bool = False
    ) -> dict:
    """
    Load yaml file.
    """
    with open(file, 'r') as stream:
        if keep_order:
            return yaml.load(stream.read(), Loader=yaml.RoundTripLoader)
        else:
            return yaml.safe_load(stream.read())


def save_yaml(
    data: Any,
    file: str,
    default_style: str = '"'
    ) -> None:
    """
    Save data to yaml file.
    """
    with open(file, 'w') as yaml_file:
        yaml.dump(data, yaml_file, Dumper=yaml.RoundTripDumper, default_style=default_style)
