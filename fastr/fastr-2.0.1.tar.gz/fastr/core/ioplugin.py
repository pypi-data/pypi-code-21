# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the manager class for IOPlugins and the
base class for all IOPlugins
"""

import argparse
import json
import os
import urlparse as up

if __name__ == '__main__':
    FASTR_LOG_TYPE = 'console'

import fastr
from fastr.core.baseplugin import Plugin
from fastr.core.datatypemanager import typelist
from fastr.core.pluginmanager import PluginSubManager
from fastr.core.tool import Tool
from fastr.core.version import Version
import fastr.data.url as urltools
from fastr.datatypes import URLType, TypeGroup
import fastr.exceptions as exceptions
from abc import abstractproperty
from abc import ABCMeta


class IOPluginManager(PluginSubManager):
    """
    A mapping containing the IOPlugins known to this system
    """

    def __init__(self):
        """
        Create the IOPluginManager and populate it.

        :return: newly created IOPluginManager
        """
        super(IOPluginManager, self).__init__(parent=fastr.plugin_manager,
                                              plugin_class=IOPlugin)
        self._key_map = {}

    def cleanup(self):
        """
        Cleanup all plugins, this closes files, connections and other things
        that could be left dangling otherwise.
        """
        for ioplugin in self.values():
            ioplugin.cleanup()

    def __keytransform__(self, key):
        try:
            return self._key_map[key]
        except KeyError:
            self._key_map.clear()
            for id_, value in self.data.items():
                if isinstance(value.scheme, tuple):
                    for scheme in value.scheme:
                        self._key_map[scheme] = id_
                else:
                    self._key_map[value.scheme] = id_

            return self._key_map[key]

    def __iter__(self):
        for value in self.data.values():
            if isinstance(value.scheme, tuple):
                for scheme in value.scheme:
                    yield scheme
            else:
                yield value.scheme

    def _print_key(self, key):
        """
        Get a printable string for the IOPlugin key

        :param key: key to get the printable version for
        :return: printable version of the key
        :rtype: str
        """
        return self[key].status.value, '{}://'.format(key)

    def expand_url(self, url):
        """
        Expand the url by filling the wildcards. This function checks the url scheme
        and uses the expand function of the correct IOPlugin.

        :param str url: url to expand
        :return: list of urls
        :rtype: list of str
        """
        parsed_url = up.urlparse(url)
        return self[parsed_url.scheme].expand_url(url)

    def pull_source_data(self, url, outdir, sample_id, datatype=None):
        """
        Retrieve data from an external source. This function checks the url scheme and
        selects the correct IOPlugin to retrieve the data.

        :param url: url to pull
        :param str outdir: the directory to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        :return: None
        """
        parsed_url = up.urlparse(url)
        return self[parsed_url.scheme].pull_source_data(url, outdir, sample_id, datatype)

    def push_sink_data(self, inpath, outurl, datatype=None):
        """
        Send data to an external source. This function checks the url scheme and
        selects the correct IOPlugin to retrieve the data.

        :param str inpath: the path of the data to be pushed
        :param str outurl: the url to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        """
        parsed_url = up.urlparse(outurl)
        return self[parsed_url.scheme].push_sink_data(inpath=inpath,
                                                      outurl=outurl,
                                                      datatype=datatype)

    def put_url(self, inpath, outurl):
        """
        Put the files to the external data store.

        :param inpath: path to the local data
        :param outurl: url to where to store the data in the external data store.
        """
        parsed_url = up.urlparse(outurl)
        return self[parsed_url.scheme].put_url(inpath, outurl)

    def url_to_path(self, url):
        """
        Retrieve the path for a given url

        :param str url: the url to parse
        :return: the path corresponding to the input url
        :rtype: str
        """
        parsed_url = up.urlparse(url)
        return self[parsed_url.scheme].url_to_path(url)

    @staticmethod
    def register_url_scheme(scheme):
        """
        Register a custom scheme to behave http like. This is needed to parse
        all things properly with urlparse.

        :param scheme: the scheme to register
        """
        for method in [s for s in dir(up) if s.startswith('uses_')]:
            if scheme not in getattr(up, method):
                getattr(up, method).append(scheme)

    def populate(self):
        """
        Populate the IOPlugins manager. After the default directory scan, add
        the vfs IOPlugin and create the Tools for the IOPlugins
        """
        super(IOPluginManager, self).populate()

    @staticmethod
    def create_ioplugin_tool():
        """
        Create the tools which handles sinks and sources. The command of this tool is the main of core.ioplugin.
        """
        # First create the Enum for the behaviour input
        fastr.typelist.create_enumtype('__ioplugin__behaviour__Enum__', ('source', 'sink'))

        if ('fastr', 'Source', '1.0') not in fastr.toollist:
            source_tool = Tool()
            source_tool.id = 'Source'
            source_tool.name = source_tool.id
            source_tool.version = Version('1.0')
            source_tool.namespace = 'fastr'
            source_tool.node_class = 'Node'
            source_tool.filename = __file__
            source_tool.tests = []
            source_tool._target = None
            source_tool.command = {'authors': ['fastr devs'],
                                   'description': 'Source Tool: tool to handle SourceNode operation.',
                                   'targets': [{'os': '*', 'arch': '*', 'bin': 'ioplugin.py', 'interpreter': 'python', 'paths': './', 'module': None}],
                                   'url': 'http://www.bigr.nl/fastr',
                                   'version': Version('1.0')}

            input_params = [{'id': 'input',
                             'name': 'input',
                             'description': 'The data to be retrieved by the SourceNode',
                             'datatype': 'String',
                             'prefix': '--input',
                             'repeat_prefix': False,
                             'cardinality': '1-*',
                             'required': True,
                             'hidden': True},
                            {'id': 'behaviour',
                             'name': 'behaviour',
                             'enum': ('source', 'sink'),
                             'prefix': '--behaviour',
                             'repeat_prefix': False,
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'datatype',
                             'name': 'datatype',
                             'datatype': 'String',
                             'prefix': '--datatype',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'targetdir',
                             'name': 'targetdir',
                             'description': 'The location to store the result',
                             'datatype': 'Directory',
                             'prefix': '--output',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'sample_id',
                             'name': 'sample_id',
                             'description': 'The sample id for the SourceJob that is run',
                             'datatype': 'String',
                             'prefix': '--sample_id',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True}]

            output_params = [{'id': 'output',
                              'name': 'The output urls in vfs scheme',
                              'description': '',
                              'datatype': 'AnyType',
                              'cardinality': 'unknown',
                              'automatic': True,
                              'location': '^__IOPLUGIN_OUT__=(.*)$',
                              'method': 'json'}]

            interface = {'inputs': input_params, 'outputs': output_params}
            source_tool.interface = fastr.interfaces['FastrInterface'](id_='source-interface', document=interface)

            # Register source tool with the ToolManager
            fastr.toollist[source_tool.namespace, source_tool.id, source_tool.version] = source_tool

        if ('fastr', 'Sink', '1.0') not in fastr.toollist:
            sink_tool = Tool()
            sink_tool.id = 'Sink'
            sink_tool.name = sink_tool.id
            sink_tool.version = Version('1.0')
            sink_tool.namespace = 'fastr'
            sink_tool.node_class = 'Node'
            sink_tool.filename = __file__
            sink_tool.tests = []
            sink_tool._target = None
            sink_tool.command = {'authors': ['fastr devs'],
                                 'description': 'Sink Tool: tool to handle Sink Node operation.',
                                 'targets': [{'os': '*', 'arch': '*', 'bin': 'ioplugin.py', 'interpreter': 'python', 'paths': './', 'module': None}],
                                 'url': 'http://www.bigr.nl/fastr',
                                 'version': Version('1.0')}

            input_params = [{'id': 'input',
                             'name': 'The url to process (can also be a list)',
                             'description': 'The data to be store by the SinkNode',
                             'datatype': 'AnyType',
                             'prefix': '--input',
                             'cardinality': '1-*',
                             'required': True, },
                            {'id': 'behaviour',
                             'name': 'behaviour',
                             'enum': ('source', 'sink'),
                             'prefix': '--behaviour',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'output',
                             'name': 'output',
                             'datatype': 'String',
                             'prefix': '--output',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'datatype',
                             'name': 'datatype',
                             'datatype': 'String',
                             'prefix': '--datatype',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            ]

            output_params = []

            interface = {'inputs': input_params, 'outputs': output_params}
            sink_tool.interface = fastr.interfaces['FastrInterface'](id_='source-interface', document=interface)

            # Register sink tool with the ToolManager
            fastr.toollist[sink_tool.namespace, sink_tool.id, sink_tool.version] = sink_tool


class IOPlugin(Plugin):
    """
    :py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` are used for data import
    and export for the sources and sinks. The main use of the
    :py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` is during execution (see
    :ref:`Execution <manual_execution>`). The :py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>`
    can be accessed via ``fastr.ioplugins``, but generally there should be no need
    for direct interaction with these objects. The use of is mainly via the URL
    used to specify source and sink data.
    """
    __metaclass__ = ABCMeta
    _instantiate = True

    def __init__(self):
        """
        Initialization for the IOPlugin

        :return: newly created IOPlugin
        """
        super(IOPlugin, self).__init__()
        self._results = {}

    @abstractproperty
    def scheme(self):
        """
        ``(abstract)`` This abstract property is to be overwritten by a subclass to indicate
        the url scheme associated with the IOPlugin.
        """
        raise exceptions.FastrNotImplementedError("IOPlugin scheme is not set")

    def url_to_path(self, url):
        """
        ``(abstract)`` Get the path to a file from a url.

        :param str url: the url to retrieve the path for
        :return: the corresponding path
        :rtype: str
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for working with urls'.format(self.scheme))

    def fetch_url(self, inurl, outfile):
        """
        ``(abstract)``  Fetch a file from an external data source.

        :param inurl: url to the item in the data store
        :param outpath: path where to store the fetch data locally
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct url data retrieval'.format(self.scheme))

    def fetch_value(self, inurl):
        """
        ``(abstract)``  Fetch a value from an external data source.

        :param inurl: the url of the value to retrieve
        :return: the fetched value
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct value data retrieval'.format(self.scheme))

    def put_url(self, inpath, outurl):
        """
        ``(abstract)`` Put the files to the external data store.

        :param inpath: path to the local data
        :param outurl: url to where to store the data in the external data store.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct url data storage'.format(self.scheme))

    def put_value(self, value, outurl):
        """
        ``(abstract)`` Put the files to the external data store.

        :param value: the value to store
        :param outurl: url to where to store the data in the external data store.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct value data storage'.format(self.scheme))

    def path_to_url(self, path, mountpoint=None):
        """
        ``(abstract)`` Construct an url from a given mount point and a relative
        path to the mount point.

        :param str path: the path to determine the url for
        :param mountpoint: the mount point to use, will be automatically
                           detected if None is given
        :type mountpoint: str or None
        :return: url matching the path
        :rtype: str
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for working with urls'.format(self.scheme))

    def setup(self, *args, **kwargs):
        """
        ``(abstract)`` Setup before data transfer. This can be any function
        that needs to be used to prepare the plugin for data transfer.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument,no-self-use
        pass

    def cleanup(self):
        """
        ``(abstract)`` Clean up the IOPlugin. This is to do things like
        closing files or connections. Will be called when the plugin is no
        longer required.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument,no-self-use
        pass

    def expand_url(self, url):
        """
        ``(abstract)`` Expand an URL. This allows a source to collect multiple
        samples from a single url. The URL will have a wildcard or point to
        something with info and multiple urls will be returned.

        :param str url: url to expand
        :return: the resulting url(s), a tuple if multiple, otherwise a str
        :rtype: str or tuple of str
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument,no-self-use
        return url

    @staticmethod
    def isurl(string):
        """
        Test if given string is an url.

        :param str string: string to test
        :return: ``True`` if the string is an url, ``False`` otherwise
        :rtype: bool
        """
        parsed_url = up.urlparse(str(string))
        return parsed_url.scheme != ''

    @staticmethod
    def print_result(result):
        """
        Print the result of the IOPlugin to stdout to be picked up by the tool

        :param result: value to print as a result
        :return: None
        """
        print('__IOPLUGIN_OUT__={}'.format(json.dumps(result)))

    def pull_source_data(self, inurl, outdir, sample_id, datatype=None):
        """
        Transfer the source data from inurl to be available in outdir.

        :param str inurl: the input url to fetch data from
        :param str outdir: the directory to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        :return: None
        """
        results = {}
        self.setup()

        # First expand the URL
        valuelist = self.expand_url(inurl)

        fastr.log.debug('[{}] pulling sample {} with value {} and datatype {}'.format(self.scheme, sample_id, inurl, datatype))

        if isinstance(valuelist, tuple):
            # We expanded the URL, so now process each new value/URL seperately
            if len(valuelist) == 0:
                raise exceptions.FastrValueError(('No data found when expanding'
                                                  ' URL {}, this probably means '
                                                  'the URL is not correct.').format(inurl))
            for cardinality_nr, (sub_sample_id, value) in enumerate(valuelist):
                if sub_sample_id is None:
                    fastr.log.debug('Changing sub sample id from None to {}'.format(sub_sample_id))
                    sub_sample_id = '{}_{}'.format(sample_id, cardinality_nr)
                fastr.log.debug('Found expanded item {}: {}'.format(sub_sample_id, value))
                if self.isurl(value):
                    # Expanded value is an URL, so it need to be processed
                    outsubdir = os.path.join(outdir, str(sub_sample_id))
                    if not os.path.isdir(outsubdir):
                        os.mkdir(outsubdir)
                    result = fastr.ioplugins.pull_source_data(value, outsubdir, sub_sample_id, datatype)
                    results.update(result)
                else:
                    # Expanded value is a value, so we assume this is the value to be used
                    results[sub_sample_id] = (value,)
        elif isinstance(valuelist, str):
            # The expand did not change the URL
            if valuelist != inurl:
                raise exceptions.FastrValueError('If valuelist is a str, it should be the original inurl!')

            # Check against None to avoid issubclass throwing an error
            if datatype is not None and issubclass(datatype, TypeGroup):
                if all(issubclass(x, URLType) for x in datatype.members):
                    urltype = True
                elif all(not issubclass(x, URLType) for x in datatype.members):
                    urltype = False
                else:
                    raise exceptions.FastrNotImplementedError('Cannot use a SourceNode that can supply mixed URL and Value types')
            else:
                # Check against None to avoid issubclass throwing an error
                urltype = datatype is not None and issubclass(datatype, URLType)

            fastr.log.debug('[{}] the urltype found is {}'.format(self.scheme, urltype))

            if urltype:
                outfile = os.path.join(outdir, urltools.basename(inurl))
                result = self.fetch_url(inurl, outfile)

                if not result:
                    raise exceptions.FastrIOError('Could not retrieve data from {}'.format(inurl))

                if datatype is None or issubclass(datatype, TypeGroup):
                    datatype = typelist.guess_type(result, options=datatype)
                    fastr.log.debug('Refined datatype to {}'.format(datatype))

                if datatype is not None:
                    contents = datatype.content(inurl, result)
                    fastr.log.debug('Found contents {}'.format(contents))
                else:
                    contents = [(inurl, result)]

                for extrain, extraout in contents:
                    if extrain == inurl and extraout == result:
                        fastr.log.info('Skipping original file {} -> {}'.format(extrain, extraout))
                        continue

                    fastr.log.debug('Orig {} -> {}'.format(inurl, result))
                    fastr.log.debug('Processing original file {} -> {}'.format(extrain, extraout))

                    if not os.path.exists(extraout):
                        extra_result = self.fetch_url(extrain, extraout)
                        if not extra_result:
                            raise exceptions.FastrIOError('Could not retrieve data from {} to {}'.format(extrain, extraout))

                results[sample_id] = (result,)
            else:
                result = self.fetch_value(inurl)
                results[sample_id] = (result,)
        else:
            fastr.log.error('Expand of {}  returned an invalid type! ({} after expansion)'.format(inurl, valuelist))

        return results

    def push_sink_data(self, inpath, outurl, datatype=None):
        """
        Write out the sink data from the inpath to the outurl.

        :param str inpath: the path of the data to be pushed
        :param str outurl: the url to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        :return: None
        """
        fastr.log.info('Push sink called with: {}, {}'.format(inpath, outurl))
        self.setup()

        if datatype is None or issubclass(datatype, TypeGroup):
            previous_datatype = datatype.id if datatype is not None else None
            datatype = typelist.guess_type(inpath, options=datatype)
            fastr.log.info('Determined specific datatype as {} (based on {})'.format(datatype.id, previous_datatype))

        if datatype is not None and issubclass(datatype, URLType):
            contents = datatype.content(inpath, outurl)
            fastr.log.info('Found URL contents: {}'.format(contents))
        else:
            contents = [(inpath, outurl)]
            fastr.log.info('Found value/simple contents: {}'.format(contents))

        for extracontent, extratarget in contents:
            if datatype is not None and issubclass(datatype, URLType):
                result = self.put_url(extracontent, extratarget)
            else:
                result = self.put_value(extracontent, extratarget)
            if not result:
                raise exceptions.FastrIOError('Could not store data from {} to {}'.format(extracontent, extratarget))

    @staticmethod
    def _correct_separators(path):
        """
        Translates the URL seperator '/' into the apropriate seperator for the OS

        :param str path: the path to correct
        :return: path with corrected separators
        :rtype: str
        """
        return path.replace('/', os.path.sep)


def main():
    """
    The main entry point for command line access to the IOPlugin
    """
    # The main function creates an entry point for the SourceNode and SinkNode
    parser = argparse.ArgumentParser(description="executes an ioplugin",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--behaviour', type=str, required=True,
                        choices=['source', 'sink'],
                        help="Select if the script should behave like"
                             " a 'source' or a 'sink'")
    parser.add_argument('-i', '--input', nargs='+', type=str, required=True,
                        help="The url to process (can also be a list)")
    parser.add_argument('-o', '--output', nargs='+', type=str, metavar='OUTPUT', required=True,
                        help="The output urls in vfs scheme (can also be a"
                             " list and should be the same size as --inurl)")
    parser.add_argument('-d', '--datatype', nargs='+', default=None, type=str,
                        help="The datatype of the source/sink data to handle")
    parser.add_argument('-s', '--sample_id', default=None, type=str,
                        help="The sample_id of the source/sink data to handle")

    args = parser.parse_args()

    fastr.log.info(('Arguments:\nbehaviour: {}\ninput: {}\noutput: {}\n'
                    'datatype: {}\nsample_id: {}').format(args.behaviour,
                                                          args.input,
                                                          args.output,
                                                          args.datatype,
                                                          args.sample_id))

    inputs = args.input
    outputs = args.output
    sample_id = args.sample_id

    # Get the datatype to use
    datatypes = args.datatype

    if args.behaviour == 'source':
        if len(outputs) != 1:
            message = 'Source can only handle one output per job (found: {})'.format(outputs)
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)
        output = outputs[0]

        if len(datatypes) != 1:
            message = 'Source can only handle one datatype per job (found: {})'.format(datatypes)
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)

        datatype = datatypes[0]
        if datatype is not None:
            datatype = fastr.typelist[datatype]
        fastr.log.debug("datatype to use: {}".format(datatype))

        if sample_id is None:
            message = 'For Source behaviour the sample id needs to be defined!'
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)

        if urltools.isurl(output):
            message = 'For Source behaviour the output should be a directory, not a URL! (found {})'.format(output)
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)

        results = []
        for input_ in inputs:
            if urltools.isurl(input_):
                parsed_input = up.urlparse(input_)
                try:
                    plugin = fastr.ioplugins[parsed_input.scheme]
                except KeyError:
                    message = "No valid scheme is supplied in: {} (Found {}). The following schemes are supported: {}".format(input_, parsed_input.scheme, ' '.join(fastr.ioplugins.keys()))
                    fastr.log.error(message)
                    raise exceptions.FastrUnknownURLSchemeError(message)

                results.append(plugin.pull_source_data(input_, output, sample_id, datatype))
            else:
                results.append(input_)

        if len(results) == 1:
            # If we have only one result, there is no need to merge
            result = results[0]
        else:
            # Merge multiple cardinality into a single result
            samples = set()
            for part in results:
                # Check if we got value or if the value was a simple value
                if isinstance(part, dict):
                    samples.update(part.keys())

            # For each sample collect all found values
            result = {}
            for sample_id in samples:
                result[sample_id] = temp = []

                for part in results:
                    if isinstance(part, dict):
                        # We have a dictionary with {sampleid: (value1, value2)} format
                        # FIXME: Is this behaviour desired? It might lead to strange results
                        temp.extend(part.get(sample_id, []))
                    else:
                        # We have a value (not URL) that was given, we assume this to be used for ALL samples (broadcasting)
                        temp.append(part)

        IOPlugin.print_result(result)
    elif args.behaviour == 'sink':
        if len(datatypes) == 1:
            datatypes *= len(inputs)

        for input_, output, datatype in zip(inputs, outputs, datatypes):
            fastr.log.info('Processing {} --> {} [{}]'.format(input_, output, datatype))

            if datatype is not None:
                datatype = fastr.typelist[datatype]

            fastr.log.debug("datatype to use: {}".format(datatype))

            if urltools.isurl(input_):
                message = 'For Sink behaviour the sink should be a path, not a URL! (found {})'.format(input_)
                fastr.log.critical(message)
                raise exceptions.FastrValueError(message)

            parsed_output = up.urlparse(output)
            try:
                plugin = fastr.ioplugins[parsed_output.scheme]
            except KeyError:
                message = "No valid scheme is supplied in: {} (Found {}). The following schemes are supported: {}".format(output, parsed_output.scheme, ' '.join(fastr.ioplugins.keys()))
                fastr.log.error(message)
                raise exceptions.FastrUnknownURLSchemeError(message)

            plugin.push_sink_data(input_, output, datatype)

    # Cleanup all plugins
    fastr.ioplugins.cleanup()


if __name__ == '__main__':
    try:
        main()
    except Exception as exception:
        # Pass error on to main process and raise error again
        exception = (
            type(exception).__name__,
            str(exception),
            exception.filename if hasattr(exception, 'filename') else None,
            exception.linenumber if hasattr(exception, 'linenumber') else None,
        )

        print('__FASTR_ERRORS__ = {}'.format(
            json.dumps(
                [exception]
            )
        ))
        raise
