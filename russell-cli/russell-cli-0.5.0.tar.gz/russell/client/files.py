# coding=utf-8
import progressbar
from enum import Enum

try:
    import _thread
except ImportError:
    import thread as _thread
import shutil
import websocket
from russell.client.base import RussellHttpClient
from russell.cli.utils import *
from russell.log import logger as russell_logger
from russell.exceptions import *


SOCKET_STATE = Enum('State', 'INIT UPLOADING FINISH FAILED')
class FsClient(RussellHttpClient):

    def __init__(self):
        self.ws_url = "ws://{host}:{port}".format(host=russell.russell_fs_host,
                                                  port=russell.russell_fs_port)
        self.FILE_NAME = ''
        self.STATE = SOCKET_STATE.INIT
        super(FsClient, self).__init__()

    def on_message(self, ws, message):
        russell_logger.debug(ws.header)
        russell_logger.debug(message)

        def start_sending(*args):
            with open(self.FILE_NAME, 'rb') as f:
                # with progressbar.ProgressBar(maxval=int(ws.header.get('size', 0))) as bar:
                # bar = progressbar.ProgressBar(maxval=int(ws.header.get('size', 0)))
                bar = progressbar.ProgressBar(maxval=int(ws.header.get('size', 0))).start()
                try:
                    total_uploaded_size = 0
                    block_size = 1024 * 1024
                    msg = f.read(block_size)
                    while msg:
                        total_uploaded_size += len(msg)
                        ws.sock.send_binary(msg)
                        msg = f.read(block_size)
                        bar.update(total_uploaded_size)
                except:
                    pass
                finally:
                    pass

        russell_logger.debug('received {}'.format(message))
        resp_json = json.loads(message)
        code = resp_json.get('code')
        if code == 522:
            raise OverPermissionException()
        elif code == 532:
            raise RussellException()
        elif code == 529:
            raise NotFoundException()
        elif code == 506:
            raise AuthenticationException()
        elif code == 507:
            raise Exception('Login expired!')
        elif code == 200:  # to be modified
            if self.STATE == SOCKET_STATE.INIT:
                self.STATE = SOCKET_STATE.UPLOADING
                russell_logger.info('Start uploading...')
                _thread.start_new_thread(start_sending, ())
            else:
                self.STATE = SOCKET_STATE.FINISH
                ws.close()
        else:
            raise ServiceBusyException()

    def clear_archive(self):
        abs_archive_file = os.path.abspath(self.FILE_NAME)
        if os.path.exists(abs_archive_file):
            os.remove(abs_archive_file)

    def on_error(self, ws, error):
        self.STATE = SOCKET_STATE.FAILED
        russell_logger.debug(str(error))

    def on_close(self, ws):
        self.clear_archive()
        russell_logger.debug('close connection to server')

    def on_open(self, ws):
        russell_logger.debug('setup connection to server')


    def socket_upload(self, file_type, filename, access_token, file_id, user_name, data_name):
        self.module_id = file_id
        # compress the folder
        russell_logger.info('compressing files...')
        try:
            shutil.make_archive(base_name=file_id,
                                format='gztar',
                                root_dir=filename,
                                owner=None,
                                group=None,
                                logger=russell_logger)
        except Exception as e:
            raise e
        # compute md5 checksum
        self.FILE_NAME = '{}.tar.gz'.format(file_id)
        hash_code = get_md5_checksum(self.FILE_NAME)
        # compute compressed_size
        compressed_size = os.path.getsize(self.FILE_NAME)
        russell_logger.info("compressed size: {} Bytes".format(compressed_size))
        # setup connection
        # websocket.enableTrace(True)
        web_socket = websocket.WebSocketApp(
            url=self.ws_url + "/{}/{}/".format(file_type, file_id),
            header={
                'access_token': access_token,
                'size': str(compressed_size),
                'hash_code': hash_code,
                'user_name': user_name,
                'data_name': data_name
            },
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        web_socket.on_open = self.on_open
        web_socket.run_forever()

    def get_state(self):
        return self.STATE