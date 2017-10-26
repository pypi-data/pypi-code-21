# coding=utf-8
import os
import subprocess
import time
import tkFileDialog
import tkMessageBox
from Tkinter import *

import pyPdf

# a.datas += [('mark.png', './winmark.png', 'DATA'), ('wechat.gif', './wechat.gif', 'DATA')]

SEP = os.sep
###########parm#####
ENTRY_WITDH = 65
window_width = 500
window_height = 180
###########parm#####
reload(sys)
sys.setdefaultencoding('utf8')
try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.abspath(".")
font_path = os.path.join(base_path, 'font.fon')
wechat_path = os.path.join(base_path, 'wechat.gif')
mark_path = os.path.join(base_path, 'mark.png')


# execute command, and return the output
def execCmd(cmd):
    text = ''
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        text += '\n' + line
    return text


def probe_duration(m3u8_test):
    cmd = "ffprobe -i " + m3u8_test
    result = execCmd(cmd)
    dur = 'Duration: (.*), start'
    DURATION = re.findall(dur, result)[0]
    print DURATION
    return DURATION


def get_file_size(file_path):
    return os.path.getsize(file_path)


def if_no_create_it(file_path):
    the_dir = os.path.dirname(file_path)
    if os.path.isdir(the_dir):
        pass
    else:
        os.makedirs(the_dir)


def nowTimeStr():
    secs = time.time()
    return time.strftime("%Y-%m-%d-%H%M", time.localtime(secs))


def pdf_link_2_txt(path_pdf='drm20150330-20170310.pdf'):
    PDFFile = open(path_pdf, 'rb')
    PDF = pyPdf.PdfFileReader(PDFFile)
    pages = PDF.getNumPages()
    key = '/Annots'
    uri = '/URI'
    ank = '/A'
    all_link = []
    for page in range(pages):
        pageSliced = PDF.getPage(page)
        pageObject = pageSliced.getObject()
        if pageObject.has_key(key):
            ann = pageObject[key]
            for a in ann:
                u = a.getObject()
                if u[ank].has_key(uri):
                    print u[ank][uri]
                    if 'maomaoChyan' not in u[ank][uri]:
                        if 'channel' not in u[ank][uri]:
                            all_link.append(u[ank][uri])
    out_path = path_pdf.replace('.pdf', '.txt')
    file_txt = open(out_path, 'w')
    all_link_set = set(all_link)
    for link in all_link_set:
        link = link.split('&')[0]
        file_txt.writelines(link)
        file_txt.writelines('\n')
    file_txt.close()
    return out_path


def download_youtube(link_txt='linkdrm20130701-20150325.txt'):
    txt_file = open(link_txt, 'r')
    links = txt_file.readlines()
    txt_file.close()
    for download_link in links:
        # print links
        command = "youtube-dl " + download_link.split('&')[0] + " -c"
        print command
        os.system(command)
    return 0


def rename_tag(rename_file_dir='toberename', tag='【咻】', digital_len=8):
    for parent, dirnames, filenames in os.walk(rename_file_dir):
        for filename in filenames:
            files_in = os.path.join(parent, filename)
            files_in_name = os.path.basename(files_in)
            numbers = [num for num in files_in_name if num.isdigit()]
            date = ''
            for digit_str in numbers:
                date += digit_str
            files_out = files_in.replace(files_in_name, date[:digital_len] + tag + files_in_name)
            os.rename(files_in, files_out)
    return 0


