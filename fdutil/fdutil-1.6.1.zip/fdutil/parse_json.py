
import os
import json
import codecs
import logging_helper

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'

logging = logging_helper.setup_logging()


def sort_json_object(obj):

    """ Example

        # Check if there are any changes
        if not sort_json_object(catalog_feed_data) == sort_json_object(old_catalog_feed_data):
            # There are changes

        else:
            # There are no changes

    :param obj: The json object to sort

    """

    if isinstance(obj, dict):
        return sorted((k, sort_json_object(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(sort_json_object(x) for x in obj)
    else:
        return obj


def write_json_to_file(content,
                       output_dir,
                       filename,
                       backup_dir=None,
                       file_ext=u'json'):

    """ Write some data into a file

    :param content:     str:    Variable containing some data to be written into the file
    :param output_dir:  str:    Directory the file is to be written to
    :param backup_dir:  str:    Directory an existing file of the same name will be moved to (overwrites)
    :param filename:    str:    new files filename
    :param file_ext:    str:    new files extension
    :return:            tuple:  (new file path, backup file path)
    """

    out_file = u'{feed}.{ext}'.format(feed=filename,
                                      ext=file_ext)

    file_path = u'{p}{s}{f}'.format(p=output_dir,
                                    s=os.sep,
                                    f=out_file)

    backup_path = u''

    if backup_dir:

        # Move existing file to backup directory
        if os.path.isfile(file_path):

            backup_path = u'{p}{s}{f}'.format(p=backup_dir,
                                              s=os.sep,
                                              f=out_file)

            if os.path.isfile(backup_path):
                os.remove(backup_path)

            os.rename(file_path,
                      backup_path)

    else:
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Write out new file to output directory
    with codecs.open(file_path, mode=u'wb') as json_file:
        json.dump(content, json_file)

    return file_path, backup_path
