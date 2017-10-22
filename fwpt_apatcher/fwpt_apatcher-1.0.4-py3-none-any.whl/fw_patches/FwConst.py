'''
Created on 24.08.2010

@author: raidan
'''
# System version
VERSION = "0.4.0"
DEFAULT_ENCODING="windows-1251"
DEFAULT_CONSOLE_ENCODING="cp866"

# Patch apply templates
# Regular expressions
VER_SIMPLE_PATTERN='update[ ]*fw_version[ ]*set [ ]*n_database_ver[ ]*=[ ]*(\d{3,5})[ ]*;'
VER_PROJECT_PATTERN='update[ ]*fw_version_project[ ]*set [ ]*n_database_ver[ ]*=[ ]*(\d{3,5})[ ]* where[ ]*v_project[ ]*=[ ]*\''
VER_PROJECT_PATTERN_END='\'[ ]*;'

# SQL templates
SQL='''
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
SET SERVEROUTPUT ON
SET ECHO ON
SET DEFINE OFF
SET SQLBLANKLINES ON
SET TIMING ON

@{0}

exit
'''
SELECT_SIMPLE_VER='select v_system, n_database_ver from fw_version'
SELECT_PROJECT_VER='select v_project, n_database_ver from fw_version_project where v_project = :proj'


# Patch prepare templates
LAST_VERSION_DIR_POSTFIX='XXXXX'
VERSION_DIR_PREFIX='/2*'
SQL_PATH='*.sql'
VERSION_FILE_TEMPLATE='\d{4}-\d{2}-\d{2}_(\d{5}).sql$'
OUTPUT_NAME_TEMPLATE='{0}/{1}_{2}.sql'
INCLUDE_TEPLATE='''

    
-- <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
-- Include external file "{0}"
-- 
    
{1}
    
-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    
'''
EXECUTE_SAFE_TEMPLATE='''
begin
  execute_('{0}');
end;
/
'''
SVN_ADD='svn add {0}'
CONFIRM_MESSAGE_PREFIX='>>>'


TABLESPACE = 'TABLESPACE'
TABLESPACE_NORMAL = 'BILLING'
TABLESPACE_BIG = 'BILLINGLARGE'
KNOWN_TABLESPACES=[TABLESPACE_BIG, TABLESPACE_NORMAL]



# Generate template properties
SYSOBJECTS_DIR="sysobjects/"
INSTALL_SCRIPTS_DIR="install/scripts/"
PATCHES_DIR="patches/"
SCHEMA_VERSION="init/schema_version.sql"
SCHEMA_VERSION_TEMPLATE='''insert into fw_version(V_SYSTEM, N_DATABASE_VER) values ('{0}', {1});

'''
SCHEMA_VERSION_PROJECT_TEMPLATE='''insert into fw_version_project(V_PROJECT, N_DATABASE_VER) values ('{0}', {1});

'''
