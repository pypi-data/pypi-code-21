import argparse
import bravado
import contextlib
import os.path
import re
import subprocess
import sys
import unittest
import urllib3
from bravado_core.schema import is_ref
from bravado.client import SwaggerClient
from bravado.exception import make_http_exception
from bravado.requests_client import RequestsClient
from jinja2 import Environment


TEMPLATE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'apicheckr.py.tmpl')


@contextlib.contextmanager
def smart_open(filename=None):
    ''' write to file or stdout '''
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def _replace_function_parameter(code, function, parameter, value):
    ret = ''
    start = 0
    for line in code.splitlines():
        if start:
            if len(line) and len(re.match(r'^(\s*)', line).group(1)) <= start:
                start = 0
            else:
                if not re.match(r'^\s+#', line):
                    quote = ''
                    if isinstance(value, str):
                        quote = '\''
                    line = re.sub(r'^(\s+' + parameter + '=).*?(,|$)',
                                  r'\g<1>' + quote + str(value) + quote +
                                  r'\g<2>',
                                  line)
        if line.find('def ' + function + '(') != -1:
            start = len(re.match(r'^(\s+)def', line).group(1))
        ret += line + '\n'
    return ret


def _replace_function_option(code, function, option, value):
    ret = ''
    start = 0
    options = 0
    state = 0
    for line in code.splitlines():
        if not len(line) or re.match(r'^\s+#', line):
            ret += line + '\n'
            continue
        if state > 0:
            if len(re.match(r'^(\s+)', line).group(1)) <= start:
                state = 0
        if state == 0:
            if line.find('def ' + function + '(') != -1:
                start = len(re.match(r'^(\s+)def', line).group(1))
                state = 1
        if state > 1:
            if len(re.match(r'^(\s+)', line).group(1)) <= options:
                state = 0
        if state == 1:
            if line.find('_request_options=') != -1:
                options = len(re.match(r'^(\s+)_req', line).group(1))
                state = 2
        if state == 2:
            quote = ''
            if isinstance(value, str):
                quote = '\''
            line = re.sub(r'^(.*\'' + option + '\': ).*?(,|$)',
                          r'\1' + quote + str(value) + quote + r'\2', line)
        ret += line + '\n'
    return ret


def _replace_function_check(code, function, value):
    ret = ''
    start = 0
    out = ''
    state = 0
    for line in code.splitlines():
        if not len(line):
            ret += line + '\n'
            continue
        if state > 0:
            if len(re.match(r'^(\s+)', line).group(1)) <= start:
                state = 0
        if state == 0:
            if line.find('def ' + function + '(') != -1:
                start = len(re.match(r'^(\s+)def', line).group(1))
                state = 1
        if state == 1:
            if line.find('# DONOTDEL checkstart') != -1:
                out = re.match(r'^(\s+)#', line).group(1)
                state = 2
                ret += line + '\n'
                continue
        if state > 1:
            if len(re.match(r'^(\s+)', line).group(1)) < len(out):
                state = 0
        if state == 2:
            if line.find('# DONOTDEL checkend') != -1:
                if isinstance(value, str):
                    for vline in value.splitlines():
                        ret += out + vline + '\n'
                else:
                    ret += out + str(value) + '\n'
                state = 0
            else:
                continue
        ret += line + '\n'
    return ret


def inject_from_file(filename_values, filename_test):
    '''
    read values from filename_values, use them in filename_test and
    persists result in filename_test (overwrite it)
    '''
    values = {}
    values = eval(open(filename_values, 'r').read())
    if type(values) is not dict:
        print('no values found, wrong schema?')
        return
    test = open(filename_test, 'r').read()
    for fname, function in values.items():
        if 'parameter' in function:
            for parameter, value in function['parameter'].items():
                test = _replace_function_parameter(test, fname, parameter,
                                                   value)
        if 'options' in function:
            for option, value in function['options'].items():
                test = _replace_function_option(test, fname, option, value)
        if 'check' in function:
            test = _replace_function_check(test, fname, function['check'])
    open(filename_test, 'w').write(test)


