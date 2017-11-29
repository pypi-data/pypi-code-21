# -*- coding: utf-8 -*-

# Copyright 2017 Nico Madysa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains the functions for input file collection."""

from pathlib import Path

HEADER_SUFFIXES = frozenset(['.h', '.H', '.hh', '.hp', '.hpp', '.HPP',
                             '.hxx', '.h++', '.inl', '.tcc', '.icc'])

SOURCE_SUFFIXES = frozenset(['.c', '.C', '.cc', '.cp', '.cpp', '.CPP',
                             '.cxx', '.c++', '.i', '.ii'])

CPP_SUFFIXES = frozenset.union(HEADER_SUFFIXES, SOURCE_SUFFIXES)


def iter_input_files(args, recursive, exclude, exclude_dir):
    """Iterate over all input files specified by the given arguments.

    Args:
        args: An iterable of file and directory names.
        recursive: If `True`, recursively search directories for input
            files. If `False`, ignore directory names.
        exclude: A list of shell-like glob patterns. If an input file
            name matches any of these patterns, it is ignored.
        exclude_dir: As `exclude`, but applied to directory names. If
            `recursive` is `False`, this has no effect.

    Returns:
        An iterator over all input file names. Input files must have a
        file suffix given in `CPP_SUFFIXES`.
    """
    if recursive:
        return _iter_input_files_deep(args, exclude, exclude_dir)
    else:
        return _iter_input_files_flat(args, exclude)


def _iter_input_files_flat(args, exclude):
    """Non-recursive version of `iter_input_files`."""
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            pass
            # log
        elif path.suffix in CPP_SUFFIXES and not _any_match(path, exclude):
            yield path


def _iter_input_files_deep(args, exclude, exclude_dir):
    """Recursive version of `iter_input_files`."""
    stack = [Path(arg) for arg in reversed(args)]
    while stack:
        path = stack.pop()
        if path.is_dir():
            if not _any_match(path, exclude_dir):
                stack.extend(path.iterdir())
        elif path.suffix in CPP_SUFFIXES and not _any_match(path, exclude):
            yield path


def _any_match(path, patterns):
    """True if any of the given patterns match `path`."""
    return any(path.match(pattern) for pattern in patterns)
