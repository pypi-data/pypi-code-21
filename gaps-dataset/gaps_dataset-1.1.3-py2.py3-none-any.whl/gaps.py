# -*- coding: utf-8 -*-
"""
Created 2017/04/27
Last update 2017/08/14

@author: Markus Eisenbach

Description:
Automatic download of GAPs dataset if not available on PC.
"""

from __future__ import print_function, absolute_import
import os
import numpy as np
from .ftp_utils import download_if_not_available


def _check_file(dataset_file, debug_outputs=False):
    """Helper function plotting error messages in case of a failed download."""
    if not os.path.exists(dataset_file):
        if debug_outputs:
            msg = 'download failed for file {}'.format(dataset_file)
            msg2 = 'you may apply for a valid login first'
            msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
            print('ERROR: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        else:
            msg4 = 'for detailed error messages set debug_outputs=True'
            print('ERROR occured during download: {}'.format(msg4))
        return None


def download(
        login='skip',
        datadir='/local/datasets/gaps/v1', version=1.0, size='64x64',
        source='ftp://141.24.24.121/GAPs/v1/',
        train='train/chunks_64x64_NORMvsDISTRESS_train_info.pkl',
        train_checksum='8ff1685346ee4809836e2173e17ab006',
        valid='valid/chunks_64x64_NORMvsDISTRESS_valid_info.pkl',
        valid_checksum='a04203dd87cf3387c9c3831ef930c1e4',
        test='test/chunks_64x64_NORMvsDISTRESS_test_info.pkl',
        test_checksum='0aca7893c6fcef41afdfa819c01dcef5',
        load_train=True, load_valid=True, load_test=True,
        debug_outputs=False, set_access_rights=False):
    """Downloads the GAPs dataset. Please enter a valid login."""
    if login == 'skip':
        return
    if version != 1.0:
        print('ERROR: currently only version 1.0 available')
        return
    if size != '64x64':
        print('ERROR: only patch size 64x64 available')
        print('HINT: other sizes will be available in later versions')
        return
    if load_train:
        download_if_not_available(datadir, source + train, train_checksum,
                                  login, debug_outputs)
        _check_file(os.path.join(datadir, train), debug_outputs)
    if load_valid:
        download_if_not_available(datadir, source + valid, valid_checksum,
                                  login, debug_outputs)
        _check_file(os.path.join(datadir, valid), debug_outputs)
    if load_test:
        download_if_not_available(datadir, source + test, test_checksum,
                                  login, debug_outputs)
        _check_file(os.path.join(datadir, test), debug_outputs)
    if set_access_rights:
        os.system('chmod -R 777 ' + datadir)


def load_chunk(no, subset='train', login='skip',
               datadir='/local/datasets/gaps/v1', version=1.0, size='64x64',
               debug_outputs=False):
    """Loads a 500MB chunk of the GAPs dataset. If you did not download the
       dataset first, please enter a valid login to make up this step."""
    download(login=login, version=version, size=size, datadir=datadir,
             debug_outputs=debug_outputs)
    # check if dataset is downloaded
    dataset_file = ('{0}/chunks_64x64_NORMvsDISTRESS'
                    '_{0}_info.pkl'.format(subset))
    dataset_file = os.path.join(datadir, dataset_file)
    if not os.path.exists(dataset_file):
        if login == 'skip':
            msg = 'could not load chunk'
            msg2 = 'you must download the dataset first by entering '
            msg2 += 'a valid login'
            msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
            print('ERROR: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
            return None
        else:
            msg = 'cannot download dataset without valid login'
            msg2 = 'if you do not have one, please apply for a login'
            msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
            print('ERROR[1]: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
            if not debug_outputs:
                msg4 = 'for detailed error messages set debug_outputs=True'
                print('HINT: {}'.format(msg4))
            return None
    # continue extracting the chunk
    filename = '{0}/chunks_64x64_NORMvsDISTRESS_{0}_chunk_{1:03d}_{2}.npy'
    chunk_filepath_fmt = os.path.join(datadir, filename)
    chunk_x = chunk_filepath_fmt.format(subset, no, 'x')
    if not os.path.exists(chunk_x):
        msg = 'cannot load chunk; file {} does not exist'.format(chunk_x)
        msg2 = 'you may download the dataset first by entering a valid login'
        msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
        print('ERROR[2]: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        if not debug_outputs:
            msg4 = 'for detailed error messages set debug_outputs=True'
            print('HINT: {}'.format(msg4))
        return None
    x = np.load(chunk_x)
    chunk_y = chunk_filepath_fmt.format(subset, no, 'y')
    if not os.path.exists(chunk_y):
        msg = 'cannot load chunk; file {} does not exist'.format(chunk_y)
        msg2 = 'you may download the dataset first by entering a valid login'
        msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
        print('ERROR[3]: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        if not debug_outputs:
            msg4 = 'for detailed error messages set debug_outputs=True'
            print('HINT: {}'.format(msg4))
        return None
    y = np.load(chunk_y)
    return x, y


def download_images(
        login='skip',
        datadir='/local/datasets/gaps/v1', version=1.0, size='64x64',
        source='ftp://141.24.24.121/GAPs/v1/',
        images='images/images.zip',
        images_checksum='8df7a86b6c5c04776a539001d893e047',
        train='images/patch_references_train.npy',
        train_checksum='23253cff2efc61e5e2cf37509d0cdb68',
        valid='images/patch_references_valid.npy',
        valid_checksum='9691cfd3bb4714398fe4f431b3124e26',
        test='images/patch_references_test.npy',
        test_checksum='481e1407800e940cef3f4ae9c9de21a8',
        load_images=True, load_train=True, load_valid=True, load_test=True,
        debug_outputs=False, set_access_rights=False):
    """Downloads the images of the GAPs dataset. Please enter a valid login."""
    if login == 'skip':
        msg = 'could not load chunk'
        msg2 = 'you must download the dataset first by entering '
        msg2 += 'a valid login'
        msg3 = 'see http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
        print('ERROR: {}\nHINT: {}\nHINT: {}'.format(msg, msg2, msg3))
        return
    if version != 1.0:
        print('ERROR: currently only version 1.0 available')
        return
    if size != '64x64':
        print('ERROR: only patch size 64x64 available')
        print('HINT: other sizes will be available in later versions')
        return
    if load_images:
        download_if_not_available(datadir, source + images, images_checksum,
                                  login, debug_outputs)
        _check_file(os.path.join(datadir, images), debug_outputs)
    if load_train:
        download_if_not_available(datadir, source + train, train_checksum,
                                  login, debug_outputs)
        _check_file(os.path.join(datadir, train), debug_outputs)
    if load_valid:
        download_if_not_available(datadir, source + valid, valid_checksum,
                                  login, debug_outputs)
        _check_file(os.path.join(datadir, valid), debug_outputs)
    if load_test:
        download_if_not_available(datadir, source + test, test_checksum,
                                  login, debug_outputs)
        _check_file(os.path.join(datadir, test), debug_outputs)
    if set_access_rights:
        os.system('chmod -R 777 ' + datadir)
