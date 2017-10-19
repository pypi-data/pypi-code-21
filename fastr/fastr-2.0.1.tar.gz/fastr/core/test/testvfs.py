# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import nose.tools as nt
import fastr
import os
import tempfile
import random
import shutil
import string
import fastr.exceptions as exceptions


class TestVFS:

    def setup(self):
        fastr.log.info('Setup')
        """ Setup the test environment for the vfs tests. """
        # We assume there is a tmp mount. (It should be tested).
        # Generate a file in the tmp mount.
        self.dir = os.path.join(fastr.config.mounts['tmp'], '_test')
        if os.path.exists(self.dir):
            fastr.log.warning('Cleaning up existing temporary test directory {}'.format(self.dir))
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        fastr.log.info('Using temporary directory {}'.format(self.dir))
        if not os.path.isdir(self.dir):
            fastr.log.critical('Temporary directory not available!')

        self.source_dir = os.path.join(self.dir, 'source')
        os.mkdir(self.source_dir)
        self.destination_dir = os.path.join(self.dir, 'destination')
        os.mkdir(self.destination_dir)

        self.handle, self.absfilename = tempfile.mkstemp(dir=self.source_dir)
        self.filename = os.path.basename(self.absfilename)
        self.niigz_handle, self.niigz_absfilename = tempfile.mkstemp(dir=self.source_dir, suffix='.nii.gz')
        self.niigz_filename = os.path.basename(self.niigz_absfilename)

        fastr.log.info('Created {} and {}'.format(self.absfilename, self.niigz_absfilename))
        if not os.path.exists(self.absfilename):
            fastr.log.critical('Source file {} does not exist!'.format(self.absfilename))
        if not os.path.exists(self.niigz_absfilename):
            fastr.log.critical('Source file {} does not exist!'.format(self.niigz_absfilename))

    def teardown(self):
        """ Tear down the test environment for the vfs tests. """
        # Delete the generated temporary file
        shutil.rmtree(self.dir)

    def random_unique_string(self, length=8, existing=None):
        """ Return a random alpha-numeric string with a certain length. """
        s = ''.join([random.choice(string.ascii_letters + string.digits) for ch in range(length)])
        if existing is not None and s in existing:
            s = self.random_unique_string(length, existing)
        return s

    def test_url_to_path(self):
        nt.eq_(fastr.vfs.url_to_path('vfs://tmp/_test/source/{}'.format(self.filename)), self.absfilename)

    def test_path_to_url(self):
        nt.eq_(fastr.vfs.path_to_url(self.absfilename), 'vfs://tmp/_test/source/{}'.format(self.filename))

    @nt.raises(exceptions.FastrUnknownURLSchemeError)
    def test_url_to_path_unknown_scheme(self):
        # Get a random sequence of strings to get a non existing scheme.
        s = self.random_unique_string(length=5, existing=fastr.ioplugins.keys())
        fastr.vfs.url_to_path("{}://tmp/blaat.nii.gz".format(s))

    @nt.raises(exceptions.FastrMountUnknownError)
    def test_url_to_path_unknown_mount(self):
        # Get a random sequence of strings to get a non existing scheme.
        m = self.random_unique_string(length=5, existing=fastr.config.mounts.keys())
        fastr.vfs.url_to_path("vfs://{}/blaat.nii.gz".format(m))

    @nt.raises(exceptions.FastrMountUnknownError)
    def test_path_to_url_unknown_mount(self):
        # Get a random sequence of strings to get a non existing scheme.
        m = self.random_unique_string(length=5, existing=fastr.config.mounts.keys())
        fastr.vfs.path_to_url("/{}/blaat.nii.gz".format(m))

    def test_ioplugins_pull_source_data_no_extension(self):
        output_file = os.path.join(self.destination_dir, self.filename)
        fastr.vfs.pull_source_data('vfs://tmp/_test/source/{}'.format(self.filename),
                                   self.destination_dir,
                                   'id_0',
                                   datatype=fastr.typelist['NiftiImageFile'])
        nt.ok_(os.path.isfile(output_file), 'expected output at {}'.format(output_file))
        if os.path.isfile(output_file):
            os.remove(output_file)

    def test_ioplugins_pull_source_data_niigz(self):
        fastr.vfs.pull_source_data('vfs://tmp/_test/source/{}'.format(self.filename),
                                   self.destination_dir,
                                   'id_nii_0',
                                   datatype=fastr.typelist['NiftiImageFileCompressed'])
        output_file = os.path.join(self.destination_dir, self.filename)
        nt.ok_(os.path.isfile(output_file))
        if os.path.isfile(output_file):
            os.remove(output_file)

    def test_ioplugins_pull_source_data_mhd(self):
        absfilename_mhd = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.mhd')
        absfilename_raw = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.raw')
        filename_mhd = os.path.basename(absfilename_mhd)
        filename_raw = os.path.basename(absfilename_raw)

        destination_path = self.destination_dir
        destination_path_mhd = os.path.join(self.destination_dir, filename_mhd)
        destination_path_raw = os.path.join(self.destination_dir, filename_raw)

        if os.path.exists(destination_path_mhd):
            os.remove(destination_path_mhd)
        if os.path.exists(destination_path_raw):
            os.remove(destination_path_raw)

        fastr.vfs.pull_source_data(fastr.vfs.path_to_url(absfilename_mhd),
                                   destination_path,
                                   'id_mhd_0',
                                   datatype=fastr.typelist['ITKImageFile'])
        new_mhd_exists = os.path.isfile(destination_path_mhd)
        new_raw_exists = os.path.isfile(destination_path_raw)
        nt.ok_(new_mhd_exists, 'expected output .mhd file {} not found'.format(destination_path_mhd))
        nt.ok_(new_raw_exists, 'expected output .raw file {} not found'.format(destination_path_raw))

    def test_ioplugins_push_sink_data_niigz(self):
        random_filename = self.random_unique_string()
        output_file = os.path.join(self.destination_dir, random_filename) + '.nii.gz'
        output_url = fastr.vfs.path_to_url(output_file)
        fastr.vfs.push_sink_data(self.niigz_absfilename, output_url)
        nt.ok_(os.path.isfile(output_file))
        if os.path.isfile(output_file):
            os.remove(output_file)

    def test_ioplugins_push_sink_data_mhd(self):
        absfilename_mhd = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.mhd')
        absfilename_raw = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.raw')
        filename_mhd = os.path.basename(absfilename_mhd)
        filename_raw = os.path.basename(absfilename_raw)

        push_target = os.path.join(self.destination_dir, 'sink')
        os.mkdir(push_target)
        destination_path_mhd = os.path.join(push_target, filename_mhd)
        destination_path_raw = os.path.join(push_target, filename_raw)
        destination_url_mhd = fastr.vfs.path_to_url(destination_path_mhd)

        if os.path.exists(destination_path_mhd):
            os.remove(destination_path_mhd)
        if os.path.exists(destination_path_raw):
            os.remove(destination_path_raw)

        fastr.vfs.push_sink_data(absfilename_mhd, destination_url_mhd)
        new_mhd_exists = os.path.isfile(destination_path_mhd)
        new_raw_exists = os.path.isfile(destination_path_raw)
        nt.ok_(new_mhd_exists, 'expected output .mhd file {} not found'.format(destination_path_mhd))
        nt.ok_(new_raw_exists, 'expected output .raw file {} not found'.format(destination_path_raw))
