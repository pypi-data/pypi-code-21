#
import sys
import argparse
import json
from pyesp.pyesp import ESP
from PyQt5.QtCore import QCoreApplication

__serial_config_path__ = 'data/serial/config.json'


def loadconfig():
    with open(__serial_config_path__, 'r') as f:
        data = json.loads(f.read())
        if not len(data.keys()):
            raise BaseException('serial port config file empty')
    return data


def saveconfig(data):
    jobj = json.dumps( data )
    with open(__serial_config_path__, 'w') as f:
        f.write(jobj)


def createArgParser():
    """ Create arguments cmd line parser """
    _prog = "pyesp"
    desctext = '"%s v%s"' % ( _prog, __version__ )
    epitext = 'Find more info visit http://hobby-research.at.ua ; https://github.com/LeftRadio/pyesp'

    try:
        opt = loadconfig()
        serialconfig = '%s,%s,%s,%s,%s,%s,%s' % ( \
            opt['portName'], opt['baudRate'], opt['dataBits'], \
            opt['parity'], opt['stopBits'],
            opt['flowControl'], opt['linedelay'] )
    except Exception as e:
        raise BaseException('error loading default serial port config file')

    parser = argparse.ArgumentParser( description = desctext,
                                      epilog = epitext,
                                      prog = _prog )

    parser.add_argument ( '-V', '--version', action='version',
                            help = '\tversion for tool',
                            version = __version__ )
    parser.add_argument ( '-a', '--api', dest = 'api_userfile', type = str,
                            default = '',
                            metavar = 'FILE',
                            help = '\t external api file' )
    parser.add_argument ( '-c', '--command', dest = 'command', type = str,
                            default = '',
                            metavar = 'CMD',
                            help = '' )
    parser.add_argument ( '-d', '--data', dest = 'data', type = str,
                            default = '',
                            metavar = 'DATA',
                            help = 'command data, ignored for "file*" commands' )
    parser.add_argument ( '-f', '--files', dest = 'files', type = str,
                            default = '',
                            metavar = 'LIST',
                            help = '' )
    parser.add_argument ( '-p', '--platform', dest = 'platform', type = str,
                            default = 'MPY',
                            metavar = 'PLT',
                            help = ( '\t platform for ESP - '
                                     '{ MPY, NODE } '
                                     '[default MPY]' ) )
    parser.add_argument ( '-s', '--serial', dest = 'serialconfig', type = str,
                            default = serialconfig,
                            metavar = 'PARAMS',
                            help = ( '\t serial port parametrs - '
                                     'NAME,BOUD,DATABITS,PARITY,STOPBITS,FLOW,LINEDELAY '
                                     '[default %s], '
                                     'linedelay is specified in milliseconds' % serialconfig ) )
    parser.add_argument( '-v', '--verbose', action='store_true', default = False,
                            help = ( '\t increase output verbosity '
                                     '[default False]') )
    return parser


readend = False

#
def read_callback(data):
    global readend
    if not readend:
        readend = ('END' in data)
    print(data)


def main():
    #
    global readend
    #
    parser = createArgParser()
    args = parser.parse_args()
    #
    if not len(sys.argv[1:]):
        parser.print_help()
        print('\r\nNo arguments, nothing remains :(, we leave...')
        return
    #
    try:
        sc = args.serialconfig.split(',')
        serialconfig = {
            'portName': str(sc[0]),
            'baudRate': int(sc[1]),
            'dataBits': int(sc[2]),
            'parity': int(sc[3]),
            'stopBits': int(sc[4]),
            'flowControl': int(sc[5]),
            'linedelay': int(sc[6]) }
    except Exception as e:
        raise BaseException('error in serial config parametrs')
    #
    esp = ESP( serialconfig, args.platform, args.api_userfile )
    #
    if args.files:
        if args.command == 'filewrite':
            pass
        elif args.command == 'fileread':
            pass

        for f in args.files.split(','):
            print('-'*120)
            print('read: ', f)
            print('-'*120)
            esp.send( args.command, name=f, data=args.data, callback=read_callback )
            while not readend:
                esp.processEvents()
            readend = False
    else:
        esp.send( args.command, data=args.data, callback=read_callback )
        while not readend:
            esp.processEvents()

    #
    saveconfig( esp.serialconfig )
    #
    print('--- Press ENTER to exit ---')
    input()
    sys.exit(True)


if __name__ == '__main__':
    main()