class ApiCheckr(unittest.TestCase):

    def __init__(self, url, *args):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        unittest.TestCase.__init__(self, *args)
        self.url = url
        # do not verify certificates (for self signed)
        http_client = RequestsClient()
        http_client.session.verify = False
        self._client = SwaggerClient.from_url(url, http_client=http_client)
        self._funcs = []
        self._models = {}
        self._functions = {}
        self._functionsresponses = {}
        self._functionsparameters = {}
        self._responses = []

    def unittest(self):
        ApiCheckr.url = self.url
        unittest.main()

    @classmethod
    def setUpClass(cls):
        cls.ac = ApiCheckr(cls.url)
        # do not verify certificates(for self signed)
        http_client = RequestsClient()
        http_client.session.verify = False
        cls.client = SwaggerClient.from_url(cls.url,
                                            http_client=http_client)

    def check_response_code(self, code, operation, response, do_check=None):
        self.assertEqual(code.status_code, response,
                         'http status codes differ')
        if do_check:
            do_check(code.swagger_result)

    def get_all_end_points(self):
        ''' get all Endpoints '''
        return dir(self._client)

    def get_all_functions_of_endpoints(self, ep):
        ''' get all Functions of the given Endpoint '''
        return dir(getattr(self._client, ep))

    def get_function_definition(self, ep, func):
        '''
        get the Definition from OpenApi from the given endpoint and function
        '''
        return getattr(getattr(getattr(self._client, ep), func).operation,
                       'op_spec')

    def do_deep_deref(self, d):
        ''' resolve all references within dictonary '''
        for k, v in d.items():
            if is_ref(v):
                v = self._client.swagger_spec.deref(v)
                d[k] = v
            if isinstance(v, dict):
                v = self.do_deep_deref(v)
        return d

    def get_resolved_type(self, parameter):
        '''
        return the type or schema reference found under 'schema' or
        'schema''items'. arrays ar preceded with '+'.
        '''
        self.do_deep_deref(parameter)
        ret = ''
        if 'x-model' in parameter:
            ret += parameter['x-model']
        elif 'type' in parameter:
            ret += parameter['type']
            if ret == 'array':
                ret = '+'
        if 'schema' in parameter:
            if 'x-model' in parameter['schema']:
                ret += parameter['schema']['x-model']
            elif 'type' in parameter['schema']:
                ret += parameter['schema']['type']
                if ret == 'array':
                    ret = '+'
            if 'items' in parameter['schema']:
                if 'type' in parameter['schema']['items']:
                    ret += parameter['schema']['items']['type']
                if 'x-model' in parameter['schema']['items']:
                    ret += parameter['schema']['items']['x-model']
        return ret

    def get_model(self, parameter):
        '''
        return the schema reference found under 'schema' or 'schema''items'.
        '''
        if 'items' in parameter['schema']:
            return parameter['schema']['items']['x-model']
        else:
            return parameter['schema']['x-model']

    def get_responsekeys_of_function(self, endpoint: str, function):
        '''
        return all possible responses of a function as text list.
        'default' is converted to '200'
        '''
        li = list((self.get_function_definition(endpoint, function)[
            'responses']).keys())
        li = [x if x != 'default' else '200' for x in li]
        return li

    def get_short_parameters_of_function(self, endpoint, function):
        '''
        return list of all parameters of a function as a dictonary.
        only the parameter name with the additionally information 'required'
        and 'type' are returned.
        This should be used to test is the signature of a function has changed.
        '''
        return {parameter['name']: {'required': parameter['required'],
                                    'type': self.get_resolved_type(parameter)}
                for parameter in
                self.get_function_definition(endpoint, function)['parameters']}

    def get_details_of_response(self, response):
        if 'schema' in response:
            if 'x-model' in response['schema']:
                return re.sub(r'\s+$', '', re.sub(r'^(.*)$', r'        # \1',
                              self._client.get_model(
                                  response['schema']['x-model']).__doc__,
                              flags=re.MULTILINE), flags=re.MULTILINE)
        return ''

    def _construct_functionlist(self, function, definition, response):
        ret = {}
        ret['function'] = function
        ret['response'] = response if response != 'default' else '200'
        ret['responseexception'] = self._get_bravado_exceptionclassname(response)
        ret['responsedata'] = self.get_resolved_type(
            definition['responses'][response]) if 'schema' in\
            definition['responses'][response] else None
        ret['responsedetails'] = self.get_details_of_response(
            definition['responses'][response])
        ret['description'] = definition['responses'][response]['description']
        ret['models'] = list(map(lambda p: self.get_model(p),
                                 filter(lambda p: 'type' not in p,
                                        definition['parameters'])))
        ret['parameters'] = list(map(lambda p: dict({
            'name': p['name'],
            'isobject': 'type' not in p,
            'objectproperties': self._client.get_model(
                self.get_model(p))._properties if 'schema' in p else None,
            'objectdetail': re.sub(re.compile("^\s*(.*)(\s*)$", re.MULTILINE),
                                   r"            # \1", self._client.get_model(
                                       self.get_model(p)).__doc__)
            if 'schema'in p else '',
            'type': self.get_resolved_type(p)[1:]
            if self.get_resolved_type(p)[:1] == '+' else
            self.get_resolved_type(p),
            'isarray': self.get_resolved_type(p)[:1] == '+',
            'required': p['required'],
            'description': p['description'] if 'description' in p else ''
        }), definition['parameters']))
        return ret

    def _get_bravado_exceptionclassname(self, response):
        try:
            ret = 'bravado.exception.' +\
                make_http_exception(type('', (object,), {
                                         'status_code': int(response)
                                         })()).__class__.__name__
        except Exception:
            ret = ''
        return ret

    def get_exception(self, response):
        try:
            ret = make_http_exception(type('', (object,), {
                'status_code': int(response)
            })()).__class__
        except Exception:
            ret = None
        return ret

    def create_TestCases_for_all_endpoints(self, filename=""):
        '''
        create TestCases for all endpoints
        output one file per endpoint with filename = <filename>_endpoint.py
        '''
        eps = self.get_all_end_points()
        for ep in eps:
            if not filename or filename == '-':
                self.create_TestCases_for_endpoint(filename=filename,
                                                   endpoint=ep)
            else:
                self.create_TestCases_for_endpoint(filename=filename + '_' +
                                                   ep + '.py', endpoint=ep)

    def create_TestCases_for_endpoint(self, filename="", endpoint=""):
        '''
        create TestCase for specified endpoint
        output to file <filename> or to stdout if file is '-' or empty
        '''
        with smart_open(filename) as fh:
            eps = self.get_all_end_points()
            if endpoint not in eps:
                raise ValueError("endpoint '%s' not found in %s" %
                                 (endpoint, eps))
            funcs = []
            models = {}
            functions = {}
            functionsresponses = {}
            functionsparameters = {}
            responses = []
            for e in eps:
                functions[e] = self.get_all_functions_of_endpoints(e)
                functionsresponses[e] = {}
                functionsparameters[e] = {}
                for f in functions[e]:
                    functionsresponses[e][f] =\
                        self.get_responsekeys_of_function(e, f)
                    functionsparameters[e][f] =\
                        self.get_short_parameters_of_function(e, f)
            for func in self.get_all_functions_of_endpoints(endpoint):
                onefunc = self.get_function_definition(endpoint, func)
                for r in sorted(onefunc['responses']):
                    if r == 'default':
                        if '200' not in responses:
                                responses.append('200')
                    else:
                        if r not in responses:
                            responses.append(r)
                    funcs.append(
                        self._construct_functionlist(func, onefunc, r))
                    for i in filter(lambda p: 'type' not in p,
                                    onefunc['parameters']):
                        if self.get_model(i) not in models:
                            models.update(dict({
                                'name': self.get_model(i)
                            }))
            with open(TEMPLATE_PATH, 'r') as f:
                env = Environment(lstrip_blocks=True, trim_blocks=True)
                print(env.from_string(f.read()).render(
                    endpoints=eps, endpoint=endpoint, url=self.url,
                    funcs=funcs, functions=functions,
                    functionsresponses=functionsresponses,
                    functionsparameters=functionsparameters,
                    responses=responses
                ), file=fh)


