# -*- coding: utf-8

from IPython.display import display, FileLink

import re

def create_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    display(FileLink(filename, url_prefix="../edit/"))
    return filename

def append_line(filename, line, quiet=True):
    with open(filename, "a") as f:
        f.write("%s\n" % line)
    if not quiet:
        print("Ligne '%s' ajoutée à la fin du fichier %s" % (line, filename))

re_fline = re.compile("\\bf([\\w\\d_]+)\\s*:=\\s*([\\sx\\w\\d_+&!|()TRUEFALSE]+)\s*;")
re_int = re.compile("^\\d+$")

def parse_bn(content):
    content = re.sub("\\s","",content.strip())
    defs = re_fline.findall(content)
    data = "".join(["f%s:=%s;" % d for d in defs])
    if data != content:
        raise Exception("Invalid syntax")

    def typekey(kv):
        (k,v) = kv
        if re_int.match(k):
            k = int(k)
        return (k,v)

    return dict(map(typekey, defs))

def read_bn(bnfile):
    with open(bnfile) as f:
        return parse_bn(f.read())

