"""[summary].

[description]
"""
import os
from megalus.core import utils
from megalus.projects.config import profile


def run(application, port):
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
        return False

    container_id, name = utils.get_app(
        application=application,
        title="Rodar Telnet",
        data=data
    )

    if not container_id:
        return False

    os.chdir(data.project_path)
    os.system(
        'docker exec -ti {} telnet 127.0.0.1 {}'.format(
            container_id, port
        )
    )
    return False
