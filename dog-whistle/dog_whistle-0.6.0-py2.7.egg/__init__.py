# python 2 and 3 support
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from six import u

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

import os
import re
import copy

logging.getLogger(__name__).addHandler(NullHandler())
log = logging.getLogger(__name__)

# the max length of a message
MAX_LENGTH = 50


def dw_analyze(path):
    """Used to analyze a project structure and output the recommended settings dictionary to be used when used in practice. Run this method, then add the resulting output to your project

    :param str path: The folder path to analyze"""
    global MAX_LENGTH
    log.debug("dw_analyze")

    def walk(path):
        """Walks a directory, yields filepaths"""
        for dirName, subdirList, fileList in os.walk(path):
            log.debug('Found directory: %s' % dirName)
            for fname in fileList:
                if not fname.startswith('.'):
                    log.debug('File: \t%s' % fname)
                    val = os.path.join(dirName, fname)
                    yield val

    # compile regexes
    regex_lf = re.compile('(LogFactory.get_instance)')
    regex_log = re.compile('\.(?:info|warn|warning|error|critical)\(((["\']).*?\\2)')
    regex_inc = re.compile('\.(?:info|warn|warning|error|critical)\((.*(?:\+|\.format\().*).*\)')
    regex_com = re.compile('((["\']).*?\\2),')
    found_lf = False
    line_cache = []
    unknown_cache = []

    # walk the filesystem, gather valid/invalid lines
    for file in walk(path):
        log.debug("checking file " + file)

        with open(file, 'r') as f:
            line_number = 1

            for line in f:
                results = regex_lf.findall(line)
                if len(results) > 0:
                    log.debug("found log factory use")
                    found_lf = True

                matches = regex_log.findall(line)
                if len(matches) > 0:
                    if len(regex_inc.findall(line)) == 0:
                        log.debug("found valid line")
                        line_cache.append((file, str(line_number), line.strip(),
                                           matches[0]))
                    else:
                        log.debug("found unknown line")
                        unknown_cache.append((file, str(line_number),
                                              line.strip(), matches[0]))

                line_number += 1


    if found_lf:
        log.debug("LogFactory in use")

        # print valid lines
        if len(line_cache) > 0:
            print("")
            print("Valid Lines")
            print("-----------")
            curr_file = None
            for item in line_cache:
                if curr_file != item[0]:
                    curr_file = item[0]
                    print(u(item[0]))
                print('  ', item[1], ':', u(item[2]))
        else:
            print("You don't appear to have any logger statements.")

        # print lines that need to be fixed
        if len(unknown_cache) > 0:
            print("")
            print("Invalid Lines")
            print("-------------")
            print("")
            print("<<<<<<<<<< YOU MUST FIX THESE BEFORE USING THE DOGWHISTLE LIBRARY >>>>>>>>>>>")
            print("")
            curr_file = None
            for item in unknown_cache:
                if curr_file != item[0]:
                    curr_file = item[0]
                    print(u(item[0]))
                print('  ', item[1], ':', u(item[2]))

        # messy but it makes a really nice string in the end
        recommended_str = '''
dw_dict = {
    'name': '<my_project>',
    'tags': [
        # high level tags that everything in your app will have
        'item:descriptor'
    ],
    'metrics': {
        # By default, everything is a counter using the concatentated log string
        # the 'counters' key is NOT required, it is shown here for illustration
        'counters': [
            # datadog metrics that will use ++'''

        for item in line_cache:
            recommended_str += '\n            (' + item[3][0] + ', "' + _ddify(item[3][0], False) + '"),'

        recommended_str += '''
        ],
        # datadog metrics that have a predefined value like `51`
        # These metrics override any 'counter' with the same key,
        # and are shown here for illustration purposes only
        'gauges': [
            '''

        for item in line_cache:
            if len(regex_com.findall(item[2])) > 0:
                recommended_str += '\n            (' + item[3][0] + ', "' + _ddify(item[3][0], False) + '", "<extras.key.path>"),'

        recommended_str += '''
        ]
    },
    'options': {
        # use statsd for local testing, see docs
        'statsd_host': 'localhost',
        'statsd_port': 8125,
        'local': True,
    },

}

Ensure the above dictionary is passed into `dw_config()`
'''

        print("")
        print("Auto-Generated Template Settings")
        print("--------------------------------")
        print(recommended_str)
    else:
        print("It does not appear like the LogFactory is used in this project")


