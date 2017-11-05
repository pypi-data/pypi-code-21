import os
import json
from pathlib import Path
from subprocess import check_call, check_output, STDOUT
from abc import ABC, abstractmethod


class Packer():
    def __init__(self, packer_dir="./packer", var_file='vars.json'):
        self.home_dir = Path(os.getcwd())
        self.packer_dir = self.home_dir / packer_dir
        vars_file = self.packer_dir / var_file
        if vars_file.exists():
            with vars_file.open() as data_file:
                self.vars = json.load(data_file)

    def get(self, key):
        return self.vars[key]

    def check_sudo(self, cmd, **kwargs):
        return check_call(["sudo"] + cmd, **kwargs)

    def check_as(self, cmd, check=check_call, **kwargs):
        def demote(user_uid, user_gid):
            def set_ids():
                os.setgid(user_gid)
                os.setuid(user_uid)

            return set_ids

        return check(cmd, preexec_fn=demote(1000, 1000), **kwargs)

    def mkdir(self, dir, *, own=None, mod=None, uid=None, gid=None):
        check_call(["sudo", "mkdir", "-p", dir])

        if own is None:
            if uid is None:
                uid = str(os.getuid())
            if gid is None:
                gid = str(os.getgid())
            own = f"{uid}:{gid}"

        self.check_sudo(["chown", own, dir])
        if mod is not None:
            self.check_sudo(["chmod", mod, dir])

    def mv(self, file_name, dest, *, own=None, mod=None, src_dir=None, if_exists_only=True):
        if src_dir is None:
            src_dir = self.packer_dir

        file_path = Path(src_dir) / file_name
        if file_path.exists() or not if_exists_only:
            self.check_sudo(["mv", file_path, dest])

            if own is not None:
                self.check_sudo(["chown", own, f"{dest}/{file_name}"])

            if mod is not None:
                self.check_sudo(["chmod", mod, f"{dest}/{file_name}"])

    def cp_ssh_key(self, private, public=None):
        self.mv('id_rsa', self.home_dir / '.ssh')


class PackerInstaller(ABC):
    def __init__(self, packer):
        self.packer = packer

    @abstractmethod
    def install(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class NginxInstaller(PackerInstaller):
    def install(self, conf_files):
        self.packer.check_sudo(["rm", "/etc/nginx/sites-enabled/default"])

        self.update(conf_files)

        out = str(check_output(["nginx", "-v"], stderr=STDOUT, universal_newlines=True))
        return out.split('/')[1].split()[0] + " (configuration files in /etc/nginx/sites-enabled/)"

    def update(self, conf_files):
        for file in conf_files:
            self.packer.mv(file, f"/etc/nginx/sites-available/{file}")
            self.packer.check_sudo(
                ["ln", "-s", f"/etc/nginx/sites-available/{file}", f"/etc/nginx/sites-enabled/{file}"])

        self.packer.check_sudo(["systemctl", "restart", "nginx"])

    def install_ssl(self):
        self.packer.mkdir("/etc/nginx/ssl", own="www-data:")
        ssl_dir = self.packer.packer_dir / 'ssl'
        for file in ssl_dir.glob('*'):
            name = os.path.basename(file)
            self.packer.mv(name, '/etc/nginx/ssl', own="www-data:", src_dir=ssl_dir)


class UwsgiInstaller(PackerInstaller):
    def install(self):
        self.packer.mkdir("/etc/uwsgi", own="www-data:")
        self.packer.mkdir("/var/log/uwsgi/", own="www-data:root")
        self.packer.mv("uwsgi.service", "/etc/uwsgi", own="www-data:root")
        self.packer.check_sudo(["ln", "-s", "/etc/uwsgi/uwsgi.service", "/etc/systemd/system/uwsgi.service"])
        self.packer.check_sudo(["systemctl", "enable", "uwsgi"])

        self.update()

        out = self.packer.check_output(["uwsgi", "--version"], universal_newlines=True)
        return out + " (configuration file in /etc/uwsgi/)"

    def update(self):
        self.packer.mv("uwsgi.ini", "/etc/uwsgi", own="www-data:root", if_exists_only=True)
        self.packer.check_sudo(["systemctl", "restart", "uwsgi"])
        self.packer.mv("uwsgi.service", "/etc/uwsgi", own="www-data:root", if_exists_only=True)


class ApplicationInstaller(PackerInstaller):
    def install(self):
        app_dir = self.packer.get('app_dir')
        self.packer.mkdir(app_dir, own="www-data:root")

        self.update()

        return f"\nApplication is on '{app_dir}'\n"

    def update(self):
        app_dir = self.packer.get('app_dir')
        self.packer.mv("application.py", app_dir, own="www-data:root", mod="a+r")
