
from SpirentSLC import SLC

"""Open the native ssh session type directly, supplying required session profile information"""

with SLC.init(host='localhost:9005') as slc:
    # # Process session
    # with slc.sessions.process.open() as process:
    #     print(process.command('help'))

    # # Command Prompt session
    # with slc.sessions.cmd.open() as cmd:
    #     print(cmd.command('dir'))

    
    # # HTTP session
    with slc.sessions.http.open() as http:
        resp = http.command('get page http://spirent.com')

        print('show queries')
        # Use automatic queties or response map queries
        print(resp.queries())
        # Call for particular query
        print(resp.pragma())

    # Rest session test
    # with slc.sessions.rest.open(url='https://jsonplaceholder.typicode.com/') as s1:
    #     resp = s1.GET('/posts/1')
    #     print(resp.json)

    # SSH session using properties tree
    ssh = slc.sessions.ssh.open(properties = {
       'ipAddress':'velocity-itest3.xored.com',
       'user':'root',
       'password':'iRyLc4KQj80=',
       'TerminalProperties':{
               'prompts': [ { 'prompt1':{ 'Content':'root@velocity-itest3:~#' } }, { 'prompt2':{ 'Content':'root@velocity-itest3:/#' } } ]
           }
       })
    print(ssh.command('cd /'))