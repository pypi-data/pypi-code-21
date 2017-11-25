# pylint: disable=C0103

import time
import queue

from unicornclient import hat
from unicornclient import routine

class Routine(routine.Routine):
    def __init__(self):
        routine.Routine.__init__(self)
        self.hat = hat.Unicorn()
        self.status = {}
        self.monitor = None
        self.just_updated = False
        self.pending_toggle = False

    def run(self):
        while True:
            got_task = False

            try:
                data = self.queue.get_nowait()
                status = data['status'] if 'status' in data else None
                monitor = data['monitor'] if 'monitor' in data else None
                got_task = True
            except queue.Empty:
                status = None
                monitor = None

            self.just_updated = False
            if status:
                self.status = status
                self.just_updated = True
            if monitor:
                self.monitor = monitor
                self.just_updated = True

            self.hat.clear()
            self.update()
            self.hat.show()

            if got_task:
                self.queue.task_done()
            time.sleep(0.2)

    def status_to_color(self, status):
        if not status:
            return {'r':0, 'g':0, 'b':0}
        status = str(status).lower()

        if status == 'passed' or status == 'fixed':
            return {'r':0, 'g':255, 'b':0}
        if status in ['failed', 'still failing', 'broken', 'errored']:
            return {'r':255, 'g':0, 'b':0}
        if status == 'pending':
            self.pending_toggle = not self.pending_toggle
            strength = 255 if self.pending_toggle else 0
            return {'r':strength, 'g':strength, 'b':0}

        return {'r':0, 'g':0, 'b':255}

    def update(self):
        if self.just_updated:
            return self.hat.set_all_pixel(255, 255, 255)

        self.update_monitor()
        self.update_status()

    def update_status(self):
        rows = {}
        interesting_branches = ['dev', 'preprod', 'prod'][::-1]
        repo_names = []

        for repo_name, repo_data in self.status.items():
            repo_names.append(repo_name)
            if repo_name not in rows:
                rows[repo_name] = {}
            for branch_name, branch_data in repo_data.items():
                if branch_name in interesting_branches:
                    rows[repo_name][branch_name] = self.status_to_color(branch_data['status'])

        x = 0
        for repo_name in repo_names:
            y = 0
            for branch_name in interesting_branches:
                if branch_name in rows[repo_name] and x < self.hat.get_width():
                    color = rows[repo_name][branch_name]
                    self.hat.set_pixel(x, y, color['r'], color['g'], color['b'])
                y += 1
            x += 1

    def update_monitor(self):
        if self.monitor == 'failed' or self.monitor == 'error':
            self.hat.set_line_pixel(3, 255, 0, 0)
        else:
            self.hat.set_line_pixel(3, 0, 255, 0)
