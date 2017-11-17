import logging
import argparse
import optparse
import shlex
from ast import literal_eval

import xcam

#
# def cmdline_get_options(cmdline = None, _defaults = None):
#     """
#     The command line parsing helper function that should be called from the
#     main() routine.
#
#     @param cmdline: if set, then this command line string will override the
#         console command line input. Useful for debugging.
#
#     @rtype: dict
#     @return: the options key value map
#     """
#
#     args = shlex.split(cmdline) if cmdline else None
#
#     parser = optparse.OptionParser(
#         usage="\n%prog [options]",
#         version="%prog 1.0"
#     )
#
#     choices = ["readout", "acquire", "init"]
#     parser.add_option("-e", "--execute",
#         dest="cmd",
#         type="choice",
#         choices=choices,
#         help="command the XCAM driver.[%s]" % str(choices)
#     )
#     parser.add_option("-n", "--bytes",
#         dest="bytes",
#         type="int",
#         help="number of bytes to readout"
#     )
#     parser.add_option("-r", "--rows",
#         dest="rows",
#         type="int",
#         default=1600,
#         help="number of rows"
#     )
#     parser.add_option("-c", "--cols",
#         dest="cols",
#         type="int",
#         default=4600,
#         help="number of columns"
#     )
#     parser.add_option("-i", "--inttime",
#         dest="inttime",
#         type="int",
#         default=4600,
#         help="number of columns"
#     )
#     parser.add_option("-o", "--output",
#         dest="output",
#         type="str",
#         default="data.raw",
#         help="the output image data file"
#     )
#     options = parser.parse_args(args)[0]
#
#     return options, parser


# # =============================================================================
# def init_logging(verbose = False):
#
#     f = "%(asctime)s %(levelname)-7s %(name)-8s"
#     f += " %(module)s.%(funcName)-20s"
#     f += " %(message)s"
#
#     h = logging.StreamHandler(sys.stdout)
#     h.setFormatter(logging.Formatter(f))
#
#     log = logging.getLogger("xcam")
#     log.addHandler(h)
#
#     if verbose:
#         log.setLevel(logging.DEBUG)
#     else:
#         log.setLevel(logging.INFO)


# # =============================================================================
# def main(cmdline=None):
#
#
#     opts = parser.parse_args()
#
#     log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
#
#     logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)-7s %(name)-20s %(funcName)-20s %(message)s')
#
#     logging.basicConfig()
#
#     opts, _parser = cmdline_get_options(cmdline)
#     if opts.cmd == 'readout':
#         n = opts.bytes
#         return XCam.Readout(n)

# from esapy.core import pyfits_ext
# from esapy.core import header

# # =============================================================================
# def test():
#     headers = header.Header()
#     headers['ADCTYPE'] = 'no desc'
#     headers.finalize()
#     headers['ADCTYPE'] = '14D'
#
#     rawdata = numpy.fromfile(DATA_FILE, dtype=numpy.uint16)
#     rawdata = rawdata & 0x3fff
#
#     fout = r'f:\data\CCD273-84-2-F15_11263-07-01_20130516_Card14bitCDS\test\test_062.fits'
#     data = XCam.Decode(rawdata, rows=4600, cols=4600, channels=2, nodeLocation="1234", nodeOrientation="NHBV", rdir=3)
#     pyfits_ext.save_data(fout, data, header=headers)
#     return
#
#     r = 4600
#     c = 4600
#     r2 = r / 2
#     c2 = c / 2
#     TL = data[ 0:r2,  0:c2]
#     TR = data[ 0:r2, c2:c ]
#     BR = data[r2:r,  c2:c ]
#     BL = data[r2:r,   0:c2]
#
#     BR = numpy.fliplr(BR)
#     BL = numpy.flipud(BL)
#
#     out = numpy.zeros((r, c)).astype(numpy.uint16)
#
#     out[ 0:r2,  0:c2] = BL # top left
#     out[ 0:r2, c2:c ] = TL # top right
#     out[r2:r,  c2:c ] = TR # bottom right
#     out[r2:r,   0:c2] = BR # bottom left
#     pyfits_ext.save_data(fout, out, header=headers)
#
# # =============================================================================
# def xcam_open(xc, seqFile, adcType="16Q", autoLoad=False, loadRack=False, async=False, voltFile=VOLT_FILE):
#     xc.open()
#     xc.init_usb_controller()
#     xc.init_rack(dspFile=seqFile, voltFile=voltFile)
#     xc.set_async_readout(async)
#     if autoLoad:
#         xc.load_rack()
#     if loadRack:
#         xc.load_rack_state()
#     xc.set_channels(adcType)