def dw_config(settings):
    """Set up the datadog callback integration

    :param dict settings: The settings dict containing the `dw_analyze()` configuration
    :raises: :class:`Exception` if configuration is missing"""
    # import globals
    global _dw_configuration
    global _dw_init
    global _dw_stats
    global _dw_local

    log.debug("dw_config called")

    if not _dw_init:
        _dw_configuration = settings
        log.debug("init settings " + str(_dw_configuration))

        # check configuration validity
        if 'name' not in _dw_configuration:
            log.error("Unknown application name")
            raise Exception("'name' key required in dog_whistle config")

        if 'options' not in _dw_configuration:
            log.debug("no options provided")
            _dw_configuration['options'] = {}

        if 'metrics' not in _dw_configuration:
            log.debug("no metrics provided")
            _dw_configuration['metrics'] = {
                'counters': [],
                'gauges': []
            }
        if 'tags' not in _dw_configuration:
            log.debug("no tags provided")
            _dw_configuration['tags'] = []

        if 'allow_extra_tags' not in _dw_configuration:
            log.debug("defaulting to no extra tags")
            _dw_configuration['allow_extra_tags'] = False

        # configure local testing vs with datadog
        if 'local' in _dw_configuration['options'] and _dw_configuration['options']['local'] == True:
            from statsd import StatsClient

            if 'statsd_host' not in _dw_configuration['options'] or \
                    'statsd_port' not in _dw_configuration['options']:
                log.error("Unknown statsd config for local setup")
                raise Exception("Unknown statsd config for local setup")

            statsd = StatsClient(_dw_configuration['options']['statsd_host'],
                                 _dw_configuration['options']['statsd_port'])
            _dw_stats = statsd
            _dw_stats.increment = statsd.incr
            _dw_local = True
        else:
            from datadog import initialize, statsd

            if 'statsd_host' not in _dw_configuration['options'] or \
                    'statsd_port' not in _dw_configuration['options']:
                log.error("Unknown statsd config for DataDog setup")
                raise Exception("Unknown statsd config for DataDog setup")

            initialize(**_dw_configuration['options'])
            _dw_stats = statsd

        # generate override mappings
        _dw_configuration['metrics']['c_mapper'] = {}
        _dw_configuration['metrics']['g_mapper'] = {}

        if 'counters' in _dw_configuration['metrics']:
            for item in _dw_configuration['metrics']['counters']:
                _dw_configuration['metrics']['c_mapper'][item[0]] = item[1]
            del _dw_configuration['metrics']['counters']

        if 'gauges' in _dw_configuration['metrics']:
            for item in _dw_configuration['metrics']['gauges']:
                # all gauges are mapped into a list to be looped over
                _dw_configuration['metrics']['g_mapper'][item[0]] = []
                if isinstance(item[1], list):
                    # we have a multi gauge setup
                    log.debug("received multi gauge setup")
                    _dw_configuration['metrics']['g_mapper'][item[0]] = []
                    for part in item[1]:
                        obj_part = {
                            'name': part[0],
                            'value': part[1],
                        }
                        _dw_configuration['metrics']['g_mapper'][item[0]].append(obj_part)
                else:
                    log.debug("received single gauge setup")
                    _dw_configuration['metrics']['g_mapper'][item[0]].append({
                        'name': item[1],
                        'value': item[2]
                    })
            del _dw_configuration['metrics']['gauges']

        _dw_init = True
    else:
        log.warning("tried to configure DogWhistle more than once within app")


