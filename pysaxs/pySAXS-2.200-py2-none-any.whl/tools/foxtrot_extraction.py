#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#
# Extracting script for Foxtrot application
#
# Author: Stephane Poirier
# date  : 2009/09/11
#
# version: 1.3
#
# usage: python foxtrot_extraction.py <path/to/nexus_file> <destination/path>
#

# importing pytables module
from tables import *

# generic modules
import sys
import os
import os.path
import re

# global variables
g_macro_names_translation = {'Ave':'data-average', 'Sum':'sum-data', 'Sub':'sub-data', 'JoinS':'joined-data(stat)', 'JoinV':'joined-data(var)', 'Lin':'linear-data', 'Sca':'scaled-data' }
g_macro_names_translation_2 = {'Average':'Ave', 'Subtract':'Sub', 'LinearFunction':'Lin', 'Spectra':'' }
g_result_names = ['RadialIntensity', 'AzimuthalIntensity', 'projection', 'meanProjection']
g_file_ext = '.dat'
g_header_separator = '#####################################################################################################\n'

#------------------------------------------------------------------------------
def write_output_results(f, I, Sig, Q, twoTheta, Psi, concat_string):
	# comment next 2 lines to activate twoTheta
	if Q is not None:
		twoTheta = None

	if I is not None:
		qname = "q(A-1)"
		twoThetaname = "2Theta(degrees)"
		psiname = "Psi(degrees)"
		iname = "I(q)" + concat_string
		signame = "Sig(q)" + concat_string
		# Compute best output format (100 characters max)
		length = max(len(iname), len(signame))
		xFormat = '%-20s'
		yFormat = '%-100s'
		for i in range(10):
			mult = (i + 1) * 10
			if length < mult:
				yFormat = '%-' + str(mult) + 's'
				break
		if Psi is not None:
			if Sig is None:
				# Result titles
				format = xFormat + yFormat + '\n'
				f.write(format %  (psiname, iname))
				# Result values
				for i in range(len(Psi)):
					f.write(xFormat % Psi[i])
					f.write(yFormat % I[i])
					f.write('\n')
			else:
				# Result titles
				format = xFormat + yFormat + yFormat + '\n'
				f.write(format %  (psiname, iname, signame))
				# Result values
				for i in range(len(Psi)):
					f.write(xFormat % Psi[i])
					f.write(yFormat % I[i])
					f.write(yFormat % Sig[i])
					f.write('\n')
		elif Q is None:
			if twoTheta is not None:
				if Sig is None:
					# Result titles
					format = xFormat + yFormat + '\n'
					f.write(format %  (twoThetaname, iname))
					# Result values
					for i in range(len(twoTheta)):
						f.write(xFormat % twoTheta[i])
						f.write(yFormat % I[i])
						f.write('\n')
				else:
					# Result titles
					format = xFormat + yFormat + yFormat + '\n'
					f.write(format %  (twoThetaname, iname, signame))
					# Result values
					for i in range(len(twoTheta)):
						f.write(xFormat % twoTheta[i])
						f.write(yFormat % I[i])
						f.write(yFormat % Sig[i])
						f.write('\n')
		elif twoTheta is None:
			if Sig is None:
				# Result titles
				format = xFormat + yFormat +'\n'
				f.write(format %  (qname, iname))
				# Result values
				for i in range(len(Q)):
					f.write(xFormat % Q[i])
					f.write(yFormat % I[i])
					f.write('\n')
			else:
				# Result titles
				format = xFormat + yFormat + yFormat + '\n'
				f.write(format %  (qname, iname, signame))
				# Result values
				for i in range(len(Q)):
					f.write(xFormat % Q[i])
					f.write(yFormat % I[i])
					f.write(yFormat % Sig[i])
					f.write('\n')
		else:
			if Sig is None:
				# Result titles
				format = xFormat + yFormat + xFormat + '\n'
				f.write(format %  (qname, iname, twoThetaname))
				# Result values
				for i in range(len(Q)):
					f.write(xFormat % Q[i])
					f.write(yFormat % I[i])
					f.write(xFormat % twoTheta[i])
					f.write('\n')
			else:
				# Result titles
				format = xFormat + yFormat + yFormat + xFormat + '\n'
				f.write(format %  (qname, iname, signame, twoThetaname))
				# Result values
				for i in range(len(Q)):
					f.write(xFormat % Q[i])
					f.write(yFormat % I[i])
					f.write(yFormat % Sig[i])
					f.write(xFormat % twoTheta[i])
					f.write('\n')

