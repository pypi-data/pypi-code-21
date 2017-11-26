import NodeDefender
import NodeDefender.config.celery 
import NodeDefender.config.database
import NodeDefender.config.general
import NodeDefender.config.logging
import NodeDefender.config.mail
import NodeDefender.config.redis
import configparser
import os

parser = configparser.ConfigParser()
parser.read('NodeDefender.conf')

basepath = os.path.abspath(os.path.dirname('..'))

def write():
    with open('NodeDefender.conf', 'w') as fw:
        parser.write(fw)
