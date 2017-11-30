import click
import configparser
import sys
import json

class Label:
    """
    Represents label

    has *name* - label name

    has *color* - label color in RGB
    """
    def __init__(self, name, color):
        self.n = name
        self.c = color

class Error:
    """
    Represents error with its information

    has *operation* - operation with label

    has *repo* - name of repository

    has *label* - name of the label

    has *message* - error message
    """
    def __init__(self, operation, repo, label, message):
        self.o = operation
        self.r = repo
        self.l = label
        self.m = message

def eprint(err):
    """
    Prints error

    :param err: Error message
    """
    click.echo("GitHub: ERROR {}" .format(err), err=True)

#TOKEN SETTING
def get_token(token,config):
    """
    Return token provided by CLI or from

    :param token: token from CLI
    :param config: config file name from CLI
    :return: token (String)
    """
    if(token != None):
        return token
    else:
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(config)
        #problem
        if(parser.has_section('github')):
            return parser['github']['token']
        else:
            return None

#TOKEN CHECK
def check_token(token):
    """
    Exit with 3 if there is no token

    :param token: GitHub token (String)
    """
    if(token == None):
        click.echo('No GitHub token has been provided', err=True)
        sys.exit(3)

#AUTHORIZATION
def authorization(ctx,token):
    """
    Fill authorisation and User-Agent headers and return the session

    :param ctx: context for passing the objects
    :param token: GitHub token
    :return: session with filled headers (requests.session)
    """
    session = ctx.obj['session']
    session.headers = {'User-Agent': 'Python'}
    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req
    session.auth = token_auth
    return ctx.obj['session']

#UPDATED REPOS COUNTING
def add_updated(ctx, repo):
    """
    Add name of repository to list of updated

    :param ctx: context for passing the objects
    :param repo: Name of the repository
    """
    updated = ctx.obj['updated']
    if(updated.count(repo) == 0):
        updated.append(repo)

#ERROR COUNTER
def add_error(ctx, operation, repo, label, message):
    """
    Add error to list of errors

    :param ctx: context for passing the objects
    :param operation: operation with the actual label
    :param repo: name of the repository
    :param label: name of the actual label
    :param message: error message
    """
    errors = ctx.obj['errors']
    err = Error(operation, repo, label, message)
    errors.append(err)

#GET ERROR MESSAGE FROM JSON
def get_message(r):
    """
    Returns status code and message

    :param r: Reponse from request
    :return: Status code and message (String)
    """
    text = r.json()['message']
    message= str(r.status_code) + " - " + text
    return message

#LABEL COMPARE
def cmp_labels(a,b):
    """
    Compare two labels

    :param a: first label
    :param b: second label
    :return: (bool)
    """
    if(a.n== b.n and a.c == b.c):
        return True
    else:
        return False

def is_named(template, label):
    """
    Check if the name of the label is in template

    :param template: template of labels
    :param label: label to check
    :return: True if label's name is in template (bool)
    """
    for temp in template:
        if(temp.n == label.n):
            return True
    return False

def same_lower_name(a, b):
    """
    Check if two labels have same names

    :param a: first label
    :param b: second label
    :return: True if the labels have same names (bool)
    """
    if(a.n.lower() == b.n.lower() ):
        return True
    else:
        return False

def is_included(template, label):
    """
    Check if the template includes the label.

    :param template: template of labels
    :param label: label to check
    :return: True if
    """
    for temp in template:
        if(cmp_labels(temp,label)):
            return True
        elif(temp.n == label.n):
            temp.c = label.c
    return False

def is_named_diff(template, label):
    """
    Check if template includes label with different case

    :param template: template of labels
    :param label: label to check
    :return: True if template includes samed named label with different case (bool)
    """
    for temp in template:
        if(different_case(temp, label)):
            return True
    return False

def different_case(a,b):
    """
    Check if same named labels has different case names

    :param a: first label
    :param b: second label
    :return: True if labels are named samed but different case (bool)
    """
    if(a.n != b.n and a.n.lower() == b.n.lower()):
        return True
    else:
        return False