#------------------------------------------------------------------------------
def write_polar_data(f, polarData, psi, twoTheta, concat_string):

	title = "Psi (degrees) / 2 Theta(degrees)"
	psiFormat = '%-35s'
	valueFormat = '%-25s'

	if psi is not None:
		if twoTheta is not None:
			if polarData is not None:
				f.write(psiFormat % title)
				for i in range(len(twoTheta)):
					f.write(valueFormat % twoTheta[i])
				f.write('\n')
				for i in range(len(psi)):
					f.write(psiFormat % psi[i])
					for j in range(len(twoTheta)):
						f.write(valueFormat % polarData[i][j])
					f.write('\n')

#------------------------------------------------------------------------------
def get_matching_op_name_from_param_node_sub(macro, nameStart, index):
	paramIndex = 0
	op_name = ''
	if check_dataset(macro, nameStart + 'count'):
		count = macro._f_getChild(nameStart + 'count').read()[0]
		for i in range(count):
			param_node = macro._f_getChild(nameStart + str(i))
			if 'name' in param_node._v_attrs:
				nodeName = param_node.attrs["name"]
				if is_effective(nodeName):
					paramIndex = paramIndex + 1
					if paramIndex == index:
						op_name = get_input_op_name_from_param_node_sub(param_node)
						break
	return op_name

#------------------------------------------------------------------------------
def get_input_op_name_from_param_node_sub(param_node):
	"""
		Returns a tuple containing the acquisition name and the input parameter name
		for a subtract macro argument
	"""

	target_items = param_node._v_attrs.target.split('/')
	acqui = target_items[1]
	image = target_items[2]

	if acqui == 'userMacros':
		# rebuild the original macro name
		name_attr = param_node._v_attrs.name
		# search string between '(' and ')'
		s = re.compile('\\(.+\\)').search(name_attr)
		acqui = name_attr[s.end():] + '_' + name_attr[s.start()+1:s.end()-1]
		image = image[image.rfind('_')+1:]

	for key in g_macro_names_translation_2:
		acqui = acqui.replace(key, g_macro_names_translation_2[key])
		image = image.replace(key, g_macro_names_translation_2[key])

	return acqui + '_' + image

#------------------------------------------------------------------------------
def adapt_name(name):
	"""
		Transforms a nexus written name into user readable one
	"""
	name = name.replace('_#','').replace('#_','#').replace('#-','(').replace('-#',')').replace('___',',').replace('--__--',' ')
	return name

#------------------------------------------------------------------------------
def adapt_name2(name):
	"""
		Transforms a nexus written name into user readable one
	"""
	name = name.replace('_#','}').replace('#_','{').replace('#-','(').replace('-#',')').replace('___',',').replace('--__--',' ')
	return name

#------------------------------------------------------------------------------
def adapt_name_in_macro(name):
	"""
		Transforms a name written in a macro node into a nexus name
	"""
	name = name.replace('}','_#').replace('{','#_').replace('(','#-').replace(')','-#')
	return name

#------------------------------------------------------------------------------
def adapt_acquisition_name(acqui_name):
	"""
		Adapts acquisition name to file name
	"""
	if acqui_name.find('/') == 0:
		acqui_name = acqui_name[1:]
	if acqui_name.find('/') > -1:
		acqui_name = acqui_name[:acqui_name.rfind('/')]
		if acqui_name.find('/') > -1:
			acqui_name = '_'.join(acqui_name.split('/'))
	if acqui_name.find('_img'):
		acqui_name = acqui_name.replace('_img', '')
	return adapt_name2(acqui_name)

#------------------------------------------------------------------------------
def is_effective(name):
	if name.endswith('/'):
		name = name[:name.rfind('/')]
	if name.find('/') > -1:
		tmp = name.split('/')
		name = tmp[len(tmp) - 1]
	return 'Intensity' in name or 'projection' in name.lower()

