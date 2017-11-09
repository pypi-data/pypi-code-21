#!/usr/bin/env python
#coding: utf-8

#from .. import Task

class Processor:

    name = 'hello'
    version = '20171107'
    description = '''hello api desc
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


