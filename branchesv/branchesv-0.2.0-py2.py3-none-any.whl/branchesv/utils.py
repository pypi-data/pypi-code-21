import os
import shutil
import simplejson as json
import logging
import re

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-5s - %(name)s.%(module)s.%(funcName)s - %(message)s'
)
_logger = logging.getLogger('Branchesv')


def save_json(info, filename):
    """ Save info into Json file.
        :param info: Object to be saved
        :param filename: Name of Json file
        :return: Absolute path of Json file
    """
    if not os.path.isabs(filename):
        filename = os.path.abspath(filename)
    try:
        with open(filename, 'w') as fout:
            json.dump(info, fout, sort_keys=True, indent=4, ensure_ascii=False,
                      separators=(',', ':'))
    except IOError as error:
        _logger.error(error)
        raise
    return filename


def load_json(filename):
    """ Load info from Json file
        :param filename: Name of Json file
        :return: Object loaded if successful, None otherwise
    """
    try:
        with open(filename, "r") as dest:
            info = json.load(dest)
    except IOError as error:
        _logger.error(error)
        raise
    return info


def clean_files(files):
    """ Remove unnecessary and temporary files
       :param files: A list of absolute or relative paths thar will be erased
    """
    items = files if hasattr(files, '__iter__') else [files]
    for item in items:
        if item != "/":
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
        else:
            _logger.error("Invalid target path: '/'")


def simplify_path(branches_info):
    """ This function deletes all common directories in branches' path
        :param branches_info: List of dictionaries with branches' info
        :return: List of dictionaries with branches' info
    """
    if len(branches_info) > 1:
        repeated = True
        while repeated:
            piece_path = []
            for branch in branches_info:
                piece_path.append(branch['path'].split('/', 1)[0])
            word = piece_path[0]
            repeated = True
            for each in piece_path:
                if each != word:
                    repeated = False
            if repeated:
                for branch in branches_info:
                    branch.update({'path': branch['path'].split('/', 1)[1]})
    elif branches_info:
        branch = branches_info[0]
        branch.update({'path': os.path.basename(branch['path'])})
    return branches_info


def name_from_url(url):
    """ Takes name of a GIT repo from origin url
        :param url: Url of private GIT repo
        :returns: Repo's name
    """
    name = url.split('/')[-1].split('.')[0]
    return name


def copy_list_dicts(lines):
    res = []
    for line in lines:
        dict_t = {}
        for keys in line.keys():
            dict_t.update({keys: line[keys]})
        res.append(dict_t.copy())
    return res


def set_message(branch, str_msg=None):
    """ Sets the exit message for GitBranch actions like clone, pull
    and update
        :param branch: The repo that's being used
        :param str_msg: Posible string message received from an action
        :return: Message dictionary containing:
            - name: Name of the repo
            - msg: Message to be returned
            - exit_code: Code or return
    """
    url = branch['repo_url'].get('origin', list(branch['repo_url'].values())[0])
    fatal_error = None
    if str_msg:
        fatal_regexp = re.compile(r'fatal: (.*)')
        fatal_error = fatal_regexp.search(str_msg)
    if not fatal_error:
        res = {"name": branch['name'],
               "exit_code": 0,
               "msg": "Successful action"}
    else:
        res = {
               "name": branch['name'],
               "exit_code": 1,
               "msg": "{error} while cloning {repo} from {url}".format(error=fatal_error.group(0),
                                                                       repo=branch['name'],
                                                                       url=url)}
    return res
