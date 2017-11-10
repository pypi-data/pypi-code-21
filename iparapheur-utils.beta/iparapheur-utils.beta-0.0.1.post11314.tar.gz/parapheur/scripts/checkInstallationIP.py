#!/usr/bin/env python
# coding=utf-8

"""
CeCILL Copyright (c) 2016-2017, Libriciel SCOP
Initiated and by Libriciel SCOP

contact@libriciel.coop

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant
donné sa spécificité de logiciel libre, qui peut le rendre complexe à
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement,
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.
"""

from parapheur.parapheur import pprint  # Colored printer
import io
import os
import subprocess
import socket
import hashlib
import sys
import platform
import multiprocessing
import requests
# import MySQLdb
import pymysql.cursors
from pymysql.constants import ER
# from packaging import version
from pkg_resources import parse_version
from urlparse import urlparse

req_version = (3, 0)
cur_version = sys.version_info
isp3 = cur_version >= req_version
# pprint.log(cur_version)

if isp3:
    from io import StringIO
    # noinspection PyCompatibility
    import configparser as ConfigParser
else:
    # noinspection PyCompatibility
    from StringIO import StringIO
    # noinspection PyCompatibility
    import ConfigParser

__author__ = 'Stephane Vast'
__version__ = '1.0.1'

defaut_install_depot = "/opt/_install"
defaut_iparapheur_root = "/opt/iParapheur"
versionIP_minimum = "4.3.0"
mysqluser = "alf"
mysqlpwd = ""
mysqlbase = ""


def isexistsdirectory(repertoire):
    pprint.header("#", False, ' ')
    pprint.info("Répertoire", False, ' ')
    pprint.info(repertoire.ljust(35), True, ' ')
    if os.path.exists(repertoire):
        pprint.success('{:>10s}'.format("OK"), True)
        return True
    else:
        pprint.warning('{:>10s}'.format("absent"))
        return False


def isexistssubdir(repertoire, sousrep):
    pprint.header("#", False, ' ')
    pprint.info("  subdir", False, ' ')
    pprint.info(sousrep.ljust(37), True, ' ')
    if os.path.exists("{0}/{1}".format(repertoire, sousrep)):
        pprint.success('{:>10s}'.format("OK"), True)
        return True
    else:
        pprint.warning('{:>10s}'.format("absent"))
        return False


def isexistsfile(repertoire, fichier):
    pprint.header("#", False, ' ')
    pprint.info(" fichier", False, ' ')
    pprint.info(fichier.ljust(37), True, ' ')
    if os.path.exists("{0}/{1}".format(repertoire, fichier)):
        pprint.success('{:>10s}'.format("OK"), True)
        return True
    else:
        pprint.warning('{:>10s}'.format("absent"))
        return False


def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def showtheheader():
    pprint.header('{:30s}{:>30s}'.format('Tests opérés pour i-Parapheur', 'Resultat'))
    pprint.header('=' * 60)
    pprint.header("# Check list pour", False, ' ')
    pprint.log("i-Parapheur", True, ' ')
    pprint.header("       résultats:", False, ' ')
    pprint.success("OK", True, ' ')
    pprint.warning("warn", True, ' ')
    pprint.error("Fail", True)
    pprint.header("# ")


# TESTS sur PRE-REQUIS: hardware (CPU  , RAM )
'''     Hardware    : nb CPU  , RAM , taille Disque ?
		OS Linux    : nom + version / NeSaitPas
		MySQL       : version? .... / NeSaitPas , local/déporté
		NginX       : version? .... / NeSaitPas , local/déporté
		JDK serveur : version? .... / NeSaitPas
		LibreOffice : version? .... / NeSaitPas
		GhostScript : version? .... / NeSaitPas
	Pour i-Parapheur, sécurité:
		Fournisseur certificats HTTPS (web,WS): ... , ... / NeSaitPas
		Date d'expiration cert. HTTPS (web,WS): ... , ... / NeSaitPas
		Version LiberSign : .....  / NeSaitPas	'''