#------------------------------------------------------------------------------
def process_macro_file(macro, dest_path, file_name, version, full_name, index, I, Sigma, Q, twoTheta, psi):
	"""
		Writes macro results and parameters in a file
	"""
	if (I is not None) and (file_name is not None):
		# opening output file
		f = open(dest_path + file_name + g_file_ext, 'w')
		print "Writing " + file_name + g_file_ext
		f.write(g_header_separator)
		f.write('# %-50s%s\n' % ("_diffrn_sofware", version))
		f.write('# %s\n' % adapt_name2(full_name))
		f.write('# %s\n' % g_macro_names_translation[macro._v_name[:3]])
		# write scalar parameters if any
		count = 0
		if check_dataset(macro, 'parameter_count'):
			count = macro.parameter_count.read()[0]
		for i in range(index, count):
			param_name = 'parameter_' + str(i)
			param_short_name = param_name + '_displayShortName'
			if check_dataset(macro, param_name) and check_dataset(macro, param_short_name):
				param_item = macro._f_getChild(param_name)
				readName = ''.join(macro._f_getChild(param_short_name).read())
				f.write('# %-50s%s\n' % (readName, str(param_item.read()[0])))
		f.write(g_header_separator)
		write_output_results(f, I, Sigma, Q, twoTheta, psi, file_name)

#------------------------------------------------------------------------------
def process_two_lists_user_macro(macro, dest_path, nexus_file_name, version):
	"""
		The subtract macro consists of subtracting one image results
		(wich may represents a dark signal) from one (or more) other images results

		parameters_0_x refer to results to be corrected
		parameters_1_y refer to results to be subtracted

		The result triplet of this macro is:
			parameters_0_<3i>   - parameter_1_0
			parameters_0_<3i+1> - parameter_1_1
			parameters_0_<3i+2> - parameter_1_2
		with i in range [0, number of images to be corrected[
	"""
	print "Processing user macro '%s'" % macro._v_name

	# Gets second argument name from 'parameter_1_0'
	op_name_2 = get_input_op_name_from_param_node_sub(macro.parameter_1_0)

	op_name = None
	full_name = None
	file_name = None
	I = None
	Sigma = None
	Q = None
	twoTheta = None
	psi = None
	i = 0

	# one output file for each result triplet or quadruplet
	for result_index in range(macro.result_0_count.read()[0]):
		if check_dataset(macro, 'result_0_' + str(result_index)):
			node = macro._f_getChild('result_0_' + str(result_index))
			nodeName = node.attrs["name"]
			index = nodeName.index('(')
			if index > -1:
				nodeName = nodeName[:index]
			if is_effective(nodeName):
				# a new intensity value is found --> we have all necessary values to write previous file
				process_macro_file(macro, dest_path, file_name, version, full_name, 2, I, Sigma, Q, twoTheta, psi)
				I = node.read()
				i = i + 1
				op_name = get_matching_op_name_from_param_node_sub(macro, 'parameter_0_', i)
				full_name = macro._v_name[:3] + '_' + op_name + '-' + op_name_2
# 				if op_name.find('img'):
# 					op_name = op_name.replace('_rad', '')
# 					op_name = op_name.replace('img', 'rad')
				if op_name.find('_img'):
					op_name = op_name.replace('_img', '')
				file_name = macro._v_name[:3] + macro._v_name[macro._v_name.rfind('_'):] + '_' + adapt_name2(op_name)
				Sigma = None
				Q = None
				twoTheta = None
			elif nodeName.endswith('twoTheta'):
				twoTheta = node.read()
			elif nodeName.endswith('Sigma'):
				Sigma = node.read()
			elif nodeName.endswith('psi'):
				psi = node.read()
			elif nodeName.endswith('Q'):
				Q = node.read()

	process_macro_file(macro, dest_path, file_name, version, full_name, 2, I, Sigma, Q, twoTheta, psi)

#------------------------------------------------------------------------------
def process_single_list_user_macro(macro, dest_path, nexus_file_name, version):

	# Calculates file name
	macro_name = macro._v_name

	print "Processing user macro '%s'" % macro_name

	# Get acquisition name from parameter_0_0
