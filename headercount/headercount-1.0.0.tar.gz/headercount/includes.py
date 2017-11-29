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

"""Functions that search files for include directives."""

import itertools


class AmbiguousName(Exception):
    """There is more than one matching file for an include directive."""


def get_includes_lists(paths, inclusive):
    """For each path in `paths`, return a list of included files.

    Args:
        paths: An iterable of `pathlib.Path`s to search.
        inclusive: If `True`, this lists not only a file's direct
            includes, but also its includes' includes, etc. Only files
            that are passed via `paths` are search recursively. If
            `False`, only direct includes are listed.

    Returns:
        A mapping from a file's path to the files included by said
        file (either directly or indirectly).
    """
    flat_lists = get_flat_includes_lists(paths)
    return _get_deep_includes_lists(flat_lists) if inclusive else flat_lists


def get_flat_includes_lists(paths):
    """For each path in `paths`, return a list of included files.

    Returns:
        A mapping from a file's path to the files directly included by
        said file.
    """
    includes = {}
    for path in paths:
        with path.open('r') as file_:
            includes[path] = list(iter_includes(file_))
    return includes


def _get_deep_includes_lists(flat_lists):

    """Takes the result of `get_includes_lists` and expands it."""

    include_map = _build_include_map(
        includes=set(itertools.chain.from_iterable(flat_lists.values())),
        available_files=flat_lists.keys(),
        )

    # The dict in which we collect our results.
    inclusive_lists = {}

    def _iter_direct_includes(path):
        """Iterate a file's direct includes, skip those not to be searched."""
        return iter(flat_lists[path])

    def _collect_all_includes(path):
        """Put together the direct and indirect includes of a file."""
        direct_includes = flat_lists[path]
        direct_include_files = (include_map.get(direct_include)
                                for direct_include in direct_includes)
        indirect_includes = (inclusive_lists.get(path, [])
                             for path in direct_include_files
                             if path)
        return list(itertools.chain(direct_includes, *indirect_includes))

    # Iterative depth-first search with a stack of iterators.
    stack = [(path, _iter_direct_includes(path)) for path in flat_lists.keys()]
    files_being_searched = set(flat_lists.keys())
    while stack:
        path, includes_to_handle = stack[-1]
        include = next(includes_to_handle, None)
        if include is None:
            # We have collected all direct+indirect includes for every
            # direct include of `path`. Now we can put them together.
            inclusive_lists[path] = _collect_all_includes(path)
            files_being_searched.remove(path)
            stack.pop()
            continue
        # Guess which file this include directive references.
        include_file = include_map.get(include)
        is_to_be_searched = (include_file and
                             include_file not in inclusive_lists and
                             include_file not in files_being_searched)
        if is_to_be_searched:
            # The included file is to be searched and we have not
            # searched it already _and_ it is not included in a
            # circular manner. Thus, we descend into it.
            stack.append((include_file, _iter_direct_includes(include_file)))
            files_being_searched.add(include_file)

    return inclusive_lists


def _build_include_map(includes, available_files):
    """Build a map of guesses which include directive maps to which file.

    Args:
        includes: A list of `Include` objects.
        available_files: A list of files that the include directives
            could possibly map to.

    Returns:
        A mapping `include => available_file` of all `include`s for
        which a file could be found.

    Raises:
        `AmbiguousName` if there are several candidates for a given
        `include`.
    """
    result = {}
    for include in includes:
        candidates = [path for path in available_files
                      if path.name == include.unquoted()]
        if len(candidates) > 1:
            raise AmbiguousName(str(include))
        elif candidates:
            (result[include],) = candidates
    return result


def iter_includes(file_):
    """Iterate over include directives in a file.

    Args:
        file_: A file object to read from.
        ignore_system: If `True`, "#include <...>" lines are ignored.

    Returns:
        An iterator over files included by `file_`. Inclusion is
        determined by searching for #include directives.
    """
    for line in file_:
        line = line.lstrip()
        if not line.startswith('#'):
            continue
        parts = line[1:].split()
        if parts[0] != 'include':
            continue
        yield Include(parts[1])


class Include(str):

    """Type representing `#include` directives.

    For speed and ease of implementation, this inherits from `str`.
    """

    def __new__(cls, *args, **kwargs):
        """Create a new instance.

        Examples:

            >>> Include('<vector>')
            >>> Include('"MyHeader.hpp"')

        Raises:
            ValueError if the given string is not wrapped by
                `#include`-style quotes (either double quotes or angle
                brackets).
        """
        result = super().__new__(cls, *args, **kwargs)
        is_system = result[0] == '<' and result[-1] == '>'
        is_regular = result[0] == '"' == result[-1]
        if not (is_system or is_regular):
            raise ValueError('cannot find quotes: '+repr(result))
        return result

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, str(self))

    def is_system(self):
        """Return `True` if the include directive uses angle brackets."""
        return self[0] == '<'

    def unquoted(self):
        """Remove quotes and return the basename of the included file."""
        return self[1:-1]
