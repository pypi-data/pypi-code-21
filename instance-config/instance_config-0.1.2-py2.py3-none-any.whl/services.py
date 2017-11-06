import subprocess


class ServiceMonitor(object):
    def __init__(self, service):
        self.service = service

    @property
    def active(self):
        cmd = 'systemctl status %s.service' % self.service
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        stdout_list = proc.communicate()[0].split('\n')
        for line in stdout_list:
            if 'Active:' in line:
                if '(running)' in line:
                    return True
        return False

    def start(self):
        cmd = 'systemctl start %s.service' % self.service
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        proc.communicate()