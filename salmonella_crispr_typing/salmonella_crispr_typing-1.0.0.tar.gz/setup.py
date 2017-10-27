from setuptools import setup
import sys, os

exec(open('salmonella_crispr_typing/version.py').read())

setup(name="salmonella_crispr_typing",
        version=__version__,
        description='This tool gets a CRISPR profile by identifying the presence of known spacers and direct repeats (DRs) in a given sequence based on a catalogue. This tool is a reimplemntation of a former Perl tool in developed by G. Guigon',
        author='Kenzo-Hugo Hillion and Laetitia Fabre',
        author_email='kehillio@pasteur.fr and laetitia.fabre@pasteur.fr',
        license='',
        keywords = ['salmonella','crispr','fasta'],
        install_requires=['biopython'],
        packages=["salmonella_crispr_typing"],
        package_data={
        'salmonella_crispr_typing': ['data/spacers_Salmonella.fa'],
        },
        entry_points={'console_scripts':['crispr_typing=salmonella_crispr_typing.main:run']},
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Environment :: Console',
            ],
        )
