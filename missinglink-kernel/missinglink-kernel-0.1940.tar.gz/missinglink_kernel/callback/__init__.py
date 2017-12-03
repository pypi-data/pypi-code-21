# coding=utf-8
from .keras_callback import KerasCallback
from .tensorflow_callback import TensorFlowCallback
from .tensorflow_project import TensorFlowProject
from .pytorch_callback import PyTorchCallback
from .pycaffe_callback import PyCaffeCallback

global_root_logger_sniffer = None


def set_global_root_logger_sniffer(global_root_logger_sniffer_):
    global global_root_logger_sniffer

    global_root_logger_sniffer = global_root_logger_sniffer_


def get_global_root_logger_sniffer():
    return global_root_logger_sniffer


__all__ = [
    'KerasCallback', 'TensorFlowCallback', 'PyTorchCallback', 'PyCaffeCallback', 'TensorFlowProject',
    'set_global_root_logger_sniffer']
