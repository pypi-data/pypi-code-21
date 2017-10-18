# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import os
from PIL import Image
import traceback

def __create_thumbs_pic(image,dst_w,dst_h,quality,dst_img,enlarge=False):
    result = True
    try:
        ori_w,ori_h = image.size
        if not enlarge:
            if (ori_w<dst_w):
                dst_w = ori_w
            if ori_h < dst_h:
                dst_h = ori_h

        if not dst_w:
            dst_w = 9999999999
        if not dst_h:
            dst_h = 9999999999

        dst_scale = float(dst_h) / dst_w #目标高宽比
        ori_scale = float(ori_h) / ori_w #原高宽比

        if ori_scale >= dst_scale:
            #原图过高。目标图片保留其高度
            height = dst_h
            width = int(float(height)/ori_scale)
        else:
            #过宽
            width = dst_w
            height = int(float(width)*ori_scale)

        if  enlarge:
            if width < dst_w:
                newWidth = dst_w
            if height < dst_h:
                newHeight = dst_h

        image.thumbnail((width,height))
        image.convert('RGB').save(dst_img,quality=quality)
    except:
        result = False
        print(traceback.format_exc())
    return result

def __create_small_crop_pic(image,dst_w,dst_h,quality,dst_img,enlarge=False):
    '''从文件创建小图片，指定图片宽度，高度，保存文件名
       需要对图片进行压缩和剪切，保证最优质量
    '''
    result = True
    try:
        path,filename = os.path.split(dst_img)
        if not os.path.exists(path):
            os.makedirs(path)

        ori_w,ori_h = image.size
        if not enlarge:
            if (ori_w<dst_w):
                dst_w = ori_w
            if ori_h < dst_h:
                dst_h = ori_h


        dst_scale = float(dst_h) / dst_w #目标高宽比
        ori_scale = float(ori_h) / ori_w #原高宽比

        if ori_scale >= dst_scale:
            #过高
            width = ori_w
            height = int(width*dst_scale)

            x = 0
            y = (ori_h - height) / 3

        else:
            #过宽
            height = ori_h
            width = int(height/dst_scale)

            x = (ori_w - width) / 2
            y = 0

        #裁剪
        box = (x,y,width+x,height+y)

        #这里的参数可以这么认为：从某图的(x,y)坐标开始截，截到(width+x,height+y)坐标
        #所包围的图像，crop方法与php中的imagecopy方法大为不一样
        newIm = image.crop(box)

        #压缩
        ratio = float(dst_w) / width
        newWidth = int(round(width * ratio))
        newHeight = int(round(height * ratio))

        if float(newWidth)/dst_w > 0.95:
            newWidth=dst_w
        if float(newHeight)/dst_h>0.95:
            newHeight=dst_h

        if  enlarge:
            if newWidth < dst_w:
                newWidth = dst_w
            if newHeight < dst_h:
                newHeight = dst_h

        im = newIm.resize((newWidth, newHeight), Image.ANTIALIAS)
        im = im.convert('RGB')
        im.save(dst_img, quality=quality)
    except:
        result = False
        print(traceback.format_exc())
    return result

def create_small_pic(im,dst_w,dst_h,quality,dst_img,is_thumbnails=False,enlarge=False):
    if is_thumbnails or not dst_h or not dst_w:
        result = __create_thumbs_pic(im,dst_w,dst_h,quality,dst_img,enlarge=enlarge)
    else:
        result = __create_small_crop_pic(im,dst_w,dst_h,quality,dst_img,enlarge=enlarge)
    return result

def create_small_pic_from_file(file,dst_w,dst_h,quality,dst_img,is_thumbnails=False,enlarge=False):
    '''从文件创建小图片，指定图片宽度，高度，保存文件名
       需要对图片进行压缩和剪切，保证最优质量
    '''
    path,filename = os.path.split(dst_img)
    if not os.path.exists(path):
        os.makedirs(path)

    im = Image.open(file)
    result = create_small_pic(im,dst_w,dst_h,quality,dst_img,is_thumbnails=is_thumbnails,enlarge=enlarge)
    return result

def resize(file,width):
    return create_small_pic_from_file(file,dst_w=width,dst_h=0,quality=95,dst_img=file,is_thumbnails=True,enlarge=False)


if __name__ == '__main__':
    import urllib2
    import cStringIO
    #url='http://127.0.0.1:8000/up/date/2017/01/10/148403138636256.jpg'
    #req = urllib2.Request(url)
    #f = cStringIO.StringIO(urllib2.urlopen(req).read())
    #f=open('d:/2.jpg')
    #create_small_pic_from_file(f,400,0,100,'d:/1.jpg',is_thumbnails=True)
    resize('d:/2.jpg',600)
