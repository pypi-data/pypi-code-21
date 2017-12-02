import yaml
import os

__all__ = ["Settings"]


class Settings(object):
    """Class for parsing and representate settings
    """

    class YAMLParseException(Exception):
        pass

    def __init__(self):
        yaml.add_constructor(
            "tag:yaml.org,2002:map",
            self.dot_notated_dict.yaml_constructor
        )

    class dot_notated_dict(dict):
        def __getattr__(self, item):
            r = self.get(item)
            if r is not None:
                return r
            return super(Settings.dot_notated_dict, self).__getattribute__(item)

        @classmethod
        def yaml_constructor(cls, loader, node):
            values = loader.construct_mapping(node, deep=True)
            return Settings.dot_notated_dict(values)

    def update_from_yaml(self, yaml_filename: str):
        """
        :param yaml_filename
        :type yaml_filename: str
        """
        yaml_str = open(yaml_filename).read()
        yaml_dict = yaml.load(yaml_str)
        if not isinstance(yaml_dict, self.dot_notated_dict):
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
