"""
Settings para o MEG-Tools

Chaves do JSON:

CONFIG_FILE = Nome do arquivo de configuração (ex: "meg-config")
ENV_NAME = Variável de ambiente com o path do projeto (ex: "MEGALUS_PATH")
ENV_LIST = Lista com as variáveis de ambiente obrigatórias no projeto.
LOCAL_DBS = Lista com a configuração de cada banco de dados do projeto:
ex: [
    {
        'local_name': "service.postgres.local",
        'desc': "Banco de dados do Painel",
        'local_port': 5432,
        'user': 'nome_do_usuario',
        'name': 'nome_do_banco',
        'admin': "nome do container docker usado para enviar os comandos (ex.:frontend.painel.local)",
        'stage_name': "",
        'stage_port': 5432
    }
]
CHECK_VPN = Usa VPN para acessar AWS?
TEST_PRIORITY = Lista com os programas para rodar testes, na ordem de prioridade.
Ex.: [
    'nose',
    'pytest'
]
APPLICATIONS = Lista de Aplicações do Projeto.
A ordem das branchs é da mais volátil até a mais estável.
Ex.: [
    ['app1', ['master']],
    ['app2', ['develop', 'master']]
]
LIBRARIES = Lista de livrarias para mostrar no comando meg list:
Ex.: [
    'Django'
]
MINIFY_BEFORE = Aplicações que minificam arquivos durante o deploy
ex.: [
    'app1'
]
SYNC_S3 = Aplicações que sincronizam arquivos no S3 durante o deploy
Ex.: [
    'app1'
]
BASEDIRSTATIC = Caminho da pasta base para Compressão de arquivos estáticos nos aplicativos acima
Ex.: [
    "dir1", "dir2", static"
]
JSSOURCES = Caminho relativo a base dos arquivos JS para minificar num unico arquivo.
Todos os arquivos são comprimidos no arquivo "all.min.js"
Ex.: [
    ['folder3', 'index.js'],
    ['folder4', 'app.js']
]
CSSSOURCES = Caminho relativo a base dos arquivos CSS para minificar num unico arquivo.
Todos os arquivos são comprimidos no arquivo "all.min.css"
Ex.: [
    ['folder3', 'index.css'],
    ['folder4', 'app.css']
]
JSALONE = Arquivos JS para minificar individualmente

Ex.: [
    ["js", "index.js"]
]
#
CSSALONE =  Arquivos CSS para minificar individualmente
Exemplo: index.css será salvo como index.min.css
Ex.: [
    ["css", "index.css"]
]
DOCKER_REPO_NAME = Nome do projeto com o Docker-Compose.yaml (ex.: "megdocker")
DOCKER_BASE_IMAGE_REPO = Imagem usada como base para a build das restantes (ex.: "megbase")
DOCKERFILE_DEPLOY = Nome do arquivo Dockerfile para deploy. Ex: "Dockerfile_deploy"
DOCKERFILE_DEVELOPMENT = Nome do arquivo Dockerfile para develop. Ex.:"Dockerfile_dev"
VCS_NAME = Nome do VCS. Ex: "Bitbucket"
VCS_BASE_URL = URL base do VCS: Ex.: "https://bitbucket.org/NOME/"
VCS_BASE_API_URL = URL base para API. Ex.: 'https://api.bitbucket.org/'
REPOSITORY_API_URL = '2.0/repositories/NOME/{repo}/commit/{commit}/statuses'
PULL_REQUEST_API_URL = '2.0/repositories/NOME/{repo}/pullrequests/'
USE_AWS = Projeto hospedado na Amazon?
S3_SYNC_CMD = Comando para sincronizar o S3. Ex.: "aws s3 sync static/ s3://dominio.cdn/{branch}/static/ --acl public-read"
USE_ECR = Projeto hospeda as imagens Docker no ECR Amazon?
ECR_NAME = Faz o De/Para do nome do projeto para o nome do container no ECS
Ex.: {
    'app1': 'prod.app'
}
USE_REDIS = Usa Redis?
USE_MEMCACHED = Usa Memcached?
USE_SLACK = Usa Slack?
TEST_CHANNEL = Canal para testes no Slack. Ex.: "#teste_automacao"
USE_DATADOG = Usa Datadog?
USE_GRAFANA = Usa Grafana?
GRAFANA_MSG_URL = URL para enviar eventos ao Grafana. Ex: "http://dominio:porta/write?db=msgs"
"""
import os
import json
import yaml
from os.path import expanduser
from collections import OrderedDict
from megalus.core import utils
from megalus.core.li_tabulate import tabulate


