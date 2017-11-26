u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import with_statement
from __future__ import absolute_import
import os
import json
from typing import List
from toktokkie.utils.metadata.media_types.Base import Base
from toktokkie.utils.metadata.media_types.TvSeries import TvSeries
from toktokkie.utils.metadata.media_types.AnimeSeries import AnimeSeries
from toktokkie.utils.metadata.media_types.Ebook import Ebook
from toktokkie.utils.metadata.media_types.LightNovel import LightNovel
from io import open


class MetaDataManager(object):
    u"""
    Class that handles the metadata for Media files
    """

    media_types = [Base, TvSeries, AnimeSeries, Ebook, LightNovel]
    u"""
    The various media types that are supported
    """
    media_type_map = {}
    for m in media_types:
        media_type_map[m.identifier] = m

    @staticmethod
    def find_recursive_media_directories(directory, media_type = u""):
        u"""
        Finds all directories that include a .meta directory and
        info.json file below a given directory.
        If a media_type is specified, only those directories containing a
        .meta/type file with the media_type as content are considered

        In case the given directory does not exist or the current user
        has no read access, an empty list is returned

        :param directory:  The directory to check
        :param media_type: The media type to check for
        :return:           A list of directories that are
                           identified as TV Series
        """
        directories = []

        if not os.path.isdir(directory):
            return []

        # noinspection PyUnboundLocalVariable
        try:
            children = os.listdir(directory)
        except (OSError, IOError):  # == PermissionError
            # If we don't have read permissions for this directory,
            # skip this directory
            return []

        if MetaDataManager.is_media_directory(directory, media_type):
            directories.append(directory)
        else:
            # Parse every subdirectory like the original directory recursively
            for child in children:
                child_path = os.path.join(directory, child)
                if os.path.isdir(child_path):
                    directories += \
                        MetaDataManager.find_recursive_media_directories(
                            child_path, media_type
                        )

        return directories

    @staticmethod
    def is_media_directory(directory, media_type = u""):
        u"""
        Checks if a given directory is a Media directory.
        A directory is a Media directory when it contains a .meta directory.
        It will also contain a info.json file which specifies the type of the
        media as well as other metadata

        :param directory:  The directory to check
        :param media_type: The type of media to check for, optional
        :return:           True if the directory is a Media directory,
                           False otherwise
        """
        # noinspection PyUnboundLocalVariable
        try:
            if not os.path.isfile(os.path.join(
                    directory, u".meta", u"info.json"
            )):
                return False
            return True \
                if not media_type \
                else MetaDataManager.is_media_subtype(directory, media_type)

        # Permission Errors or Missing type in info.json (if type specified)
        except (OSError, IOError, KeyError):
            return False

    @staticmethod
    def generate_media_directory(directory, media_type = u"base"):
        u"""
        Makes sure a directory is a media directory of the given type

        :param directory:  The directory
        :param media_type: The media type, if not supplied will default
                           to 'base'
        :raises:           IOError (FileExistsError), if the file exists
                           and is not a directory
        :return:           None
        """
        if not os.path.isdir(directory):
            if os.path.isfile(directory):
                raise IOError(u"Directory already exists and is a File?")
            else:
                os.makedirs(directory)

        if not MetaDataManager.is_media_directory(directory, media_type):

            if not os.path.isdir(os.path.join(directory, u".meta", u"icons")):
                os.makedirs(os.path.join(directory, u".meta", u"icons"))

            MetaDataManager.media_type_map[media_type](directory, True)

    @staticmethod
    def get_media_type(directory):
        u"""
        Determines the media type of a media directory

        :param directory: The directory to check
        :return:          Either the type identifier string, or an empty string
                          if the directory is not a media directory
        """
        try:
            info_file = os.path.join(directory, u".meta", u"info.json")

            if not os.path.isfile(info_file):
                return u""
            else:
                with open(info_file, u'r') as json_file:
                    return json.loads(json_file.read())[u"type"]
        except KeyError:
            return u""

    @staticmethod
    def is_media_subtype(directory, media_type):
        u"""
        Checks if a directory is of a specific media type or subtype.

        Example of a subtype: anime_series is a subtype of tv_series

        :param directory: The directory to check
        :param media_type: The media type/subtype to check
        :return: True if the media directory corresponds to the given type
        """
        try:
            dir_media_type = MetaDataManager.get_media_type(directory)
            dir_media_type_class = \
                MetaDataManager.media_type_map[dir_media_type]
            check_media_type_class = MetaDataManager.media_type_map[media_type]
            if issubclass(dir_media_type_class, check_media_type_class):
                dir_media_type_class(directory)  # Check if valid JSON
                return True

        except KeyError:
            return False
        except AttributeError:
            return False

    @staticmethod
    def autoresolve_directory(directory):
        u"""
        Automatically resolves the type of a directory

        :param directory: The directory for which to resolve the metadata type
        :return: The Metadata Object OR None if the directory is not a valid
                 metadata directory
        """
        the_type = MetaDataManager.get_media_type(directory)
        if the_type in MetaDataManager.media_type_map:
            return MetaDataManager.media_type_map[the_type](directory)
        else:
            return None