# 	acqui_name = macro.parameter_0_0._v_attrs.target.split('/')[1]
	acqui_name = adapt_acquisition_name(macro.parameter_0_0._v_attrs.target)

	# file name = <acquisisition name> + <operation number> + <First 3 chars of operation name>
	macroShortName = macro_name[:3]
	if (macro._v_name.find("Join") == 0):
		macroShortName = macro_name[:4]
		if (macro._v_name.find("StatisticalError") > -1):
			macroShortName = macroShortName + 'S'
		elif (macro._v_name.find("VarianceError") > -1):
			macroShortName = macroShortName + 'V'
# 	file_name = macroShortName + '_' + acqui_name + macro_name[macro_name.rfind('_'):]
	file_name = macroShortName + macro._v_name[macro._v_name.rfind('_'):] + '_' + acqui_name

	# opening output file
	f = open(dest_path + file_name + g_file_ext, 'w')
	print "Writing " + file_name + g_file_ext
	f.write(g_header_separator)
	f.write('# %-50s%s\n' % ("_diffrn_sofware", version))
	f.write('# %s\n' % g_macro_names_translation[macroShortName])

	# Write source images names
	# get total number of input parameters
	param_count = macro.parameter_0_count[0] / 3
# 	f.write('# %d input parameters\n' % param_count)
	f.write('# Input parameters:\n')

	# writes input image names
	for i in range(param_count):
		param_name = 'parameter_0_' + str(i * 3)
		param_item = macro._f_getChild(param_name)
# 		item_path = param_item._v_attrs.path.split('/')[2]
		item_path = param_item._v_attrs.path
		if is_effective(item_path):
			item_path = item_path.split('/')[2]
			f.write('# %s\n' % adapt_name2(item_path))
		elif 'name' in param_item._v_attrs:
			item_path = param_item._v_attrs.name
			if is_effective(item_path):
				for res_name in g_result_names:
					item_path = item_path.replace(res_name, '')
				f.write('# %s\n' % adapt_name2(item_path))

	# write parameter_0 name attribute splitting each line
	for l in macro.parameter_0._v_attrs.name.split('\n'):
		if is_effective(l):
			f.write('# %s\n' % l)
	f.write('#\n')

	# write scalar parameters if any
	count = 0
	if check_dataset(macro, 'parameter_count'):
		count = macro.parameter_count.read()[0]
	for i in range(1, count):
		param_name = 'parameter_' + str(i)
		param_short_name = param_name + '_displayShortName'
		if check_dataset(macro, param_name) and check_dataset(macro, param_short_name):
			param_item = macro._f_getChild(param_name)
			readName = ''.join(macro._f_getChild(param_short_name).read())
			f.write('# %-50s%s\n' % (readName, str(param_item.read()[0])))
	f.write(g_header_separator)

	# Result data
	result_count = macro.result_0_count.read()[0]
	I = macro.result_0_0.read()
	Sigma = None
	Q = None
	twoTheta = None
	psi = None

	for resIndex in range(result_count):
		currentResult = macro._f_getChild("result_0_" + str(resIndex))
		nodeName = currentResult.attrs["name"]
		index = nodeName.index('(')
		if index > -1:
			nodeName = nodeName[:index]
		if nodeName.endswith('Q'):
			Q = currentResult.read()
		elif nodeName.endswith('psi'):
			psi = currentResult.read()
		elif nodeName.endswith('Sigma'):
			Sigma = currentResult.read()
		elif nodeName.endswith('twoTheta'):
			twoTheta = currentResult.read()

	# Write results data
	write_output_results(f, I, Sigma, Q, twoTheta, psi, file_name)

#------------------------------------------------------------------------------
def process_single_user_macro(macro, dest_path, nexus_file_name, version):

	# macro with 1 spectrum list input
	if macro._v_name.find("Sum") == 0 or macro._v_name.find("Average") == 0 or macro._v_name.find("Join") == 0 or macro._v_name.find("LinearFunction") == 0:
		process_single_list_user_macro(macro, dest_path, nexus_file_name, version)

	# macro with 2 spectrum lists input
	elif macro._v_name.find("Subtract") == 0 or macro._v_name.find("Scaling") == 0:
		process_two_lists_user_macro(macro, dest_path, nexus_file_name, version)

