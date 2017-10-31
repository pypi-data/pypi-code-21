"""[summary].

[description]
"""
import os
from megalus.core import utils
from megalus.projects.config import profile, run_update
from megalus.projects.setup import settings
from megalus.commands.docker import build


def run(no_confirm):
    """[summary].

    [description]

    Arguments:
        no_confirm {[type]} -- [description]

    Returns
    -------
        bool -- [description]

    """
    data = profile.get_data()
    if not data:
        return False

    if no_confirm:
        resp = True
    else:
        resp = utils.confirma(
            "Este comando exclui todas as imagens\n"
            "e containers existentes na máquina,\n"
            "e inicia um novo Update/Build.\n"
            "\n\033[91mCertifique-se que você tenha um backup\n"
            "do banco de dados antes de rodar esse comando e\n"
            "que todas as alterações importantes"
            " estejam commitadas.\033[0m\n\n"
            "Deseja continuar")

    if resp:
        # Parar containers
        utils.stop_all(data)

        # Excluir containers e imagens
        utils.run_command(
            title="Excluir Containers do Docker",
            command_list=[
                {
                    'command': 'docker rm -f $(docker ps -a -q)',
                    'run_stdout': False
                }
            ]
        )
        utils.run_command(
            title="Excluir Imagens do Docker",
            command_list=[
                {
                    'command': 'docker rmi -f $(docker images -q)',
                    'run_stdout': False
                }
            ]
        )

        # Roda Update
        run_update(no_confirm=True, stable=True, staging=False)

        # Roda Build
        build.run(application=None)

        # Finaliza
        utils.notify(msg="Rebuild dos Containers finalizado")
        os.system('cls' if os.name == 'nt' else 'clear')
        print("O Rebuild foi concluído.")
        print("Antes de iniciar os containers, digite o(s) comando(s):")
        for dbdata in settings.LOCAL_DBS:
            print(
                "'cd {} && docker-compose up "
                "{}'".format(
                    data['docker_compose_path'],
                    dbdata['local_name']))
        print("para iniciar o Banco de dados pela primeira vez.")
        print("Em seguida use o comando 'meg run'.")
        return True
