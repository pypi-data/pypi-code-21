# coding=utf-8
import os
import time


def nowTimeStr():
    secs = time.time()
    return time.strftime("%Y-%m-%d-%H%M", time.localtime(secs))


def generateGIF(video_path):
    if os.path.isfile(video_path):
        ffmpeg_cmd = 'ffmpeg -ss 00:00:11 -t 00:00:01 -i ' + video_path + ' -r 1 -s 1440*810 -f gif ' + video_path.replace(
            '.mp4', '.gif')
        os.system(ffmpeg_cmd)
    return video_path.replace('.mp4', '.gif')


def picMark(video_path):
    mark_path = 'winmark.png'

    split_first = 'ffmpeg -ss 00:00:00 -t 00:00:20 -i ' + video_path + ' -strict -2  -vcodec copy -y split1.mp4'
    os.system(split_first)
    split_second = 'ffmpeg -ss 00:00:20  -i ' + video_path + ' -strict -2  -vcodec copy -y split2.mp4'
    os.system(split_second)
    water_cmd = 'ffmpeg -i split1.mp4 -i ' + mark_path + ' -strict -2 -filter_complex "overlay=x=main_w-overlay_w-10:y=main_h-overlay_h-10" -y split0.mp4'
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


def batachMark(video_dir):
    for root, dirs, names in os.walk(video_dir):
        for name in names:
            if '.mp4' in name:
                sr_path = os.path.join(root, name)
                time_str = nowTimeStr()
                des_path = os.path.join(root, time_str + '.mp4')
                os.rename(sr_path, des_path)
                gif_path = generateGIF(des_path)
                mark_video = picMark(des_path)
                os.rename(gif_path, sr_path.replace('.mp4', '.gif'))
                os.rename(mark_video, sr_path)

    return 0


if __name__ == '__main__':
    batachMark('video')
