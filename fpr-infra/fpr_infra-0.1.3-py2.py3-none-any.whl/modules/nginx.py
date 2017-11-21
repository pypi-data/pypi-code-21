# coding: utf-8

from pyinfra.api import deploy
from pyinfra.modules import files, server


@deploy("Install nginx application")
def install_less(state, host, conf_file):
    server.shell(
        state, host,
        {"Move nginx application configuration file"},
        f"mv packer/files/nginx/{conf_file} /etc/nginx/sites-available/{conf_file}",
        sudo=True
    )
    files.link(
        state, host,
        {"Enable application site on http"},
        f"/etc/nginx/sites-enabled/{conf_file}", f"/etc/nginx/sites-available/{conf_file}",
        sudo=True
    )
