# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

from SpirentSLC import SLC

with SLC.init(host='localhost:9005', itar_path='itars/') as slc:
    proj = slc.open('NativePyLib')

    print('> 2. The Python user will start by connecting to one of the below iTest endpoints.  This will be known as an endpoint session.')
    print('>    - A running instance of the iTest GUI co-existing on the local machine or on a remote host over TCP/IP')
    print('>    - A temporal Velocity agent instance which is auto-launched by this library')
    print('> 4. Upon connect, the returned object would contain attributes about the iTest GUI or Agent instance.')
    print('-->')
    print(proj.dut_ffsp.agent)
    print('')

    print('> 5a. The Python user can specify a parameter file in a project or from the filesystem for the endpoint session (equivalent to setting a \'global parameter file\' in terms of setting parameter key priorities)')
    print('Without parameters:')
    print('-->')
    with proj.test_params_ffsp.open() as params_session:
        print(params_session.command('read 2'))

    print('With project://NativePyLib/test_parameters/parameters.ffpt')
    print('-->')
    with proj.test_params_ffsp.open(parameter_file='project://NativePyLib/test_parameters/parameters.ffpt') as params_session:
        print(params_session.command('read 2'))

    print('> 5c. The Python user can specify a local iTest topology file in a project to be used in the endpoint session')
    print('> 6. The Python user then attempts to open one or more test sessions (session profiles in projects or a topology devices\' sessions)')
    print('> 8. The Python user can issue native session-level commands using object oriented method syntax over the connection. These are built-in commands associated with open test sessions.')
    print('Command session \'help\' command:\n-->')
    cmd_session = proj.ServerAndPC_tbml.server1.cmd.open()
    print(cmd_session.command('help'))
    prompt_session = proj.dut_ffsp.open()
    print('Prompt  session \'help\' command:\n-->')
    print(prompt_session.command('help'))
    cmd_session.close()
    prompt_session.close()
    print('')

    print('> 9. The Python user can issue quickcalls associated with the opened test session using object oriented method syntax.')
    print('list of quickcalls:\n-->')
    print(proj.dut_ffsp.list())
    print('')

    print('Access the list of parameters for a specific QuickCall:\n-->')
    print(proj.dut_ffsp.list('init_routes'))
    print('')

    print('Topology session quickcalls:\n-->')
    with proj.ServerAndPC_tbml.server1.Process.open() as process_session:
        print(process_session.list())
        print(process_session.to_parent_dir())
    print('')