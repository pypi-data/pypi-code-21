import json
import os
import sys
from argparse import ArgumentParser
from collections import namedtuple
from io import BytesIO
from itertools import cycle
from operator import attrgetter
from shutil import which
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, urlretrieve

from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.validation import ValidationError, Validator

github_repo = "github/gitignore"
github_api_url = "https://api.github.com/repos/github/gitignore/contents/"

FileURL = namedtuple('FileURL', ['language', 'url'])
spinner = cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])

parser = ArgumentParser()
parser.add_argument('languages', nargs='*')
parser.add_argument('--preview', '-p', action='store_true')
parser.add_argument('--out', '-o', default='.gitignore')

args = parser.parse_args()


def resolve_url(lang):
    fname = lang.title() + '.gitignore'
    return '/'.join(
        ('https://raw.githubusercontent.com', github_repo, 'master', fname)
    )


def write_file_to_stream(lang, url, index, stream, total):
    try:
        resp = urlopen(url)
    except URLError:
        sys.exit('{} url: {} not found'.format(lang, url))
    else:
        contents = resp.read()
        if contents.endswith(b'.gitignore'):
            new_url = resolve_url(contents.split(b".")[0].decode('utf-8'))
            write_file_to_stream(lang, new_url, index, stream, total)
        else:
            # Adds newline padding between each result (excluding last)
            padding = b'\n' if index != total else b''
            stream.write(contents + padding)
        resp.close()


def show_progress(count, block_size, total_size):
    sys.stdout.write(next(spinner))
    sys.stdout.flush()
    sys.stdout.write('\b')


def parse_urls_from_repo(data):
    urls = []
    for row in data:
        file_name = next(iter(row.get('name').split('.')))
        url = row.get('download_url')
        if file_name is not None and url is not None:
            urls.append(FileURL(file_name, url))
    return urls


class LanguageValidator(Validator):

    def __init__(self, completions):
        self.completions = tuple(map(str.lower, completions))

    def validate(self, document):
        choices = map(str.strip, document.text.lower().split(","))
        for choice in choices:
            if choice not in self.completions:
                url = "https://github.com/github/gitignore"
                raise ValidationError(
                    message='Language selections must one of {}'.format(url)
                )


def prompt_for_languages():
    # Temporary disable cursor (for progress spinner)
    if which('setterm'):
        os.system('setterm -cursor off')
    try:
        fname, headers = urlretrieve(github_api_url, reporthook=show_progress)
    except HTTPError:
        sys.exit("Unable to reach github API")
    else:
        with open(fname) as data_file:
            urls = parse_urls_from_repo(json.load(data_file))
            completions = tuple(map(attrgetter('language'), urls))
            completer = WordCompleter(completions, ignore_case=True)
            validator = LanguageValidator(completions)
            print(
                'Enter programing languages separated by commas in the'
                ' prompt below\n'
                '    Press <TAB> to see available completions\n'
                '    E.g. Python, Go, Node\n'
            )
            try:
                selected = prompt(
                    'Enter languages > ',
                    completer=completer,
                    validator=validator
                )
            except (EOFError, KeyboardInterrupt):
                sys.exit('Exiting')
            else:
                languages = [choice.strip() for choice in selected.split(',')]
                return [url for url in urls if url.language in languages]
    finally:
        # Re enable cursor
        if which('setterm'):
            os.system('setterm -cursor on')


def main():

    if not args.languages:
        urls = prompt_for_languages()
    else:
        urls = [(lang, resolve_url(lang)) for lang in args.languages]

    out_stream = BytesIO()

    for index, info in enumerate(urls, 1):
        write_file_to_stream(*info, index, out_stream, len(urls))

    with open(args.out, 'w') as out:
        contents = out_stream.getvalue().decode('utf-8').strip()
        out.write(contents)
        if args.preview:
            print(contents)
            response = input("\nKeep? [Y/n]: ").lower()
            if response != "y":
                os.remove(out.name)
    print("Written to: {}".format(args.out))


if __name__ == '__main__':
    main()
