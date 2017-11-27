# -*- coding: utf-8 -*-
import os
import sys


engine_configs = None

def get_engine_configs():
    global engine_configs

    if sys.version_info[0] == 2:
        import ConfigParser as configparser
    else:
        import configparser

    # Check configuration files
    Config = configparser.ConfigParser()
    if len(Config.read(".airbridgerc")) == 0 and \
        len(Config.read(os.path.expanduser("~/.airbridgerc"))) == 0:
        raise Exception("No .airbridgerc file.")

    if engine_configs is not None:
        return engine_configs

    def ConfigSectionMap(section):
        dict1 = {}
        options = Config.options(section)
        for option in options:
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    engine_configs = ConfigSectionMap('ENGINE')

    if 'USE_AIRBRIDGE_LOCAL_DB' in os.environ:
        engine_configs = ConfigSectionMap('ENGINE_LOCAL')

    return engine_configs
