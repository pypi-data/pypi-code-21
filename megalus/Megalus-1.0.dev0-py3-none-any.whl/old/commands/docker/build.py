import os
from megalus.core.messages import notify
from megalus.core.utils import (
    run_command, get_app, get_compose_data, console, stop_all
)
from megalus.projects.config import profile
from megalus.projects.setup import settings


def run(application):
    data = profile.get_data()
    if not data:
        return False

    if application == "base" or not application:
        path = os.path.join(
            data.project_path,
            settings.DOCKER_BASE_IMAGE_REPO,
            'baseimage'
        )
        ret = run_command(
            title="Gera Imagem Base do Docker",
            command_list=[
                {
                    'command': "cd {} && docker build -t {}:dev .".format(
                        path,
                        settings.DOCKER_BASE_IMAGE_REPO
                    ),
                    'run_stdout': False
                },
            ]
        )
        if not ret:
            return False

        if application == "base":
            notify(msg="A operação de Build foi concluída")
            return True

    name = ""
    container_id = None
    if application:
        container_id, name = get_app(
            application=application,
            title="Build da Aplicacao",
            data=data,
            stop=True
        )
        if not container_id:
            return False

    if settings.USE_ECR:
        run_command(
            get_stdout=False,
            command_list=[
                {
                    'command': "aws ecr get-login"
                    " --region {region}".format(
                        region=data['aws_region']),
                    'run_stdout': True
                }
            ]
        )

    stop_all(data)

    console("Gerando a build dos containers", style="section")
    os.system(
        "cd {folder} && docker-compose build {app}".format(
            folder=data['docker_compose_path'],
            app=name)
    )

    stop_all(data)

    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    retdocker = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': 'docker ps -a | grep _run_',
                'run_stdout': False
            }
        ]
    )
    if retdocker:
        os.system(
            "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
        )
    notify(msg="A operação de Build foi concluída")