#ACTUALIZE
def actualize(ctx, repo, template, verbose, dry_run, quiet, replace):
        """
        Actualise the repository according to template

        :param ctx: context for passing the objects
        :param repo: name of the repository
        :param template: template of labels
        :param verbose: run with printing operations
        :param dry_run: run with no real changes
        :param quiet: run without any printing
        :param replace: replace the complete template or not
        """
        session = ctx.obj['session']
        last = 0
        page = 1
        target_labels = []
        message = ""
        while True:
        #REQUEST
            r = session.get('https://api.github.com/repos/' +repo+ '/labels?per_page=100&page=' + str(page) )
            #1. all possible labels received
            if(len(template) == 0):
                add_updated(ctx, repo)
            if(r.status_code == 200):
                for i in r.json():
                    color = i['color']
                    name = i['name']
                    lb = Label(name, color)
                    target_labels.append(lb)
            elif(r.status_code == 404):
                message = "[LBL][ERR] " + repo + "; " + get_message(r)
                if(quiet==False and verbose):
                    click.echo('{}' .format(message))
                add_error(ctx, "LBL", repo, None, get_message(r))
                return
            else:
                message = "[LBL][ERR] " + repo + "; " + get_message(r)
                add_error(ctx, "LBL", repo, None, get_message(r))
            if( page == 1 ):
                if(not r.links):
                    break;
                last = get_last_page(r)
            elif( page == last):
                break;
            page += 1

        for template_label in template:
            #PATCH
            if ( (not is_included(target_labels, template_label) and is_named(target_labels, template_label)) or
                 is_named_diff(target_labels,template_label)):
                #label found
                data = {"name": template_label.n, "color": template_label.c}
                json_data = json.dumps(data)
                if(dry_run == False):
                    p = session.patch("https://api.github.com/repos/"+repo+"/labels/"+template_label.n.lower(), json_data)
                message = '[UPD]'
                if(dry_run):
                    message += '[DRY] '
                    add_updated(ctx, repo)
                else:
                    if(p.status_code == 200):
                        message += '[SUC] '
                        add_updated(ctx, repo)
                    else:
                        message += '[ERR] '
                        add_error(ctx, "UPD", repo, template_label, get_message(p))
                message += repo +'; '+ template_label.n +'; '+ template_label.c
                if(dry_run == False and p.status_code != 200):
                        message += '; '+ get_message(p)
                    #final message
                if(verbose and message!="" and not quiet):
                    click.echo('{}' .format(message))


            #POST
            elif(not is_named(target_labels, template_label)):
                data = {"name": template_label.n, "color": template_label.c}
                json_data = json.dumps(data)

                message = '[ADD]'
                if(dry_run == False):
                    p = session.post("https://api.github.com/repos/"+repo+"/labels", json_data)
                if(dry_run):
                    message += '[DRY] '
                    add_updated(ctx, repo)
                else:
                    if(p.status_code == 201):
                        message += '[SUC] '
                        add_updated(ctx, repo)
                    else:
                        message += '[ERR] '
                        add_error(ctx, "ADD", repo, template_label, get_message(p))
                message += repo +'; '+ template_label.n +'; '+ template_label.c
                if(dry_run == False and p.status_code != 201):
                    message += '; '+ get_message(p)

                #final message
                if(verbose and message!="" and not quiet):
                    click.echo('{}' .format(message))


        if(replace):
            for target in target_labels:
                if(not is_included(template, target)):
                    if(dry_run == False):
                        r = session.delete("https://api.github.com/repos/" +repo+ "/labels/"+ target.n)
                    message = '[DEL]'
                    if(dry_run):
                        message += '[DRY] '
                        add_updated(ctx, repo)
                    else:
                        if(r.status_code == 204):
                            message += '[SUC] '
                            add_updated(ctx, repo)
                        else:
                            message += '[ERR] '
                            add_error(ctx, "[DEL]", repo, target, get_message(r))
                    message += repo +'; '+ target.n +'; '+ target.c
                    if(dry_run == False and r.status_code != 204):
                        message += '; '+ get_message(r)
                    if(verbose and message!="" and not quiet):
                        click.echo('{}' .format(message))

def print_version(ctx, param, value):
    """
    Print version of the application and exit

    :param ctx: context for passing the objects
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo('labelord, version 0.5')
    ctx.exit()

def get_last_page(response):
    """
    Returns the last page of response

    :param response: response from requests
    :return: last page of response (String)
    """
    result = response.links['last']['url']
    final = result.split("&page=")
    result = int(final[1])
    return result