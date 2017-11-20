# -*- coding: utf-8 -*-

"""Main module."""
import argparse
import csv
import os
import os.path
import logging
import requests
import json
import time
import behavioral_signals_swagger_client as swagger_client


BEST_API_URL = "https://api4.behavioralsignals.com"
WEB_APP_URL = "http://tdemo.bsis.me"

POLLING_SLEEP_TIME = 5  # in seconds


def get_json_results_for_pid(pid, json_file):
    best_id = os.environ.get('BEST_ID')
    if not best_id:
        error_msg = 'The BEST_ID environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    best_token = os.environ.get('BEST_TOKEN')
    if not best_token:
        error_msg = 'The BEST_TOKEN environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Configuration
    swagger_client.configuration.host = BEST_API_URL
    swagger_client.configuration.api_key['X-Auth-Token'] = best_token
    api_instance = swagger_client.DefaultApi()
    api_response = api_instance.get_process_info(best_id, pid)
    if api_response.status == 2:
        api_results = api_instance.get_process_results(best_id, pid)
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(pid, api_response.status))

    return api_response.status


def get_json_results_for_pid_after_polling(pid, json_dir):
    best_id = os.environ.get('BEST_ID')
    if not best_id:
        error_msg = 'The BEST_ID environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    best_token = os.environ.get('BEST_TOKEN')
    if not best_token:
        error_msg = 'The BEST_TOKEN environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Configuration
    swagger_client.configuration.host = BEST_API_URL
    swagger_client.configuration.api_key['X-Auth-Token'] = best_token

    api_instance = swagger_client.DefaultApi()
    api_response = api_instance.get_process_info(best_id, pid)
    elapsed_time = 0
    while api_response.status == 0 or api_response.status == 1:
        api_response = api_instance.get_process_info(best_id, pid)
        time.sleep(POLLING_SLEEP_TIME)
        elapsed_time += POLLING_SLEEP_TIME

    logging.info("Polling for process {} lasted {} seconds".format(pid, elapsed_time))

    if api_response.status == 2:
        fname = os.path.splitext(os.path.basename(api_response.source))[0]
        api_results = api_instance.get_process_results(best_id, pid)
        json_file = os.path.join(json_dir, "{}_{}.json".format(fname, pid))
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(pid, api_response.status))

    return api_response.status


def get_json_results_for_pid_list(pid_file, json_dir):
    missing_pids = []
    with open(pid_file, 'r') as p:
        for line in p:
            pid = line.rstrip()
            print pid
            status = get_json_results_for_pid_after_polling(pid, json_dir)
            if status != 2:
                missing_pids.append(pid)

    return missing_pids


def get_json_results_frames_for_pid(pid, json_file):
    best_id = os.environ.get('BEST_ID')
    if not best_id:
        error_msg = 'The BEST_ID environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    best_token = os.environ.get('BEST_TOKEN')
    if not best_token:
        error_msg = 'The BEST_TOKEN environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Configuration
    swagger_client.configuration.host = BEST_API_URL
    swagger_client.configuration.api_key['X-Auth-Token'] = best_token
    api_instance = swagger_client.DefaultApi()
    api_response = api_instance.get_process_info(best_id, pid)
    if api_response.status == 2:
        api_results = api_instance.get_process_results_frames(best_id, pid)
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(pid, api_response.status))

    return api_response.status


def get_json_results_frames_for_pid_after_polling(pid, json_dir):
    best_id = os.environ.get('BEST_ID')
    if not best_id:
        error_msg = 'The BEST_ID environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    best_token = os.environ.get('BEST_TOKEN')
    if not best_token:
        error_msg = 'The BEST_TOKEN environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    # Configuration
    swagger_client.configuration.host = BEST_API_URL
    swagger_client.configuration.api_key['X-Auth-Token'] = best_token

    api_instance = swagger_client.DefaultApi()
    api_response = api_instance.get_process_info(best_id, pid)
    elapsed_time = 0
    while api_response.status == 0 or api_response.status == 1:
        api_response = api_instance.get_process_info(best_id, pid)
        time.sleep(POLLING_SLEEP_TIME)
        elapsed_time += POLLING_SLEEP_TIME

    logging.info("Polling for process {} lasted {} seconds".format(pid, elapsed_time))

    if api_response.status == 2:
        fname = os.path.splitext(os.path.basename(api_response.source))[0]
        api_results = api_instance.get_process_results_frames(best_id, pid)
        json_file = os.path.join(json_dir, "{}_{}.json".format(fname, pid))
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(pid, api_response.status))

    return api_response.status


