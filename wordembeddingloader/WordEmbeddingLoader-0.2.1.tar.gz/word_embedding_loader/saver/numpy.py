# -*- coding: utf-8 -*-
"""
Low level API for saving of word embedding file to numpy npz format.
"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json

import numpy


def save(f, arr, vocab):
    """
    Save word embedding file.
    Check :func:`word_embedding_loader.saver.glove.save` for the API.
    """
    numpy.savez(f, arr=arr, vocab=json.dumps(vocab))


def save_compressed(f, arr, vocab):
    """
    Save word embedding file.
    Check :func:`word_embedding_loader.saver.glove.save` for the API.
    """
    numpy.savez_compressed(f, arr=arr, vocab=json.dumps(vocab))
