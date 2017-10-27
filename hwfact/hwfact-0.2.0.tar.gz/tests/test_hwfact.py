#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hwfact` package."""


from hwfact.hwfact import size_to_gb, total_ram, to_gist


def test_size():
    hp = 'Size: 16384 MB'
    assert size_to_gb(hp) == 16
    sm = 'Size: 32 GB'
    assert size_to_gb(sm) == 32


def test_total_memory_hp():
    empty = {'Array Handle': '0x1000',
             'Asset Tag': 'Not Specified',
             'Bank Locator': 'Not Specified',
             'Configured Clock Speed': 'Unknown',
             'Data Width': '64 bits',
             'Error Information Handle': 'Not Provided',
             'Form Factor': 'DIMM',
             'Locator': 'PROC 1 DIMM 1G',
             'Manufacturer': 'Not Specified',
             'Part Number': 'Not Specified',
             'Rank': 'Unknown',
             'Serial Number': 'Not Specified',
             'Set': '1',
             'Size': 'No Module Installed',
             'Speed': 'Unknown',
             'Total Width': '72 bits',
             'Type': 'DDR3',
             'Type Detail': 'Synchronous',
             '_title': 'Memory Device'}

    memory = {'Array Handle': '0x1000',
              'Asset Tag': 'Not Specified',
              'Bank Locator': 'Not Specified',
              'Configured Clock Speed': '1066 MHz',
              'Data Width': '64 bits',
              'Error Information Handle': 'Not Provided',
              'Form Factor': 'DIMM',
              'Locator': 'PROC 1 DIMM 2D',
              'Manufacturer': 'Not Specified',
              'Part Number': 'Not Specified',
              'Rank': '2',
              'Serial Number': 'Not Specified',
              'Set': '2',
              'Size': '4096 MB',
              'Speed': '1333 MHz',
              'Total Width': '72 bits',
              'Type': 'DDR3',
              'Type Detail': 'Synchronous',
              '_title': 'Memory Device'}

    assert total_ram([empty]) == 0
    assert total_ram([memory, memory, empty]) == 8


def test_sum_up_dmidecode_HP():
    gist = to_gist(open('tests/dmiraw.txt', 'r').read())
    assert gist == {'ram_gb': 48,
                    'serial_number': 'CZXZHERO',
                    'model': 'ProLiant DL360 G7',
                    'firmware': '1.82',
                    'cpu_description': 'Intel(R) Xeon(R) CPU E5620 @ 2.40GHz',
                    'manufacturer': 'HP', 'nb_processor': 2, 'nb_thread': 16}
