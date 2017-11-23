from pathlib import Path

import yaml

from .config import DataFetcher, PromptFetcher, Seed, GardenerConfig
from .generation import Seed_Manager, Generator

default_values = {
    "config_file_location": "gardener.yml",
    "config_model_file_location": Path(Path(__file__).parent, 'config/prompt_models/gardener_config.yml')
}

class Fields:
    def __init__(self, required: dict=None, default: dict=None):
        self.required = required or dict()
        self.default = default or dict()

def fetch_gardener_config_fields(location: Path)-> Fields:
    # Fetch data from config file
    gardener_config_model = yaml.safe_load(location.read_text())

    default_fields = {}
    required_fields = {}

    for key, item in gardener_config_model['fields'].items():
        if item['required'] and item['required'] is True:
            required_fields[key] = item
        else:
            default_fields[key] = item

    return Fields(
        required=required_fields,
        default=default_fields
    )


def fetch_from_prompt(fields: Fields):
    # Fetch data from prompt
    return PromptFetcher.run(
        required_values=fields.required,
        default_values=fields.default
    )


def get_missing_fields(fields: Fields, data: dict):
    if data:
        missing_fields = Fields()

        for key, value in fields.required.items():
            if key not in data:
                missing_fields.required[key] = value

        for key, value in fields.default.items():
            if key not in data:
                missing_fields.default[key] = value
    else:
        missing_fields = fields

    return missing_fields


def get_gardener_config(config_file_location, cli_data: dict=None)->dict:

    config_file_location = config_file_location or default_values["config_file_location"]

    # Get gardener requirements fields
    gardener_fields = fetch_gardener_config_fields(default_values["config_model_file_location"])

    # Get data from config file
    data_fetcher = DataFetcher(
        required_values=gardener_fields.required,
        default_values=gardener_fields.default
    )
    fetched_data = data_fetcher.get_data(config_file_location) or {}

    # Cross data from file with cli arguments

    if cli_data:
        fetched_data = {**fetched_data, **cli_data}

    # TODO: define check_config_value into a validator service
    if not data_fetcher.check_config_values(fetched_data):
        print("Some information are missing")
        missing_fields = get_missing_fields(gardener_fields, fetched_data)
        fetched_data = fetch_from_prompt(fields=missing_fields)

    return fetched_data


def get_seed_config(gardener_config: dict)->Seed:
    # Get seed required data
    seed = Seed_Manager.find(
        seed_name=gardener_config["seed_name"],
        seed_location=gardener_config["seed_location"]
    )

    seed_config_model = Seed_Manager.get_prompt_requirements(seed)
    if "fields" in gardener_config:
        seed.fields = {**seed.fields, **gardener_config["fields"]}

    Seed_Manager.cross_fields(seed, gardener_config)
    missing_fields = Seed_Manager.get_missing_fields(seed_config_model['fields'], seed)

    # Fetch missing seed fields from prompt

    if len(missing_fields) > 0:
        fields = PromptFetcher.run(
            required_values=missing_fields
        )
        seed.fields = {**seed.fields, **fields}

    return seed


def run(cli_data: dict=None):

    config_file_location = cli_data['config_file_location'] or default_values["config_file_location"]

    fetched_gardener_config = get_gardener_config(Path(config_file_location), cli_data)
    seed = get_seed_config(fetched_gardener_config)

    gardener_config = GardenerConfig()
    for key, value in fetched_gardener_config.items():
        setattr(gardener_config, key, value)

    # Generate step
    generate = Generator()
    generate(
        gardener_config=gardener_config,
        seed=seed
    )
