#!python

import argparse
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="The directory name")
    parser.add_argument("media_type", help="The media type")

    args = parser.parse_args()

    name = args.name
    media_type = args.media_type

    MetaDataManager.generate_media_directory(name, media_type)
