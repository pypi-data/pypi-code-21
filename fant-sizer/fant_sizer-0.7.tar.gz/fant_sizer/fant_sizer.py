#!/usr/bin python3.6

import os
import argparse
from collections import Counter

__author__ = 'Oleksandr Rypiuk'


def _get_sorted_files_size(the_path: str, number_of_output_files: int, min_first: bool):
    """
    :param the_path: path to the directory, to be processed (with subdirectories too)
    :param number_of_output_files: how many file will be shown
    :param min_first: sorted by min/max size
    """
    result = get_sorted_files_by_size(path_to_root_dir=the_path, min_size_first=min_first)

    print_the_table(path_to_root_dir=the_path, sorted_list_of_files_by_size=result,
                    number_of_output_files=number_of_output_files, min_first=min_first)


def print_the_table(path_to_root_dir: str, sorted_list_of_files_by_size: list,
                    number_of_output_files: int, min_first: bool = False):
    """
    Print a table according parameters
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :param sorted_list_of_files_by_size: list of tuples [(path, size)]
                                         e.g [('file/path.txt', 125), ('file/path2.txt', 2)...]
    :param number_of_output_files: how many file will be shown
    :param min_first: sorted by min/max size
    """
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
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :param min_size_first: sorted by min/max size
    :param debug_mode: print some additional information, or not
    :return: sorted list of tuples

    :Example:
    >>> from fant_sizer import fant_sizer
    >>> fant_sizer.get_sorted_files_by_size(path_to_root_dir='/home')
    >>> [('/home/some/dir/file.py', 21), ('/home/some/another_file.py', 10)]
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
    if not result:
        raise OSError(f"There are no files, or the path '{path_to_root_dir}' does not exist")
    return sorted(result.items(), key=lambda x: x[1], reverse=not min_size_first)


def get_the_biggest_file(path_to_root_dir: str) -> tuple:
    """
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :return: tuple ('/path/to/file.txt', 21)
    """
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    return result[0]


def get_the_smallest_file(path_to_root_dir: str) -> tuple:
    """
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :return: tuple ('/path/to/file.txt', 0)
    """
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    return result[-1]


def get_the_average_size_of_the_files(path_to_root_dir: str) -> float:
    """
    The sum of the sizes divided by how many files are in the directory
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :return: float average size of files
    """
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    sum_of_file_sizes = sum([size for path, size in result])
    number_of_files = len(result)
    average_size = sum_of_file_sizes / number_of_files
    return average_size


def get_median_of_the_files(path_to_root_dir: str) -> int or float:
    """
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :return: the middle value of an ordered list of sizes
    """
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    if len(result) % 2 is not 0:
        median = (result[len(result) // 2][1] + result[len(result) // 2 + 1][1]) / 2
        median = median if not median.is_integer() else int(median)
    else:
        median = result[len(result) // 2][1]
    return median


def get_range_of_the_files(path_to_root_dir: str) -> int:
    """
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :return: the difference between the min and max file sizes
    """
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    return result[0][1] - result[-1][1]


def get_mode_of_the_files(path_to_root_dir: str) -> list:
    """
    :param path_to_root_dir: path to the directory, to be processed (with subdirectories too)
    :return: file sizes repeated most often
    """
    result = get_sorted_files_by_size(path_to_root_dir=path_to_root_dir, debug_mode=False)
    counter = Counter([size for _, size in result])
    max_count = max(counter.values())
    mode = [key for key, value in counter.items() if value == max_count]  # FIXME max_count + 100 or - 100
    return mode


def _main():
    parser = argparse.ArgumentParser(description='Displays sorted information about size, '
                                                 'path to files in subdirectories.')
    parser.add_argument('-p', dest='path', metavar='PATH', help='the path to parent dir', action='store',
                        default=os.getcwd())
    parser.add_argument('-n', type=int, dest='number', metavar='NUMBER', help='how much files will be shown',
                        action='store', default=5)
    parser.add_argument('-m', '--min', help='sort by min size', action='store_true')
    parser.add_argument('--biggest', help='get information about the biggest file', action='store_true')
    parser.add_argument('--smallest', help='get information about the smallest file', action='store_true')
    parser.add_argument('--average', help='get the sum of the sizes divided by how many files are in the directory',
                        action='store_true')
    parser.add_argument('--median', help='get the middle value of an ordered list of sizes', action='store_true')
    parser.add_argument('--range', help='get the difference between the min and max file sizes', action='store_true')
    parser.add_argument('--mode', help='get file sizes repeated most often', action='store_true')

    args = parser.parse_args()
    if args.biggest:
        the_biggest_file = get_the_biggest_file(path_to_root_dir=args.path)
        print_the_table(path_to_root_dir=args.path,
                        sorted_list_of_files_by_size=[the_biggest_file], number_of_output_files=1)
    elif args.smallest:
        the_smallest_file = get_the_smallest_file(path_to_root_dir=args.path)
        print_the_table(path_to_root_dir=args.path,
                        sorted_list_of_files_by_size=[the_smallest_file], number_of_output_files=1)
    elif args.average:
        average = get_the_average_size_of_the_files(path_to_root_dir=args.path)
        print(f'The average size of the files is: {average:.2f} bytes.')
    elif args.median:
        median = get_median_of_the_files(path_to_root_dir=args.path)
        print(f'The middle value of an ordered list of sizes is: {median} bytes.')
    elif args.range:
        the_range = get_range_of_the_files(path_to_root_dir=args.path)
        print(f'The difference between the min and max file sizes is: {the_range} bytes.')
    elif args.mode:
        modes = get_mode_of_the_files(path_to_root_dir=args.path)
        print(f'The file sizes repeated most often is: {", ".join(str(mode) for mode in modes)} bytes.')
    else:
        _get_sorted_files_size(the_path=args.path, number_of_output_files=args.number, min_first=args.min)


if __name__ == '__main__':
    _main()
