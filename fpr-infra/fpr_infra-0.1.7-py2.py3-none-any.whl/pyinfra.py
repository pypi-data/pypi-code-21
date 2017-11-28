# coding: utf-8

import os
from pathlib import Path
from pyinfra.api import FactBase, deploy, operation
from pyinfra.api.exceptions import OperationError
from pyinfra.modules import files, python, server


class PythonVersion(FactBase):
    """get python version"""

    def command(self):
        return 'cat /usr/local/lib/pyenv/_pyenv/version'

    def process(self, output):
        return output[0].strip()


class NodeVersion(FactBase):
    """get odoo version"""

    def command(self):
        return "node --version"

    def process(self, output):
        return output[0].strip()


@deploy("Move a file from packer folder")
def move(state, host, src_file, dest_file, **kwargs):
    """Move a file."""

    # no source or destination
    if src_file is None:
        raise OperationError('source file not defined')
    if dest_file is None:
        raise OperationError('destination file not defined')

    src_path = Path(state.deploy_dir, src_file)

    kwargs.pop('sudo', None)
    server.shell(
        state, host,
        {f"Move {src_path.as_posix()} file to {dest_file}"},
        f"mv {src_path.as_posix()} {dest_file}",
        sudo=True
    )

    if src_path.is_dir():
        files.directory(
            state, host,
            {f"Change file {dest_file} mode"},
            dest_file,
            **kwargs,
            sudo=True
        )
    else:
        files.file(
            state, host,
            {f"Change file {dest_file} mode"},
            dest_file,
            **kwargs,
            sudo=True
        )


@operation
def readme(state, host, add):
    add = add.replace('/', '\/')
    yield f"sed -i '$a\{add}' README.txt"
