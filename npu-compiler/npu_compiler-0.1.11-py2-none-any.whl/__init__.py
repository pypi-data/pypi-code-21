#coding: utf-8

from npu_compiler.session import Session
from npu_compiler.config import Config

def run(config_file):
    Config.config(config_file)
    sess = Session()
    sess.run()
    sess.close()

