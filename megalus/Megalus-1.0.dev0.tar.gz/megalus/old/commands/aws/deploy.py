"""[summary].

[description]
"""
import json
import os
import re
from git import Repo
from megalus.commands.bash import compress
from megalus.core.messages import Message, notify
from megalus.core.utils import run_command, confirma, console
from megalus.projects.config import profile
from megalus.projects.setup import settings


def run(only_pr=False):
    """Function: run.

    Summary: InsertHere
    Examples: InsertHere
    Attributes:
        @param (only_pr) default=False: InsertHere
    Returns: InsertHere
    """
    config = profile.get_data()

    if not config:
        return False

    current_dir = os.getcwd()
    folder_name = os.path.split(current_dir)[-1]
    try:
        repo = Repo(current_dir)
        branch = repo.active_branch
    except BaseException:
        text = [
            "Repositório GIT não encontrado.",
            "O comando deve ser executado na pasta raiz",
            "do repositório a ser enviado.",
            "Comando abortado."
        ]
        console(text, humanize=True, style="error")
        return False
    branch_name = branch.name

    if not only_pr:
        if branch.name == 'master':
            text = " \
                A branch 'master' não \
                pode ser atualizada diretamente,\
                Utilize o comando 'meg ci'. \
                Consulte a ajuda, para mais detalhes."
            console(text, style="error")
            return False

        # Pega a pasta atual e verifica
        # se é uma pasta valida para deploy
        app_list = [
            app.lower()
            for app, br in settings.APPLICATIONS
        ]

        if folder_name.lower() not in app_list:
            console("Repositório não reconhecido", style="error")
            return False

        # Confirma operação
        branch_name = branch.name
        last_commit = repo.head.commit.message
        text_repo = console(folder_name, style="info", format_only=True)
        print("Repositório: {}".format(text_repo))
        if branch_name in ['production', 'master']:
            text_branch = console(
                branch_name.upper(),
                bold=True,
                style="error",
                use_prefix=False,
                format_only=True)
        else:
            text_branch = branch_name.upper()
        print("Branch Atual: {}".format(text_branch))
        text = console(
            last_commit,
            style="warning",
            use_prefix=False,
            format_only=True)
        print("Último Commit:\n{}".format(last_commit))

        # Roda EB Status
        eb_status = False
        ret = run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': "eb status",
                    'run_stdout': False
                }
            ]
        )
        if ret:
            m = re.search("Status: (\w+)", ret)
            if m:
                eb_status_name = m.group(1)
                if eb_status_name == "Ready":
                    eb_status = True
                text = console(
                    eb_status_name.upper(),
                    style="success" if eb_status else "error",
                    use_prefix=False,
                    format_only=True
                )
                print("\nO Status do ElasticBeanstalk é: {}".format(text))
            else:
                console(ret, style="error")

        if not eb_status:
            return False

        resposta = confirma("Confirma o Deploy")
        if not resposta:
            return False

    # Se existir a pasta frontend
    # rodar o build do webpack
    wbpath = os.path.join(current_dir, 'frontend')
    if os.path.exists(wbpath):
        ret = run_command(
            get_stdout=False,
            title="Gerando Build do Webpack",
            command_list=[
                {
                    'command': 'cd {} && ./node_modules/.bin/webpack'
                    ' --config webpack.config.deploy.js'.format(wbpath),
                    'run_stdout': False
                }
            ]
        )
        if not ret:
            return False

    # Ações específicas do App
    # 1. Minify manual
    if folder_name in settings.MINIFY_BEFORE:
        console("Minificando arquivos estáticos", style="section")
        ret = compress.minifyCSS(current_dir=current_dir)
        if not ret:
            return False

        ret = compress.minifyJS(current_dir=current_dir)
        if not ret:
            return False

    # 2. Sincronizar estáticos
    if folder_name in settings.SYNC_S3:
        ret = run_command(
            title="Sincronizando arquivos "
            "estáticos no S3/{}".format(branch_name),
            command_list=[
                {
                    'command': settings.S3_SYNC_CMD.format(
                        branch=branch_name),
                    'run_stdout': False}])
        if not ret:
            return False

    # Gera Dockerrun
    app_name = settings.ECR_NAME.get(folder_name, None)
    if not app_name:
        app_name = folder_name.lower()
    json_model = {
        'AWSEBDockerrunVersion': '1',
        'Image': {
            'Name': '{account}.dkr.ecr.{region}'
            '.amazonaws.com/{app}:{branch}'.format(
                account=config['aws_account'],
                app=app_name,
                branch=branch_name if not only_pr else "master",
                region=config['aws_region']),
            'Update': 'true'},
        'Ports': [
            {
                'ContainerPort': '80'
            }
        ],
        "Volumes": [
            {
                "HostDirectory": "/tmp",
                "ContainerDirectory": "/tmp"
            }
        ],
        'Logging': "/var/eb_log"}

    with open("./Dockerrun.aws.json", 'w') as file:
        file.write(json.dumps(json_model, indent=2))

    if only_pr:
        last_commit = "Pull Request para versão {}".format(
            repo.tags[-1].name)

    ret = run_command(
        title="Adiciona Dockerrun",
        command_list=[
            {
                'command': "git add .",
                'run_stdout': False
            },
            {
                'command': "git commit -m \"{}\"".format(last_commit),
                'run_stdout': False
            }
        ]
    )

    # Atualiza VCS
    ret = run_command(
        title="Atualiza {} - {}".format(settings.VCS_NAME, folder_name),
        command_list=[
            {
                'command': "git push origin {}".format(branch.name),
                'run_stdout': False
            }
        ]
    )
    if not ret:
        return False

    if not only_pr:
        title = "Deploy Iniciado para ".format(folder_name)
        text = "O usuário {} iniciou Deploy do {} para o commit {}".format(
            config['vcs_username'], folder_name, last_commit)
        tags = ['Deploy']

        # Envia Mensagem Datadog/Slack
        if branch.name in ['production', 'master']:
            message = Message(
                config=config,
                branch=branch.name,
                title=title,
                text=text,
                repo=folder_name
            )
            message.send(alert_type="warning", tags=tags)

    # Gerar imagem base do Docker
    dockerbasepath = os.path.join(
        config['project_path'],
        settings.DOCKER_BASE_IMAGE_REPO,
        'baseimage'
    )
    ret = run_command(
        title="Gera Imagem Base do Docker",
        command_list=[
            {
                'command': "aws ecr get-login "
                "--region {region}".format(region=config['aws_region']),
                'run_stdout': True
            },
            {
                'command': "cd {path} && docker build -t {app}:dev .".format(
                    path=dockerbasepath,
                    app=settings.DOCKER_BASE_IMAGE_REPO
                ),
                'run_stdout': False
            },
            {
                'command': "docker tag {base}:dev "
                "{account}.dkr.ecr.{region}.amazonaws.com"
                "/{base}:latest".format(
                    base=settings.DOCKER_BASE_IMAGE_REPO,
                    account=config['aws_account'],
                    region=config['aws_region'],
                ),
                'run_stdout': False
            },
            {
                'command': "docker push {account}."
                "dkr.ecr.{region}.amazonaws.com/{base}:latest".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    base=settings.DOCKER_BASE_IMAGE_REPO
                ),
                'run_stdout': False
            },
        ]
    )
    if not ret:
        return False

    # Gerar imagem do Docker
    ret = run_command(
        title="Gera Imagem no Docker - {}".format(folder_name),
        command_list=[
            {
                'command': "docker build -f {name} -t {app}:{branch} .".format(
                    name=settings.DOCKERFILE_DEPLOY,
                    app=app_name,
                    branch=branch_name if not only_pr else "master"
                ),
                'run_stdout': False
            },
            {
                'command': "docker tag {app}:{branch} "
                "{account}.dkr.ecr.{region}.amazonaws.com"
                "/{app}:{branch}".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=app_name,
                    branch=branch_name if not only_pr else "master"
                ),
                'run_stdout': False
            },
            {
                'command': "docker push {account}."
                "dkr.ecr.{region}.amazonaws.com/{app}:{branch}".format(
                    account=config['aws_account'],
                    region=config['aws_region'],
                    app=app_name,
                    branch=branch_name if not only_pr else "master"
                ),
                'run_stdout': False
            },
        ]
    )
    if not ret:
        return False

    if only_pr:
        return True

    # Rodar EB Deploy
    ret = run_command(
        title="Rodando EB Deploy - {}".format(folder_name),
        command_list=[
            {
                'command': "eb deploy --timeout 60",
                'run_stdout': False
            }
        ]
    )
    if not ret:
        return False

    title = "Deploy Finalizado para ".format(folder_name)
    text = "O Deploy para {} foi finalizado.".format(folder_name)
    tags = ['Deploy']

    # Envia Mensagem Datadog/Slack
    if branch.name in ['production', 'master']:
        message = Message(
            config=config,
            branch=branch.name,
            title=title,
            text=text,
            repo=folder_name
        )
        message.send(alert_type="success", tags=tags)

    notify(msg="O Deploy do {} foi finalizado".format(folder_name))
    return True
