#!/usr/bin python3.6

import os
import argparse

__author__ = 'Oleksandr Rypiuk'


def get_sorted_files_size(the_path: str, number_of_files: int, min_first: bool):

    result = get_result(path_to_dir=the_path, min_size_first=min_first)

    if not result:
        print(f"There are no files, or the path '{the_path}' does not exist")
        return

    if number_of_files > len(result):
        number_of_files = len(result)
    elif number_of_files <= 0:
        number_of_files = 1

    # Set the size of the table columns
    bytes_column_len = len(str(result[0][1])) if not min_first else len(str(result[number_of_files-1][1]))
    number_column_len = len(str(number_of_files))
    megabytes_column_len = bytes_column_len - 6 if bytes_column_len - 6 > 0 else 1

    print(f'Path: {the_path}')
    print(f'Number of files: {len(result)}')

    print_the_table(number_column_len, bytes_column_len, megabytes_column_len, number_of_files, result)


def print_the_table(number_column_len: int, bytes_column_len: int,
                    megabytes_column_len: int, number_of_files: int, result: list):
    # The header
    print(f'{"№":>{number_column_len}} | {"B":^{bytes_column_len}} | {"MB":^{megabytes_column_len+2}} | Path')

    # The content
    for i in range(number_of_files):
        print(f'{i+1:{number_column_len}} | {result[i][1]:{bytes_column_len}} | '
              f'{result[i][1] * 0.000001:{megabytes_column_len+2}.1f} | {result[i][0]}')


def get_result(path_to_dir: str, min_size_first: bool):
    """
    Get recursively information about the size of files in subdirectories
    and sort it according to the size
    """
    result = {}
    for root, dirs, files in os.walk(path_to_dir):
        for file in files:
            path = os.path.join(root, file)
            try:
                size = os.stat(path).st_size
            except FileNotFoundError:
                print('There is no such file or directory:', path)
            else:
                result[path] = size

    return sorted(result.items(), key=lambda x: x[1], reverse=not min_size_first)


def main():
    parser = argparse.ArgumentParser(description='Displays sorted information about size, '
                                                 'path to files in subdirectories.')
    parser.add_argument('-p', dest='path', metavar='PATH', help='the path to parent dir', action='store',
                        default=os.getcwd())
    parser.add_argument('-n', type=int, dest='number', metavar='NUMBER', help='how much files will be shown',
                        action='store', default=5)
    parser.add_argument('-m', '--min', help='sort by min size', action='store_true')

    args = parser.parse_args()
    get_sorted_files_size(the_path=args.path, number_of_files=args.number, min_first=args.min)


if __name__ == '__main__':
    main()
