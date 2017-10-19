# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
`Service`

Role
====

Dynamic object for service consumption based on service metadata attributes.
"""

from __future__ import absolute_import

from pprint import pformat
from collections import OrderedDict
from azureml.common.utils import function_beget, to_camel_case
from .encoding_type import EncodingType

import logging
import base64
import os
import shutil
import pandas as pd

log = logging.getLogger(__name__)


def fn_docstring_tpl(service):
    """
    Builds the function's docstring based on describing features.

    :param dict service: The service metadata.
    :return str doc: The function docstring.
    """

    tpl = """Consume the {0} service.

    {1}
    
    {2}    
    :returns ServiceResponse: The `<ServiceResponse>` object contains the set of
        expected output values and artifacts. The possible outputs include:
                
        {3}        

    :Raises:
        HttpException: If server errors occur while executing the service.
        ValueError: If argument input types do not match the expected service
            input types.
    """

    def io(schema, io_tpl):
        args = []
        for arg in schema:
            args.append(io_tpl.format(EncodingType.to_python(arg['type']),
                                      arg['name']))

        return args

    # -- build `:para type name: description` --
    input_tpl = ':param {0} {1}: The required service input.'
    output_tpl = 'Output: {0} {1}'

    inputs = service.get('inputParameterDefinitions', [])
    outputs = service.get('outputParameterDefinitions', [])

    return tpl.format(service['name'],
                      service['description'],
                      '\n    '.join(io(inputs, input_tpl)),
                      '\n    '.join(io(outputs, output_tpl)))

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class Service(object):
    """
    Service object from metadata.
    """

    def __new__(cls, *args, **kwargs):
        service = args[0]
        body = dict(cls.__dict__)

        log.debug('New Service with meta properties:\n %s', service)

        # -- prepare consume function ---
        params = ['self']
        for key in service.get('inputParameterDefinitions', {}):
            params.append(key['name'])

        def fn(self):
            args = locals()
            props = dict()

            for key in self._service.get('inputParameterDefinitions', {}):
                props[key.get('name')] = args[key.get('name')]

            return self._consume(props)

        # -- build consume function and attach --
        fn_name = service.get('operationId')
        doc = fn_docstring_tpl(service)
        fn_name = 'consume' if fn_name is None else fn_name
        body[fn_name] = function_beget(fn, fn_name, params, doc)

        # -- store fn for help/capabilities --
        service['_fn'] = {'name': fn_name, 'args': ','.join(params)}

        # -- Class Name by service name --
        name = to_camel_case(service['name'], prefix='Service')
        name = '{}{}'.format(name, cls.__name__)

        return object.__new__(type(name, (cls,), body))

    def __init__(self, service, http_client):
        """
        Constructor

        :param service:
        :param http_client:
        """
        super(Service, self).__init__()

        self._service = service
        self._http_client = http_client
        self._api = '/api/' + service.get('name') + '/' + service.get('version')


    def capabilities(self):
        """
        Gets the service holding capabilities.

        :return: A dict of key/values describing the service.
        """

        service = self._service
        swagger = self._http_client.host + self._api + '/swagger.json'
        inputs = service.get('inputParameterDefinitions')
        outputs = service.get('outputParameterDefinitions')
        operation_id = service.get('operationId')
        fn = service.get('_fn')

        # -- Display I/O from server types to python type --
        def io_to_python(args):
            io = []
            for schema in list(args):
                io.append({
                  'name': schema['name'],
                  'type': EncodingType.to_python(schema['type'])
                })

            return io

        return {
            'api': self._api,
            'name': service.get('name'),
            'version': service.get('version'),
            'published_by': service.get('versionPublishedBy'),
            'runtime': service.get('runtimeType'),
            'description': service.get('description'),
            'creation_time': service.get('creationTime'),
            'snapshot_id':  service.get('snapshotId'),
            'inputs': inputs,
            'outputs': outputs,
            'inputs_encoded': io_to_python(inputs),
            'outputs_encoded': io_to_python(outputs),
            'artifacts': service.get('outputFileNames'),
            'operation_id': 'consume' if operation_id is None else operation_id,
            'swagger': swagger,
            'public-functions': {
                fn['name']: fn['name'] + '(' + fn['args'] + ')',
                'capabilities': 'capabilities()',
                'swagger': 'swagger(json=True)',
                'get_batch': 'get_batch(execution_id)',
                'list_batch_execution': 'list_batch_execution()',
                'batch': 'batch(records, parallel_count=10)'
            }
        }

    def swagger(self):
        """
        Retrieves the `swagger.json` for this service (see http://swagger.io/).
        :return: The swagger document for this service.
        """

        response = self._http_client.get(self._api + '/swagger.json')
        return response.text

    def get_batch(self, execution_id):
        """
        Retrieve the `Batch` based on an `execution id`

        :param execution_id: The id of the batch execution.
        :return: The `Batch`.
        """

        return Batch(self, execution_id=execution_id)

    def list_batch_executions(self):
        """
        Gets all batch executions currently queued for this service.

        :return: A list of `execution ids`.
        """

        return self._http_client.get(self._api + '/batch').json()

    def batch(self, records, parallel_count=10):
        """
        Register a set of input records for batch execution on this service.

        :param records: The `data.frame` or `list` of
               input records to execute.
        :param parallel_count: Number of threads used to process entries in
               the batch. Default value is 10. Please make sure not to use too
               high of a number because it might negatively impact performance.
        :return: The `Batch` object to control service batching
                lifecycle.
        """

        # schema `inputParameterDefinitions` has ordered arguments
        encode = EncodingType.cast_from_python
        arg_order = self._service.get('inputParameterDefinitions', [])
        ordered_records = []

        # Batch with no inputs. This will simply
        if arg_order is None or len(arg_order) == 0:
            raise ValueError('Attempt to batch a service with void inputs.')

        if isinstance(records, list):
            ordered_records = records
        elif isinstance(records, dict):
            # Highly inefficient approach, however list sizes will be small.
            #
            # Take dict `records` in this format:
            # {
            #   'arg1': [1, 2, 3]
            #   'arg2': [True, False, True]
            # }
            #
            # and transform the `records` into an encoded format:
            # [
            #   { 'arg1': 1, 'arg2': True },
            #   { 'arg2': 2, 'arg2': False },
            #   { 'arg3': 3, 'arg2': True }
            # ]

            # grab any, all same size
            batch_cnt = len(records[arg_order[0]['name']])
            for index in range(batch_cnt):
                record = {}  # fn signature --> fn(arg1, arg2, arg3, ...)
                for arg in arg_order:
                    if len(records[arg['name']]) != batch_cnt:
                        msg = 'Record out of bounds "{0}", all records must ' \
                              'be of the same length.'.format(arg['name'])
                        raise ValueError(msg)

                    record[arg['name']] = encode(arg['type'],
                                                 records[arg['name']][index])
                ordered_records.append(record)
        else:
            # order each col in the DataFrame row to make sure they match the
            # argument order of the service. We want a,b,c --not-- c,a,b
            for row in records.itertuples(index=True, name='Pandas'):
                ordered_row = []
                for arg in arg_order:
                    # (col-arg, value)
                    ordered_row.append((arg['name'], encode(arg['type'],
                                        getattr(row, arg['name']))))

                ordered_records.append(OrderedDict(ordered_row))

        records = ordered_records

        # return records
        return Batch(self, records=records, parallel_count=parallel_count)

    def _sanitize_for_serialization(self, body):
        for schema in self._service.get('inputParameterDefinitions', {}):
            value = body[schema['name']]
            try:
                body[schema['name']] = \
                    EncodingType.cast_from_python(schema['type'], value)
            except Exception as e:
                log.error(e)
                msg = 'Invalid `input` {0}\n{1}\nname: {2} type: {3}'.format(
                    type(e).__name__, str(e), schema['name'], schema['type'])
                raise ValueError(msg)

        return body

    def _consume(self, body):
        # map input values into service consume format for json marshalling
        body = self._sanitize_for_serialization(body)

        # POST /api/:name/:version
        response = self._http_client.post(self._api, json=body).json()

        output_schema = self._service.get('outputParameterDefinitions', {})

        return ServiceResponse(self._api, response, output_schema)

    def __str__(self):
        return '<' + type(self).__name__ + '> \n' + pformat(vars(self),
                                                            indent=4, width=1)

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class ServiceResponse(object):
    """
    Create a new Response Object by service name and raw service metadata.
    """
    def __init__(self, api, response, output_schema):
        self.api = api
        self.error = response.get('errorMessage', '')
        self.console_output = response.get('consoleOutput', '')
        self.raw_outputs = response.get('outputParameters', {})
        self.artifacts = response.get('outputFiles', [])

        # -- map and cast server output values back to python types --
        output_values = response.get('outputParameters', {})
        outputs = dict()

        for schema in output_schema:
            name = schema['name']
            server_type = schema['type']
            value = output_values.get(name)
            outputs[name] = EncodingType.cast_to_python(server_type, value)

        self.outputs = outputs

    @property
    def api(self):
        """
        Gets the api endpoint.
        """
        return self._api

    @api.setter
    def api(self, api):
        """
        Sets the api endpoint

        :param api: The api endpoint.
        """
        self._api = api

    @property
    def error(self):
        """
        Gets the error if present.
        """
        return self._error

    @error.setter
    def error(self, error):
        """
        Sets the error if present, otherwise empty.

        :param error: The error message.
        """
        self._error = error

    @property
    def console_output(self):
        """
        Gets the console output if present.
        """
        return self._console_output

    @console_output.setter
    def console_output(self, console_output):
        """
        Sets the console output if present, otherwise empty.

        :param console_output: The console output.
        """
        self._console_output = console_output

    @property
    def raw_outputs(self):
        """
        Gets the raw response outputs if present.
        """
        return self._raw_outputs

    @raw_outputs.setter
    def raw_outputs(self, raw_outputs):
        """
        Sets the raw response outputs if present, otherwise empty.

        :param outputs: The outputs.
        """
        self._raw_outputs = raw_outputs

    @property
    def outputs(self):
        """
        Gets the response outputs if present.
        """
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        """
        Sets the response outputs if present, otherwise empty.

        :param outputs: The outputs.
        """
        self._outputs = outputs

    @property
    def artifacts(self):
        """
        Gets the response outputs if present.
        """
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts):
        """
        Sets the response file artifacts if present, otherwise empty.

        :param outputs: The response file artifacts.
        """
        self._artifacts = artifacts

    def output(self, output):
        """
         A convenience function to look up a output values by name.

        :param output:
        :returns: The service output.
        """
        return self.outputs.get(output)

    def artifact(self, artifact_name, decode=True, encoding=None):
        """
        A convenience function to look up a file artifact by name and optionally
        base64 decode it.

        :param artifact_name: The name of the file artifact.
        :param decode: Whether to decode the Base64 encoded artifact string.
        :param encoding:
        :return: The file artifact as a Base64 encoded string if `decode=False`
                 otherwise the decoded string.
        """

        artifact = self.artifacts.get(artifact_name)

        if artifact is not None and decode:
            try:
                artifact = base64.b64decode(artifact)

                if encoding is not None:
                    artifact = artifact.decode(encoding)
            except ValueError as e:
                log.error(e)
                msg = 'Artifact b64decode error: {0}\n{1}\n{2}'\
                    .format(type(e).__name__, str(e), artifact_name)
                raise ValueError(msg)

        return artifact

    def __str__(self):
        return '<ServiceResponse> \n' \
           '   api: {api} \n' \
           '   error: {error}\n' \
           '   console_output: {console}\n' \
           '   outputs: {outputs}\n' \
           '   raw_outputs: {raw}\n' \
           '   artifacts: {artifacts}'.format(api=self.api,
                                              error=self.error,
                                              console=self.console_output,
                                              outputs=self.outputs,
                                              raw=self.raw_outputs,
                                              artifacts=self.artifacts)

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


def execution(func):
    def wrapper(self, *args, **kwargs):
        if self._execution_id is None:
            raise ValueError('Batch not started, `execution_id` is None.')

        return func(self, *args)
    return wrapper


class Batch(object):
    """
    Manager of a service's batch execution lifecycle.
    """

    def __init__(self, service, records=[], parallel_count=10,
                 execution_id=None):

        self._api = service.capabilities()['api'] + '/batch'
        self._output_schema = service.capabilities()['outputs']
        self._http_client = service._http_client  # TODO

        self.records = records
        self.parallel_count = parallel_count
        self.execution_id = execution_id

    @property
    def api(self):
        """
        Gets the api endpoint.
        """
        return self._api

    @api.setter
    def api(self, api):
        """
        Sets the api endpoint

        :param str api: The api endpoint.
        """
        self._api = api

    @property
    def records(self):
        """
        Gets the batch input records.
        """
        return self._records

    @records.setter
    def records(self, records):
        """
        Sets the records on inputs to batch.

        :param list records: The records on inputs to batch.
        """
        self._records = records

    @property
    def parallel_count(self):
        """
        Gets this batch's parallel count of threads.
        """
        return self._parallel_count

    @parallel_count.setter
    def parallel_count(self, parallel_count):
        """
        Sets this batch's parallel count of threads.

        :param int parallel_count: The parallel count of threads to be applied.
        """

        self._parallel_count = parallel_count

    @property
    def execution_id(self):
        """
        Gets this batch's `execution id` if currently started, otherwise `None`.
        """
        return self._execution_id

    @execution_id.setter
    def execution_id(self, execution_id):
        """
        Sets this batch's `execution id`.

        :param str execution_id: The `execution id` for this batch.
        """
        self._execution_id = execution_id

    def start(self):
        """
        Start a batch execution.

        :return: Self
        """
        if self.execution_id is not None:
            return self

        url = self._api + '?parallelCount=' + str(self.parallel_count)
        response = self._http_client.post(url, json=self.records).json()

        self.execution_id = response['BatchExecutionId']

        return self

    @execution
    def cancel(self):
        """
        Cancel this batch execution.
        """
        self._http_client.delete(self._api + '/' + self.execution_id)

    def state(self):
        pass

    @execution
    def artifact(self, index, file_name):
        """

        Get the file artifact for this service batch execution `index`.

        :param index: Batch execution index.
        :param file_name: Artifact filename
        :return: A single file artifact.
        """
        url = [self._api, self.execution_id, str(index), 'files', file_name]
        return self._http_client.get('/'.join(url)).content

    @execution
    def list_artifacts(self, index):
        """
        List the file artifact names belonging to this service batch execution
        `index`.

        :param index: Batch execution index.
        :returns: A `list` of file artifact names.
        """
        url = [self._api, self.execution_id, str(index), 'files']
        res = self._http_client.get('/'.join(url)).json()
        return [] if res is None else res

    @execution
    def download(self, index, file_name=None, destination=os.getcwd()):
        """
        Download the file artifact to file-system in the `destination`.

        :param index: Batch execution index.
        :param file_name: The file artifact name.
        :param destination: Download location.
        :return: A `list` of downloaded file-paths.
        """
        if not os.path.exists(destination):
            msg = 'No such file or directory "{0}".'.format(destination)
            raise ValueError(msg)

        paths = []

        # -- download and save file --
        def save(file_index, file):
            content = self.artifact(file_index, file)
            file_path = os.path.join(destination, file)

            with open(file_path, 'wb') as out_file:
                out_file.write(content)


            return file_path

        if file_name is None:
            # -- save each file in this execution context --
            files = self.list_artifacts(index)
            for i in range(len(files)):
                paths.append(save(i, files[i]))
        else:
            paths = [save(index, file_name)]

        return paths

    def results(self, show_partial_results=True):
        """
        Poll batch results.

        :param show_partial_results: To get partial execution results or not.
        :returns: An execution Self :class:`~.BatchResponse`.
        """
        if self.execution_id is None:
            return None

        show = str(show_partial_results).lower()
        url = [self._api, self.execution_id + '?showPartialResult=' + show]

        response = self._http_client.get('/'.join(url)).json()

        api = self._api[:-6]  # strip `/batch` from `/api/:name/:version/batch`
        output_schema = self._output_schema

        return BatchResponse(api, self.execution_id, response, output_schema)

    def __str__(self):
        return '<' + type(self).__name__ + '> \n' + pformat(vars(self),
                                                            indent=4, width=1)

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class BatchResponse(object):
    """
    Create a new Response Object by service name and raw service metadata.
    """

    def __init__(self, api, execution_id, response, output_schema):
        self.api = api
        self.execution_id = execution_id
        self.completed_item_count = response['completedItemCount']
        self.total_item_count = response['totalItemCount']
        self.state = response['state']
        self._execution_results = response.get('batchExecutionResults', [])
        self._output_schema = output_schema

    @property
    def api(self):
        """
        Gets the api endpoint.
        """
        return self._api

    @api.setter
    def api(self, api):
        """
        Sets the api endpoint

        :param str api: The api endpoint.
        """
        self._api = api

    @property
    def execution_id(self):
        """
        Gets this batch's `execution id` if currently started, otherwise `None`.
        """
        return self._execution_id

    @execution_id.setter
    def execution_id(self, execution_id):
        """
        Sets this batch's `execution id`.

        :param str execution_id: The `execution id` for this batch.
        """
        self._execution_id = execution_id

    @property
    def completed_item_count(self):
        """
        Gets the number of completed batch results processed thus far.
        """
        return self._completed_item_count

    @completed_item_count.setter
    def completed_item_count(self, count):
        """
        Sets the number of completed batch results processed thus far.

        :param int count: The number of completed batch results processed.
        """
        self._completed_item_count = count

    @property
    def total_item_count(self):
        """
        Gets the total number of batch results processed in any state.
        """
        return self._total_item_count

    @total_item_count.setter
    def total_item_count(self, count):
        """
        Sets the number of batch results processed in any state.

        :param int count: The total number of batch results processed.
        """
        self._total_item_count = count


    @property
    def api(self):
        """
        Gets the api endpoint.
        """
        return self._api

    @api.setter
    def api(self, api):
        """
        Sets the api endpoint

        :param str api: The api endpoint.
        """
        self._api = api

    def execution(self, index):
        response = self._execution_results[index]

        return ServiceResponse(self.api, response, self._output_schema)

    def __str__(self):
        return '\n<BatchResponse> \n' \
               '   api: {api} \n' \
               '   execution_id: {id}\n' \
               '   completed_item_count : {ic}\n' \
               '   total_item_count: {tc}\n' \
               '   state: {state}'.format(api=self.api,
                                          id=self.execution_id,
                                          ic=self.completed_item_count,
                                          tc=self.total_item_count,
                                          state=self.state)
