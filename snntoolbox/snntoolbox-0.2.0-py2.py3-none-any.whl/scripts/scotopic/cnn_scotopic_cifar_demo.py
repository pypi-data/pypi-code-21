# coding=utf-8

"""CNN scotopic CIFAR-10 demo."""

from scripts.scotopic.cnn_scotopic import cnn_scotopic
from scripts.scotopic.bin.utils import update_setup

filepath = 'scripts/scotopic/config_cifar10'
config = update_setup(filepath)

cnn_scotopic(config)
