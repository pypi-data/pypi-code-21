"""Ferramenta Megalus.
Para mais detalhes digite 'meg help'

Usage:
    meg bash        [<app>]
    meg build       [<app>] [--no-cache]
    meg config      [--clone-only]
    meg debug       [<app>]
    meg deploy
    meg configproject
    meg help        [<option>]
    meg list        [<libs>...]
    meg npm list    <app>
    meg rebuild     [-y | --yes]
    meg release     [(major|minor|patch)]
    meg release eb
    meg resetdb     [<app>]
    meg run         [<app>] [<command> ...]
    meg service     (redis|memcached) [<key>]
    meg telnet      [<app>] (<port>)
    meg test        [<app>] [--using=(django|nose|pytest)] [--rds] [-v]
    meg tunnel      [<subdomain>] [<app>]
    meg update      [-y | --yes] [--production | --staging]
    meg watch       [<app>] [--dev]

Options:
    --help          Mostra esta tela
    --django        Roda o teste unitario do Django. (Padrao: Unittest.)
    --rds           Nos testes usar o RDS da Amazon
    --no-cache      Na build nao utilizar o cache
    <command>       Rode um comando para o run do container
    -y --yes        Confirma automaticamente
    <libs>          Mostrar a versão das livrarias solicitadas
    --production    Muda para a branch mais estável (ex. 'production')
    --staging       Altera as branchs para staging/beta durante o update
    <subdomain>     O subdominio para o tunel reverso, via ngrok
    <app>           Aplicacao que sera alvo do comando
    -v              Verbose

"""
import sys
from docopt import docopt
from megalus import __version__
from megalus.commands import aws
from megalus.commands import docker
from megalus.commands import npm
from megalus.core.help import get_help
from megalus.core.release import make_pull_request, start_deploy
from megalus.core.services import run_service
from megalus.core.tunnel import run_ngrok
from megalus.core.utils import (
    confirma, run_command, console
)
from megalus.projects.config import profile, run_update
from megalus.projects.setup import settings
from megalus.version import show_version_warning


def check_vpn():
    """Checa se a VPN está ativa."""
    if settings.CHECK_VPN:
        ret_tun = run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': 'ifconfig | grep tun',
                    'run_stdout': False
                }
            ]
        )

        if not ret_tun:
            print("\n{}{}ERRO:{} VPN não encontrada.".format(
                bcolors.BOLD, bcolors.FAIL, bcolors.ENDC))
            print("Por favor, ative a VPN e tente novamente.")
            return False

    return True


def main(arguments):
    """Faz o Parse dos Comandos."""

    if not arguments['help']:
        console("Para ajuda digite: meg help", style="grey", use_prefix=False)

    #
    # CONFIG
    #
    if arguments['config'] is True and check_vpn():
        clone_only = arguments['--clone-only']

        profile.show_config()
        ret = profile.check_config(verbose=True)

        resposta = confirma("Deseja rodar a configuração?")
        if resposta:
            profile.set_data()

        return True
    #
    # DEPLOY
    #
    if arguments['deploy'] is True and check_vpn():
        ret = aws.deploy.run()
        return ret
    #
    # DEBUG
    #
    if arguments['debug'] is True:
        ret = docker.debug.run(
            application=arguments['<app>']
        )
        return ret
    #
    # TELNET
    #
    if arguments['telnet'] is True:
        ret = docker.telnet.run(
            application=arguments['<app>'],
            port=arguments['<port>']
        )
        return ret
    #
    # BASH
    #
    if arguments['bash'] is True:
        ret = docker.bash.run(
            application=arguments['<app>']
        )
        return ret
    #
    # TEST
    #
    if arguments['test'] is True:
        ret = docker.test.run(
            application=arguments['<app>'],
            using=arguments['--using'],
            rds=arguments['--rds'],
            verbose=arguments['-v']
        )
        return ret
    #
    # RUN APP
    #
    if arguments['run'] is True:
        ret = docker.run.run(
            application=arguments['<app>'],
            action='up' if not arguments['<command>'] else 'exec',
            arg=arguments['<command>']
        )
        return ret
    #
    # BUILD APP
    #
    if arguments['build'] is True:
        ret = docker.build.run(
            application=arguments['<app>']
        )
        return ret
    #
    # UPDATE
    #
    if arguments['update'] is True:
        ret = run_update(
            no_confirm=arguments['--yes'],
            stable=arguments['--production'],
            staging=arguments['--staging'])
        return ret
    #
    # REBUILD
    #
    if arguments['rebuild'] is True:
        ret = docker.rebuild.run(no_confirm=arguments['--yes'])
        return ret
    #
    # HELP
    #
    if arguments['help'] is True:
        ret = get_help(app=arguments['<option>'])
        return ret
    #
    # LIST
    #
    if arguments['list'] and not arguments['npm']:
        ret = docker.lists.run(libs=arguments['<libs>'])
        return ret
    #
    # TUNNEL
    #
    if arguments['tunnel'] is True and check_vpn():
        ret = run_ngrok(
            subdomain=arguments['<subdomain>'],
            app=arguments['<app>']
        )
        return ret
    #
    # SERVICE
    #
    if arguments['service'] is True:
        if arguments['redis']:
            service = 'redis'
        else:
            service = 'memcached'
        ret = run_service(
            service=service,
            key=arguments['<key>']
        )
        return ret
    #
    # WATCH
    #
    if arguments['watch'] is True:
        ret = npm.watch.run(
            application=arguments['<app>'],
            dev=arguments['--dev'])
        return ret
    #
    # NPM LIST
    #
    if arguments['npm'] and arguments['list']:
        ret = npm.list.run(application=arguments['<app>'])
        return ret
    #
    # RELEASE
    #
    if arguments['release'] and not arguments['eb']:
        if arguments['major']:
            release = 'major'
        elif arguments['minor']:
            release = 'minor'
        elif arguments['patch']:
            release = 'patch'
        else:
            release = "same"
        ret = make_pull_request(release=release)
        return ret
    #
    # RELEASE EB
    #
    if arguments['release'] and arguments['eb']:
        ret = start_deploy()
        return ret
    #
    # RESET DB
    #
    if arguments['resetdb'] is True:
        ret = docker.resetdb.run(application=arguments['<app>'])
        return ret
    #
    # SHOW PROJECT
    #
    if arguments['configproject'] is True:
        ret = settings.show_project()
        return ret


def start():

    arguments = docopt(__doc__, version=__version__)

    if not settings.loaded:
        ret = confirma(
            "A configuração do Projeto {} não foi encontrada.\n"
            "Deseja criá-la agora".format(settings.project))
        if ret:
            retorno = settings.create_project()
        else:
            sys.exit(1)
    else:
        console(
            "Megalus v.{}".format(__version__),
            style="main_title",
            use_prefix=False)
        console(
            "Projeto: {}".format(
                settings.project),
            style="info",
            use_prefix=False)
        show_version_warning()
        retorno = main(arguments)
    if not retorno:
        print('\n')
    else:
        print("\nOperacao finalizada.\n")

    sys.exit(retorno)


if __name__ == "__main__":
    start()
