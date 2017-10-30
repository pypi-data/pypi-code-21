
from SpirentSLC import SLC

with SLC.init(host='localhost:9005') as slc:
    print('============== Prolects list ==============')
    print(slc.list())

    print('============== NativePyLib project resources ==============')
    proj = slc.open('NativePyLib')
    print(proj.list(parameter_file=True, response_map=True))

    print('============== Quick calls ==============')
    print(proj.dut_ffsp.list())
    print('===> access the list of parameters for a specific QuickCall')
    print(proj.dut_ffsp.list('init_routes'))

    print('============== Topology ==============')
    with proj.ServerAndPC_tbml.server1.cmd.open() as cmd_session:
        print(cmd_session.command('help'))

    with proj.ServerAndPC_tbml.server1.Process.open() as process_session:
        print(process_session.list())

