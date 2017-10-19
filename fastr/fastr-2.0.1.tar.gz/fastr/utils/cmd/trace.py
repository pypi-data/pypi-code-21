#!/usr/bin/env python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import json
import shellescape
from fastr.utils.cmd import add_parser_doc_link

FASTR_LOG_TYPE = 'none'


def get_parser():
    parser = argparse.ArgumentParser(
        description="Fastr trace helps you inspect the staging directory of the"
                    " Network run and pinpoint the errors."
    )
    parser.add_argument('infile', nargs='?',
                        default=os.path.join(os.getcwd(), '__sink_data__.json'),
                        metavar='__sink_data__.json', help='result file to cat')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
                        help='set verbose output for more details')
    parser.add_argument('--sinks',  dest='sinks', nargs="*",
                        help='list results for specified sinks')
    parser.add_argument('--samples', dest='samples', nargs="*",
                        help='list result for all samples')
    return parser


def read_sink_data(infile):
    if os.path.isdir(infile):
        infile = os.path.join(infile, '__sink_data__.json')

    if os.path.isfile(infile) and os.access(infile, os.R_OK):
        with open(infile) as sink_data_file:
            data = json.load(sink_data_file)
    else:
        print('ERROR: could not read: {}'.format(infile))
        data = None

    return data


def switch_sample_sink(sink_data):
    # Switch samples and sinks
    samples_overview = dict()
    for sink, samples in sink_data.iteritems():
        for sample_id, sample in samples.iteritems():
            if sample_id not in samples_overview:
                samples_overview[sample_id] = dict()
            samples_overview[sample_id][sink] = sample
    return samples_overview


def print_sinks(sink_data, sink_ids, verbose):
    # Filter dict
    if sink_ids:
        filtered_dict = {sink_id: sink_data[sink_id] for sink_id in sink_ids}
    else:
        filtered_dict = sink_data

    # Print dict
    for sink, samples in sorted(filtered_dict.iteritems()):
        finished = 0
        cancelled = 0
        failed_samples_string = []
        for sample_id, sample in sorted(samples.iteritems()):
            if (sample['status'] == "JobState.cancelled") or (sample['status'] == "JobState.failed"):
                cancelled += 1
                for error_message in sample['errors']:
                    failed_samples_string.append('  {}: {}'.format(sample_id, error_message[2]))
            elif sample['status'] == "JobState.finished":
                finished += 1
        print('{} -- {} failed -- {} succeeded'.format(sink, cancelled, finished))
        if verbose:
            for error_message in failed_samples_string:
                print(error_message)


def print_samples(sink_data, sample_ids, verbose):
    samples_overview = switch_sample_sink(sink_data)

    # Filter dict
    if sample_ids:
        filtered_dict = { sample_id: samples_overview[sample_id] for sample_id in sample_ids }
    else:
        filtered_dict = samples_overview

    # Print_sinks(samples_overview)
    for sample, sinks in sorted(filtered_dict.iteritems()):
        finished = 0
        cancelled = 0
        failed_sink_string = []
        for _, sink in sorted(sinks.iteritems()):
            if sink['status'] == "JobState.cancelled" or sink['status'] == "JobState.failed":
                cancelled += 1
                for error_message in sink['errors']:
                    failed_sink_string.append(error_message[2])
            elif sink['status'] == "JobState.finished":
                finished += 1
        print('{} -- {} failed -- {} succeeded'.format(sample, cancelled, finished))
        if verbose:
            for error_message in set(failed_sink_string):
                print(error_message)


def print_job_result(job_file):
    from fastr.utils.iohelpers import load_gpickle, load_json
    from pprint import pprint

    job = load_gpickle(job_file)
    info_store = load_json(job.extrainfofile)

    print('\n\n===== JOB {} ====='.format(job.id))
    if hasattr(job, 'network_id'):
        print('Network: {}'.format(job.network_id))
    if hasattr(job, 'run_id'):
        print('Run: {}'.format(job.run_id))

    print('Node: {}'.format(job.node_id))
    print('Sample index: {}'.format(job.sample_index))
    print('Sample id: {}'.format(job.sample_id))
    print('Status: {}'.format(job.status))
    print('Timestamp: {}'.format(job.timestamp))
    print('Job file: {}'.format(job.logfile))

    if 'process' in info_store:
        command = info_store['process'].get('command', None)
        if command is not None:
            print('\nCommand:')
            print('List representation: {}'.format(command))
            printable_command = []
            for item in command:
                printable_command.append(shellescape.quote(item))
            print('String representation: {}'.format(' '.join(printable_command)))
    else:
        print('\nProcess error:')
        print('Cannot find process information in Job information, processing probably got killed')
        print('This is often a result of too high memory use')

    print('\nOutput data:')
    pprint(job.output_data)

    print('\nStatus history:')
    for timestamp, status in job.status_list:
        print('{}: {}'.format(timestamp, status))

    if hasattr(job, 'errors'):
        errors = job.errors
    elif 'errors' in info_store and isinstance(info_store['errors'], list):
        errors = info_store['errors']
    else:
        errors = []

    print('\n----- ERRORS -----')
    for job_error in errors:
        print('- {e[0]}: {e[1]} ({e[2]}:{e[3]})'.format(e=job_error))
    print('------------------')

    if 'process' in info_store:
        if 'stdout' in info_store['process']:
            print('\n----- STDOUT -----')
            print(info_store['process']['stdout'])
            print('------------------')

        if 'stderr' in info_store['process']:
            print('\n----- STDERR -----')
            print(info_store['process']['stderr'])
            print('------------------')


def print_sample_sink(sink_data, dirname, sample_sink_tuples, verbose):
    for sink, sample in sample_sink_tuples:
        print('Tracing errors for sample {} from sink {}'.format(sample, sink))
        errors = sink_data[sink][sample]['errors']
        for error in errors:
            result_pickle = os.path.abspath(os.path.join(dirname, error[3]))
            print('Located result pickle: {}'.format(result_pickle))

            print_job_result(result_pickle)


def main():
    """
    Trace samples/sinks from a run
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    sink_data = read_sink_data(args.infile)

    if not sink_data:
        exit(1)

    if args.sinks is not None and args.samples is not None:
        if len(args.sinks) == len(args.samples):
            sample_sink_tuples = zip(args.sinks, args.samples)
            print_sample_sink(sink_data, os.path.dirname(args.infile), sample_sink_tuples, args.verbose)
        else:
            print("ERROR nr of sinks does not match number of samples")
            exit(1)
    elif args.sinks is not None:
        print_sinks(sink_data, args.sinks, args.verbose)
    elif args.samples is not None:
        print_samples(sink_data, args.samples, args.verbose)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
