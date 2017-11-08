from terminal import blue,magenta
from .externals.command import Command
from .action import template_gen
from . import i18n_util

from .const import CMD,COMMAND


MSG=i18n_util.msg()


def gen():

    cmd = Command('gen',
                 arguments=['location'],
                 description=MSG['template_gen']['description'],
                  spliter='\n    -----%s%s----------------' % (blue('template'), magenta('(New)')),
                 usage='''Usage: %s gen [location] [option]

      location is optional, default: './'.

    Examples:

        1. %s gen ./demo -t gatk                 # gen a native job project using gatk template to ./demo ''' % (
                             COMMAND, CMD),
                             func=template_gen.gen)
    cmd.option("-t, --type <type>",
                          MSG['template_gen']['option']['type'], resolve=template_gen.trans_type)

    return cmd