# nb CPU - BASH: grep -c "processor" /proc/cpuinfo
def check_hardware():
    pprint.header("#", False, ' ')
    pprint.log("---- Check pre-requis systeme ----", True)

    pprint.header("#", False, ' ')
    pprint.info("Nombre de CPU disponibles (minimum 4)".ljust(46), False, ' ')
    nbcpu = multiprocessing.cpu_count()
    if nbcpu >= 4:
        pprint.success('{:>10d}'.format(nbcpu), True)
    elif nbcpu >= 2:
        pprint.warning('{:>10d}'.format(nbcpu))
    else:
        pprint.error('{:>10d}'.format(nbcpu))

    pprint.header("#", False, ' ')
    pprint.info("Taille Memoire totale (minimum 5 Go)".ljust(46), False, ' ')
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
    mem_gib = mem_bytes / (1024. ** 3)  # e.g. 3.74
    if mem_gib >= 4.5:
        pprint.success('{:>7.2f} Go'.format(mem_gib), True)
    elif mem_gib > 3.75:
        pprint.warning('{:>7.2f} Go'.format(mem_gib))
    else:
        pprint.error('{:>7.2f} Go'.format(mem_gib))

    pprint.header("#", False, ' ')
    pprint.info("Plateforme {0} : architecture {1}".format(os.uname()[0], os.uname()[4]).ljust(46), False, ' ')
    l_arch = platform.architecture()[0]
    if l_arch == "64bit":
        pprint.success('{:>10s}'.format(l_arch), True)
    else:
        pprint.error('{:>10s}'.format(l_arch), True)
        pprint.error("Erreur: Le systeme doit etre 64bit pour recevoir i-Parapheur. STOP", True)
        sys.exit()
    #	pprint.log(platform.platform())
    #	pprint.log(platform.release())
    #	pprint.log(platform.system()) # Linux
    #	pprint.log(platform.version())
    pprint.header("#", False, ' ')
    # pprint.log(platform.linux_distribution())  # ('Ubuntu', '16.04', 'xenial')
    pprint.info("Distribution: {0} {1} ({2})".format(platform.linux_distribution()[0],
                                                     platform.linux_distribution()[1],
                                                     platform.linux_distribution()[2]).ljust(46), False, ' ')
    if platform.linux_distribution()[0] == 'Ubuntu':
        if platform.linux_distribution()[1] == '16.04':
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1] == '14.04':
            pprint.warning('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1] == '12.04':
            pprint.warning('{:>10s}'.format("migrer"), True)
        else:
            pprint.error('{:>10s}'.format("A qualifier"), True)
    elif platform.linux_distribution()[0] == 'debian':
        if platform.linux_distribution()[1].startswith('9'):
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1].startswith('8'):
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1].startswith('7'):
            pprint.warning('{:>10s}'.format("OK"), True)
        else:
            pprint.error('{:>10s}'.format("non conforme"), True)
    elif platform.linux_distribution()[0] == 'CentOS Linux':
        if platform.linux_distribution()[1].startswith('7'):
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1].startswith('6'):
            pprint.warning('{:>10s}'.format("OK"), True)
        else:
            pprint.error('{:>10s}'.format("non conforme"), True)
    else:  # ajouter RHEL: 'SuSE', 'redhat', 'mandrake'
        pprint.error('{:>10s}'.format("inconnu"), True)

    pprint.header("#", False, ' ')
    pprint.info("swappiness (valeur <=10)".ljust(46), False, ' ')
    PROCFS_PATH = "/proc/sys/vm/swappiness"
    if os.path.isfile(PROCFS_PATH) and os.access(PROCFS_PATH, os.R_OK):
        myfile = open(PROCFS_PATH, 'r')
        for line in myfile:
            swappiness = int(line.rstrip("\n"))
            if swappiness > 10:
                pprint.error('{:>10d}'.format(swappiness), True)
            else:
                pprint.success('{:>10d}'.format(swappiness), True)
        myfile.close()


# pprint.log(os.getlogin())
# pprint.log(os.uname())


