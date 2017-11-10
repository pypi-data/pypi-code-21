import sys
import os
import tempfile
import shutil
import shlex

import xml.etree.ElementTree as ET


INTERPRETER_EXECUTABLE = sys.executable
CURRENT_PACKAGE_DIR, fn = os.path.split(__file__)


# remove ourselves
# remember: from version 0.1.7.2 onwards
# there is always a copy of this module named .__first_run__
os.remove(__file__)


from . import enablegalaxy


def configure (args, config):
    """Interactive package configuration after fresh install."""

    from .dialogs import ASK_QUESTION, USE_CFG_DEFAULT, NO_DEFAULT, run_dialogs
    
    fix_executable_shebang()
    prepare_galaxy_integration()

    try:
        cpu_count = os.cpu_count()
    except AttributeError:
        # os.cpu_count is not available in Python 3.3!
        # The Python 3.4+ function returns None if it cannot determine the
        # cpu number so we mimick this behaviour.
        cpu_count = None

    if cpu_count:
        # try to leave one cpu for other processes
        multithreading_default = cpu_count-1 or 1
        if multithreading_default > 4:
            # be more generous when there are enough cpus for everybody
            multithreading_default -= 1
        if multithreading_default > 16:
            # Limiting the default to 16 is quite arbitrary, but speed gains
            # from higher settings will be negligible in most situations.
            multithreading_default = 16
    else:
        # The cpu number could not be determined. Lets just stick with what's
        # hardcoded in the cfg file.
        multithreading_default = USE_CFG_DEFAULT


    try:
        tmpfiles_default = tempfile.gettempdir()
    except FileNotFoundError:
        # No writable folder for storing temporary files could be found.
        # We force the user to provide a path.
        tmpfiles_default = NO_DEFAULT

    wizardry = [        
        {
            'title': 'Multiprocessing',
            'target_param': 'multithreading_level',
            'default_value': multithreading_default,
            'intro': (
                'Some MiModD tools can make use of parallel processing to speed '
                'up certain analysis steps. '
                + (
                    'We have detected {} cpu eqivalents available on your system.'
                    .format(cpu_count)
                    if cpu_count else
                    'We could not determine the number of cpu equivalents of your '
                    'system.'
                    )
                ),
            'questions': [
                {
                    'question': 'How many cpu eqivalents maximum do you want to '
                                'allow MiModD to occupy simultaneously at any '
                                'given time {}?',
                }
            ]
        },
        {
            'title': 'Memory consumption',
            'target_param': 'max_memory',
            'intro': 'Some MiModD tools can run more efficiently '
                           'if they can use a larger amount of memory at once.',
            'questions': [
                {
                    'question': 'How much memory should MiModD be allowed to '
                                'occupy maximally at any given time {}?',
                }
            ]
        },
        {
            'title': 'Temporary data folder',
            'target_param': 'tmpfiles_path',
            'default_value': tmpfiles_default,
            'intro': 'Some MiModD tools generate lots of intermediate '
                           'data that they need to write to temporary files on '
                           'disk, but which they will delete again before '
                           'finishing. Since these can be huge files (sometimes '
                           'an order of magnitude larger than the final output we '
                           'think it is good to give you control over where they '
                           'are saved on your file system.\n'
                           'For one thing, we cannot fully exclude that, under '
                           'unusual circumstances, some of these files will not '
                           'be accidentally left behind after a tool run so you '
                           'should be able to locate the files to delete them '
                           'manually then. For another, you may want to write '
                           'temporary files to a dedicated device, e.g., a '
                           'separate HDD instead of a SDD used for regular files '
                           'to preserve write cycles of the latter.',
            'questions': [
                {
                    'question': 'Do you want MiModD to determine the location of '
                                'the temporary data folder dynamically at tool '
                                'runtime (y/n) {}?',
                    'choices': ['y', 'Y', 'n', 'N'],
                    'default_value': 'y',
                },
                {
                    'question': 'Please provide the fixed path to the folder that '
                                'should be used to store temporary data {}:',
                    'conditional':
                        lambda x: None if x.lower() == 'y' else ASK_QUESTION
                }
            ]
        },
        {
            'title': 'SnpEff location',
            'target_param': 'snpeff_path',
            'default_value': None,
            'intro': 'If you have SnpEff installed on your system, '
                           'the MiModD annotate tool can use this software to '
                           'include SnpEff annotations in its output. '
                           'For this to work MiModD needs to know where to find '
                           'SnpEff on your filesystem.',
            'questions': [
                {
                    'question': 'Please provide the path to a SnpEff installation '
                                'folder (the folder that holds the snpeff.jar '
                                'file) [SnpEff not installed]:',
                }
            ]
        }
    ]

    run_dialogs(wizardry, args, config)        
    print("""
All necessary information has been collected. Hit <Enter> to store your settings and start using MiModD.

To change settings later, you can rerun this tool with new settings provided as command line options.

""")
    _ = input()


