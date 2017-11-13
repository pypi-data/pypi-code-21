import copy
import difflib
import logging
import pprint

import musicbrainzngs

import youtube_cue


def init_musicbrainz(app, version):
    musicbrainzngs.set_useragent(app, version)


def get_tracks(artist, album):
    recordings = musicbrainzngs.search_recordings(artist=artist, release=album)['recording-list']
    youtube_cue.log_data('musicbrainz', recordings)
    return [r['title'] for r in recordings]


def match_tracks(cue, mb_tracks):
    mb_tracks = set(mb_tracks)
    tracks = copy.deepcopy(cue['tracks'])
    matches = 0
    for track in tracks:
        if len(mb_tracks) == 0:
            return
        by_ratio = sorted([(t, difflib.SequenceMatcher(a=track['title'], b=t).ratio()) for t in mb_tracks],
                          key=lambda x: -x[1])
        if by_ratio[0][1] >= 0.5:
            logging.info('Musicbrainz matched title "%s" with "%s" with score %s',
                         track['title'], by_ratio[0][0], by_ratio[0][1])
            track['title'] = by_ratio[0][0]
            matches += 1
            mb_tracks.remove(by_ratio[0][0])
    if matches > len(tracks) / 2:
        logging.info('Replaced titles with the ones from musicbrainz')
        cue['tracks'] = tracks
    else:
        logging.info('Only %d out of %d titles match musicbrainz, not using musicbrainz data', matches, len(tracks))


def guess_tracks(d):
    mb_tracks = get_tracks(d['artist'], d['album'])
    logging.info('Musicbrainz got track names for (%s, %s):\n%s\n', d['artist'], d['album'], pprint.pformat(mb_tracks))
    match_tracks(d, mb_tracks)
