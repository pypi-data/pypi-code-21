# coding:utf-8


class VarNotExist(Exception):
    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "Var <%s> not defined." % self.varname