def prepare_package_files ():
    """Automatic package configuration during upgrade."""

    print('Configuring newly installed files ...', end=' ')
    sys.stdout.flush()

    errors = False
    try:
        fix_executable_shebang()
    except:
        errors = True
        raise
    finally:
        try:
            prepare_galaxy_integration()
        except:
            errors = True
            raise
        finally:
            print('FAILED' if errors else 'done')

            print('Migrating settings ...', end=' ')
            try:    
                upgrade_cfg()
                print('done')
            except:
                print('FAILED')
                raise
            

def upgrade_cfg ():
    cfg_current = os.path.join(CURRENT_PACKAGE_DIR, 'cfg.py')
    cfg_template = os.path.join(CURRENT_PACKAGE_DIR, '.cfg')
    if not os.path.isfile(cfg_template):
        template_settings = [i + '\n' for i in DEFAULTCONFIG.split('\n')]
    else:
        with open(cfg_template, 'r', encoding='utf-8') as template:
            template_settings = template.readlines()
    with open(cfg_current, 'r', encoding='utf-8') as current:
        current_backup = current.readlines()

    current_settings = {}
    for line in current_backup:
        if line.strip() and line.lstrip()[0] != '#':
            key, value = [part.strip() for part in line.split('=')]
            current_settings[key] = value

    newcfg_lines = []            
    for line in template_settings:
        overwrite = False
        if not line.strip() or line.lstrip()[0] == '#':
            newcfg_lines.append(line)
            continue
        if line[0] == '!':
            line = line[1:]
            overwrite = True
        key, value = [part.strip() for part in line.split('=')]
        if overwrite or key not in current_settings:
            newcfg_lines.append(line)
        else:
            newcfg_lines.append('{0}= {1}\n'
                                .format(line.split('=')[0],
                                        current_settings[key])
                                )
            
    with open(cfg_current, 'w', encoding='utf-8') as newcfg:
        try:
            newcfg.writelines(newcfg_lines)
        except:
            newcfg.close()
            with open(cfg_current, 'w', encoding='utf-8') as newcfg:
                newcfg.writelines(current_backup)
            raise


def fix_executable_shebang ():
    mimodd_script = os.path.join(CURRENT_PACKAGE_DIR, 'bin', 'mimodd')
    # Adjust the shebang line to the environment if possible.
    if os.path.exists(mimodd_script) \
       and INTERPRETER_EXECUTABLE and not ' ' in INTERPRETER_EXECUTABLE:
        # with POSIX systems there is no way to form a valid shebang line
        # if there is a space in the executable path so we leave the file alone.
        # Under Windows we could do:
        # if ' ' in interpreter_executable:
        #    # quote the interpreter path if it contains spaces
        #    interpreter_executable = '"%s"' % interpreter_executable

        with open(mimodd_script, 'r', encoding='utf-8') as script_in:
            first_line = script_in.readline()
            if not first_line.startswith('#!'):
                raise RuntimeError(
                    'Compromised starter script.'
                    )
            first_line = '#!' + INTERPRETER_EXECUTABLE + '\n'
            remaining_lines = script_in.readlines()
        with open(mimodd_script, 'w', encoding='utf-8') as script_out:
            script_out.write(first_line)
            script_out.writelines(remaining_lines)


def prepare_galaxy_integration ():
    enablegalaxy.GalaxyAccess.set_toolbox_path()


DEFAULTCONFIG = """\
# USER-CONTROLLED SETTINGS
tmpfiles_path = r''
multithreading_level = 1
max_memory = 2
snpeff_path = r''
use_galaxy_index_files = True

input_decoding = 'lenient'

# INSTALLATION SETTINGS
# DON'T CHANGE!

bin_path = r'../bin'
template_path = r'../templates'
"""