def check_server_socket(address, port):
    # Create a TCP socket
    s = socket.socket()
    # print "Attempting to connect to %s on port %s" % (address, port)
    try:
        s.connect((address, port))
        # print "Connected to %s on port %s" % (address, port)
        s.close()
        return True
    except socket.error as e:
        print("Connection to %s on port %s failed: %s" % (address, port, e))
        return False


def issitereachable(theurl):
    pprint.header("#", False, ' ')
    pprint.info("Test site {0}".format(theurl).ljust(46), False, ' ')

    response = requests.get(theurl)

    if not response.ok:
        pprint.error('{:>10s}'.format("Erreur"), True)
        pprint.error("Erreur lors de la requête {0}: Code d'erreur {1}".
                     format(theurl, response.status_code),
                     True)
        pprint.error(response.getvalue())
    else:
        pprint.success('{:>10s}'.format("OK"), True)


# besoin HTTP/HTTPS sortant, accès http://crl.adullact.org http://libersign.adullact-projet.fr
def check_network_needed():
    pprint.header("#", False, ' ')
    pprint.log("---- Check pre-requis reseau ----", True)
    issitereachable("http://crl.adullact.org")
    issitereachable("http://libersign.adullact-projet.fr")


# pprint.error('{:>10s}'.format("non fait"), True)


def check_mandatory_command(thecommand):
    pprint.header("#", False, ' ')
    pprint.info("Commande : {0}".format(thecommand).ljust(46), False, ' ')
    if which(thecommand):
        pprint.success('{:>10s}'.format("OK"))
    else:
        pprint.error('{:>10s}'.format("Absent"), True)


def check_required_software():
    pprint.header("#", False, ' ')
    pprint.log("---- Check pre-requis logiciels selon manuel ----", True)

    if isexistsdirectory(defaut_install_depot):
        isexistssubdir(defaut_install_depot, "confs")
    if not isexistsdirectory(defaut_iparapheur_root):
        pprint.error("Erreur: Le répertoire {0} doit être présent. STOP".format(defaut_iparapheur_root), True)
        sys.exit()

    da_commands = ['at', 'tar', 'crontab', 'unzip', 'mailx',
                   'mysql', 'mysqldump', 'mysqlcheck', '/opt/java/jdk1.6.0_45/bin/java']
    for to_test in da_commands:
        check_mandatory_command(to_test)
    # check_mandatory_command("FauxPositif")


def check_smtp_needed(smtp_srv):
    pprint.header("#", False, ' ')
    pprint.log("---- Check SMTP ----", True)
    if check_server_socket(smtp_srv, 25):
        pprint.info("un service SMTP est présent sur {0}".format(smtp_srv).ljust(46), False, ' ')
        pprint.success("ok")
    else:
        pprint.warning("ko")
    pprint.warning('{:>10s}'.format("TODO"), True)


def check_https_service_config():
    pprint.header("#", False, ' ')
    pprint.log("---- Check configuration service HTTPS basique ----", True)

    if not isexistsdirectory("/etc/nginx"):
        pprint.header("#   ", False, ' ')
        pprint.warning("Pas de configuration NginX, c'est pourtant le serveur HTTPS à utiliser", True)
        return False
    isexistsdirectory("/etc/nginx/conf.d")
    if isexistsdirectory("/etc/nginx/ssl"):
        isexistsfile("/etc/nginx/ssl", "recup_crl_nginx.sh")
        isexistssubdir("/etc/nginx/ssl", "validca")

    # Vérifier process Nginx pas trop vieux (p/r lancement crontab) ?
    line = subprocess.check_output('nginx -v', stderr=subprocess.STDOUT, shell=True).decode("utf-8")
    outl, outr = line.rstrip("\n").split("nginx/")
    pprint.header("#", False, ' ')
    pprint.info("Version detectee NginX:     {0}".format(outr.rstrip()).ljust(46), False, ' ')
    # if version.parse("1.8.0") < version.parse(outr.rstrip()):
    if parse_version("1.8.0") < parse_version(outr.rstrip()):
        pprint.success('{:>10s}'.format(">1.8.0, OK"), True)
    else:
        pprint.error('{:>10s}'.format("< 1.8.0"), True)

    nginxserver = "localhost"
    nginxport = 443
    pprint.header("#", False, ' ')
    pprint.info("Service NginX sur {0}:{1}".format(nginxserver, nginxport).ljust(46), False, ' ')
    if not check_server_socket(nginxserver, nginxport):
        pprint.warning('{:>10s}'.format("inactif"), True)
    else:
        pprint.success('{:>10s}'.format("actif"), True)

    print("   CAVEAT: tests sur certificat valide, validca OK, etc.")


