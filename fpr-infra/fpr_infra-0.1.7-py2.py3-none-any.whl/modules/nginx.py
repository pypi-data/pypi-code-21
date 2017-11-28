# coding: utf-8

from pyinfra.api import deploy
from pyinfra.modules import files
from fpr_infra import pyinfra


@deploy("Install nginx application")
def install_nginx(state, host, conf_file, dest=None):
    dest = dest or conf_file
    pyinfra.move(
        state, host,
        f"files/nginx/{conf_file}", f"/etc/nginx/sites-available/{dest}",
        sudo=True
    )
    files.link(
        state, host,
        {"Enable application site on http"},
        f"/etc/nginx/sites-enabled/{conf_file}", f"/etc/nginx/sites-available/{dest}",
        sudo=True
    )
