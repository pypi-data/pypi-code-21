#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

import jk_utils





#
# Items in this enumeration define the high level data types a column may have.
#
class EnumDBColType(jk_utils.EnumBase):

	PK = 10, 'pk'
	BOOL = 20, 'bool'
	INT32 = 30, 'int32'
	INT64 = 31, 'int64'
	DOUBLE = 40, 'double'
	STR256 = 50, 'str256'
	CLOB = 60, 'clob'
	BLOB = 70, 'blob'

#




