import fileutils
import validator_xml

import validate_maps
import validator_localization
import validate_sounds


def print_log(validator, caption):
    print caption
    validator.validate()
    for i, log in enumerate(sorted(validator.logs)):
        print '\t', str(i + 1) + '\t: ', log
    if not validator.logs:
        print '\tSuccess'


def run():
    result = True
    fileutils.ignore_folders.extend(['steam', 'cocoscenes'])
    fileutils.inspectResources()

    # validate xmls
    for file in fileutils.xmls:
        validator_xml.validate(file)
    logs = sorted(validator_xml.logs)
    for i, log in enumerate(logs):
        print '\t', str(i + 1) + '\t: ', log
    print '{} errors in {} xmls'.format(len(logs), len(fileutils.xmls))
    print 'Unused atlases:\n\t', '\n\t'.join(fileutils.unused) if len(fileutils.unused) else ' not founded'

    print_log(validate_maps, 'Validate maps:')
    print_log(validator_localization, 'Validate localization:')
    print_log(validate_sounds, 'Validate sounds:')

    result = result and len(validator_xml.logs) == 0
    result = result and len(validate_maps.logs) == 0
    result = result and len(validator_localization.logs) == 0
    if not result:
        print 'Validation finished with Failed result'
        exit(-1)
    print 'Validation finished.'


if __name__ == '__main__':
    run()
