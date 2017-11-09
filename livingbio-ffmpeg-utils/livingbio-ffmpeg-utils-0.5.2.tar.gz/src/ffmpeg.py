#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 lizongzhe
#
# Distributed under terms of the MIT license.
import json
import logging
import os
import re
import subprocess

from workspace import cache


def execute(cmd, ignore_error=False):
    logging.info(u"Exe: {}".format(cmd))

    cmd = map(str, cmd)
    process = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )
    message = process.communicate()[1]

    logging.info(u"{}".format(message))
    rc = process.returncode

    if not ignore_error:
        assert rc == 0, u'EXE: %s\n%s' % (cmd, message)

    return message


def get_dimension(videofile):
    lines = execute(['ffmpeg', '-i', videofile], ignore_error=True).split('\n')

    for line in lines:
        rx = re.compile(r'.+Video.+, (\d{2,4})x(\d{2,4}).+')
        m = rx.match(line)

        if m is not None:
            w = int(m.group(1))
            h = int(m.group(2))

            return w, h


def get_duration(video):
    command = [
        "ffmpeg",
        "-i", video,
    ]
    proc_log = execute(command, ignore_error=True)
    duration = __parse_duration(proc_log)
    return duration


def __parse_duration(ffmpeg_log):
    duration_str = re.search(r"Duration:\s+([\d:.]*)", ffmpeg_log).groups()[0]
    duration = __time_to_second(duration_str)
    return duration


def __time_to_second(time_str):
    hour_str, minute_str, second_str, _ = re.match(
        "(\d{1,2}):(\d{1,2}):(\d{1,2}(\.\d+)?)", time_str).groups()
    hour, minute, second = int(hour_str), int(minute_str), float(second_str)
    total_seconds = hour * 3600 + minute * 60 + second
    return total_seconds


def __parse_frames_log(ffmpeg_log):
    lines = re.split("[\r\n]", ffmpeg_log)
    img_logs = [line for line in lines if "pts_time" in line]
    frames = []
    for img_log in img_logs:
        img_info = dict(re.findall(
            "(\w+)\s*:\s*([^ \[]+|\[[^\]]*\])", img_log.replace(' \x08', '')))
        img_info['pts_time'] = float(img_info['pts_time'])
        img_info['n'] = int(img_info['n'])
        img_info['stdev'] = json.loads(img_info['stdev'].replace(' ', ','))
        img_info['mean'] = json.loads(img_info['mean'].replace(' ', ','))
        frames.append(img_info)

    return frames


def __second_to_time(total_seconds):
    total_seconds = float(total_seconds)

    hour = int(total_seconds / 3600)
    minute = int((total_seconds % 3600) / 60)
    seconds = int(total_seconds % 60)
    point = str(total_seconds % 1.0).split(".")[1]

    return "{:0>2}:{:0>2}:{:0>2}.{}".format(hour, minute, seconds, point)


def __check_has_output(ffmpeg_log):
    assert "Output file is empty, nothing was encoded" not in ffmpeg_log


def __get_scene_infos(video, threshold):
    command = [
        "ffmpeg",
        '-y',
        "-i", video,
        "-filter", "select='gt(scene\\,{0})',showinfo".format(threshold),
        "-vsync", "0",
        "-an",
        "-f", "null", "/dev/null"
    ]

    proc_log = execute(command)
    frame_infos = __parse_frames_log(proc_log)

    return frame_infos


def __is_effict_frame(frame_info):
    return not sum(frame_info['stdev']) < 10


def __merge_scences(frame_durations, merge_delta_time=0.7, min_delta_time=3):
    last_frame_duration = frame_durations[0]
    result = []
    tmp = [last_frame_duration]
    for frame_duration in frame_durations[1:]:
        frame_info, frame_time = frame_duration
        delta_time = frame_time[1] - frame_time[0]

        last_frame_info, last_frame_time = last_frame_duration
        last_delta_time = last_frame_time[1] - last_frame_time[0]

        if __is_effict_frame(frame_info) and __is_effict_frame(last_frame_info) and last_delta_time < merge_delta_time and delta_time < merge_delta_time:
            tmp.append(frame_duration)
            continue
        else:
            duration = tmp[0][1][0], tmp[-1][1][1]
            if __is_effict_frame(tmp[0][0]) and duration[1] - duration[0] > min_delta_time:
                result.append((tmp[0], duration))
            last_frame_duration = frame_duration
            tmp = [last_frame_duration]
    result = [r[1] for r in result]
    return result


