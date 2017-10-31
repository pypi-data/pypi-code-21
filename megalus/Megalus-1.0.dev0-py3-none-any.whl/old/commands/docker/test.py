"""[summary].

[description]
"""
import os
import re
from megalus.core import utils
from megalus.projects.config import profile
from megalus.projects.setup import settings
from megalus.core.messages import notify


def run(application, using, rds, verbose):
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
        title="Rodar Teste",
        data=data
    )

    if not container_id:
        return False

    finalmsg = "Teste não efetuado."
    # Rodar o container com o endereco do
    # Banco de dados selecionado
    dbdata = [
        obj
        for obj in settings.LOCAL_DBS
        if obj.get('admin') == name
    ]
    if rds:
        host = dbdata[0].get('stage_name', None)
        port = dbdata[0].get('stage_port', None)
    else:
        host = dbdata[0].get('local_name', None)
        port = dbdata[0].get('local_port', None)

    if not host or not port:
        utils.console("Nome ou Porta do Banco não encontrado.", style="error")
        return False

    os.chdir(data.project_path)
    # Parar o container
    print(("Rodar Testes - {}".format(name)))
    print("Reiniciando container...")
    utils.run_command(
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

    # Encontrar o programa
    test_app = using if using else data['use_for_tests']
    if not using:
        check_list = [test_app] + settings.TEST_PRIORITY
        ret_pip = utils.run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': "cd {} && "
                    "docker-compose run {} pip freeze".format(
                        data['docker_compose_path'],
                        name),
                    'run_stdout': False}])
        for test in check_list:
            if "{}==".format(test) in ret_pip:
                test_app = test
                break

    # Checa se o coverage está instalado
    dependencies_found = True
    if test_app != "pytest" and 'coverage' not in ret_pip:
        dependencies_found = False
    if 'pydocstyle' not in ret_pip:
        dependencies_found = False
    if 'pycodestyle' not in ret_pip:
        dependencies_found = False
    if test_app == "pytest" and 'pytest-cov' not in ret_pip:
        dependencies_found = False

    # Rodar novo container
    # Para Unittest, Django, Pytest e Nose rodar via Docker-Compose
    new_container_id = utils.run_command(
        get_stdout=True,
        command_list=[
            {
                'command': "cd {} && docker-compose "
                "run -d -e DATABASE_HOST={} -e DATABASE_PORT={} {}".format(
                    data['docker_compose_path'],
                    host,
                    port,
                    name),
                'run_stdout': False},
        ])

    if new_container_id and dependencies_found:

        new_container_id = new_container_id.replace("\n", "")

        database_path = utils.run_command(
            get_stdout=True,
            command_list=[
                {
                    'command': "docker exec -ti {} printenv"
                    " | grep DATABASE_HOST".format(
                        new_container_id),
                    'run_stdout': False
                }
            ]
        )
        os.system('cls' if os.name == 'nt' else 'clear')
        titletext = "Rodando testes com: {}".format(test_app.upper()) + \
            "\nUsando banco de dados: {}".format(
            database_path.replace("\n", "").replace("\r", "").split("=")[1])
        utils.console(titletext, style="main_title", use_prefix=False)

        if test_app == "django":
            command = "coverage run --source='.' manage.py test{}".format(
                ' -v2' if verbose else ""
            )
        elif test_app == "nose":
            command = "nosetests --with-coverage --cover-package=app"
        elif test_app == "pytest":
            command = "pytest --cov=.{}".format(
                " --verbose" if verbose else "")
        else:
            command = "coverage run -m unittest discover -v -s /opt/app"

        os.system(
            'docker exec -ti {} {}'.format(
                new_container_id, command
            )
        )
        # Coverage

        utils.console("Coverage Result", style="section")
        coverage_data = utils.run_command(
            get_stdout=True,
            command_list=[
                {
                    "command": "docker exec -ti {} "
                    "coverage report -m --skip-covered".format(
                        new_container_id),
                    "run_stdout": False
                }
            ]
        )
        print(coverage_data)
        match_groups = re.finditer("(\d+%)", coverage_data)
        min_coverage = os.environ.get('MIN_COVER', 80)
        coverage_total = [
            match.group()
            for match in match_groups
        ][-1]
        coverage_level = int(coverage_total.replace("%", ""))
        coverage_result = True if coverage_level >= min_coverage else False
        if coverage_result:
            utils.console(
                'Result: OK ({}/{})'.format(
                    coverage_level, min_coverage),
                style="success"
            )
        else:
            utils.console(
                'Result: FAIL ({}/{})'.format(
                    coverage_level, min_coverage),
                style="error"
            )

        # PEP8
        pep8_result = utils.run_command(
            title="PEP8 Check",
            get_stdout=False,
            command_list=[
                {
                    "command": "docker exec -ti {} "
                    "pycodestyle {}--exclude=manage.py,settings.py,"
                    "venv,migrations,frontend .".format(
                        new_container_id,
                        "--show-source " if verbose else ""),
                    "run_stdout": False}])

        if pep8_result:
            utils.console('Result: OK', style="success")
        else:
            utils.console('Result: FAIL', style="error")

        # PEP257
        pep257_result = utils.run_command(
            title="PEP257 Check",
            get_stdout=False,
            command_list=[
                {
                    "command": "docker exec -ti {} pydocstyle"
                    " --match-dir='[^venv|^migrations|^frontend].*' "
                    "--match='(?!__|manage).*\.py'".format(
                        new_container_id
                    ),
                    "run_stdout": False
                }
            ]
        )
        if pep257_result:
            utils.console('Result: OK', style="success")
        else:
            utils.console('Result: FAIL', style="error")

        utils.console("Final Result", style="section")
        if coverage_result and pep8_result and pep257_result:
            finalmsg = "Todos os Testes passaram com sucesso."
            utils.console(finalmsg, style="success")
        else:
            finalmsg = "ERROS ENCONTRADOS "
            "DURANTE OS TESTES. Verifique os logs."
            utils.console(finalmsg, style="error")

    elif not dependencies_found:
        utils.console(
            "Verifique se estão instalados no container: "
            "pytest-cov, coverage, pydocstyle ou pycodestyle",
            style="error")
    else:
        utils.console("Nenhum container encontrado", style="error")

    print("\n------------\nReiniciando container...")
    os.system("docker stop {}".format(new_container_id))
    os.system(
        "cd {} && docker-compose "
        "up -d {}".format(
            data['docker_compose_path'], name))

    # Exclui container extra
    # docker rm $(docker ps -a | grep host_run |  awk '{print $1}')
    os.system(
        "docker rm $(docker ps -a | grep _run_ |  awk '{print $1}')"
    )
    notify(msg="Teste Unitário em {}: {}".format(name, finalmsg))
    return False
