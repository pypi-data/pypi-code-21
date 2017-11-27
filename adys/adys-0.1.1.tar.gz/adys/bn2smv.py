# -*- coding: utf-8

from IPython.display import display, FileLink

import sys
import re

from .utils import *

modes = [
    "sync",
    "async",
    "general"
]


def bn2smv(bnfile, mode, init=None, name=None):
    assert mode in modes, "Le dernier argument doit être parmis %s" % " ".join(modes)

    hide = False
    if isinstance(bnfile, dict):
        defs = bnfile
        if not name:
            name = "tmpbn"
            hide = True
    else:
        name = name or bnfile.replace(".bn", "")
        defs = read_bn(bnfile)

    smvfile = "%s-%s.smv" % (name, mode)

    dom = list(sorted(defs.keys()))
    udom = ["u%s" % n for n in dom]

    def var(n):
        if isinstance(n, int):
            return "x%d" % n
        return n

    lines = ["MODULE main"]
    lines.append("VAR")
    lines.append("-- composants")
    for i in dom:
        lines.append("%s: boolean;" % var(i))
    lines += ["","-- variables de mise a jour"]
    if mode == "general":
        for u in udom:
            lines.append("%s: boolean;" % u)
    if mode == "async":
        lines.append("u: {START,%s};" % ",".join(udom))
    lines.append("ASSIGN")
    for i in dom:
        if mode == "sync":
            lines.append("next(%s) := f%s;" % (var(i),i))
        elif mode == "async":
            lines.append("next(%s) := case u=u%s: f%s; TRUE: %s; esac;" \
                            % (var(i),i,i,var(i)))
        elif mode == "general":
            lines.append("next(%s) := case u%s: f%s; TRUE: %s; esac;" \
                            % (var(i),i,i,var(i)))
    if mode == "async":
        lines.append("next(u) := {%s};" % ",".join(udom))
    lines += ["","-- Definition du reseau"]
    lines.append("DEFINE")
    for d in sorted(defs.items()):
        lines.append("f%s := %s;" % d)
    lines += ["","","-- regles internes"]
    lines.append("FIXEDPOINTS := %s;" \
        % (" & ".join(["%s = f%s" % (var(i),i) for i in dom])))
    lines.append("TRANS")
    lines.append("  FIXEDPOINTS")
    for i in dom:
        lines.append("| next(%s) != %s" % (var(i),var(i)))
    if mode == "async":
        lines.append("| next(u) != u")
    elif mode == "general":
        for u in udom:
            lines.append("| next(%s) != %s" % (u,u))
    lines.append(";")
    if mode == "async":
        for i in dom:
            lines.append("FAIRNESS u=u%s | FIXEDPOINTS;" % i)
            lines.append("COMPASSION (f%s!=%s, f%s!=%s&u=u%s);" \
                        % (i,var(i),i,var(i),i))
    elif mode == "general":
        for i in dom:
            lines.append("FAIRNESS u%s | FIXEDPOINTS;" % i)
            lines.append("COMPASSION (f%s!=%s, f%s!=%s&u%s);" \
                        % (i,var(i),i,var(i),i))
    if mode == "async":
        lines.append("INIT u=START;")
    elif mode == "general":
        lines.append("INIT !(%s);" % ("|".join(udom)))
    lines.append("")
    lines.append("-- INIT XXXX;")
    lines.append("-- CTLSPEC XXXX;")
    lines.append("-- LTLSPEC XXXX;")
    lines.append("")

    open(smvfile, "w").write("\n".join(lines))
    if not hide:
        display(FileLink(smvfile, url_prefix="../edit/"))

    if init is not None:
        for n in init:
            assert n in defs, "Nœud %s inconnu" % repr(n)
        smv_init = []
        for n in sorted(defs):
            smv_init.append("%s%s" % ("!" if n not in init else "" ,var(n)))
        append_line(smvfile, "INIT %s;" % (" & ".join(smv_init)))

    return smvfile


