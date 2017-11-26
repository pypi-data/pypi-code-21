u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import absolute_import
from typing import List
from toktokkie.utils.iconizing.procedures.GnomeProcedure import GnomeProcedure
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure
from toktokkie.utils.iconizing.procedures.DesktopIniProcedure import \
    DesktopIniProcedure


class ProcedureManager(object):
    u"""
    Class that offers an interface for choosing the
    correct iconization procedure
    """

    implemented_procedures = [GnomeProcedure,
                              DesktopIniProcedure]
    u"""
    List of currently implemented procedures
    """

    @staticmethod
    def get_all_procedures():
        u"""
        :return: A list of all implemented procedures
        """
        return ProcedureManager.implemented_procedures

    @staticmethod
    def get_procedure_names(supports_current_platform = True):
        u"""
        :param supports_current_platform: Can be set to True if only procedures
                                          for the current platform should be
                                          shown, and False if all implemented
                                          procedures should be returned
        :return:                          A list of implemented procedure names
        """
        procedure_names = []
        for procedure in ProcedureManager.implemented_procedures:
            if supports_current_platform:
                if procedure.is_applicable():  # pragma: no cover
                    procedure_names.append(procedure.get_procedure_name())
            else:
                procedure_names.append(procedure.get_procedure_name())
        return procedure_names

    @staticmethod
    def get_procedure_from_procedure_name(procedure_name):
        u"""
        Turns a procedure name into a Procedure class and returns it

        :param procedure_name: the procedure name of the procedure to return
        :return:               the procedure's class, or None if the name did
                               not match any implemented procedure
        """
        for procedure in ProcedureManager.implemented_procedures:
            if procedure_name == procedure.get_procedure_name():
                return procedure
        return GenericProcedure

    @staticmethod
    def get_applicable_procedure():
        u"""
        Gets an applicable iconizing procedure from the list of
        implemented procedures

        :return: The iconizing procedure,
                 or None if no applicable procedure was found
        """
        for procedure in ProcedureManager.implemented_procedures:
            if procedure.is_applicable():  # pragma: no cover
                return procedure
        return GenericProcedure