def get_json_results_frames_for_pid_list(pid_file, json_dir):
    missing_pids = []
    with open(pid_file, 'r') as p:
        for line in p:
            pid = line.rstrip()
            print pid
            status = get_json_results_frames_for_pid_after_polling(pid, json_dir)
            if status != 2:
                missing_pids.append(pid)

    return missing_pids


def get_json_results_asr_for_pid(pid, json_file):
    best_id = os.environ.get('BEST_ID')
    if not best_id:
        error_msg = 'The BEST_ID environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    best_token = os.environ.get('BEST_TOKEN')
    if not best_token:
        error_msg = 'The BEST_TOKEN environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Configuration
    swagger_client.configuration.host = BEST_API_URL
    swagger_client.configuration.api_key['X-Auth-Token'] = best_token
    api_instance = swagger_client.DefaultApi()
    api_response = api_instance.get_process_info(best_id, pid)
    if api_response.status == 2:
        api_results = api_instance.get_process_results_asr(best_id, pid)
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(pid, api_response.status))

    return api_response.status


def get_json_results_asr_for_pid_after_polling(pid, json_dir):
    best_id = os.environ.get('BEST_ID')
    if not best_id:
        error_msg = 'The BEST_ID environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    best_token = os.environ.get('BEST_TOKEN')
    if not best_token:
        error_msg = 'The BEST_TOKEN environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Configuration
    swagger_client.configuration.host = BEST_API_URL
    swagger_client.configuration.api_key['X-Auth-Token'] = best_token

    api_instance = swagger_client.DefaultApi()
    api_response = api_instance.get_process_info(best_id, pid)
    elapsed_time = 0
    while api_response.status == 0 or api_response.status == 1:
        api_response = api_instance.get_process_info(best_id, pid)
        time.sleep(POLLING_SLEEP_TIME)
        elapsed_time += POLLING_SLEEP_TIME

    logging.info("Polling for process {} lasted {} seconds".format(pid, elapsed_time))

    if api_response.status == 2:
        fname = os.path.splitext(os.path.basename(api_response.source))[0]
        api_results = api_instance.get_process_results_asr(best_id, pid)
        json_file = os.path.join(json_dir, "{}_{}_words.json".format(fname, pid))
        with open(json_file, 'w') as jf:
            json.dump(api_results.to_dict(), jf)
    else:
        logging.warning("Problem with pid: {}. Processing status: {}".format(pid, api_response.status))

    return api_response.status


def get_json_results_asr_for_pid_list(pid_file, json_dir):
    missing_pids = []
    with open(pid_file, 'r') as p:
        for line in p:
            pid = line.rstrip()
            print pid
            status = get_json_results_asr_for_pid_after_polling(pid, json_dir)
            if status != 2:
                missing_pids.append(pid)

    return missing_pids


def get_user_uri():
    best_id = os.environ.get('BEST_ID')
    if not best_id:
        error_msg = 'The BEST_ID environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)
    return '{}/client/{}'.format(BEST_API_URL, best_id)


def get_process_audio_uri():
    return '{}/process/audio'.format(get_user_uri())


def submit_single_file(file_name, data):
    best_token = os.environ.get('BEST_TOKEN')
    if not best_token:
        error_msg = 'The BEST_TOKEN environment variable has not been properly set'
        logging.error(error_msg)
        raise ValueError(error_msg)

    headers = {'X-Auth-Token': best_token, 'Accept': "application/json"}
    files = {'file': open(file_name, 'rb')}

    # Validate if number of channels and call direction are correct
    if 'channels' not in data or (data['channels'] != 1 and data['channels'] != 2):
        data['channels'] = 1
        logging.warn('Set value for channels to default')

    if 'calldirection' not in data or (data['calldirection'] != '1' and data['calldirection'] != '2'):
        data['calldirection'] = '1'
        logging.warn('Set value for call direction to default')

    response = requests.post(get_process_audio_uri(), params=data, files=files, headers=headers)
    return response


def submit_single_file_no_params(file_name):
    # Default data values
    data = {'channels': '1', 'calldirection': '1'}
    return submit_single_file(file_name, data)


def submit_file_list(file_list):
    with open(file_list, 'r') as l:
        for line in l:
            file_name = line.rstrip()
            logging.debug('Submitting {}'.format(file_name))
            r = submit_single_file_no_params(file_name)
            logging.debug(r.url)
            logging.debug(r.text)