#------------------------------------------------------------------------------
def process_user_macros(macros_group, dest_path, nexus_file_name, version):

	print "Processing " + macros_group._v_name

	# iterate other macros
	for macro in macros_group._f_iterNodes(classname='Group'):
		process_single_user_macro(macro, dest_path, nexus_file_name, version)

#------------------------------------------------------------------------------
def check_dataset(op_group, dataset_name):
	try:
		op_group._f_getChild(dataset_name)
		return True
	except:
		return False

#------------------------------------------------------------------------------
def process_single_operation(acq, op, dest_path, nexus_file_name, version):

	print "Processing operation " + op._v_name

	# look for operation names containing the string '_rad_', '_circles_', '_tiltedCircles_' or 'Polar2ThetaPsi'
	polar2ThetaPsi = False
	if op._v_name.find('_rad_') > 0:
		sub_string = 'rad'
	elif op._v_name.find('_circles_') > 0:
		sub_string = 'circles'
	elif op._v_name.find('_tiltedCircles_') > 0:
		sub_string = 'tiltedCircles'
	elif op._v_name.find('_azimAt') > 0:
		sub_string = op._v_name[op._v_name.find('_azimAt')+1:op._v_name.rfind('_')]
	elif op._v_name.find('_meanProjection') > 0:
		sub_string = op._v_name[op._v_name.find('_meanProjection')+1:op._v_name.rfind('_')]
	elif op._v_name.find('_projection') > 0:
		sub_string = op._v_name[op._v_name.find('_projection')+1:op._v_name.rfind('_')]
	elif op._v_name.find('Polar2ThetaPsi') > -1:
		sub_string = "Polar2ThetaPsi"
		polar2ThetaPsi = True
	else:
		sub_string = ''

	detector = "aviex"
	if check_dataset(acq, 'detector'):
		detector = ''.join(acq.detector.read())
	if detector == "null":
		detector = "not specified"

	beamline = "SWING"
	if check_dataset(acq, 'origin'):
		beamline = ''.join(acq.origin.read())

	comment = ""
	if check_dataset(acq, 'comment'):
		comment = ''.join(acq.comment.read())

	if sub_string != '':
		# compute output file name
		if polar2ThetaPsi:
			file_name = acq._v_name + '_' + op._v_name.replace('#img', '')
			file_name = '_'.join(file_name.split('_')[:-1])
		else:
			file_name = adapt_acquisition_name(acq._v_name + '_' + op._v_name)
