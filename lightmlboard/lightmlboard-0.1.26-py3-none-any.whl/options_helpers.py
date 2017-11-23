"""
@file
@brief Defines helpers used in different places of the module.
"""
import importlib
import logging
import os
import sys
import pandas


def read_options(config):
    """
    Reads configuration from a file or a dictionary.
    """
    config_options = {}
    if config is not None:
        if isinstance(config, dict):
            config_options.update(config)
        elif isinstance(config, str) and os.path.exists(config):
            app_log = logging.getLogger("tornado.application")
            app_log.info("[LightMLBoard] read file '{0}'".format(config))
            obj = None
            fname = os.path.splitext(config)[0]
            path, name = os.path.split(fname)
            if path:
                sys.path.append(path)
                mod = importlib.import_module(name)
                del sys.path[-1]
            else:
                mod = importlib.import_module(name)
            for k, v in mod.__dict__.items():
                if isinstance(v, pandas.DataFrame.__class__):
                    obj = v
                    break
            if obj is None:
                raise ValueError(
                    "Unable to read configuration '{0}'.".format(config))
            for k, v in obj.__dict__.items():
                if not k.startswith('_'):
                    config_options[k] = v
        else:
            raise ValueError(
                "Unable to interpret config\ncwd: '{0}'\n{1}".format(os.getcwd(), config))
    return config_options


def read_users(filename):
    """
    Reads users definition.
    """
    df = pandas.read_csv(filename)
    cols = list(sorted(df.columns))
    df = df[cols]
    exp = "login,mail,name,pwd,team".split(",")
    has = list(df.columns)
    if exp != has:
        raise ValueError(
            "Users should be defined in CSV file with columns: {0}, not {1}".format(exp, has))
    users = {}
    for i in range(0, df.shape[0]):
        name, login, mail, pwd, team = (df.loc[i, 'name'], df.loc[i, 'login'],
                                        df.loc[i, 'mail'], df.loc[i, 'pwd'], df.loc[i, 'team'])
        if login in users:
            raise ValueError("Duplicated user: '{0}'.".format(login))
        users[login] = dict(mail=mail, pwd=pwd, team=team,
                            name=name, login=login)
    return users
