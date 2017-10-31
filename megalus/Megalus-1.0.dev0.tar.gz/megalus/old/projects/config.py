"""[summary].

[description]

Variables:
    profile {[type]} -- [description]
"""
import os
from git import Repo
from os.path import expanduser
from megalus.core.messages import notify
from megalus.core import utils
from megalus.core.li_tabulate import tabulate
from megalus.projects.setup import settings


class Config():
    def __init__(self, filename=None, *args, **kwargs):
        self.data = settings.CONFIG_DICT
        proj_name = getattr(settings, 'ENV_NAME', None)
        if proj_name:
            self.project_path = os.environ.get(proj_name)
        else:
            self.project_path = None
        if filename:
            self.filename = filename
        else:
            self.filename = getattr(settings, 'CONFIG_FILE', None)

    def check_config(self, verbose=False):
        ret = True
        if not self.project_path:
            if verbose:
                utils.console(
                    "Defina a variável {} antes de continuar.".format(
                        settings.ENV_NAME), style="error")
            ret = False
        for envvar in settings.ENV_LIST:
            if not os.environ.get(envvar):
                if verbose:
                    utils.console(
                        "Defina a variável {} "
                        "antes de continuar.".format(envvar), style="error")
                ret = False
        path = self.get_filename()
        if not os.path.exists(path):
            if verbose:
                utils.console(
                    "O arquivo {} não foi encontrado".format(
                        path), style="error")
            ret = False
        else:
            loaded_dict = {}
            with open(path, 'r') as file:
                for line in file:
                    if "=" in line:
                        key = line.split("=")[0].lower()
                        value = line.split("=")[1].rstrip()
                        loaded_dict[key] = value

            for key in self.data:
                if not loaded_dict.get(key):
                    if verbose:
                        utils.print_error(
                            "O arquivo de configuração não "
                            "tem a chave {} informada.".format(key))
                    ret = False
        if ret and verbose:
            utils.print_success("Configuração OK.")
        return ret

    def show_config(self):
        utils.console("Configuração Atual:", style="warning", use_prefix=False)
        utils.console(
            "Arquivo de configuração: {}".format(
                self.get_filename()), style="warning", use_prefix=False)
        utils.console(
            "Caminho do Projeto ({}): {}\n".format(
                settings.ENV_NAME,
                self.project_path), style="warning", use_prefix=False)
        data = self.get_data(force=True)
        config_list = [
            (obj, data[obj])
            for obj in data
        ]
        print(tabulate(
            config_list,
            headers=["Opção", "Valor"]
        ) + "\n")

    def get_filename(self):
        filepath = os.path.join(expanduser("~"), ".{}".format(self.filename))
        return filepath

    def get_data(self, verbose=False, force=False):
        if self.check_config(verbose=verbose) or force:
            self.data.project_path = self.project_path
            with open(self.get_filename(), 'r') as file:
                for line in file:
                    if "=" in line:
                        key = line.split("=")[0].lower()
                        value = line.split("=")[1].rstrip()
                        self.data[key] = value
            return self.data
        else:
            return False

    def clone_repositories(self, force=False):

        if force:
            resp = True
        else:
            resp = utils.confirma("\nDeseja clonar os Repositórios")
        if resp:
            if not os.path.exists(self.project_path):
                os.makedirs(self.project_path)
            utils.run_command(
                title="Clonando Repositorios",
                command_list=[
                    {
                        'command': "git config --global "
                        "credential.helper 'cache --timeout=3600'",
                        'run_stdout': False}])

            # Baixa APPLICATIONS
            baixa_repositorios(self.project_path)

    def set_data(self, force=False):
        utils.console("Configuração", style="section")
        if force:
            resp = True
        else:
            resp = utils.confirma("Deseja configurar as chaves")
        if resp:
            with open(self.get_filename(), 'w') as file:
                for key in self.data:
                    if key == "docker_compose_path" and not self.data.get(key):
                        continue
                    if self.data.get(key):
                        ask = "Informe {} [{}]: ".format(
                            key.upper(), self.data.get(key))
                    else:
                        ask = "Informe {}: ".format(key.upper())

                    resposta_ok = False
                    while not resposta_ok:
                        try:
                            value = str(input(ask))
                            if not value and self.data[key]:
                                file.write(
                                    "{}={}\n".format(
                                        key.upper(), self.data[key]))
                                resposta_ok = True
                            if value:
                                self.data[key] = value
                                file.write(
                                    "{}={}\n".format(
                                        key.upper(), value))
                                resposta_ok = True
                        except KeyboardInterrupt:
                            print("\nOperação interrompida")
                            return False
                        except BaseException:
                            print('erro')
                            pass
            # Grava arquivo de credenciais da Amazon
            if settings.USE_AWS:
                resp = utils.confirma(
                    "Deseja gravar o arquivo com as credenciais da Amazon?")
                if resp:
                    aws_folder = os.path.join(expanduser("~"), ".aws")
                    if not os.path.exists(aws_folder):
                        os.makedirs(aws_folder)
                    with open(os.path.join(aws_folder, "config"), 'w') as file:
                        file.write("[config]\n")
                        file.write(
                            'region = {}\n'.format(
                                self.data['aws_region']))

                    with open(os.path.join(
                            aws_folder, "credentials"), 'w') as file:
                        file.write('[default]\n')
                        file.write(
                            'aws_access_key_id = {}\n'.format(
                                self.data['aws_key']))
                        file.write(
                            'aws_secret_access_key = {}\n'.format(
                                self.data['aws_secret']))

        # Confirma o caminho do docker-compose.yml
        if not self.data.get('docker_compose_path'):
            ret = utils.run_command(
                title="Localizando arquivo docker-compose.yml",
                get_stdout=True,
                command_list=[
                    {
                        'command': "locate docker-compose.yml",
                        'run_stdout': False
                    }
                ]
            )
            if ret:
                paths_found = ret.split('\n')
                if paths_found[-1] == '':
                    paths_found.pop(-1)
                if len(paths_found) == 1:
                    self.data['docker_compose_path'] = paths_found[
                        0].replace('docker-compose.yml', '')
                elif paths_found:
                    print(
                        "Informe a localização do arquivo"
                        " 'docker-compose.yml' do Projeto")
                    print("(A localização padrão é: '{}/{}')\n".format(
                        self.project_path,
                        settings.DOCKER_REPO_NAME
                    ))
                    print("Os caminhos encontrados foram:")
                    for num, path in enumerate(paths_found):
                        print("{}. {}".format(num + 1, path))
                    resposta_ok = False
                    print("\n")
                    while not resposta_ok:
                        try:
                            rep = input(
                                "Selecione o "
                                "caminho: (1-{}): ".format(num + 1))
                            if rep and int(rep) in range(1, num + 1):
                                resposta_ok = True
                        except KeyboardInterrupt:
                            print("Operação interrompida\n")
                            return False
                        except BaseException:
                            pass
                    self.data['docker_compose_path'] = paths_found[
                        int(rep) - 1].replace('docker-compose.yml', '')
            else:
                resposta_ok = False
                while not resposta_ok:
                    try:
                        default_path = os.path.join(
                            self.project_path, settings.DOCKER_REPO_NAME)
                        rep = input(
                            "Informe o caminho do arquivo "
                            "docker-compose.yml [{}]: ".format(default_path))
                        if rep == "":
                            rep = default_path
                        if os.path.exists(
                            os.path.join(
                                rep,
                                "docker-compose.yml")):
                            resposta_ok = True
                            self.data['docker_compose_path'] = rep
                    except KeyboardInterrupt:
                        print("Operação interrompida\n")
                        return False
                    except BaseException:
                        pass

            if self.data.get('docker_compose_path'):
                print('Arquivo encontrado!')
                with open(self.get_filename(), 'a') as file:
                    file.write(
                        "{}={}\n".format(
                            "DOCKER_COMPOSE_PATH",
                            self.data.get('docker_compose_path')
                        ))

        notify(msg="Configuração finalizada.")
        return True