## OpenSSL: récupérer la chaîne de certificats SSL d’un host
## https://blog.hbis.fr/2017/02/11/openssl-certificate_chain/
# echo | openssl s_client -connect iparapheurfl.demonstrations.libriciel.fr:443 -showcerts 2>&1 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > mycert.pem




def check_mysql_service_config(varconf):
    pprint.header("#", False, ' ')
    pprint.log("---- Check configuration service MySQL ----  TODO", True)

    # Extract mysqlserver from db.url schema: 
    # defaults to: db.url=jdbc:mysql://localhost/alfresco 
    # so cut out the 'jdbc:' stream and parse the resulting URL afterwards
    mysqldburl = varconf.get("Parapheur", "db.url")
    urlparsed = urlparse(mysqldburl[5:])
    #pprint.info(urlparsed)
    mysqlserver = urlparsed.hostname  # "localhost"
    mysqlport = 3306

    pprint.header("#", False, ' ')
    pprint.info("Service MySQL sur {0}:{1}".format(mysqlserver, mysqlport).ljust(46), False, ' ')
    if not check_server_socket(mysqlserver, mysqlport):
        pprint.warning('{:>10s}'.format("inactif"), True)
        return False
    else:
        pprint.success('{:>10s}'.format("actif"), True)

        mysqluser = varconf.get("Parapheur", "db.username")
        mysqlpwd = varconf.get("Parapheur", "db.password")
        mysqlbase = varconf.get("Parapheur", "db.name")
        pprint.header("#", False, ' ')
        pprint.info("DB '{3}' sur {0}@{1}:{2}".format(mysqluser, mysqlserver, mysqlport, mysqlbase).ljust(46), False,
                    ' ')

        try:
            cur_max_cnx = ""
            parametre_mysql = ""

            cnx = pymysql.connect(user=mysqluser, password=mysqlpwd,
                                          host=mysqlserver, database=mysqlbase)
            pprint.success('{:>10s}'.format("OK"), True)

            cursor = cnx.cursor()
            query = "SELECT @@GLOBAL.max_connections as res;"
            cursor.execute(query)
            for res in cursor:
                cur_max_cnx = res[0]
            pprint.header("#", False, ' ')
            pprint.info('Nombre de connexions maxi      = {:>6d}'.format(cur_max_cnx).ljust(46), False, ' ')
            if cur_max_cnx < 360:
                pprint.error('{:>10s}'.format("< 360"), True)
            else:
                pprint.success('{:>10s}'.format(">=360, OK"), True)

            query = "SELECT @@GLOBAL.innodb_file_per_table as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('innodb_file_per_table          = {0:>6d}'.format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql != 1:
                pprint.error('{0:>10s}'.format("!= 1"), True)
            else:
                pprint.success('{0:>10s}'.format("=1, OK"), True)

            query = "SELECT @@GLOBAL.open_files_limit as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('open_files_limit               = {0:>6d}'.format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql < 8192:
                pprint.error('{0:>10s}'.format("< 8192"), True)
            else:
                pprint.success('{0:>10s}'.format(" OK"), True)

            query = "SELECT @@GLOBAL.wait_timeout as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('wait_timeout                   = {0:>6d}'.format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql < 28800:
                pprint.error('{0:>10s}'.format("< 28800"), True)
            else:
                pprint.success('{0:>10s}'.format("  OK"), True)

            query = "SELECT @@GLOBAL.innodb_locks_unsafe_for_binlog as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('innodb_locks_unsafe_for_binlog = {0:>6d}'.format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql != 1:
                pprint.error('{0:>10s}'.format("!= 1"), True)
            else:
                pprint.success('{0:>10s}'.format("=1, OK"), True)

            cursor.close()

        except pymysql.Error as err:
            pprint.error('{0:>10s}'.format("Erreur"), True)
            if err.errno == ER.ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == ER.BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            cnx.close()
        pprint.warning('{0:>10s}'.format("TODO"), True)


