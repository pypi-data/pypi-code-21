import subprocess
import logging


def run_command(arguemnts):
    logging.debug('Execute: %s', ' '.join(arguemnts))
    return subprocess.check_output(arguemnts).strip().decode('utf-8')


# noinspection PyBroadException
def git_version():
    try:
        return run_command(['git', 'version'])
    except Exception as ex:
        logging.debug('Failed to get git version.Error: {}'.format(ex))
        return None


def git_remote_url():
    return run_command(['git', 'remote', 'get-url', 'origin'])


def git_repo_template():
    remote_url = git_remote_url()
    repo_url = (remote_url.split('@')[1].strip()).replace(':', '/')[:-4]
    return 'https://' + repo_url


# noinspection PyBroadException
def git_status():
    try:
        return run_command(['git', 'status'])
    except Exception as ex:
        logging.debug('Failed to get git status.Error: {}'.format(ex))
        return None


def git_branch_name():
    return run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])


def git_local_tip():
    return run_command(['git', 'rev-parse', git_branch_name()])


# def git_remote_tip():
#     return run_command(['git', 'rev-parse', 'origin/{}'.format(git_branch_name())])
#

def git_local_tip_url():
    return '{}/commit/{}'.format(git_repo_template(), git_local_tip())


def git_is_clean():
    return run_command(['git', 'status', '--porcelain']).strip() == ''


def git_get_commit_by_sha(sha):
    import json
    x = run_command(['git', 'log', '--pretty=format:{ "date": %at,  "refs": "%d", "parents":"%P"}', '-1', sha])
    y = json.loads(x.replace('\n', '\\n'))
    y['message'] = git_get_format_for_sha(sha, "%B")
    y['author'] = git_get_format_for_sha(sha, "%aN <%aE>")

    return y


def git_get_format_for_sha(sha, frm):
    return run_command(['git', 'log', "--pretty=format:{}".format(frm), '-1', sha])

# def git_remote_tip_url():
#     return '{}/commit/{}'.format(git_repo_template(), git_remote_tip())

# def git_patch_from_remote():
#     return run_command(['git', 'format-patch', 'origin/HEAD', '--stdout'])

#
# def git_diff_staged():
#     return run_command(['git', 'diff', '--staged'])

#
# def git_diff_modified():
#     return run_command(['git', 'diff'])


# def git_get_text_diff(file_name):
#     try:
#         return run_command(['git', '--no-pager', 'diff', '/dev/null', file_name])
#     except subprocess.CalledProcessError as ex:
#         output = ex.__getattribute__('output')
#         if output is not None:
#             if output.endswith(' differ\n'):  # todo: regex this
#                 logging.warn('%s is binary file. Only text files are supported', file_name)
#             return output


# def git_diff_new():
#     new_files = run_command(['git', 'ls-files', '--others', '--exclude-standard']).strip().split('\n')
#     res = ''
#     for file in new_files:
#         file = file.strip()
#         res += git_get_text_diff(file) + '\n'
#     return res
#
# from pprint import pprint
#
# pprint(git_get_commit_by_sha(git_local_tip()))