class Setting():
    """Settings object.

    This objects has the PROJECT properties loaded from
    a json file and the USER properties define
    on the CONFIG_DICT dictionary.
    """

    def __init__(self):
        """Init definition."""
        self.project = None
        basepath = expanduser("~")
        self.path = os.path.join(basepath, ".megalus")
        self.loaded = False

    def show_projects(self):
        """[summary].

        [description]

        Returns:
            [type] -- [description]
        """
        all_projects = [
            filename.replace(".json", "").replace("_", " ").title()
            for root, dirs, file in os.walk(self.path)
            for filename in file
            if filename.endswith(".json")
        ]
        if all_projects:
            utils.console("Projetos disponíveis", style="section")
            for i, app in enumerate(all_projects):
                print("{}. {}".format(i + 1, app))
            print("\n")

    def check_file(self):
        """[summary].

        [description]

        Returns
        -------
            [type] -- [description]

        """
        filename = os.path.join(self.path, "{}.json".format(
            self.project.replace(" ", "_").lower()
        ))
        return os.path.isfile(filename)

    def load(self):
        """[summary].

        [description]
        """
        self.get_current_project()
        if not self.project:
            self.show_projects()
            self.loaded = False
        else:
            if not self.check_file():
                self.loaded = False
            else:
                filename = os.path.join(self.path, "{}.json".format(
                    self.project.replace(" ", "_").lower()
                ))
                with open(filename, "r") as file:
                    config_dict = json.loads(file.read())
                    for key in config_dict:
                        setattr(self, key, config_dict[key])
                self.loaded = True

    def show_project_config(self):
        """[summary].

        [description]

        Returns:
            bool -- [description]
        """
        self.read()
        if not self.loaded:
            return False

        os.system('cls' if os.name == 'nt' else 'clear')
        utils.console(
            "Configuração do projeto {}".format(
                self.project),
            style="section")
        table_data = []
        for key in dir(settings):
            if "__" not in key and key == key.upper() and key != "CONFIG_DICT":
                data = getattr(settings, key)
                if isinstance(data, list):
                    if key == "APPLICATIONS":
                        for i, item in enumerate(data):
                            table_data.append([
                                utils.humanize(key) if i == 0 else "",
                                item[0],
                                utils.humanize(item[1])
                            ])
                    elif key == "LOCAL_DBS":
                        for item in data:
                            for i, config in enumerate(item):
                                table_data.append([
                                    utils.humanize(key) if i == 0 else "",
                                    item['local_name'] if i == 0 else "",
                                    "{}: {}".format(
                                        utils.humanize(config), item[config])
                                ])
                    else:
                        for i, item in enumerate(data):
                            table_data.append([
                                utils.humanize(key) if i == 0 else "",
                                utils.humanize(item)
                            ])
                else:
                    table_data.append(
                        [utils.humanize(key), data]
                    )
        print(tabulate(
            table_data,
            headers=["Variável", "Valor", "Detalhe"]
        ))
        resp = utils.confirma("Deseja atualizar os dados")

        return True

    def create_project(self):
        
        utils.console("Nova configuração para Projeto\n"
            "Projeto selecionado: {}".format(self.project),
            style="main_title",
            use_prefix=False
        )
        dc_path = input("Informe o caminho completo do arquivo docker-compose.yml: ")
        try:
            with open(dc_path, 'r') as file:
                dc_data = yaml.load(file)
        except:
            pass


    def get_current_project(self):
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        setup_path = os.path.join(self.path, '.setup')
        if os.path.isfile(setup_path):
            with open(setup_path, 'r') as file:
                setup_data = json.loads(file.read())
        else:
            setup_data = {
                'project_name': None
            }
            with open(setup_path, 'w') as file:
                json.dump(setup_data, file)
        self.project = setup_data['project_name']


settings = Setting()
settings.load()

settings.CONFIG_DICT = OrderedDict.fromkeys(
    [
        "docker_compose_path",
        "use_for_tests",
        "vcs_username",
        'vcs_password'
    ]
)
settings.CONFIG_DICT['use_for_tests'] = 'unittest'

if getattr(settings, 'USE_AWS', None):
    settings.CONFIG_DICT['aws_key'] = None
    settings.CONFIG_DICT['aws_secret'] = None
    settings.CONFIG_DICT['aws_region'] = None
    settings.CONFIG_DICT['aws_account'] = None

if getattr(settings, 'USE_SLACK', None):
    settings.CONFIG_DICT['slack_url'] = None
    settings.CONFIG_DICT['slack_channel'] = None
    settings.CONFIG_DICT['slack_icon'] = None
    settings.CONFIG_DICT['slack_user'] = None

if getattr(settings, 'USE_DATADOG', None):
    settings.CONFIG_DICT['datadog_api_key'] = None
    settings.CONFIG_DICT['datadog_app_key'] = None

if getattr(settings, 'USE_REDIS', None):
    settings.CONFIG_DICT['redis_host'] = None
    settings.CONFIG_DICT['redis_port'] = None
    settings.CONFIG_DICT['redis_db'] = None

if getattr(settings, 'USE_MEMCACHED', None):
    settings.CONFIG_DICT['memcached_host'] = None
    settings.CONFIG_DICT['memcached_port'] = None
