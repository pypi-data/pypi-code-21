import docker
from typing import Optional, List
from processy import run
from cmdinter import CmdFuncResult, Status

client = docker.from_env()


def _image_exists(image):
    result = run(
        cmd=['docker', 'inspect', '--type=image', image],
        verbose=False,
        return_stdout=True
    )

    return 'Error: No such image' not in result.stdout


def stop_container(
    by_port: Optional[int] = None,
):
    if by_port:
        cmd = ['docker', 'ps', '-q', '--filter', f'expose={by_port}',
               '--format="{{.ID}}"']

    ids = run(cmd, return_stdout=True).stdout.split('\n')

    for id_ in [id_ for id_ in ids if id_]:
        run(['docker', 'stop', id_.replace('"', '')])


def run_container(version=VERSION):
    """
    Run Docker container locally.
    """
    image = f'{IMAGE}:{version}'

    run(['docker', 'run', '-d', '-p', f'127.0.0.1:{PORT}:{PORT}', image])


def remove_image(image=image):
    run(['docker', 'rmi', image, '--force'])


def build(
    dockerfile: str = '.',
    tags: Optional[List[str]] = None,
) -> CmdFuncResult:
    """"""
    title = 'Build Docker Image.'

    try:
        if tags:
            for tag in tags:
                client.images.build(
                    tag=tag,
                    dockerfile=dockerfile
                )
        else:
            client.images.build(dockerfile=dockerfile)

        returncode = 0

    except Exception as e:
        returncode = 1

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )

