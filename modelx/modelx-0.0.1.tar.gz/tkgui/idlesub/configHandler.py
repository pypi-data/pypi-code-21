""" IDLE branch 3.4. stripped version, only reading capabilities """
import os
import sys

from configparser import ConfigParser
from tkinter import TkVersion
from tkinter.font import Font

class InvalidConfigType(Exception): pass
class InvalidConfigSet(Exception): pass
class InvalidFgBg(Exception): pass
class InvalidTheme(Exception): pass


class IdleConfParser(ConfigParser):
    """
    A ConfigParser specialised for idle configuration file handling
    """
    def __init__(self, cfgFile, cfgDefaults=None):
        """
        cfgFile - string, fully specified configuration file name
        """
        self.file = cfgFile
        ConfigParser.__init__(self, defaults=cfgDefaults, strict=False)

    def Get(self, section, option, type=None, default=None, raw=False):
        """
        Get an option value for given section/option or return default.
        If type is specified, return as type.
        """
        # TODO Use default as fallback, at least if not None
        # Should also print Warning(file, section, option).
        # Currently may raise ValueError
        if not self.has_option(section, option):
            return default
        if type == 'bool':
            return self.getboolean(section, option)
        elif type == 'int':
            return self.getint(section, option)
        else:
            return self.get(section, option, raw=raw)

    def GetOptionList(self, section):
        "Return a list of options for given section, else []."
        if self.has_section(section):
            return self.options(section)
        else:  #return a default value
            return []

    def Load(self):
        "Load the configuration file from disk."
        self.read(self.file)


class IdleUserConfParser(IdleConfParser):
    """
    IdleConfigParser specialised for user configuration handling.
    """
    def IsEmpty(self):
        "Return True if no sections after removing empty sections."
        return not self.sections()