def run_server(opts):
    return


def execute(opts):

    if opts.readout:
        xcam.Readout.readout(opts.readout)
        return

    cam = xcam.XCam()
    cam.init_usb_controller()

    seq_file = opts.seq_file.format(**opts.__dict__)
    bias_file = opts.bias_file.format(**opts.__dict__)
    state_file = xcam.XCamConst.STATE_FILE

    if opts.build:
        pass

    if opts.init:
        cam.init_rack(state_file=state_file, dsp_file=seq_file, volt_file=bias_file)

    if opts.load:
        cam.load_seq(seq_file)

    if opts.load_rack:
        cam.load_rack_state()

    cam.set_async_readout(not opts.sync)
    cam.set_channels(opts.adc_type)

    if opts.power_off:
        cam.set_power(False)

    if opts.vclock:
        for entry in opts.vclock:
            key, val = entry.split('=', 1)
            matched = cam.voltages.match_key(key, xcam.CMD_CLOCK_VOLTAGE)
            if len(matched):
                adu = cam.voltages.find_by_key(matched[0])
                cam.set_voltage_clock(adu.address, float(val))

    if opts.vbias:
        for entry in opts.vbias:
            key, val = entry.split('=', 1)
            matched = cam.voltages.match_key(key, xcam.CMD_BIAS_VOLTAGE)
            if len(matched):
                adu = cam.voltages.find_by_key(matched[0])
                cam.set_voltage_bias(adu.address, float(val))

    if opts.address:
        for entry in opts.address:
            key, val = entry.split('=', 1)
            key = xcam.Param.find_key(key)
            if key:
                val = literal_eval(val)
                addr = getattr(xcam.Param, key)
                if addr == xcam.Param.addr_int_time:
                    cam.set_int_time(val)
                else:
                    cam.set_param(addr, val)

    if opts.power_on:
        cam.set_power(True)

    if opts.dump:
        for addr in range(0, 42):
            val = cam.clock_out_memory_location(addr)
            label = xcam.Param(addr)
            logging.info('Memory  : %3d (0x%02X) = %5d (0x%04X) %s' % (addr, addr, val, val, label))

    if opts.acquire:
        raw_data = cam.acquire(opts.rows, opts.cols, opts.expose_time)
        cols = cam.rack.get_param(xcam.Param.addr_cols)
        rows = cam.rack.get_param(xcam.Param.addr_rows)
        rdir = cam.rack.get_param(xcam.Param.addr_readout_dir)
        chns = cam.rack.get_param(xcam.Param.addr_channels)

        data = xcam.Readout.decode(raw_data, rows, cols, chns, rdir=rdir)
        xcam.Readout.save_data('test.fits', data)


