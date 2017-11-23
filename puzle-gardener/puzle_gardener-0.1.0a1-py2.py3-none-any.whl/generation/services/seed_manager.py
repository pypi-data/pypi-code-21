from pathlib import Path

import os

import yaml

from src.config.models.field import Field
from src.config.models.seed import Seed

class Seed_Manager:

    @staticmethod
    def find(seed_name:str, seed_location: Path)-> Seed:
        if seed_name == "":
            raise ValueError("The seed name must exist")

        if seed_location == "":
            seed_location = "./seeds"

        abspath = Path(os.path.join(seed_location, seed_name))
        print("seed path: {0}", abspath)
        if not abspath.is_dir():
            raise FileNotFoundError("Cannot find the following seed : ", abspath)
        else:
            seed_location = abspath

        return Seed(
            name=seed_name,
            location=seed_location
        )

    @staticmethod
    def get_prompt_requirements(seed: Seed, config_file_path: Path=Path('puzle-seed.yml'))->dict:
        config_file = Path(seed.location, config_file_path)
        result = None
        if config_file.exists() and config_file.is_file():
            result = yaml.safe_load(config_file.read_text())
        return result

    @staticmethod
    def set_fields(seed: Seed, config_model: dict)->Seed:
        if config_model is not None:
            for key, items in config_model['fields'].items():
                field = Field(
                    label=key,
                    required=items['required'] or False,
                    default=items['default']or "",
                    user_text=items['text']or "",
                )
                seed.fields.append(field)
        return seed

    @staticmethod
    def cross_fields(seed: Seed, config: dict)->Seed:
        for field in seed.fields:
            if field in config:
                seed.fields[field] = config[field]

        return seed

    @staticmethod
    def get_missing_fields(required_fields:dict, seed: Seed)->dict:
        result = {}
        for key, value in required_fields.items():
            if key not in seed.fields and value["required"] and value["required"] == True:
                result[key] = value

        return result