def _cut_scenes(video_path, threshold, min_delta_time=None):
    scenes = []
    # first_frame = __cut_frame(video_path, 0)

    total_duration = get_duration(video_path)
    frame_infos = __get_scene_infos(video_path, threshold)

    frame_infos = frame_infos

    times = [frame_info['pts_time'] for frame_info in frame_infos]
    times.append(total_duration)

    durations = zip(times[:-1], times[1:])
    frame_durations = zip(frame_infos, durations)

    if not min_delta_time:
        if total_duration < 60:
            min_delta_time = 1
        else:
            min_delta_time = 3

    scenes = __merge_scences(frame_durations, min_delta_time=min_delta_time)

    if not scenes:
        scenes = [(0, total_duration)]

    result = []
    for scene in scenes:
        # get scene center frame (start + end)/2 * fps // fps=22
        info = {
            'from_ts': scene[0],
            'to_ts': scene[1],
            'duration': scene[1] - scene[0]
        }
        result.append(info)

    return result, total_duration


def get_scene_info(filepath, threshold, min_delta_time):
    # make sure all video is split completely
    scenes, total_duration = _cut_scenes(filepath, threshold, min_delta_time)

    # add first clip
    if scenes[0]['from_ts'] > 1:
        scenes.insert(0, {
            "from_ts": 0,
            "to_ts": scenes[0]['from_ts'],
            "duration": scenes[0]['from_ts'],
        })

    if scenes[-1]['to_ts'] + 1 < total_duration:
        scenes.append({
            "from_ts": scenes[-1]["to_ts"],
            "to_ts": total_duration,
            "duration": total_duration - scenes[-1]["to_ts"],
        })

    return scenes


@cache(u'{0}-{1}-{2}.mp4')
def cut_clip(path, from_ts, duration, opath):
    execute([
        'ffmpeg',
        '-ss',
        from_ts,
        '-t',
        duration,
        '-i',
        path,
        '-strict',
        '-2',
        '-movflags',
        '+faststart',
        opath
    ])
    return opath


@cache(u'{0}-{1}-tmp/')
def _sample_images(path, fps, opath):
    execute([
        'ffmpeg',
        '-i',
        path,
        '-r',
        fps,
        '{}thumb%05d.jpg'.format(opath)
    ])

    return opath


def sample_images(path, fps):
    odir = _sample_images(path, fps)

    files = [os.path.join(odir, ifile) for ifile in os.listdir(odir) if ifile.endswith('.jpg')]
    files.sort()

    return files


@cache(u'{0}.wav')
def convert_wav(path, opath):
    execute([
        'ffmpeg',
        '-i',
        path,
        opath
    ])

    return opath


@cache(u'{0}.{1}x{2}.mp4')
def convert_mp4(filepath, width, height, opath):
    execute([
        'ffmpeg',
        '-i',
        filepath,
        '-vf',
        'scale={}:{}'.format(width, height),
        '-strict',
        '-2',
        '-movflags',
        '+faststart',
        opath
    ])

    return opath


def sample_clips(filepath, threshold=0.3, min_delta_time=1):
    scenes = get_scene_info(filepath, threshold, min_delta_time)

    def _iter():
        for scene in scenes:
            yield scene, cut_clip(filepath, scene['from_ts'], scene['duration'])

    return list(_iter())


@cache("{0}-{1}.jpg")
def extract_frame(filepath, second, opath):
    execute([
        "ffmpeg",
        "-ss",
        second,
        "-i",
        filepath,
        "-vframes",
        1,
        opath
    ])
    return opath