profile = Config()


def run_update(no_confirm, stable, staging):
    data = profile.get_data()

    if not data:
        return False

    utils.console("Atualizar Repositórios", style="section")

    if no_confirm:
        resp = True
    else:
        resp = utils.confirma(
            "Este comando atualiza todos os Repositórios\n"
            "que estejam nas branchs 'production', 'staging'\n"
            "'release', 'beta' ou 'master'.\n"
            "Além disso, baixa novos repositórios que ainda\n"
            "não estejam na pasta do projeto.\n"
            "Deseja continuar")

    if resp:
        # Iterar todos os repositórios
        # Checar em que branch está
        # Se tiver em production ou master, dar o git pull
        for app in settings.APPLICATIONS:
            app_name = app[0]
            stable_branch = app[1][-1]
            caminho = os.path.join(data.project_path, app_name)
            if os.path.exists(caminho):
                repo = Repo(
                    os.path.join(data.project_path, app_name)
                )
                # 1. Checa se o remote existe e é válido
                remote_url_list = repo.remotes
                origin = [
                    obj
                    for obj in remote_url_list
                    if obj.name == 'origin'
                ]
                if origin:
                    origin = origin[0]
                remote_url = "{}{}.git".format(
                    settings.VCS_BASE_URL,
                    app_name.lower())
                if origin:
                    if origin.url != remote_url:
                        if no_confirm:
                            resp = True
                        else:
                            resp = utils.confirma(
                                "O repositório '{}' está com o endereço\n"
                                "remoto: {}.\nDeseja trocar".format(
                                    app_name, origin.url))
                        if resp:
                            origin.set_url(
                                new_url=remote_url
                            )
                else:
                    repo.create_remote(name="origin", url=remote_url)

                # 2. Se tiver a opção 'stable'
                # mudar para a branch mais estável
                if stable:
                    os.chdir(caminho)
                    utils.run_command(
                        title=None,
                        command_list=[
                            {
                                'command': 'git checkout {branch}'.format(
                                    branch=stable_branch
                                ),
                                'run_stdout': False
                            }
                        ]
                    )

                # Checa Staging
                if staging:
                    stage_branch = None
                    if 'staging' in app[1]:
                        stage_branch = 'staging'
                    if 'beta' in app[1]:
                        stage_branch = 'beta'

                    if not stage_branch:
                        stage_branch = stable_branch

                    os.chdir(caminho)
                    utils.run_command(
                        title=None,
                        command_list=[
                            {
                                'command': 'git checkout {branch}'.format(
                                    branch=stage_branch
                                ),
                                'run_stdout': False
                            }
                        ]
                    )

                # 3. Checa se o repositorio é production/master
                # e faz o update
                branch = repo.active_branch.name
                if branch in [
                    'production',
                    'staging',
                    'beta',
                    'release',
                        'master']:
                    utils.console(
                        "Atualizando {}/{}".format(app_name, branch),
                        style="info",
                        use_prefix=False
                    )
                    os.chdir(caminho)
                    utils.run_command(
                        title=None,
                        command_list=[
                            {
                                'command': 'git remote update '
                                '&& git fetch && git pull --all',
                                'run_stdout': False
                            }
                        ]
                    )
                else:
                    utils.print_warning("Repositório '{}' "
                                        "ignorado. Branch: {}".format(
                                            app_name, branch))
        # Baixa os repositorios faltantes
        baixa_repositorios(data.project_path)
        notify(msg="Update dos projetos finalizado.")


def baixa_repositorios(path):
    for app, branch_list in settings.APPLICATIONS:
        if os.path.exists(os.path.join(path, app)):
            continue
        utils.print_warning("Baixando '{}'".format(app))
        first_branch = True
        for branch in branch_list:
            github_url = "{}{}.git".format(
                settings.VCS_BASE_URL,
                app.lower())
            if first_branch:
                ret = utils.run_command(
                    title=None,
                    command_list=[
                        {
                            'command': 'git clone -b'
                            ' {branch} {url} "{dir}"'.format(
                                branch=branch,
                                url=github_url,
                                dir=os.path.join(
                                    path,
                                    app)),
                            'run_stdout': False}])
                first_branch = False
            else:
                if ret:
                    os.chdir(os.path.join(path, app))
                    utils.run_command(
                        title=None,
                        command_list=[
                            {
                                'command': 'git checkout'
                                ' -b {branch} remotes/origin/{branch}'.format(
                                    branch=branch
                                ),
                                'run_stdout': False
                            }
                        ]
                    )
