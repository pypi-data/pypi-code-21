import hashlib
import hmac
import click
import configparser
import sys
import json
import os

def set_config():
    """
    Return the name of the configuration file from the Enviromental variable or default name

    :return: Name of config file (String)
    """
    if "LABELORD_CONFIG" in os.environ:
        return os.environ['LABELORD_CONFIG']
    else:
        return 'config.cfg'

#retur the list of target repos from config file set to 1/yes/on
def get_config_repos(config):
    """
    Parse the config file and returns the set of target repositories

    :param config: name of the configuration file
    :return: set of target repositories (Array<String>)
    """
    repos = []
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(config)

    if (parser.has_section('repos')):
        for (each_repo, each_flag) in parser.items('repos'):
            if(parser.getboolean('repos', each_repo)):
                repos.append(each_repo)
        return repos
    else:
        click.echo('No repositories specification has been found', err=True)
        sys.exit(7)


def get_tkn(config):
    """
    Parse the configuration file and returns the token if exits else exits with 3

    :param config: name of the config file
    :return: token from config file (String)
    """
    parser = None
    parser = configparser.ConfigParser()
    parser.read(config)
    config = set_config()

    if(parser.has_option('github','token')):
        return parser['github']['token']
    else:
        click.echo('No GitHub token has been provided', err=True)
        sys.exit(3)

#return secret from the config file
def get_secret(config):
    """
    Parse the config file and returns the webhook secret if exists else exits with 8

    :param config: name of the configuration file
    :return: webhook secret (String)
    """
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(config)
    if (parser.has_section('github') and parser.has_option('github','webhook_secret')):
        return parser['github']['webhook_secret']
    else:
        click.echo('No webhook secret has been provided', err=True)
        sys.exit(8)


#create label in other repos
def create_label(name, color, repos, session, origin):
    """
    Creates label

    :param name: name of the label
    :param color: color of the label
    :param repos: repository where label is created
    :param session: session for communication
    :param origin: repository where the label came from
    :return: message code 200 (int)
    """
    for repo in repos:
        if(repo != origin):
            data = {"name": name, "color": color}
            json_data = json.dumps(data)
            r = session.post("https://api.github.com/repos/"+repo+"/labels", json_data)
    return "200"

#edit label in other repos
def edit_label(old_name, new_name, new_color, repos, session, origin):
    """
    Edits label

    :param old_name: old name of the label
    :param new_name: new name of the label
    :param new_color: new color of the label
    :param repos: repository in which is label edited
    :param session: session for communication
    :param origin: repository where the label came from
    :return: message code 200 (int)
    """
    for repo in repos:
        if(repo != origin):
            data = {"name": new_name, "color": new_color}
            json_data = json.dumps(data)
            if(old_name == None):
                r = session.patch("https://api.github.com/repos/" + repo + "/labels/" + new_name,json_data)
            else:
                r = session.patch("https://api.github.com/repos/" + repo + "/labels/" + old_name, json_data)
    return "200"

#delete label in other repos
def delete_label(name,repos, session, origin):
    """
    Deletes label

    :param name: name of the label to delete
    :param repos: name of the repository where is the label
    :param session: session for communication
    :param origin: from where the label came from
    :return: message code 200 (int)
    """
    for repo in repos:
        if(repo != origin):
            r = session.delete("https://api.github.com/repos/"+repo+"/labels/" + name)
    return "200"

#return True if the computed and received signatures are the same
def check_signature(secret, request):
    """
    Check if the signature in response and computed signature from webhook secret are the same

    :param secret: webhook secret
    :param request: incomming request
    :return: True if the signatures are the same, else False (bool)
    """
    sig = 'sha1=' + hmac.new(secret.encode('utf-8'), request.data, hashlib.sha1).hexdigest()
    #compare computed and received signature
    if sig == get_signature(request):
        return True
    else:
        return False

#return x-github-signaure from request
def get_signature(request):
    """
    Returns X-Hub-Signature from request header

    :param request: incomming request
    :return: X-Hub-Signature if exists (String)
    """
    if('X-Hub-Signature' in request.headers):
        return request.headers['X-Hub-Signature']
    else:
        return ""

def get_old_name(request):
    """
    Returns the old name of the label when edited

    :param request: incomming request
    :return: old name of the label (String)
    """
    if('name' in request.json['changes']):
        return request.json['changes']['name']['from']

def get_old_color(request):
    """
    Returns the old color of the label when edited

    :param request: incomming request
    :return: old color of the label (String)
    """
    if('color' in request.json['changes']):
        return request.json['changes']['color']['from']

#return action used for the label from request
def get_action(request):
    """
    Returns the actual action from request

    :param request: incomming request
    :return: action/operation with label from webhook (String)
    """
    return request.json['action']

#return label name from request
def get_lname(request):
    """
    Returns the name of the label which has been changed

    :param request: incomming request
    :return: label name from request (String)
    """
    return request.json['label']['name']

#return label color from request
def get_lcolor(request):
    """
    Returns the name of the label which has been changed

    :param request: incomming request
    :return: label color from the request (String)
    """
    return request.json['label']['color']

def get_repo_name(request):
    """
    Returns the repository name from the request

    :param request: incomming request
    :return: repository name from the webhook (String)
    """
    return request.json['repository']['full_name']

#return Github event from request
def get_event(request):
    """
    Returns the name of the event from request

    :param request: incomming request
    :return: event from webhook (String)
    """
    return request.headers['X-Github-Event']
