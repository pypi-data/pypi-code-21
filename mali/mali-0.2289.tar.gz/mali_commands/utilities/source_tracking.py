import logging

from six.moves.urllib import parse


class GitError(Exception):
    pass


class GitExpando(object):
    pass


def ssh_to_https(url):
    if '@' in url:
        return 'https://' + (url.split('@')[1].strip()).replace(':', '/')
    return url


def enforce_https(url):
    if url.startswith('http://'):
        return 'https://' + url[len('http://'):]
    return url


def remove_dot_git(url):
    return url if not url.lower().endswith('.git') else url[:-4]


def __remote_to_template(remote_url):
    return remove_dot_git(enforce_https(ssh_to_https(remote_url.lower())))


def import_git():
    try:
        import git
        return git
    except ImportError:
        logging.warning('Failed to import git')
    raise GitError('Failed to import git')


def get_remote_url():
    try:
        repo = import_git().Repo('.', search_parent_directories=True)
        if len(repo.remotes) > 0:
            remote = list(repo.remotes)[0]
            return __remote_to_template(remote.url)
    except GitError as gr:
        logging.error("Failed to get remote git repository of current folder. {}".format(str(gr)))
    return None


def remote_url_obj(url):
    if url is None:
        return None
    obj = parse.urlparse(__remote_to_template(url))
    if obj.hostname is None or object.hostname == '':
        return None
    return obj


def get_org_from_remote_url(url):
    url_obj = parse.urlparse(__remote_to_template(url))
    if url_obj is None:
        return None
    return url_obj.path.split('/')[:-1].lower()


def validate_remote_urls_org(src, trg):
    src_org = get_remote_url(src)
    remote_org = get_remote_url(trg)

    return src_org == remote_org
