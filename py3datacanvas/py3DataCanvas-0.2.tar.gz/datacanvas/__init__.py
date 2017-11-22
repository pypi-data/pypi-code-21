# -*- coding: utf-8 -*-

from .version import version

__version__ = version
__author__ = "xiaolin"

from datacanvas.clusters import EmrCluster
from datacanvas.log_parser import parse_syslog, parse_s3_stderr
from datacanvas.module import Input, Output, Param
from datacanvas.runtime import DatacanvasRuntime, HadoopRuntime, PigRuntime, HiveRuntime, \
    EmrRuntime, EmrHiveRuntime, EmrJarRuntime, EmrPigRuntime
from datacanvas.utils import cmd
