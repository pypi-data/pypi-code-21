from ..util import client, util, config
from terminal import bold, magenta, white, blue, green,red, yellow, confirm


def delete(app_name, revision="", yes=False):
    arr = app_name.split(',')
 
    t = util.parse_id_arr(arr, 'apps', True)

    if yes:
        __batch_del(t, revision)
    else:
        msg = "Delete all these apps:\n%s \nAre you sure" % red('\n'.join(t))
        if len(t)==1 and revision!='':
            msg = "Delete this app revision:\n%s(revision=%s) \nAre you sure" % (red(t[0]), revision)

        try:
            if confirm(msg, default=False):
                __batch_del(t, revision)
        except KeyboardInterrupt:
            print('')
            return


def __batch_del(arr,revision=""):
    for item in arr:
        __del_app(item, revision if len(arr)==1 else '')


def __del_app(appName, revision=""):
    print(white('exec: bcs delete_app %s %s' % (appName,revision)))
    client.delete_app(appName, revision)
    print(green('done'))