def main():
    parser = argparse.ArgumentParser(prog='apicheckr')
    subparsers = parser.add_subparsers(help='possible commands',
                                       dest='cmd')
    subparsers.required = True
    generate_parser = subparsers.add_parser('generate')
    generate_parser.add_argument('URL', help='url of swagger file '
                                 '(use file://... for local files)')
    generate_parser.add_argument('FILE', help='check file '
                                 '(use - for STDOUT)')
    generate_parser.add_argument('-ep', '--endpoint', help='if empty for each '
                                 'endpoint a check file with '
                                 'FILE_<endpoint>.py will be created')
    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('FILE', help='filename of previous generated'
                            ' test script')
    run_parser.add_argument('-p', '--python', default='3', type=int,
                            choices=[2, 3], help='version of python to use')
    run_parser.add_argument('TESTFUNCTION', nargs='?', default='')
    run_parser = subparsers.add_parser('inject')
    run_parser.add_argument('FILE_VALUES', help='see command \'schema\''
                            ' script')
    run_parser.add_argument('FILE_TEST', help='filename of previous generated'
                            ' test script')
    run_parser.add_argument('-p', '--python', default='3', type=int,
                            choices=[2, 3], help='version of python to use')
    run_parser = subparsers.add_parser('schema')
    args = parser.parse_args()
    if args.cmd == 'generate':
        b = ApiCheckr(args.URL)
        if args.endpoint:
            b.create_TestCases_for_endpoint(args.FILE, endpoint=args.endpoint)
        else:
            b.create_TestCases_for_all_endpoints(args.FILE)
    if args.cmd == 'run':
        subprocess.call(['/usr/bin/python' + str(args.python), args.FILE,
                         args.TESTFUNCTION])
    if args.cmd == 'inject':
        inject_from_file(args.FILE_VALUES, args.FILE_TEST)
    if args.cmd == 'schema':
        print('''
{
    '<function>':
    {
        'parameter':  # werden beim Aufruf der <function> übergeben
        {
            '<para>': <value>,  # z.B. 'store_id': 'fotopuzzle.de'
            '<para>': <value>,
            ...
        },
        'options':    # werden als _request_options beim Aufruf übergeben
        {
            '<opt>': <value>,  # z.B. 'headers': {'Accept-Language': 'de'}
            ...
        },
        'check': <value>  # ist der Code, der ausgeführt wird, wenn der
        # Aufruf das Ergebnis zurückbekommt. Kann auch mehrzeilig sein durch
        # Verwendung von \\n oder als Docstring
        # z.B.
        'check': \'\'\'out_Problem = json.loads(response)
                    self.assertTrue(\'title\' in out_Problem)\'\'\'
    },
    '<function>':
    ...
}
        ''')


if __name__ == "__main__":
    main()
