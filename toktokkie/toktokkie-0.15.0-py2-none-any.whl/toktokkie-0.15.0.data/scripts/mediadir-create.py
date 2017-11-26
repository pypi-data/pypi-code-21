#!python

from __future__ import absolute_import
import argparse
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager

if __name__ == u"__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(u"name", help=u"The directory name")
    parser.add_argument(u"media_type", help=u"The media type")

    args = parser.parse_args()

    name = args.name
    media_type = args.media_type

    MetaDataManager.generate_media_directory(name, media_type)
