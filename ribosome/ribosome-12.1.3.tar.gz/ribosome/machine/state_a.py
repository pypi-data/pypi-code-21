#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x1bb3a1c7

# Compiled with Coconut version 1.3.0 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop
import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_NamedTuple, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_pipe, _coconut_star_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: -----------------------------------------------------------

from typing import TypeVar  # line 1

from lenses import Lens  # line 3

from amino.do import tdo  # line 5
from amino import IO  # line 6
from amino import List  # line 6
from amino import Path  # line 6
from amino import Left  # line 6
from amino.json import decode_json  # line 7
from amino.json import dump_json  # line 7

from ribosome.nvim import NvimIO  # line 9
from ribosome.nvim.io import NvimIOState  # line 10
from ribosome.settings import AutoData  # line 11

A = TypeVar('A')  # line 13
D = TypeVar('D', bound=AutoData)  # line 14


@tdo(NvimIOState[D, Path])  # line 17
def state_file(name: 'str') -> 'Generator':  # line 18
    settings = yield NvimIOState.inspect(lambda a: a.settings)  # line 19
    dir = yield NvimIOState.lift(settings.state_dir.value_or_default)  # line 20
    yield NvimIOState.lift(NvimIO.from_io(IO.delay(dir.mkdir, parents=True, exist_ok=True)))  # line 21
    yield NvimIOState.pure(dir / f'{name}.json')  # line 22


@tdo(NvimIOState[D, None])  # line 25
def load_json_data(name: 'str') -> 'Generator':  # line 26
    file = yield state_file(name)  # line 27
    exists = yield NvimIOState.lift(NvimIO.from_io(IO.delay(file.exists)))  # line 28
    if exists:  # line 29
        json = yield NvimIOState.lift(NvimIO.from_io(IO.delay(file.read_text)))  # line 30
        yield NvimIOState.pure(decode_json(json))  # line 31
    else:  # line 32
        yield NvimIOState.pure(Left(f'state file {file} does not exist'))  # line 33


@_coconut_tco  # line 36
def load_json_state(name: 'str', l: 'Lens') -> 'NvimIOState[D, None]':  # line 36
    return _coconut_tail_call(load_json_data(name).cata, lambda a: NvimIOState.pure(None), lambda d: NvimIOState.modify(lambda a: l.bind(a).set(d)))  # line 37


@tdo(NvimIOState[D, None])  # line 40
def store_json_data(name: 'str', data: 'A') -> 'Generator':  # line 41
    file = yield state_file(name)  # line 42
    json = yield NvimIOState.lift(NvimIO.from_either(dump_json(data)))  # line 43
    yield NvimIOState.lift(NvimIO.from_io(IO.delay(file.write_text, json)))  # line 44
    yield NvimIOState.pure(None)  # line 45


@tdo(NvimIOState[D, None])  # line 48
def store_json_state(name: 'str', data: '_coconut.typing.Callable[[D], A]') -> 'Generator':  # line 49
    payload = yield NvimIOState.inspect(data)  # line 50
    yield store_json_data(name, payload)  # line 51

__all__ = ('load_json_state', 'store_json_data', 'store_json_state')  # line 53
