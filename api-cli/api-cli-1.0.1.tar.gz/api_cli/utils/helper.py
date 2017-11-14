#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/utils
* file   : helper.py
* time   : 2017/10/27
'''
#--------------------#
import configparser, codecs
import base
#--------------------#

#--------------------#
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()
#--------------------#

#--------------------#
def get_config(file, *args, **kwargs):
    cfg = configparser.ConfigParser(*args, **kwargs)
    if file:
        cfg.read(file)
    return cfg
#----------#
def set_config(file, cfg):
    fp = codecs.open(file, 'w', 'utf-8')
    cfg.write(fp)
    fp.close()
#--------------------#

#--------------------#
def union_dict(dict1, dict2):
    data = dict1 or {}
    for k, v in dict2.items():
        data[k] = v
    return data
#--------------------#

#--------------------#
def get_space(num):
    space = ''
    for i in range(0, num):
        space += ' '
    return space
#----------#
def get_input_yes(tip, default=False, space=0):
    prefx = get_space(space)
    tail = ''
    if default:
        tail = ' [Y/n]: '
    else:
        tail = ' [y/N]: '
    #
    ret = default
    dat = raw_input(prefx + tip + tail)
    if dat == 'y' or dat == 'Y':
        ret = True
    elif dat == 'n' or dat == 'N':
        ret = False
    return ret
#--------------------#

#--------------------#
def apply_templete(info, templete):
    try:
        text = templete.replace(u'{#}', '#')
        for k,v in info.items():
            text = text.replace(u'{'+k+u'}', v)
        return text
    except:
        pass
    return u''
#--------------------#

#--------------------#
def git_clone(git, path):
    cmd = 'git clone "%s" "%s"' % (git, path)
    ret = base.call(cmd)
    return (ret == 0)
#--------------------#

#--------------------#
def str_get_line_pos(s, line):
    pb = pe = l = 0
    lt = ''
    while True:
        pe,rt = base.find_return(s, pb)
        if pe is not -1:
            if line == -1:
                l += 1
                pb = pe + len(rt)
                lt = rt
                continue
            if l == line:
                return [pb, pe, lt, rt]
            pb = pe + len(rt)
            lt = rt
            l += 1
        else:
            if line == -1 or l == line:
                return [pb, len(s), lt, rt]
            break
    #
    return None
#----------#
def str_replace_by_line(src, rpstr, fm=0, to=-1, linc=False, rinc=False):
    pb = str_get_line_pos(src, fm)
    pe = str_get_line_pos(src, to)
    if not pb or not pe:
        assert(False)
    pl = pb[0]
    pr = pe[1]
    if linc:
        pl -= len(pb[2])
    if rinc:
        pr += len(pe[3])
    return src[:pl] + rpstr + src[pr:]
#--------------------#
