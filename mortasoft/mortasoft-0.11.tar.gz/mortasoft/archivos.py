#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# @Date    : 2017-11-24 10:20:10
# @Author  : mortasoft (mario@mortasoft.com)
# @Link    : http://mortasoft.xyz
# @Version : $Id$
import glob, os

def listar(ruta):

	filelist = glob.glob("*"+ruta+"*",recursive=True)
	for f in filelist:
		print(f)

def leer(ruta):
    try:
        file = open(ruta,"r")
        line = file.readlines()
        return line
    except:
        return file

def escribirLinea(texto,ruta):
	try:
		file = open(ruta,"a")
		file.write(texto+"\n")
		file.close
	except Exception as e:
		print("Error al escribir en el archivo: "+e)

def escribir(texto,ruta):
	try:
		file = open(ruta,"w")
		file.write(texto)
		file.close
	except Exception as e:
		print("Error al escribir en el archivo: "+e)
	