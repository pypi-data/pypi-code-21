from ..const import CMD
from batchcompute.utils.functions import ConfigError
from terminal import Logger, white, blue, green,magenta,bold
import json
from ..util import config, client,formater,result_cache,list2table
from batchcompute.utils.jsonizable import BatchEncoder

log = Logger()

def all(imageId=None, description=False, show_json=False):
    if imageId:
        get(imageId, description, show_json)
    else:
        list(show_json)


def list(show_json=False):

    result = client.list_images()

    if show_json:
        print(json.dumps(result, indent=2, cls=BatchEncoder))
        return

    arr = formater.items2arr(result.get('Items'))

    result_len = len(arr)

    arr = formater.format_date_in_arr(arr, ['CreationTime'])

    result_cache.save(arr, 'Id', 'images')

    print('%s' % bold(magenta('Images:')))
    list2table.print_table(arr, ['Id', 'Name', 'EcsImageId', 'Platform','Type', 'CreationTime'])

    arrlen = len(arr)

    cache_str = white('(cache %s %s)' % (arrlen, 'rows' if arrlen > 1 else 'row'))
    print('%s %s' % (green('Total: %s' % result_len), cache_str))

    print(white('\n  type "%s i <Id|No.>" to show image detail' % (CMD)))
    print(white('\n  using "%s set -i <Id>" to set default image\n' % (CMD)))


def get(imageId, descOnly=False, show_json=False):

    imageId = result_cache.get(imageId, 'images')

    print(white('exec: bcs image %s' % imageId))
    result = client.get_image(imageId)


    if show_json:
        print(result)
        return

    if descOnly:
        print(result)
        return

    arr = [{
        'a': '%s: %s' % (blue('Id'), result.get('Id')),
        'b': '%s: %s' % (blue('Name'), result.get('Name')),
        'c': '%s: %s' % (blue('Platform'),'%s (%s)' % ( result.get('Platform'), result.get('Type')))
    }, {
        'a': '%s: %s' % (blue('EcsImageId'), result.get('EcsImageId')),
        'b': '%s: %s' % (blue('Created'), formater.from_now(result.get('CreationTime'))),
        'c': '%s: %s' % (blue('OwnerId'), '%s (%s)' % (result.get('OwnerId'), result.get('Type')))
    }]
    print('%s' % bold(magenta('Image:')))
    list2table.print_table(arr, ['a', 'b', 'c'], show_no=False, show_header=False)


    print(blue('Description:'))
    print(result.get('Description'))
