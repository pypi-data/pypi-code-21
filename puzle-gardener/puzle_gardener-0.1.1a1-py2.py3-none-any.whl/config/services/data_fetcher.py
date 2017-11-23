# Data Init
from pathlib import Path
import yaml
import sys

class DataFetcher:

    def __init__(self, required_values: dict, default_values: dict):
        self.required_values = required_values.copy()
        self.default_values = default_values.copy()

    def set_default_value(self, data: dict)-> dict:

        result = {}
        for key, item in self.default_values:
            result[key] = item.default

        result.update(data)
        return result

    def check_config_values(self, config: dict)-> bool:
        return config and all(key in config for key in self.required_values)

    @classmethod
    def get_data(cls, config_file_path: Path = Path(sys.argv[0], 'gardener.yml'))->dict:
        result = None
        if config_file_path.is_file():
            data = config_file_path.read_text()
            result = yaml.safe_load(data)

        return result
