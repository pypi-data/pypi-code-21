import os
import time

import pyPdf
from tqdm import tqdm

import subprocess

from datetime import date, datetime, time, timedelta

SEFMENT_TIME = '00:14:00'


def getLength(filename):
    result = subprocess.Popen(["ffprobe", filename],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dur = [x for x in result.stdout.readlines() if "Duration" in x]
    dur = dur[0].split(',')[0].split('Duration: ')[-1].split('.')[0]
    return dur


def nowTimeStr():
    secs = time.time()
    return time.strftime("%Y-%m-%d-%H%M", time.localtime(secs))


def generateGIF(video_path):
    if os.path.isfile(video_path):
        ffmpeg_cmd = 'ffmpeg -ss 00:00:41 -t 00:00:01 -i ' + video_path + ' -r 1 -s 1440*810 -f gif ' + video_path.replace(
            '.mp4', '.gif')
        os.system(ffmpeg_cmd)
    return video_path.replace('.mp4', '.gif')


def picMark(video_path):
    mark_path = 'winmark.png'
    split_first = 'ffmpeg -ss 00:00:00 -t 00:00:20 -i ' + video_path + ' -strict -2  -vcodec copy -y split1.mp4'
    os.system(split_first)
    split_second = 'ffmpeg -ss 00:00:20  -i ' + video_path + ' -strict -2  -vcodec copy -y split2.mp4'
    os.system(split_second)
    water_cmd = 'ffmpeg -i split1.mp4 -i ' + mark_path + ' -strict -2 -filter_complex "overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2" -y split0.mp4'
    print water_cmd
    os.system(water_cmd)
    cmd_line = "ffmpeg -i split0.mp4 -vcodec copy -acodec copy -vbsf h264_mp4toannexb -y c_1.ts"
    os.system(cmd_line)

    cmd_line = "ffmpeg -i split2.mp4 -vcodec copy -acodec copy -vbsf h264_mp4toannexb -y c_2.ts"
    os.system(cmd_line)

    cmd_line = "ffmpeg -i \"concat:c_1.ts|c_2.ts\"  -vcodec copy -acodec copy -absf aac_adtstoasc -y combine.mp4"

    os.system(cmd_line)
    os.remove("c_2.ts")
    os.remove("c_1.ts")
    os.rename('combine.mp4', video_path.replace('.mp4', '_pic_water.mp4'))
    os.remove('split1.mp4')
    os.remove('split0.mp4')
    os.remove('split2.mp4')
    os.remove(video_path)
    return video_path.replace('.mp4', '_pic_water.mp4')


def pdf_link_2_txt(path_pdf='drm20150330-20170310.pdf'):
    PDFFile = open(path_pdf, 'rb')
    PDF = pyPdf.PdfFileReader(PDFFile)
    pages = PDF.getNumPages()
    key = '/Annots'
    uri = '/URI'
    ank = '/A'
    all_link = []
    try:
        for page in range(pages):
            pageSliced = PDF.getPage(page)
            pageObject = pageSliced.getObject()
            if pageObject.has_key(key):
                ann = pageObject[key]
                for a in ann:
                    u = a.getObject()
                    print u
                    print u[ank]
                    if u[ank].has_key(uri):
                        print u[ank][uri]
                        if 'maomaoChyan' not in u[ank][uri]:
                            if 'channel' not in u[ank][uri]:
                                all_link.append(u[ank][uri])
    except KeyError:
        pass

    out_path = path_pdf.replace('.pdf', '.list')
    file_txt = open(out_path, 'w')
    all_link_set = set(all_link)
    for link in all_link_set:
        link = link.split('&')[0]
        file_txt.writelines(link)
        file_txt.writelines('\n')
    file_txt.close()
    return out_path


def down(down_path):
    with open(down_path) as bm:
        bm_lines = bm.readlines()
    for line in tqdm(bm_lines):
        if line[-1] == '\n':
            path = line[:-1]
        else:
            path = line
        cmd = "youtube-dl -f best " + path
        print cmd
        if 'watch?v' in cmd:
            os.system(cmd)
    return 0


def webm2mp4(webmPath):
    cmd = 'ffmpeg -i ' + webmPath + ' -y -strict -2 ' + webmPath.replace('.webm', '.mp4')
    print cmd
    os.system(cmd)
    return webmPath.replace('.webm', '.mp4')


def batachMark(video_dir):
    digital_len = 8
    tag = '[xiu-lai-le]'
    final_path = ''
    for root, dirs, names in os.walk(video_dir):
        for name in names:
            if '.mp4' in name:
                sr_path = os.path.join(root, name)
                time_str = nowTimeStr()
                des_path = os.path.join(root, time_str + '.mp4')
                os.rename(sr_path, des_path)
                gif_path = generateGIF(des_path)
                mark_video = picMark(des_path)
                # os.rename(gif_path, sr_path.replace('.mp4', '.gif'))
                os.remove(gif_path)
                files_in_name = os.path.basename(sr_path)
                numbers = [num for num in sr_path if num.isdigit()]
                date = ''
                for digit_str in numbers:
                    date += digit_str
                files_out = sr_path.replace(files_in_name, date[
                                                           :digital_len] + 'was collected by ' + tag + '_at_' + nowTimeStr() + '_wechat.mp4')  # + files_in_name)
                if len(numbers) < digital_len:
                    os.rename(mark_video, sr_path)
                else:
                    os.rename(mark_video, files_out)
            elif '.webm' in name:
                sr_path = os.path.join(root, name)
                time_str = nowTimeStr()
                des_path = os.path.join(root, time_str + '.webm')
                os.rename(sr_path, des_path)
                des_path = webm2mp4(des_path)

                mark_video = picMark(des_path)
                # os.rename(gif_path, sr_path.replace('.mp4', '.gif'))

                files_in_name = os.path.basename(sr_path)
                numbers = [num for num in sr_path if num.isdigit()]
                date = ''
                for digit_str in numbers:
                    date += digit_str
                files_out = sr_path.replace(files_in_name, date[
                                                           :digital_len] + 'was collected by ' + tag + '_at_' + nowTimeStr() + '_wechat.mp4')  # + files_in_name)
                if len(numbers) < digital_len:
                    os.rename(mark_video, sr_path)
                    final_path = sr_path
                else:
                    os.rename(mark_video, files_out)
                    final_path = sr_path
            elif '.pdf' in name:
                pdf_path = os.path.join(root, name)
                pdf_link_2_txt(pdf_path)
            elif '.list' in name:
                down_path = os.path.join(root, name)
                down(down_path)
    return final_path


def extract_start_dur_video(video_path, video_NO, start_time, dur):
    cmd = 'ffmpeg -i ' + video_path + ' -ss ' + str(start_time) + ' -t ' + str(
        dur) + ' -y -strict -2 -c copy ' + video_path[
                                           :-3] + str(video_NO) + '.mp4'
    os.system(cmd)

    return 0


def calcTime(now, delta):
    dt = datetime.combine(date.today(), time(now[0], now[1])) + timedelta(minutes=delta)
    # print dt.time()
    return dt.time()


def split_into_n_part(video_path):
    start_time = calcTime([0, 0], 0)
    dur = getLength(video_path)
    dur_list = dur.split(':')
    hour, mins, secs = int(dur_list[0]), int(dur_list[1]), int(dur_list[2])
    print hour, mins, secs
    NO = 1
    while start_time < calcTime([int(hour), int(mins)], 0):
        extract_start_dur_video(video_path, NO, start_time, SEFMENT_TIME)
        NO += 1
        start_time_h, start_time_m = start_time.hour, start_time.minute
        print start_time
        start_time = calcTime([start_time_h, start_time_m], int(SEFMENT_TIME[3:5]))

    return 0


if __name__ == '__main__':
    video_path = batachMark('v')
    # video_path = 'v/t.mp4'
    # generateGIF(video_path)
    # split_into_n_part(video_path)
