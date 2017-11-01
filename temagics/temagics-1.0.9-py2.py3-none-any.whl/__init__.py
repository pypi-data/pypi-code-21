from .magics import teMagics
from .comm_handlers import convert_file_comm, save_file_comm, getNotebookLocation

__version__ = '1.0.9'

ip = get_ipython()
ip.register_magics(teMagics)
ip.kernel.comm_manager.register_target('convert_file_comm', convert_file_comm)
ip.kernel.comm_manager.register_target('save_file_comm', save_file_comm)

# with open('/tmp/nterout', 'a') as myfile:
#     myfile.write('finished registering magics and comms\n')
