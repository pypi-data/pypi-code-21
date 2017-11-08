# -*- coding: utf-8 -*-
import re
from subprocess import Popen, PIPE
import os
import click
from .encoding import fix_encoding
from . import require_exe

def get_languages(fn):
  cmd = ['ffmpeg', '-i', fn]
  p = Popen(cmd, stdout=PIPE, stderr=PIPE)
  output, error = p.communicate()
  return re.findall('Stream #(\d+:\d+)\(?(\w*?)\)?: Subtitle: (\w+)', error, flags=re.S)


@click.command(help='Extract embedded subtitles from a movie file')
@click.argument('fn', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--lang', 'language', default=None)
@click.option('--encoding', 'encoding', default='windows-1250')
@click.option('-f', '--first', is_flag=True, default=False)
def esub(fn, language, encoding, first):
    require_exe('ffmpeg')
    langs = get_languages(fn)
    if not (language or first):
        if langs:
            return click.echo('\n'.join('#%s: language "%s" format "%s"' % a for a in langs))
        else:
            return click.secho('no subtitles found', fg='red', bold=True)
    lang = [a for a in langs if a[1] == language or first]
    if not lang:
        return click.secho('no subtitles in selected language', fg='red', bold=True)
    lang = lang[0]
    sfn = os.path.splitext(fn)[0] + '.' + ('srt' if lang[2] == 'subrip' else lang[2])
    click.echo('saving %s subtitles to "%s"' % (lang[1], sfn))
    p = Popen(['ffmpeg', '-i', fn, '-map', lang[0], '-c', 'copy', sfn]).communicate()
    click.echo('converting encoding to %s' % encoding)
    with open(sfn, 'r') as f:
        sub = f.read()
    with open(sfn, 'wb') as f:
        f.write(fix_encoding(sub, encoding=encoding))