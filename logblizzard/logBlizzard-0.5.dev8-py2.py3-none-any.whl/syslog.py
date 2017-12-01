

import logging
import json
import socket
from logging.handlers import RotatingFileHandler

def syslog(SYSLOG_IP = "0.0.0.0", SYSLOG_PORT = 514, blast_log=True):

	with open('network_cfg.json','r') as nwc:
		nw=json.load(nwc)

	SYSLOG_IP= nw['SYSLOG_IP']
	SYSLOG_PORT=nw['SYSLOG_PORT']

	if blast_log == True:
		with open ('syslog.log','w') as f:
			f.close()

	else:
		pass




	logger = logging.getLogger()
	logger.setLevel(logging.INFO)


	handler = RotatingFileHandler('syslog.log',maxBytes=1000,backupCount=0)
	logger.addHandler(handler)


	sock = socket.socket(socket.AF_INET,
	                     socket.SOCK_DGRAM)
	sock.bind((SYSLOG_IP, SYSLOG_PORT))

	while True:
	   data, addr = sock.recvfrom(2048)
	   data=data.decode()
	   addr=str(addr[0])
	   logmsg={'log_message':data,'orig_addr':addr}
	   logmsg=json.dumps(logmsg)
	   logger.info(logmsg)

if __name__=='__main__':
	syslog()
