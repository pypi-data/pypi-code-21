"""[summary].

[description]
"""
import os
from megalus.core import utils
from megalus.projects.config import profile


def run(application):
    """[summary].

    [description]

    Arguments:
        application {[type]} -- [description]

    Returns
    -------
        bool -- [description]

    """
    data = profile.get_data()
    if not data:
        return False
    # 1. Identifica o container
    container_id, name = utils.get_app(
        application=application,
        title="Rodar em Modo Depuração",
        data=data)
    if not container_id:
        return False

    # 2. Parar e reiniciar o container com service ports
    # docker-compose stop $app
    # docker-compose run --service-ports $app
    os.system('cls' if os.name == 'nt' else 'clear')
    os.chdir(data.project_path)
    utils.run_command(
        title="Modo Depuração: {}".format(name),
        get_stdout=True,
        command_list=[
            {
                'command': "cd {} && "
                "docker-compose stop {}".format(
                    data['docker_compose_path'], name),
                'run_stdout': False
            },
        ]
    )
    os.system(
        'cd {} && docker-compose run '
        '--service-ports {}\n'.format(
            data['docker_compose_path'], name)
    )

    print("Reiniciando o container...")
    utils.run_command(
        command_list=[
            {'command': "cd {} && "
             "docker-compose up -d {}".format(
                 data['docker_compose_path'], name),
             'run_stdout': False}
        ]
    )

    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    os.system(
        "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
    )
    return False
