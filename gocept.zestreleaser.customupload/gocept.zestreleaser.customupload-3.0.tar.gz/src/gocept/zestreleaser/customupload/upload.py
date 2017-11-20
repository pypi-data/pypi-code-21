from six.moves import configparser, urllib
import glob
import os
import os.path
import zest.releaser.utils


def split_destination(destination):
    """Returns list of options and destination."""
    parts = destination.split()
    options = parts[:-1]
    destination = parts[-1]
    if '://' not in destination:
        destination = 'scp://' + destination.replace(':', '/', 1)
    return options, destination


def upload(context):
    destination = choose_destination(
        context['name'], read_configuration('~/.pypirc'),
        'gocept.zestreleaser.customupload')
    if not destination:
        return
    url = urllib.parse.urlsplit(split_destination(destination)[1])
    if url.password:
        url = url[0:1] + (url[1].replace(url.password, '<passwd>'),) + url[2:]
    target_url = urllib.parse.urlunsplit(url)
    if not zest.releaser.utils.ask('Upload to %s' % target_url):
        return
    sources = glob.glob(os.path.join(context['tagdir'], 'dist', '*'))
    for call in get_calls(sources, destination):
        os.system(' '.join(call))


def get_calls(sources, destination):
    result = []
    options, destination = split_destination(destination)
    url = urllib.parse.urlsplit(destination)
    if url[0] in ('scp', ''):
        netloc, path = url[1], url[2]
        assert path.startswith('/')
        port = '22'
        if netloc.find(':') != -1:
            netloc, port = netloc.split(':')
        path = path[1:]
        result.append(['scp'] + ['-P %s' % port] + sources +
                      ['%s:%s' % (netloc, path)])
    if url[0] in ('http', 'https'):
        if destination.endswith('/'):
            destination = destination[:-1]
        default_params = ['curl']
        default_params.extend(options)
        default_params.extend(['-X', 'PUT', '--data-binary'])
        default_params = tuple(default_params)
        for source in sources:
            source_name = os.path.basename(source)
            result.append(
                list(default_params +
                     ('@' + source, '%s/%s' % (destination, source_name))))
    if url[0] in ('sftp', ):
        netloc, path = url[1], url[2]
        assert path.startswith('/')
        port = '22'
        if netloc.find(':') != -1:
            netloc, port = netloc.split(':')

        for source in sources:
            result.append(
                ['echo', '"put %s"' % source, '|', 'sftp',
                    '-P %s' % port, '-b', '-', "%s:%s" % (netloc, path)])
    return result


def read_configuration(filename):
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(filename))
    return config


def choose_destination(package, config, section):
    if section not in config.sections():
        return None
    items = sorted(config.items(section), key=lambda x: len(x[0]),
                   reverse=True)
    package = package.lower()
    for prefix, destination in items:
        if package.startswith(prefix.lower()):
            return destination
    return None
