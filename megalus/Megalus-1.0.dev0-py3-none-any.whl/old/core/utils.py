import os
import subprocess
import sys
import yaml
from colorama import Fore, Back, Style
from unidecode import unidecode


def get_style(format_type):
    """Function: get_color.

    Summary: return text format color for correpondent type
    Examples: get_color("error")

    Attributes
    ----------
        @param (format_type):string

    Returns
    -------
    Object: Colorama instance

    """
    return {
        'start': Fore.BLUE,
        'error': Fore.RED,
        'success': Fore.GREEN,
        'info': Fore.YELLOW,
        'warning': Fore.YELLOW,
        'section': Fore.YELLOW,
        'git': Back.LIGHTBLUE_EX + Fore.YELLOW,
        'main_title': Fore.BLUE,
        'grey': Fore.LIGHTBLACK_EX
    }.get(format_type, "")


def console(
        text,
        style=None,
        humanize=False,
        format_only=False,
        use_prefix=True,
        bold=False):
    """Function: console.

    Summary: print command replacement using colors
    Examples: console("Hello World!", style="title")

    Attributes
    ----------
        @param (text):String
        @param (style) default=None: String
        @param (humanize) default=False: Bool
        @param (format_only) default=False: Bool
        @param (use_prefix) default=True: Bool
        @param (bold) default=False: Bool

    Returns
    -------
    String or stdout
    """
    if use_prefix and style not in ['section']:
        text = "{}: {}".format(style.upper(), text)
    if humanize:
        text = humanize(text)
    if style == "section":
        line1 = "\n>> {}\n".format(text)
        line2 = "{:*^{num}}\n".format('', num=len(line1) - 2)
        text = line1 + line2
    if style == "main_title":
        line_sizes = [
            len(line)
            for line in text.split("\n")
        ]
        longest_line = sorted(line_sizes, reverse=True)[0]

        horizontal_line = "{:*^{num}}".format('', num=longest_line + 6)
        vertical_line = "*{:^{num}}*".format('', num=longest_line + 4)

        main_texts = [
            "*{:^{num}}*".format(
                text_line, num=longest_line + 4
            )
            for text_line in text.split("\n")
        ]
        text = "{}\n{}\n{}\n{}\n{}".format(
            horizontal_line,
            vertical_line,
            "\n".join(main_texts),
            vertical_line,
            horizontal_line
        )
    if style:
        text = "{}{}{}".format(
            get_style(style),
            text,
            Style.RESET_ALL
        )
    if bold:
        text = "{}{}".format(Style.BRIGHT, text)

    if format_only:
        return text
    else:
        print(text)


def confirma(pergunta, warning=False):
    """Retorna S ou N"""
    resposta_ok = False
    text = console(
        "\n{} (s/n)? ".format(pergunta),
        style="warning" if not warning else "error",
        use_prefix=False,
        format_only=True
    )
    while not resposta_ok:
        resposta = input(text)
        if resposta and resposta[0].upper() in ["S", "N"]:
            resposta_ok = True
    return resposta[0].upper() == "S"


def unitext(text):
    text = unidecode(text)
    return text


def run_command(command_list, title=None, get_stdout=False):
    if title:
        console(title, style="section")
    try:
        for task in command_list:
            if task.get('run_stdout', None):
                command = subprocess.check_output(
                    task['command'],
                    shell=True
                )

                if not command:
                    print('Ocorreu um erro. Processo abortado')
                    return False

                ret = subprocess.call(
                    command,
                    shell=True
                )
            elif get_stdout is True:
                ret = subprocess.check_output(
                    task['command'],
                    shell=True
                )
            else:
                ret = subprocess.call(
                    task['command'],
                    shell=True,
                    stderr=subprocess.STDOUT
                )

            if ret != 0 and not get_stdout:
                # print('Ocorreu um erro. Processo abortado')
                return False
    except BaseException:
        return False

    return True if not get_stdout else ret.decode('utf-8')


