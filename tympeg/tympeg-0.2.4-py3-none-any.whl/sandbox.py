import shutil

from converter import MediaConverter
from mediaobject import MediaObject
from pympeg import *
from tools import *

from tympeg.concat import *


def sandbox1():
    filePath = 'T:\Video\Movies\Foreign Movies\Mandarin (Cantonese)\Crouching.Tiger.Hidden.Dragon.2000.1080p.Bluray.DTS.x264-GCJM.mkv'

    mediaInfo = MediaObject(filePath)
    mediaInfo.run()

    videoStreamIndice = mediaInfo.videoStreams[0]

    speeds = ['veryslow', 'slower', 'slow', 'medium', 'fast', 'faster',
                          'veryfast', 'superfast', 'ultrafast']
    # for speed in speeds:
    #     converter = MediaConverter(mediaInfo, outputFilePath='T:\Video\Movies\Foreign Movies\Mandarin (Cantonese)\Test Set\\' + str(speed) + '.mkv')
    #     converter.createVideoStream(videoStreamIndice, 'cbr', 'x264', cbr=1000, speed=speed)
    #
    #     for stream in mediaInfo.audioStreams:
    #         converter.createAudioStream(stream, audioEncoder='aac', audioBitrate=mediaInfo.bitrates[stream]/1000)
    #
    #     for stream in mediaInfo.subtitleStreams:
    #         converter.createSubtitleStreams(mediaInfo.subtitleStreams)
    #
    #     converter.clip('00:44:08', '00:45:03')

    converter = MediaConverter(mediaInfo, outputFilePath='C:\Media\Crouching Tiger Hidden Dragon.mkv')
    converter.createVideoStream(videoStreamIndice, 'cbr', 'x264', cbr=3500, speed='medium')

    for stream in mediaInfo.audioStreams:
        converter.createAudioStream(stream, audioEncoder='aac', audioBitrate=mediaInfo.bitrates[stream]/1000)

    for stream in mediaInfo.subtitleStreams:
        converter.createSubtitleStreams(mediaInfo.subtitleStreams)

    converter.clip('00:44:08', '00:45:03')


def sandbox2():
    root = 1
    fileList = 2
    mediaObjectArray = makeMediaObjectsInDirectory("C:/Users/taish/Desktop/concattest")
    i = 0

    for file in fileList:
        mediaObject = MediaObject(fileList[i])
        mediaObjectArray.append(mediaObject)
        i =+ 1

    ffConcat(mediaObjectArray, 'C:/Users/taish/Desktop/output.mkv')


def sandbox4():
    mediaObjectArray = makeMediaObjectsInDirectory("C:/Users/taish/Desktop/concattest")

    for media in mediaObjectArray:
        videoStreamIndice = media.videoStreams[0]
        converter = MediaConverter(media, outputFilePath="C:/Users/taish/Desktop/concattest2/" + str(media.fileName) + '.mkv')
        converter.createVideoStream(videoStreamIndice, 'crf', 'x264', crf=20, speed='ultrafast')
        converter.convert()


def sandbox5():
    media = MediaObject("C:/Users/taish/Documents/SpiderOak Hive/PROJECTS/tympeg/testmedia/Sintel_550_Clip.mkv")
    media.run()
    videoEncoders = ['x264', 'x265']
    rateControlMethod = ['crf', 'cbr']

    for encoder in videoEncoders:
        for rateControl in rateControlMethod:

            if rateControl == 'crf':
                rate = 51
            else:
                rate = 400

            converter = MediaConverter(media, "C:/Users/taish/Desktop/" + encoder + "_" + rateControl + "_test.mkv")
            converter.createVideoStream(encoder, rateControl, rate, 'ultrafast')
            converter.convert()


def sandbox6():
    media = MediaObject("C:/Users/taish/Documents/SpiderOak Hive/PROJECTS/tympeg/testmedia/Crouching Tiger Hidden Dragon.mkv")

    cvt = MediaConverter(media, "C:/Users/taish/Desktop/test_dualAudio_dualBitrates.mkv")
    cvt.createVideoStream('x264', 'crf', 23, speed='ultrafast')
    cvt.createAudioStream(media.audioStreams[0], 'opus')
    cvt.createAudioStream(media.audioStreams[1], 'opus')
    cvt.convert()


def sandbox7():
    inputFolder = ""
    mediaArray = makeMediaObjectsInDirectory(inputFolder)

    for media in mediaArray:
        name, ext = path.splitext(media.fileName)
        cvt = MediaConverter(media, inputFolder + "/converted/" + name + '.mkv')
        cvt.createVideoStream('x265', 'crf', 20, speed='veryfast')
        # cvt.createAudioStream(media.audioStreams[0], audioEncoder='opus', audioBitrate=128)
        cvt.convert()

def sandbox8():
    inputFile = ""
    outputFile = ""
    startTime = "00:00:00"
    endTime   = "01:23:15"

    media = MediaObject(inputFile)

    cvt = MediaConverter(media, outputFile)
    cvt.createVideoStream('copy', 'copy', 0)
    cvt.createAudioStream(media.audioStreams[0], audioEncoder='copy')
    cvt.clip(startTime, endTime)


def convert_child_folders_x265(parent_folder, profile):
    dirs = list_dirs(parent_folder)
    for directory in dirs:
        convert_folder_x265_profile(directory, profile)