class IdleConf:
    """Hold config parsers for all idle config files in singleton instance.

    Default config files, self.defaultCfg --
        for config_type in self.config_types:
            (idle install dir)/config-{config-type}.def

    User config files, self.userCfg --
        for config_type in self.config_types:
        (user home dir)/.idlerc/config-{config-type}.cfg
    """
    def __init__(self):
        self.config_types = ('main', 'extensions', 'highlight', 'keys')
        self.defaultCfg = {}
        self.userCfg = {}
        self.cfg = {}  # TODO use to select userCfg vs defaultCfg
        self.CreateConfigHandlers()
        self.LoadCfgFiles()

    def CreateConfigHandlers(self):
        "Populate default and user config parser dictionaries."
        #build idle install path
        if __name__ != '__main__': # we were imported
            idleDir=os.path.dirname(__file__)
        else: # we were exec'ed (for testing only)
            idleDir=os.path.abspath(sys.path[0])
        userDir=self.GetUserCfgDir()

        defCfgFiles = {}
        usrCfgFiles = {}
        # TODO eliminate these temporaries by combining loops
        for cfgType in self.config_types: #build config file names
            defCfgFiles[cfgType] = os.path.join(
                    idleDir, 'config-' + cfgType + '.def')
            usrCfgFiles[cfgType] = os.path.join(
                    userDir, 'config-' + cfgType + '.cfg')
        for cfgType in self.config_types: #create config parsers
            self.defaultCfg[cfgType] = IdleConfParser(defCfgFiles[cfgType])
            self.userCfg[cfgType] = IdleUserConfParser(usrCfgFiles[cfgType])

    def GetUserCfgDir(self):
        """Return a filesystem directory for storing user config files.

        Creates it if required.
        """
        cfgDir = '.idlerc'
        userDir = os.path.expanduser('~')
        if userDir != '~': # expanduser() found user home dir
            if not os.path.exists(userDir):
                warn = ('\n Warning: os.path.expanduser("~") points to\n ' +
                        userDir + ',\n but the path does not exist.')
                try:
                    print(warn, file=sys.stderr)
                except OSError:
                    pass
                userDir = '~'
        if userDir == "~": # still no path to home!
            # traditionally IDLE has defaulted to os.getcwd(), is this adequate?
            userDir = os.getcwd()
        userDir = os.path.join(userDir, cfgDir)
        if not os.path.exists(userDir):
            try:
                os.mkdir(userDir)
            except OSError:
                warn = ('\n Warning: unable to create user config directory\n' +
                        userDir + '\n Check path and permissions.\n Exiting!\n')
                print(warn, file=sys.stderr)
                raise SystemExit
        # TODO continue without userDIr instead of exit
        return userDir

    def GetOption(self, configType, section, option, default=None, type=None,
                  warn_on_default=True, raw=False):
        """Return a value for configType section option, or default.

        If type is not None, return a value of that type.  Also pass raw
        to the config parser.  First try to return a valid value
        (including type) from a user configuration. If that fails, try
        the default configuration. If that fails, return default, with a
        default of None.

        Warn if either user or default configurations have an invalid value.
        Warn if default is returned and warn_on_default is True.
        """
        try:
            if self.userCfg[configType].has_option(section, option):
                return self.userCfg[configType].Get(section, option,
                                                    type=type, raw=raw)
        except ValueError:
            warning = ('\n Warning: configHandler.py - IdleConf.GetOption -\n'
                       ' invalid %r value for configuration option %r\n'
                       ' from section %r: %r' %
                       (type, option, section,
                       self.userCfg[configType].Get(section, option, raw=raw)))
            try:
                print(warning, file=sys.stderr)
            except OSError:
                pass
        try:
            if self.defaultCfg[configType].has_option(section,option):
                return self.defaultCfg[configType].Get(
                        section, option, type=type, raw=raw)
        except ValueError:
            pass
        #returning default, print warning
        if warn_on_default:
            warning = ('\n Warning: configHandler.py - IdleConf.GetOption -\n'
                       ' problem retrieving configuration option %r\n'
                       ' from section %r.\n'
                       ' returning default value: %r' %
                       (option, section, default))
            try:
                print(warning, file=sys.stderr)
            except OSError:
                pass
        return default

    def GetSectionList(self, configSet, configType):
        """Return sections for configSet configType configuration.

        configSet must be either 'user' or 'default'
        configType must be in self.config_types.
        """
        if not (configType in self.config_types):
            raise InvalidConfigType('Invalid configType specified')
        if configSet == 'user':
            cfgParser = self.userCfg[configType]
        elif configSet == 'default':
            cfgParser=self.defaultCfg[configType]
        else:
            raise InvalidConfigSet('Invalid configSet specified')
        return cfgParser.sections()

    def GetHighlight(self, theme, element, fgBg=None):
        """Return individual theme element highlight color(s).

        fgBg - string ('fg' or 'bg') or None.
        If None, return a dictionary containing fg and bg colors with
        keys 'foreground' and 'background'.  Otherwise, only return
        fg or bg color, as specified.  Colors are intended to be
        appropriate for passing to Tkinter in, e.g., a tag_config call).
        """
        if self.defaultCfg['highlight'].has_section(theme):
            themeDict = self.GetThemeDict('default', theme)
        else:
            themeDict = self.GetThemeDict('user', theme)
        fore = themeDict[element + '-foreground']
        if element == 'cursor':  # There is no config value for cursor bg
            back = themeDict['normal-background']
        else:
            back = themeDict[element + '-background']
        highlight = {"foreground": fore, "background": back}
        if not fgBg:  # Return dict of both colors
            return highlight
        else:  # Return specified color only
            if fgBg == 'fg':
                return highlight["foreground"]
            if fgBg == 'bg':
                return highlight["background"]
            else:
                raise InvalidFgBg('Invalid fgBg specified')

    def GetThemeDict(self, type, themeName):
        """Return {option:value} dict for elements in themeName.

        type - string, 'default' or 'user' theme type
        themeName - string, theme name
        Values are loaded over ultimate fallback defaults to guarantee
        that all theme elements are present in a newly created theme.
        """
        if type == 'user':
            cfgParser = self.userCfg['highlight']
        elif type == 'default':
            cfgParser = self.defaultCfg['highlight']
        else:
            raise InvalidTheme('Invalid theme type specified')
        # Provide foreground and background colors for each theme
        # element (other than cursor) even though some values are not
        # yet used by idle, to allow for their use in the future.
        # Default values are generally black and white.
        # TODO copy theme from a class attribute.
        theme ={'normal-foreground':'#000000',
                'normal-background':'#ffffff',
                'keyword-foreground':'#000000',
                'keyword-background':'#ffffff',
                'builtin-foreground':'#000000',
                'builtin-background':'#ffffff',
                'comment-foreground':'#000000',
                'comment-background':'#ffffff',
                'string-foreground':'#000000',
                'string-background':'#ffffff',
                'definition-foreground':'#000000',
                'definition-background':'#ffffff',
                'hilite-foreground':'#000000',
                'hilite-background':'gray',
                'break-foreground':'#ffffff',
                'break-background':'#000000',
                'hit-foreground':'#ffffff',
                'hit-background':'#000000',
                'error-foreground':'#ffffff',
                'error-background':'#000000',
                #cursor (only foreground can be set)
                'cursor-foreground':'#000000',
                #shell window
                'stdout-foreground':'#000000',
                'stdout-background':'#ffffff',
                'stderr-foreground':'#000000',
                'stderr-background':'#ffffff',
                'console-foreground':'#000000',
                'console-background':'#ffffff' }
        for element in theme:
            if not cfgParser.has_option(themeName, element):
                # Print warning that will return a default color
                warning = ('\n Warning: configHandler.IdleConf.GetThemeDict'
                           ' -\n problem retrieving theme element %r'
                           '\n from theme %r.\n'
                           ' returning default color: %r' %
                           (element, themeName, theme[element]))
                try:
                    print(warning, file=sys.stderr)
                except OSError:
                    pass
            theme[element] = cfgParser.Get(
                    themeName, element, default=theme[element])
        return theme

    def CurrentTheme(self):
        """Return the name of the currently active text color theme.

        idlelib.config-main.def includes this section
        [Theme]
        default= 1
        name= IDLE Classic
        name2=
        # name2 set in user config-main.cfg for themes added after 2015 Oct 1

        Item name2 is needed because setting name to a new builtin
        causes older IDLEs to display multiple error messages or quit.
        See https://bugs.python.org/issue25313.
        When default = True, name2 takes precedence over name,
        while older IDLEs will just use name.
        """
        default = self.GetOption('main', 'Theme', 'default',
                                 type='bool', default=True)
        if default:
            theme = self.GetOption('main', 'Theme', 'name2', default='')
        if default and not theme or not default:
            theme = self.GetOption('main', 'Theme', 'name', default='')
        source = self.defaultCfg if default else self.userCfg
        if source['highlight'].has_section(theme):
            return theme
        else:
            return "IDLE Classic"

    def GetFont(self, root, configType, section):
        """Retrieve a font from configuration (font, font-size, font-bold)
        Intercept the special value 'TkFixedFont' and substitute
        the actual font, factoring in some tweaks if needed for
        appearance sakes.

        The 'root' parameter can normally be any valid Tkinter widget.

        Return a tuple (family, size, weight) suitable for passing
        to tkinter.Font
        """
        family = self.GetOption(configType, section, 'font', default='courier')
        size = self.GetOption(configType, section, 'font-size', type='int',
                              default='10')
        bold = self.GetOption(configType, section, 'font-bold', default=0,
                              type='bool')
        if (family == 'TkFixedFont'):
            if TkVersion < 8.5:
                family = 'Courier'
            else:
                f = Font(name='TkFixedFont', exists=True, root=root)
                actualFont = Font.actual(f)
                family = actualFont['family']
                size = actualFont['size']
                if size < 0:
                    size = 10  # if font in pixels, ignore actual size
                bold = actualFont['weight']=='bold'
        return (family, size, 'bold' if bold else 'normal')

    def LoadCfgFiles(self):
        """Load all configuration files."""
        for key in self.defaultCfg:
            self.defaultCfg[key].Load()
            self.userCfg[key].Load() #same keys

idleConf = IdleConf()
