import argparse
import json
import logging
import os.path
import pprint
import re
import os
import time

import musicbrainz
import youtube_dl

import youtube

log_directory = None
logged_data = {}
logged_messages = []
use_musicbrainz = False


def init_musicbrainz(app, version):
    global use_musicbrainz
    use_musicbrainz = True
    musicbrainz.init_musicbrainz(app, version)


def set_log_directory(path):
    global log_directory
    log_directory = path


def log_data(key, value):
    if log_directory:
        global logged_data
        logged_data[key] = value


def write_log():
    if log_directory is None:
        return
    with open(os.path.join(log_directory, logged_data['id']), 'w') as f:
        json.dump(logged_data, f, indent=4)


def get_offset(hours, minutes, seconds):
    return (int(hours) * 3600 if hours else 0) + int(minutes) * 60 + int(seconds)


def parse_description(description):
    tracks = []
    for line in description.splitlines():
        m = re.search('(\(?\[?(?:(\d+):)?(\d+):(\d+))(?:.*)(?:(?:\d+:)?\d+:\d+)?', line)
        if m is None:
            continue
        if m.start(1) > len(line) - m.end(1):
            title = line[:m.start(1)]
        else:
            title = line[m.end(1):]
        title = title.strip()
        tracks.append(dict(title=title, offset=get_offset(m.group(2), m.group(3), m.group(4))))
    # If track no is present, remove lines without it
    matches = [(t, re.match('\s*0?%d+[ ./":-]* ?(.*)' % i, t['title'])) for (i, t) in enumerate(tracks, 1)]
    if len([1 for m in matches if m[1]]) >= len(tracks) / 2:
        logging.info('Detected track numbers')
        tracks = []
        for (track, match) in matches:
            if match:
                tracks.append(track)
                tracks[-1]['title'] = match.group(1)
    if tracks != sorted(tracks, key=lambda x: x['offset']):
        logging.info('Got track lengths, not offsets')
        # Got track lengths, not offsets
        lengths = [0] + [t['offset'] for t in tracks]
        for i in range(len(tracks)):
            tracks[i]['offset'] = lengths[i] + (tracks[i - 1]['offset'] if i > 0 else 0)
    for track in tracks:
        track['title'] = track['title'].strip('"/- \t')
    return tracks


def guess_artist_album(d):
    ignore = ['\([^)]*\)', '\[[^]]*\]', '\{[^}]*\}', 'full album.*', '(?<!\w)hd(?!\w)', '(?<!\w)hq(?!\w)']
    t = d['title']
    logging.info('Title: %s', d['title'])
    for regexp in ignore:
        t = re.sub(regexp, '', t, flags=re.IGNORECASE)
        logging.debug('Title after %s removal: %s', regexp, t)
    t = t.strip()
    logging.info('Title after junk removal: %s', t)
    m = re.match('(.*)\s* -\s* (.*)', t)
    if m:
        d['artist'] = m.group(1)
        d['album'] = m.group(2)
        if len(d['album']) > 2 and d['album'].startswith('"') and d['album'].startswith('"'):
            d['album'] = d['album'].strip('"')
        logging.info('Guessing artist/album\n   Artist: %s\n   Album: %s\n', d['artist'], d['album'])
    else:
        logging.info('Cannot guess artist/album')


def add_duration(tracks, duration):
    for i in range(len(tracks) - 1):
        tracks[i]['duration'] = tracks[i + 1]['offset'] - tracks[i]['offset']
    tracks[-1]['duration'] = duration - tracks[-1]['offset']


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        logging.warn('youtube-dl warn: %s', msg)

    def error(self, msg):
        logging.error('youtube-dl error: %s', msg)


def youtubedl(url):
    """Retry youtube-dl -j until it returns the description"""
    ytdl = youtube_dl.YoutubeDL({'logger': MyLogger()})
    for _ in range(3):
        o = ytdl.extract_info(url, download=False)
        if not o.get('description'):
            logging.warn('youtube-dl returned empty description')
            time.sleep(3)
            continue
        return o
    return o


def _get_cue(url):
    o = youtubedl(url)
    title = o['title']
    log_data('youtubedl', o)
    logging.info('Got description\n%s\n', o['description'])
    d = dict(url=o['webpage_url'],
             duration=o['duration'],
             title=title,
             tracks=parse_description(o['description']))
    logging.info('Parsed description\n%s\n', pprint.pformat(d['tracks']))
    if not d['tracks']:
        logging.info('Could not parse tracks from description, trying comments')
        comments = list(youtube.get_comments(d['url']))
        log_data('comments', comments)
        for comment in comments:
            d['tracks'] = parse_description(comment)
            if d['tracks']:
                log_data('comment', comment)
                logging.info('Parsed comment:\n%s\n', comment)
                logging.info('Parsed tracks from comment:\n%s\n', pprint.pformat(d['tracks']))
                break
    if len(d['tracks']) < 2:
        # Not much of a cue with just 1 track, eh?
        d['tracks'] = []
    if d['tracks']:
        guess_artist_album(d)
        if d.get('artist'):
            logging.info('Have artist, using musicbrainz to guess track titles')
            if use_musicbrainz:
                musicbrainz.guess_tracks(d)
        add_duration(d['tracks'], d['duration'])
    log_data('output', d)
    return d


def get_cue(url):
    if log_directory:
        youtubeid = youtube.get_youtube_id(url)
        log_data('id', youtubeid)

        fh = logging.FileHandler(os.path.join(log_directory, '%s.log' % youtubeid), mode='w')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(fh)
    try:
        return _get_cue(url)
    except:
        logging.exception('get_cue() failed')
    finally:
        write_log()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='youtube url')
    parser.add_argument('--musicbrainz-app', dest='musicbrainz_app')
    parser.add_argument('--musicbrainz-version', dest='musicbrainz_version')
    args = parser.parse_args()

    if args.musicbrainz_app and args.musicbrainz_version:
        init_musicbrainz(args.musicbrainz_app, args.musicbrainz_version)
    if 'youtubecue_log_dir' in os.environ:
        set_log_directory(os.environ.get('youtubecue_log_dir'))
    print json.dumps(get_cue(args.url), indent=4)
