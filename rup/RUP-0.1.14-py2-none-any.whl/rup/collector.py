import logging
import os
import time

import yaml

import util
from util import determine_run_number


class RunFiles:

    def __init__(self, run):
        self.files = []
        self.run = run
        self.last_mod = time.time()
        self.rup_config = None
        self.log_file = None

    def append_file(self, f):
        self.files.append(f)

    def reset_mod_time(self):
        self.last_mod = time.time()

    def n_files(self):
        return len(self.files)

    def n_nominal_files(self):
        return int(self.rup_config['n_files'])

    def is_complete(self):
        return self.n_files() == self.n_nominal_files() and self.log_file

    def has_rup(self):
        return self.rup_config is not None

    def set_rup_path(self, path):
        self.rup_config = util.load_yaml(path)[self.run]

    def set_log_path(self, path):
        self.log_file = path


class Collector:

    def __init__(self):
        self.runs = {}
        self.observers = []
        self.logging = logging.getLogger(self.__class__.__name__)

    def attach(self, watcher):
        watcher.add_observer(self.__react_watch)

    def __react_watch(self, f):
        path = f.path
        d = os.path.dirname(path)

        self.logging.info("Received file {}".format(path))
        n = f.n

        run = self.runs.get((d, n), RunFiles(n))

        if util.is_data(path):
            if path not in run.files:
                self.logging.info("Appended {} to run {}".format(path, n))
                run.append_file(path)
            else:
                self.logging.info("Already had {}".format(path))
        elif util.is_rup(path):
            if not run.has_rup():
                self.logging.info("RUP file for run {} is {}".format(n, path))
            else:
                self.logging.warn("Multiple RUP files for {}: 1={} 2={}. Replacing 1 with 2.".format(n, path, run.rup_path))

            run.set_rup_path(path)
        elif util.is_run_log(path):
            self.handle_run_log(f)
            return
        elif util.is_log(path):
            run.set_log_path(path)

        self.logging.info("Run {} has {} entries".format(n, run.n_files()))

        self.runs[(d, n)] = run

        self.notify_observers(run)

    def add_observer(self, obs):
        self.observers.append(obs)

    def remove_run(self, run):
        self.logging.warn("Removing run# {}".format(run.run))
        d = os.path.dirname(run.files[0])
        self.runs.pop((d, run.run))

    def notify_observers(self, run):
        for obs in self.observers:
            try:
                obs(run)
            except Exception as e:
                self.logging.error(e)

    def handle_run_log(self, f):
        path = f.path
        d = os.path.dirname(path)
        try:
            run_log = util.load_yaml(path)
            for key, value in run_log.iteritems():

                n_files = value.get('n_files')
                if not n_files or int(n_files) == 0:
                    continue

                self.logging.debug("Run log entry: {}".format(key))
                run = self.runs.get((d, key), RunFiles(key))
                run.rup_config = run_log.get(key)
                self.runs[(d, key)] = run

                self.notify_observers(run)

        except Exception as e:
            self.logging.error(e)