def speed_quality_test(file_paths, speed, qualities, output_folder):

    with open(path.join(output_folder, 'log.txt'), 'w', encoding='utf8') as f:
        quality_rates = []
        ratios = []
        for i in range(len(qualities)):

            ratios.append(0)
            quality_rates.append([])

        f.write("Files:\n")
        for i in range(len(file_paths)):
            f.write("{}\n".format(file_paths[i]))

        for file in file_paths:
            media = MediaObject(file)
            shutil.copyfile(file, path.join(output_folder, media.fileName))
            # f.write("{}:\n".format(media.fileName))

            for quality in qualities:
                name, ext = media.fileName.split('.')
                output_file_path = path.join(output_folder, name + "_" + str(speed) + "_" + str(quality) + ".mkv")
                cvt = MediaConverter(media, output_file_path)
                cvt.createVideoStream('x265', 'crf', quality, speed)
                cvt.createAudioStream(media.audioStreams[0], 'opus', 96, 'stereo')


                file_time = cvt.convert()


                input_size = media.file_size/1000000  # MB
                output_size = path.getsize(output_file_path)/1000000  # MB
                file_time += 60  # just to make sure div by 0 is avoided
                minutes, seconds = divmod(file_time, 60)
                hours, minutes = divmod(minutes, 60)
                rate_string = "{0:,.2f}".format(input_size/(file_time/60))
                quality_rates[qualities.index(quality)].append(rate_string)
                ratio = output_size/input_size
                ratios[qualities.index(quality)] += ratio

                print("File {0} completed in {1}:{2}:{3:.02f}".format(media.fileName, int(hours), int(minutes), seconds))
                print("\tQuality: {}".format(quality))
                print("\t{0:,.2f} MB >> {1:,.2f} MB".format(input_size, output_size))
                print("\tRatio of {0:.2f}".format(ratio))
                print("\tProcessed input at rate of {} MB/min\n".format(rate_string))

        print(quality_rates)
        for i in range(len(qualities)):
            f.write("\nQuality = {}\n".format(qualities[i]))

            avg_rate = 0
            for j in range(len(file_paths)):
                if i > 1:
                    print("BREAK")
                    print(quality_rates)
                print(i, j)
                avg_rate += float(quality_rates[i][j])
                f.write("Input rate: {} MB/min\n".format(quality_rates[i][j]))

            f.write("Average rate  = {0:,.2f} MB/min\n".format(avg_rate/len(qualities)))
            f.write("Average Ratio = {0:,.2f}\n".format(ratios[i]/len(qualities)))

    f.close()

media = MediaObject("/home/tai/Downloads/[HorribleSubs] Shingeki no Bahamut - Virgin Soul - 01v2 [720p].mkv")
# media = MediaObject("/home/tai/Downloads/test1.mkv")
cvt = MediaConverter(media, "/home/tai/Downloads/test1.mkv", verbosity=8)
# cvt.createVideoStream('vp9', 'crf', 28)
cvt.createVideoStream('x265', 'crf', 25, speed='ultrafast')
cvt.createAudioStream(audioStream=cvt.mediaObject.audioStreams[0], audioEncoder='opus', audioChannels='mono', audioBitrate=64)
# cvt.convert()
cvt.clip("00:01:40", "00:01:50")
# quick_clip("C:/Users/taish/Desktop/test.mkv", subtract_timecodes("00:19:00", "00:20:40"), subtract_timecodes("00:19:00", "00:20:49"), "C:/Users/taish/Desktop/ahegao_fuuka.mp4")
# quick_clip("T:/Cams/XFuukaX-2017-05-02-14-38-39.ts", "00:20:40", "00:20:49", "C:/Users/taish/Desktop/ahegao_fuuka.mp4")
# for file in files:
#     if path.isfile(file):
#         print("Certified file here: " + file)
# crfs = [20, 23, 25, 28]
# # # crfs = [23, 28]
# output = "C:/Users/taish/Desktop/qualities/"
# speed_quality_test(files, 'veryfast', crfs, output)

# save_bits_per_pixel_dist("X:/Dem Gals/JAV/NN & Soft/Actresses/", "C:/Users/taish/Desktop/test.csv", 'hevc')

# m = MediaObject('testmedia/Sintel_550_Clip.mkv')
# m.run()
# cvt = MediaConverter(m, 'testmedia/sintel_resolution_test.mkv', debug=True)
# cvt.createVideoStream('x264', 'crf', 20, 'ultrafast', width=800, height=600)
# cvt.createAudioStream(audioStream=m.audioStreams[0], audioEncoder='opus')
# cvt.convert()

# if __name__ == '__main__':
# m = makeMediaObjectsInDirectory("X:\Dem Gals\JAV\Actresses\Iori Kogawa")
# c = []
# for media in m:
#     name, ext = split_ext(media.fileName)
#     cvt = MediaConverter(media, path.join('C:/Users/taish/Desktop/test', name + '.mkv'))
#     cvt.createVideoStream('x264', 'crf', 20, 'ultrafast')
#     for stream in media.audioStreams:
#         cvt.createAudioStream(audioStream=stream, audioEncoder='opus', audioBitrate=32)
#     c.append(cvt)
#
# q = MediaConverterQueue(max_processes=2)
# q.add_jobs(c)
# q.run()

# print(list_files('testmedia'))
# print(len(list_files('testmedia')))


