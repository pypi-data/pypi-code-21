"""[summary].

[description]
"""
import os
from megalus.core import utils
from megalus.projects.config import profile
from megalus.projects.setup import settings


def run_django_commands(cmd_list, data, name):
    """[summary].

    [description]

    Arguments:
        cmd_list {[type]} -- [description]
        data {[type]} -- [description]
        name {[type]} -- [description]
    """
    for cmd in cmd_list:
        utils.console(
            "Rodando comando: {}".format(cmd),
            style="warning",
            use_prefix=False)
        os.system(
            "cd {folder} && docker-compose {cmd} {app} {com}".format(
                folder=data['docker_compose_path'],
                cmd="run",
                app=name,
                com=cmd)
        )


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

    # Selecionar Banco
    container_id, name = utils.get_app(
        application=application,
        title="Redefinir Banco de Dados",
        data=data,
        stop=True,
        no_container=True
    )

    if not name:
        return False

    dbdata = [
        obj
        for obj in settings.LOCAL_DBS
        if obj.get('admin') == name
    ]

    if not dbdata:
        utils.print_error("Banco de Dados não encontrado para a Aplicação.")
        return False

    local_name = dbdata[0].get('local_name', None)
    db_name = dbdata[0].get('name', None)
    db_user = dbdata[0].get('user', None)

    if not local_name or not db_name or not db_user:
        utils.print_error("Configuração do Banco de Dados não encontrado.")
        return False

    # Confirmar
    warning_text = "Este comando exclui o banco de "
    "dados {} - Deseja continuar".format(
        local_name.upper())
    resp = utils.confirma(warning_text, warning=True)
    if resp:
        # Parar os containers
        utils.console(
            "\nParando containers",
            style="warning",
            use_prefix=False)
        utils.stop_all(data)

        # Iniciar o Postgres
        utils.console(
            "\nIniciando {}".format(local_name),
            style="warning",
            use_prefix=False)
        new_container_id = utils.run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': "cd {} && docker-compose "
                    "run -d {}".format(
                        data['docker_compose_path'],
                        local_name),
                    'run_stdout': False
                },
            ]
        )
        new_container_id = new_container_id.replace("\n", "")

        # Apagar o banco antigo
        cmd = "dropdb -U {user} {database}".format(
            user=db_user,
            database=db_name
        )
        utils.console(
            "\nRodando comando: {}".format(cmd),
            style="warning",
            use_prefix=False)
        os.system(
            "docker exec -ti {container} {com}".format(
                folder=data['docker_compose_path'],
                container=new_container_id,
                com=cmd)
        )
        # Criar o banco novo
        cmd = "createdb -U {user} -O {user} {database}".format(
            user=db_user,
            database=db_name
        )
        utils.console(
            "\nRodando comando: {}".format(cmd),
            style="warning",
            use_prefix=False)
        os.system(
            "docker exec -ti {container} {com}".format(
                folder=data['docker_compose_path'],
                container=new_container_id,
                com=cmd)
        )
        # Reiniciar os containers
        utils.console(
            "\nReiniciando Containers".format(cmd),
            style="warning",
            use_prefix=False)
        utils.stop_all(data)
        os.system(
            "cd {folder} && docker-compose up -d".format(
                folder=data['docker_compose_path']
            )
        )
        # Rodar Operações do Django
        cmd_list = [
            "python manage.py makemigrations",
            "python manage.py migrate",
            "python manage.py makemessages"
            "python manage.py compilemessages",
            "python manage.py createdata"
        ]
        run_django_commands(cmd_list, data, name)

        # Parar os containers
        utils.console(
            "\nParando containers",
            style="warning",
            use_prefix=False)
        utils.stop_all(data)

        # Excluir containers extra
        os.system(
            "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
        )

        return True
