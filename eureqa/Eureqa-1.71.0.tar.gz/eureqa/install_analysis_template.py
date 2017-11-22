#!/usr/bin/env python

# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This is a companion script for "run_analysis_template.py".
# Their implementations overlap substantially.

import sys
import json
import argparse
import os
import re

if __package__:
    # We're being run as "python -m eureqa install"
    from . import Eureqa
    from .analysis_templates import Parameters
    from .utils._analysis_template_cli import *
    from .session import Http404Exception
else:
    # We're being run as "eureqa/install_analysis_template.py"
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from eureqa import Eureqa
    from eureqa.analysis_templates import Parameters
    from eureqa.utils._analysis_template_cli import *
    from eureqa.session import Http404Exception

def main(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION, epilog=textwrap.dedent("""\
        Usage Examples:

        To upload the example module included with this project, do:
        python -m eureqa install_analysis_template example_module
        You will be prompted for username and password if necessary.
        Re-run to update the new module in place.

        To install with a custom name and within a Eureqa Organization:
        python -m eureqa install_analysis_template.py --name 'My Template' -u <username> -p <password> -o <organization> example_module

        To overwrite an existing module with ID 52 with the example:
        python -m eureqa install_analysis_template.py --id 52 example_module

        To use as part of a non-interactive shell script (Mac/Linux):
        NEW_TEMPLATE_ID=$(python -m eureqa install_analysis_template -q -u <username> example_module)
        This will use your saved password from the Eureqa API credential store,
        or error out if it isn't available.  (Omit '-q' to instead prompt
        for a password.)
        """))

    ## Pick the command-line arguments that this app needs
    add_module_args(parser)
    add_server_args(parser)
    add_template_args(parser)
    add_script_args(parser)

    ## parse_args() wants the arguments to the command.
    ## argv[0] *is* the command.
    args = parser.parse_args(argv[1:])

    for module_dir in [args.module_dir] + args.dependency_dir:
        module_name = os.path.basename(module_dir)
        if not re.match("[A-Za-z_][A-Za-z0-9_]*", module_name):
            raise RuntimeError, "Invalid directory name: '%s'  Module directory names must contain only [A-Za-z0-9_].  Its first character cannot be a number." % module_name

    params = merge_defaults_from_json(args.module_dir, args)

    clean_and_populate_params(params, not args.quiet)

    if not args.quiet:
        params_no_password = dict(params)
        params_no_password['password'] = '********'
        print "Installing module '%s':\n%s" % (module_name, json.dumps(params_no_password,
                                                                       indent=4,
                                                                       sort_keys=True))

    ## Make sure the module is in path so it can be imported
    mod_path = os.path.dirname(os.path.abspath(params['module_dir']))
    sys.path.insert(0, mod_path)

    parameters = get_parameters_from_module(module_name_from_module_dir(params['module_dir']))._to_json()

    id_ = apply_module(module_name = os.path.basename(args.module_dir),
                       id_=params.get('id', None),
                       parameters=parameters,
                       **params)

    if not args.quiet:
        print "Successfully uploaded to analysis template '%s' (%s)" % (params['name'], id_)
    else:
        print id_

    params['id'] = id_

    if args.save:
        write_defaults_to_json(params, params['module_dir'])

    sys.path.remove(mod_path)


def apply_module(module_dir, module_name, organization, id_, name, description, parameters, url, username, verify_ssl_certificate, dependency_dir, quiet=False, password=False, save_credentials=False, icon_path=None, **unused_args):
    """Create and/or fetch the analysis template as necessary,
    and upload the specified module to it.

    :param str module_dir: The directory where the module to apply can be found.
    :param str module_name: The name of the module to apply.
    :param str organization: The organization containing the data.
    :param str id_: The id for the module.
    :param str name: A name for the template.
    :param str description: A user-defined description for the template.
    :param dict parameters: Template parameters as dictionary.
    :param str url: The url defining the endpoint.
    :param str username: The username for authentication.
    :param bool verify_ssl_certificate: Whether to use certificate-based authentication.
    :param str dependency_dir: A directory where required modules will be found.
    :param bool quiet: Whether to use interactive mode.
    :param bool password: Whether password authentication is to be used.
    :param bool save_credentials: Whether the credentials should be saved by Eureqa.
    :param bool save_credentials: Whether the credentials should be saved by Eureqa. 
    :param str icon_path: path to an icon to use for the analysis
    """

    eureqa_args = {
        'url': url,
        'user_name': username,
        'organization': organization
        }
    if password:
        eureqa_args['password'] = password
    if save_credentials:
        eureqa_args['save_credentials'] = save_credentials

    eureqa_args['verify_ssl_certificate'] = verify_ssl_certificate == 'true'
    eureqa_args['interactive_mode'] = not quiet

    conn = Eureqa(**eureqa_args)

    # if we were given a pre-existing id to use, try to do so
    template = None
    if id_:
        try:
            template = conn._get_analysis_template(id_)
            template.name = name
            template.description = description
            template.parameters = parameters
            template.set_icon(icon_path)
        except Http404Exception:
            if not quiet:
                print "ID '%s' was provided but no analysis template with such ID exists." % id_
                print 'Therefore ID will be ignored a new analysis template will be created.'

    if not template:
        template = conn.create_analysis_template(name, description,
                                                 Parameters._from_json(parameters) if parameters else Parameters(),
                                                 icon_filepath=icon_path)
        id_ = template._id

    template.set_module(module_name, module_dir, ignore_files=[EUREQA_CONFIG_FILE], additional_modules_paths=dependency_dir, icon_path=icon_path)
    return id_


## If we're being run, do stuff.
## (If we're being imported as a library, don't do stuff.)
if __name__ == "__main__":
    main(sys.argv)
