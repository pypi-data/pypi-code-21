from __future__ import print_function

from tellurium import (
    antimonyConverter,
    inlineOmex,
    executeInlineOmex,
    exportInlineOmex,
    )

import tellurium as te
set_model = te.__set_model
from roadrunner import RoadRunner
import re

# http://stackoverflow.com/questions/28703626/ipython-change-input-cell-syntax-highlighting-logic-for-entire-session
import IPython
#js = "IPython.CodeCell.config_defaults.highlight_modes['magic_fortran'] = {'reg':[/^%%fortran/]};"
#IPython.core.display.display_javascript(js, raw=True)

from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)

@magics_class
class teMagics(Magics):
    def contentIsEmpty(self, content):
        '''Checks whether content (of a cell) is either empty or consists solely of whitespace.'''
        whitespace = re.compile(r'^[\s \t\r\n]*$')
        if whitespace.match(content) != None:
            return True
        else:
            return False

    @cell_magic
    def crn(self, line, cell):
        "Defines a chemical reaction network (CRN) in Antimony syntax"

        if self.contentIsEmpty(cell):
            print('Cell body appears to be empty/whitespace')
            return

        # convert cell content (Antimony) to raw SBML
        module,sbml_str = antimonyConverter().antimonyToSBML(cell)

        # override name?
        if line:
            if module == '__main':
                module = line
            elif module != line:
                raise RuntimeError('Conflicting names for model: {} vs {}.'.format(module, line))

        set_model(module, RoadRunner(sbml_str))
        print("Success: Model can be accessed via variable {}".format(module))
        if module == '__main':
            print('Consider enclosing your code in a model definition to name your model:\nmodel name_of_your_model()\n  ...\nend')

        # add RoadRunner instance to global namespace
        import sys
        sys.modules['builtins'].__dict__[module] = te.model(module)

    @cell_magic
    def omex(self, line, cell):
        "Defines a COMBINE archive in this cell"

        if self.contentIsEmpty(cell):
            print('Cell body appears to be empty/whitespace')
            return

        savefile = None
        savecmd = re.compile('^\s*save\((.*)$').match(line)
        if savecmd != None:
            rest = savecmd.group(1)
            # find first occurance of non-escaped closing paren
            filematch = re.compile(r'^(.*[^\\])\)').match(rest)
            if filematch != None:
                savefile = filematch.group(1)

        if not savefile:
            executeInlineOmex(cell)
        else:
            exportInlineOmex(cell, savefile)
            print('Exported to {}'.format(savefile))
