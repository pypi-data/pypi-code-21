# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import pycountry
from pymediainfo import MediaInfo
from fractions import Fraction

from pyfileinfo.file import File


class Medium(File):
    def __init__(self, file_path):
        File.__init__(self, file_path)

        self._video_tracks = None
        self._audio_tracks = None
        self._subtitle_tracks = None
        self._duration = None
        self._mean_volume = None

        self._mediainfo = None

    @staticmethod
    def is_valid(path):
        if os.path.getsize(path) == 0:  # mediainfo can't handle empty file.
            return False

        medium = Medium(path)
        return len(medium.video_tracks) > 0 or len(medium.audio_tracks) > 0

    @property
    def mediainfo(self):
        if self._mediainfo is None:
            self._mediainfo = MediaInfo.parse(self.path)

        return self._mediainfo

    @property
    def title(self):
        return self.mediainfo.tracks[0].title

    @property
    def album(self):
        return self.mediainfo.tracks[0].album

    @property
    def album_performer(self):
        return self.mediainfo.tracks[0].album_performer

    @property
    def performer(self):
        return self.mediainfo.tracks[0].performer

    @property
    def track_name(self):
        return self.mediainfo.tracks[0].track_name

    @property
    def track_name_position(self):
        return self.mediainfo.tracks[0].track_name_position

    @property
    def part_position(self):
        return self.mediainfo.tracks[0].part_position

    @property
    def video_tracks(self):
        if self._video_tracks is None:
            self._video_tracks = [_VideoTrack(track) for track in self.mediainfo.tracks
                                  if track.track_type == 'Video']

        return self._video_tracks

    @property
    def audio_tracks(self):
        if self._audio_tracks is None:
            self._audio_tracks = [_AudioTrack(track) for track in self.mediainfo.tracks
                                  if track.track_type == 'Audio']

        return self._audio_tracks

    @property
    def subtitle_tracks(self):
        if self._subtitle_tracks is None:
            self._subtitle_tracks = [_SubtitleTrack(track) for track in self.mediainfo.tracks
                                     if track.track_type == 'Text']

        return self._subtitle_tracks

    @property
    def chapters(self):
        tracks = [track for track in self.mediainfo.tracks if track.track_type == 'Menu']

        if len(tracks) == 0:
            return [{'Number': 1, 'Start': 0, 'Duration': self.duration}]

        chapters = []
        chapter_number = 1

        for timing in dir(tracks[0]):
            if len(timing.split('_')) != 3:
                continue

            hour, minutes, seconds = timing.split('_')
            if not hour.isdigit():
                continue

            chapters.append({'Number': chapter_number,
                             'Start': float(hour)*3600 + float(minutes)*60 + float(seconds)/1000,
                             'Duration': None})

            chapter_number += 1

        chapters.append({'Start': self.duration})
        for idx in range(len(chapters) - 1):
            chapters[idx]['Duration'] = chapters[idx + 1]['Start'] - chapters[idx]['Start']

        chapters.pop(-1)
        return chapters

    @property
    def main_video_track(self):
        return self.video_tracks[0]

    @property
    def main_audio_track(self):
        if len(self.audio_tracks) == 0:
            return None

        return self.audio_tracks[0]

    @property
    def width(self):
        return self.main_video_track.width

    @property
    def height(self):
        return self.main_video_track.height

    @property
    def interlaced(self):
        return self.main_video_track.interlaced

    @property
    def duration(self):
        return float(self.mediainfo.tracks[0].duration)/1000

    @staticmethod
    def hint():
        return ['.avi', '.mov', '.mp4', '.m4v', '.m4a', '.mkv', '.mpg', '.mpeg', '.ts', '.m2ts']

    def is_audio_track_empty(self):
        return len(self.audio_tracks) == 0

    def is_hd(self):
        return self.width >= 1200 or self.height >= 700

    def is_video(self):
        return len(self.video_tracks) > 0

    def is_audio(self):
        return not self.is_video() and len(self.audio_tracks) > 0


class _Track:
    def __init__(self, track):
        self._track = track

    def __getattr__(self, item):
        return getattr(self._track, item)

    @property
    def stream_id(self):
        return self.stream_identifier

    @property
    def streamorder(self):
        return int(self._track.streamorder)

    @property
    def language(self):
        if self._track.language is None:
            return None

        return pycountry.languages.get(alpha_2=self._track.language)


class _VideoTrack(_Track):
    @property
    def display_aspect_ratio(self):
        for aspect_ratio in self.other_display_aspect_ratio:
            if ':' in aspect_ratio:
                return aspect_ratio

        return self.other_display_aspect_ratio[0]

    @property
    def display_width(self):
        w_ratio, h_ratio = self.display_aspect_ratio.split(':')

        return int(self.height * Fraction(w_ratio) / Fraction(h_ratio))

    @property
    def display_height(self):
        return self.height

    @property
    def interlaced(self):
        return self.scan_type != 'Progressive'

    @property
    def progressive(self):
        return not self.interlaced

    @property
    def frame_rate(self):
        return self._track.frame_rate

    @property
    def frame_count(self):
        return self._track.frame_count


class _AudioTrack(_Track):
    @property
    def channels(self):
        return self.channel_s


class _SubtitleTrack(_Track):
    pass
