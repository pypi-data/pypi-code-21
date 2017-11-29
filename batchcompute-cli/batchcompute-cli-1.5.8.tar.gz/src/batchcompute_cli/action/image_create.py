
# -*- coding:utf-8 -*-

from ..util import client
from terminal import green
import json

def create_image(imageName, ecsImageId, platform='Linux', description='', show_json=False):

    desc = {}
    desc['Name'] = imageName
    desc['EcsImageId'] = ecsImageId
    desc['Platform'] = platform
    desc['Description'] = description

    if not ecsImageId.startswith('m-'):
        raise Exception('Invalid ecsImageId')

    if show_json:
        print(json.dumps(desc, indent=4))
        return

    result = client.create_image(desc)

    if result.StatusCode==201:
        print(green('Image create: %s' % result.Id))


def trans_platform(platform='Linux'):
    platform = platform.lower()
    if platform=='linux':
        return 'Linux'
    elif platform=='windows':
        return 'Windows'
    else:
        raise Exception('platform should be "linux" or "windows"')
