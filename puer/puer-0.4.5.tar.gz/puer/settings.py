import yaml
import os

__all__ = ["Settings"]


class Settings(object):
    """Class for parsing and representate settings
    """

    class YAMLParseException(Exception):
        pass

    def update_from_yaml(self, yaml_filename: str):
        """
        :param yaml_filename
        :type yaml_filename: str
        """
        yaml_str = open(yaml_filename).read()
        yaml_dict = yaml.load(yaml_str)
        if not isinstance(yaml_dict, dict):
            raise Settings.YAMLParseException("YAML must be dict")
        self.__dict__.update(yaml_dict)
        if "$import" in yaml_dict:
            for import_file in yaml_dict["$import"]:
                try:
                    self.update_from_yaml(os.path.join(os.path.dirname(yaml_filename), import_file))
                except FileNotFoundError:
                    print("%s, imported from %s not found" % (import_file, yaml_filename))

    @staticmethod
    def from_yaml(yaml_filename: str):
        settings = Settings()
        settings.update_from_yaml(yaml_filename)
        return settings
