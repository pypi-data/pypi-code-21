# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-
"""
Subcommands for training, deploying, and otherwise managing models - this is
the default subcommand.
"""
from __future__ import print_function
from builtins import str

import base64
from functools import partial
import io
import json
import logging
import os
import py_compile
import re
import requests
from shutil import copyfile
import sys
import time
from zipfile import ZipFile

from ncloud.commands.command import (BaseList, Command, Results,
                                     build_subparser, string_argument,
                                     collection_argument)
from ncloud.commands.command import SHOW, TRAIN, STOP, IMPORT, DEPLOY
from ncloud.formatting.time_zone import utc_to_local
from ncloud.formatting.output import print_table
from ncloud.util.file_transfer import multipart_upload
from ncloud.config import MODELS, STREAM_PREDICTIONS
from ncloud.completers import (HTTPCompleter, ModelCompleter,
                               NeonVersionCompleter)

logger = logging.getLogger()


class Show(Command):
    """
    Show model details for a given model ID.
    """
    @classmethod
    def parser(cls, subparser):
        show_model = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                          help=Show.__doc__,
                                          description=Show.__doc__)
        show_model.add_argument(
            "model_id",
            type=int,
            help="ID of model to show details of."
        ).completer = ModelCompleter
        show_model.add_argument("-l", "--console-log", action="store_true",
                                help="Show console log from model runtime.")
        show_model.add_argument("-n", "--neon-log", action="store_true",
                                help="Show neon log file.")
        show_model.add_argument("-r", "--rename",
                                type=string_argument,
                                help="Rename a model.")
        show_model.add_argument('-z', "--model-zoo", action="store_true",
                                help="Show model in the model zoo.")
        show_model.add_argument('-L', "--console-log-follow",
                                action="store_true",
                                help="Show console log data as the " +
                                      "output grows; similar to tail -f " +
                                      "on a UNIX-based machine.")
        show_model.add_argument('-N', "--neon-log-follow", action="store_true",
                                help="Show neon log data as the output " +
                                     "grows; similar to tail -f on a " +
                                     "UNIX-based machine.")

        show_model.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id, console_log=False, console_log_follow=False,
             neon_log=False, neon_log_follow=False, rename=None,
             model_zoo=False):
        model_id = str(model_id)
        if console_log or neon_log or console_log_follow or neon_log_follow:
            results_path = os.path.join(MODELS, model_id, "results")
            vals = {}
            if model_zoo:
                vals["model_zoo"] = "True"
            # if we are following neon or console, then set those vals
            # to true as well
            neon_log |= neon_log_follow
            console_log |= console_log_follow
            if not (console_log_follow or neon_log_follow):
                vals.update({
                    "format": "zip",
                    "filter": ["*.log"],
                })
                log_data = Show.api_call(config, results_path, params=vals)
                # if we aren't streaming, then the data returned is
                # zipfile bytes
                zipbytes = io.BytesIO(log_data)
                archive = ZipFile(zipbytes)
                ziplogs = archive.namelist()

                # has to be done here because of pytest shenanigans
                # pytest replaces sys.stdout specifically
                write = getattr(sys.stdout, 'buffer', sys.stdout).write
                # looks like we either read from neon.log or launcher.log
                # why never console.log?
                if neon_log:
                    try:
                        write(archive.read('neon.log'))
                    except KeyError:
                        logger.warning("attempting to view non-existent " +
                                       "neon.log")
                else:
                    log = 'launcher.log'
                    if log in ziplogs:
                        write(archive.read(log))
            else:
                # if we are streaming, then hit our endpoint
                # /models/<model_id>/results/<log_file> so we
                # only fetch the data we need next in the file
                # as opposed to the whole file again and again
                if console_log_follow:
                    log_file = 'launcher.log'
                else:
                    log_file = 'neon.log'
                # we are gonna request the log file itself
                results_path += "/" + log_file

                # make the initial request of the object!
                # we will get back data in the format of:
                # {'results': FILE_DATA_HERE, 'offset': END_OF_FILE_HERE}
                # so we can fetch from the end of the file!
                # keep things in the same session so we can
                # make use of keep-alive
                sess = requests.session()
                result, status_code = Show.api_call(
                    config, results_path, params=vals, stream=True,
                    session=sess, return_status_code=True,
                    console_log_follow=console_log_follow)
                if not result:
                    if status_code == 500:
                        print("No logs available.")
                    else:
                        print("Waiting for job to start...")
                    return
                log_data = json.loads(result)
                if log_data.get('status') == 'Model not found':
                    print("Model not found.")
                    return
                # compile regex of a line that includes an epoch result
                # also compile regex of a finished epoch result
                epoch_re = re.compile('Epoch \d+\s+')
                finished_epochs_re = re.compile('(\d+)[/](\d+)\s+batches')
                old_result = {}
                while True:
                    try:
                        # if we are logging immediately, then keep
                        # trying to fetch the tailing logs
                        # even though they might not be here yet
                        # only applies to console_log_follow (-L)
                        # TODO: why does custom code return 404...
                        if (status_code in {400, 404} and console_log_follow):
                            # put dummy data here, we'll retry again at
                            # the bottom of this loop
                            log_data = {'results': '', 'offset': 0}
                        elif (status_code in {500} and console_log_follow):
                            # put dummy data here, but redo the last line
                            log_data = {'results': '',
                                        'offset': log_data['offset']-1}
                        # continue to print out the file data and request
                        # the next part of the file!
                        # if we find epoch data returned, then we need to
                        # reset the offset back to the beginning of the
                        # last epoch line if the epochs aren't done
                        # completing yet
                        results = log_data['results']
                        # where we will fetch next; might be reset
                        # back to the beginning of the epoch line if we aren't
                        # done displaying that epoch yet
                        offset = log_data['offset']

                        # decode the last line as unicode so we can
                        # check the count of missing little boxes
                        # that represent how many epochs have trained
                        # so far
                        last_line = results[results
                                            .rfind('\n') + 1:]
                        if epoch_re.match(last_line):
                            # check to see if we have finished this line
                            finished_epoch = re.search(finished_epochs_re,
                                                       last_line)
                            if finished_epoch:
                                # if we've finished the line, then
                                # print carriage return unless the groups match
                                batch_num, batch_total = \
                                    finished_epoch.groups()
                                if batch_num != batch_total:
                                    # set the offset back to the length of
                                    # the line encoded as utf-8.
                                    # Unicode representation is different than
                                    # string representation in terms of bytes
                                    offset -= len(last_line.encode('utf-8'))
                                    # add a carriage return so we can write
                                    # over this epoch data as it grows
                                    results += '\r'

                        # only print if we actually have more data
                        if results:
                            print(results, end="")

                        vals['offset'] = offset
                        result, status_code = Show.api_call(
                            config, results_path, params=vals, stream=True,
                            session=sess, return_status_code=True,
                            console_log_follow=console_log_follow)
                        if status_code == 202:
                            break
                        if not result or result == old_result:
                            logger.info("Waiting for training logs...")
                            time.sleep(1)
                            continue
                        old_result = result
                        log_data = json.loads(result)
                    except KeyboardInterrupt:
                        # once the user terminates the program, exit gracefully
                        sys.exit(0)

        else:
            show_path = os.path.join(MODELS, str(model_id))
            if rename:
                vals = {"operation": "replace", "name": rename}
                # yes, this will fail
                if model_zoo:
                    vals["model_zoo"] = "True"
                res = Show.api_call(config, show_path, method="PATCH",
                                    data=vals, return_json=True)
            else:
                vals = {}
                if model_zoo:
                    vals["model_zoo"] = "True"
                res = Show.api_call(
                    config, show_path, data=vals, return_json=True)

            try:
                fstr = '{0:g}'.format(res['epochs_completed'])
                res['epochs_completed'] = fstr
            except ValueError:
                # prior to helium v1.1.0, we only returned a string
                pass
            for tm in ["train_request", "train_start", "train_end"]:
                if tm in res and res[tm] is not None:
                    res[tm] = utc_to_local(res[tm])
            return res


