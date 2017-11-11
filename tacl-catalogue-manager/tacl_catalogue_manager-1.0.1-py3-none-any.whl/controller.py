from collections import OrderedDict
import configparser
import os.path

from .catalogue import Catalogue


class Controller:

    def __init__(self):
        self._base_path = '.'
        self._groups_path = None
        self._mappings = None

    @property
    def base_path(self):
        """Returns the base path for the loaded control file.

        This path is used as the base for the paths used within the
        control file.

        :rtype: `str`

        """
        return self._base_path

    def generate_catalogues(self, output_base_path):
        """Writes catalogues to `base_path` using the groups and mappings
        defined in the loaded control file.

        :param output_base_path: base path to save catalogue files to
        :type output_base_path: `str`

        """
        # QAZ: handle case when self._groups_path is None.
        # QAZ: handle case when self._mappings is None.
        # QAZ: handle exceptions.
        catalogue = Catalogue()
        groups = self.load_groups(self.groups_path)
        report = []
        for group in groups:
            group_path = os.path.join(self.base_path, group)
            report.extend(catalogue.add_group_file(group_path))
        for (mapping_file, output_file) in self.mappings:
            mapping = self.load_mapping(os.path.join(
                self.base_path, mapping_file))
            output_path = os.path.join(output_base_path, output_file)
            catalogue.save(output_path, mapping)
        return report

    @property
    def groups_path(self):
        """Returns the path to the groups file specified in the loaded control
        file.

        :rtype: `str`

        """
        return self._groups_path

    def load_control(self, path):
        self._base_path = os.path.abspath(os.path.dirname(path))
        config = configparser.ConfigParser()
        config.read(path)
        self._groups_path = config['MERGING']['groups']
        self._mappings = [(input_file, output_file) for input_file, output_file
                          in config['MAPPING'].items()]

    def load_groups(self, path):
        """Returns the contents of `path` as a list of group paths.

        :param path: path to group file
        :type path: `str`
        :rtype: `list` of `str`

        """
        # QAZ: handle exception when there is no file/unreadable file/etc.
        with open(os.path.join(self.base_path, path), encoding='utf-8') as fh:
            groups = [line.strip() for line in fh]
        return groups

    def load_mapping(self, path):
        """Returns the contents of `path` as a mapping object.

        :param path: path to mapping file
        :type path: `str`
        :rtype: `collections.OrderedDict`

        """
        mapping = OrderedDict()
        # QAZ: handle exception when there is no file/unreadable file/etc.
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    group, label = parts
                elif len(parts) == 1:
                    group = parts[0]
                    label = ''
                else:
                    continue
                mapping[group] = label
        return mapping

    @property
    def mappings(self):
        """Returns the mapping file paths and their associated output
        filenames specified in the loaded control file.

        The return value is a list of 2-tuples specifying a mapping
        file path and its output file path.

        :rtype: `list`

        """
        return self._mappings
