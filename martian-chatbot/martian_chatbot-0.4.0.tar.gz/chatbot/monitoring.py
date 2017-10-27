import psutil
import time
import requests
import logging
import uptime
import os
import datetime

from threading import Thread
from chatbot.utils.database_utils import DatabaseUtils

class ChatbotMonitoring:

    def __init__(self, pid, config):
        self.logFile = config.monitoring['log']
        self.process = psutil.Process(pid)
        self.dbname = config.monitoring['dbname']
        self.interval = config.monitoring['interval']
        self.monitor = Thread(target=self.run, name='Monitoring')
        self.url = config.monitoring['monitor_url']
        self.db_utils = DatabaseUtils(config.database, config.facebook['access_token'])
        self.ip = requests.get('https://api.ipify.org').text

    def start_monitoring(self):
        self.monitor.start()

    def run(self):
        while True:
            self.check_process()
            self.check_logs()
            self.check_server()
            time.sleep(self.interval)


    def check_process(self):
        logging.debug(' Started process check.')

        data = {
            'process_pid': self.process.pid,
            'dbname': self.dbname,
            'cpu': self.process.cpu_percent(),
            'ram': self.process.memory_info(),
            'status': self.process.status(),
            'num_threads': self.process.num_threads(),
            'connections': len(self.process.connections())
        }
        try:
            r = requests.post(self.url + '/process', json=data)
            logging.debug(' /process: {}'.format(r.status_code))
        except Exception as e:
            logging.error(' /process: {}'.format(e))



    def check_logs(self):
        logging.debug(' Started logs check.')

        users = self.db_utils.get_users()
        logFile = open(self.logFile, 'r')
        data = logFile.read()
        with open(self.logFile, 'w') as file:
            file.truncate()
        if 'Incoming message!' in data:
            for message in data.split('Incoming message!')[1:]:
                user_id = message.split('ID: ')[1].split('\n')[0]
                data = {
                    'write': True,
                    'user_id': user_id,
                    'dbname': self.dbname,
                    'db_users': len(users)
                }
                try:
                    r = requests.post(self.url + '/logs', json=data)
                    logging.info(' /logs: {}'.format(r.status_code))
                except Exception as e:
                    logging.error(' /logs: {}'.format(e))
        else:
            data = {
                'write': False,
                'dbname': self.dbname,
                'db_users': len(users)
            }
            try:
                r = requests.post(self.url + '/logs', json=data)
                logging.debug(' /logs: {}'.format(r.status_code))
            except Exception as e:
                logging.error(' /logs: {}'.format(e))



    def check_server(self):
        logging.debug(' Started server check.')

        try:
            buffers = psutil.virtual_memory().buffers
            cached = psutil.virtual_memory().cached
            num_connections = len(psutil.net_connections())
        except:
            buffers = 0
            cached = 0
            num_connections = 0

        data = {
            'ip': self.ip,
            'chatbot_name': self.dbname,
            'uptime': uptime.uptime(),
            'num_processes': len(psutil.pids()),
            'loadavg_1': os.getloadavg()[0],
            'loadavg_5': os.getloadavg()[1],
            'loadavg_15': os.getloadavg()[2],
            'cpu_percent_used': psutil.cpu_percent(),
            'cpu_percent_idle': psutil.cpu_times_percent().idle,
            'cpu_num_cores': len(psutil.cpu_percent(percpu=True)),
            'vmem_total': psutil.virtual_memory().total,
            'vmem_available': psutil.virtual_memory().available,
            'vmem_percent': psutil.virtual_memory().percent,
            'vmem_used': psutil.virtual_memory().used,
            'vmem_free': psutil.virtual_memory().free,
            'vmem_buffered': buffers,
            'vmem_cached': cached,
            'disk_total': psutil.disk_usage('/').total,
            'disk_used': psutil.disk_usage('/').used,
            'disk_free': psutil.disk_usage('/').free,
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_read_bps': psutil.disk_io_counters().read_bytes / psutil.disk_io_counters().read_time,
            'disk_write_bps': psutil.disk_io_counters().write_bytes / psutil.disk_io_counters().write_time,
            'net_sent': psutil.net_io_counters().packets_sent,
            'net_recv': psutil.net_io_counters().packets_recv,
            'net_errin': psutil.net_io_counters().errin,
            'net_errout': psutil.net_io_counters().errout,
            'net_dropin': psutil.net_io_counters().dropin,
            'net_dropout': psutil.net_io_counters().dropout,
            'net_connections': num_connections

        }

        try:
            r = requests.post(self.url + '/server', json=data)
            logging.debug(' /server: {}'.format(r.status_code))
        except Exception as e:
            logging.error(' /server: {}'.format(e))