# 			file_name = acq._v_name + '_' + op._v_name[:re.compile(sub_string).search(op._v_name).end()]
# 			file_name = file_name.replace('img', sub_string)
# 			file_name = file_name[:re.compile('_' + sub_string+ '$').search(file_name).start()].replace('#_', '{').replace('_#', '}')

		# opening output file
		f = open(dest_path + file_name + g_file_ext, 'w')
		print "Writing " + file_name + g_file_ext

		f.write(g_header_separator)
		f.write('# NeXus source file: %s\n' % nexus_file_name)
		f.write('# NXdata: name = %20s\n#\n#\n' % op._v_name)

		if check_dataset(op, 'twoThetaValue') and check_dataset(op, 'twoThetaDelta'):
			f.write('# %-50s%s +- %s\n' % ("2Theta (degrees)", op.twoThetaValue.read()[0], op.twoThetaDelta.read()[0]))
		if check_dataset(op, 'qValue') and check_dataset(op, 'qDelta'):
			f.write('# %-50s%s +- %s\n' % ("Q (A-1)", op.qValue.read()[0], op.qDelta.read()[0]))

		if check_dataset(op, 'exposureTime'):
			f.write('# %-50s%s + %s\n' % ("Exposure_msec", op.exposureTime.read()[0], op.shutterCloseDelay.read()[0]))
		f.write('# %-50s%s\n'      % ("_diffrn_source.source", "Storage Ring Soleil, beamline " + beamline))
		f.write('# %-50s%s\n'      % ("_diffrn_sofware", version))
		f.write('# %-50s%s\n'      % ("_diffrn_detector.detector", detector))
		f.write('# %-50s%s\n'      % ("_diffrn_comment.comment", comment))
		if check_dataset(op, 'image'):
			f.write('# %-50s%s\n'      % ("_sas_detc.pixnum_ax", op.image._v_attrs.dimX))
			f.write('# %-50s%s\n'      % ("_sas_detc.pixnum_eq", op.image._v_attrs.dimY))
		if check_dataset(op, 'pixelSize'):
			f.write('# %-50s%s\n'      % ("_sas_detc.pixsize", op.pixelSize.read()[0]))
		if check_dataset(op, 'bin'):
			f.write('# %-50s%s\n'      % ("_sas_detc.binning", op.bin.read()[0]))
		if check_dataset(op, 'x0'):
			f.write('# %-50s%s\n'      % ("_sas_detc.center_ax", op.x0.read()[0]))
		if check_dataset(op, 'z0'):
			f.write('# %-50s%s\n'      % ("_sas_detc.center_eq", op.z0.read()[0]))
		if check_dataset(op, 'distance'):
			f.write('# %-50s%s\n'      % ("_sas_detc.dist_spec/detc", op.distance.read()[0]))
		if check_dataset(acq, 'energy'):
			f.write('# %-50s%s\n'      % ("_sas_detc.energy", acq.energy.read()[0]))
		if check_dataset(op, 'gain'):
			f.write('# %-50s%s\n'      % ("_sas_detc.gain", op.gain.read()[0]))
		if check_dataset(op, 'detectorBasedUncertainty'):
			f.write('# %-50s%s\n'      % ("_sas_detc.detector_based_uncertainty", op.detectorBasedUncertainty.read()[0]))
		if check_dataset(op, 'delta'):
			f.write('# %-50s%s\n'      % ("_sas_detc.delta", op.delta.read()[0]))
		if check_dataset(op, 'deltaOffset'):
			f.write('# %-50s%s\n'      % ("_sas_detc.delta_offset", op.deltaOffset.read()[0]))
		if check_dataset(op, 'gammaOffset'):
			f.write('# %-50s%s\n'      % ("_sas_detc.gamma_offset", op.deltaOffset.read()[0]))
		if check_dataset(op, 'lambda'):
			f.write('# %-50s%s\n'      % ("_sas_detc.wave_length", op._f_getChild("lambda").read()[0]))
		if check_dataset(op, 'useBias'):
			UseBias = 'false'
			if op.useBias.read()[0] == 1:
				UseBias = 'true'
			f.write('# %-50s%s\n'      % ("_sas_detc.bias.sub", UseBias))
		if check_dataset(op, 'bias'):
			f.write('# %-50s%s\n'      % ("_sas_detc.bias", op.bias.read()[0]))
		f.write('# %-50s%s\n'      % ("_sas_detc.sector_width", 360.0))
		if check_dataset(op, 'mask'):
			f.write('# %-50s%s\n'      % ("_sas_detc.mask", op.mask._v_attrs.name))
		isNormalized = 'false'
		if check_dataset(op, 'normalize') and op.normalize.read()[0] == 1:
			isNormalized = 'true'
		if check_dataset(op, 'isNormalized') and  op.isNormalized.read()[0] == 1:
			isNormalized = 'true'	
		if not polar2ThetaPsi:
			f.write('# %-50s%s\n'      % ("Normalization", isNormalized))
		if check_dataset(op, 'normalizationCount'):
			count = op.normalizationCount.read()[0]
		else:
			count = 0
		globalCoeff = check_dataset(op, 'coefficient')
		if count > 0:
			f.write('# %-50s%s\n'      % ("Normalization Count", count))
			for i in range (count):
				f.write('# %-50s%s\n'      % ("Normalization Factor " + str(i), op._f_getChild("normalizationFactor" + str(i)).read()[0]))
				f.write('# %-50s%s\n'      % ("Normalization Monitor " + str(i), op._f_getChild("mi" + str(i)).read()[0]))
				if check_dataset(op, "miIntensity" + str(i)):
					f.write('# %-50s%s\n'      % ("Normalization Intensity " + str(i), op._f_getChild("miIntensity" + str(i)).read()[0]))
				if globalCoeff:
					f.write('# %-50s%s\n'      % ("GlobalNormalization " + str(i), op.coefficient.read()[i]))
		else:
			if check_dataset(op, 'normalizationFactor'):
				f.write('# %-50s%s\n'      % ("Normalization Factor", op.normalizationFactor.read()[0]))
			if check_dataset(op, 'mi'):
				f.write('# %-50s%s\n'      % ("Normalization Monitor", op.mi.read()[0]))
			if check_dataset(op, 'miIntensity'):
				f.write('# %-50s%s\n'      % ("Normalization Intensity", op.miIntensity.read()[0]))
			if globalCoeff:
				f.write('# %-50s%s\n'      % ("GlobalNormalization", op.coefficient.read()[0]))

		if check_dataset(op, 'roi'):
			# roi : may be on several lines
			roi = op.roi.read(0)[0]
			roi_list = roi.split('\n')
			f.write('# %-50s%s\n'      % ("Roi=", roi_list[0]))
			for i in range (1, len(roi_list)):
				f.write('# %-50s%s\n'      % ("", roi_list[i]))

		f.write(g_header_separator)

		if check_dataset(op, 'twoTheta'):
			twoTheta = op.twoTheta.read()
		else:
			twoTheta = None

		if check_dataset(op, 'psi'):
			psi = op.psi.read()
		else:
			psi = None

		if polar2ThetaPsi:
			polarData = op.polarData.read();
			write_polar_data(f, polarData, psi, twoTheta, adapt_name(file_name))
		else:
			# Result data
			I = None
			for node in op._f_iterNodes(classname='Leaf'):
				if 'name' in node._v_attrs:
					nodeName = node.attrs["name"]
					if is_effective(nodeName):
						I = node.read()
						break
			if check_dataset(op, 'Sigma'):
				Sigma = op.Sigma.read()
			else:
				Sigma = None
			if check_dataset(op, 'Q'):
				Q = op.Q.read()
			else:
				Q = None

			# Write results data
			write_output_results(f, I, Sigma, Q, twoTheta, psi, adapt_name(file_name))

