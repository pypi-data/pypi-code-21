# -*- coding:utf-8 -*-

from ..util import client, formater, list2table, result_cache
from terminal import bold, magenta, white, blue, green,red, yellow
from ..const import CMD
import json
PROGRESS_LEN = 70

def all(appName=None, description=False, revision=None):

    if appName:
        if revision:
           getRevision(appName, revision, description)
        else:
            get(appName, description)
    else:
        list()


def list():

    result = client.list_apps()

    arr = formater.items2arr(result.get('Items'))

    result_len = len(arr)

    arr = formater.format_date_in_arr(arr, ['CreationTime'])

    result_cache.save(arr, 'Name', 'apps')

    print('%s' % bold(magenta('Apps:')))
    list2table.print_table(arr, ['Name', ('Description','Description', formater.sub_desc), 'Scope', 'CreationTime',('CreationTimeFromNow','FromNow')])

    arrlen = len(arr)

    cache_str = white('(cache %s %s)' % (arrlen, 'rows' if arrlen > 1 else 'row'))
    print('%s %s' % (green('Total: %s' % result_len), cache_str))

    print(white('\n  type "%s a <Name|No.>" to show app detail' % (CMD)))
    print('')


def get(appName, descOnly=False):

    appName = result_cache.get(appName, 'apps')

    scope = 'Private'
    if appName.startswith(':'):
        appName  = appName[1:]
        scope = 'Public'

    print(white('exec: bcs a %s%s' % (appName, '(public)' if scope == 'Public' else '')))

    info = client.get_app(appName, scope)

    result = info.detail()
    result['Scope'] = scope

    if descOnly:
        print(info.dump(indent=4))
        return

    arr = [{
        'a': '%s: %s' % (blue('Name'), result.get('Name')),
        'b': '%s: %s' % (blue('Scope'), result.get('Scope')),
        'c': '%s: %s' % (blue('Created'), formater.from_now(result.get('CreationTime')))
    }]
    print('%s' % bold(magenta('App:')))
    list2table.print_table(arr, ['a','b','c'], show_no=False, show_header=False)


    # InputParameters
    t = []
    for (k, n) in result['InputParameters'].items():
        n = n.detail()
        n['Name'] = k
        t.append(n)
    print('%s' % bold(magenta('InputParameters:')))
    list2table.print_table(t, ['Name','Default','Type', 'LocalPath', 'Description'], show_no=False)

    # OutputParameters
    t = []
    for (k, n) in result['OutputParameters'].items():
        n = n.detail()
        n['Name'] = k
        t.append(n)
    print('%s' % bold(magenta('OutputParameters:')))
    list2table.print_table(t, ['Name','Default', 'Type', 'LocalPath', 'Description'], show_no=False)

    # config
    t = []
    for (k, n) in result['Config'].items():
        n = n.detail()
        n['Name'] = k
        t.append(n)
    print('%s' % bold(magenta('Config:')))
    list2table.print_table(t, ['Name', 'Default', 'Overwritable', 'Description'], show_no=False)


    #print(result)
    if scope=='Private':
        print('%s' % bold(magenta('Revisions:')))
        revisionsResult = client.get_app_revisions(appName)

        arr = formater.format_date_in_arr(revisionsResult.Items, ['UpdateTime'])
        list2table.print_table(arr, ['Revision', 'UpdateTime'], show_no=False)

        print(white('\n  type "%s a <Name|No.> <Revision>" to show revision detail' % (CMD)))
        print('')

def getRevision(appName, revision, descOnly=False):

    appName = result_cache.get(appName, 'apps')

    print(white('exec: bcs a %s %s %s' % (appName, revision, '-d' if descOnly else '')))

    detail = client.get_app_detail(appName, revision)


    if descOnly:
        print(detail.dump(indent=4))
        return

    print('%s: %s' % (blue('Name'), detail.Name))

    print('%s: %s' % (blue('Description'), detail.Description))
    print('%s: %s' % (blue('CommandLine'), detail.CommandLine))
    print('%s: %s' % (blue('Daemonize'), detail.Daemonize))

    if detail.get('VM'):
        print('%s' % (blue('VM')))
        print('  %s: %s' % (blue('ECSImageId'), detail.VM.ECSImageId))

    if detail.get('Docker'):
        print('%s' % blue('Docker'))
        print('  %s: %s' % (blue('Image'), detail.Docker.Image))
        print('  %s: %s' % (blue('RegistryOSSPath'), detail.Docker.RegistryOSSPath))

    # env vars
    if detail.get('EnvVars'):
        print(blue('EnvVars'))
        for k,v in detail.EnvVars.items():
            print('  %s: %s' % (k,v))




    # InputParameters
    t = []
    for (k, n) in detail.InputParameters.items():
        n = n.detail()
        n['Name'] = k
        t.append(n)
    print('%s' % bold(magenta('InputParameters:')))
    list2table.print_table(t, ['Name', 'Default', 'Type', 'LocalPath', 'Description'], show_no=False)

    # OutputParameters
    t = []
    for (k, n) in detail.OutputParameters.items():
        n = n.detail()
        n['Name'] = k
        t.append(n)
    print('%s' % bold(magenta('OutputParameters:')))
    list2table.print_table(t, ['Name', 'Default', 'Type', 'LocalPath', 'Description'], show_no=False)


    # config
    t = []
    for (k, n) in detail.Config.items():
        n = n.detail()
        n['Name'] = k
        t.append(n)
    print('%s' % bold(magenta('Config:')))
    list2table.print_table(t, ['Name', 'Default', 'Overwritable', 'Description'], show_no=False)