class List(BaseList):
    """
    List all submitted, queued, and running models.
    """
    @classmethod
    def parser(cls, subparser):
        list_models = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)

        list_models_type = list_models.add_mutually_exclusive_group()
        list_models_type.add_argument("--done", action="store_true",
                                      help="Show only models finished "
                                           "training.")
        list_models_type.add_argument("--training", action="store_true",
                                      help="Show only training models.")
        list_models.add_argument("-t", "--tenant_ids", type=int, nargs="+",
                                 help="Tenant(s) to view models for. Enter 0 "
                                      "for all tenants. Only applies to users "
                                      "with admin privileges.")
        list_models_type.add_argument("--details", action="store_true",
                                      help="Show more details about models.")
        list_models_type.add_argument("--all-users", action="store_true",
                                      help="Show models from all users.")
        list_models_type.add_argument('-z', "--model-zoo", action="store_true",
                                      help="List all models in the model zoo.")
        list_models.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, details=False, done=False, training=False,
             model_zoo=False, tenant_ids=None, all_users=False):
        # get things from the parent class
        vals = List.BASE_ARGS
        vals.update({'details': details, 'model_zoo': model_zoo})

        if done:
            vals["filter"] = ["Completed", "Error", "Deploying", "Deployed",
                              "Undeploying", "Imported"]
        elif training:
            vals["filter"] = ["Preparing Data (1/4)", "Preparing Data (2/4)",
                              "Preparing Data (3/4)", "Preparing Data (4/4)",
                              "Queued", "Running"]
        else:
            vals["filter"] = ["Received", "Preparing Data (1/4)",
                              "Preparing Data (2/4)", "Preparing Data (3/4)",
                              "Preparing Data (4/4)", "Submitted", "Queued",
                              "Running", "Removed", "Completed", "Error",
                              "Deploying", "Deployed", "Undeploying",
                              "Imported"]
        vals["tenant_ids"] = tenant_ids
        vals["all_users"] = all_users

        return List.api_call(config, MODELS, params=vals, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            # offset is used in pagination of model list results
            offset = res.get('offset')
            if offset:
                if offset != -1:
                    print('Model offset: {}'.format(offset))
                else:
                    print('No more models.')
            model_results = res.get('models')
            if model_results:
                print_table(model_results)
            else:
                print_table(res)


class Train(Command):
    """
    Submit a deep learning model for training.
    """
    @classmethod
    def parser(cls, subparser):
        train = subparser.add_parser(TRAIN.name, aliases=TRAIN.aliases,
                                     help=Train.__doc__,
                                     description=Train.__doc__)
        train.add_argument("-n", "--name",
                           type=string_argument,
                           help="Colloquial name of the model. Default"
                                " name will be given if not provided.")
        train.add_argument("--datasets", action="append",
                           type=collection_argument,
                           help="List of dataset ids for training and"
                                " testing. Example: train:10, test:11.")
        train.add_argument(
            "-v", "--volume-id",
            help="ID of volume to use."
        )
        train.add_argument(
            "-d", "--dataset-id",
            help="[DEPRECATED] Please see --volume-id."
        )
        train.add_argument(
            "--validation-percent",
            default=.2,
            help="[DEPRECATED] Ignored."
        )
        train.add_argument("-e", "--epochs",
                           help="Number of epochs to train this model. "
                                "[deprecated]")
        train.add_argument("-S", "--resume-snapshot",
                           metavar=('SNAPSHOT_NUMBER',),
                           help="Resume training from this snapshot number.")
        train.add_argument("-z", "--batch-size",
                           help="Mini-batch size to train this model. "
                                "[deprecated]")
        train.add_argument(
            "-f", "--framework-version",
            help="Neon tag, branch or commit to use."
        ).completer = NeonVersionCompleter
        train.add_argument(
            "-m", "--mgpu-version",
            help="MGPU tag, branch or commit to use, if 'gpus' > 1."
        )
        train.add_argument("--aeon_version",
                           help="Aeon tag, branch, or commit to use.")
        train.add_argument("-a", "--args", help="Neon command line arguments."
                                                " [deprecated]")
        train.add_argument("-i", "--resume-model-id",
                           help="Start training a new model using the state "
                                "parameters of a previous one.")
        train.add_argument("-g", "--gpus", default=1,
                           help="Number of GPUs to train this model with.")
        train.add_argument("-r", "--replicas", default=0,
                           help="Number of replicas of the main process to "
                                "invoke.  0 means use standard process, 1 "
                                "means use a parameter server, 2-N means "
                                "use peer-to-peer communication.")
        train.add_argument(
            "-u", "--custom-code-url",
            help="URL for codebase containing custom neon "
                 "scripts and extensions."
        ).completer = HTTPCompleter
        train.add_argument("-c", "--custom-code-commit", default="master",
                           help="Commit ID or branch specifier for custom "
                                "code repo.")
        train.add_argument("--model-count", default=1, type=int,
                           help="The number of models to create.")
        train.add_argument("-L", "--log_immediately", action="store_true",
                           help="Immediately start tailing model train "
                                "logs. Triggers an `ncloud model show -L` "
                                "call on the trained model automatically.")
        train.add_argument("-p", "--package", help="Run custom "
                           "dependencies as if they were a python "
                           "package. If set, <filename> is a folder "
                           "with a python package structure (ie "
                           "__main__.py is your training script "
                           "and it's in a folder alongside "
                           "utils.py.) Required if not "
                           "passing in a single filename to train. "
                           "See: https://docs.python.org/3/library"
                           "/__main__.html",
                           action='store_true')
        train.add_argument("-s", "--main-file", type=string_argument,
                           help="Optionally used with -p arg. Ignored "
                                "otherwise. Treats passed file as "
                                "the __main__.py file for training. Must "
                                "exist inside training folder.")
        train.add_argument("filename", type=string_argument,
                           help=".yaml, .py script file, or folder for Neon "
                                "to execute.")
        train.add_argument("arguments", nargs='*',
                           help="Neon command line arguments (prefix flag "
                                "start with '--').")

        train.set_defaults(func=cls.arg_call)

    @classmethod
    def check_valid_python_and_return_extension(cls, filename):
        """helper function used to make sure we have valid python
           files we are training. Also returns file extension
           for further processing
        """
        extension = os.path.splitext(filename)[1][1:]
        if extension == "py":
            try:
                py_compile.compile(filename, doraise=True)
            except py_compile.PyCompileError as pe:
                print(pe)
                sys.exit(1)
        # skip yaml syntax checking and instead do it server side to
        # keep third party libraries to a minimum (pyyaml / libyaml).

        return extension

    @staticmethod
    def call(config, filename, package=False, main_file=None, gpus=1,
             replicas=0, framework_version=None, mgpu_version=None,
             aeon_version=None, name=None, datasets=None, volume_id=None,
             dataset_id=None, validation_percent=None, custom_code_url=None,
             args=None, arguments=None, resume_model_id=None, epochs=None,
             resume_snapshot=None, batch_size=None, custom_code_commit=None,
             model_count=1, log_immediately=False):

        vals = {
            "filename": filename,
            "gpus": gpus,
            "replicas": replicas
        }

        if package:
            # going to make a zip file so we can parse dependencies of
            # training scripts
            main_file_path = ''
            all_files = []
            temp_main = None
            for dirpath, dirnames, files in os.walk(filename):
                for file in files:
                    full_path = os.path.join(dirpath, file)
                    Train.check_valid_python_and_return_extension(
                        full_path)
                    if file == '__main__.py':
                        main_file_path = full_path.replace('__main__.py', '')
                    elif main_file and file == main_file:
                        main_file_path = full_path.replace(file, '')
                        temp_main = os.path.join(main_file_path, '__main__.py')
                        copyfile(full_path, temp_main)
                        all_files.append(temp_main)
                    if not full_path.endswith('.pyc'):
                        all_files.append(full_path)
            if main_file_path:
                # this fixes package names like ../myPackage/
                zip_file = os.path.basename(os.path.normpath(filename)) + \
                    '.zip'
                with ZipFile(zip_file, 'w') as fi:
                    for each_file in all_files:
                        # need everything relative to __main__.py path
                        fi.write(each_file, each_file.replace(
                            main_file_path, ''))
                with open(zip_file, 'rb') as fi:
                    # NOTE: do we want a filesize cap here?
                    vals['zip'] = base64.b64encode(fi.read())
                if temp_main:
                    os.remove(temp_main)
            elif not main_file:
                raise ValueError("invalid module: __main__.py not found, "
                                 "more info <https://docs.python.org/3/library"
                                 "/__main__.html>")
            else:
                raise ValueError("Main file not found in package!")

            vals["filename"] = zip_file
            os.remove(zip_file)
        else:
            # we are training a file with no additional file dependencies
            if custom_code_url is None:
                extension = Train.check_valid_python_and_return_extension(
                    filename)
                if extension in ["py", "yaml"]:
                    with open(filename, "r") as model_file:
                        vals[extension] = model_file.read()

            vals["filename"] = filename

        if framework_version:
            vals["framework_version"] = framework_version

        if mgpu_version:
            vals["mgpu_version"] = mgpu_version

        if aeon_version:
            vals["aeon_version"] = aeon_version

        if name:
            vals["name"] = name

        if volume_id:
            vals["volume_id"] = volume_id

        if datasets:
            vals["datasets"] = json.dumps(datasets)

        if args or arguments:
            vals["args"] = (args or '') + ' '.join(arguments or [])

        if resume_model_id:
            vals["resume_model_id"] = resume_model_id

        if epochs:
            vals["epochs"] = epochs

        if resume_snapshot and resume_model_id is None:
            raise ValueError('Must resume a model id '
                             'when resuming a snapshot.')
        if resume_snapshot:
            vals["resume_snapshot"] = resume_snapshot

        if batch_size:
            vals["batch_size"] = batch_size

        if custom_code_url:
            vals["custom_code_url"] = custom_code_url
            vals["custom_code_cmd"] = filename if not package else None

        if custom_code_commit:
            vals["custom_code_commit"] = custom_code_commit

        rets = []
        for _ in range(model_count):
            rets.append(
                Train.api_call(
                    config, MODELS, method="POST", data=vals,
                    return_json=True)
            )

        return rets

    @staticmethod
    def display_after(config, args, res):
        print_table(res)

        if args.log_immediately:
            print('Beginning log tailing...\n')
            # NOTE: only works for training 1 model because otherwise
            # how do you display all the logs?
            # launch an `ncloud m s -L {id}` after training
            Show.call(
                config, res[0]['id'], console_log_follow=True)


class Stop(Command):
    """
    Stop training a model given a model ID.
    """
    @classmethod
    def parser(cls, subparser):
        stop_training = subparser.add_parser(STOP.name, aliases=STOP.aliases,
                                             help=Stop.__doc__,
                                             description=Stop.__doc__)
        stop_training.add_argument("model_id", help="ID of model to stop.",
                                   type=int, nargs='?')
        stop_training.add_argument("-a", "--all-models", action="store_true",
                                   help="Stop all model IDs you have " +
                                   "access to")
        stop_training.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id=None, all_models=False):
        model_id = str(model_id)

        # if we want to delete just one model
        if not all_models:
            if not model_id:
                print("Missing model ID!!")
                sys.exit(1)
            endpoint = MODELS + model_id
        else:
            # if we delete all models
            endpoint = MODELS + 'all'
        return Stop.api_call(
            config, endpoint, method="DELETE", return_json=True)


