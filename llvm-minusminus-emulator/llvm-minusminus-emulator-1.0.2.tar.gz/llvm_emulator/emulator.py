"""
Main module of the program.

To start the application, call the main function. For the end user,
this is achieved by a script stored in the bin folder.

"""

import argparse

from llvm_emulator import stepper, parser


def main():
    arg_parser = argparse.ArgumentParser(description='A hacky LLVM-- emulator/debugger')

    arg_parser.add_argument('-a', '--auto',
                            action='store', type=str, dest='auto_path',
                            help='Automatically step through llvm in the given file')

    parse_res_raw = arg_parser.parse_args()
    parse_res = vars(parse_res_raw)

    global llvm_parser
    llvm_parser = parser.LLVMParser()
    llvm_parser.build()

    if parse_res['auto_path'] is not None:
        go_auto(parse_res['auto_path'])
    else:
        enter_interactive_mode()


def go_auto(path_to_file):
    with open(path_to_file, 'r') as f:
        file_contents = f.read()
    print('Parsing {}'
          .format(path_to_file))
    ast = llvm_parser.parse(file_contents)
    print('Beginning execution of {}'
          .format(path_to_file))
    stepper.auto_step(ast)


def enter_interactive_mode():
    print('TODO: Interactive mode has not been implemented yet. Sorry...')
