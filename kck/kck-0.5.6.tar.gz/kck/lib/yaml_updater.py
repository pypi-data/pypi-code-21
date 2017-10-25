import os

from .config import kck_config_lookup
from .kck_updater import KCKUpdater
from .yaml_reader import YAMLReader

class KCKYamlUpdater(KCKUpdater, YAMLReader):

    def __init__(self, yaml_filepath):

        self.filepath = yaml_filepath

        self._proc_updater_yaml()

    @classmethod
    def register_updaters(cls, data_obj):
        """register all yaml-based updaters in the updaters dir"""
        # from kck.lib.kck_data import KCKData
        # data_obj = KCKData.get_instance()
        def fnfilter(filepath):
            # print("fp: {}, fpl: {}".format(filepath, filepath[-3:]))
            if filepath[-4:] == ".yml":
                return True
            return False

        def proc_primer_yaml(filepath):
            data_obj.register_updater(
                os.path.basename(filepath)[:-4],
                KCKYamlUpdater(filepath)
            )

        cls.proc_files_in_dirpath(
            cls.make_relpath_absolute(kck_config_lookup("kck", "updaters_dirpath")),
            fnfilter,
            proc_primer_yaml
        )


    def _proc_updater_yaml(self):
        # print("yfp: {}".format(self.filepath))
        u = self.read_yaml(self.filepath)

        # print("u: {}".format(u))

        # the key is the same as the yaml file (minus the .yml)
        self.name = [os.path.basename(self.filepath)[:-4]]

        self.database = u["database"]

        self.parameters = u["parameters"]
        # print("parameters: {}".format(self.parameters))

        # self.expire = datetime.timedelta(seconds=u["expire_seconds"])

        self.query_template = u["query"]["template"]
