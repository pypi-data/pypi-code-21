from satnogsclient.web.weblogger import WebLogger
import logging
import cPickle
import subprocess
import os

from satnogsclient.upsat import packet_settings
from satnogsclient import settings as client_settings
from satnogsclient.observer.udpsocket import Udpsocket
from satnogsclient.upsat import packet


logging.setLoggerClass(WebLogger)
logger = logging.getLogger('default')
assert isinstance(logger, WebLogger)

backend_listener_sock = Udpsocket(('0.0.0.0', client_settings.BACKEND_LISTENER_PORT))  # Port in which client listens for frames from gnuradio
ui_listener_sock = Udpsocket(('127.0.0.1', client_settings.BACKEND_FEEDER_PORT))
ecss_feeder_sock = Udpsocket([])  # The socket with which we communicate with the ecss feeder thread
backend_feeder_sock = Udpsocket([])
ld_socket = Udpsocket([])
ld_uplink_socket = Udpsocket([])
ld_downlink_socket = Udpsocket([])


def write_to_gnuradio(buf):
    backend_feeder_sock.sendto(buf, (client_settings.GNURADIO_IP, client_settings.GNURADIO_UDP_PORT))


def read_from_gnuradio():
    logger.info('Started gnuradio listener process')
    while True:
        conn = backend_listener_sock.recv()
        buf_in = bytearray(conn[0])
        ecss_dict = {}
        ret = packet.deconstruct_packet(buf_in, ecss_dict, "gnuradio")
        ecss_dict = ret[0]
        pickled = cPickle.dumps(ecss_dict)
        if len(ecss_dict) == 0:
            logger.error('Ecss Dictionary not properly constructed. Error occured')
            continue
        try:
            if ecss_dict['ser_type'] == packet_settings.TC_LARGE_DATA_SERVICE:
                if ecss_dict['ser_subtype'] <= 8:  # 8 is sthe maximum service subtype corresponding to Large Data downlink
                    ld_downlink_socket.sendto(pickled, ('127.0.0.1', client_settings.LD_DOWNLINK_LISTEN_PORT))
                else:
                    ld_uplink_socket.sendto(pickled, ('127.0.0.1', client_settings.LD_UPLINK_LISTEN_PORT))
            else:
                ecss_feeder_sock.sendto(pickled, ('127.0.0.1', client_settings.ECSS_FEEDER_UDP_PORT))
        except KeyError:
            logger.error('Ecss Dictionary not properly constructed. Error occured. Key \'ser_type\' not in dictionary')


def exec_gnuradio(observation_file, waterfall_file, origin, freq, user_args, script_name, decoded_data):
    arguments = {'filename': observation_file,
                 'waterfall': waterfall_file,
                 'rx_device': client_settings.SATNOGS_RX_DEVICE,
                 'center_freq': str(freq),
                 'user_args': user_args,
                 'script_name': script_name,
                 'decoded_data': decoded_data}
    scriptname = arguments['script_name']
    arg_string = ' '
    if not scriptname:
        scriptname = client_settings.GNURADIO_SCRIPT_FILENAME
    if origin == 'network':
        rx_freq = arguments['center_freq']
        device = client_settings.SATNOGS_RX_DEVICE
        file_path = arguments['filename']
        waterfall_file_path = arguments['waterfall']
        arg_string += '--rx-sdr-device=' + device + ' '
        arg_string += '--rx-freq=' + rx_freq + ' '
        arg_string += '--file-path=' + file_path + ' '
        if arguments['waterfall'] != "":
            arg_string += '--waterfall-file-path=' + waterfall_file_path + ' '
    else:
        arg_string = user_args + ' '
    if client_settings.SATNOGS_RX_DEVICE and "--rx-sdr-device" not in arg_string:
        arg_string += '--rx-sdr-device=' + client_settings.SATNOGS_RX_DEVICE + ' '
    if client_settings.SATNOGS_DOPPLER_CORR_PER_SEC and "--doppler-correction-per-sec" not in arg_string:
        arg_string += '--doppler-correction-per-sec=' + client_settings.SATNOGS_DOPPLER_CORR_PER_SEC + ' '
    if client_settings.SATNOGS_LO_OFFSET and "--lo-offset" not in arg_string:
        arg_string += '--lo-offset=' + client_settings.SATNOGS_LO_OFFSET + ' '
    if client_settings.SATNOGS_PPM_ERROR and "--ppm" not in arg_string:
        arg_string += '--ppm=' + client_settings.SATNOGS_PPM_ERROR + ' '
    if client_settings.SATNOGS_IF_GAIN and "--if-gain" not in arg_string:
        arg_string += '--if-gain=' + client_settings.SATNOGS_IF_GAIN + ' '
    if client_settings.SATNOGS_RF_GAIN and "--rf-gain" not in arg_string:
        arg_string += '--rf-gain=' + client_settings.SATNOGS_RF_GAIN + ' '
    if client_settings.SATNOGS_BB_GAIN and "--bb-gain" not in arg_string:
        arg_string += '--bb-gain=' + client_settings.SATNOGS_BB_GAIN + ' '
    if client_settings.SATNOGS_ANTENNA and "--antenna" not in arg_string:
        arg_string += '--antenna=' + client_settings.SATNOGS_ANTENNA + ' '
    if client_settings.SATNOGS_DEV_ARGS and "--dev-args" not in arg_string:
        arg_string += '--dev-args=' + client_settings.SATNOGS_DEV_ARGS + ' '
    if client_settings.ENABLE_IQ_DUMP and "--enable-iq-dump" not in arg_string:
        arg_string += '--enable-iq-dump=' + str(int(client_settings.ENABLE_IQ_DUMP is True)) + ' '
    if client_settings.IQ_DUMP_FILENAME and "--iq-file-path" not in arg_string:
        arg_string += '--iq-file-path=' + client_settings.IQ_DUMP_FILENAME + ' '
    if not client_settings.DISABLE_DECODED_DATA and "--decoded-data-file-path" not in arg_string:
        arg_string += '--decoded-data-file-path=' + arguments['decoded_data'] + ' '

    logger.info('Starting GNUradio python script')
    proc = subprocess.Popen([scriptname + " " + arg_string], shell=True,
                            preexec_fn=os.setsid)
    return proc