def submit_pids_web_application(all_pids):
    if not all_pids:
        logging.error('Error pids json array is empty')
        raise ValueError('ERROR: empty pids json array')

    web_app_token = os.environ.get('WEB_APP_TOKEN')
    if not web_app_token:
        logging.error('The WEB_APP_TOKEN environment variable has not been properly set')
        raise ValueError('ERROR: failed to retrieve WEB_APP_TOKEN environmental variable')

    web_app_token = 'Bearer ' + str(web_app_token)

    web_app_url_pids = WEB_APP_URL + str('/jobs/create/pids/')
    headers = {'Authorization': web_app_token, "Content-Type":
               "Application/json", "Accept": "Application/json", }

    json_pids = json.dumps(all_pids, ensure_ascii=False)
    web_app_response = requests.post(web_app_url_pids, data=json_pids, headers=headers)

    if web_app_response.status_code != 200:
        logging.error('The error in response from web application')
        raise ValueError('ERROR: web application responded with status code: %s' % web_app_response.status_code)


def submit_csv_file(csv_file, pid_file, submit_to_webapp, tag=None, nchannels=1):
    data_fields = ['channels', 'calldirection', 'agentId', 'agentTeam', 'campaignId', 'callType', 'callTime', 'timezone', 'ANI', 'tag']
    n_failures = 0

    jobs = []
    all_pids = {}
    call_id = None

    with open(csv_file, 'r') as f:
        with open(pid_file, 'w') as p:
            reader = csv.reader(f)
            for row in reader:
                file_name = row[0]
                data = {}
                n_data_values = len(row)
                if n_data_values > 1:
                    for idx, value in enumerate(row[1:]):
                        if value:
                            data[data_fields[idx]] = value
                            if data_fields[idx] == 'tag':
                                if tag is not None:
                                    data['tag'] += ',{}'.format(tag)

                if 'tag' not in data and tag is not None:
                    data['tag'] = tag
                if 'channels' not in data:
                    data['channels'] = nchannels

                r = submit_single_file(file_name, data)
                logging.debug(r.text)

                if r.status_code != 200:
                    n_failures += 1

                else:
                    j = json.loads(r.text)
                    p.write("{}\n".format(j['pid']))

                    if submit_to_webapp:
                        pid = r.json().get('pid')
                        job = {}

                        job['pid'] = pid
                        job['filename'] = file_name
                        job['jobname'] = 'job_' + str(file_name)
                        job['call_id'] = call_id
                        job['agent_id'] = None
                        job['campaign_id'] = None

                        jobs.append(job)

    if submit_to_webapp:
        all_pids['jobs'] = jobs
        submit_pids_web_application(all_pids)

    return n_failures


def get_user_details():
    best_token = os.environ.get('BEST_TOKEN')
    headers = {'X-Auth-Token': best_token, 'Accept': "application/json"}
    r = requests.get(get_user_uri(), headers=headers)
    logging.debug(r.url)
    logging.debug(r.text)


def send_audio(args):
    logging.info('Using csv file: {}'.format(args.csvFile))

    n_failures = submit_csv_file(args.csvFile, args.pidFile, submit_to_webapp=args.webapp, tag=args.tag, nchannels=args.nchannels)

    if n_failures == 0:
        logging.info("File uploading ran successfully.")


def get_results(args):
    if not os.path.exists(args.resultsDir):
        logging.warning("Creating new folder: {}".format(args.resultsDir))
        os.mkdir(args.resultsDir)
    missing_pids = get_json_results_for_pid_list(args.pidFile, args.resultsDir)

    if len(missing_pids) > 0:
        logging.info("The following pids do not have associated results: {}".format(missing_pids))
    else:
        logging.info("Results for all pids have been downloaded.")


def get_results_frames(args):
    if not os.path.exists(args.resultsDir):
        logging.warning("Creating new folder: {}".format(args.resultsDir))
        os.mkdir(args.resultsDir)

    missing_pids = get_json_results_frames_for_pid_list(args.pidFile, args.resultsDir)
    if len(missing_pids) > 0:
        logging.info("The following pids do not have associated results: {}".format(missing_pids))
    else:
        logging.info("Results for all pids have been downloaded.")


