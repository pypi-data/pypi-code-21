'''
Created on 24.08.2010

@author: raidan
'''
# System version
VERSION = '0.9.2'
DEFAULT_ENCODING = 'windows-1251'
DEFAULT_CONSOLE_ENCODING = 'cp866'

SYSTEM = 'Forward Patch System 2, v.' + VERSION

SDK_DIR = 'sdk'
OSS_DIR = 'oss'

# Patch apply templates
# Regular expressions
VER_SIMPLE_PATTERN = '\Aupdate[ ]*(fw_version)[ ]*set [ ]*n_database_ver[ ]*=[ ]*(\d{3,5})[ ]*(;)'
VER_PROJECT_PATTERN = '\Aupdate[ ]*(fw_version_project)[ ]*set [ ]*n_database_ver[ ]*=[ ]*(\d{3,5})[ ]* where[ ]*v_project[ ]*=[ ]*\''
VER_PROJECT_PATTERN_END = '\'[ ]*;'
#exec pack_version.finish_patch_project( aProject => 'FORWARD SDK 1.0', aExpected => %ver%);
#exec pack_version.finish_patch( aVersion => 1937);
#5 matcher = version
VER_SIMPLE_PATTERN_PROC = '\A((exec)|(begin))[ ]*pack_version.finish_patch[ ]*\([ ]*(aVersion =>)?[ ]*(\d{3,5})\);'
#7 matcher = version
VER_PROJECT_PATTERN_PROC = '\A((exec)|(begin))[ ]*pack_version.finish_patch_project[ ]*\([ ]*(aProject => )[ ]*\''
VER_PROJECT_PATTERN_PROC_END = '\'[ ]*,[ ]*(aVersion =>)?[ ]*(\d{3,5})\);'

RE = 're'

SQLPLUS = 'sqlplus -L {0} {1}'
SQLPLUS_GENERATE = 'sqlplus -L {account} @{0}'

# SQL templates
SQL = '''
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
SET SERVEROUTPUT ON
SET ECHO ON
SET DEFINE OFF
SET SQLBLANKLINES ON
SET TIMING ON

@{0}

exit
'''
SELECT_SIMPLE_VER = 'select v_system, n_database_ver from fw_version'
SELECT_PROJECT_VER = 'select v_project, n_database_ver from fw_version_project where v_project = :proj'


# Patch prepare templates
LAST_VERSION_DIR_POSTFIX = 'XXXXXX'
VERSION_DIR_PREFIX = '2*'
SQL_PATH = '*.sql'
VERSION_FILE_TEMPLATE = '\d{4}-\d{2}-\d{2}_(\d{5}).sql$'
INCLUDE_TEPLATE = '''

    
-- <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
-- Include external file "{0}"
--
 
{1}

-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    
'''
EXECUTE_SAFE_TEMPLATE = '''
begin
  execute_('{0}');
end;
/
'''
SVN_ADD = 'svn add {0}'


CONFIRM_MESSAGE_PREFIX = '>>>'


SVN_UPDATE = 'svn update {0}'

OPTION_TEMPLATE_START = '-- <execute-{0}>'
OPTION_TEMPLATE_END = '-- </execute-{0}>'

DYNAMIC_START = '-- ##<if>'
DYNAMIC_END = '-- ##</if>'

DBOPTION_PARTITIONING='partitions'
KNOWN_DBOPTIONS=[DBOPTION_PARTITIONING]

TABLESPACE = 'TABLESPACE'
TABLESPACE_ARCHIVE = '_ARCHIVE_'
TABLESPACE_NORMAL = '_NORMAL_'
TABLESPACE_BIG = '_BIG_'
KNOWN_TABLESPACES=[TABLESPACE_NORMAL, TABLESPACE_BIG, TABLESPACE_ARCHIVE]


# Generate template properties
INSTALL_DIR = 'install'
SYSOBJECTS_DIR = 'sysobjects'
INSTALL_SCRIPTS_DIR = INSTALL_DIR + '/scripts/'
START_AQ_SCRIPT = [INSTALL_SCRIPTS_DIR + 'start_all_queues.sql']
PATCHES_DIR = 'patches'
INIT_DIR = "init"
SCHEMA_VERSION = 'schema_version.sql'
SCHEMA_VERSION_TEMPLATE = '''insert into fw_version(V_SYSTEM, N_DATABASE_VER) values ('{0}', {1});

'''
SCHEMA_VERSION_PROJECT_TEMPLATE = '''insert into fw_version_project(V_PROJECT, N_DATABASE_VER) values ('{0}', {1});

'''


EXCLUDE_PREFIX = '-'
ROOT_PREFIX = '!'
CHECK_DBOPTION_PREFIX = '+'
SKIP_COMPRESS = '~'

AUTO_TYPE = '[ ]*create[ ]*or[ ]*replace[ ]*type[ ]*([^ ]*)[ ]*(as|is)[ ]*'