def main():
    """ main entry point of script """

    # ini_file = 'mwir.ini'  # TODO: specific to mwir, use a default settings file
    #
    # # check if a configuration file was passed in and use it's default values
    # for key in ['-i', '--ini-file']:
    #     if key in sys.argv:
    #         ini_file = sys.argv[sys.argv.index(key) + 1]
    #
    # # gather all the default settings from the configuration file
    # settings = {}
    # if ini_file:
    #     if ExtendedInterpolation:
    #         cfg = ConfigParser(interpolation=ExtendedInterpolation())
    #     else:
    #         cfg = ConfigParser()
    #     cfg.read(ini_file)
    #     for section in cfg.sections():
    #         for key in cfg[section]:
    #             if section == 'bias':
    #                 settings[section] = settings.get(section, [])
    #                 settings[section].append('%s=%s' % (key.upper(), cfg[section][key]))
    #             else:
    #                 settings[key] = str(cfg[section][key])

    # define the argument parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', default=0, type=int, help='Run the application as a web server')

    parser.add_argument('-i', '--ini-file',
                        help='The .ini configuration file')

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='increase output verbosity')

    group = parser.add_argument_group('dsp')
    group.add_argument('-d', '--directory', default='../dsp',
                       help='DSP tim.asm source directory')
    group.add_argument('--seq-file', default='{directory}/seq.dex',
                       help='seq.dex file')
    group.add_argument('--bias-file', default='xcam_state_vtg_ccd47-20.txt',
                       help='seq.dex file')
    group.add_argument('--adc-type', default='16Q', choices=['16S', '16D', '16Q', '14S', '14D'])
    group.add_argument('--readout-dir', default=2,
                       help='0 <-- EFGH -->,1 --> 4Rev <--,2 <-- FG <--,3 --> EH -->')
    # group.add_argument('-s', '--sensor', choices=['mwir', 'leti', 'selex'],
    #                    help='the sensor id')

    group = parser.add_argument_group('viewer')
    group.add_argument('--viewer',
                       help='the ds9.exe or esaimage.py file location. Leave empty to disable this viewer.')

    group = parser.add_argument_group('acquire')
    group.add_argument('--title', default='testing',
                       help='the measurement label (no spaces)')
    group.add_argument('-o', '--output', default='./data/{TIME}/{SENSOR}_R{I_RAMP:02d}_M{I_GROUP:02d}_N{I_FRAME:02d}.fits',
                       help='the output fits file.')
    # group.add_argument('-m', '--idle-mode', default=0, type=int,
    #                    help='idle mode')
    # group.add_argument('-ch', '--channels', default=0, type=int,
    #                    help='number of channels')
    # group.add_argument('-rp', '--ramps', default=0, type=int,
    #                    help='number of ramps')
    # group.add_argument('-f', '--frames', default=0, type=int,
    #                    help='number of frames to readout in a ramp')
    group.add_argument('-r', '--rows', default=None, type=int,
                       help='number of rows')
    group.add_argument('-c', '--cols', default=None, type=int,
                       help='number of columns')
    group.add_argument('-e', '--expose-time', default=None, type=float,
                       help='exposure time in seconds')
    group.add_argument('-x', '--repeat', default=1, type=int,
                       help='number of times to repeat the acquisition')

    group.add_argument('--readout', default=None, type=int,
                       help='number of times to repeat the acquisition')

    group = parser.add_argument_group('bias voltages')
    group.add_argument('-vb', '--vbias', action='append',
                       help='append a bias voltage setting. '
                            'Example: -vb 5=0.2 -vb DG_R3=9.945')

    group = parser.add_argument_group('clock voltages')
    group.add_argument('-vc', '--vclock', action='append',
                       help='append a bias voltage setting. '
                            'Example: -vc V_COL_LCOL=2.2 -vc VDBD0_BO4=2.25')

    group = parser.add_argument_group('parameters')
    group.add_argument('-a', '--address', action='append',
                       help='append a bias voltage setting. '
                            'Example: -a int-time=2.2 -a 15=2.3')

    group = parser.add_argument_group('actions')
    group.add_argument('-A', '--acquire', action='store_true',
                       help='acquire the frames x ramps images')
    group.add_argument('-B', '--build', action='store_true',
                       help='build the assembly code')
    group.add_argument('-D', '--dump', action='store_true',
                       help='dump the state of the DSP to the console')
    group.add_argument('-I', '--init', action='store_true',
                       help='init internal memory with the last known state of the rack')
    group.add_argument('-L', '--load', action='store_true',
                       help='upload the seq.dex file to the DSP')
    group.add_argument('-p', '--power-off', action='store_true',
                       help='power off bias voltage')
    group.add_argument('-P', '--power-on', action='store_true',
                       help='power on bias voltage')
    group.add_argument('-R', '--load-rack', action='store_true',
                       help='load the last known rack state into the controller')
    group.add_argument('-S', '--sync', action='store_true',
                       help='enable synchronous readout')
    # group.add_argument('-V', '--voltage-apply', action='store_true',
    #                    help='Apply the bias voltage settings.')

    # process the arguments
    # parser.set_defaults(**settings)
    parser.parse_args()
    opts = parser.parse_args()

    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]

    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)-7s %(name)-20s %(funcName)-20s %(message)s')
    if opts.port:
        try:
            run_server(opts)
        except KeyboardInterrupt:
            print('Caught ctr+c')
    else:
        execute(opts)

# =============================================================================
if __name__ == '__main__':
    main()
#     xc = XCam()
#     # xc.open()
#     # xc.set_usb_timeout(300)
#     # xc.set_usb_timeout(600)
# ##    state = parport.Inp32(0x379)
# ##    xc = XCam()
# ##    xcam_open(xc, r'C:\dev\lab\pyccd\seq\seq.dex', '16S', False)
# ##    xc.set_param(15, 1000)
# ##    print xc.clock_out_memory_location(15)
# ##    sys.exit(0)
# ##    rawdata = numpy.fromfile(DATA_FILE, dtype=numpy.uint16)
# ##    out = XCam.Decode(rawdata, 460, 920, 4, nodeLocation="1234", nodeOrientation="NHBV", rdir=3)
# ##    pyfits_ext.save_data('test.fits', out)
#
#     init_logging(True)
#     g_cmdline = "-c readout -n 1000"
#     g_cmdline = None
#     #test()
#     #sys.exit(0)
#     main(g_cmdline)
