import os
import gzip

import fastr
from fastr.core.serializable import Serializable
from fastr.core.tool import Tool


def verify_resource_loading(filename):
    name, ext = os.path.splitext(filename)

    # Check if file is gzipped
    if ext == '.gz':
        compressed = True
        name, ext = os.path.splitext(filename)
    else:
        compressed = False

    # Read file data
    fastr.log.info('Trying to read file with compression {}'.format('ON' if compressed else 'OFF'))
    if compressed:
        try:
            with gzip.open(filename, 'r') as file_handle:
                data = file_handle.read()
        except:
            fastr.log.error('Problem reading gzipped file: {}'.format(filename))
            return False
    else:
        try:
            with open(filename, 'r') as file_handle:
                data = file_handle.read()
        except:
            fastr.log.error('Problem reading normal file: {}'.format(filename))
            return False

    fastr.log.info('Read data from file successfully')

    # Try to read tool doc based on serializer matching the extension
    serializer = ext[1:]
    fastr.log.info('Trying to load file using serializer "{}"'.format(serializer))

    if serializer not in Tool.dumpfuncs:
        fastr.log.error('No matching serializer found for "{}"'.format(serializer))
        return False

    load_func = Serializable.dumpfuncs[serializer].loads

    try:
        doc = load_func(data)
    except Exception as exception:
        fastr.log.error('Could not load data using serializer "{}", encountered exception: {}'.format(serializer,
                                                                                                      exception))
        return False

    return doc


def verify_tool(filename):
    """
    Verify that a file
    """
    # Load the file
    doc = verify_resource_loading(filename)

    if not doc:
        fastr.log.error('Could not load data successfully from  {}'.format(filename))
        return False

    # Match the data to the schema for Tools
    fastr.log.info('Validating data against Tool schema')
    serializer = Tool.get_serializer()

    try:
        doc = serializer.instantiate(doc)
    except Exception as exception:
        fastr.log.error('Encountered a problem when verifying the Tool schema: {}'.format(exception))
        return False

    # Create the Tool object as the final test
    fastr.log.info('Instantiating Tool object')
    try:
        tool = Tool(doc)
        tool.filename = filename
    except Exception as exception:
        fastr.log.error('Encountered a problem when creating the Tool object: {}'.format(exception))
        return False

    fastr.log.info('Loaded tool {} successfully'.format(tool))

    fastr.log.info('Testing tool...')
    try:
        tool.test()
    except fastr.exceptions.FastrValueError as e:
        fastr.log.error('Tool is not valid: {}'.format(e))

    return True