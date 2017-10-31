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
        port {[type]} -- [description]

    Returns
    -------
        bool -- [description]

    """
    data = profile.get_data()
    if not data:
        utils.console("Configuração não encontrada", style="error")
        return False

    container_id, name = utils.get_app(
        application=application,
        title="Rodar Bash",
        data=data
    )

    if not container_id:
        utils.console("Container não encontrado", style="error")
        return False

    os.chdir(data.project_path)
    os.system(
        'docker exec -ti {} /bin/bash'.format(
            container_id
        )
    )
    return True
