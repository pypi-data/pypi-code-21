"""
Main module of the program.

To start the application, call the main function. For the end user,
this is achieved by a script stored in the bin folder.

"""

import argparse

from llvm_emulator import stepper, parser


def make_argument_parser():
    arg_parser = argparse.ArgumentParser(description='A hacky LLVM-- emulator/debugger')

    commands = arg_parser.add_subparsers(dest='main_command')
    auto_parser = commands.add_parser('auto',
                                      help=('Automatically step through llvm'
                                            ' in a given file'))
    auto_parser.add_argument('path_to_llvm_file',
                             metavar='PATH', type=str,
                             help='Path to the file containing the LLVM IR')

    auto_parser.add_argument('-pf', '--pause-frequency',
                             metavar='STEPS', type=int, default=100,
                             help=('Number of steps to automatically run between pausing'
                                   ' to ask, if you want to continue. A value less than'
                                   ' one makes the stepper never pause. '
                                   'Default: %(default)s'))

    return arg_parser


def main():
    arg_parser = make_argument_parser()
    parse_res_raw = arg_parser.parse_args()
    parse_res = vars(parse_res_raw)

    global llvm_parser
    llvm_parser = parser.LLVMParser()
    llvm_parser.build()

    main_command = parse_res['main_command']
    if main_command == 'auto':
        go_auto(parse_res['path_to_llvm_file'], parse_res['pause_frequency'])
    elif main_command is None:
        enter_interactive_mode()
    else:
        print('TODO: Command {} not implemented yet'
              .format(main_command))


def go_auto(path_to_file, pause_frequency):
    with open(path_to_file, 'r') as f:
        file_contents = f.read()
    print('Parsing {}'
          .format(path_to_file))
    ast = llvm_parser.parse(file_contents)
    print('Beginning execution of {}'
          .format(path_to_file))
    freq = None if pause_frequency < 1 else pause_frequency
    stepper.auto_step(ast, pause_frequency=freq)


def enter_interactive_mode():
    print('TODO: Interactive mode has not been implemented yet. Sorry...')
