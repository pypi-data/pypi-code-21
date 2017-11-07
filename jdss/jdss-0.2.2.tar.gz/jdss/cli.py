import argparse
import os
import json
import glob
import requests
from jdss import SummaryReport
import base64


def job(args):
    report = SummaryReport()
    section = report.add_section()
    tabs = section.add_tabs()
    for i in range(0, len(args.tab)):
        tab_contents = args.tab[i]
        name = 'tab{}'.format(i + 1) if len(args.names) <= i else args.names[i]
        tab = tabs.add_tab(name)
        for files in [glob.glob(f) for f in tab_contents]:
            for file in files:
                file_name = os.path.splitext(os.path.split(file)[-1])[0]
                file_ext = os.path.splitext(os.path.split(file)[-1])[1].lower()
                if file_ext == '.json':
                    with open(file, 'r') as json_file:
                        contents = json.loads(json_file.read())
                    table = tab.add_table()
                    header = table.add_row()
                    header.add_cell('Key')
                    header.add_cell('Value')
                    for key in sorted(contents.keys()):
                        row = table.add_row()
                        row.add_cell(key)
                        row.add_cell(contents[key])
                elif file_ext in ['.png', '.jpeg', '.jpg']:
                    with open(file, 'rb') as image:
                        image_data = base64.b64encode(image.read()).decode('utf-8').replace('\n', '')
                    tab.add_field(
                        file_name,
                        '<![CDATA[<img src="data:image/{};base64,{}"/>]]>'.format(file_ext[1:], image_data)
                    )
    report.write(args.file, args.output)


def jobs(args):
    url = '{}lastBuild/buildNumber'.format(args.url)
    response = (
        requests.get(url)
        if args.user is None or args.password is None else
        requests.get(url, auth=(args.user, args.password))
    )
    if response.status_code != 200:
        raise Exception('Not ok response received for latest build number. Check the url and credentials')
    last_build_number = int(response.content.decode())

    builds = []
    build_number = last_build_number
    artifact_keys = set()
    while build_number > 0 and len(builds) <= args.history:
        try:
            artifact_values = {}
            url = '{}/{}/api/json'.format(args.url, build_number)
            summary_response = (
                requests.get(url)
                if args.user is None or args.password is None else
                requests.get(url, auth=(args.user, args.password))
            )

            if summary_response.status_code != 200:
                print('WARN: Summary was not available for build number {}'.format(build_number))
                continue
            try:
                summary = json.loads(summary_response.content.decode())
            except:
                print('WARN: Summary was not valid JSON for build number {}'.format(build_number))
                continue

            if summary['result'].upper() != 'SUCCESS':
                print('INFO: Skipping build {}, because it did not succeed'.format(build_number))
                continue

            if len(summary['actions']) > 0:
                action_index = 0
                action_found = False
                for action in summary['actions']:
                    if 'parameters' in action['_class'].lower():
                        action_found = True
                        break
                    action_index += 1
                if action_found and 'parameters' in summary['actions'][action_index]:
                    for parameter in args.parameters:
                        if parameter in [p['name'] for p in summary['actions'][action_index]['parameters']]:
                            artifact_keys.add(parameter)
                            artifact_values[parameter] = [p['value'] for p in summary['actions'][action_index]['parameters'] if p['name'] == parameter][0]

            for artifact in args.artifact:
                url = '{}/{}/artifact/{}'.format(args.url, build_number, artifact)
                artifact_response = (
                    requests.get(url)
                    if args.user is None or args.password is None else
                    requests.get(url, auth=(args.user, args.password))
                )

                if artifact_response.status_code != 200:
                    print('WARN: Artifact was not available for build number {}'.format(build_number))
                    continue

                try:
                    artifact_content = json.loads(artifact_response.content.decode())
                except:
                    print('WARN: Artifact was not valid JSON for build number {}'.format(build_number))
                    continue

                for key in artifact_content.keys():
                    if len(args.artifact) == 1:
                        artifact_values[key] = artifact_content[key]
                    else:
                        artifact_values['{}/{}'.format(os.path.splitext(artifact)[0], key)] = artifact_content[key]

            for key in artifact_values.keys():
                artifact_keys.add(key)

            builds.append({'build_number': build_number, 'artifact': artifact_values, 'description': summary['description']})

        finally:
            build_number -= 1

    report = SummaryReport()
    section = report.add_section()
    accordion = section.add_accordion(args.name)
    table = accordion.add_table()

    header = table.add_row()
    header.add_cell('build')
    sorted_keys = sorted(artifact_keys)
    for key in sorted_keys:
        header.add_cell(key)
    header.add_cell('description')

    for build in builds:
        row = table.add_row()
        row.add_cell(build['build_number'], '{}/{}'.format(args.url, build['build_number']))
        for key in sorted_keys:
            if key not in build['artifact']:
                row.add_cell('-')
            else:
                row.add_cell(build['artifact'][key])
        row.add_cell(build['description'])

    report.write(args.file, args.output)


def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()

    jobs_parser = sub_parsers.add_parser('jobs')
    jobs_parser.add_argument('--url', required=True, help='The url of the build job in Jenkins to summarise')
    jobs_parser.add_argument(
        '--artifact',
        nargs='*',
        required=True,
        help='The name, or names, of the artifact that will be used to populate the metadata about head job. This should be a JSON '
             'file containing a list of key value pairs. e.g. `--artifact metrics.json`, `--artifacts metrics-1.json metrics-2.json`'
    )
    jobs_parser.add_argument('--history', type=int, default=50, help='The number of historic builds to summarise')
    jobs_parser.add_argument('--name', default='History', help='The name to put on the accordion header')
    jobs_parser.add_argument('--file', default='summary.xml', help='The name of the output file')
    jobs_parser.add_argument('--parameters', default=[], nargs='*', help='If provided, this is the list of build parameter names that should be included from the build results')
    jobs_parser.add_argument('--user', default=None, help='The username to use when communicating with Jenkins, if basic authentication is enabled')
    jobs_parser.add_argument('--password', default=None,help='The password to use when communicating with Jenkins, if basic authentication is enabled')
    jobs_parser.add_argument('--output', required=True, help='The output directory into which the summary report XML file should be written')
    jobs_parser.set_defaults(func=jobs)

    job_parser = sub_parsers.add_parser('job')
    job_parser.add_argument(
        '--tab',
        action='append',
        default=[],
        nargs='*',
        help='This option can  be used multiple times to specify the content of an individual tab. Multiple values can '
             'be provided, each being a file path that is read. If the file contains XML or JSON, the values are parsed '
             'into a field per property. The assumption here is that the file will contain key value pairs - if the '
             'structure is more complicated, nested objects will be ignored. If the file paths provided are PNG or JPEG '
             'files then these will be included in the tab as images.'
    )
    job_parser.add_argument(
        '--names',
        default=[],
        nargs='*',
        help='A list of names to be used when labelling the tabs whose content is provided in `--tabs`. If no names are '
             'provided then the tabs will be labelled tab1, tab2, etc. If more names are provided than tabs then the '
             'extras will be ignored.'
    )
    job_parser.add_argument('--file', default='summary.xml', help='The name of the output file')
    job_parser.add_argument('--output', required=True, help='The output directory into which the summary report XML file should be written')
    job_parser.set_defaults(func=job)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
