import json
import os
from terminal import white
from . import config
import re
usr_home = os.path.expanduser('~')
cfg_dir = os.path.join(usr_home, '.batchcompute')

def save(arr, col, title):

    cli_path = os.path.join(cfg_dir, 'clicache_%s.json' % title)

    t = []
    for n in arr:
        if(n.get(col)):
            t.append(n[col])

    s = json.dumps({'data':t, 'title':title})
    with open(cli_path, 'w') as f:
        f.write(s)

def get_index(index, title):
    cli_path = os.path.join(cfg_dir, 'clicache_%s.json' % title)

    if(os.path.exists(cli_path)):
        with open(cli_path, 'r') as f:
            obj = json.loads(f.read())
        if obj.get('title') == title:
            arrlen = len(obj.get('data'))

            if index > arrlen:
                print(white('%s > %s(cache length), use %s' % (index, arrlen, arrlen)))
                index = arrlen-1
            elif index < 1:
                print(white('%s < 1, use 1' % index))
                index = 0
            else:
                index -= 1

            return obj['data'][index]
    return None


def get(id, title, needCheckGod=False):

    if needCheckGod and not config.isGod() and re.match(r'^[0-9]+$', id):
        raise Exception('Invalid id: %s' % id)

    try:
        i = int(id)
        v = get_index(i, title)
        return v or id
    except:
        return id