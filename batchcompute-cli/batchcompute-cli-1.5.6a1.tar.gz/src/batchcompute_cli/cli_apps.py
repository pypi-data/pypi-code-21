# -*- coding: utf-8 -*-
from terminal import red
from .externals.command import Command

from . import const,i18n_util
from .action import app,job_asub,app_del,app_create,app_update

from batchcompute.core.exceptions import ClientError

COMMAND = const.COMMAND
CMD = const.CMD

IMG_ID = 'img-xxxxxx'
INS_TYPE = 'ecs.s3.large'

VERSION = const.VERSION

IS_GOD = const.IS_GOD


# SPLITER = '\n    --%s' + ('-' * 40)

MSG=i18n_util.msg()


def asub():
    cmd = Command('asub',
                       arguments=['app_name','job_name'],
                       description=MSG['asub']['description'],
                       usage='''Usage: %s asub <app_name> [job_name] [option]

        Examples:

            1. %s asub app_name -h              # show all options of app
            2. %s asub app_name job_name --input_[input_key]=[input_value] --output_[input_key]=[input_value]
            3. %s asub app_name job_name --input_from_file_[input_key]=[input_value]
            ''' % (COMMAND, CMD, CMD, CMD), func=job_asub.asub)
    cmd.option("--description [description]", MSG['asub']['option']['description'])
    cmd.option("-r, --resource_type [resource_type]", MSG['asub']['option']['resource_type'])
    cmd.option("-t, --type [instance_type]", MSG['asub']['option']['type'])
    cmd.option("-n, --nodes [instance_count]", MSG['asub']['option']['nodes'])
    cmd.option("--min_disk_size [min_disk_size]", MSG['asub']['option']['min_disk_size'])
    cmd.option("-d, --disk_type [disk_type]", MSG['asub']['option']['disk_type'])
    cmd.option("--max_retry_count [max_retry_count]", MSG['asub']['option']['max_retry_count'])
    cmd.option("--timeout [timeout]", MSG['asub']['option']['timeout'])
    cmd.option("--config [config]", MSG['asub']['option']['config'], resolve=job_asub.trans_config, visible=IS_GOD)

    return cmd


# 追加 option
def asub_app_options(app_name, cmd):

    desc = {}
    try:
        (desc,app_name_p) = job_asub.get_app(app_name)
    except ClientError as e:
        if e.get_status_code() == 404:
            raise Exception('NotFound App named %s' % app_name)

    cmd.option("--show_json", '%s\n    %s' % (MSG['asub']['option']['show_json'], MSG['asub']['option']['param_desc']))

    inputs = desc.get('InputParameters')

    if inputs:
        for k,v in inputs.items():
            _set_option('Input', k, v, cmd)

    outputs = desc.get('OutputParameters')

    if outputs:
        for k, v in outputs.items():
            _set_option('Output', k, v, cmd)


def _set_option(title, k, v, cmd):
    type = v.get('Type')
    default_value = v.get('Default')
    description = v.get('Description')

    dstr = ['%s Parameters' % title]
    if type: dstr.append('Type: %s' % type)
    if default_value: dstr.append('Default: %s' % default_value)
    if description: dstr.append('%s' % description)

    # if title=='Input':
    #     dstr.append(MSG['asub']['option']['inputs'])
    # else:
    #     dstr.append(MSG['asub']['option']['outputs'])

    if type == 'Boolean':
        cmd.option("--%s" % k, ', '.join(dstr))
    else:
        if title=='Input':
            cmd.option("--i%s [%s]" % (k,k), ', '.join(dstr), visible=False)
            cmd.option("--input_from_file_%s [%s]" % (k,k), ', '.join(dstr), visible=False)
            cmd.option("--input_%s [%s]" % (k,k), ', '.join(dstr))
        else:
            cmd.option("--output_%s [%s]" % (k, k), ', '.join(dstr))
            cmd.option("--o%s [%s]" % (k, k), ', '.join(dstr), visible=False)


def delete():
    cmd = Command('delete_app', alias=['da'],
                          arguments=['app_name', 'revision'],
                          description=MSG['delete_app']['description'],
                          usage='''Usage: %s delete_app|da [app1,app2...] [revision] [option]

    Examples:

        1. %s da app_name1,app_name2        # delete app and all revisions
        2. %s da app_name 1                 # only delete revision==1
        ''' % (COMMAND, CMD, CMD),
                          func=app_del.delete)


    cmd.option("-y, --yes", MSG['delete_app']['option']['yes'])
    return cmd