def get_results_asr(args):
    if not os.path.exists(args.resultsDir):
        logging.warning("Creating new folder: {}".format(args.resultsDir))
        os.mkdir(args.resultsDir)

    missing_pids = get_json_results_asr_for_pid_list(args.pidFile, args.resultsDir)
    if len(missing_pids) > 0:
        logging.info("The following pids do not have associated results: {}".format(missing_pids))
    else:
        logging.info("Results for all pids have been downloaded.")


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='''
    Basic command line interface to callER.ai.
    ''')

    subparsers = parser.add_subparsers()
    post_parser = subparsers.add_parser("send_audio", help='''
    Submit audio to the Behavioral Signals API.

    The required csv file needs to be formatted as follows:
    path/to/file, number of channels, call direction, agentId, agentTeam, campaign Id,
    calltype, calltime, timezone, ANI, tag.

    Parameters can be omitted as long as the remaining columns can be read unambiguously.
    For example, one can just provide the list of paths to the audio files.

    The number of channels (integer) is the number of channels in the audio file, i.e., 1 if both speakers are
    recorded in a single channel, 2 otherwise, call direction (integer) is
    whether the call is inbound (1) or outbound (2). The rest of the parameters are strings chosen on a per case
    basis. Calltype is either "LA" (live answer) or "AM" (answering machine).

    EXAMPLE CSV FILE ENTRY:
    /home/user/audio1.wav,1,1,mike01,fw00,prod-001-42,LA,2016-04-15 20:42:31,-3,312-123-4564
    ''')
    get_parser = subparsers.add_parser("get_results", help='''
    Get json results from the Behavioral Signals API.

    The list of process ids (as generated by a call to send_audio and the output directory, where
    processing results will be stored, are required arguments.
    ''')
    get_parser.set_defaults(func=get_results)
    get_parser.add_argument('pidFile', metavar='pidFile', type=str, help='''
    File with the process ids whose results will be retrieved
    ''')
    get_parser.add_argument('resultsDir', metavar='resultsDir', type=str,
                            help='Directory where the json results will be stored')
    
    get_frames_parser = subparsers.add_parser("get_results_frames", help='''
        Get json results at frame-level from the Behavioral Signals API.
        
        The list of process ids (as generated by a call to send_audio and the output directory, where
        processing results will be stored, are required arguments.
        ''')
    get_frames_parser.set_defaults(func=get_results_frames)
    get_frames_parser.add_argument('pidFile', metavar='pidFile', type=str, 
                                   help='File with the process ids whose results will be retrieved')
    get_frames_parser.add_argument('resultsDir', metavar='resultsDir', type=str, 
                                   help='Directory where the json results will be stored')
    
    get_asr_parser = subparsers.add_parser("get_results_asr", help='''
        Get json ASR results from the Behavioral Signals API.
        
        The list of process ids (as generated by a call to send_audio and the output directory, where
        processing results will be stored, are required arguments.
        ''')
    get_asr_parser.set_defaults(func=get_results_asr)
    get_asr_parser.add_argument('pidFile', metavar='pidFile', type=str, 
            help='File with the process ids whose results will be retrieved')
    get_asr_parser.add_argument('resultsDir', metavar='resultsDir', type=str, 
            help='Directory where the json results will be stored')

    post_parser.set_defaults(func=send_audio)
    post_parser.add_argument('csvFile', metavar='csvFile', type=str, 
            help='List of files to be submitted to the API')
    post_parser.add_argument('pidFile', metavar='pidFile', type=str, 
            help='''
            File where the list of API process ids will be stored for the files which 
            have been successfully submitted''')
    post_parser.add_argument('--tag', metavar='tag', type=str, default='fuploader', 
            help='A tag serving as identifier for the specific dataset to be processed')
    post_parser.add_argument('--nchannels', metavar='nchannels', type=int, default=1, 
            help='The number of channels in the audio files, if that is common for all uploaded files')

    post_parser.add_argument('--webapp', metavar='webapp', default= False, type=str, 
            help='Optinaly updates web app ')

    parser.add_argument('--log', metavar='logLevel', default='DEBUG', type=str,
                        help='Logging level: error, warning, debug, info')

    args = parser.parse_args()

    numericLogLevel = getattr(logging, args.log.upper(), None)
    if not isinstance(numericLogLevel, int):
        raise ValueError('Invalid logging level: %s' % args.log)
    logging.basicConfig(level=numericLogLevel)

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(numericLogLevel)
    requests_log.propagate = True
    args.func(args)


if __name__ == '__main__':
    main()
