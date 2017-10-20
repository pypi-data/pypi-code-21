# -*- coding: utf-8 -*-
from terminal import blue
from .externals.command import Command

from . import const,i18n_util
from .action import image ,image_create,image_delete


COMMAND = const.COMMAND
CMD = const.CMD

IMG_ID = 'img-xxxxxx'
INS_TYPE = 'ecs.s3.large'

VERSION = const.VERSION

IS_GOD = const.IS_GOD


# SPLITER = '\n    --%s' + ('-' * 40)

MSG=i18n_util.msg()


def delete():
    # delete image
    cmd_del_image = Command('delete_image', alias=['di'],
                            arguments=['imageId'],
                            description=MSG['delete_image']['description'],
                            usage='''Usage: %s delete_image|di [imageId,imageId2,imageId3...] [option]

            Examples:

                1. %s di img-idxxx1                # delete image with imageId
                2. %s di img-idxxx1,img-idxxx2 -y  # delete images in silent mode''' % (COMMAND, CMD, CMD),
                            func=image_delete.del_image)
    cmd_del_image.option("-y, --yes", MSG['delete_image']['option']['yes'])
    return cmd_del_image

def create():
    # create image
    cmd_create_image = Command('create_image', alias=['ci'],
                               description=MSG['create_image']['description'],
                               arguments=['imageName', 'ecsImageId'],
                               usage='''Usage: %s create_image|ci [option] <imageName> <ecsImageId>

            Examples:

                1. %s ci myimage1 m-xxsxxx
                2. %s ci myimage1 m-xxsxxx  -p Linux -d 'this is description' ''' % (COMMAND, CMD, CMD),
                               spliter='\n    -----%s----------------' % blue('create, update, delete'),
                               func=image_create.create_image)
    cmd_create_image.option("-p, --platform [platform]", MSG['create_image']['option']['platform'],
                            resolve=image_create.trans_platform)
    cmd_create_image.option("-d, --description [description]",
                            MSG['create_image']['option']['description'])
    cmd_create_image.option("--show_json",
                            MSG['create_image']['option']['show_json'])
    return cmd_create_image

def images():
    cmd_images = Command('image', alias=['img', 'i'],
                         arguments=['imageId'],
                         description=MSG['image']['description'],
                         usage='''Usage: %s image|img|i [imageId|No.] [option]

    Examples:

        list images:
          1. %s i

        get image info:
          1. %s i img-6ki4fsea5ldlvsupbrk01q
          2. %s i 1''' % (COMMAND, CMD, CMD, CMD),
                         func=image.all)


    cmd_images.option('-d,--description', MSG['image']['option']['description'])
    cmd_images.option('--show_json', MSG['image']['option']['show_json'], visible=IS_GOD)

    return cmd_images