#------------------------------------------------------------------------------
def process_operations(op_group, dest_path, nexus_file_name, version):

	print "Processing " + op_group._v_name

	# iterate other operations
	for op in op_group._f_iterNodes(classname='Group'):
		process_single_operation(op_group, op, dest_path, nexus_file_name, version)

#------------------------------------------------------------------------------
def process_file(nexus_file, dest_path, path_to_group=None):

	print "Processing file " + nexus_file

	# creating destination path if needed
	#nexus_file_name = os.path.splitext(nexus_file)[0]
	nexus_complete_file_name = os.path.split(nexus_file)[1]
	nexus_file_name = os.path.splitext(nexus_complete_file_name)[0]
	full_path = dest_path.rstrip('/\\') + '/' + nexus_file_name + '/'
	print "full path: " + full_path
	if not os.path.exists (full_path):
		os.makedirs (full_path)

	file_handle = openFile(nexus_file)
	
	rootNode = file_handle.getNode("/")

	if 'creator' in rootNode._v_attrs:
		version = rootNode._v_attrs.creator
	else:
		version = "FOXTROT"

	if path_to_group is None:
		# iterate other NXentry groups
		for grp in file_handle.iterNodes("/", classname='Group'):
			group_name = grp._v_name
			if group_name == 'userMacros':
				process_user_macros(grp, full_path, nexus_file_name, version)
			else:
				# operation group (first level macro)
				process_operations(grp, full_path, nexus_file_name, version)
	
	else:
		# Third parameter gives the operation to process
		acq_name = path_to_group[:path_to_group.rfind('/')].lstrip('/')
		try:
			op = file_handle.getNode('/' + path_to_group)
			acq = file_handle.getNode('/' + acq_name)
			if acq_name == 'userMacros':
				process_single_user_macro(op, full_path, nexus_file_name, version)
			else:
				# operation group (first level macro)
				process_single_operation(acq, op, full_path, nexus_file_name, version)
			
		except NoSuchNodeError:
			print "Node %s not found" % acq_name

	file_handle.close()

#------------------------------------------------------------------------------
# Entry point
#------------------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 3:
		print "Input file name and destination directory are required."

	elif not isHDF5File(sys.argv[1]):
		print "Bad input file."

	else:
		if len(sys.argv) == 3:
			process_file(sys.argv[1], sys.argv[2])
		else:
			process_file(sys.argv[1], sys.argv[2], sys.argv[3])
		

