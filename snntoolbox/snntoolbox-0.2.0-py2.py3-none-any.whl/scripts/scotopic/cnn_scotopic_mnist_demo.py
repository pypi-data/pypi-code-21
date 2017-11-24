# coding=utf-8

"""CNN scotopic mnist demo."""

from scripts.scotopic.cnn_scotopic import cnn_scotopic
from scripts.scotopic.bin.utils import update_setup

filepath = 'scripts/scotopic/config_mnist'
config = update_setup(filepath)

cnn_scotopic(config)
