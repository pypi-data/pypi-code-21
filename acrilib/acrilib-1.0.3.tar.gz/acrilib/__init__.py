# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from .VERSION import __version__

from .idioms.decorate import traced_method, LogCaller
from .idioms.threaded import Threaded, RetriveAsycValue, threaded
from .idioms.singleton import Singleton, NamedSingleton
from .idioms.sequence import Sequence
from .idioms.data_types import MergedChainedDict
from .idioms.synchronize import Synchronization, SynchronizeAll, dont_synchronize, do_synchronize, synchronized
from .idioms.mediator import Mediator

from .idioms.osutil import get_free_port, get_ip_address, get_hostname, hostname_resolves

from .logging.formatters import LoggerAddHostFilter, LevelBasedFormatter, MicrosecondsDatetimeFormatter
from .logging.handlers import TimedSizedRotatingHandler, HierarchicalTimedSizedRotatingHandler, get_file_handler
from .logging.logsim import LogSim