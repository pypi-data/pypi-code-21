#!/usr/bin/env python
#coding: utf-8

class Processor:
    description = '''
    test processor
    '''
    submit_format = '''
    '''
    response_format = '''
    '''
    name = 'testprocessor'
    version = '20171107'

    def __init__(self):
        pass

    @staticmethod
    def proc(task_id, data):
        print('=====processor test=====')
        print(task_id)
        import time
        for i in range(10):
            print(i)
            time.sleep(1)
        print(data)
        print('=====processor test=====')
