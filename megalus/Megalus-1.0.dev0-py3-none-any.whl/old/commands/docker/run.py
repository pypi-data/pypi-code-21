"""[summary].

[description]
"""
import os
from megalus.core import utils
from megalus.projects.config import profile


def run(application, action, opt=None, arg=None):
    """[summary].

    [description]

    Arguments:
        application {[type]} -- [description]
        action {[type]} -- [description]

    Keyword Arguments:
        opt {[type]} -- [description] (default: {None})
        arg {[type]} -- [description] (default: {None})

    Returns
    -------
        bool -- [description]

    """
    data = profile.get_data()
    if not data:
        return False

    name = ""
    container_id = None
    if application:
        container_id, name = utils.get_app(
            application=application,
            title="Build/Run da Aplicacao",
            data=data,
            stop=False if action == "exec" else True
        )
        if not container_id:
            return False

    if action == "exec":
        utils.console("Rodando comando '{}' em '{}'".format(
            " ".join(arg), name), style="warning", use_prefix=False)
        os.system(
            "docker {cmd} -ti {app}{arg}".format(
                cmd=action,
                app=container_id,
                arg=" {}".format(" ".join(arg)) if arg else "")
        )
    else:
        # Parar os containers
        utils.stop_all(data)

        # Rodar o comando
        os.system(
            "cd {folder} && docker-compose {cmd} {opt} {app}".format(
                folder=data['docker_compose_path'],
                cmd=action,
                app=name,
                opt=opt if opt else "")
        )
    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    if action == "run":
        os.system(
            "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
        )
