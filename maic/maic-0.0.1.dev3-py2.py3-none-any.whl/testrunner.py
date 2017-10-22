#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
from time import sleep
from datetime import datetime, timedelta
from multiprocessing import Process, Manager

from requests_futures.sessions import FuturesSession

from maic.assertion import Assertion
from maic.database.store import TestCase, TestStore


class TestRunner(Assertion):
    def __init__(self,
                 name='',
                 environment='',
                 log=True,
                 connection=None,
                 timeout=30,
                 workers=2,
                 db_log=False,
                 categories=None):
        super(TestRunner, self).__init__()
        self.store = TestStore(connection, db_log)
        self.test = self.store.create_run(name, environment)
        self.log = log
        self.session = FuturesSession()
        self.running_cases = []
        self.timeout = timeout
        self.has_failed = False
        self.workers = workers
        self.stored_cases = []
        self.all_processes = []
        self.running = []
        self.running_now = []
        self.process_cases = []
        self.finished = []
        self.manager = Manager()
        self.cases = self.manager.list([])
        self.data = self.manager.dict({})
        self.categories_filter = categories

    def _get_cases(self):
        items = []
        for name, f in inspect.getmembers(self):
            if getattr(f, 'is_case', None):
                if (self.categories_filter is not None and
                        isinstance(self.categories_filter, list) and
                        len(self.categories_filter) > 0):
                    if getattr(f, 'category', '') not in self.categories_filter:
                        continue
                items.append(f)
        return items

    def _log(self, message=''):
        if self.log:
            print(message)

    def _expire_case(self, expired_case):
        expired_case['process'].terminate()
        expired_case['case'].end(success=False, details={'error': 'Time out!'})
        self.store.save(expired_case['case'])
        self.has_failed = True

    def _fetch_stored_case(self, case_id):
        for item in self.stored_cases:
            if item.id == case_id:
                return item
        return None

    def _process_test_result(self):
        while len(self.cases) > 0:
            new_case = self.cases.pop()
            original_case = self._fetch_stored_case(new_case.get('id'))
            runned_case = new_case.get('case')
            if original_case and runned_case:
                original_case.ended_at = runned_case.ended_at
                original_case.status = runned_case.status
                original_case.details = runned_case.details
                self.store.save(original_case)
                if not self.has_failed and original_case.failed():
                    self.has_failed = True

    def _get_next_task(self):
        """
        Verify all the running tasks and expire timed out ones. Returns a task if a new can start
        :return: Task that can be started or None
        """
        to_remove = []
        to_return = None
        for running in self.running_now:
            expiration = running['started']
            expiration += timedelta(seconds=self.timeout)
            if running['process'].is_alive():
                if expiration > datetime.now():
                    print("Task {} is still running".format(running['case']))
                    continue
                self._log("------ Task {} expired------".format(running['case']))
                self._expire_case(running)
                to_remove.append(running)
            else:
                self._log("------ Task {} finished-----".format(running['case']))
                self._process_test_result()
                to_remove.append(running)

        for item in to_remove:
            self.running_now.remove(item)

        if len(self.running_now) < self.workers and len(self.process_cases) > 0:
            to_return = self.process_cases.pop()
        return to_return

    def _process_queue(self, func, func_name, shared_cases, shared_data, run_id, case_id, case):
        result_case = func(self, case)
        shared_data[func_name] = result_case.extra_data
        shared_cases.append({'case': result_case, 'id': case_id, 'run_id': run_id})

    def _verify_any_timeout(self):
        for item in self.all_processes:
            if item['process'].is_alive():
                item['process'].terminate()
        for item in self.stored_cases:
            self._log('------ Verifying case {}... ------'.format(item.report()))
            if not item.is_running_or_pending():
                continue
            self._log('------ Timeout: {} ------'.format(item))
            item.end(success=False, details={'error': 'Time out'})
            self.store.save(item)
            self.cases.append(item)

    def end(self, success=None):
        self._verify_any_timeout()
        if success and isinstance(success, bool):
            self.has_failed = not success
        self.test.end(not self.has_failed)
        self.store.save(self.test)
        return self.test.export()

    def add_test(self, name, category, save=True, relate=True):
        self._log('Adding test {}/{}'.format(name, category))
        if relate:
            case = self.test.add_test(name, category)
        else:
            case = TestCase(name, category)
        if save:
            self.store.save(case)
        return case

    def start(self):
        self._log('Starting Run {}'.format(self.test.name))
        self.test.start()
        self.store.save(self.test)
        cases = [
            {
                'func': item,
                'name': getattr(item, 'name'),
                'category': getattr(item, 'category'),
                'function_name': getattr(item, 'function_name')
            } for item in self._get_cases()
        ]

        for item in cases:
            case_store = self.test.add_test(item.get('name'), item.get('category'))
            self.store.save(case_store)
            item['case'] = case_store
            self.stored_cases.append(case_store)
            process = Process(target=self._process_queue,
                              args=(
                                  item.get('func'),
                                  item.get('function_name'),
                                  self.cases,
                                  self.data,
                                  self.test.id,
                                  case_store.id,
                                  case_store
                              ))
            process.daemon = True
            case_process = {
                'case': case_store,
                'process': process
            }
            self.process_cases.append(case_process)
            self.all_processes.append(case_process)

        while True:
            sleep(0.5)
            next_task = self._get_next_task()
            if next_task:
                next_task['case'].start()
                self.store.save(next_task['case'])
                next_task['process'].start()
                next_task['started'] = datetime.now()
                self.running_now.append(next_task)

            if len(self.process_cases) == 0 and len(self.running_now) == 0:
                self._process_test_result()
                self._log('All are done.\n')
                break
