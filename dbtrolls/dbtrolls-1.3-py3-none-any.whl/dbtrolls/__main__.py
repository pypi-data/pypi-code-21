#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

import os
import fnmatch
import yaml
import subprocess

from optparse import OptionParser


cfg = None
if os.path.isfile("config.yml"):
    with open("config.yml", 'r') as yml_file:
        cfg = yaml.load(yml_file)


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def cfg_exist():
    result = True
    if not cfg:
        print('First you need create a config file named as config.yml')
        result = False
    return result

def create_pipe(sql):
    read, write = os.pipe()
    os.write(write, sql.encode())
    os.close(write)
    return read


def create_config(parser, options, args):
    CONFIG_TEMPLATE = """### Example

mysql:
    host: 10.0.0.18
    user: root
    passwd: ff3cff653c36946f0bb3964f7a194edd
    database_source: {database_source}
    database_target: {database_target}

preload:
    path: /var/www/api.padrao.wpensar.intranet/current
    files: ['pre.sql']

container:
    path: /home/caputo/Projects/padrao/__docs/sql
    files: ['cpf_valido.sql', 'data_vencimento_util.sql', 'dia_util.sql', 'dv_barra_bb.sql',
            'feriado.sql', 'primeiro_nome.sql', 'sacado_valido.sql', 'sobrenome.sql',
            'valor_esperado_cobranca.sql', 'valor_esperado_cobranca_curso_livre.sql', 'valor_esperado_parcela.sql',
            'atualizar_pagamentos.sql', 'criar_analista.sql', 'evento_financeiro_excluir.sql',
            'evento_financeiro_inserir.sql', 'evento_financeiro_trocar.sql', 'replicar_ano_letivo.sql',
            'aluno_atualizacao.sql', 'aluno_cadastro.sql', 'cobranca_atualizacao.sql', 'matricula_data_atualizacao.sql',
            'matricula_data_cadastro.sql', 'matricula_delete_after.sql', 'parcela_atualizacao.sql', 'parcela_cadastro.sql',
            'responsavel_atualizacao.sql', 'responsavel_cadastro.sql', 'updade_usuario_on_insert.sql', 'aluno_inscricao_curso.sql',
            'aluno_matriculas.sql', 'sacado.sql', 'sacado_novo.sql', 'usuario_pessoa.sql']

fix:
    - sed -i 's/{database_source}/{database_target}/g' {database_source}.sql
    - sed -i 's/datetime(6)/datetime/g' {database_source}.sql
    - sed -i 's/time(6)/time/g' {database_source}.sql
    - sed -i 's/DEFINER=`user_l_sorrentin`@`%`//g' {database_source}.sql
    - sed -i 's/DEFINER=`app_padrao`@`%`//g' {database_source}.sql
    - sed -i 's/DEFINER=`app_financeiro`@`%`//g' {database_source}.sql
    - sed -i 's/DEFINER=`wpensar`@`%`//g' {database_source}.sql
    - sed -i 's/DEFINER=`app_financeiro`@`%`//g' {database_source}.sql
    - sed -i 's/DEFINER=`app_financeiro`@`209.59.219.243`//g' {database_source}.sql
""".format(database_source=options.database_source, database_target=options.database_target)

    with open('config.yml', "w+") as a_file:
        a_file.write(CONFIG_TEMPLATE)
        a_file.close()
    print("Well Done!")


def run_file(queries):
    if cfg_exist():
        command = ["mysql",

                   "-h{host}".format(host=cfg['mysql']['host']),
                   "-u{user}".format(user=cfg['mysql']['user']),
                   "-p{passwd}".format(passwd=cfg['mysql']['passwd']),
                   "{database}".format(database=cfg['mysql']['database_target'])]
        proc = subprocess.Popen(command, stdin=queries, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = proc.communicate()
        return stdout


def run_single(parser, options, args):
    if cfg_exist():
        if options.preload:
            print('\n Execute Preload Files...\n')
            container = cfg['preload']['files']
            for sql in container:
                file_path = find(sql, cfg['preload']['path'])
                if os.path.isfile(file_path[0]):
                    with open(file_path[0], 'r') as queries:
                        stdout = run_file(queries)
                        if not stdout:
                            print("ok => {script} \n".format(script=sql))
                        else:
                            print("nok => {script} \n {stdout}\n".format(script=sql, stdout=stdout))

        if options.fix:
            print('\n Fix SQL file...\n')
            for i in cfg['fix']:
                stdout, stderr = subprocess.Popen(i, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                  shell=True).communicate()

                if not stdout:
                    print("ok => {script}".format(script=i))
                else:
                    print("nok => {script} \n {stdout}\n".format(script=i, stdout=stdout))

        if args:
            file_name = args[0]
            print('\n Execute Single SQL file...\n')
            with open(file_name, 'r') as queries:
                stdout = run_file(queries)
                if not stdout:
                    print("ok => {script}".format(script=file_name))
                else:
                    print("nok => {script} \n {stdout}\n".format(script=file_name, stdout=stdout))


def run_multiple(parser, options, args):
    if cfg_exist():
        print('Execute Multiple SQL files...\n')
        container = cfg['container']['files']
        for sql in container:
            file_path = find(sql, cfg['container']['path'])
            with open(file_path[0], 'r') as queries:
                stdout = run_file(queries)
                if not stdout:
                    print("ok => {script}".format(script=sql))
                else:
                    print("nok => {script} \n {stdout}\n".format(script=sql, stdout=stdout))


COMMANDS = {
    'config': create_config,
    'single': run_single,
    'multiple': run_multiple,
}


def main():
    # Parse options
    parser = OptionParser(usage="Usage: %prog -s <SQL_FILE>")

    parser.add_option("-c", "--config",
                      action="store_true",
                      help="Create config file")

    parser.add_option("--database_source",
                      action="store")

    parser.add_option("--database_target",
                      action="store")

    parser.add_option("-s", "--single",
                      action="store_true",
                      help="Execute single SQL file.")

    parser.add_option("-m", "--multiple",
                      action="store_true",
                      help="Execute multiple SQL files.")

    parser.add_option("-f", "--fix",
                      action="store_true",
                      help="Set fix true.")

    parser.add_option("-p", "--preload",
                      action="store_true",
                      help="Preload and Execute extra SQL files. ")


    (options, args) = parser.parse_args()

    if options.single:
        command = 'single'
    elif options.multiple:
        command = 'multiple'
    elif options.config:
        command = 'config'
    else:
        try:
            command = args[0]
        except IndexError:
            parser.print_help()
        return

    if command in COMMANDS:
        COMMANDS[command](parser, options, args)
    else:
        parser.error("Unrecognised command: " + command)


if __name__ == "__main__":
    main()