def get_app(application, data, title=None, stop=False, no_container=False):
    # 1. Lista todos os containers que estao rodando
    # docker ps -a | grep painel | awk '{print $1,$2}'
    if not stop:
        ret = run_command(
            title=title,
            get_stdout=True,
            command_list=[
                {
                    'command': "docker ps | awk '{print $1, $NF}'",
                    'run_stdout': False
                }
            ]
        )
    else:
        ret = run_command(
            title=title,
            get_stdout=True,
            command_list=[
                {
                    'command': "docker ps -a | awk '{print $1, $NF}'",
                    'run_stdout': False
                }
            ]
        )
        if no_container:
            ret = ret.replace('CONTAINER NAMES\n', '')
            if not ret:
                dc = get_compose_data(data)
                ret = [
                    "0 {}".format(dc['services'][container]['container_name'])
                    for container in dc['services']
                ]
                ret = "\n".join(ret)

    raw_list = ret.split('\n')

    app_list = []

    for obj in raw_list:
        if obj.startswith("CONTAINER"):
            continue
        if len(obj.split(" ")) != 2:
            continue

        app_list.append((
            obj.split(" ")[0],
            obj.split(" ")[1]
        ))

    # 2. Identifica qual o container que bate com o app solicitado
    filtered_list = [
        app
        for app in app_list
        if application and application in app[1]
    ]

    ask_for_app = False
    if filtered_list:
        if len(filtered_list) == 1:
            return (filtered_list[0][0], filtered_list[0][1])
        else:
            ask_for_app = True
    elif app_list:
        ask_for_app = True
    else:
        print("Nenhum aplicativo encontrado.")
        return (None, None)

    if ask_for_app:
        all_apps = filtered_list or app_list
        choices = [
            app[1]
            for app in all_apps
        ]
        rep = escolha(choices)
        return (all_apps[int(rep) - 1][0], all_apps[int(rep) - 1][1])

def escolha(choices):
    i = 1
    for choice in enumerate(choices):
        print("{}. {}".format(i + 1, choice))
    resposta_ok = False
    print("\n")
    while not resposta_ok:
        try:
            rep = input(
                "Selecione (1-{}): ".format(i - 1))
            if rep and int(rep) in range(1, i):
                resposta_ok = True
        except KeyboardInterrupt:
            print("\n")
            return (None, None)
        except BaseException:
            pass
    return rep


def progress_bar(iteration, total, prefix='Lendo',
                 suffix='Complete', barLength=50):
    """
    Gerador de Barra de Progresso
    """
    formatStr = "{0:.2f}"
    percents = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write(
        '\r%s |%s| %s%s %s ' %
        (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()


def get_compose_data(data):
    dc_path = os.path.join(
        data['docker_compose_path'],
        'docker-compose.yml'
    )

    with open(dc_path, 'r') as file:
        dc_data = yaml.load(file)

    return dc_data


def stop_all(data):
    run_command(
        get_stdout=False,
        title=None,
        command_list=[
            {
                'command': "cd {} && docker-compose stop".format(
                    data['docker_compose_path']),
                'run_stdout': False}])
    ret_docker = run_command(
        get_stdout=True,
        command_list=[
            {
                'command': 'docker ps -q',
                'run_stdout': False
            }
        ]
    )
    if ret_docker:
        run_command(
            get_stdout=False,
            command_list=[
                {
                    'command': 'docker stop $(docker ps -q)',
                    'run_stdout': False
                }
            ]
        )


def humanize(data):
    if isinstance(data, str):
        ret = data.replace("_", " ").title()
    if isinstance(data, bool):
        ret = "Sim" if data else "Não"
    if isinstance(data, list) or isinstance(data, tuple):
        ret = ", ".join(data)
    if isinstance(data, dict):
        ret = "\n".join([
            "{}: {}: {}".format(i + 1, key, data[key])
            for i, key in enumerate(data)
        ])

    return ret
