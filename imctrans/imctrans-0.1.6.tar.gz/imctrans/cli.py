import argparse
import os
import shutil
import subprocess

import imctrans.cpp.code
import imctrans.cpp.tests

# Default Git Repository URL.
GIT_URL = 'https://www.github.com/oceanscan/imc'
# Supported output languages.
LANGS = ['cpp']


def trans(args):
    if args.language == 'cpp':
        imctrans.cpp.code.main(args.xml, args.output_folder, args.no_base, args.force)
        if args.output_test is not None:
            imctrans.cpp.tests.gen_test_file(args.xml, args.output_test, args.force)


def download(args):
    # Clone.
    shutil.rmtree(args.output_folder, ignore_errors=True)
    subprocess.check_output(['git', 'clone', args.url, args.output_folder], universal_newlines=True)

    # Checkout.
    os.chdir(args.output_folder)
    subprocess.check_output(['git', 'checkout', args.tag], universal_newlines=True)


def main():
    parser = argparse.ArgumentParser(description="IMC Bindings Generator")

    subparsers = parser.add_subparsers(title="Commands", dest='command', help='Supported Commands')
    subparsers.required = True

    parser_dl = subparsers.add_parser('download', help='Clone IMC XML from Git Repository')
    parser_dl.set_defaults(func=download)
    parser_dl.add_argument('-o', '--output-folder', required=True, metavar='OUT_FOLDER', help="Output folder")
    parser_dl.add_argument('-t', '--tag', metavar='GIT_TAG', default='master', help="Tag, branch, or commit hash")
    parser_dl.add_argument('-u', '--url', metavar='GIT_URL', default=GIT_URL, help="Repository URL")

    parser_trans = subparsers.add_parser('translate', help='Translate IMC Specification to Source Code')
    parser_trans.set_defaults(func=trans)
    parser_trans.add_argument('-l', '--language', required=True, choices=LANGS, help="Output Language")
    parser_trans.add_argument('-x', '--xml', required=True, metavar='IMC_XML', help="IMC XML file")
    parser_trans.add_argument('-o', '--output-folder', required=True, metavar='OUT_FOLDER', help="Output folder")
    parser_trans.add_argument('-n', '--no-base', action='store_true', help="Do not install assets files")
    parser_trans.add_argument('-f', '--force', action='store_true', help="Force generation of all files")
    parser_trans.add_argument('-t', '--output-test', metavar='OUT_TEST', help="Generate test file")

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    main()
