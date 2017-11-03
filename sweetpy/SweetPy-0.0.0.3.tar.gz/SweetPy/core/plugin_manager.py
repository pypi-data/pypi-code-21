from ..common.func_helper import FuncHelper
import sys

class PluginManager(object):

    classes = {}
    @staticmethod
    def get_instance_by_plugin_name(plugin_name):
        _class_ = PluginManager.classes.get(plugin_name,None)
        if not _class_:
            _class_ = PluginManager.get_plugin_class_by_plugin_name(plugin_name)
            if not _class_:
                return None
            else:
                PluginManager.classes[plugin_name] = _class_
                return _class_()
        return _class_()

    @staticmethod
    def get_plugin_class_by_plugin_name(plugin_name):
        _path = FuncHelper.get_file_path_by_full_path(__file__)
        _path = _path.replace('/core','/') + 'plugin/'
        sys.path.append(_path)
        filename = _path + plugin_name + '.py'
        if FuncHelper.check_file_exists(filename):
            class_name_arr = FuncHelper.get_all_classname_by_file_path_name(filename,'object')
            if class_name_arr:
                plugin = __import__(plugin_name)
                plugin_class = getattr(plugin, class_name_arr[0])
                return plugin_class
        return None