def dw_callback(message, extras):
    """The actual callback method passed to the logger

    :param str message: The log message
    :param dict extras: The extras dictionary from the logger"""
    # import globals
    global _dw_configuration
    global _dw_init
    log.debug("dw_callback called")

    if _dw_init:
        log.debug("inside callback " + message + " " + str(extras))
        # set gauge metric
        if message in _dw_configuration['metrics']['g_mapper']:
            # loop through any gauges for this log statement
            log.debug("executing gauge log to datadog")
            for item in _dw_configuration['metrics']['g_mapper'][message]:
                value = _get_value(extras, item['value'])
                if value is None:
                    log.warning("Could not find key " + item['value'] + " inside extras")
                else:
                    the_msg = _ddify(item['name'])

                    if 'tags' in extras and _dw_configuration['allow_extra_tags']:
                        _gauge(the_msg, value, tags=_dw_configuration['tags'] + extras['tags'])
                    else:
                        _gauge(the_msg, value, tags=_dw_configuration['tags'])
        # increment counter metric
        else:
            if message in _dw_configuration['metrics']['c_mapper']:
                # we have a direct mapping
                the_msg = _ddify(_dw_configuration['metrics']['c_mapper'][message])
            else:
                the_msg = _ddify(message)

            if 'tags' in extras and _dw_configuration['allow_extra_tags']:
                _increment(the_msg, tags=_dw_configuration['tags'] + extras['tags'])
            else:
                _increment(the_msg, tags=_dw_configuration['tags'])
    else:
        log.warning("Tried to increment attribute before configuration")


# --------------- HELPER METHODS ------------------

def _ddify(message, prepend=True):
    """Datadogifys and normalizes a log message into a datadog key

    :param str message: The message to concatentate
    :param bool prepend: prepend the application name to the metric
    :returns: the final datado string result
    """
    global MAX_LENGTH
    global _dw_configuration
    if prepend:
        message = '{}.{}'.format(_dw_configuration['name'], message)
    message = re.sub(r'[^0-9a-zA-Z_. ]', '', message)
    return message.rstrip('.').lower().replace(' ', '_').replace('"', '')[:MAX_LENGTH]


def _get_value(item, key):
    """Grabs a nested value within a dict

    :param dict item: the dictionary
    :param str key: the nested key to find
    :returns: the value if found, otherwise None
    """
    keys = key.split('.', 1)

    if isinstance(item, dict):
        if len(keys) == 2:
            if keys[0] in item:
                return _get_value(item[keys[0]], keys[1])
        elif keys[0] in item:
            return copy.deepcopy(item[keys[0]])


def _increment(name, tags):
    """Increments a counter

    :param str name: The name of the stats
    :param list tag: A list of tags"""
    global _dw_stats
    global _dw_local

    tags = _normalize_tags(tags)

    if _dw_local:
        _dw_stats.increment(stat=name)
    else:
        _dw_stats.increment(metric=name, tags=tags)

    log.info("incremented counter " + name)


def _gauge(name, value, tags):
    """Increments a gauge

    :param str name: The name of the stats
    :param int value: The value of the gauge
    :param list tag: A list of tags"""
    global _dw_stats
    global _dw_local

    tags = _normalize_tags(tags)

    if _dw_local:
        _dw_stats.gauge(stat=name, value=value)
    else:
        _dw_stats.gauge(metric=name, value=value, tags=tags)

    log.info("metric guage " + name)

def _normalize_tags(tags):
    return [t.lower() for t in tags]

def _get_dw_stats():
    """Returns the statsd implementation in use"""
    global _dw_stats
    return _dw_stats

def _get_config():
    """Returns the current configuration of the module"""
    global _dw_configuration
    return _dw_configuration

def _reset():
    """Resets the module configuration to the defaults"""
    global _dw_stats
    global _dw_local
    global _dw_configuration
    global _dw_init

    _dw_configuration = None
    _dw_init = False
    _dw_stats = None
    _dw_local = False

# set the initial global configs
_reset()
