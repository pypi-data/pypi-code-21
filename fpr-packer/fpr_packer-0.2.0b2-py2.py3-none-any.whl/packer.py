import os
import json
from pathlib import Path
from subprocess import check_call, check_output, STDOUT


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

    def mv(self, vars, src, dest, *, own=None, mod=None, src_dir=None):
        if src_dir is None:
            src_dir = self.packer_dir

        self.check_sudo(["mv", f"{src_dir}/{src}", dest])

        if own is not None:
            self.check_sudo(["chown", own, f"{dest}/{src}"])

        if mod is not None:
            self.check_sudo(["chmod", mod, f"{dest}/{src}"])

    def install_nginx(self, conf_files):
        self.check_sudo(["rm", "/etc/nginx/sites-enabled/default"])

        for file in conf_files:
            self.check_sudo(["mv", f"{self.packer_dir}/{file}", f"/etc/nginx/sites-available/{file}"])
            self.check_sudo(["ln", "-s", f"/etc/nginx/sites-available/{file}", f"/etc/nginx/sites-enabled/{file}"])

        out = str(check_output(["nginx", "-v"], stderr=STDOUT, universal_newlines=True))
        return out.split('/')[1].split()[0] + " (configuration files in /etc/nginx/sites-enabled/)"
