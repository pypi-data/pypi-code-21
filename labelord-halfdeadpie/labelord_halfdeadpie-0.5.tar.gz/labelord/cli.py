import click
import requests
import configparser
import sys
from .cli_support import *

@click.group('labelord')
@click.option('--config', '-c', default='config.cfg',
              help='Path of the auth config file.')
@click.option('--token', '-t', envvar='GITHUB_TOKEN.',
              help='GitHub API token.')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show the version and exit.')
@click.pass_context
def cli(ctx, token, config):
    session = ctx.obj.get('session', requests.Session())
    ctx.obj['session'] = session
    ctx.obj['config'] = config
    ctx.obj['token'] = token

@cli.command()
@click.pass_context
def list_repos(ctx):
    """
    Listing accesible repositories
    :param ctx:
    :return:
    """
    config = ctx.obj['config']
    realtoken = ctx.obj['token']
    if(realtoken == None):
        realtoken = get_token(ctx.obj['token'],config)
    check_token(realtoken)
    session = authorization(ctx,realtoken)


    #REQUEST
    session = ctx.obj['session']
    page = 1
    last = 0
    while True:
        r = session.get('https://api.github.com/user/repos?per_page=100&page='+str(page) )
        #1. data received
        if(r.status_code == 200):
            for i in r.json():
                owner = i['owner']['login']
                repo = i['name']
                click.echo('{}/{}' .format(owner,repo))
        #2. data not received - bad code
        elif(r.status_code == 404):
            eprint(get_message(r))
            sys.exit(5)
        elif(r.status_code == 401):
            eprint(get_message(r))
            sys.exit(4)
        else:
            sys.exit(10)
        if( page == 1 ):
            if(not r.links):
                break;
            last = get_last_page(r)
        elif( page == last):
            break;
        page += 1

@cli.command()
@click.pass_context
@click.argument('repository')
def list_labels(ctx, repository):
    """Listing labels of desired repository."""
    session = ctx.obj['session']
    last = 0
    page = 1

    config = ctx.obj['config']
    realtoken = ctx.obj['token']
    if(realtoken == None):
        realtoken = get_token(ctx.obj['token'],config)
    check_token(realtoken)
    session = authorization(ctx,realtoken)

    while True:
    #REQUEST
        r = session.get('https://api.github.com/repos/' +repository+ '/labels?per_page=100&page=' + str(page) )
        #1. all possible labels received
        if(r.status_code == 200):
            for i in r.json():
                color = i['color']
                name = i['name']
                click.echo('#{} {}' .format(color,name))
        #2. data not received - bad code
        elif(r.status_code == 401):
            eprint(get_message(r))
            sys.exit(4)
        elif(r.status_code == 404):
            eprint(get_message(r))
            sys.exit(5)
        else:
            sys.exit(10)

        if( page == 1 ):
            if(not r.links):
                break;
            last = get_last_page(r)
        elif( page == last):
            break;
        page += 1

@cli.command()
@click.pass_context
@click.argument('mode', type=click.Choice(['update', 'replace']))
@click.option('--template-repo', '-r', default=None,
            help='The name of the template repo for labels.')
