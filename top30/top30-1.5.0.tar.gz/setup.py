###########################################################################
# Top30 is Copyright (C) 2016-2017 Kyle Robbertze <krobbertze@gmail.com>
#
# Top30 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Top30 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Top30.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
"""
Top30 is a Python 3 module that allows for the creation of rundowns from charts
as sent out by UCT Radio.
"""
from codecs import open
from setuptools import setup, find_packages

setup(
    name='top30',
    version='1.5.0',
    description='Creates rundowns from top30 charts',
    long_description='Top30 automatically creates rundowns of songs for a Top 30 chart show',
    url='https://gitlab.com/paddatrapper/top30',
    author='Kyle Robbertze',
    author_email='krobbertze@gmail.com',
    license='GPL-3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Other Audience',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='radio audio rundown',
    packages=find_packages(),
    install_requires=['mutagen', 'pydub', 'docx2txt', 'youtube_dl', 'PyQt5'],
    package_data={
        'top30': ['main_window.ui'],
    },
    entry_points={
        'console_scripts': [
            'rundown-creator=top30:main',
        ],
    },
)
