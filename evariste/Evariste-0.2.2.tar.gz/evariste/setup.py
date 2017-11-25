# Copyright Louis Paternault 2015-2017
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Parse setup file."""

import collections
import configparser

from evariste import utils
from evariste.errors import EvaristeError

def Options(*args, **kwargs):
    """Return a :class:`collections.defaultdict` object, default being `None`.
    """
    # pylint: disable=invalid-name
    return collections.defaultdict(lambda: None, *args, **kwargs)

def Sections(dictionary=None):
    """Return a :class:`collections.defaultdict` object, default being `Options`
    """
    # pylint: disable=invalid-name
    if dictionary is None:
        dictionary = {}
    return collections.defaultdict(
        Options,
        {key: Options(value) for (key, value) in dictionary.items()}
        )

class Setup:
    """Representation ef Evariste setup."""

    def __init__(self, dictionary=None):
        if dictionary is None:
            dictionary = {}
        self.dict = Sections(dictionary)

    def __iter__(self):
        yield from self.dict

    def __getitem__(self, value):
        return self.dict[value]

    def __str__(self):
        return "{{{}}}".format(", ".join([
            "{}: {}".format(key, value)
            for key, value
            in self.dict.items()
            ]))

    def __eq__(self, other):
        for section in set(self.keys()) | set(other.keys()):
            for option in set(self[section].keys()) | set(other[section].keys()):
                if self[section][option] != other[section][option]:
                    return False
        return True

    def fill_blanks(self, dictionary):
        """Fill unset self options with argument.

        Returns ``self`` for convenience.
        """
        for section in dictionary:
            if section in self.dict:
                for option in dictionary[section]:
                    if option not in self.dict[section]:
                        self.dict[section][option] = dictionary[section][option]
            else:
                self.dict[section] = Options(dictionary[section])
        return self

    def update(self, other, *, extend_list=False):
        """Update setup, with another setup or dict object.

        Similar to :meth:`dict.update`.

        :param boolean extend_list: If `True` and both values are lists,
            extend the first one with the second one.

        Return `self` for convenience.
        """
        for section in other:
            for option in other[section]:
                if (
                        extend_list
                        and
                        isinstance(self.dict[section][option], list)
                        and
                        isinstance(other[section][option], list)
                    ):
                    self.dict[section][option].extend(other[section][option])
                else:
                    self.dict[section][option] = other[section][option]
        return self


    @classmethod
    def from_file(cls, filename):
        """Parse configuration file ``filename``."""
        with open(filename, encoding='utf8') as file:
            return cls.from_string(file.read())

    @classmethod
    def from_string(cls, string):
        """Parse ``string`` as the content of a configuration file."""
        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(string)
        return cls.from_config(config)

    @classmethod
    def from_config(cls, setup):
        """Parse ``setup`` as a :class:`configparser.ConfigParser` object."""
        return cls.from_dict(utils.DeepDict.from_configparser(setup))

    @classmethod
    def from_dict(cls, dictionary):
        """Return a setup object, from a dictionary."""
        return cls(dictionary)

    def keys(self):
        """Return a new view of the setup’s keys"""
        return self.dict.keys()

    def pprint(self):
        """Pretty print of the object."""
        from pprint import pprint
        pprint(self.dict)

    @property
    def __dict__(self):
        """Return self, as a :class:`dict` of :class:`dict`."""
        dictionary = {}
        for section in self:
            dictionary[section] = dict(self[section])
        return dictionary

    def copy(self):
        """Return a copy of this object."""
        return self.__class__.from_dict(vars(self))

    def items(self):
        """Iterate over (key, value) pairs, as 2-tuples."""
        yield from self.dict.items()


class SetupError(EvaristeError):
    """Error in setup file."""

    pass
