import os
import sys
import json
import argparse
import textwrap

from eureqa.analysis_templates.runner import analysis_template_runner
from eureqa.utils._analysis_template_cli import *

def main(argv):
    """ Handle executing analysis template code without actually uploading it to the server.
    Mostly a wrapper around :class:`~eureqa.analysis_templates.runner.analysis_template_runner`.
    The latter is called directly by the server; this one is a little more user-friendly
    and respects eureqa_config.json.

    :param list argv: Arguments
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION, epilog=textwrap.dedent("""\
        Usage Examples:

        To run the example module included with this project, do:
        python -m eureqa run_analysis_template example_module
        You will be prompted for username and password if necessary.

        To run within a particular Eureqa Organization:
        python -m eureqa run_analysis_template -u <username> -p <password> -o <organization> example_module
        """))

    ## Pick the command-line arguments that this app needs
    add_module_args(parser)
    add_server_args(parser)
    add_local_template_args(parser)
    add_script_args(parser)

    ## parse_args() wants the arguments to the command.
    ## argv[0] *is* the command.
    args = parser.parse_args(argv[1:])

    params = merge_defaults_from_json(args.module_dir, args)

    clean_and_populate_params(params, not args.quiet)
    module_dir  = params['module_dir']
    module_name = os.path.basename(module_dir)

    if not args.quiet:
        params_no_password = dict(params)
        params_no_password['password'] = '********'

        # Flatten structure for pretty-printing
        if 'parameter_values' in params_no_password and isinstance(params_no_password['parameter_values'], dict):
            params_no_password['parameter_values'] = params_no_password['parameter_values']['parameters']

        print "Installing module '%s':\n%s" % (module_name, json.dumps(params_no_password,
                                                                      indent=4,
                                                                      sort_keys=True))

    runner_args = ['-m', module_name,
                   '-u', params['username'],
                   '-e', params['url'],
                   '-o', params['organization']]

    if 'password' in params:
        runner_args.append('-p')
        runner_args.append(params['password'])
    if 'api_key' in params:
        runner_args.append('-k')
        runner_args.append(params['api_key'])
    if 'save_credentials' in params:
        runner_args.append('--save-credentials')
    if 'quiet' in params:
        runner_args.append('--quiet')

    ## Make sure the module is in path so it can be imported
    mod_path = os.path.dirname(os.path.abspath(params['module_dir']))
    sys.path.insert(0, mod_path)

    runner = analysis_template_runner()
    runner.run_args(runner_args, params.get('parameter_values', {}))

    if args.save:
        write_defaults_to_json(params, module_dir)

    sys.path.remove(mod_path)
