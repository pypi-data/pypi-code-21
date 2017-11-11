from collections import OrderedDict
import csv
import os.path


class Catalogue:

    def __init__(self):
        self._data = OrderedDict()

    def add_group_file(self, path):
        """Merges the contents of `path` into the catalogue.

        Returns a list of messages indicating works removed from
        groups.

        :param path: path to group file
        :type path: `str`
        :rtype: `list`

        """
        report = []
        group = os.path.basename(path)
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                work = line.strip()
                if work in self._data:
                    report.append('{} removed from {}'.format(work, group))
                else:
                    self._data[work] = group
        return report

    @property
    def data(self):
        return self._data

    def save(self, path, mapping):
        """Saves this catalogue's data to `path`, with the labels and ordering
        specified in `mapping`.

        :param path: file path to save catalogue data to
        :type path: `str`
        :param mapping: ordered mapping of group names to labels
        :type mapping: `collections.OrderedDict`

        """
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            writer = csv.writer(fh, delimiter=' ')
            # This is an inefficient approach, but the number of
            # values in the innermost loop will never be enough for
            # performance to matter.
            for mapping_group, label in mapping.items():
                for work, original_group in self._data.items():
                    if mapping_group == original_group:
                        writer.writerow([work, label])
