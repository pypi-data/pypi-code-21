#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import parapheur

setup(

    name='iparapheur-utils.beta',

    version=parapheur.__version__,

    # Liste les packages à insérer dans la distribution
    # plutôt que de le faire à la main, on utilise la foncton
    # find_packages() de setuptools qui va cherche tous les packages
    # python recursivement dans le dossier courant.
    packages=find_packages(),

    author="Lukas Hameury",

    # Votre email, sachant qu'il sera publique visible, avec tous les risques
    # que ça implique.
    author_email="lukas.hameury@libriciel.fr",

    # Une description courte
    description="Client python pour i-Parapheur",

    # Une description longue, sera affichée pour présenter la lib
    # Généralement on dump le README ici
    long_description=open('README.md').read(),

    # Vous pouvez rajouter une liste de dépendances pour votre lib
    # et même préciser une version. A l'installation, Python essayera de
    # les télécharger et les installer.
    #
    # Ex: ["gunicorn", "docutils >= 0.3", "lxml==0.5a7"]
    #
    # Dans notre cas on en a pas besoin, donc je le commente, mais je le
    # laisse pour que vous sachiez que ça existe car c'est très utile.
    install_requires=[
        'python-magic',
        'suds',
        'requests>=2.16.0',
        'importlib',
        'PyMySql',
        'progressbar2'
    ],

    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=True,

    # Une url qui pointe vers la page officielle de votre lib
    url='https://gitlab.libriciel.fr/i-parapheur/client-python',

    # classifiers=[
    #     "Programming Language :: Python",
    #     "Development Status :: 1 - Planning",
    #     "License :: OSI Approved",
    #     "Natural Language :: French",
    #     "Operating System :: OS Independent",
    #     "Programming Language :: Python :: 2.7",
    #     "Topic :: Communications",
    # ],


    # C'est un système de plugin, mais on s'en sert presque exclusivement
    # Pour créer des commandes, comme "django-admin".
    # La syntaxe est "nom-de-commande-a-creer = package.module:fonction".
    entry_points={
        'console_scripts': [
            'ph-echo = parapheur.core:echo',
            'ph-check = parapheur.core:check',
            'ph-init = parapheur.core:init',
            'ph-recupArchives = parapheur.core:recuparchives',
            'ph-properties-merger = parapheur.core:properties_merger',
            'ph-export = parapheur.core:export_data',
            'ph-import = parapheur.core:import_data'
        ],
    },

    # A fournir uniquement si votre licence n'est pas listée dans "classifiers"
    # ce qui est notre cas
    license="CeCILL v2",

)