def update():
    cmd_update_app = Command('update_app', alias=['ua'],
                             arguments=['app_name','cmd'],
                             description=MSG['update_app']['description'],
                             usage='''Usage: %s update_app|ua <app_name> [cmd] [option]

    Examples:
        1. %s ua app_name "echo 'hello2'"                            # update cmd
        2. %s ua app_name --docker myubuntu@oss://bucket/dockers/    # update docker Container
        3. %s ua app_name -i m-xxxx                                  # update VM
        4. %s ua app_name -e a:1,b:2                                 # update env vars
        5. %s ua app_name --daemonize true                           # update daemonize
        6. %s ua app_name -description demo                          # update description
        ''' % (COMMAND, CMD, CMD, CMD, CMD, CMD, CMD),
                             func=app_update.update)


    cmd_update_app.option("--docker [docker]", MSG['update_app']['option']['docker'])
    cmd_update_app.option("-i, --image [image]", MSG['update_app']['option']['image'])
    cmd_update_app.option("-e, --env [kv_pairs]", MSG['update_app']['option']['env'],
                          resolve=app_update.trans_env)


    cmd_update_app.option("--daemonize [daemonize]", MSG['update_app']['option']['daemonize'])
    cmd_update_app.option("--description [description]", MSG['update_app']['option']['description'])
    cmd_update_app.option("-y,--yes", MSG['update_app']['option']['yes'])
    cmd_update_app.option("--show_json",
                          MSG['update_app']['option']['show_json'])

    return cmd_update_app

def create():
    cmd_create_app = Command('create_app', alias=['ca'],
                             arguments=['app_name', 'cmd'],
                             description=MSG['create_app']['description'],
                             usage='''Usage: %s create_app|ca <app_name> <cmd> [option]

    Examples:

        1. %s ca app_name "echo 'hello'" --docker myubuntu@oss://bucket/dockers/    # create a docker Container app
        2. %s ca app_name "echo 'hello'" -i m-xxxx                                           # create a VM Container app
        3. %s ca app_name "echo 'hello'" -e a:1,b:2
        4. %s ca app_name "echo 'hello'" -t ecs.t1.small        # default overwritable is false
        5. %s ca app_name "echo 'hello'" -t ecs.t1.small:true   # overwritable is true
        6. %s ca app_name "echo 'hello'" --inputs input1:String:luogc::,input2,input3   # with 3 input parameters
        7. %s ca --file app1.json      # create app from file
        ''' % (COMMAND, CMD, CMD, CMD, CMD, CMD, CMD, CMD),
                             spliter=' ',
                             func=app_create.create)


    cmd_create_app.option("--docker [docker]", MSG['create_app']['option']['docker'])
    cmd_create_app.option("--file [file]", MSG['create_app']['option']['file'])
    cmd_create_app.option("-i, --image [image]", MSG['create_app']['option']['image'])
    cmd_create_app.option("-e, --env [kv_pairs]", MSG['create_app']['option']['env'],
                          resolve=app_create.trans_env)

    cmd_create_app.option("-r, --resource_type [resource_type]", MSG['create_app']['option']['resource_type'])
    cmd_create_app.option("-t, --type [instance_type]", MSG['create_app']['option']['type'])
    cmd_create_app.option("-n, --nodes [instance_count]", MSG['create_app']['option']['nodes'])
    cmd_create_app.option("--min_disk_size [min_disk_size]", MSG['create_app']['option']['min_disk_size'])
    cmd_create_app.option("-d, --disk_type [disk_type]", MSG['create_app']['option']['disk_type'])
    cmd_create_app.option("--max_retry_count [max_retry_count]", MSG['create_app']['option']['max_retry_count'])
    cmd_create_app.option("--timeout [timeout]", MSG['create_app']['option']['timeout'])

    cmd_create_app.option("--inputs [input_params]", MSG['create_app']['option']['inputs'],
                          resolve=app_create.trans_inputs_params)
    cmd_create_app.option("--outputs [output_params]", MSG['create_app']['option']['outputs'],
                          resolve=app_create.trans_outputs_params)

    cmd_create_app.option("--daemonize", MSG['create_app']['option']['daemonize'])
    cmd_create_app.option("--description [description]", MSG['create_app']['option']['description'])

    cmd_create_app.option("--show_json",
                          MSG['create_app']['option']['show_json'])
    return cmd_create_app


def apps():
    cmd_apps = Command('app', alias=['a'],
                       arguments=['appName', 'revision'],
                       description=MSG['app']['description'],
                       usage='''Usage: %s app|a [appName|No.] [revision] [option]

        Examples:

            list apps:
              1. %s a

            get app info:
              1. %s a <appName> # example: %s a app_2
              2. %s a 1 # with No.

            get app revision detail:
              1. %s a <appName> <revision> # example: %s a app_2 0
            ''' % (COMMAND, CMD, CMD, CMD, CMD, CMD, CMD),
                       func=app.all)
    # cmd_apps.option('-p, --public', MSG['app']['option']['public'])


    cmd_apps.option('-d, --description', MSG['app']['option']['description'])
    return cmd_apps
