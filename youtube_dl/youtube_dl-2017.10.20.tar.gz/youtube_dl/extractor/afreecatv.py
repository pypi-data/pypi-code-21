# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_xpath
from ..utils import (
    determine_ext,
    ExtractorError,
    int_or_none,
    xpath_text,
)


class AfreecaTVIE(InfoExtractor):
    IE_NAME = 'afreecatv'
    IE_DESC = 'afreecatv.com'
    _VALID_URL = r'''(?x)
                    https?://
                        (?:
                            (?:(?:live|afbbs|www)\.)?afreeca(?:tv)?\.com(?::\d+)?
                            (?:
                                /app/(?:index|read_ucc_bbs)\.cgi|
                                /player/[Pp]layer\.(?:swf|html)
                            )\?.*?\bnTitleNo=|
                            vod\.afreecatv\.com/PLAYER/STATION/
                        )
                        (?P<id>\d+)
                    '''
    _TESTS = [{
        'url': 'http://live.afreecatv.com:8079/app/index.cgi?szType=read_ucc_bbs&szBjId=dailyapril&nStationNo=16711924&nBbsNo=18605867&nTitleNo=36164052&szSkin=',
        'md5': 'f72c89fe7ecc14c1b5ce506c4996046e',
        'info_dict': {
            'id': '36164052',
            'ext': 'mp4',
            'title': '데일리 에이프릴 요정들의 시상식!',
            'thumbnail': 're:^https?://(?:video|st)img.afreecatv.com/.*$',
            'uploader': 'dailyapril',
            'uploader_id': 'dailyapril',
            'upload_date': '20160503',
        },
        'skip': 'Video is gone',
    }, {
        'url': 'http://afbbs.afreecatv.com:8080/app/read_ucc_bbs.cgi?nStationNo=16711924&nTitleNo=36153164&szBjId=dailyapril&nBbsNo=18605867',
        'info_dict': {
            'id': '36153164',
            'title': "BJ유트루와 함께하는 '팅커벨 메이크업!'",
            'thumbnail': 're:^https?://(?:video|st)img.afreecatv.com/.*$',
            'uploader': 'dailyapril',
            'uploader_id': 'dailyapril',
        },
        'playlist_count': 2,
        'playlist': [{
            'md5': 'd8b7c174568da61d774ef0203159bf97',
            'info_dict': {
                'id': '36153164_1',
                'ext': 'mp4',
                'title': "BJ유트루와 함께하는 '팅커벨 메이크업!'",
                'upload_date': '20160502',
            },
        }, {
            'md5': '58f2ce7f6044e34439ab2d50612ab02b',
            'info_dict': {
                'id': '36153164_2',
                'ext': 'mp4',
                'title': "BJ유트루와 함께하는 '팅커벨 메이크업!'",
                'upload_date': '20160502',
            },
        }],
        'skip': 'Video is gone',
    }, {
        'url': 'http://vod.afreecatv.com/PLAYER/STATION/18650793',
        'info_dict': {
            'id': '18650793',
            'ext': 'mp4',
            'title': '오늘은 다르다! 쏘님의 우월한 위아래~ 댄스리액션!',
            'thumbnail': r're:^https?://.*\.jpg$',
            'uploader': '윈아디',
            'uploader_id': 'badkids',
            'duration': 107,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://vod.afreecatv.com/PLAYER/STATION/10481652',
        'info_dict': {
            'id': '10481652',
            'title': "BJ유트루와 함께하는 '팅커벨 메이크업!'",
            'thumbnail': 're:^https?://(?:video|st)img.afreecatv.com/.*$',
            'uploader': 'dailyapril',
            'uploader_id': 'dailyapril',
            'duration': 6492,
        },
        'playlist_count': 2,
        'playlist': [{
            'md5': 'd8b7c174568da61d774ef0203159bf97',
            'info_dict': {
                'id': '20160502_c4c62b9d_174361386_1',
                'ext': 'mp4',
                'title': "BJ유트루와 함께하는 '팅커벨 메이크업!' (part 1)",
                'thumbnail': 're:^https?://(?:video|st)img.afreecatv.com/.*$',
                'uploader': 'dailyapril',
                'uploader_id': 'dailyapril',
                'upload_date': '20160502',
                'duration': 3601,
            },
        }, {
            'md5': '58f2ce7f6044e34439ab2d50612ab02b',
            'info_dict': {
                'id': '20160502_39e739bb_174361386_2',
                'ext': 'mp4',
                'title': "BJ유트루와 함께하는 '팅커벨 메이크업!' (part 2)",
                'thumbnail': 're:^https?://(?:video|st)img.afreecatv.com/.*$',
                'uploader': 'dailyapril',
                'uploader_id': 'dailyapril',
                'upload_date': '20160502',
                'duration': 2891,
            },
        }],
        'params': {
            'skip_download': True,
        },
    }, {
        # non standard key
        'url': 'http://vod.afreecatv.com/PLAYER/STATION/20515605',
        'info_dict': {
            'id': '20170411_BE689A0E_190960999_1_2_h',
            'ext': 'mp4',
            'title': '혼자사는여자집',
            'thumbnail': 're:^https?://(?:video|st)img.afreecatv.com/.*$',
            'uploader': '♥이슬이',
            'uploader_id': 'dasl8121',
            'upload_date': '20170411',
            'duration': 213,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        # adult video
        'url': 'http://vod.afreecatv.com/PLAYER/STATION/26542731',
        'info_dict': {
            'id': '20171001_F1AE1711_196617479_1',
            'ext': 'mp4',
            'title': '[생]서아 초심 찾기 방송 (part 1)',
            'thumbnail': 're:^https?://(?:video|st)img.afreecatv.com/.*$',
            'uploader': 'BJ서아',
            'uploader_id': 'bjdyrksu',
            'upload_date': '20171001',
            'duration': 3600,
            'age_limit': 18,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://www.afreecatv.com/player/Player.swf?szType=szBjId=djleegoon&nStationNo=11273158&nBbsNo=13161095&nTitleNo=36327652',
        'only_matching': True,
    }, {
        'url': 'http://vod.afreecatv.com/PLAYER/STATION/15055030',
        'only_matching': True,
    }]

    @staticmethod
    def parse_video_key(key):
        video_key = {}
        m = re.match(r'^(?P<upload_date>\d{8})_\w+_(?P<part>\d+)$', key)
        if m:
            video_key['upload_date'] = m.group('upload_date')
            video_key['part'] = int(m.group('part'))
        return video_key

    def _real_extract(self, url):
        video_id = self._match_id(url)

        video_xml = self._download_xml(
            'http://afbbs.afreecatv.com:8080/api/video/get_video_info.php',
            video_id, query={
                'nTitleNo': video_id,
                'partialView': 'SKIP_ADULT',
            })

        flag = xpath_text(video_xml, './track/flag', 'flag', default=None)
        if flag and flag != 'SUCCEED':
            raise ExtractorError(
                '%s said: %s' % (self.IE_NAME, flag), expected=True)

        video_element = video_xml.findall(compat_xpath('./track/video'))[1]
        if video_element is None or video_element.text is None:
            raise ExtractorError('Specified AfreecaTV video does not exist',
                                 expected=True)

        video_url = video_element.text.strip()

        title = xpath_text(video_xml, './track/title', 'title', fatal=True)

        uploader = xpath_text(video_xml, './track/nickname', 'uploader')
        uploader_id = xpath_text(video_xml, './track/bj_id', 'uploader id')
        duration = int_or_none(xpath_text(
            video_xml, './track/duration', 'duration'))
        thumbnail = xpath_text(video_xml, './track/titleImage', 'thumbnail')

        common_entry = {
            'uploader': uploader,
            'uploader_id': uploader_id,
            'thumbnail': thumbnail,
        }

        info = common_entry.copy()
        info.update({
            'id': video_id,
            'title': title,
            'duration': duration,
        })

        if not video_url:
            entries = []
            file_elements = video_element.findall(compat_xpath('./file'))
            one = len(file_elements) == 1
            for file_num, file_element in enumerate(file_elements, start=1):
                file_url = file_element.text
                if not file_url:
                    continue
                key = file_element.get('key', '')
                upload_date = self._search_regex(
                    r'^(\d{8})_', key, 'upload date', default=None)
                file_duration = int_or_none(file_element.get('duration'))
                format_id = key if key else '%s_%s' % (video_id, file_num)
                formats = self._extract_m3u8_formats(
                    file_url, video_id, 'mp4', entry_protocol='m3u8_native',
                    m3u8_id='hls',
                    note='Downloading part %d m3u8 information' % file_num)
                file_info = common_entry.copy()
                file_info.update({
                    'id': format_id,
                    'title': title if one else '%s (part %d)' % (title, file_num),
                    'upload_date': upload_date,
                    'duration': file_duration,
                    'formats': formats,
                })
                entries.append(file_info)
            entries_info = info.copy()
            entries_info.update({
                '_type': 'multi_video',
                'entries': entries,
            })
            return entries_info

        info = {
            'id': video_id,
            'title': title,
            'uploader': uploader,
            'uploader_id': uploader_id,
            'duration': duration,
            'thumbnail': thumbnail,
        }

        if determine_ext(video_url) == 'm3u8':
            info['formats'] = self._extract_m3u8_formats(
                video_url, video_id, 'mp4', entry_protocol='m3u8_native',
                m3u8_id='hls')
        else:
            app, playpath = video_url.split('mp4:')
            info.update({
                'url': app,
                'ext': 'flv',
                'play_path': 'mp4:' + playpath,
                'rtmp_live': True,  # downloading won't end without this
            })

        return info
