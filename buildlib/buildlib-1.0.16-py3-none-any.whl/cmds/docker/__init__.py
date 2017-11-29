from typing import Optional, List
from processy import run
from cmdinter import CmdFuncResult, Status


def _image_exists(image) -> bool:
    result = run(
        cmd=['docker', 'inspect', '--type=image', image],
        verbose=False,
        return_stdout=True
    )

    return 'Error: No such image' not in result.stdout


def run_container(
    image: str,
    port: int
) -> CmdFuncResult:
    """
    Run Docker container locally.
    """
    title = 'Run Docker Container.'

    p = run(['docker', 'run', '-d', '-p', f'127.0.0.1:{port}:{port}', image])

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def stop_container(
    by_port: int,
) -> CmdFuncResult:
    title = 'Stop Docker Container'

    if by_port:
        cmd = ['docker', 'ps', '-q', '--filter', f'expose={by_port}',
               '--format="{{.ID}}"']

    ids = run(
        cmd=cmd,
        return_stdout=True,
    ).stdout.split('\n')

    ps = [
        run(['docker', 'stop', id_.replace('"', '')])
        for id_
        in ids
        if id_
    ]

    returncode = max([p.returncode for p in ps]) if ps else 0

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def remove_image(
    image: str
) -> CmdFuncResult:
    """"""
    title = 'Remove Docker Image.'

    cmd = ['docker', 'rmi', image, '--force']

    if _image_exists(image):
        p = run(cmd)
        returncode = p.returncode
    else:
        returncode = 0

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def build_image(
    tags: List[str],
) -> CmdFuncResult:
    """
    """
    title = 'Build Docker Image.'

    cmd = ['docker', 'build', '.', '--pull', '-f', 'Dockerfile']
    for tag in tags:
        cmd.extend(['-t', tag])

    p = run(cmd)

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )
