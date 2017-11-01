import os
from tellurium import antimonyConverter
from tellurium.teconverters import saveInlineOMEX, inlineOmexImporter, SBOError
from errno import EPERM, EIO, ENXIO, EACCES, EFBIG, ENOSPC, EROFS, ENAMETOOLONG
import json

def errnoToMessage(e):
    return {
        EPERM:  'Operation not permitted',
        EIO:    'I/O error',
        ENXIO:  'No such device or address',
        EACCES: 'Permission denied',
        EFBIG:  'File too large',
        ENOSPC: 'No space left on device',
        EROFS:  'Read-only file system',
        ENAMETOOLONG: 'File name too long',
    }[e]

from ipykernel.comm import Comm
class getNotebookLocationComm(Comm):
    def __init__(self, data=None, metadata=None, buffers=None, **kwargs):
        # def printout(s):
        #     with open('/tmp/nterout', 'a') as myfile:
        #         myfile.write(s+'\n')
        # printout('get notebook loc ctor')

        self.location = None

        @self.on_msg
        def _recv(msg):
            try:
                self.location = msg['content']['data']['location']
            except KeyError:
                self.location = ''
            self.close()

        super(getNotebookLocationComm, self).__init__(target_name='get_notebook_location', data=data, metadata=metadata, buffers=buffers, **kwargs)
        import time, zmq
        ipython = get_ipython()
        kernel = ipython.kernel
        while self.location is None:
            time.sleep(0.1)
            from contextlib import contextmanager
            @contextmanager
            def context():
                yield
            with context():
                kernel.do_one_iteration()
            # zmq.eventloop.ioloop.IOLoop.instance()
            # printout('kernel.control_stream {}'.format(kernel.control_stream))
            # kernel..control_stream.flush()
        # return
        return self.location

def getNotebookLocation():
    notebook_location_comm = getNotebookLocationComm()
    notebook_location_comm.close()
    return notebook_location_comm.location

def convert_file_comm(comm, msg):
    """ Handles convert file requests from Tellurium.

    :param comm: The kernel Comm instance
    :param msg: The comm_open message
    """

    # def printout(s):
    #     with open('/tmp/nterout', 'a') as myfile:
    #         myfile.write(s+'\n')
    # printout('message = {}'.format(msg))
    # if 'path' in msg['content']['data']:
    #     printout('importing {}'.format(msg['content']['data']['path']))

    # Register handler for later messages
    @comm.on_msg
    def _recv(msg):
        # Use msg['content']['data'] for the data in the message
        # with open('/tmp/nterout', 'a') as myfile:
        #     myfile.write('import_file_comm _recv\n')
        pass

    def returnError(err):
        'Report error'
        comm.send({'status': 'error', 'error': err})
        comm.close()

    def returnSource(src, format):
        'convert the file and send it back'
        if format not in ['antimony', 'omex', 'python']:
            returnError('Unrecognized format "{}"'.format(format))
        comm.send({'content': {
            'cells': [{
                'source': src,
                'type': format
                }]
            }
        })
        comm.close()

    if not 'target_format' in msg['content']['data']:
        # printout('import_file_comm no target_format')
        returnError('Expected "target_format" in message data payload')
    else:
        # printout('set target_format')
        target_format = msg['content']['data']['target_format']
        if 'path' in msg['content']['data']:
            # given path to file
            file_path = msg['content']['data']['path']
            if target_format == 'python':
                try:
                    with open(file_path) as f:
                        returnSource(f.read(), format='python')
                except OSError as err:
                    try:
                        returnError('{}.'.format(errnoToMessage(err.errno)))
                    except:
                        returnError('Unable to import file.')
                except Exception as e:
                    returnError(str(e))
            elif target_format == 'antimony':
                try:
                    module,sb = antimonyConverter().sbmlFileToAntimony(file_path, addSBO=True)
                except SBOError as e:
                    # try again without SBO
                    try:
                        module,sb = antimonyConverter().sbmlFileToAntimony(file_path, addSBO=False)
                    except:
                        returnError('Unable to import SBML file')
                except Exception as e:
                    returnError('Unable to import SBML file')
                # Antimony pads with a newline for some reason
                returnSource(sb.rstrip(), format='antimony')
            elif target_format == 'cellml':
                # printout('cellml format')
                module,sb = antimonyConverter().cellmlFileToAntimony(file_path)
                # Antimony pads with a newline for some reason
                returnSource(sb.rstrip(), format='antimony')
            elif target_format == 'omex':
                # printout('target_format = omex')
                try:
                    importer = inlineOmexImporter.fromFile(file_path)
                    format = 'omex'
                    if importer.containsSBMLOnly() and importer.numSBMLEntries() == 1:
                        format = 'antimony'
                        # Can't have headers in antimony cell
                        importer.headerless = True
                    source = importer.toInlineOmex(detailedErrors=False)
                    returnSource(source, format=format)
                except Exception as e:
                    # printout('error '+str(e))
                    returnError(str(e))
        elif 'content' in msg['content']['data']:
            # given raw content
            raw_content = msg['content']['data']['content']
            if target_format == 'antimony':
                try:
                    module,sb = antimonyConverter().sbmlToAntimony(raw_content, addSBO=True)
                except SBOError as e:
                    # try again without SBO
                    try:
                        module,sb = antimonyConverter().sbmlToAntimony(raw_content, addSBO=False)
                    except:
                        returnError('Unable to convert SBML file')
                except:
                    returnError('Unable to convert SBML file')
                returnAntimony(sb)
        else:
            # printout('import_file_comm no path or content')
            returnError('Expected "path" or "content" in message data payload')

