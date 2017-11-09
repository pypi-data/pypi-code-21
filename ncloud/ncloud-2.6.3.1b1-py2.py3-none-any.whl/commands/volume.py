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
Subcommands for managing volumes.
"""
from __future__ import print_function

import os
from collections import OrderedDict
from functools import partial
from glob import glob

import queue
from builtins import str

from ncloud.commands.command import (Command, Results, string_argument,
                                     build_subparser)
from ncloud.commands.command import LS, SHOW, UL, LN, RM
from ncloud.completers import DatasetCompleter, DirectoriesCompleter
from ncloud.config import VOLUMES, UPLOAD_QUEUE_SIZE
from ncloud.formatting.output import print_table
from ncloud.formatting.time_zone import utc_to_local
from ncloud.util.file_transfer import parallel_upload


class List(Command):
    """
    List available volumes.
    """

    @classmethod
    def parser(cls, subparser):
        dataset_list = subparser.add_parser(LS.name, aliases=LS.aliases,
                                            help=List.__doc__,
                                            description=List.__doc__)
        dataset_list.add_argument("-n", "--count", type=int, default=10,
                                  help="Show up to n most recent volumes. "
                                       "For unlimited set n=0.")
        dataset_list.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, count):
        if count:
            vals = {'count': count}
        else:
            vals = {}
        return List.api_call(config, VOLUMES, params=vals, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['volumes'])


class Show(Command):
    """
    Show volume details for a given volume ID.
    """

    @classmethod
    def parser(cls, subparser):
        dataset_show = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                            help=Show.__doc__,
                                            description=Show.__doc__)
        dataset_show.add_argument(
            "volume_id", type=int, help="ID of volume to show details of."
        ).completer = DatasetCompleter
        dataset_show.add_argument("-r", "--rename",
                                  type=string_argument,
                                  help="Rename a dataset.")

        dataset_show.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, volume_id, rename=None):
        show_path = os.path.join(VOLUMES, str(volume_id))
        if rename:
            vals = {"operation": "replace", "name": rename}
            res = Show.api_call(
                config, show_path, method="PATCH", data=vals, return_json=True)
        else:
            res = Show.api_call(config, show_path, return_json=True)

        for tm in ["created_at", "last_modified"]:
            if tm in res and res[tm] is not None:
                res[tm] = utc_to_local(res[tm])

        return res


class Upload(Command):
    """
    Upload a custom volume to Nervana Cloud.
    """

    @classmethod
    def parser(cls, subparser):
        dataset_upload = subparser.add_parser(UL.name, aliases=UL.aliases,
                                              help=Upload.__doc__,
                                              description=Upload.__doc__)
        dataset_upload.add_argument(
            "path",
            help="Path to a single file or a directory of the data. "
                 "Uploads a single file or a whole directory recursively."
        ).completer = DirectoriesCompleter
        dataset_upload.add_argument(
            "-n", "--name",
            help="Colloquial name of the volume. "
                 "Default name will be given if not provided.")
        dataset_upload.add_argument(
            "--follow-symlinks",
            action="store_true",
            help="follow symlinks while recursively enumerating "
                 "files in the directory to upload.")
        # TODO: support human-readable batch sizes; ex: 5M, 512K
        dataset_upload.add_argument(
            "-b", "--batch-size",
            type=int,
            default=5242880,
            help="File uploads will be sent in batches of this size. "
                 "Defaults to 5242880 bytes.")
        dataset_upload.add_argument(
            "-i", "--volume-id",
            default=None,
            type=str,
            help="Add data to an existing volume "
                 "with this id. This will replace identically-named files."
        ).completer = DatasetCompleter

        dataset_upload.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, path, batch_size, name=None, volume_id=None,
             follow_symlinks=False):

        vals = {"preprocess": False}
        if name:
            vals["name"] = name

        if not glob(path):  # invalid file/directory paths
            print("Invalid file or directory path: {}".format(path))
            return
        if volume_id is None:
            create_dataset = Upload.api_call(
                config, VOLUMES, method="POST", data=vals, return_json=True)
            if "id" not in create_dataset:
                print("Could not create volume.")
                return

            volume_id = str(create_dataset["id"])
            print("Created volume with ID {}.".format(volume_id))

        upload_queue = queue.Queue(maxsize=UPLOAD_QUEUE_SIZE)

        success, failed, total_files = parallel_upload(
            config, path, volume_id, upload_queue, batch_size, follow_symlinks)

        output = OrderedDict([
            ("id", volume_id),
            ("success", success),
            ("failed", failed),
            ("total_files", total_files)
        ])
        return output

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


class Link(Command):
    """
    Link a volume not residing in the Nervana Cloud.
    """

    @classmethod
    def parser(cls, subparser):
        dataset_link = subparser.add_parser(LN.name, aliases=LN.aliases,
                                            help=Link.__doc__,
                                            description=Link.__doc__)
        dataset_link.add_argument(
            "directory",
            help="Network path of the data root directory.")
        dataset_link.add_argument(
            "-n", "--name",
            help="Colloquial name of the volume. "
                 "Default name will be given if not provided.")
        dataset_link.add_argument(
            "-e", "--region",
            help="Region in which volume resides. "
                 "For S3, defaults to us-west-1")

        dataset_link.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, directory, name=None, region=None):
        vals = {"location_path": directory, "preprocess": False}

        if name:
            vals["name"] = name

        if region:
            vals["region"] = region

        res = Link.api_call(
            config, VOLUMES, method="POST", data=vals, return_json=True)
        return res

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


class Remove(Command):
    """
    Remove a linked or uploaded volume.
    """

    @classmethod
    def parser(cls, subparser):
        dataset_remove = subparser.add_parser(RM.name, aliases=RM.aliases,
                                              help=Remove.__doc__,
                                              description=Remove.__doc__)
        dataset_remove.add_argument(
            "volume_id", type=int, help="ID of volume to remove."
        ).completer = DatasetCompleter

        dataset_remove.set_defaults(func=cls.arg_call)

    @staticmethod
    def arg_names():
        return ['volume_id']

    @staticmethod
    def call(config, volume_id):
        remove_path = os.path.join(VOLUMES, str(volume_id))
        res = Remove.api_call(config, remove_path, method="DELETE")
        return res

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


DatasetResults = Results(
    "volumes",
    DatasetCompleter,
    VOLUMES
)
parser = partial(
    build_subparser, 'volume', ['vs', 'v'], __doc__,
    (List, Show, Upload, Link, Remove, DatasetResults)
)
