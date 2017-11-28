#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# @Date    : 2017-11-24 10:20:10
# @Author  : mortasoft (mario@mortasoft.com)
# @Link    : http://mortasoft.xyz
# @Version : $Id$

def imprimir(texto,color=''):
	salida=''
	if color=='rojo':
		print(chr(27) + "[0;31m" + texto + chr(27) + "[0m")
	if color=='verde':
		print(chr(27) + "[0;32m" + texto + chr(27) + "[0m")
	if color=='amarillo':
		print(chr(27) + "[0;33m" + texto + chr(27) + "[0m")
	if color=='azul':
		print(chr(27) + "[0;34m" + texto + chr(27) + "[0m")
	if color=='morado':
		print(chr(27) + "[0;35m" + texto + chr(27) + "[0m")
	if color=='magenta':
		print(chr(27) + "[0;36m" + texto + chr(27) + "[0m")
	if color=='blanco':
		print(chr(27) + "[0;37m" + texto + chr(27) + "[0m")
	if color=='gris':
		print(chr(27) + "[0;30m" + texto + chr(27) + "[0m")