def save_file_comm(comm, msg):
    """ Handles save file requests from Tellurium.

    :param comm: The kernel Comm instance
    :param msg: The comm_open message
    """

    # def printout(s):
    #     with open('/tmp/nterout', 'a') as myfile:
    #         myfile.write(s+'\n')
    # printout('save_file_comm')

    def returnOkay(path):
        'Report success with written file path'
        # printout('saved {}'.format(path))
        # Antimony pads with a newline for some reason
        comm.send({'status': 'okay', 'file': path})
        comm.close()

    def returnError(err):
        'Report success with written file path'
        # printout('error {}'.format(err))
        # Antimony pads with a newline for some reason
        comm.send({'status': 'error', 'error': err})
        comm.close()

    if  not 'path' in msg['content']['data'] or \
        not 'target_format' in msg['content']['data'] or \
        not 'source_format' in msg['content']['data'] or \
        not 'source_str' in msg['content']['data']:
        # printout('missing info')
        returnError('Missing data for save command')
    else:
        # printout('have info')
        source_format = msg['content']['data']['source_format']
        target_format = msg['content']['data']['target_format']
        source_str    = msg['content']['data']['source_str']
        path      = msg['content']['data']['path']
        if source_format == 'antimony':
            if target_format == 'sbml':
                target_str = antimonyConverter().antimonyToSBML(source_str)[1]
                try:
                    with open(path, 'w') as f:
                        f.write(target_str)
                except OSError as err:
                    try:
                        returnError('{}.'.format(errnoToMessage(err.errno)))
                    except:
                        returnError('Unable to write file.')
            else:
                returnError('Unrecognized target format "{}".'.format(target_format))
        elif source_format == 'omex':
            # printout('src omex')
            try:
                # remove the archive first if it exists
                if os.path.isfile(path):
                    os.remove(path)
                saveInlineOMEX(source_str, path)
                returnOkay(os.path.basename(path))
            except OSError as err:
                try:
                    returnError('{}.'.format(errnoToMessage(err.errno)))
                except:
                    # Unknown OS error
                    # import traceback
                    # printout(traceback.format_exc())
                    returnError('Unable to write file.')
            except:
                # Unknown error
                # import traceback
                # printout(traceback.format_exc())
                returnError('Unable to write file.')