def downVideoGUI():
    def combine_all_video(dir="./"):
        video_path = []
        for parent, dirname, filename in os.walk(dir):
            for file in filename:
                path = os.path.join(parent, file)
                if ".mp4" in path or '.MP4' in path:
                    video_path.append(path)
        video_path = sorted(video_path)
        if len(video_path) != 0:
            number = 1
            for sub_video in video_path:
                cmd_line = "ffmpeg -i " + sub_video + " -vcodec copy -acodec copy -vbsf h264_mp4toannexb output_" + str(
                    number) + ".ts"
                os.system(cmd_line)
                os.remove(sub_video)
                number += 1
            file_str = ""
            for file_i in range(len(video_path) - 1):
                file_str += "output_" + str(file_i + 1) + ".ts|"
            file_str += "output_" + str(len(video_path)) + ".ts"
            cmd_line = "ffmpeg -i \"concat:" + file_str + "\"  -vcodec copy -acodec copy -absf aac_adtstoasc combine.mp4"
            os.system(cmd_line)
            for temp_i in range(len(video_path)):
                os.remove("output_" + str(temp_i + 1) + ".ts")
        return 0

    def download_pdf_for_link():
        pdf_path = link_contend.get()
        if pdf_path == '':
            tkMessageBox.showinfo("sorry!", "请先点击选择MP4找到对应的pdf文件")
            return 0
        pdf_link_2_txt(pdf_path)
        txt_path = pdf_path.replace('.pdf', '.txt')
        download_youtube(txt_path)
        return 0

    def rename_it():
        dir_rename = link_contend.get()
        if dir_rename == '':
            tkMessageBox.showinfo("sorry!", "请先再输入框中键入文件夹地址")
            return 0
        rename_tag(dir_rename)
        return 0

    def download():
        youtube_link = link_contend.get()
        if youtube_link == '':
            tkMessageBox.showinfo("sorry!", "请先在输入框中键入YouTube地址")
            return 0
        youtube_dl_cmd = 'youtube-dl -f best ' + youtube_link + ' --external-downloader aria2c --external-downloader-args "-x 16  -k 1M"'
        info_entry.insert(1.0, '\nipv6下载：\n', 'a')
        info_entry.insert(1.0, youtube_dl_cmd, 'a')
        os.system(youtube_dl_cmd)
        return 0

    def downloadXXnet():
        youtube_link = link_contend.get()
        if youtube_link == '':
            tkMessageBox.showinfo("sorry!", "请先在输入框中键入YouTube地址")
            return 0
        youtube_dl_cmd = 'youtube-dl --no-check-certificate  --proxy 0.0.0.0:8087 -f 22 ' + youtube_link
        info_entry.insert(1.0, '\nXX-net下载：\n', 'a')
        info_entry.insert(1.0, youtube_dl_cmd, 'a')
        os.system(youtube_dl_cmd)
        return 0

    def generatePart2GIF():
        timestamp = nowTimeStr()
        if os.path.isfile('./split02_pic_water.mp4'):
            video_path = './split02_pic_water.mp4'
        else:
            video_path = './split01_pic_water.mp4'
        info_entry.insert(1.0, '选择视频\n：', 'a')
        info_entry.insert(1.0, video_path, 'a')
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        # print new_video_path
        if os.path.isfile(video_path):
            os.rename(video_path, new_video_path)
            ffmpeg_cmd = 'ffmpeg -ss 00:00:11 -t 00:00:01 -i ' + new_video_path + ' -r 1 -s 1440*810 -f gif ' + timestamp + '.gif'
            info_entry.insert(1.0, '生成GIF\n：', 'a')
            info_entry.insert(1.0, ffmpeg_cmd, 'a')
            os.system(ffmpeg_cmd)
            if_no_create_it(video_path)
            os.rename(new_video_path, video_path)
            os.rename(timestamp + '.gif', video_path.replace(video_format, 'gif'))
            info_entry.insert(1.0, '生成GIF\n：', 'a')
            info_entry.insert(1.0, video_path.replace(video_format, 'gif'), 'a')
        return 0

    def picPart1Mark():
        start = time.time()
        timestamp = nowTimeStr()
        for item in range(7):
            video_path = './split0' + str(item) + '.mp4'
            if os.path.isfile(video_path):
                video_format = video_path.split('.')[-1]
                new_video_path = timestamp + '_mark.' + video_format

                os.rename(video_path, new_video_path)
                split_first = 'ffmpeg -ss 00:00:00 -t 00:00:20 -i ' + new_video_path + ' -strict -2  -vcodec copy -y split1.mp4'
                os.system(split_first)
                split_second = 'ffmpeg -ss 00:00:20  -i ' + new_video_path + ' -strict -2  -vcodec copy -y split2.mp4'
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
                if_no_create_it(video_path)
                os.rename(new_video_path, video_path)
                os.remove('split1.mp4')
                os.remove('split0.mp4')
                os.remove('split2.mp4')
                os.remove(video_path)
        end = time.time()
        info_entry.insert(1.0, 'watermarking...\n：%.0f s\n' % (end - start), 'a')
        return 0

    def split_8_video():
        timestamp = nowTimeStr()
        video_path = link_contend.get()
        if video_path == '':
            tkMessageBox.showinfo("sorry!", "请输入地址或者当前文件夹有MP4视频文件")
            return 0
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        os.rename(video_path, new_video_path)
        cmd_line = "ffmpeg -ss 00:00:00 -t 00:14:40 -i " + new_video_path + "  -strict -2 -vcodec copy -acodec copy -y " + "split01.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:14:40  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:40 -y " + "split02.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:29:20  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:40 -y " + "split03.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:44:00  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:40 -y " + "split04.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:58:00  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:40 -y " + "split05.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 01:12:40  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:40 -y " + "split06.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 01:27:20  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -y " + "split07.mp4"
        os.system(cmd_line)
        for item in range(7):
            file_path_name = 'split0' + str(item + 1) + '.mp4'
            if os.path.isfile(file_path_name):
                if get_file_size(file_path_name) < 10000000:
                    os.remove(file_path_name)
        return 0

    def choose():
        filename = tkFileDialog.askopenfilename(initialdir='/home/zhangxulong/Downloads/',
                                                filetypes=[('mp4', '*.mp4'), ('pdf', '*.pdf'), ('ALL', '*.*')])
        link_contend.set(filename)
        info_entry.insert(1.0, '选择文件：\n', 'a')
        info_entry.insert(1.0, filename, 'a')
        return 0

    def emptyIt():
        link_contend.set('')
        info_entry.insert(1.0, '清空输入框：\n', 'a')
        info_entry.insert(1.0, '', 'a')
        return 0

    def vidolM3U8partDOWN():
        M3U8 = link_contend.get()
        if M3U8 == '':
            tkMessageBox.showinfo("sorry!", "请先输入M3U8地址")
            return 0
        duration = probe_duration(M3U8)
        end = '00:10:00'
        time_part = ['00:00:00', '00:10:00', '00:20:00', '00:30:00', '00:40:00', '00:50:00', '01:00:00', '01:10:00',
                     '01:20:00', '01:30:00', '01:40:00', '01:50:00', '02:00:00', ]
        for item in time_part:
            if item < duration[:-3]:
                ffmpeg_cmd = 'ffmpeg -ss ' + item + ' -t ' + end + ' -i "' + M3U8 + '" -c copy -bsf:a aac_adtstoasc -y ' + item.replace(
                    ':', '.') + '_' + end.replace(':', '.') + '.mp4'
                print ffmpeg_cmd
                info_entry.insert(1.0, '\nM3U8下载\n', 'a')
                info_entry.insert(1.0, ffmpeg_cmd, 'a')
                os.system(ffmpeg_cmd)

        return 0

    def vidolM3U8ZD():
        M3U8 = link_contend.get()
        if M3U8 == '':
            tkMessageBox.showinfo("sorry!", "请先输入M3U8地址")
            return 0
        ffmpeg_cmd = 'ffmpeg -ss 00:00:00 -i "' + M3U8 + '" -c copy -bsf:a aac_adtstoasc -y ' + nowTimeStr() + '.mp4'
        print ffmpeg_cmd
        info_entry.insert(1.0, '\nM3U8下载\n', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        return 0

    def vidolM3U8ZDwithStart():
        M3U8 = link_contend.get()
        if M3U8 == '':
            tkMessageBox.showinfo("sorry!", "请先输入开始时间@#持续时间@#M3U8地址")
            return 0
        start = M3U8.split('@#')[0]
        end = M3U8.split('@#')[1]
        M3U8 = M3U8.split('@#')[2]
        ffmpeg_cmd = 'ffmpeg -ss ' + start + ' -t ' + end + ' -i "' + M3U8 + '" -c copy -bsf:a aac_adtstoasc -y ' + start.replace(
            ':', '.') + '_' + end.replace(':', '.') + '.mp4'
        print ffmpeg_cmd
        info_entry.insert(1.0, '\nM3U8下载\n', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        return 0
    def vidolM3U8playwithStart():
        time_str=nowTimeStr()

        M3U8 = link_contend.get()
        if M3U8 == '':
            tkMessageBox.showinfo("sorry!", "请先输入开始时间@#持续时间@#M3U8地址")
            return 0

        end = '01:00:00'
        ffmpeg_cmd = 'ffmpeg  -t ' + end + ' -i "' + M3U8 + '" -c copy -y ' + time_str + '.mp4'
        print ffmpeg_cmd
        info_entry.insert(1.0, '\nM3U8下载\n', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        return 0
    def playVidolM3U8ZD():
        M3U8 = link_contend.get()
        if M3U8 == '':
            tkMessageBox.showinfo("sorry!", "请先输入M3U8地址")
            return 0
        ffmpeg_cmd = 'ffplay  "' + M3U8 + '"'
        print ffmpeg_cmd
        info_entry.insert(1.0, '\nM3U8下载\n', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        return 0

    def find_vedeo():
        for roots, dirs, names in os.walk('.' + SEP):
            for name in names:
                if '.mp4' in name:
                    video_path = os.path.join(roots, name)
                    link_contend.set(video_path)
                else:
                    info_entry.insert(1.0,
                                      '\nno mp4 in current dir',
                                      'a')
                    # root.quit()
        return 0

    def find_video_or_downIt():
        link_or_path = link_contend.get()
        if '.m3u8?' in link_or_path:
            vidolM3U8ZD()
        elif 'youtu' in link_or_path:
            download()
        else:
            print 'error:'
        find_vedeo()
        return 0

    def oneClick():
        find_video_or_downIt()
        split_8_video()
        picPart1Mark()
        generatePart2GIF()
        return 0

    root = Tk()
    root.title('AcFun上传daleloogn下载编辑小工具@咻')
    root.minsize(window_width, window_height)
    root.maxsize(window_width, window_height)
    menubar = Menu(root)
    # create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="选择文件", command=choose)
    filemenu.add_command(label="合并所有子文件", command=combine_all_video)
    filemenu.add_command(label="重命名子文件", command=rename_it)
    filemenu.add_command(label="v站直播下载", command=vidolM3U8playwithStart)
    filemenu.add_command(label="v站播放", command=playVidolM3U8ZD)
    filemenu.add_command(label="v站指定段落下载", command=vidolM3U8ZDwithStart)
    filemenu.add_command(label="v站固定分段下载", command=vidolM3U8partDOWN)
    filemenu.add_command(label="XX下载", command=downloadXXnet)
    filemenu.add_command(label="pdf下载", command=download_pdf_for_link)
    filemenu.add_command(label="清空输入", command=emptyIt)
    menubar.add_cascade(label="辅助", menu=filemenu)
    # display the menu
    root.config(menu=menubar)
    entry_link = Entry(root, width=ENTRY_WITDH)
    entry_link.grid(row=0, column=0, columnspan=3)
    link_contend = StringVar()
    entry_link.config(textvariable=link_contend)
    link_contend.set('')
    wechat_image = PhotoImage(file=wechat_path, height=150, width=154)
    wechat_label = Label(root, image=wechat_image)
    wechat_label.grid(row=1, column=0, columnspan=2, rowspan=5)
    button_one_click = Button(root, width=31, height=1, text='一键生成', command=oneClick)
    button_one_click.grid(row=1, column=2)
    info_entry = Text(root, width=21, height=3, )
    info_entry.grid(row=2, column=2, rowspan=3)
    info_entry.tag_config('a', foreground='blue')
    info_entry.config(font='helvetica 18')
    info_entry.insert(1.0,
                      '扫一扫，关注微信公众号【咻来了】\nxx-net下载供上外网使用\n选择文件\n输入m3u8地址\n需要批量重命名的文件夹地址\nVidol 下载需输入m3u8地址\n谷歌浏览器开发模式可过滤出来! ',
                      'a')
    mainloop()
    return 0


if __name__ == '__main__':
    downVideoGUI()
