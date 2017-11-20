# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)

import logging
import sys
import traceback
from datetime import datetime

from prettytable import PrettyTable

from benchsuite.cli.argument_parser import get_options_parser
from benchsuite.cli.shell import BenchsuiteShell
from benchsuite.core.controller import BenchmarkingController
from benchsuite.core.model.exception import BashCommandExecutionFailedException, BaseBenchmarkingSuiteException

RUNTIME_NOT_AVAILABLE_RETURN_CODE = 1

logger = logging.getLogger(__name__)


class CliParsingException(BaseBenchmarkingSuiteException):
    pass

def list_benchmarks_cmd(args):
    table = PrettyTable()
    table.field_names = ["Tool", "Workloads"]
    table.align = 'l'
    with BenchmarkingController(args.config) as bc:
        for p in bc.list_available_benchmark_cfgs():
            table.add_row([p.tool_name, [n['id'] for n in p.workloads]])
    print(table.get_string())

def list_providers_cmd(args):
    table = PrettyTable()
    table.field_names = ["Name", "Service Types"]
    table.align = 'l'
    with BenchmarkingController(args.config) as bc:
        for p in bc.list_available_providers():
            table.add_row([p.name, ', '.join(p.service_types)])
    print(table.get_string())


def list_executions_cmd(args):

    table = PrettyTable()
    table.field_names = ["Id", "Benchmark", "Created", "Exec. Env.", "Session"]

    with BenchmarkingController(args.config) as bc:
        execs = bc.list_executions()
        for e in execs:
            created = datetime.fromtimestamp(e.created).strftime('%Y-%m-%d %H:%M:%S')
            table.add_row([e.id, e.test.tool_name+'/'+e.test.workload_name, created, e.exec_env, e.session.id])

    print(table.get_string())


def list_sessions_cmd(args):

    table = PrettyTable()
    table.field_names = ["Id", "Provider", "Service Type", "Created", "Properties"]

    with BenchmarkingController(args.config) as bc:
        sessions = bc.list_sessions()
        for s in sessions:
            created = datetime.fromtimestamp(s.created).strftime('%Y-%m-%d %H:%M:%S')
            props = "; ".join(["{0}={1}".format(k,v) for k,v in s.props.items()]) if hasattr(s, 'props') else ""
            table.add_row([s.id, s.provider.name, s.provider.service_type, created, props])

        print(table.get_string())


def destroy_session_cmd(args):
    with BenchmarkingController(args.config) as bc:
        bc.destroy_session(args.id)
        print('Session {0} successfully destroyed'.format(args.id))


def parse_new_session_properties(args):
    props = {}

    for i in args.property or []:
        v = i.split("=")
        if len(v) != 2:
            raise CliParsingException('Cannot parse property "{0}". '
                                      'The property must be in the format <name>=<value>'.format(i))
        props[v[0]] = v[1]

    if args.user:
        props['user'] = args.user

    if args.tag:
        props['tags'] = args.tag

    return props


def new_session_cmd(args):
    with BenchmarkingController(args.config) as bc:
        e = bc.new_session(args.provider, args.service_type, properties = parse_new_session_properties(args))
        print(e.id)

def new_execution_cmd(args):
    with BenchmarkingController(args.config) as bc:
        e = bc.new_execution(args.session, args.tool, args.workload)
        print(e.id)


def prepare_execution_cmd(args):
    with BenchmarkingController(args.config) as bc:
        bc.prepare_execution(args.id)


def collect_results_cmd(args):
    with BenchmarkingController(args.config) as bc:
        out, err = bc.collect_execution_results(args.id)
        print(str(out))
        print(str(err))


def run_execution_cmd(args):
    with BenchmarkingController(args.config, storage_config_file=args.storage_config) as bc:
        bc.run_execution(args.id, async=args.async)


def multiexec_cmd(args):

    # parse the tests to execute
    tuples = []
    for s in args.tests:
        t = s.split(':', maxsplit=1)
        if len(t) == 1:
            tuples.append((t[0], None))
        else:
            tuples.append((t[0], t[1]))

    with BenchmarkingController(storage_config_file=args.storage_config) as bc:
        bc.execute_onestep(args.provider, args.service_type, tuples,
                           new_session_props=parse_new_session_properties(args),
                           fail_on_error=args.failonerror)


def start_shell_cmd(args):
    BenchsuiteShell().cmdloop()



cmds_mapping = {
    'new_session_cmd': new_session_cmd,
    'list_sessions_cmd': list_sessions_cmd,
    'destroy_session_cmd': destroy_session_cmd,
    'new_execution_cmd': new_execution_cmd,
    'prepare_execution_cmd': prepare_execution_cmd,
    'run_execution_cmd': run_execution_cmd,
    'collect_results_cmd': collect_results_cmd,
    'multiexec_cmd': multiexec_cmd,
    'list_executions_cmd': list_executions_cmd,
    'list_providers_cmd': list_providers_cmd,
    'list_benchmarks_cmd': list_benchmarks_cmd,
    'start_shell_cmd': start_shell_cmd
}



def main(args=None):

    parser = get_options_parser(cmds_mapping=cmds_mapping)

    args = parser.parse_args(args = args or sys.argv[1:])

    # adjust logging to the console accordingly with the verbosity level requested
    #
    # FATAL
    # CRITICAL
    # ERROR
    # WARNING
    # INFO -v
    # DEBUG -vv
    # DEBUG (all modules) -vvv

    logging_level = logging.WARNING
    logging_format = '%(message)s'

    if args.verbose:
        if args.verbose == 1:
            logging_level = logging.INFO
            logging_format = '%(message)s'

        if args.verbose == 2:
            logging_level = logging.DEBUG
            logging_format = '%(levelname)s: %(message)s'

        if args.verbose > 2:
            logging_level = logging.DEBUG
            logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


    # if the user sets the --quiet flag, do not print logging messages. Only print() messages will appear on the screen
    if args.quiet:
        logging.basicConfig(stream=None)
    else:
        # basic config for all loggers (included the ones from third-party libs)
        logging.basicConfig(
            level=logging.ERROR,
            stream=sys.stdout,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


        # logging from benchsuite modules
        st = logging.StreamHandler(stream=sys.stdout)
        st.setLevel(logging_level)
        st.setFormatter(logging.Formatter(logging_format))
        bench_suite_loggers = logging.getLogger('benchsuite')
        bench_suite_loggers.handlers = []
        bench_suite_loggers.addHandler(st)
        bench_suite_loggers.setLevel(logging_level)
        bench_suite_loggers.propagate = False

        if args.verbose and args.verbose > 2:
            logging.root.handlers = []
            logging.root.addHandler(st)
            logging.root.setLevel(logging.DEBUG)

    try:

        if not hasattr(args, 'func'):
            print('A command must be specified. Run with --help  to check the different options')
            return 10

        return args.func(args) or 0


    except BashCommandExecutionFailedException as e:
        return 1

    except Exception as e:
        print('ERROR!!! An exception occured: "{0}" (run with -v to see the stacktrace)'.format(str(e)))
        if args.verbose and args.verbose > 0:
            traceback.print_exc()
        return 100


if __name__ == '__main__':
    main(sys.argv[1:])