####################################################################################################
#
# Musica - A Music Theory Package for Python
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

# from ..Tools.ParameterChecker import ParameterChecker

# __ctor_checker__ = ParameterChecker(
#     arg=('x', 'y',
#          'clone'
#         )
#     )

# args = self.__ctor_checker__(args, kwargs)

# Fixme: setattr
# self.x = args['x']
# self.y = args['y']

####################################################################################################

class ParameterChecker:

    ##############################################

    def __init__(self, args_list, kwargs):

        self._args = {}
        self._kwargs = {}

        for args in args_list:
            number_of_args = len(args)
            if number_of_args not in self._args:
                self._args[number_of_args] = args
            else:
                raise NameError("Invalid args_list")
            self._kwargs.extend({name:None for args in args_list})

        self._default = {key:value for key, value in self._kwargs.items()}

    ##############################################

    def valid(self, *args, **kwargs):

        number_of_args = len(args)
        arg_names = self._args.get(number_of_args, None)
        if arg_names is not None:
            out_kwargs = {name:value for name, value in zip(arg_names, args)}
        else:
            out_kwargs = {}

        for key, value in kwargs:
            if key in self._kwargs:
                out_kwargs[key] = value

        for key, value in kwargs:
