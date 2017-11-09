#!/usr/bin/env python
#coding: utf-8

#from .. import Task
import os

class Processor:

    name = 'fp'
    version = '20171108'
    description = '''fp api desc
    '''
    submit_format = '''
    post: task=...
    '''
    response_format = '''
    {'taskid': task}
    '''

    def __init__(self):
        pass

    @staticmethod
    def proc(task_id, data): 
        print('=====processor hello=====')
        print(task_id)
        print(data)
        print('=====processor hello=====')


