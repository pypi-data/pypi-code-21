# -*- coding: utf-8 -*-

"""
wcc.utils
----------

工具函数模块。
"""
import os
import os.path
import base64
import calendar
import datetime
import time
#gif2mp4需要
import subprocess
from tinytag import TinyTag
from hashlib import md5
import hashlib
#subprocess.check_output输出的典型如下
#b'ExifToolVersion: 10.55\nFileName: gif2mp4.gif\nDirectory: .\nFileSize: 1858 kB\nFileModifyDate: 2017:06:27 04:33:34+08:00\nFileAccessDate: 2017:06:27 04:34:23+08:00\nFileInodeChangeDate: 2017:06:27 04:34:13+08:00\nFilePermissions: rw-rw-r--\nFileType: GIF\nFileTypeExtension: gif\nMIMEType: image/gif\nGIFVersion: 89a\nImageWidth: 400\nImageHeight: 293\nHasColorMap: Yes\nColorResolutionDepth: 8\nBitsPerPixel: 8\nBackgroundColor: 255\nAnimationIterations: Infinite\nXMPToolkit: Adobe XMP Core 5.3-c011 66.145661, 2012/02/06-14:56:27\nCreatorTool: Adobe Photoshop CS6 (Windows)\nInstanceID: xmp.iid:F7D68892A55711E6B8BCA26F653F0E33\nDocumentID: xmp.did:F7D68893A55711E6B8BCA26F653F0E33\nDerivedFromInstanceID: xmp.iid:F7D68890A55711E6B8BCA26F653F0E33\nDerivedFromDocumentID: xmp.did:F7D68891A55711E6B8BCA26F653F0E33\nFrameCount: 35\nDuration: 2.10 s\nImageSize: 400x293\nMegapixels: 0.117\n'
def parse_exif(file):
    devnull = open('/dev/null', 'w')
    args = [ "exiftool", "-S", file ]
    output = subprocess.check_output(args, stderr=devnull)
    #它返回的是bytes-like objcet
    output = str(output)
    output_array = output.split("\\n")
    #print(output_array)
    exif = {}
    for line in output_array:
        try:
            (tag, value) = line.split(':')
            tag = tag.strip()
            value = value.strip()
        except:
            continue
        exif[tag] = value
    return exif

def gif2mp4(giffile,overwrite=False,keep=True):
    if not giffile.endswith('.gif'):
        print("ignore "+giffile+" must endswith .gif")
        return False
    if not os.path.exists(giffile):
        print("not exist "+giffile)
        return False

    base_name = giffile[:-4]
    target = base_name + ".mp4"
    if os.path.exists(target) and not overwrite:
        print("local path has "+target)
        return True
    meta = parse_exif(giffile)
    #print(meta)
    duration = 0
    frame_count = 0
    try:
        #很多gif的duartion是0,通过exiftool -v 可以看出每帧之间的delay是0
        #个浏览器都会自动处理这个0延迟,改成100ms
        #Nearly all browsers change 0 ms and 10 ms delays to 100 ms. 
        #If a GIF uses delays of 0 ms or 10 ms, it will look identical in Firefox and IE. 
        #IE currently changes 20-50 ms delays to 100 ms. Firefox does not change them. 
        #If you see if GIF that looks too fast in Firefox, 
        #this is the range of delays they are likely using. Just tell whoever created the GIFs that they look stupid in Firefox and Mozilla, and they will probably change them to look correct in all browsers.
        #我们在这里如果没有延迟，我们就设为100ms
        #http://forums.mozillazine.org/viewtopic.php?t=108528
        #FrameCount这个属性Gif都有,这个确实能做到
        frame_count = int(meta["FrameCount"])
        if "Duration" not in meta:
            duration = float(frame_count)*0.1
        else:
            duration = float(meta["Duration"].replace("s","").strip())
    except Exception as err:
        print("Exception when parse_gif:"+giffile)
        print(err)
    if not frame_count:
        print("no frame_count for "+giffile)
        return False
    if not duration:
        print("no Duration for "+giffile)
        return False
    frame_rate = frame_count/duration
    ffmpeg_cmd = "ffmpeg -v quiet -r " + str(frame_rate) + " -i  " + giffile + " -crf 20 -tune film -preset veryslow -y -an " + target
    #print(ffmpeg_cmd)
    os.system(ffmpeg_cmd)
    if not keep:
        os.system("rm " + giffile)
    try:
        tinytag_class = TinyTag.get(target)
        duration = tinytag_class.duration
        print("gif2mp4 "+str(giffile)+" => "+str(target)+" lot:"+str(duration))
    except Exception as err:
        print("gif2mp4 "+str(giffile)+" => "+str(target)+" err:"+str(err))
        return False
    return True

def b64encode_as_string(data):
    return to_string(base64.b64encode(data))


def content_md5(data):
    """计算data的MD5值，经过Base64编码并返回str类型。
    返回值可以直接作为HTTP Content-Type头部的值
    """
    m = hashlib.md5(to_bytes(data))
    return b64encode_as_string(m.digest())


def md5_string(data):
    """返回 `data` 的MD5值，以十六进制可读字符串（32个小写字符）的方式。"""
    return hashlib.md5(to_bytes(data)).hexdigest()


#获取文件的MD5值，适用于小文件
def md5_file(filepath):
    if os.path.exists(filepath):
        try:
            f = open(filepath,'rb')
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            f.close()
            md5str = md5obj.hexdigest()
            return md5str
        except Exception as err:
            print(err)
            return None
    else:
        return None
