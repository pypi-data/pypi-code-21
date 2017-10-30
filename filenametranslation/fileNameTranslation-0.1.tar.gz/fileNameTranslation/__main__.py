#!/usr/bin/env python
# coding=utf-8
import os

from googletrans import Translator

from fileNameTranslation.options import args_parse


def getFilesPaths(path, extensions):
    files = []
    for root, directories, file_names in os.walk(unicode(path)):
        for filename in file_names:
            if (extensions and filename.endswith(tuple(["." + ext for ext in extensions]))) or (extensions is None):
                files.append(os.path.join(root, filename))
    return files


def separatePathsAndFilesNameAndExt(files):
    return [("\\".join(os.path.splitext(f)[0].split('\\')[: -1]), os.path.splitext(f)[0].split('\\')[-1],
             os.path.splitext(f)[1]) for f in files]


def main():
    translator = Translator()
    options = args_parse.parse_args()
    src = 'auto'
    if options.source:
        src = options.source
    files = getFilesPaths(options.FILES_LOCATION, options.extensions)
    if not files:
        print "couldn't find file that match your request"
    paths_and_files_name_and_ext = separatePathsAndFilesNameAndExt(files)
    fails = 0
    for pfe in paths_and_files_name_and_ext:
        file_name = pfe[1].encode("utf-8")
        detected = translator.detect(file_name)
        if (not detected.lang == options.target) or (detected.confidence < 0.8):
            new_file_name = translator.translate(file_name, dest=options.target, src=src)
            try:
                os.rename(os.path.join(pfe[0], pfe[1] + pfe[2]),
                          os.path.join(pfe[0], new_file_name.text.title() + pfe[2]))
            except WindowsError:
                fails += 1
                pass
    print "Done!"
    print "Succeeded: " + str(len(paths_and_files_name_and_ext))
    print "Failed: " + fails


if __name__ == '__main__':
    main()
