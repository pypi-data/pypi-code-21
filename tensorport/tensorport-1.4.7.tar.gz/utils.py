import random
import string
import click
from terminaltables import SingleTable, AsciiTable, GithubFlavoredMarkdownTable
import re

MIN_NUM = 100
MAX_NUM = 999
adjs = [
    "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
    "summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter",
    "patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue",
    "billowing", "broken", "cold", "damp", "falling", "frosty", "green", "long",
    "late", "lingering", "bold", "little", "morning", "muddy", "old", "red",
    "rough", "still", "small", "sparkling", "throbbing", "shy", "wandering",
    "withered", "wild", "black", "young", "holy", "solitary", "fragrant",
    "aged", "snowy", "proud", "floral", "restless", "divine", "polished",
    "ancient", "purple", "lively", "nameless"
]
nouns = [
    "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
    "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
    "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
    "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
    "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
    "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
    "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
    "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper", "frog",
    "smoke", "star"
]


def random_name_generator():
    return random.choice(adjs) + '-' + random.choice(nouns) + '-' + str(
        random.randint(MIN_NUM, MAX_NUM))


def random_string():
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(12))


def normalize(lines, string, length):
    """ Normalize a long string into multiple lines.
    A recursive function that will append string to list of lines.
    Args:
        lines: list
        string: string that will be normalized and appended to lines
        length: max length of each line
    """
    if string == '':
        return lines

    words = string.split(' ', 1)
    if len(words) == 2:
        w1, w2 = words[0], words[1]
    elif len(words) < 2:
        w1 = words[0]
        w2 = ''

    if len(lines[-1]) + len(w1) + 1 < length:
        lines[-1] = (lines[-1] + ' ' + w1).strip()
        return normalize(lines, w2, length)
    else:
        if len(w1) < length:
            lines.append(w1)
            return normalize(lines, w2, length)
        else:
            if len(lines[-1]) == 0:
                lines[-1] = w1[:length]
            else:
                lines.append(w1[:length])
            return normalize(lines, (w1[length:] + ' ' + w2).strip(), length)


def normalize_string(string, length):
    """ Normalize a string into multiple lines.
    """
    lines = normalize([''], string, length)
    s = lines[0]
    for line in lines[1:]:
        s += '\n' + line
    return s


def select_valid_index(min_val, max_val, message):
    index = None
    message += ' [%d - %d]' % (min_val, max_val)
    while (index is None) or (not (index >= min_val and index <= max_val)):
        index = click.prompt(text=message, default=min_val, type=int)
    return index


def select_valid_integer(ints, message):
    index = None
    while (index is None) or (not index in ints):
        index = click.prompt(text=message, default=ints[0], type=int)
    return index


def describe(dictionary):
    for key, value in dictionary.items():
        click.echo("  - %s : %s" % (key, value))


def select_repo(repos, name='repository'):
    repo_names = []
    counter = 0
    valid_repos = []
    for repo in repos:
        try:
            click.echo(
                option('%s | %s/%s | Commits: %s' % (counter, repo.get(
                    'owner')['username'], repo.get('name'), len(
                    repo.get('commits', [])))))
            repo_names.append(
                [repo.get('owner')['username'],
                 repo.get('name')])
            counter += 1
            valid_repos.append(repo)
        except:
            pass

    repo_id = select_valid_index(
        0,
        len(valid_repos) - 1,
        question('Enter the id of the desired %s' % name))
    username = valid_repos[repo_id].get('owner')['username']
    repo_name = valid_repos[repo_id].get('name')
    return username, repo_name


def select_job(jobs, message=None):
    click.echo(info('Jobs:'))
    data = []
    data.append(
        ['#', 'Job Name', 'Project', 'Status', 'Launch at'])

    i = 0
    valid_jobs = []
    for job in jobs:
        try:
            data.append([
                i,
                job.get('display_name'),
                '%s/%s:%s' % (job.get('repository_owner'),
                              job.get('repository_name'),
                              job.get('git_commit_hash')[:8]),
                job.get('status'),
                '' if job.get('launched_at') is None else job.get(
                    'launched_at')[:-5]
            ])
            valid_jobs.append(job)
            i += 1
        except:
            pass
    table = render_table(data, max_length=36)
    click.echo(table.table)

    # Select the job
    job_to_pause_id = select_valid_index(
        0, len(valid_jobs) - 1,
        message)
    job_id = valid_jobs[job_to_pause_id].get('job_id')
    job_name = valid_jobs[job_to_pause_id].get('display_name')
    return job_id, job_name


def render_table(data, max_length=24):
    assert (max_length > 0)
    normalized_data = [[normalize_string(str(j), max_length) for j in i]
                       for i in data]
    return GithubFlavoredMarkdownTable(normalized_data)


def tokenize_repo(repo_name):
    try:
        assert (repo_name.count('/') == 1)
        assert (repo_name.count(':') <= 1)
        user, rem = repo_name.split('/')
        rem = rem.split(':')
        repo = rem[0]
        try:
            commit = rem[1]
        except:
            commit = None

        return user, repo, commit
    except:
        return None, None, None


def question(text):
    return " -> %s" % text


def info(text):
    return "%s\n" % text


def option(text):
    return "%s" % text


def special_match(string, search=re.compile(r'[^A-Za-z0-9\-]').search):
    return not bool(search(string))


def repo_name_validator(name, config):
    # Validate name to only have characters and -
    if name is None:
        return False, 'Name can not be None'
    if len(name) == 0:
        return False, 'Name can not be empty'
    if not special_match(name):
        return False, 'Name should only contain characters, numbers and -'
    if not special_match(name[0], search=re.compile(r'[^A-Za-z]').search):
        return False, 'Name should start with characters'
    return True, None


def job_name_validator(name, config):
    pass


def time_limit_validator(time_limit):
    time_limit = time_limit.lower()
    try:
        assert (time_limit.count('h') < 2)
        assert (time_limit.count('m') < 2)
        assert (time_limit.replace('m', '').replace('h', '').isdigit())
        if time_limit.count('h') == 0:
            time_limit = '0h' + time_limit
        if time_limit.count('m') == 0:
            time_limit = time_limit + '0m'
        if time_limit.find('h') < time_limit.find('m'):
            h, rem = time_limit.split('h', 1)
            m = rem.strip('m')
        else:
            m, rem = time_limit.split('m', 1)
            h = rem.strip('h')
        return int(h), int(m)
    except:
        return None, None
