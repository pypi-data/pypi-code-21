from EvoDAG.command_line import params
from test_root import X, cl
from EvoDAG.utils import Inputs
import tempfile
import json
fname = tempfile.mktemp()
with open(fname, 'w') as fpt:
    for x, y in zip(X, cl):
        a = {k: v for k, v in enumerate(x)}
        a['klass'] = int(y)
        a['num_terms'] = len(x)
        fpt.write(json.dumps(a) + '\n')

inputs = Inputs()
X, y = inputs.read_data_json(fname)
        
# print("termine con el json")
# sys.argv = ['EvoDAG', '-C', '-Poutput.evodag', '--json',
#             '-e1', '-p3', '-r2', fname]
# params()
# os.unlink(fname)
# print(open('output.evodag').read())
# os.unlink('output.evodag')
# default_nargs()


