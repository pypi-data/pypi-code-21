# encoding: utf-8
import json
import logging
import os
import socket
import threading
import time
import uuid

import psutil
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

ZOOKEEPER_HOSTS = None
SIZE = 60 * 24
KEY = 'CTEC_CONSUMER_DATAS'
RECONNECT_INTERVAL = 60
UPLOAD_DATA_INTERVAL = 60

logger = logging.getLogger('default')


class DataAgent(object):
    counter = 0

    def __init__(self, name, desc, app_path, queue, amqp_url):
        self._agent_thread = threading.Thread(target=self.worker)
        self.name = name
        self.desc = desc
        self.app_path = app_path
        self.queue = amqp_url + '/' + queue
        self.__zk_cli = KazooClient(ZOOKEEPER_HOSTS)
        self.__key = str(uuid.uuid4()).replace('-', '')
        self.__process = psutil.Process()

    def worker(self):
        while not self.__zk_cli.connected:
            time.sleep(RECONNECT_INTERVAL)
            try:
                self.__zk_cli.start(5)
                self.__zk_cli.create('/%s/%s' % (KEY, self.__key), ephemeral=True, makepath=True)
            except Exception as e:
                logger.exception('连接zk server异常:%s', e.message)
        try:
            zk_path = '/%s/%s' % (KEY, self.__key)
            datas = {
                'name': self.name,
                'desc': self.desc,
                'app_path': self.app_path,
                'queue': self.queue,
                'cpu': [],
                'mem': [],
                'num_threads': 0,
                'consumer_counter': [],
                'host_ip': socket.gethostbyname(socket.gethostname()) if os.environ.get(
                    'HOST_IP') is None else os.environ.get('HOST_IP')
            }

            while 1:
                cpu = datas.get('cpu')
                mem = datas.get('mem')
                consumer_counter = datas.get('consumer_counter')

                # 更新动态信息，如CPU等
                with self.__process.oneshot():
                    cpu.append([time.time() * 1000, self.__process.cpu_percent()])
                    mem.append([time.time() * 1000, self.__process.memory_percent()])
                    datas['num_threads'] = self.__process.num_threads()
                    consumer_counter.append([time.time() * 1000, DataAgent.counter])

                # 如果数组长度超过指定值，则截断
                if len(cpu) > SIZE:
                    cpu = cpu[len(cpu) - SIZE:]
                    mem = mem[len(cpu) - SIZE:]
                    consumer_counter = consumer_counter[len(cpu) - SIZE:]

                # 更新动态值
                datas['cpu'] = cpu
                datas['mem'] = mem
                datas['consumer_counter'] = consumer_counter

                try:
                    logger.debug('开始上传监控数据，datas=%s', datas)
                    self.__zk_cli.set(zk_path, json.dumps(datas, ensure_ascii=False))
                    # 此处counter不是线程安全的，会比实际数据少，不过为了性能，你懂的
                    DataAgent.counter = 0
                except NoNodeError:
                    logger.warning('session 失效，重新建立node')
                    self.__zk_cli.create('/%s/%s' % (KEY, self.__key), ephemeral=True, makepath=True)
                except Exception as e:
                    logger.exception('上传监控数据异常:%s', e.message)
                logger.debug('上传结束，计数器归零')
                time.sleep(UPLOAD_DATA_INTERVAL)
        except Exception as e:
            logger.exception('监控线程异常:%s', e.message)

    def run(self):
        try:
            self.__zk_cli.start(5)
            self.__zk_cli.create('/%s/%s' % (KEY, self.__key), ephemeral=True, makepath=True)
        except Exception as e:
            logger.exception('连接zk server异常:%s', e.message)

        self._agent_thread.setDaemon(True)
        self._agent_thread.start()
