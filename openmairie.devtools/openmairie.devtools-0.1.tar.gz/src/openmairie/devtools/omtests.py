#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import re
import shutil
import sys

import ConfigParser
import tempfile
import re
import fileinput

DOC_TEMPLATE = """
*** Settings ***
Documentation  Mots-clefs %s rédigés en Robot Framework et employables dans les tests fonctionnels.
...    Cette documentation est générée par l'outil 'Libdoc' à partir des ressources du répertoire tests/resources/%s.

*** Keywords ***

"""

class OMTests(object):
    """
    """

    line1 = "=============================================================================="
    line2 = "------------------------------------------------------------------------------"
    _document_root = "/var/www/"
    _database_name_default = "openexemple"
    _instance_name_default = "openexemple"
    _params_delete_files = []
    _params_create_folders = []
    _params_copy_files = []
    _params_chmod_777 = []

    def __init__(self):
        """
        """
        #
        self._init_instance_path()
        #
        self._init_args_parser()
        #
        self._init_conf_parser()

    @property
    def __dict__(self):
        return {
            '_document_root': self._document_root,
            '_database_name_default': self._database_name_default,
            '_instance_name_default': self._instance_name_default,
            '_params_delete_files': self._params_delete_files,
            '_params_create_folders': self._params_create_folders,
            '_params_copy_files': self._params_copy_files,
        }

    def _init_instance_path(self):
        """
        """
        #
        self._instance_path = "/".join(os.getcwd().split("/")[:-1])

    def _init_conf_parser(self):
        """
        """
        #
        self._conf_parser = ConfigParser.ConfigParser()
        #
        fname = os.getenv("HOME") + '/.om-tests/config.cfg'
        if os.path.isfile(fname):
            self._conf_parser.readfp(open(fname))
        #

        def aslist_cronly(value):
            if isinstance(value, str):
                value = filter(None, [x.strip() for x in value.splitlines()])
            return list(value)

        def aslist(value, flatten=True):
            """
            Return a list of strings, separating the input based on newlines
            and, if flatten=True (the default), also split on spaces within
            each line.
            """
            values = aslist_cronly(value)
            if not flatten:
                return values
            result = []
            for value in values:
                subvalues = value.split()
                result.extend(subvalues)
            return result
        fname = self._instance_path + "/tests/resources/om-tests.cfg"
        if os.path.isfile(fname) is not True:
            return
        conf_parser_app = ConfigParser.ConfigParser()
        conf_parser_app.readfp(open(fname))
        if conf_parser_app.has_section("om-tests") is True :
            if conf_parser_app.has_option("om-tests", "database_name") is True:
                self._database_name_default = conf_parser_app.get('om-tests', 'database_name')
            if conf_parser_app.has_option("om-tests", "instance_name") is True:
                self._instance_name_default = conf_parser_app.get('om-tests', 'instance_name')
            if conf_parser_app.has_option("om-tests", "delete_files") is True:
                self._params_delete_files = aslist(conf_parser_app.get('om-tests', 'delete_files'))
            if conf_parser_app.has_option("om-tests", "chmod_777") is True:
                self._params_chmod_777 = aslist(conf_parser_app.get('om-tests', 'chmod_777'))
            if conf_parser_app.has_option("om-tests", "create_folders") is True:
                self._params_create_folders = aslist(conf_parser_app.get('om-tests', 'create_folders'))
            if conf_parser_app.has_option("om-tests", "copy_files") is True:
                for line in conf_parser_app.get('om-tests', 'copy_files').split('\n'):
                    if line != '':
                        elem = line.split()
                        self._params_copy_files.append({'in': elem[0], 'out': elem[1]})

    def _init_args_parser(self):
        """
        """
        #
        self._args_parser = argparse.ArgumentParser(
            description="om_tests",
        )
        #
        self._args_parser.add_argument(
            "-c",
            dest="command",
            help="initdb | initenv | runall | runone | runphpunit | runrobot | startsmtp | stopsmtp",
            required=True
        )
        #
        self._args_parser.add_argument(
            "-d",
            dest="database_name",
            default=None,
            help="database name"
        )
        #
        self._args_parser.add_argument(
            "-t",
            dest="testsuite",
            default=None,
            help="testsuite name"
        )
        #
        self._args_parser.add_argument(
            "--noinit",
            action="store_true", default=False
        )
        #
        self._args_parser.add_argument(
            "--nocleanresults",
            action="store_true", default=False
        )
        #
        self._args_parser.add_argument(
            "--exclude",
            action="store_true", default=False
        )
        #
        self._args = self._args_parser.parse_args()

    def _clean_results_folder(self):
        """
        """
        # Suppression des anciens résultats
        if os.path.isdir(self._instance_path + "/tests/results"):
            shutil.rmtree(self._instance_path + "/tests/results")
        # Création d'un répertoire vide permettant de recevoir les
        # prochains résultats
        os.mkdir(self._instance_path + "/tests/results")

    def _replace_browser(self):
        """
        """
        if self._conf_parser.has_section("browser") is True \
           and self._conf_parser.has_option("browser", "src_path") is True \
           and self._conf_parser.has_option("browser", "dest_path") is True:
            src_path = self._conf_parser.get("browser", "src_path")
            dest_path = self._conf_parser.get("browser", "dest_path")
            print "sudo ln -s %s %s" % (src_path, dest_path)
            ret = os.system(
                "sudo ln -s %s %s" % (src_path, dest_path)
            )
            if ret != 0:
                print ret

    def _reset_browser(self):
        """
        """
        if self._conf_parser.has_section("browser") is True \
           and self._conf_parser.has_option("browser", "src_path") is True \
           and self._conf_parser.has_option("browser", "dest_path") is True:
            dest_path = self._conf_parser.get("browser", "dest_path")
            print "sudo rm %s" % dest_path
            ret = os.system(
                "sudo rm %s" % dest_path
            )
            if ret != 0:
                print ret

    def _handle_mailhost(self, kill=False):
        """
        """
        # kill the service
        if kill:
            status = os.system(
                "maildump --stop -p /tmp/maildump_pid"
            )
            if status:
                print status
            return

        # Start the service
        print "maildump -p /tmp/maildump_pid"
        status = os.system(
            "maildump -p /tmp/maildump_pid"
        )
        if status:
            print status

    def _run_all_robot_tests(self):
        """ Lance l'ensemble des tests RobotFramework présents dans tests/

        """
        print self.line1
        print "RobotFramework"
        tag_exclude = ""
        if self._args.exclude is True:
            tag_exclude = "-e exclude "
        ret = os.system(
            "pybot -d results -e doc %s." % tag_exclude
        )
        self.gendoc()
        return ret

    def _run_all_phpunit_tests(self):
        """ Lance tous les tests PHPUnit listés dans le fichier config.xml, dans l'ordre
        du fichier.

        """
        # On exécute tous les tests suite
        print self.line1
        print "PHPUnit"
        print self.line1
        # Vérification du fichier bootstrap
        bootstrap = ""
        if (os.path.isfile("bootstrap.php")):
            bootstrap = "--bootstrap bootstrap.php "
        ret = os.system(
            "phpunit %s--log-junit results/results.xml -c config.xml" % bootstrap
        )
        return ret

    def _documentation_generation(self, source):
        """Génére la doc HTML.
        Cette méthode collecte et concatène tous les fichiers de ressources
        RobotFramework contenu dans le dossier *source*, les nettoie,
        les enrichit et génére le HTML en utilisant robot.libdoc.
        """
        source_path = 'resources/%s' % source
        if os.path.isdir(source_path) is not True:
            return
        # On crée un fichier temporaire qui va contenir toutes les ressources
        h, tmp_path = tempfile.mkstemp()

        with open(tmp_path, 'w') as keywords:

            title = self._instance_name_default
            if source == 'core':
                title = 'openMairie'
            keywords.write(DOC_TEMPLATE % (title, source))

            for resource in os.listdir(source_path):

                if not resource.endswith('.robot'):
                    continue
                resource_name = resource.split('.')[0]

                buffer = ''
                tags_re = re.compile('^    \[Tags\]')
                with open('%s/%s' % (source_path, resource)) as resource_content:

                    for line in resource_content.readlines():
                        # Ajout d'un mot-clef identique au nom de la resource
                        if tags_re.search(line):
                            tags = '    [Tags]  %s' % resource_name
                            line = tags_re.sub(tags, line)
                        buffer += line
                    # On a besoin d'un saut de ligne pour libdoc
                    if not buffer.endswith('\n'):
                        buffer += '\n'
                # On ne garde que les mots-clefs de la ressource
                keywords.write(buffer.partition('*** Keywords ***\n')[2])

        # La ressource doit être au format robot
        os.system(
            "mv %s %s.robot" % (tmp_path, tmp_path)
        )

        # Test de l'existence du dossier de documentation et création dans le cas contraire
        if not os.path.exists("doc"):
            os.mkdir("doc")

        # Génération via Libdoc dans un fichier temporaire sans sortie écran
        os.system(
            "python -m robot.libdoc --name %s %s.robot doc/%s.tmp.html > /dev/null"
            % (title, tmp_path, source)
        )

        # L'objectif du code qui suit est de gérer l'antériorité de génération afin de pas avoir
        # de différence inutile avec le repository :
        # - les versions Robot Framework et de Python peuvent changer selon l'environnement de génération ;
        # - la date de génération est forcément différente.
        # On ne tient donc pas compte de ces informations lors de la comparaison :
        # - les versions sont dans une balise HTML spécifique que l'on supprime ;
        # - la date de génération est dans du code JavaScript que l'on nettoie.

        javascript_new_line = ''
        # Suppression des versions dans le fichier HTML généré
        # et récupération du code JavaScript sans date de génération
        for line in fileinput.input("doc/%s.tmp.html" % source, inplace=True):
            if not re.search('^<meta\scontent="Robot\sFramework', line):
                print line,
            if re.search('^libdoc = {', line):
                javascript_new_line = re.sub(r'"generated":"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"',r'',line)

        javascript_old_line = ''
        # S'il y avait une précédente génération on récupère également son code JavaScript nettoyé
        # Les versions ayant déjà été otées il est inutile de refaire un traitement à cet effet.
        if os.path.isfile("doc/%s.html" % source):
            for line in fileinput.input("doc/%s.html" % source, inplace=True):
                if re.search('^libdoc = {', line):
                    javascript_old_line = re.sub(r'"generated":"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"',r'',line)
                print line,

        # Étant donné que le code JavaScript a été nettoyé de la date de génération,
        # s'il y a la moindre différence entre l'ancien et le nouveau cela signifiera
        # que la documentation a changé
        if javascript_old_line != javascript_new_line:
            os.system(
                "mv doc/%s.tmp.html doc/%s.html"
                % (source, source)
            )
            print "resource/%s : génération effectuée" % source
        else:
            os.system(
                "rm doc/%s.tmp.html"
                % source
            )
            print "resource/%s : aucune regénération" % source


    def _tests_setup(self):
        """ Méthode effectuant les actions communes à tous les types de tests.

        """
        #
        # initenv
        if self._args.noinit is False:
            self.initenv()
        # On ne supprime pas les résultats de tests si le paramètre est passé
        if self._args.nocleanresults is False:
            self._clean_results_folder()

    def _run(self, tests):
        """ Méthode générique qui traite les commandes runall, runphpunit et runrobot.

        """
        retglobal = 0
        #
        print self.line1
        print "run%s (begin)" % tests
        print self.line1
        #
        self._handle_mailhost()
        self._replace_browser()
        self._tests_setup()
        # On se positionne dans le répertoire de tests
        os.chdir(self._instance_path + "/tests")
        # On exécute tous les tests suite
        if tests == 'all':
            ret = self._run_all_phpunit_tests()
            if ret != 0:
                retglobal = -1
            if self._args.noinit is False:
                self.initenv()
            os.chdir(self._instance_path + "/tests")
            ret = self._run_all_robot_tests()
            if ret != 0:
                retglobal = -1
        #
        if tests == 'phpunit':
            ret = self._run_all_phpunit_tests()
            if ret != 0:
                retglobal = -1
        #
        if tests == 'robot':
            ret = self._run_all_robot_tests()
            if ret != 0:
                retglobal = -1
        #
        self._reset_browser()
        self._handle_mailhost(kill=True)
        #
        print self.line1
        print "run%s (end)" %tests
        print self.line1
        #
        return retglobal

    def initenv(self):
        """
        """
        # On se positionne dans le répertoire racine de l'instance
        os.chdir(self._instance_path)
        #
        print self.line1
        print "initenv (begin)"
        print self.line1

        # Point d'entrée pour les actions spécifiques d'initialisation
        for param, value in self.__dict__.items():
            if not param.startswith('_params_'):
                continue
            method = getattr(self, param.replace('_params_', ''), None)
            if not method:
                continue
            method(value)

        # GESTION DES PERMISSIONS
        # On positionne les permissions sur les répertoires de stockage et de
        # génération pour ne pas obtenir d'erreurs dans les tests qui seraient
        # liées à la configuration du serveur et non à l'applicatif lui même
        # !!! ATTENTION !!! Ces permissions sont destinées à un environnement
        # de tests, elles ne doivent évidemment pas être utilisées sur un
        # environnement de production.
        self.chmod_777(self._params_chmod_777)

        # ACCES WEB A L'APPLICATION
        # On cré le lien symbolique qui est utilisé par les tests en fonction
        # de l'emplacement actuel uniquement si cet emplacement est un lien
        # symbolique ou n'existe pas. Ce lien symbolique est créé dans le
        # répertoire DocumentRoot d'apache. Objectif : http://localhost/<APP>
        print self.line2
        print "-> Accès web à l'instance de l'application ..."
        path_tests = self._document_root + self._instance_name_default
        if os.path.islink(path_tests):
            ret = os.system(
                "sudo rm -f %s" % (path_tests)
            )
            if ret != 0:
                print ret
        if not os.path.exists(path_tests):
            ret = os.system(
                "sudo ln -s %s %s" % (self._instance_path, path_tests)
            )
            if ret != 0:
                print ret

        # REDEMARRAGE APACHE
        # On redémarre apache pour être sur de prendre en compte les derniers
        # fichiers de traduction
        print self.line2
        print "-> Redémarrage apache ..."
        ret = os.system(
            "sudo service apache2 graceful > /dev/null"
        )
        if ret != 0:
            print ret
        # initialisation de la base de donnees
        self.initdb()
        #
        print self.line1
        print "initenv (end)"
        print self.line1

    def initdb(self):
        """
        """
        #
        print self.line1
        print "initdb (begin)"
        print self.line1
        #
        path = "/data/pgsql/"
        database_user = "postgres"
        if self._args.database_name is None :
            database_name = self._database_name_default
        else:
            database_name = self._args.database_name
        #
        os.chdir(self._instance_path + path)
        #
        print "-> Suppression de la base %s ..." % database_name
        ret = os.system(
            "sudo su %s -c \"dropdb %s\""
            % (database_user, database_name, )
        )
        if ret != 0:
            print ret

        #
        print self.line2
        print "-> Création de la base %s ..." % database_name
        ret = os.system(
            "sudo su %s -c \"createdb %s\""
            % (database_user, database_name, )
        )
        if ret != 0:
            print ret

        #
        print self.line2
        print "-> Initialisation de la base %s ..." % database_name
        ret = os.system(
            "sudo su %s -c \"psql %s -q -f install.sql > /dev/null\""
            % (database_user, database_name, )
        )
        if ret != 0:
            print ret

        #
        os.chdir(self._instance_path)
        #
        print self.line1
        print "initdb (end)"
        print self.line1

    def runone(self):
        """
        """
        retglobal = 0
        #
        if self._args.testsuite is None:
            self._args_parser.error("argument -t is required with command runone")
        #
        print self.line1
        print "runone (begin)"
        print self.line1
        #
        #
        self._handle_mailhost()
        self._replace_browser()
        self._tests_setup()
        # On se positionne dans le répertoire de tests
        os.chdir(self._instance_path + "/tests")
        # On exécute le testsuite en fonction de l extension du fichier
        if self._args.testsuite.endswith(".robot"):
            print self.line1
            print "RobotFramework"
            print "pybot -d results %s" % self._args.testsuite
            ret = os.system(
                "pybot -d results %s" % self._args.testsuite
            )
            if ret != 0:
                retglobal = -1
            self.gendoc()
        elif self._args.testsuite.endswith(".php"):
            #
            print self.line1
            print "PHPUnit"
            print self.line1
            if (os.path.isfile("bootstrap.php")):
                bootstrap = "--bootstrap bootstrap.php "
            ret = os.system(
                "phpunit %s--log-junit results/results.xml %s" % (bootstrap, self._args.testsuite)
            )
            if ret != 0:
                retglobal = -1
        #
        self._reset_browser()
        self._handle_mailhost(kill=True)
        #
        print self.line1
        print "runone (end)"
        print self.line1
        #
        return retglobal

    def runall(self):
        """
        """
        return self._run('all')

    def runphpunit(self):
        """
        """
        return self._run('phpunit')

    def runrobot(self):
        """
        """
        return self._run('robot')

    def gendoc(self):
        """
        """
        self._documentation_generation('app')
        self._documentation_generation('core')

    def startsmtp(self):
        """
        """
        self._handle_mailhost()

    def stopsmtp(self):
        """
        """
        self._handle_mailhost(kill=True)

    def main(self, mode="default"):
        """
        """
        #
        if self._args.command not in ["initdb", "initenv", "gendoc", "runall", "runone", "runphpunit", "runrobot", "_replace_browser", "_reset_browser", "startsmtp", "stopsmtp", ]:
            self._args_parser.error("command does not exist")
        #
        return getattr(self, self._args.command)()

    def delete_files(self, paths):
        """ Supprime les fichier passés en paramètres
        :param paths: liste des chemins des fichers à supprimer
        :type paths: list

        """
        for path in paths:
            print "-> Suppression de %s ..." % path
            ret = os.system("sudo rm -f %s" % (path))
            if ret != 0:
                print ret

    def copy_files(self, paths):
        """ Copie les fichiers passés en paramètres
        :param paths: +liste des chemins source et cibles
        :type paths: list of dict i.e
            [{'in': '/tmp/plop','out': '/tmp/plip'}]

        """
        for path in paths:
            print "-> Copie de %s ..." % path
            ret = os.system("sudo cp -r %s %s" % (path['in'], path['out']))
            if ret != 0:
                print ret

    def create_folders(self, paths):
        """ Crée les répertoires passés en paramètres
        :param paths: +liste des chemins à créer
        :type paths: list

        """
        for path in paths:
            print "-> Création du répertoire %s ..." % path
            ret = os.system("sudo mkdir -p %s" % (path))
            if ret != 0:
                print ret

    def chmod_777(self, paths):
        """ Applique la commande chmod 777 sur les chemins passés en paramètres
        :param paths: +liste des chemins sur lesquels positionner 777
        :type paths: list

        """
        # GESTION DES PERMISSIONS
        # On positionne les permissions sur les répertoires de stockage et de
        # génération pour ne pas obtenir d'erreurs dans les tests qui seraient
        # liées à la configuration du serveur et non à l'applicatif lui même
        # !!! ATTENTION !!! Ces permissions sont destinées à un environnement
        # de tests, elles ne doivent évidemment pas être utilisées sur un
        # environnement de production.
        for path in paths:
            print "-> Positionnement des permissions sur %s ..." % path
            ret = os.system("sudo chmod -R 777 %s" % (path))
            if ret != 0:
                print ret


def main():
    tests = OMTests()
    tests.main()
