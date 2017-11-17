
from IPython.display import *

import subprocess

from .utils import *
from .bnutils import *
from .bn2smv import *
from .models import *

class CmdError(subprocess.CalledProcessError):
    def __str__(self):
        stderr = "\n%s" % self.stderr.decode() if self.stderr else None
        return "Command '%s' returned non-zero exit status %d%s\n" \
            % (" ".join(self.cmd), self.returncode, stderr)

def NuSMV(*args, **kwargs):
    quiet = kwargs.get("quiet", True)
    parse = kwargs.get("parse", False)
    parse_dict = kwargs.get("parse_dict", False)

    args = ["NuSMV"] + ["-dcx"] + list(args)
    try:
        output = subprocess.check_output(args, stderr=subprocess.PIPE).decode().strip()
    except subprocess.CalledProcessError as e:
        # backward compatible 'raise e from None'
        if sys.version_info[0] >= 3:
            e = CmdError(e.returncode, e.cmd, e.output, e.stderr)
        e.__cause__ = None
        raise e
    ret = None
    if quiet or parse:
        lines = output.split("\n")
        if quiet:
            lines = [l for l in lines if l \
                    and not l.startswith("WARNING") \
                    and not l.startswith("***")]
        if parse:
            if parse_dict:
                ret = {}
            else:
                ret = []
            for line in lines:
                if not line.startswith("-- specification "):
                    continue
                parts = line.split()
                result = True if parts[-1] == "true" else False
                if parse_dict:
                    prop = " ".join(parts[2:-2])
                    ret[prop] = result
                else:
                    ret.append(result)
        output = "\n".join(lines)
    if not parse or not quiet:
        print(output)
    return ret


def svg_of_graph(g):
    return g.to_pydot().create_svg().decode()

def setup_ipython():
    try:
        ip = get_ipython()
    except NameError:
        return
    # nxgraph to svg
    svg_formatter = ip.display_formatter.formatters["image/svg+xml"]
    svg_formatter.for_type(graph, svg_of_graph)

setup_ipython()

