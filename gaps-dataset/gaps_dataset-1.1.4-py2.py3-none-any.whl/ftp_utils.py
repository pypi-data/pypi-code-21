# -*- coding: utf-8 -*-
"""
Created 2017/09/20
Latest update 2017/09/20

@author: Markus Eisenbach

Description:
Helper functions for downloading datasets from FTP.
"""

from __future__ import print_function
import os
import ftplib
try:
    import cPickle as pkl
except:
    import pickle as pkl
import hashlib

FTP_LOGIN_SHA256_CHECKSUM = ('330453216adcadf76a60e0a0d4ecd0f7'
                             'a399c9eb464efdc38cd5725398dc8fa9')


def _download_from_ftp(url, user, passwd, fpath, debug_outputs=False):
    """Helper function to retrieve a file from a FTP server."""
    # split url in host, directory and filename
    url_part = url.split('/')
    host = url_part[2]
    beg = len(host) + len(url_part[1]) + len(url_part[0]) + 2
    end = -len(url_part[-1])
    ftp_dir = url[beg:end]
    ftp_file = url_part[-1]
    # connect to ftp server
    try:
        ftp = ftplib.FTP(host, user=user, passwd=passwd)
    except (ftplib.error_perm):
        if debug_outputs:
            print('ERROR: cannot connect to FTP server')
        return
    except:
        if debug_outputs:
            print('ERROR: cannot establish an internet connection')
        return
    # change directory
    ftp.cwd(ftp_dir)
    # write to file
    with open(fpath, 'wb') as dst_file:
        ftp.retrbinary('RETR ' + ftp_file, dst_file.write)
    # close ftp connection
    ftp.quit()


def _download_from_ftp_if_neccessary(url, user, passwd, fpath,
                                     debug_outputs=False):
    """Helper function that checks if file exists. If not,
       the file is downloaded from FTP."""
    # check if download is necessary
    if not os.path.exists(fpath):
        # file not found -- download from ftp
        if debug_outputs:
            print('download {}'.format(url))
        _download_from_ftp(url, user, passwd, fpath)


def _calc_md5(filename, debug_outputs=False):
    """Helper function to compute the MD5 checksum
       of the content of a file."""
    md5_checksum = None
    try:
        with open(filename, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_checksum = hashlib.md5(data).hexdigest()
    except (IOError):
        if debug_outputs:
            print('ERROR: cannot open file {}'.format(filename))
    return md5_checksum


def _is_valid(filename, md5_checksum, debug_outputs=False):
    """Helper function to check whether the MD5 checksum
       of the content of a file matches the expected checksum."""
    file_md5 = _calc_md5(filename, debug_outputs)
    file_is_valid = file_md5 == md5_checksum
    return file_is_valid


def download_if_not_available(datadir, source, checksum, login,
                              debug_outputs=False):
    """Helper function to download the dataset if it is not available on
       file system. Checks the correctness of each files checksum. Deletes
       files that do not match the checksum and downloads them again (maximum
       three times)."""
    if not os.path.exists(datadir):
        if debug_outputs:
            print('create directory {}'.format(datadir))
        try:
            os.makedirs(datadir)
        except:
            if debug_outputs:
                print('ERROR: cannot create directory {}'.format(datadir))

    # get filename from URL
    file_parts = source.split('/')
    dirname, filename = file_parts[-2], file_parts[-1]
    fpath = os.path.join(datadir, dirname, filename)

    # create subdir
    subdir = os.path.join(datadir, dirname)
    if not os.path.exists(subdir):
        if debug_outputs:
            print('create directory {}'.format(subdir))
        try:
            os.makedirs(subdir)
        except:
            if debug_outputs:
                print('ERROR: cannot create directory {}'.format(subdir))

    download_list = [(source, fpath, checksum, 3)]

    login_check = login.encode('utf-8')
    if hashlib.sha256(login_check).hexdigest() != FTP_LOGIN_SHA256_CHECKSUM:
        print('ERROR: login not correct')
        return
    split = int(login[-1])
    user = login[:split]
    passwd = login[split:-1]

    while len(download_list) > 0:
        s, f, c, tries = download_list.pop(0)
        if tries == 0:
            if debug_outputs:
                print('download failed 3x -- terminate')
            return

        # check if download is necessary
        _download_from_ftp_if_neccessary(s, user=user, passwd=passwd,
                                         fpath=f, debug_outputs=debug_outputs)

        if not _is_valid(f, c, debug_outputs):
            download_list.append((s, f, c, tries - 1))
            try:
                os.remove(f)
            except:
                pass
            if debug_outputs:
                print('checksum failed for file {} -- delete file'.format(f))

    # check if it is an info file listing all other download files
    if os.path.splitext(fpath)[-1] == '.pkl':
        # read info file
        with open(fpath, 'rb') as pkl_file:
            try:
                data = pkl.load(pkl_file, encoding='latin1')  # python 3
            except TypeError:
                data = pkl.load(pkl_file)  # python 2

        # get chunk names
        chunk_descriptor_digits = data['chunk_descriptor_digits']
        n_chunks = data['n_chunks']
        templ = 'chunk_{:0' + str(chunk_descriptor_digits) + 'd}_{}.npy'
        fpath_template = fpath[:-8] + templ
        source_template = source[:-8] + templ
        checksums = data['checksums']

        # download chunks if neccessary
        download_list = []
        for chunk_idx in range(n_chunks):
            md5_checksums = checksums[chunk_idx]
            for data_idx in ['x', 'y']:
                # get filename and URL of chunk
                fpath_chunk = fpath_template.format(chunk_idx, data_idx)
                source_chunk = source_template.format(chunk_idx, data_idx)

                if data_idx == 'x':
                    md5_compare = md5_checksums[0]
                else:
                    md5_compare = md5_checksums[1]
                download_list.append((source_chunk, fpath_chunk,
                                      md5_compare, 3))

        while len(download_list) > 0:
            s, f, c, tries = download_list.pop(0)
            if tries == 0:
                if debug_outputs:
                    print('download failed 3x -- terminate')
                return

            # check if download is necessary
            _download_from_ftp_if_neccessary(s, user=user, passwd=passwd,
                                             fpath=f,
                                             debug_outputs=debug_outputs)

            if not _is_valid(f, c, debug_outputs):
                download_list.append((s, f, c, tries - 1))
                try:
                    os.remove(f)
                except:
                    pass
                if debug_outputs:
                    print('checksum failed for file {}'
                          ' -- delete file'.format(f))