class Import(Command):
    """
    Import a previously trained model.
    """
    @classmethod
    def parser(cls, subparser):
        i_pars = subparser.add_parser(IMPORT.name, aliases=IMPORT.aliases,
                                      help=Import.__doc__,
                                      description=Import.__doc__)
        i_pars.add_argument("input",
                            help="Serialized neon model filename or url "
                                 "to import.")
        i_pars.add_argument("-e", "--epochs",
                            help="Number of epochs imported model trained. "
                                 "(amount originally requested)")
        i_pars.add_argument("-n", "--name", type=string_argument,
                            help="Colloquial name of the model. Default "
                                 "name will be given if not provided.")

        i_pars.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, input, epochs=None, name=None):
        vals = dict()
        if epochs:
            vals["epochs_requested"] = epochs
        if name:
            vals["name"] = name

        def import_model(vals, files=None):
            return Import.api_call(config, MODELS + "import", method="POST",
                                   data=vals, files=files, return_json=True)

        if input.startswith("http") or input.startswith("s3"):
            vals["model_url"] = input
            res = import_model(vals)
        elif os.path.exists(input):
            chunksize = 5242880

            basename = os.path.basename(input)
            if os.path.getsize(input) <= chunksize:
                files = [('model_file', (basename, open(input, "rb")))]
                res = import_model(vals, files)
            else:
                vals['multipart'] = True
                res = import_model(vals)
                print("Model ID: {}".format(res['id']))
                multipart_id = res['multipart_id']

                res = multipart_upload(config, input, multipart_id, chunksize)
        else:
            print("no/invalid input model specified")
            sys.exit(1)

        return res

    @staticmethod
    def display_before(conf, args):
        print("importing (may take some time)...")


