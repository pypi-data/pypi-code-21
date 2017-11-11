import sys
import os.path

# make sure this is run from inside the package
from . import config as mimodd_settings
from . import __version__
from . import FileAccessError


class GalaxyAccess (object):
    CONFIG_FILE_GUESSES = ['config/galaxy.ini',
                           'universe_wsgi.ini']
    TOOL_CONFIG_FILE_REF = 'tool_config_file'
    TOOL_DEP_DIR_REF = 'tool_dependency_dir'
    TOOL_DEP_DIR_GUESS = 'database/dependencies'
    pkg_galaxy_data_path = os.path.join(
        os.path.dirname(mimodd_settings.__file__),
        'galaxy_data')
    tool_conf_file = os.path.join(
        pkg_galaxy_data_path, 'mimodd_tool_conf.xml'
        )

    @classmethod
    def set_toolbox_path (cls):
        """Update the mimodd_tool_conf.xml file installed as part of the
        package with an absolute tool_path to the package xml wrappers."""
        
        with open(cls.tool_conf_file, 'r', encoding='utf-8') as sample:
            template = sample.readlines()[1:]
        with open(cls.tool_conf_file, 'w', encoding='utf-8') as out:
            out.write('<toolbox tool_path="{0}">\n'
                      .format(cls.pkg_galaxy_data_path)
                      )
            out.writelines(template)

    def __init__ (self, galaxydir = None,
                  config_file = None, dependency_dir = None):
        if galaxydir is None:
            if config_file is None:
                raise ArgumentParseError(
                    'The location of either the Galaxy root directory '
                    'or of the Galaxy config file must be specified.'
                    )
            if not os.path.isabs(config_file):
                raise ArgumentParseError(
                    'Need a Galaxy root directory to base relative path to '
                    'config file on.'
                    )
            if dependency_dir and not os.path.isabs(dependency_dir):
                raise ArgumentParseError(
                    'Need a Galaxy root directory to base relative path to '
                    'tool dependency folder on.'
                    )
        elif not os.path.isdir(galaxydir):
            raise FileAccessError(
                'Galaxy root path {0} does not specify a valid directory.'
                .format(galaxydir)
                )
        # TO DO: see if we can reliably determine the Galaxy root directory
        # from the specified config_file in at least some situations.
        # Currently, we just store the passed in value even if it is None.
        self.galaxy_dir = galaxydir

        # Get the path to the Galaxy configuration file and read its content.
        if config_file is None:
            self.config_file = self.get_config_file()
            if not self.config_file:
                raise FileAccessError(
                    'Could not find any Galaxy configuration file in its '
                    'default location with Galaxy root path {0}.\n'
                    'Please correct the Galaxy root path or specify the '
                    'configuration file directly.'
                    .format(self.galaxy_dir)
                    )
        else:
            self.config_file = os.path.normpath(
                os.path.join(self.galaxy_dir or '', config_file)
                )
            if not os.path.isfile(self.config_file):
                raise FileAccessError(
                    'Could not find the Galaxy configuration file {0}.'
                    .format(self.config_file)
                    )
        with open(self.config_file, 'r', encoding='utf-8') as config_in:
            self.config_data = config_in.readlines()

        # Get the path to the Galaxy tool dependency folder.
        if dependency_dir is None:
            self.tool_dependency_dir = self.get_tool_dependency_dir()
            if not self.tool_dependency_dir:
                raise FileAccessError(
                    "Could not detect the location of Galaxy's tool "
                    'dependency directory with Galaxy root path {0}.\n'
                    'Please correct the Galaxy root path or specify the '
                    'tool dependency folder directly.'
                    .format(self.galaxy_dir)
                    )
        else:
            self.tool_dependency_dir = os.path.normpath(
                os.path.join(self.galaxy_dir or '', dependency_dir)
                )
            if not os.path.isdir(self.tool_dependency_dir):
                raise FileAccessError(
                    'Could not find a Galaxy tool dependency directory at {0}.'
                    .format(self.tool_dependency_dir)
                    )

    def get_setting (self, token):
        for line_no, line in enumerate(self.config_data):
            if line.startswith(token):
                try:
                    key, value = line.split('=')
                except ValueError:
                    raise FileAccessError(
                        'Unexpected format of configuration file line {0}: {1}.'
                        .format(line_no, line)
                        )
                key = key.rstrip()
                if key == token:
                    value = value.strip()
                    return value, line_no
        return None, -1

    def get_config_file (self):
        for location_guess in self.CONFIG_FILE_GUESSES:
            config_file = os.path.join(self.galaxy_dir, location_guess)
            if os.path.isfile(config_file):
                return os.path.normpath(config_file)

    def get_tool_dependency_dir (self):
        # If the Galaxy config file declares an existing folder as the
        # tool dependency directory, return the absolute path to that folder.
        # If the config file does not set a tool dependency directory explicitly
        # (as is the case if the setting is commented out), return a guess of
        # the default setting if that directory exists.
        # In any other case, return None.
        value, line_no = self.get_setting(self.TOOL_DEP_DIR_REF)
        if line_no == -1:
            value = self.TOOL_DEP_DIR_GUESS
        if value:
            tool_dep_dir = os.path.join(self.galaxy_dir, value)
            if os.path.isdir(tool_dep_dir):
                return os.path.normpath(tool_dep_dir)
            
    def add_to_galaxy (self, line_token = None, expose_samtools = True):
        """Register MiModD and its tool wrappers for Galaxy.

        Updates the Galaxy configuration file to include the MiModD
        tool_conf.xml as a tool_config_file and adds MiModD as a
        Galaxy-resolvable dependency package using an env.sh file.
        Also exposes MiModD's bundled samtools/bcftools as a Galaxy package if
        no such package is configured yet.
        """
        
        # Try to parse the tool_config_file setting from the pre-read
        # configuration file.
        if line_token is None:
            line_token = self.TOOL_CONFIG_FILE_REF
        value, line_no = self.get_setting(line_token)
        if line_no == -1:
            raise OSError(
                'Galaxy configuration file {0} has no {1} setting. '
                'Maybe the line "{1} = ..." has been commented out?'
                .format(self.config_file, line_token)
                )
        conf_files = [file.strip() for file in value.split(',')]

        # expose MiModD as a Galaxy package
        mimodd_dependency_folder = os.path.join(
            self.tool_dependency_dir, 'MiModD', 'externally_managed'
            )
        os.makedirs(mimodd_dependency_folder, exist_ok=True)
        with open(os.path.join(mimodd_dependency_folder, 'env.sh'), 'w') as env:
            env.write('# configure PATH to MiModD binaries\n')
            env.write('PATH="{0}:$PATH"\n'.format(mimodd_settings.bin_path))
            env.write('export PATH\n')

        if expose_samtools:
            # if this instance of Galaxy does not have a samtools Galaxy
            # package configured yet, expose MiModD's bundled version now.
            samtools_dependency_folder = os.path.join(
                self.tool_dependency_dir, 'samtools'
                )
            try:
                os.mkdir(samtools_dependency_folder)
            except FileExistsError:
                pass
            else:
                try:
                    os.symlink(
                        os.path.join('..', 'MiModD', 'externally_managed'),
                        os.path.join(samtools_dependency_folder, 'default'),
                        target_is_directory=True
                        )
                except FileExistsError:
                    # unlikely race condition that we want to ignore
                    pass
            
        if not self.tool_conf_file in conf_files:
            # Add the path to MiModD's tool_conf file to the corresponding
            # setting in the configuration file.
            self.config_data[line_no] = '{0},{1}\n'.format(
                self.config_data[line_no].rstrip(),
                self.tool_conf_file
                )
            
            # ask for user backup before making changes to Galaxy config file
            print('We recommend to back up the Galaxy configuration file {0} '
                  'before proceeding!'
                  .format(self.config_file)
                  )
            confirm = input('Proceed (y/n)? ')
            if confirm != 'y' and confirm != 'Y':
                print('No changes made to Galaxy configuration file. Aborting.')
                return

            # write changes to config file    
            with open(self.config_file, 'w', encoding='utf-8') as config_out:
                try:
                    config_out.writelines(self.config_data)
                except:
                    raise OSError(
                        'We are very sorry, but an error has occurred while '
                        'making changes to the Galaxy configuration file {0}. '
                        'If you have made a backup of the file, you may want '
                        'to use it now.'
                        .format(self.config_file)
                        )
                    
            print('Successfully updated the Galaxy configuration file {0} '
                  'to include the MiModD tools.'
                  .format(self.config_file)
                  )
            print()
        print('Your Galaxy instance is now set up for use of MiModD.')
        print('If Galaxy is currently running, you will have to restart it '
              'for changes to take effect.'
              )
                
        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='\nintegrate this installation of MiModD into '
                    'a local Galaxy.\n'
        )
    parser.add_argument(
        'galaxydir',
        metavar='GALAXY_PATH',
        nargs='?', default=os.getcwd(),
        help="the path to your local Galaxy's root directory (default: the "
             'current working directory);\n'
             'the specified path will serve as the basis for locating the '
             'Galaxy configuration file and the tool dependency folder, '
             'or as the base for relative paths provided through the '
             '--config-file or --dependency-dir options.'
        )
    parser.add_argument(
        '-c', '--config-file',
        metavar='CONFIG_FILE',
        default=argparse.SUPPRESS,
        help='skip autodetection of the Galaxy configuration file and use the '
             'indicated file instead; if CONFIG_FILE is a relative path, it '
             'will be interpreted relative to GALAXY_PATH.'
        )
    parser.add_argument(
        '-d', '--dependency-dir',
        metavar='TOOL_DEPENDENCY_DIR',
        default=argparse.SUPPRESS,
        help='do not try to locate the Galaxy tool dependency folder '
             'automatically, but use the indicated folder directly; '
             'if TOOL_DEPENDENCY_DIR is a relative path, it will be '
             'interpreted relative to GALAXY_PATH.'
        )
    parser.add_argument(
        '-t', '--tool-config-token',
        dest='line_token',
        default=argparse.SUPPRESS,
        help='add the path to the MiModD Galaxy tool wrappers to this variable '
             'in the configuration file (default: tool_config_file)'
        )
    parser.add_argument(
        '--without-samtools',
        dest='expose_samtools',
        action='store_false',
        help='do not try to expose the samtools/bcftools versions bundled with '
             'MiModD as a Galaxy package.'
        )

    args = vars(parser.parse_args())
    # Split up args for the GalaxyAccess instance and its add_to_galaxy method
    # and delegate all further work to them.
    GalaxyAccess(
        **{k: v for k, v in args.items()
           if k in ['galaxydir', 'config_file', 'dependency_dir']}
        ).add_to_galaxy(
            **{k: v for k, v in args.items()
               if k in ['line_token', 'expose_samtools']}
            )
