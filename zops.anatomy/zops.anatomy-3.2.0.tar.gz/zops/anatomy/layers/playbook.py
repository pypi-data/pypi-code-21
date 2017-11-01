from zops.anatomy.layers.feature import AnatomyFeatureRegistry
from zops.anatomy.yaml import yaml_from_file

from collections import OrderedDict


class AnatomyPlaybook(object):
    """
    Describes features and variables to apply in a project tree.
    """

    def __init__(self):
        self.__features = OrderedDict()
        self.__variables = {}

    @classmethod
    def from_file(cls, filename):
        contents = yaml_from_file(filename)
        result = cls.from_contents(contents)
        return result

    @classmethod
    def from_contents(cls, contents):
        result = cls()
        contents = contents.pop('anatomy-playbook', contents)
        use_features = contents.pop('use-features')
        if not isinstance(use_features, dict):
            raise TypeError('Use-features must be a dict not "{}"'.format(use_features.__class__))
        if isinstance(use_features, dict):
            for i_feature_name, i_variables in use_features.items():
                result.__use_feature(i_feature_name)
                result.__set_variable(i_feature_name, i_variables)
        return result

    def __use_feature(self, feature_name):
        feature = AnatomyFeatureRegistry.get(feature_name)
        feature.using_features(self.__features)

    def __set_variable(self, key, value):
        """
        :param str key:
        :param object value:
        """
        assert key not in self.__variables
        self.__variables[key] = value

    def apply(self, directory):
        from zops.anatomy.layers.tree import AnatomyTree
        import os

        tree = AnatomyTree()

        if not os.path.isdir(directory):
            os.makedirs(directory)

        for i_feature_name, i_feature in self.__features.items():
            print('applying anatomy-feature {}'.format(i_feature_name))
            i_feature.apply(tree)

        print('applying anatomy-tree')
        tree.apply(directory, self.__variables)