@click.option('--verbose','-v', is_flag=True)
@click.option('--dry-run','-d', is_flag=True)
@click.option('--quiet','-q', is_flag=True)
@click.option('--all-repos', '-a', is_flag=True)
def run(ctx,mode, template_repo, verbose, dry_run, quiet, all_repos):
    """Run labels processing."""
    config = ctx.obj['config']
    real_template_repo = None
    session = ctx.obj['session']
    config = ctx.obj['config']
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(config)
    template = []
    targets = []
    message = ""
    updated = []
    errors = []
    ctx.obj['updated'] = updated
    ctx.obj['errors'] = errors

    realtoken = ctx.obj['token']
    if(realtoken == None):
        realtoken = get_token(ctx.obj['token'],config)
    check_token(realtoken)
    session = authorization(ctx,realtoken)


    #repo from the command line
    if(template_repo != None):
        real_template_repo = template_repo
    #repo from the config file
    elif(parser.has_section('others') and parser.has_option('others','template-repo')):
        real_template_repo = parser['others']['template-repo']

    #template repo from the config file
    last = 0
    page = 1

    if(real_template_repo != None):
        while True:
            r = session.get('https://api.github.com/repos/' + str(real_template_repo) + "/labels?per_page=100&page=" + str(page))
            if(r.status_code == 200):
                for i in r.json():
                    color = i['color']
                    name = i['name']
                    lb = Label(name,color)
                    template.append(lb)
            elif(r.status_code == 401):
                if(quiet == False):
                    click.echo(get_message(r), err=True)
                sys.exit(4)
            else:
                message = "[LBL][ERR] " + real_template_repo + "; " + get_message(r)
                add_error(ctx, "LBL", real_template_repo, None, get_message(r))

            if( page == 1 ):
                if(not r.links):
                    break;
                last = get_last_page(r)
            elif( page == last):
                break;
            page += 1

    #labels from config file
    else:
        if(parser.has_section('labels')):
            for (each_key, each_val) in parser.items('labels'):
                lb = Label(each_key, each_val)
                template.append(lb)
        else:
                #if(quiet == False):
            click.echo("No labels specification has been found", err=True)
            sys.exit(6)

    if(message != "" and verbose and quiet == False):
        click.echo("{}" .format(message))

    last = 0
    page = 1


    if(all_repos):
        while True:
            r = session.get('https://api.github.com/user/repos?per_page=100&page=' + str(page))
            #1. data received
            if(r.status_code == 200):
                for i in r.json():
                    owner = i['owner']['login']
                    name = i['name']
                    repo = owner +"/"+ name
                    targets.append(repo)
            #2. data not received - bad code
            elif(r.status_code == 401):
                if(quiet == False):
                     click.echo(get_message(r), err=True)
                sys.exit(4)
            else:
                sys.exit(10)

            if( page == 1 ):
                if(not r.links):
                    break;
                last = get_last_page(r)
            elif( page == last):
                break;
            page += 1


    else:
        if(parser.has_section('repos')):
            for (each_repo, each_flag) in parser.items('repos'):
                if(parser.getboolean('repos',each_repo)):
                        targets.append(each_repo)
        else:
            click.echo("No repositories specification has been found", err=True)
            sys.exit(7)



    #Target repos in targets
    for repo in targets:
        if( mode == "replace" ):
                actualize(ctx, repo, template, verbose, dry_run, quiet, True)
        else:
                actualize(ctx, repo, template, verbose, dry_run, quiet, False)

    #Printing
    if( (verbose and quiet) or (verbose==False and quiet==False) ):
        if(len(errors) > 0):
            for error in errors:
                errmsg = error.o +"; "+ error.r + "; "
                if(error.l != None):
                    errorlabel = error.l
                    errmsg += errorlabel.n + "; " +errorlabel.c + "; "
                errmsg += error.m
                click.echo('ERROR: {}' .format(errmsg), err=True)
            click.echo('SUMMARY: {} error(s) in total, please check log above' .format(len(errors)), err=True)
            sys.exit(10)
        else:
            click.echo('SUMMARY: {} repo(s) updated successfully' .format(len(updated)))
            sys.exit(0)

    #print verbose summary
    if(verbose or dry_run):
        if(len(errors) > 0):
            click.echo("[SUMMARY] {} error(s) in total, please check log above" .format(len(errors)))
            sys.exit(10)
        else:
            click.echo('[SUMMARY] {} repo(s) updated successfully' .format(len(updated)))
            sys.exit(0)

    if(len(errors) > 0 and quiet==False):
        click.echo("[SUMMARY] {} error(s) in total, please check log above" .format(len(errors)))
        sys.exit(10)

    if(len(errors) > 0):
        sys.exit(10)