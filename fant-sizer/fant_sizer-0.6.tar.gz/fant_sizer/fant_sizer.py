#!/usr/bin python3.6

import os
import argparse

__author__ = 'Oleksandr Rypiuk'


def _get_sorted_files_size(the_path: str, number_of_output_files: int, min_first: bool):

    result = get_sorted_files_by_size(path_to_root_dir=the_path, min_size_first=min_first)

    if not result:
        print(f"There are no files, or the path '{the_path}' does not exist")
        return

    print_the_table(path_to_root_dir=the_path, sorted_list_of_files_by_size=result,
                    number_of_output_files=number_of_output_files, min_first=min_first)


def print_the_table(path_to_root_dir: str, sorted_list_of_files_by_size: list,
                    number_of_output_files: int, min_first: bool = False):

    if number_of_output_files > len(sorted_list_of_files_by_size):
        number_of_output_files = len(sorted_list_of_files_by_size)
    elif number_of_output_files <= 0:
        number_of_output_files = 1

    # Set the size of the table columns
    bytes_column_len = len(str(sorted_list_of_files_by_size[0][1])) if not min_first else \
        len(str(sorted_list_of_files_by_size[number_of_output_files - 1][1]))
    number_column_len = len(str(number_of_output_files))
    megabytes_column_len = bytes_column_len - 6 if bytes_column_len - 6 > 0 else 1

    print(f'Path: {path_to_root_dir}')
    print(f'Number of files: {len(sorted_list_of_files_by_size)}')

    # The header
    print(f'{"№":>{number_column_len}} | {"B":^{bytes_column_len}} | {"MB":^{megabytes_column_len+2}} | Path')

    # The content
    for i in range(number_of_output_files):
        print(f'{i+1:{number_column_len}} | {sorted_list_of_files_by_size[i][1]:{bytes_column_len}} | '
              f'{sorted_list_of_files_by_size[i][1] * 0.000001:{megabytes_column_len+2}.1f} | '
              f'{sorted_list_of_files_by_size[i][0]}')


def get_sorted_files_by_size(path_to_root_dir: str = os.getcwd(),
                             min_size_first: bool = False, debug_mode: bool = True):
    """
    Get recursively information about the size of files in subdirectories
    and sort it according to the size
    """
    result = {}
    for root, dirs, files in os.walk(path_to_root_dir):
        for file in files:
            path = os.path.join(root, file)
            try:
                size = os.stat(path).st_size
            except FileNotFoundError:
                print('There is no such file or directory:', path) if debug_mode else None
            else:
                result[path] = size

    return sorted(result.items(), key=lambda x: x[1], reverse=not min_size_first)


def get_the_biggest_file(path_to_root_dir: str) -> tuple:
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    if not result:
        print(f'Bad path to root directory: {path_to_root_dir}')
        return None, None
    return result[0][0], result[0][1]


def get_the_smallest_file(path_to_root_dir: str) -> tuple:
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    if not result:
        print(f'Bad path to root directory: {path_to_root_dir}')
        return None, None
    return result[-1][0], result[-1][1]


def main():
    parser = argparse.ArgumentParser(description='Displays sorted information about size, '
                                                 'path to files in subdirectories.')
    parser.add_argument('-p', dest='path', metavar='PATH', help='the path to parent dir', action='store',
                        default=os.getcwd())
    parser.add_argument('-n', type=int, dest='number', metavar='NUMBER', help='how much files will be shown',
                        action='store', default=5)
    parser.add_argument('-m', '--min', help='sort by min size', action='store_true')

    args = parser.parse_args()
    _get_sorted_files_size(the_path=args.path, number_of_output_files=args.number, min_first=args.min)


if __name__ == '__main__':
    main()