def check_isexists_alfrescoglobal():
    pprint.header("#", False, ' ')
    pprint.log("---- Exists alfresco-global.properties  ? ----  ", True)

    # Alfresco-global.properties
    isexistsdirectory(defaut_iparapheur_root)
    isexistssubdir(defaut_iparapheur_root, "tomcat/shared/classes")
    return isexistsfile("{0}/tomcat/shared/classes".format(defaut_iparapheur_root), "alfresco-global.properties")


def check_config_alfrescoglobal(varconf):
    pprint.header("#", False, ' ')
    pprint.log("---- Check alfresco-global.properties ----  TODO", True)

    alf_dir_root = varconf.get("Parapheur", "dir.root")
    # pprint.info(varconf.options("Parapheur"))
    # pprint.info(varconf.items("Parapheur"))

    pprint.header("#", False, ' ')
    pprint.info("alf_dir_root = {0}".format(alf_dir_root))
    pprint.header("#", False, ' ')
    pprint.info("database URL = {0}".format(varconf.get("Parapheur", "db.url")))


def check_config_ghostscript():
    pprint.header("#", False, ' ')
    pprint.log("---- Check config GhostScript ----", True)
    libgs_path = defaut_iparapheur_root + "/common/lib/libgs.so"
    if not isexistsfile("{0}/common/lib".format(defaut_iparapheur_root), "libgs.so"):
        return
    libgsstat = os.stat(libgs_path)
    pprint.header("#", False, ' ')
    pprint.info("Taille libgs.so = {0} octets".format(libgsstat.st_size).ljust(46), False, ' ')
    if libgsstat.st_size < 19 * 1024 * 1024:
        pprint.error('{0:>10s}'.format("< 19Mo"), True)
    else:
        pprint.success('{0:>10s}'.format("> 19Mo, OK"), True)
    command_line = "ldconfig -n /opt/iParapheur/common/lib/ -v | grep libgs.so"
    output = subprocess.check_output(command_line, shell=True)
    outl, outr = output.split("-> ")
    pprint.header("#", False, ' ')
    pprint.info("Version detectee: {0}".format(outr.rstrip()), False)


def check_files_needed():
    pprint.header("#", False, ' ')
    pprint.log("---- Check présence fichiers post-config ----", True)
    da_files = ['backup_parapheur.sh', 'custom-wsdl.sh',
                'deployWarIparapheur.sh', 'iparaph-updateAMP.sh',
                'logrotate-iparapheur.conf', 'nettoieEntrepot.sh', 'nettoieLogs.sh',
                'purge-xemwebview.sh', 'srgb.profile', 'verdanai.ttf',
                'warn_needPurge.sh']
    for to_test in da_files:
        isexistsfile("/opt/iParapheur", to_test)


# chapitre  XEMELIOS
def check_xemwebview_service_config():
    pprint.header("#", False, ' ')
    pprint.log("---- Check configuration service Xemwebviewer ----  TODO", True)
    isexistsfile("/etc/init.d", "xemwebview")
    if not isexistsdirectory("/var/tmp/bl-xemwebviewer"):
        pprint.header("#   ", False, ' ')
        pprint.warning("Le service Xemelios ne fonctionnera pas: manquent les répertoires temporaires.")
    else:
        da_reps = ['xwv-cache', 'xwv-extract', 'xwv-shared']
        for to_test in da_reps:
            if not isexistssubdir("/var/tmp/bl-xemwebviewer", to_test):
                pprint.header("#   ", False, ' ')
                pprint.warning("Le service Xemelios ne fonctionnera pas: manque le répertoire {0}.".format(to_test))