class Deploy(Command):
    """
    Make a trained model available for generating predictions against.
    """
    @classmethod
    def parser(cls, subparser):
        deploy = subparser.add_parser(
            DEPLOY.name, aliases=DEPLOY.aliases,
            help=Deploy.__doc__, description=Deploy.__doc__
        )
        deploy.add_argument(
            "model_id",
            type=int,
            help="ID of model to deploy."
        ).completer = ModelCompleter
        deploy.add_argument(
          "-g", "--gpus",
          default=0,
          type=int,
          help="Number of GPUs to use to generate predictions.  Defaults to 0 "
               "(use CPU only)."
        )
        deploy.add_argument(
            "-v", "--volume-id",
            type=int,
            help="ID of volume to include."
        )
        deploy.add_argument(
            "-d", "--dataset-id",
            help="[DEPRECATED] Please see --volume-id."
        )
        deploy.add_argument(
            "-f", "--extra-files",
            help="Zip of extra files to include in the deployment."
        )
        deploy.add_argument(
            "--framework-version",
            help="Neon tag, branch or commit to use."
        )
        deploy.add_argument(
            "--custom-code-url",
            help="URL for codebase containing custom neon scripts and "
                 "extensions."
        )
        deploy.add_argument(
            "--custom-code-commit",
            default="master",
            help="Commit ID or branch specifier for custom code repo."
        )

        deploy.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id, gpus=0, volume_id=None, dataset_id=None,
             extra_files=None, framework_version=None, custom_code_url=None,
             custom_code_commit=None):

        vals = {"model_id": model_id, "gpus": gpus}

        if volume_id is not None:
            vals["volume_id"] = volume_id

        files = None
        if extra_files is not None:
            files = [('extra_files', (os.path.basename(extra_files),
                     open(extra_files, "rb")))]

        if framework_version is not None:
            vals["framework_version"] = framework_version

        if custom_code_url is not None:
            vals["custom_code_url"] = custom_code_url

        if custom_code_commit is not None:
            vals["custom_code_commit"] = custom_code_commit

        return Deploy.api_call(
            config, STREAM_PREDICTIONS, method="POST", data=vals,
            files=files, return_json=True)


ModelResults = Results(
    "model",
    ModelCompleter,
    MODELS
)
parser = partial(
    build_subparser, 'model', ['m'], __doc__,
    (Show, List, Train, Stop, Import, ModelResults, Deploy)
)
