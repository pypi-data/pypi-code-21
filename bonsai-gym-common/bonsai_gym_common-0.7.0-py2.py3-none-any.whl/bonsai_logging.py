"""
This file contains functionality related to logging.
"""
import logging

import bonsai
import gym


def logging_basic_config(level=logging.INFO):
    """
    This function first undoes gym's default logging configuration, and
    then calls into bonsai.logging_basic_config() to allow it to configure
    a simple root logger. If you are using gym or GymSimulator, use this
    function instead of calling bonsai.logging_basic_config() directly.

    Make sure you call this function after you 'import gym', as gym will
    configure a root logger by default on import. Doing that is usually
    a bad pattern for a third party package, though fortunately they
    expose a method for undoing it. For more on gym's reasons for
    configuring logging like this, see the conversation here:
    https://github.com/openai/gym/pull/199
    """
    gym.undo_logger_setup()
    bonsai.logging_basic_config(level=level)