# chapitre anti-fraude
def guess_iParapheur_version(basedir):
    pprint.header("#", False, ' ')
    IP_MODULE_PATH = "{0}/{1}".format(basedir, "tomcat/webapps/iparapheur/META-INF/maven/org.adullact.iparapheur/iparapheur-surf-webapp/pom.properties")
    if not os.path.exists(IP_MODULE_PATH):
        pprint.error("Impossible de deviner la version de i-Parapheur")
        return -1
    with open(IP_MODULE_PATH, 'r') as f:
        module_string = '[Parapheur]\n' + f.read()
    module_fp = io.BytesIO(module_string)
    leMdodule = ConfigParser.RawConfigParser()
    leMdodule.readfp(module_fp)
    versionIP = leMdodule.get("Parapheur", "version")
    pprint.info("Version detectee sur le serveur:", False, ' ')
    if "SNAPSHOT" in versionIP:
        pprint.warning('{:>13s}'.format("Problème de détection"), True)
    elif parse_version(versionIP_minimum) <= parse_version(versionIP):
        pprint.success('{:>10s}'.format(versionIP), False, ' ')
        pprint.success('{:>13s}'.format(" >4.3.0, OK"), True)
    else:
        pprint.success('{:>10s}'.format(versionIP), False, ' ')
        pprint.error('{:>13s}'.format("non supportée"), True)
    return versionIP

def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def check_iParapheur_version_is_valid(basedir):
    pprint.header("#", False, ' ')
    pprint.log("---- Check i-Parapheur version ----  TODO", True)
    da_version = guess_iParapheur_version(basedir)

    if da_version == -1:
        return

    da_file = "{0}/{1}".format(basedir, "tomcat/webapps/alfresco.war")
    if os.path.exists(da_file):
        pprint.info("   alfresco.war  trouvé")
        pprint.info("Hash WAR: {0}".format(sha256_checksum(da_file)), False)
    else:
        pprint.header("#   ", False, ' ')
        pprint.warning(" webapp 'alfresco.war' introuvable, normal???")


################################################################
################################################################
showtheheader()
check_hardware()
check_network_needed()
check_required_software()
check_smtp_needed("localhost")

check_https_service_config()

if not check_isexists_alfrescoglobal():
    pprint.error("BAD")
    sys.exit()

ALF_CONFIG_PATH = "{0}/tomcat/shared/classes/alfresco-global.properties".format(defaut_iparapheur_root)
'''
def get_config_app(varfichier):
	### lire https://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/25493615#25493615
	####   https://stackoverflow.com/questions/2885190/using-pythons-configparser-to-read-a-file-without-section-name
	with open(varfichier, 'r') as f:
	    config_string = '[Parapheur]\n' + f.read()
	# config_fp = StringIO.StringIO(config_string)
	config_fp = io.BytesIO(config_string)
	config = ConfigParser.RawConfigParser()
	return config.readfp(config_fp)
'''
with open(ALF_CONFIG_PATH, 'r') as f:
    config_string = '[Parapheur]\n' + f.read()
config_fp = io.BytesIO(config_string)
config = ConfigParser.RawConfigParser()
config.readfp(config_fp)
# alfrescoconfig = get_config_app(CONFIG_PATH)
# print(config.items("Parapheur"))
# print(config.get("Parapheur", "dir.root"))

# check health of MySQL configuration
check_mysql_service_config(config)

check_config_alfrescoglobal(config)

# check  "libgs"
check_config_ghostscript()

# tests présence verdanai.ttf , srgb.profile ,etc.
check_files_needed()

# ulimit dans alfresco.sh
# ctl.sh : limite à 30 mini pour shutdown

check_xemwebview_service_config()

check_iParapheur_version_is_valid(defaut_iparapheur_root)
pprint.info(".end.")
