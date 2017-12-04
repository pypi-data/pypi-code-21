import os
import mutagen
import mutagen.id3
from logbook import warn


FIELDS = ('title',
          'artist',
          'album',
          'genre',
          'albumartist',
          'bpm',
          'key',
          'tracknumber',
          'year')


class NoTaggerError(Exception):
    pass


class Tagger(object):

    def __init__(self, fname):
        self.tags = mutagen.File(fname)

    def save(self):
        self.tags.save()

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __str__(self):
        return str(self.todict())

    def todict(self):
        return {key: self[key] for key in FIELDS}


class Mp3Tagger(Tagger):

    supported_extensions = ('.mp3',)

    def __getitem__(self, key):
        try:
            return self.tags[self.translate_key(key)].text[0]
        except KeyError:
            # This should not happen for correcly formatted tags, but it seems
            # to happen for some files
            return None

    def __setitem__(self, key, value):
        tagname = self.translate_key(key)
        self.tags[tagname] = getattr(mutagen.id3, tagname)(text=[value])

    @staticmethod
    def translate_key(key):
        d = {'title': 'TIT2',
             'artist': 'TPE1',
             'album': 'TALB',
             'genre': 'TCON',
             'albumartist': 'TPE2',
             'bpm': 'TBPM',
             'tracknumber': 'TRCK',
             'year': 'TYER',
             'key': 'TKEY',
             }
        return d[key]


class FlacTagger(Tagger):

    supported_extensions = ('.flac', '.ogg')

    def __getitem__(self, key):
        if key in self.tags:
            return self.tags[key][0]
        else:
            return None

    def __setitem__(self, key, value):
        self.tags[key] = [value]


class M4aTagger(Tagger):

    supported_extensions = ('.m4a',)

    def __getitem__(self, key):
        if key == 'tracknumber':
            return str(self.tags['trkn'][0][0])
        elif key == 'key':
            warn('Keys are not supported for M4A files')
            return ''
        return self.tags[self.translate_key(key)][0]

    def __setitem__(self, key, value):
        if key == 'tracknumber':
            k, n = self.tags['trkn'][0]
            self.tags['trkn'][0] = (int(value), n)
        elif key == 'key':
            warn('Keys are not supported for M4A files')
            pass
        else:
            self.tags[self.translate_key(key)] = [value]

    def translate_key(self, key):
        self.d = {'title': '\xa9nam',
                  'artist': '\xa9ART',
                  'album': '\xa9alb',
                  'genre': '\xa9gen',
                  'albumartist': 'aART',
                  'bpm': 'tmpo',
                  'year': '\xa9day',
                  }
        if key == 'key' and key not in self.d:
            candidates = [key for key in self.tags if 'initialkey' in key]
            self.d['key'] = candidates[0]
        return self.d[key]


def get_tagger(fname):
    basename, extension = os.path.splitext(fname)
    tagger = [tagr
              for tagr in Tagger.__subclasses__()
              if extension.lower() in tagr.supported_extensions]
    if len(tagger):
        return tagger[0](fname)
    else:
        raise NoTaggerError('Could not find tagger for extension {}'
                            .format(extension))


def bpm2str(value):
    return str(int(round(float(value))))


def set_multiple_tags(fname, tags, prefix=''):
    tagger = get_tagger(fname)
    changed = False
    for key in FIELDS:
        value = tags.get(prefix + key, None)
        if value is not None:
            tagger[key] = value
            changed = True
    if changed:
        tagger.save()
