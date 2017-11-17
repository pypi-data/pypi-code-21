# -*- coding: utf-8 -*-

from os import listdir, rename
from os.path import isfile, join
import subprocess
import os
import glob

# return name of file to be kept after conversion.
# we are just changing the extension. azw3 here.


def get_final_filename(f):
    f = f.split(".")
    filename = ".".join(f[0:-1])
    processed_file_name = filename + ".pdf"
    return processed_file_name

# return file extension. pdf or epub or mobi


def get_file_extension(f):
    return f.split(".")[-1]

# list of extensions that needs to be ignored.
ignored_extensions = ["pdf"]

# here all the downloaded files are kept
mypath = "/home/faketaxi/DANIAS/Project_django/skripsi/coba2/bashrc/a/"  # "/home/user/Downloads/ebooks/"


raw_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
converted_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for f in raw_files:
    final_file_name = get_final_filename(f)
    extension = get_file_extension(f)
    if final_file_name not in converted_files and extension not in ignored_extensions:
        print("Converting : " + f)
        try:
            # convert epub / mobi to pdf
            subprocess.call(["ebook-convert", mypath + f, mypath + final_file_name])
            subprocess.call(['rm', '-r', mypath + f])  # remove epub / mobi
            # convert pdf to png
            subprocess.call(['pdftocairo', '-png', mypath + final_file_name, mypath])
            subprocess.call(['rm', '-r', mypath + final_file_name])  # remove pdf
            s = rename(mypath + f)
            print(s)
        except Exception as e:
            print(e)
    else:
        print("Already exists : " + final_file_name)


#######
#######


def file_converter(_file):
    # _file.path =
    # /home/agaust/ENV/env-welut/welut/welut_demo/media/ebooks/2017/11/13/pg55939_m9m4VI4.epub
    full_epub_path = _file.path
    splited_path = os.path.split(full_epub_path)
    current_path, origin_file = splited_path[0], splited_path[-1]
    full_pdf_path = os.path.join(current_path, get_final_filename(full_epub_path, '.pdf'))

    try:
        subprocess.call(['ebook-convert', full_epub_path, full_pdf_path])
        #subprocess.call(['rm', '-r', full_epub_path])
        subprocess.call(['pdftocairo', '-png', full_pdf_path, current_path])

        # move all files from: 13-01.png to 13/filename-01.png
        # eg: '/home/agaust/ENV/env-welut/welut/welut_demo/media/ebooks/2017/11'

        # ('/home/agaust/ENV/env-welut/welut/welut_demo/media/ebooks/2017/11', '13')
        splited_path = os.path.split(current_path)

        # '/home/agaust/ENV/env-welut/welut/welut_demo/media/ebooks/2017/11'
        path_before = splited_path[0]

        # egg: '13'
        path_next = splited_path[-1]

        for fname in os.listdir(path_before):
            # fname.replace(get_file_extension(fname), '.png')  # 'foo.epub' => 'foo.png'
            new_fname = fname.replace(get_file_extension(fname), '.png')
            dir_next = os.path.basename(os.path.splitext(full_epub_path)[0])  # 'pg55939'
            file_next = '%s/%s/%s' % (current_path, dir_next, new_fname)
            new_dir = os.path.split(file_next)[0]

            if not os.path.exists(new_dir):
                os.makedirs(new_dir)

            file_before = os.path.join(path_before, fname)

            if os.path.isfile(file_before) and get_file_extension(file_before) == '.png':
                shutil.move(file_before, file_next)

        # removing all file uploaded with specific extensions
        for ext in WELUT_REMOVED_EXTENSIONS:
            if os.path.isfile(full_epub_path):
                if ext == '.epub' or ext == '.mobi':
                    os.remove(full_epub_path)
                elif ext == '.pdf':
                    os.remove(full_pdf_path)
        return True
    except Exception as e:
        raise e
