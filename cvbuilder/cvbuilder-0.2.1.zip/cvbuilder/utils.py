import os
import shlex
import shutil
import subprocess
import logging
from typing import Iterable

import click
import crayons
import requests
from pathlib import Path

from tqdm import tqdm

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def run_process(cmd,
                shell: bool = False,
                requires_sudo: bool = False,
                cwd: Path = None,
                run_as_user=None,
                raise_return_exception=False,
                expected_return_code=0):
    if run_as_user is not None:
        # escaping is messed up if called with single quotes
        cmd = '''sudo -u {} -H {}'''.format(run_as_user, cmd)
    elif requires_sudo:
        cmd = "sudo {}".format(cmd)

    returncode = -1
    try:
        cwd_str = None if cwd is None else str(cwd.resolve())
        args = cmd if shell else shlex.split(cmd)

        p = subprocess.Popen(args, cwd=cwd_str, shell=shell)  # TODO replace with check call??
        p.wait()  # block until done
        returncode = p.returncode
    except KeyboardInterrupt:
        logger.info("Interrupting process running at PID '{}'...".format(p.pid))
        p.kill()
        logger.info("Process with PID '{}' interrupted!".format(p.pid))
        raise InterruptedError("Process was interrupted.")
    finally:
        logger.info(
            "Finished command: {} and return code '{}'".format(crayons.yellow(cmd), crayons.yellow(str(p.returncode))))

    if raise_return_exception and returncode != expected_return_code:
        raise AssertionError("Invalid return code: {}".format(returncode))

    return returncode


def check_output(cmd: str, shell: bool = True) -> Iterable[str]:
    output = subprocess.check_output(cmd,
                                     stderr=subprocess.STDOUT,
                                     shell=shell)
    output_lines = output.decode("utf-8").split("\n")
    return output_lines


def pip_install(requirements: object, venv: Path = None, upgrade: bool = False):
    args = []

    if upgrade:
        args.append("--upgrade")

    if isinstance(requirements, Path):
        args.append("-r {}".format(requirements.resolve()))
    else:
        args.append(requirements)

    if venv:
        activate_in_shell = venv.joinpath("bin").joinpath("activate")
        cmd = ". {venv_activate} && pip3 install {req}".format(venv_activate=str(activate_in_shell.resolve()),
                                                               req=" ".join(args))
        run_process(cmd, requires_sudo=False, shell=True, raise_return_exception=True)
    else:
        cmd = "pip3 install {req}".format(req=" ".join(args))
        run_process(cmd, requires_sudo=print, shell=True, raise_return_exception=True)

    return


def select_packages(packages: dict, enable_gui: bool = False,
                    enable_video: bool = False) -> list:
    APT_DEPTS = packages.get("main")

    # optional video packages
    APT_DEP_VIDEO = packages.get("video")

    # optional GUI packages -> only relevant when running GUIs
    APT_DEP_GUI = packages.get("gui")

    if enable_video:
        APT_DEPTS += APT_DEP_VIDEO
    if enable_gui:
        APT_DEPTS += APT_DEP_GUI

    return APT_DEPTS


def sizeof_fmt(num, suffix='B'):
    """
    https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    :param num:
    :param suffix:
    :return:
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def install_packages(command: str = "apt install -y {}", package_list: list = None, requires_sudo: bool = True):
    packages = " ".join(package_list)
    logger.info("Installing these packages: {}".format(packages))
    cmd = command.format(packages)
    run_process(cmd, requires_sudo=requires_sudo, raise_return_exception=True)


def install_numpy(venv: Path):
    logger.info("Installing numpy now ...")
    pip_install("numpy", upgrade=True, venv=venv)


def download_unzip_clean(url: str, target: Path, absolute_directory: Path, tmp_dir: Path,
                         keep_target_file: bool = False):
    if not target.exists():
        download_file(url=url, filename=target)
    else:
        logger.info("Target already exists: {}".format(target))
    if not keep_target_file and absolute_directory.exists():
        shutil.rmtree(str(absolute_directory), ignore_errors=False, onerror=None)
    if not keep_target_file or (target.exists() and not absolute_directory.exists()):
        logger.info("Unpacking archive: {}".format(target))
        shutil.unpack_archive(filename=str(target), extract_dir=str(tmp_dir))
    if not keep_target_file:
        os.remove(str(target.resolve()))


def download_file(url: str, filename: Path):
    r = requests.get(url, stream=True)

    if not r.ok:
        raise IOError("Cannot download file from {}".format(url))

    # FIXME -> with scale 32 it is faster, but an exception is raised when the download finishes
    unit_scale = 1  # 32
    chunk_size = unit_scale * 1024

    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0))
    chunked_size = int(total_size / chunk_size)
    logger.info("Downloading file from: {} to {}".format(crayons.green(url), crayons.green(str(filename))))
    logger.info("Downloading size: {}".format(crayons.green(str(sizeof_fmt(total_size)))))

    try:
        with filename.open('wb') as f:
            # for data in tqdm(r.iter_content(chunk_size=1), total=total_size, unit='B',
            for data in tqdm(r.iter_content(chunk_size=chunk_size), total=chunked_size, unit='KB',
                             unit_scale=False, miniters=1):
                f.write(data)
    except KeyboardInterrupt:
        logger.info("Download interrupted, removing temporary file: {}".format(crayons.red(str(filename))))
        os.remove(filename.absolute())
    except BaseException as be:
        raise be


def is_user_not_root():
    try:
        USERID = os.environ.get("EUID", None)
    except:
        USERID = 0
    USER_NOT_ROOT = True
    if USERID == 0:
        USER_NOT_ROOT = False
    return USER_NOT_ROOT
