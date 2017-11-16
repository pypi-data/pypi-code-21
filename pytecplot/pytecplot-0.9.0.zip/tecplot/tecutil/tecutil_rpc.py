# coding: utf-8
"""GENERATED FILE. DO NOT EDIT."""
from __future__ import division, absolute_import, print_function, unicode_literals
from builtins import *

from ctypes import *
from copy import copy
from enum import Enum

from .tecrpc.Status import *
from ..constant import *

class ValueType(Enum):
    Scalar = 0
    Array = 1
    Text = 2
    ArbParam = 3
    Address = 4


class TecUtilRPC(object):

 def AddOnAllowUnload(self,add_on_id,do_allow_unload):
  args=((ValueType.Address,c_uint64,getattr(add_on_id,'value',add_on_id)),
        (ValueType.Scalar,c_bool,do_allow_unload),)
  rep=self.sndrcv("AddOnAllowUnload",*args).Reply()
  self.chk(rep)
 def AddOnGetPath(self,add_on_id):
  args=((ValueType.Address,c_uint64,getattr(add_on_id,'value',add_on_id)),)
  rep=self.sndrcv("AddOnGetPath",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def AddOnGetRegisteredInfo(self,official_name):
  args=((ValueType.Text,None,official_name),)
  rep=self.sndrcv("AddOnGetRegisteredInfo",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)),
   self.read_text(rep.Args(1)))
 def AddOnLoad(self,lib_name,not_used,not_used2):
  args=((ValueType.Text,None,lib_name),
        (ValueType.Text,None,not_used),
        (ValueType.Scalar,c_int32,not_used2),)
  rep=self.sndrcv("AddOnLoad",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AddOnRegForeignLibLoader(self,foreign_lib_id,foreign_lib_loader,client_data):
  args=((ValueType.Text,None,foreign_lib_id),
        (ValueType.Address,c_uint64,getattr(foreign_lib_loader,'value',foreign_lib_loader)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("AddOnRegForeignLibLoader",*args).Reply()
  self.chk(rep)
 def AddOnRegister(self,tecplot_base_version_number,official_name,version,author):
  args=((ValueType.Scalar,c_int32,tecplot_base_version_number),
        (ValueType.Text,None,official_name),
        (ValueType.Text,None,version),
        (ValueType.Text,None,author),)
  rep=self.sndrcv("AddOnRegister",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AddPreWriteLayoutCallback(self,write_layout_pre_write_callback,client_data):
  args=((ValueType.Address,c_uint64,getattr(write_layout_pre_write_callback,'value',write_layout_pre_write_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("AddPreWriteLayoutCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateContourLevels(self,start_level,end_level,level_skip,create_movie_file,movie_f_name):
  args=((ValueType.Scalar,c_int32,start_level),
        (ValueType.Scalar,c_int32,end_level),
        (ValueType.Scalar,c_int32,level_skip),
        (ValueType.Scalar,c_bool,create_movie_file),
        (ValueType.Text,None,movie_f_name),)
  rep=self.sndrcv("AnimateContourLevels",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateContourLevelsX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateContourLevelsX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateIJKBlanking(self,start_i_min_fract,start_j_min_fract,start_k_min_fract,start_i_max_fract,start_j_max_fract,start_k_max_fract,end_i_min_fract,end_j_min_fract,end_k_min_fract,end_i_max_fract,end_j_max_fract,end_k_max_fract,num_steps,create_movie_file,movie_f_name):
  args=((ValueType.Scalar,c_double,start_i_min_fract),
        (ValueType.Scalar,c_double,start_j_min_fract),
        (ValueType.Scalar,c_double,start_k_min_fract),
        (ValueType.Scalar,c_double,start_i_max_fract),
        (ValueType.Scalar,c_double,start_j_max_fract),
        (ValueType.Scalar,c_double,start_k_max_fract),
        (ValueType.Scalar,c_double,end_i_min_fract),
        (ValueType.Scalar,c_double,end_j_min_fract),
        (ValueType.Scalar,c_double,end_k_min_fract),
        (ValueType.Scalar,c_double,end_i_max_fract),
        (ValueType.Scalar,c_double,end_j_max_fract),
        (ValueType.Scalar,c_double,end_k_max_fract),
        (ValueType.Scalar,c_int32,num_steps),
        (ValueType.Scalar,c_bool,create_movie_file),
        (ValueType.Text,None,movie_f_name),)
  rep=self.sndrcv("AnimateIJKBlanking",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateIJKBlankingX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateIJKBlankingX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateIJKPlanes(self,ij_or_k,start_index,end_index,index_skip,create_movie_file,movie_f_name):
  args=((ValueType.Text,None,ij_or_k),
        (ValueType.Scalar,c_int64,start_index),
        (ValueType.Scalar,c_int64,end_index),
        (ValueType.Scalar,c_int64,index_skip),
        (ValueType.Scalar,c_bool,create_movie_file),
        (ValueType.Text,None,movie_f_name),)
  rep=self.sndrcv("AnimateIJKPlanes",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateIJKPlanesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateIJKPlanesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateIsoSurfacesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateIsoSurfacesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateLineMapsX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateLineMapsX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateSlices(self,start_slice,end_slice,num_slices,create_movie_file,movie_f_name):
  args=((ValueType.Scalar,c_int32,start_slice),
        (ValueType.Scalar,c_int32,end_slice),
        (ValueType.Scalar,c_int32,num_slices),
        (ValueType.Scalar,c_bool,create_movie_file),
        (ValueType.Text,None,movie_f_name),)
  rep=self.sndrcv("AnimateSlices",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateSlicesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateSlicesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateStream(self,num_steps_per_cycle,num_cycles,create_movie_file,movie_f_name):
  args=((ValueType.Scalar,c_int32,num_steps_per_cycle),
        (ValueType.Scalar,c_int32,num_cycles),
        (ValueType.Scalar,c_bool,create_movie_file),
        (ValueType.Text,None,movie_f_name),)
  rep=self.sndrcv("AnimateStream",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateStreamX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateStreamX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateTimeX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateTimeX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateZones(self,start_zone,end_zone,zone_skip,create_movie_file,movie_f_name):
  args=((ValueType.Scalar,c_int32,start_zone),
        (ValueType.Scalar,c_int32,end_zone),
        (ValueType.Scalar,c_int32,zone_skip),
        (ValueType.Scalar,c_bool,create_movie_file),
        (ValueType.Text,None,movie_f_name),)
  rep=self.sndrcv("AnimateZones",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AnimateZonesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("AnimateZonesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAlloc(self):
  rep=self.sndrcv("ArgListAlloc").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ArgListAppendArbParam(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.ArbParam,None,value),)
  rep=self.sndrcv("ArgListAppendArbParam",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendArbParamPtr(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.ArbParam,None,value.contents),)
  rep=self.sndrcv("ArgListAppendArbParamPtr",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendArray(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Array,c_uint8,value),)
  rep=self.sndrcv("ArgListAppendArray",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendDouble(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Scalar,c_double,value),)
  rep=self.sndrcv("ArgListAppendDouble",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendDoublePtr(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Scalar,c_double,value.contents.value),)
  rep=self.sndrcv("ArgListAppendDoublePtr",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendFunction(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Address,c_uint64,value.contents.value),)
  rep=self.sndrcv("ArgListAppendFunction",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendInt(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Scalar,c_int64,value),)
  rep=self.sndrcv("ArgListAppendInt",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendSet(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Address,c_uint64,getattr(value,'value',value)),)
  rep=self.sndrcv("ArgListAppendSet",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendString(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Text,None,value),)
  rep=self.sndrcv("ArgListAppendString",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendStringList(self,arg_list,name,string_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),)
  rep=self.sndrcv("ArgListAppendStringList",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListAppendStringPtr(self,arg_list,name,value):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),
        (ValueType.Address,c_uint64,value.contents.value),)
  rep=self.sndrcv("ArgListAppendStringPtr",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ArgListClear(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ArgListClear",*args).Reply()
  self.chk(rep)
 def ArgListDealloc(self,arg_list):
  args=((ValueType.Address,c_uint64,arg_list.contents.value),)
  rep=self.sndrcv("ArgListDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ArgListGetArbParamByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetArbParamByIndex",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def ArgListGetArbParamPtrByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetArbParamPtrByIndex",*args).Reply()
  self.chk(rep)
  ret = arg_list._handles[index - 1]
  ret[0] = self.read_arbparam(rep.Args(0))
  return ret
 def ArgListGetArgCount(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ArgListGetArgCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ArgListGetArgNameByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetArgNameByIndex",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def ArgListGetArgTypeByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetArgTypeByIndex",*args).Reply()
  self.chk(rep)
  return ArgListArgType(rep.Args(0).Int32Value())
 def ArgListGetArrayByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetArrayByIndex",*args).Reply()
  self.chk(rep)
  return self.read_array(rep.Args(0), c_uint8)
 def ArgListGetDoubleByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetDoubleByIndex",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ArgListGetDoublePtrByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetDoublePtrByIndex",*args).Reply()
  self.chk(rep)
  ret = arg_list._handles[index - 1]
  ret[0] = rep.Args(0).Float64Value()
  return ret
 def ArgListGetFunctionByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetFunctionByIndex",*args).Reply()
  self.chk(rep)
  return self.read_array(rep.Args(0), c_uint8)
 def ArgListGetIndexByArgName(self,arg_list,name):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Text,None,name),)
  rep=self.sndrcv("ArgListGetIndexByArgName",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def ArgListGetIntByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetIntByIndex",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ArgListGetSetByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetSetByIndex",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ArgListGetStringByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetStringByIndex",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def ArgListGetStringListByIndex(self,arg_list,index):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ArgListGetStringListByIndex",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ArrayAlloc(self,size,debug_info):
  args=((ValueType.Scalar,c_int64,size),
        (ValueType.Text,None,debug_info),)
  rep=self.sndrcv("ArrayAlloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ArrayDealloc(self,array):
  args=((ValueType.Address,c_uint64,array.contents.value),)
  rep=self.sndrcv("ArrayDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AutoRedrawIsActive(self):
  rep=self.sndrcv("AutoRedrawIsActive").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def AuxDataBeginAssign(self):
  rep=self.sndrcv("AuxDataBeginAssign").Reply()
  self.chk(rep)
 def AuxDataDataSetGetRef(self):
  rep=self.sndrcv("AuxDataDataSetGetRef").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AuxDataDealloc(self,aux_data):
  args=((ValueType.Address,c_uint64,aux_data.contents.value),)
  rep=self.sndrcv("AuxDataDealloc",*args).Reply()
  self.chk(rep)
 def AuxDataDeleteItemByIndex(self,aux_data_ref,index):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("AuxDataDeleteItemByIndex",*args).Reply()
  self.chk(rep)
 def AuxDataDeleteItemByName(self,aux_data_ref,name):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Text,None,name),)
  rep=self.sndrcv("AuxDataDeleteItemByName",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AuxDataEndAssign(self):
  rep=self.sndrcv("AuxDataEndAssign").Reply()
  self.chk(rep)
 def AuxDataFrameGetRef(self):
  rep=self.sndrcv("AuxDataFrameGetRef").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AuxDataGetItemByIndex(self,aux_data_ref,index):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("AuxDataGetItemByIndex",*args).Reply()
  self.chk(rep)
  return (
   self.read_text(rep.Args(0)),
   self.read_arbparam(rep.Args(1)),
   AuxDataType(rep.Args(2).Int32Value()),
   rep.Args(3).Boolean())
 def AuxDataGetItemByName(self,aux_data_ref,name):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Text,None,name),)
  rep=self.sndrcv("AuxDataGetItemByName",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_arbparam(rep.Args(0)),
   AuxDataType(rep.Args(1).Int32Value()),
   rep.Args(2).Boolean())
 def AuxDataGetItemIndex(self,aux_data_ref,name):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Text,None,name),)
  rep=self.sndrcv("AuxDataGetItemIndex",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def AuxDataGetNumItems(self,aux_data_ref):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),)
  rep=self.sndrcv("AuxDataGetNumItems",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def AuxDataGetStrItemByIndex(self,aux_data_ref,index):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("AuxDataGetStrItemByIndex",*args).Reply()
  self.chk(rep)
  return (
   self.read_text(rep.Args(0)),
   self.read_text(rep.Args(1)),
   rep.Args(2).Boolean())
 def AuxDataGetStrItemByName(self,aux_data_ref,name):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Text,None,name),)
  rep=self.sndrcv("AuxDataGetStrItemByName",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)),
   rep.Args(1).Boolean())
 def AuxDataLayoutGetRef(self):
  rep=self.sndrcv("AuxDataLayoutGetRef").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AuxDataLineMapGetRef(self,map):
  args=((ValueType.Scalar,c_int32,map),)
  rep=self.sndrcv("AuxDataLineMapGetRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AuxDataPageGetRef(self):
  rep=self.sndrcv("AuxDataPageGetRef").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AuxDataSetItem(self,aux_data_ref,name,value,type,retain):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Text,None,name),
        (ValueType.ArbParam,None,value),
        (ValueType.Scalar,c_int32,AuxDataType(type).value),
        (ValueType.Scalar,c_bool,retain),)
  rep=self.sndrcv("AuxDataSetItem",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AuxDataSetStrItem(self,aux_data_ref,name,value,retain):
  args=((ValueType.Address,c_uint64,getattr(aux_data_ref,'value',aux_data_ref)),
        (ValueType.Text,None,name),
        (ValueType.Text,None,value),
        (ValueType.Scalar,c_bool,retain),)
  rep=self.sndrcv("AuxDataSetStrItem",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AuxDataVarGetRef(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("AuxDataVarGetRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AuxDataZoneGetRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("AuxDataZoneGetRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def AverageCellCenterData(self,zone_set,var_set):
  args=((ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Address,c_uint64,getattr(var_set,'value',var_set)),)
  rep=self.sndrcv("AverageCellCenterData",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def AxisGetGridRange(self):
  rep=self.sndrcv("AxisGetGridRange").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value(),
   rep.Args(3).Float64Value())
 def AxisGetNextRangeValue(self,axis,axis_num,current_value,is_increasing,auto_adjust_to_nice_values):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),
        (ValueType.Scalar,c_double,current_value),
        (ValueType.Scalar,c_bool,is_increasing),
        (ValueType.Scalar,c_bool,auto_adjust_to_nice_values),)
  rep=self.sndrcv("AxisGetNextRangeValue",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def AxisGetRange(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("AxisGetRange",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def AxisGetVarAssignments(self):
  rep=self.sndrcv("AxisGetVarAssignments").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int32Value(),
   rep.Args(1).Int32Value(),
   rep.Args(2).Int32Value())
 def AxisLabelGetNumberFormat(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("AxisLabelGetNumberFormat",*args).Reply()
  self.chk(rep)
  return NumberFormat(rep.Args(0).Int32Value())
 def AxisLabelGetPrecisionFormat(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("AxisLabelGetPrecisionFormat",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def AxisLabelGetTimeDateFormat(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("AxisLabelGetTimeDateFormat",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def BlankingCheckDataPoint(self,zone,point_index):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int64,point_index),)
  rep=self.sndrcv("BlankingCheckDataPoint",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def BlankingCheckFECell(self,zone,cell_index):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int64,cell_index),)
  rep=self.sndrcv("BlankingCheckFECell",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def BlankingCheckIJKCell(self,zone,zone_plane,cell_index):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,IJKPlanes(zone_plane).value),
        (ValueType.Scalar,c_int64,cell_index),)
  rep=self.sndrcv("BlankingCheckIJKCell",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def BlankingIsActive(self):
  rep=self.sndrcv("BlankingIsActive").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def CheckActiveAllocs(self):
  rep=self.sndrcv("CheckActiveAllocs").Reply()
  self.chk(rep)
 def ColorMapCopyStandard(self,color_map):
  args=((ValueType.Scalar,c_int32,ContourColorMap(color_map).value),)
  rep=self.sndrcv("ColorMapCopyStandard",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ColorMapCreateX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ColorMapCreateX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ColorMapDelete(self,source_color_map_name):
  args=((ValueType.Text,None,source_color_map_name),)
  rep=self.sndrcv("ColorMapDelete",*args).Reply()
  self.chk(rep)
 def ColorMapExists(self,color_map_name):
  args=((ValueType.Text,None,color_map_name),)
  rep=self.sndrcv("ColorMapExists",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ColorMapGetBasicColorRGB(self,basic_color):
  args=((ValueType.Scalar,c_int32,basic_color),)
  rep=self.sndrcv("ColorMapGetBasicColorRGB",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Uint8Value(),
   rep.Args(1).Uint8Value(),
   rep.Args(2).Uint8Value())
 def ColorMapGetContourRGB(self,color_map_number,contour_color_offset):
  args=((ValueType.Scalar,c_int32,color_map_number),
        (ValueType.Scalar,c_int32,contour_color_offset),)
  rep=self.sndrcv("ColorMapGetContourRGB",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Uint8Value(),
   rep.Args(1).Uint8Value(),
   rep.Args(2).Uint8Value())
 def ColorMapGetCount(self):
  rep=self.sndrcv("ColorMapGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ColorMapGetName(self,color_map_number):
  args=((ValueType.Scalar,c_int32,color_map_number),)
  rep=self.sndrcv("ColorMapGetName",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def ColorMapGetNumByName(self,color_map_name):
  args=((ValueType.Text,None,color_map_name),)
  rep=self.sndrcv("ColorMapGetNumByName",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ColorMapIsBuiltIn(self,color_map_name):
  args=((ValueType.Text,None,color_map_name),)
  rep=self.sndrcv("ColorMapIsBuiltIn",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ColorMapNumBasicColors(self):
  rep=self.sndrcv("ColorMapNumBasicColors").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ColorMapRedistributeControlPts(self,color_map_name):
  args=((ValueType.Text,None,color_map_name),)
  rep=self.sndrcv("ColorMapRedistributeControlPts",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ColorMapRefresh(self):
  rep=self.sndrcv("ColorMapRefresh").Reply()
  self.chk(rep)
 def ColorMapRename(self,source_color_map_name,new_color_map_name):
  args=((ValueType.Text,None,source_color_map_name),
        (ValueType.Text,None,new_color_map_name),)
  rep=self.sndrcv("ColorMapRename",*args).Reply()
  self.chk(rep)
 def ColorMapResetRawUserDefined(self,source_color_map_name):
  args=((ValueType.Text,None,source_color_map_name),)
  rep=self.sndrcv("ColorMapResetRawUserDefined",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ColorMapSetBase(self,base_color_map):
  args=((ValueType.Scalar,c_int32,ContourColorMap(base_color_map).value),)
  rep=self.sndrcv("ColorMapSetBase",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ConnectGetPrevSharedZone(self,zones_to_consider,zone):
  args=((ValueType.Address,c_uint64,getattr(zones_to_consider,'value',zones_to_consider)),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ConnectGetPrevSharedZone",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ConnectGetShareZoneSet(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ConnectGetShareZoneSet",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ContourGetLevels(self,contour_group):
  args=((ValueType.Scalar,c_int32,contour_group),)
  rep=self.sndrcv("ContourGetLevels",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64ArrayLength(),
   copy(rep.Args(0).Float64Array()))
 def ContourLabelX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ContourLabelX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ContourLevelX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ContourLevelX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ContourSetVariable(self,new_variable):
  args=((ValueType.Scalar,c_int32,new_variable),)
  rep=self.sndrcv("ContourSetVariable",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ContourSetVariableX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ContourSetVariableX",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ConvAddPostReadCallback(self,converter_id_string,converter_post_read_callback):
  args=((ValueType.Text,None,converter_id_string),
        (ValueType.Address,c_uint64,getattr(converter_post_read_callback,'value',converter_post_read_callback)),)
  rep=self.sndrcv("ConvAddPostReadCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Convert3DPositionToGrid(self,x_position,y_position,z_position):
  args=((ValueType.Scalar,c_double,x_position),
        (ValueType.Scalar,c_double,y_position),
        (ValueType.Scalar,c_double,z_position),)
  rep=self.sndrcv("Convert3DPositionToGrid",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def ConvertGridTo3DPosition(self,x_grid_position,y_grid_position,z_grid_position):
  args=((ValueType.Scalar,c_double,x_grid_position),
        (ValueType.Scalar,c_double,y_grid_position),
        (ValueType.Scalar,c_double,z_grid_position),)
  rep=self.sndrcv("ConvertGridTo3DPosition",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def ConvertUnits(self,old_units,new_units,old_size):
  args=((ValueType.Scalar,c_int32,Units(old_units).value),
        (ValueType.Scalar,c_int32,Units(new_units).value),
        (ValueType.Scalar,c_double,old_size),)
  rep=self.sndrcv("ConvertUnits",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ConvertXDimension(self,old_coord_sys,new_coord_sys,old_dimension):
  args=((ValueType.Scalar,c_int32,CoordSys(old_coord_sys).value),
        (ValueType.Scalar,c_int32,CoordSys(new_coord_sys).value),
        (ValueType.Scalar,c_double,old_dimension),)
  rep=self.sndrcv("ConvertXDimension",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ConvertXPosition(self,old_coord_sys,new_coord_sys,old_x):
  args=((ValueType.Scalar,c_int32,CoordSys(old_coord_sys).value),
        (ValueType.Scalar,c_int32,CoordSys(new_coord_sys).value),
        (ValueType.Scalar,c_double,old_x),)
  rep=self.sndrcv("ConvertXPosition",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ConvertYDimension(self,old_coord_sys,new_coord_sys,old_dimension):
  args=((ValueType.Scalar,c_int32,CoordSys(old_coord_sys).value),
        (ValueType.Scalar,c_int32,CoordSys(new_coord_sys).value),
        (ValueType.Scalar,c_double,old_dimension),)
  rep=self.sndrcv("ConvertYDimension",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ConvertYPosition(self,old_coord_sys,new_coord_sys,old_y):
  args=((ValueType.Scalar,c_int32,CoordSys(old_coord_sys).value),
        (ValueType.Scalar,c_int32,CoordSys(new_coord_sys).value),
        (ValueType.Scalar,c_double,old_y),)
  rep=self.sndrcv("ConvertYPosition",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def CreateCircularZone(self,i_max,j_max,k_max,x_origin,y_origin,radius,z_min,z_max,field_data_type):
  args=((ValueType.Scalar,c_int64,i_max),
        (ValueType.Scalar,c_int64,j_max),
        (ValueType.Scalar,c_int64,k_max),
        (ValueType.Scalar,c_double,x_origin),
        (ValueType.Scalar,c_double,y_origin),
        (ValueType.Scalar,c_double,radius),
        (ValueType.Scalar,c_double,z_min),
        (ValueType.Scalar,c_double,z_max),
        (ValueType.Scalar,c_int32,FieldDataType(field_data_type).value),)
  rep=self.sndrcv("CreateCircularZone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateContourLineZones(self):
  rep=self.sndrcv("CreateContourLineZones").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateContourLineZonesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("CreateContourLineZonesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateFEBoundary(self,source_zone,remove_blanked_surfaces):
  args=((ValueType.Scalar,c_int32,source_zone),
        (ValueType.Scalar,c_bool,remove_blanked_surfaces),)
  rep=self.sndrcv("CreateFEBoundary",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateMirrorZones(self,source_zones,mirror_var):
  args=((ValueType.Address,c_uint64,getattr(source_zones,'value',source_zones)),
        (ValueType.Text,None,mirror_var),)
  rep=self.sndrcv("CreateMirrorZones",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateRectangularZone(self,i_max,j_max,k_max,x_min,y_min,z_min,x_max,y_max,z_max,field_data_type):
  args=((ValueType.Scalar,c_int64,i_max),
        (ValueType.Scalar,c_int64,j_max),
        (ValueType.Scalar,c_int64,k_max),
        (ValueType.Scalar,c_double,x_min),
        (ValueType.Scalar,c_double,y_min),
        (ValueType.Scalar,c_double,z_min),
        (ValueType.Scalar,c_double,x_max),
        (ValueType.Scalar,c_double,y_max),
        (ValueType.Scalar,c_double,z_max),
        (ValueType.Scalar,c_int32,FieldDataType(field_data_type).value),)
  rep=self.sndrcv("CreateRectangularZone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateSimpleZone(self,num_points,v1_values,v2_values,field_data_type):
  args=((ValueType.Scalar,c_int64,num_points),
        (ValueType.Array,c_double,v1_values),
        (ValueType.Array,c_double,v2_values),
        (ValueType.Scalar,c_int32,FieldDataType(field_data_type).value),)
  rep=self.sndrcv("CreateSimpleZone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateSliceZoneFromPlane(self,slice_source,origin_x,origin_y,origin_z,normal_x,normal_y,normal_z):
  args=((ValueType.Scalar,c_int32,SliceSource(slice_source).value),
        (ValueType.Scalar,c_double,origin_x),
        (ValueType.Scalar,c_double,origin_y),
        (ValueType.Scalar,c_double,origin_z),
        (ValueType.Scalar,c_double,normal_x),
        (ValueType.Scalar,c_double,normal_y),
        (ValueType.Scalar,c_double,normal_z),)
  rep=self.sndrcv("CreateSliceZoneFromPlane",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateSliceZoneFromPlneX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("CreateSliceZoneFromPlneX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CreateSliceZoneShowTrace(self,do_show):
  args=((ValueType.Scalar,c_bool,do_show),)
  rep=self.sndrcv("CreateSliceZoneShowTrace",*args).Reply()
  self.chk(rep)
 def CreateSphericalZone(self,i_max,j_max,x_origin,y_origin,z_origin,radius,field_data_type):
  args=((ValueType.Scalar,c_int64,i_max),
        (ValueType.Scalar,c_int64,j_max),
        (ValueType.Scalar,c_double,x_origin),
        (ValueType.Scalar,c_double,y_origin),
        (ValueType.Scalar,c_double,z_origin),
        (ValueType.Scalar,c_double,radius),
        (ValueType.Scalar,c_int32,FieldDataType(field_data_type).value),)
  rep=self.sndrcv("CreateSphericalZone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CurveGetDisplayInfo(self,line_map):
  args=((ValueType.Scalar,c_int32,line_map),)
  rep=self.sndrcv("CurveGetDisplayInfo",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def CurveRegisterExtCrvFit(self,curve_fit_name,get_line_plot_data_points_callback,get_probe_value_callback,get_curve_info_string_callback,get_curve_settings_callback,get_abbreviated_settings_string_callback):
  args=((ValueType.Text,None,curve_fit_name),
        (ValueType.Address,c_uint64,getattr(get_line_plot_data_points_callback,'value',get_line_plot_data_points_callback)),
        (ValueType.Address,c_uint64,getattr(get_probe_value_callback,'value',get_probe_value_callback)),
        (ValueType.Address,c_uint64,getattr(get_curve_info_string_callback,'value',get_curve_info_string_callback)),
        (ValueType.Address,c_uint64,getattr(get_curve_settings_callback,'value',get_curve_settings_callback)),
        (ValueType.Address,c_uint64,getattr(get_abbreviated_settings_string_callback,'value',get_abbreviated_settings_string_callback)),)
  rep=self.sndrcv("CurveRegisterExtCrvFit",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CurveSetExtendedSettings(self,line_map_num,settings):
  args=((ValueType.Scalar,c_int32,line_map_num),
        (ValueType.Text,None,settings),)
  rep=self.sndrcv("CurveSetExtendedSettings",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def CurveWriteInfo(self,file_name,line_map,curve_info_mode):
  args=((ValueType.Text,None,file_name),
        (ValueType.Scalar,c_int32,line_map),
        (ValueType.Scalar,c_int32,CurveInfoMode(curve_info_mode).value),)
  rep=self.sndrcv("CurveWriteInfo",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CustomLabelsAppend(self,label_list):
  args=((ValueType.Address,c_uint64,getattr(label_list,'value',label_list)),)
  rep=self.sndrcv("CustomLabelsAppend",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def CustomLabelsGet(self,which_set):
  args=((ValueType.Scalar,c_int32,which_set),)
  rep=self.sndrcv("CustomLabelsGet",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def CustomLabelsGetNumSets(self):
  rep=self.sndrcv("CustomLabelsGetNumSets").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataAlter(self,equation,zone_set,i_min,i_max,i_skip,j_min,j_max,j_skip,k_min,k_max,k_skip,dest_data_type):
  args=((ValueType.Text,None,equation),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_int64,i_min),
        (ValueType.Scalar,c_int64,i_max),
        (ValueType.Scalar,c_int64,i_skip),
        (ValueType.Scalar,c_int64,j_min),
        (ValueType.Scalar,c_int64,j_max),
        (ValueType.Scalar,c_int64,j_skip),
        (ValueType.Scalar,c_int64,k_min),
        (ValueType.Scalar,c_int64,k_max),
        (ValueType.Scalar,c_int64,k_skip),
        (ValueType.Scalar,c_int32,FieldDataType(dest_data_type).value),)
  rep=self.sndrcv("DataAlter",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataAlterX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataAlterX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataAxialDuplicate(self,data_set_id,zones,spatial_vars,num_vectors,u_vars,v_vars,w_vars,is3_d_rotation,rotation_in_degrees,offset_angle_in_degrees,num_duplicates,origin,normal,add_zones_to_existing_strands):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Address,c_uint64,getattr(zones,'value',zones)),
        (ValueType.Array,c_int32,spatial_vars),
        (ValueType.Scalar,c_int32,num_vectors),
        (ValueType.Array,c_int32,u_vars),
        (ValueType.Array,c_int32,v_vars),
        (ValueType.Array,c_int32,w_vars),
        (ValueType.Scalar,c_bool,is3_d_rotation),
        (ValueType.Scalar,c_double,rotation_in_degrees),
        (ValueType.Scalar,c_double,offset_angle_in_degrees),
        (ValueType.Scalar,c_int32,num_duplicates),
        (ValueType.Array,c_double,origin),
        (ValueType.Array,c_double,normal),
        (ValueType.Scalar,c_bool,add_zones_to_existing_strands),)
  rep=self.sndrcv("DataAxialDuplicate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataConnectBranchShared(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataConnectBranchShared",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataConnectGetShareCount(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataConnectGetShareCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataConnectIsSZLData(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataConnectIsSZLData",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataConnectIsSharingOk(self,source_zone,dest_zone):
  args=((ValueType.Scalar,c_int32,source_zone),
        (ValueType.Scalar,c_int32,dest_zone),)
  rep=self.sndrcv("DataConnectIsSharingOk",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataConnectShare(self,source_zone,dest_zone):
  args=((ValueType.Scalar,c_int32,source_zone),
        (ValueType.Scalar,c_int32,dest_zone),)
  rep=self.sndrcv("DataConnectShare",*args).Reply()
  self.chk(rep)
 def DataElemGetFace(self,elem_to_face_map,elem,face_offset):
  args=((ValueType.Address,c_uint64,getattr(elem_to_face_map,'value',elem_to_face_map)),
        (ValueType.Scalar,c_int64,elem),
        (ValueType.Scalar,c_int32,face_offset),)
  rep=self.sndrcv("DataElemGetFace",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataElemGetNumFaces(self,elem_to_face_map,elem):
  args=((ValueType.Address,c_uint64,getattr(elem_to_face_map,'value',elem_to_face_map)),
        (ValueType.Scalar,c_int64,elem),)
  rep=self.sndrcv("DataElemGetNumFaces",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataElemGetReadableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataElemGetReadableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataFECellGetNodes(self,zone,face,cell_index):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,face),
        (ValueType.Scalar,c_int64,cell_index),)
  rep=self.sndrcv("DataFECellGetNodes",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value(),
   rep.Args(3).Int64Value())
 def DataFECellGetUniqueNodes(self,zone,face_offset,cell_index,unique_nodes_size,unique_nodes):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,face_offset),
        (ValueType.Scalar,c_int64,cell_index),
        (ValueType.Scalar,c_int32,unique_nodes_size),
        (ValueType.Array,c_int64,unique_nodes.contents),)
  rep=self.sndrcv("DataFECellGetUniqueNodes",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(1).Int64ArrayLength(),
   rep.Args(0).Int32Value(),
   copy(rep.Args(1).Int64Array()))
 def DataFaceMapAlloc(self,zone,num_faces,num_face_nodes,num_face_bndry_faces,num_face_bndry_conns):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int64,num_faces),
        (ValueType.Scalar,c_int64,num_face_nodes),
        (ValueType.Scalar,c_int64,num_face_bndry_faces),
        (ValueType.Scalar,c_int64,num_face_bndry_conns),)
  rep=self.sndrcv("DataFaceMapAlloc",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceMapAssignBConns(self,face_map,num_bndry_faces,num_bndry_conns__array,face_bndry_elems__array,face_bndry_elem_zones__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int32,num_bndry_faces),
        (ValueType.Array,c_int32,num_bndry_conns__array),
        (ValueType.Array,c_int32,face_bndry_elems__array),
        (ValueType.Array,c_int32,face_bndry_elem_zones__array),)
  rep=self.sndrcv("DataFaceMapAssignBConns",*args).Reply()
  self.chk(rep)
 def DataFaceMapAssignBConns64(self,face_map,num_bndry_faces,num_bndry_conns__array,face_bndry_elems__array,face_bndry_elem_zones__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int32,num_bndry_faces),
        (ValueType.Array,c_int32,num_bndry_conns__array),
        (ValueType.Array,c_int64,face_bndry_elems__array),
        (ValueType.Array,c_int32,face_bndry_elem_zones__array),)
  rep=self.sndrcv("DataFaceMapAssignBConns64",*args).Reply()
  self.chk(rep)
 def DataFaceMapAssignElemToNodeMap(self,face_map,num_elements,faces_per_elem__array,nodes_per_face__array,elem_to_node_map__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,num_elements),
        (ValueType.Array,c_int32,faces_per_elem__array),
        (ValueType.Array,c_int32,nodes_per_face__array),
        (ValueType.Array,c_int32,elem_to_node_map__array),)
  rep=self.sndrcv("DataFaceMapAssignElemToNodeMap",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceMapAssignElemToNodeMap64(self,face_map,num_elements,faces_per_elem__array,nodes_per_face__array,elem_to_node_map__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,num_elements),
        (ValueType.Array,c_int32,faces_per_elem__array),
        (ValueType.Array,c_int32,nodes_per_face__array),
        (ValueType.Array,c_int64,elem_to_node_map__array),)
  rep=self.sndrcv("DataFaceMapAssignElemToNodeMap64",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceMapAssignElems(self,face_map,num_faces,face_left_elems__array,face_right_elems__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,num_faces),
        (ValueType.Array,c_int32,face_left_elems__array),
        (ValueType.Array,c_int32,face_right_elems__array),)
  rep=self.sndrcv("DataFaceMapAssignElems",*args).Reply()
  self.chk(rep)
 def DataFaceMapAssignElems64(self,face_map,num_faces,face_left_elems__array,face_right_elems__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,num_faces),
        (ValueType.Array,c_int64,face_left_elems__array),
        (ValueType.Array,c_int64,face_right_elems__array),)
  rep=self.sndrcv("DataFaceMapAssignElems64",*args).Reply()
  self.chk(rep)
 def DataFaceMapAssignNodes(self,face_map,num_faces,num_face_nodes__array,face_nodes__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,num_faces),
        (ValueType.Array,c_int32,num_face_nodes__array),
        (ValueType.Array,c_int32,face_nodes__array),)
  rep=self.sndrcv("DataFaceMapAssignNodes",*args).Reply()
  self.chk(rep)
 def DataFaceMapAssignNodes64(self,face_map,num_faces,num_face_nodes__array,face_nodes__array):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,num_faces),
        (ValueType.Array,c_int32,num_face_nodes__array),
        (ValueType.Array,c_int64,face_nodes__array),)
  rep=self.sndrcv("DataFaceMapAssignNodes64",*args).Reply()
  self.chk(rep)
 def DataFaceMapBeginAssign(self,face_map):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),)
  rep=self.sndrcv("DataFaceMapBeginAssign",*args).Reply()
  self.chk(rep)
 def DataFaceMapCustomLOD(self,zone,num_faces,num_face_nodes,num_face_bndry_faces,num_face_bndry_conns,load_callback,unload_callback,cleanup_callback,client_data):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int64,num_faces),
        (ValueType.Scalar,c_int64,num_face_nodes),
        (ValueType.Scalar,c_int64,num_face_bndry_faces),
        (ValueType.Scalar,c_int64,num_face_bndry_conns),
        (ValueType.Address,c_uint64,getattr(load_callback,'value',load_callback)),
        (ValueType.Address,c_uint64,getattr(unload_callback,'value',unload_callback)),
        (ValueType.Address,c_uint64,getattr(cleanup_callback,'value',cleanup_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("DataFaceMapCustomLOD",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceMapEndAssign(self,face_map):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),)
  rep=self.sndrcv("DataFaceMapEndAssign",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceMapGetBndryConn(self,face_map,face,bndry_conn_offset):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,face),
        (ValueType.Scalar,c_int32,bndry_conn_offset),)
  rep=self.sndrcv("DataFaceMapGetBndryConn",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int32Value())
 def DataFaceMapGetClientData(self,face_map):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),)
  rep=self.sndrcv("DataFaceMapGetClientData",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def DataFaceMapGetElementRawItemType(self,face_map):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),)
  rep=self.sndrcv("DataFaceMapGetElementRawItemType",*args).Reply()
  self.chk(rep)
  return OffsetDataType(rep.Args(0).Int32Value())
 def DataFaceMapGetFaceNode(self,face_map,face,node_offset):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,face),
        (ValueType.Scalar,c_int32,node_offset),)
  rep=self.sndrcv("DataFaceMapGetFaceNode",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataFaceMapGetLeftElem(self,face_map,face):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,face),)
  rep=self.sndrcv("DataFaceMapGetLeftElem",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataFaceMapGetNBndryConns(self,face_map,face):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,face),)
  rep=self.sndrcv("DataFaceMapGetNBndryConns",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataFaceMapGetNFaceNodes(self,face_map,face):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,face),)
  rep=self.sndrcv("DataFaceMapGetNFaceNodes",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataFaceMapGetNFaces(self,face_map):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),)
  rep=self.sndrcv("DataFaceMapGetNFaces",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataFaceMapGetNodeRawItemType(self,face_map):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),)
  rep=self.sndrcv("DataFaceMapGetNodeRawItemType",*args).Reply()
  self.chk(rep)
  return OffsetDataType(rep.Args(0).Int32Value())
 def DataFaceMapGetNumNodes(self,face_map):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),)
  rep=self.sndrcv("DataFaceMapGetNumNodes",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataFaceMapGetReadableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataFaceMapGetReadableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataFaceMapGetRightElem(self,face_map,face):
  args=((ValueType.Address,c_uint64,getattr(face_map,'value',face_map)),
        (ValueType.Scalar,c_int64,face),)
  rep=self.sndrcv("DataFaceMapGetRightElem",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataFaceMapGetWritableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataFaceMapGetWritableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataFaceNbrAssignArrayByRef(self,face_neighbor,dest_offset,num_neighbors,neighbor_elems):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),
        (ValueType.Scalar,c_int64,dest_offset),
        (ValueType.Scalar,c_int32,num_neighbors),
        (ValueType.Array,c_int32,neighbor_elems),)
  rep=self.sndrcv("DataFaceNbrAssignArrayByRef",*args).Reply()
  self.chk(rep)
 def DataFaceNbrAssignArrayByRef64(self,face_neighbor,dest_offset,num_neighbors,neighbor_elems):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),
        (ValueType.Scalar,c_int64,dest_offset),
        (ValueType.Scalar,c_int32,num_neighbors),
        (ValueType.Array,c_int64,neighbor_elems),)
  rep=self.sndrcv("DataFaceNbrAssignArrayByRef64",*args).Reply()
  self.chk(rep)
 def DataFaceNbrAssignByRef(self,face_neighbor,element,face,nbrs_comp_obscure,num_neighbors,neighbor_elems,neighbor_zones):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,face),
        (ValueType.Scalar,c_bool,nbrs_comp_obscure),
        (ValueType.Scalar,c_int32,num_neighbors),
        (ValueType.Array,c_int32,neighbor_elems),
        (ValueType.Array,c_int32,neighbor_zones),)
  rep=self.sndrcv("DataFaceNbrAssignByRef",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceNbrAssignByRef64(self,face_neighbor,element,face,nbrs_comp_obscure,num_neighbors,neighbor_elems,neighbor_zones):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,face),
        (ValueType.Scalar,c_bool,nbrs_comp_obscure),
        (ValueType.Scalar,c_int32,num_neighbors),
        (ValueType.Array,c_int64,neighbor_elems),
        (ValueType.Array,c_int32,neighbor_zones),)
  rep=self.sndrcv("DataFaceNbrAssignByRef64",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceNbrBeginAssign(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataFaceNbrBeginAssign",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceNbrCustomLOD(self,zone,auto_assign_fn,load_callback,unload_callback,cleanup_callback,client_data):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_bool,auto_assign_fn),
        (ValueType.Address,c_uint64,getattr(load_callback,'value',load_callback)),
        (ValueType.Address,c_uint64,getattr(unload_callback,'value',unload_callback)),
        (ValueType.Address,c_uint64,getattr(cleanup_callback,'value',cleanup_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("DataFaceNbrCustomLOD",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceNbrEndAssign(self):
  rep=self.sndrcv("DataFaceNbrEndAssign").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataFaceNbrFaceIsObscured(self,face_neighbor,element,face,active_zones):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,face),
        (ValueType.Address,c_uint64,getattr(active_zones,'value',active_zones)),)
  rep=self.sndrcv("DataFaceNbrFaceIsObscured",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataFaceNbrGetClientData(self,face_neighbor):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),)
  rep=self.sndrcv("DataFaceNbrGetClientData",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def DataFaceNbrGetModeByRef(self,face_neighbor):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),)
  rep=self.sndrcv("DataFaceNbrGetModeByRef",*args).Reply()
  self.chk(rep)
  return FaceNeighborMode(rep.Args(0).Int32Value())
 def DataFaceNbrGetModeByZone(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataFaceNbrGetModeByZone",*args).Reply()
  self.chk(rep)
  return FaceNeighborMode(rep.Args(0).Int32Value())
 def DataFaceNbrGetNbrByRef(self,face_neighbor,element,face,neighbor_number):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,face),
        (ValueType.Scalar,c_int32,neighbor_number),)
  rep=self.sndrcv("DataFaceNbrGetNbrByRef",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int32Value())
 def DataFaceNbrGetNumNByRef(self,face_neighbor,element,face):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,face),)
  rep=self.sndrcv("DataFaceNbrGetNumNByRef",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int32Value(),
   rep.Args(1).Boolean())
 def DataFaceNbrGetReadableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataFaceNbrGetReadableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataFaceNbrRawItemType(self,face_neighbor):
  args=((ValueType.Address,c_uint64,getattr(face_neighbor,'value',face_neighbor)),)
  rep=self.sndrcv("DataFaceNbrRawItemType",*args).Reply()
  self.chk(rep)
  return OffsetDataType(rep.Args(0).Int32Value())
 def DataIJKCellGetIndices(self,zone,plane,cell_index):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,IJKPlanes(plane).value),
        (ValueType.Scalar,c_int64,cell_index),)
  rep=self.sndrcv("DataIJKCellGetIndices",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value(),
   rep.Args(3).Int64Value())
 def DataLoadBegin(self):
  rep=self.sndrcv("DataLoadBegin").Reply()
  self.chk(rep)
 def DataLoadEnd(self):
  rep=self.sndrcv("DataLoadEnd").Reply()
  self.chk(rep)
 def DataLoadFinishX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataLoadFinishX",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value())
 def DataLoadStart(self):
  rep=self.sndrcv("DataLoadStart").Reply()
  self.chk(rep)
 def DataNodeAlloc(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataNodeAlloc",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataNodeArrayGetByRef(self,source_node_map,source_offset,source_count,dest_node_array):
  args=((ValueType.Address,c_uint64,getattr(source_node_map,'value',source_node_map)),
        (ValueType.Scalar,c_int64,source_offset),
        (ValueType.Scalar,c_int64,source_count),
        (ValueType.Array,None,dest_node_array),)
  rep=self.sndrcv("DataNodeArrayGetByRef",*args).Reply()
  self.chk(rep)
  dest_node_array[:] = cast(byref(rep.Args(0).Uint8Array()), POINTER(type(dest_node_array))).contents[:]
 def DataNodeArraySetByRef(self,dest_node_map,dest_offset,dest_count,source_node_array):
  args=((ValueType.Address,c_uint64,getattr(dest_node_map,'value',dest_node_map)),
        (ValueType.Scalar,c_int64,dest_offset),
        (ValueType.Scalar,c_int64,dest_count),
        (ValueType.Array,c_int32,source_node_array),)
  rep=self.sndrcv("DataNodeArraySetByRef",*args).Reply()
  self.chk(rep)
 def DataNodeArraySetByRef64(self,dest_node_map,dest_offset,dest_count,source_node_array):
  args=((ValueType.Address,c_uint64,getattr(dest_node_map,'value',dest_node_map)),
        (ValueType.Scalar,c_int64,dest_offset),
        (ValueType.Scalar,c_int64,dest_count),
        (ValueType.Array,c_int64,source_node_array),)
  rep=self.sndrcv("DataNodeArraySetByRef64",*args).Reply()
  self.chk(rep)
 def DataNodeAutoLOD(self,zone,file_name,offset,is_data_native_byte_order):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Text,None,file_name),
        (ValueType.Scalar,c_int64,offset),
        (ValueType.Scalar,c_bool,is_data_native_byte_order),)
  rep=self.sndrcv("DataNodeAutoLOD",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataNodeCustomLOD(self,zone,load_callback,unload_callback,cleanup_callback,client_data):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Address,c_uint64,getattr(load_callback,'value',load_callback)),
        (ValueType.Address,c_uint64,getattr(unload_callback,'value',unload_callback)),
        (ValueType.Address,c_uint64,getattr(cleanup_callback,'value',cleanup_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("DataNodeCustomLOD",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataNodeGetByRef(self,node_map_ptr,element,corner):
  args=((ValueType.Address,c_uint64,getattr(node_map_ptr,'value',node_map_ptr)),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,corner),)
  rep=self.sndrcv("DataNodeGetByRef",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataNodeGetByZone(self,zone,element,corner):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,corner),)
  rep=self.sndrcv("DataNodeGetByZone",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataNodeGetClientData(self,node_map):
  args=((ValueType.Address,c_uint64,getattr(node_map,'value',node_map)),)
  rep=self.sndrcv("DataNodeGetClientData",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def DataNodeGetNodesPerElem(self,node_map_ptr):
  args=((ValueType.Address,c_uint64,getattr(node_map_ptr,'value',node_map_ptr)),)
  rep=self.sndrcv("DataNodeGetNodesPerElem",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataNodeGetRawItemType(self,node_map):
  args=((ValueType.Address,c_uint64,getattr(node_map,'value',node_map)),)
  rep=self.sndrcv("DataNodeGetRawItemType",*args).Reply()
  self.chk(rep)
  return OffsetDataType(rep.Args(0).Int32Value())
 def DataNodeGetRawPtrByRef(self,node_map):
  args=((ValueType.Address,c_uint64,getattr(node_map,'value',node_map)),)
  rep=self.sndrcv("DataNodeGetRawPtrByRef",*args).Reply()
  self.chk(rep)
 def DataNodeGetRawPtrByRef64(self,node_map):
  args=((ValueType.Address,c_uint64,getattr(node_map,'value',node_map)),)
  rep=self.sndrcv("DataNodeGetRawPtrByRef64",*args).Reply()
  self.chk(rep)
 def DataNodeGetReadableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataNodeGetReadableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataNodeGetWritableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataNodeGetWritableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataNodeSetByRef(self,nm,element,corner,node):
  args=((ValueType.Address,c_uint64,getattr(nm,'value',nm)),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,corner),
        (ValueType.Scalar,c_int64,node),)
  rep=self.sndrcv("DataNodeSetByRef",*args).Reply()
  self.chk(rep)
 def DataNodeSetByZone(self,zone,element,corner,node):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int64,element),
        (ValueType.Scalar,c_int32,corner),
        (ValueType.Scalar,c_int64,node),)
  rep=self.sndrcv("DataNodeSetByZone",*args).Reply()
  self.chk(rep)
 def DataNodeToElemMapGetElem(self,node_to_elem_map,node,elem_offset):
  args=((ValueType.Address,c_uint64,getattr(node_to_elem_map,'value',node_to_elem_map)),
        (ValueType.Scalar,c_int64,node),
        (ValueType.Scalar,c_int64,elem_offset),)
  rep=self.sndrcv("DataNodeToElemMapGetElem",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataNodeToElemMapGetNumElems(self,node_to_elem_map,node):
  args=((ValueType.Address,c_uint64,getattr(node_to_elem_map,'value',node_to_elem_map)),
        (ValueType.Scalar,c_int64,node),)
  rep=self.sndrcv("DataNodeToElemMapGetNumElems",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataNodeToElemMapGetReadableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("DataNodeToElemMapGetReadableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataRotate(self,data_set_id,zones,spatial_vars,num_vectors,u_vars,v_vars,w_vars,is3_d_rotation,rotation_in_degrees,origin,normal):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Address,c_uint64,getattr(zones,'value',zones)),
        (ValueType.Array,c_int32,spatial_vars),
        (ValueType.Scalar,c_int32,num_vectors),
        (ValueType.Array,c_int32,u_vars),
        (ValueType.Array,c_int32,v_vars),
        (ValueType.Array,c_int32,w_vars),
        (ValueType.Scalar,c_bool,is3_d_rotation),
        (ValueType.Scalar,c_double,rotation_in_degrees),
        (ValueType.Array,c_double,origin),
        (ValueType.Array,c_double,normal),)
  rep=self.sndrcv("DataRotate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataRotate2D(self,zone_set,rotate_amount_in_degrees,x_origin,y_origin):
  args=((ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_double,rotate_amount_in_degrees),
        (ValueType.Scalar,c_double,x_origin),
        (ValueType.Scalar,c_double,y_origin),)
  rep=self.sndrcv("DataRotate2D",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAddJournalCommand(self,command_processor_id_string,instructions,raw_data):
  args=((ValueType.Text,None,command_processor_id_string),
        (ValueType.Text,None,instructions),
        (ValueType.Text,None,raw_data),)
  rep=self.sndrcv("DataSetAddJournalCommand",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAddRawJournalCom(self,command):
  args=((ValueType.Text,None,command),)
  rep=self.sndrcv("DataSetAddRawJournalCom",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAddVar(self,var_name,field_data_type__array):
  args=((ValueType.Text,None,var_name),
        (ValueType.Array,c_int32,FieldDataType(field_data_type__array).value),)
  rep=self.sndrcv("DataSetAddVar",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAddVarX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataSetAddVarX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAddWriterX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataSetAddWriterX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAddZone(self,name,i_max,j_max,k_max,zone_type,var_data_type__array):
  args=((ValueType.Text,None,name),
        (ValueType.Scalar,c_int64,i_max),
        (ValueType.Scalar,c_int64,j_max),
        (ValueType.Scalar,c_int64,k_max),
        (ValueType.Scalar,c_int32,ZoneType(zone_type).value),
        (ValueType.Array,c_int32,FieldDataType(var_data_type__array).value),)
  rep=self.sndrcv("DataSetAddZone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAddZoneX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataSetAddZoneX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetAutoAssignStrandIDs(self,zone_set):
  args=((ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),)
  rep=self.sndrcv("DataSetAutoAssignStrandIDs",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetCreate(self,data_set_title,var_names,reset_style):
  args=((ValueType.Text,None,data_set_title),
        (ValueType.Address,c_uint64,getattr(var_names,'value',var_names)),
        (ValueType.Scalar,c_bool,reset_style),)
  rep=self.sndrcv("DataSetCreate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetDeleteVar(self,var_list):
  args=((ValueType.Address,c_uint64,getattr(var_list,'value',var_list)),)
  rep=self.sndrcv("DataSetDeleteVar",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetDeleteZone(self,zone_list):
  args=((ValueType.Address,c_uint64,getattr(zone_list,'value',zone_list)),)
  rep=self.sndrcv("DataSetDeleteZone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetGetActiveStrandIDs(self):
  rep=self.sndrcv("DataSetGetActiveStrandIDs").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataSetGetInfo(self):
  rep=self.sndrcv("DataSetGetInfo").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)),
   rep.Args(1).Int32Value(),
   rep.Args(2).Int32Value())
 def DataSetGetInfoByUniqueID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("DataSetGetInfoByUniqueID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)),
   rep.Args(1).Int32Value(),
   rep.Args(2).Int32Value())
 def DataSetGetIntItemTypeForContentRange(self,max_value_stored_in_array):
  args=((ValueType.Scalar,c_int64,max_value_stored_in_array),)
  rep=self.sndrcv("DataSetGetIntItemTypeForContentRange",*args).Reply()
  self.chk(rep)
  return OffsetDataType(rep.Args(0).Int32Value())
 def DataSetGetMaxStrandID(self):
  rep=self.sndrcv("DataSetGetMaxStrandID").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataSetGetNumVars(self):
  rep=self.sndrcv("DataSetGetNumVars").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataSetGetNumVarsByUniqueID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("DataSetGetNumVarsByUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataSetGetNumVarsForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("DataSetGetNumVarsForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataSetGetNumZones(self):
  rep=self.sndrcv("DataSetGetNumZones").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataSetGetNumZonesByUniqueID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("DataSetGetNumZonesByUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataSetGetNumZonesForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("DataSetGetNumZonesForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataSetGetRelevantZones(self,solution_time_min,solution_time_max,ignore_static_zones):
  args=((ValueType.Scalar,c_double,solution_time_min),
        (ValueType.Scalar,c_double,solution_time_max),
        (ValueType.Scalar,c_bool,ignore_static_zones),)
  rep=self.sndrcv("DataSetGetRelevantZones",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataSetGetSZLRegistration(self):
  rep=self.sndrcv("DataSetGetSZLRegistration").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataSetGetStrandIDs(self):
  rep=self.sndrcv("DataSetGetStrandIDs").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataSetGetStrandRelevantZones(self,strand_id,solution_time_min,solution_time_max):
  args=((ValueType.Scalar,c_int32,strand_id),
        (ValueType.Scalar,c_double,solution_time_min),
        (ValueType.Scalar,c_double,solution_time_max),)
  rep=self.sndrcv("DataSetGetStrandRelevantZones",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataSetGetUniqueID(self):
  rep=self.sndrcv("DataSetGetUniqueID").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataSetGetVarLoadMode(self):
  rep=self.sndrcv("DataSetGetVarLoadMode").Reply()
  self.chk(rep)
  return VarLoadMode(rep.Args(0).Int32Value())
 def DataSetGetZonesForStrandID(self,strand_id):
  args=((ValueType.Scalar,c_int32,strand_id),)
  rep=self.sndrcv("DataSetGetZonesForStrandID",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataSetIsAvailable(self):
  rep=self.sndrcv("DataSetIsAvailable").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataSetIsAvailableByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("DataSetIsAvailableByUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataSetIsAvailableForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("DataSetIsAvailableForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataSetIsLODAllowed(self):
  rep=self.sndrcv("DataSetIsLODAllowed").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataSetIsLocked(self):
  rep=self.sndrcv("DataSetIsLocked").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Boolean(),
   self.read_text(rep.Args(1)))
 def DataSetIsSharingAllowed(self):
  rep=self.sndrcv("DataSetIsSharingAllowed").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataSetIsUsedInLayout(self):
  rep=self.sndrcv("DataSetIsUsedInLayout").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataSetJournalIsValid(self):
  rep=self.sndrcv("DataSetJournalIsValid").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataSetLockOff(self,lock_string):
  args=((ValueType.Text,None,lock_string),)
  rep=self.sndrcv("DataSetLockOff",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetLockOn(self,lock_string):
  args=((ValueType.Text,None,lock_string),)
  rep=self.sndrcv("DataSetLockOn",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetMakeVarsAvailableByUniqueID(self,data_set_id,zones,vars_needed):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Address,c_uint64,getattr(zones,'value',zones)),
        (ValueType.Address,c_uint64,getattr(vars_needed,'value',vars_needed)),)
  rep=self.sndrcv("DataSetMakeVarsAvailableByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetPostReadFinished(self,is_read_ok):
  args=((ValueType.Scalar,c_bool,is_read_ok),)
  rep=self.sndrcv("DataSetPostReadFinished",*args).Reply()
  self.chk(rep)
 def DataSetReadX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataSetReadX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetSetTitle(self,data_set_title):
  args=((ValueType.Text,None,data_set_title),)
  rep=self.sndrcv("DataSetSetTitle",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetSetTitleByUniqueID(self,unique_id,data_set_title):
  args=((ValueType.Scalar,c_int64,unique_id),
        (ValueType.Text,None,data_set_title),)
  rep=self.sndrcv("DataSetSetTitleByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataSetSuspendMarking(self,do_suspend):
  args=((ValueType.Scalar,c_bool,do_suspend),)
  rep=self.sndrcv("DataSetSuspendMarking",*args).Reply()
  self.chk(rep)
 def DataSetWriteX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataSetWriteX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueAlloc(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueAlloc",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueArrayGetByRef(self,source_field_data,source_offset,source_count,dest_value_array):
  args=((ValueType.Address,c_uint64,getattr(source_field_data,'value',source_field_data)),
        (ValueType.Scalar,c_int64,source_offset),
        (ValueType.Scalar,c_int64,source_count),
        (ValueType.Array,None,dest_value_array),)
  rep=self.sndrcv("DataValueArrayGetByRef",*args).Reply()
  self.chk(rep)
  dest_value_array[:] = cast(byref(rep.Args(0).Uint8Array()), POINTER(type(dest_value_array))).contents[:]
 def DataValueArraySetByRef(self,dest_field_data,dest_offset,dest_count,source_value_array):
  args=((ValueType.Address,c_uint64,getattr(dest_field_data,'value',dest_field_data)),
        (ValueType.Scalar,c_int64,dest_offset),
        (ValueType.Scalar,c_int64,dest_count),
        (ValueType.Array,c_uint8,source_value_array),)
  rep=self.sndrcv("DataValueArraySetByRef",*args).Reply()
  self.chk(rep)
 def DataValueAutoLOD(self,zone,var,data_value_structure,file_name,offset,stride,is_data_native_byte_order):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),
        (ValueType.Scalar,c_int32,DataValueStructure(data_value_structure).value),
        (ValueType.Text,None,file_name),
        (ValueType.Scalar,c_int64,offset),
        (ValueType.Scalar,c_int64,stride),
        (ValueType.Scalar,c_bool,is_data_native_byte_order),)
  rep=self.sndrcv("DataValueAutoLOD",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueBranchShared(self,zone,var,copy_shared_data):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),
        (ValueType.Scalar,c_bool,copy_shared_data),)
  rep=self.sndrcv("DataValueBranchShared",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueCopy(self,source_zone,dest_zone,var):
  args=((ValueType.Scalar,c_int32,source_zone),
        (ValueType.Scalar,c_int32,dest_zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueCopy",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueCustomLOD(self,zone,var,variable_load,variable_unload,variable_cleanup,get_value_function,set_value_function,client_data):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),
        (ValueType.Address,c_uint64,getattr(variable_load,'value',variable_load)),
        (ValueType.Address,c_uint64,getattr(variable_unload,'value',variable_unload)),
        (ValueType.Address,c_uint64,getattr(variable_cleanup,'value',variable_cleanup)),
        (ValueType.Address,c_uint64,getattr(get_value_function,'value',get_value_function)),
        (ValueType.Address,c_uint64,getattr(set_value_function,'value',set_value_function)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("DataValueCustomLOD",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueGetByRef(self,field_data,point_index):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),
        (ValueType.Scalar,c_int64,point_index),)
  rep=self.sndrcv("DataValueGetByRef",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def DataValueGetByZoneVar(self,zone,var,value_index):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),
        (ValueType.Scalar,c_int64,value_index),)
  rep=self.sndrcv("DataValueGetByZoneVar",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def DataValueGetClientData(self,field_data):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),)
  rep=self.sndrcv("DataValueGetClientData",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def DataValueGetCountByRef(self,field_data):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),)
  rep=self.sndrcv("DataValueGetCountByRef",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def DataValueGetLocation(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetLocation",*args).Reply()
  self.chk(rep)
  return ValueLocation(rep.Args(0).Int32Value())
 def DataValueGetLocationByRef(self,field_data):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),)
  rep=self.sndrcv("DataValueGetLocationByRef",*args).Reply()
  self.chk(rep)
  return ValueLocation(rep.Args(0).Int32Value())
 def DataValueGetMinMaxByRef(self,field_data):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),)
  rep=self.sndrcv("DataValueGetMinMaxByRef",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def DataValueGetMinMaxByZoneVar(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetMinMaxByZoneVar",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def DataValueGetPrevSharedZone(self,zones_to_consider,zone,var):
  args=((ValueType.Address,c_uint64,getattr(zones_to_consider,'value',zones_to_consider)),
        (ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetPrevSharedZone",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataValueGetRawPtrByRef(self,field_data):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),)
  rep=self.sndrcv("DataValueGetRawPtrByRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetReadableCCRef(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetReadableCCRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetReadableDerivedRef(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetReadableDerivedRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetReadableNLRef(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetReadableNLRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetReadableNativeRef(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetReadableNativeRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetReadableNativeRefByUniqueID(self,dataset_id,zone,var):
  args=((ValueType.Scalar,c_int64,dataset_id),
        (ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetReadableNativeRefByUniqueID",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetRefType(self,field_data):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),)
  rep=self.sndrcv("DataValueGetRefType",*args).Reply()
  self.chk(rep)
  return FieldDataType(rep.Args(0).Int32Value())
 def DataValueGetShareCount(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetShareCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def DataValueGetShareZoneSet(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetShareZoneSet",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetType(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetType",*args).Reply()
  self.chk(rep)
  return FieldDataType(rep.Args(0).Int32Value())
 def DataValueGetWritableNativeRef(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetWritableNativeRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetWritableNativeRefByUniqueID(self,dataset_id,zone,var):
  args=((ValueType.Scalar,c_int64,dataset_id),
        (ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueGetWritableNativeRefByUniqueID",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueGetZoneVarByRef(self,fd):
  args=((ValueType.Address,c_uint64,getattr(fd,'value',fd)),)
  rep=self.sndrcv("DataValueGetZoneVarByRef",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value(),
   rep.Args(1).Int32Value())
 def DataValueIsLoaded(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueIsLoaded",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataValueIsMinMaxValidByZoneVar(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueIsMinMaxValidByZoneVar",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataValueIsPassive(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueIsPassive",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataValueIsSharingOk(self,source_zone,dest_zone,var):
  args=((ValueType.Scalar,c_int32,source_zone),
        (ValueType.Scalar,c_int32,dest_zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueIsSharingOk",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def DataValueRefGetGetFunc(self,fd):
  args=((ValueType.Address,c_uint64,getattr(fd,'value',fd)),)
  rep=self.sndrcv("DataValueRefGetGetFunc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueRefGetSetFunc(self,fd):
  args=((ValueType.Address,c_uint64,getattr(fd,'value',fd)),)
  rep=self.sndrcv("DataValueRefGetSetFunc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def DataValueSetByRef(self,fd,point_index,value):
  args=((ValueType.Address,c_uint64,getattr(fd,'value',fd)),
        (ValueType.Scalar,c_int64,point_index),
        (ValueType.Scalar,c_double,value),)
  rep=self.sndrcv("DataValueSetByRef",*args).Reply()
  self.chk(rep)
 def DataValueSetByZoneVar(self,zone,var,point_index,value):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),
        (ValueType.Scalar,c_int64,point_index),
        (ValueType.Scalar,c_double,value),)
  rep=self.sndrcv("DataValueSetByZoneVar",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueSetByZoneVarX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("DataValueSetByZoneVarX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DataValueSetMinMaxByRef(self,field_data,min_value,max_value):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),
        (ValueType.Scalar,c_double,min_value),
        (ValueType.Scalar,c_double,max_value),)
  rep=self.sndrcv("DataValueSetMinMaxByRef",*args).Reply()
  self.chk(rep)
 def DataValueSetMinMaxByZoneVar(self,zone,var,min_value,max_value):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),
        (ValueType.Scalar,c_double,min_value),
        (ValueType.Scalar,c_double,max_value),)
  rep=self.sndrcv("DataValueSetMinMaxByZoneVar",*args).Reply()
  self.chk(rep)
 def DataValueShare(self,source_zone,dest_zone,var):
  args=((ValueType.Scalar,c_int32,source_zone),
        (ValueType.Scalar,c_int32,dest_zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueShare",*args).Reply()
  self.chk(rep)
 def DataValueUnload(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("DataValueUnload",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Delay(self,seconds):
  args=((ValueType.Scalar,c_int32,seconds),)
  rep=self.sndrcv("Delay",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DialogAllowDoubleClickLaunch(self,dialog,do_allow):
  args=((ValueType.Scalar,c_int32,Dialog(dialog).value),
        (ValueType.Scalar,c_bool,do_allow),)
  rep=self.sndrcv("DialogAllowDoubleClickLaunch",*args).Reply()
  self.chk(rep)
 def DialogCheckPercentDone(self,percent_done):
  args=((ValueType.Scalar,c_int32,percent_done),)
  rep=self.sndrcv("DialogCheckPercentDone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DialogDrop(self,dialog_to_drop):
  args=((ValueType.Scalar,c_int32,Dialog(dialog_to_drop).value),)
  rep=self.sndrcv("DialogDrop",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DialogDropPercentDone(self):
  rep=self.sndrcv("DialogDropPercentDone").Reply()
  self.chk(rep)
 def DialogErrMsg(self,message):
  args=((ValueType.Text,None,message),)
  rep=self.sndrcv("DialogErrMsg",*args).Reply()
  self.chk(rep)
 def DialogGetSimpleText(self,instructions,default_text):
  args=((ValueType.Text,None,instructions),
        (ValueType.Text,None,default_text),)
  rep=self.sndrcv("DialogGetSimpleText",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def DialogLastMessageBox(self):
  rep=self.sndrcv("DialogLastMessageBox").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DialogLaunch(self,dialog_to_launch):
  args=((ValueType.Scalar,c_int32,Dialog(dialog_to_launch).value),)
  rep=self.sndrcv("DialogLaunch",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DialogLaunchPercentDone(self,label,show_the_scale):
  args=((ValueType.Text,None,label),
        (ValueType.Scalar,c_bool,show_the_scale),)
  rep=self.sndrcv("DialogLaunchPercentDone",*args).Reply()
  self.chk(rep)
 def DialogMessageBox(self,message,message_box_type):
  args=((ValueType.Text,None,message),
        (ValueType.Scalar,c_int32,MessageBoxType(message_box_type).value),)
  rep=self.sndrcv("DialogMessageBox",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DialogSetPercentDoneText(self,text):
  args=((ValueType.Text,None,text),)
  rep=self.sndrcv("DialogSetPercentDoneText",*args).Reply()
  self.chk(rep)
 def DispatchWorkAreaEvent(self,i,j,button_or_key,event,is_shifted,is_alted,is_controlled):
  args=((ValueType.Scalar,c_int32,i),
        (ValueType.Scalar,c_int32,j),
        (ValueType.Scalar,c_int32,button_or_key),
        (ValueType.Scalar,c_int32,Event(event).value),
        (ValueType.Scalar,c_bool,is_shifted),
        (ValueType.Scalar,c_bool,is_alted),
        (ValueType.Scalar,c_bool,is_controlled),)
  rep=self.sndrcv("DispatchWorkAreaEvent",*args).Reply()
  self.chk(rep)
 def DoubleBuffer(self,double_buffer_action):
  args=((ValueType.Scalar,c_int32,DoubleBufferAction(double_buffer_action).value),)
  rep=self.sndrcv("DoubleBuffer",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DrawGraphics(self,do_drawing):
  args=((ValueType.Scalar,c_bool,do_drawing),)
  rep=self.sndrcv("DrawGraphics",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def DropOpeningBanner(self):
  rep=self.sndrcv("DropOpeningBanner").Reply()
  self.chk(rep)
 def DynamicLabelRegisterCallback(self,dynamic_label_name,dynamic_label_callback,client_data):
  args=((ValueType.Text,None,dynamic_label_name),
        (ValueType.Address,c_uint64,getattr(dynamic_label_callback,'value',dynamic_label_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("DynamicLabelRegisterCallback",*args).Reply()
  self.chk(rep)
 def ElapseTimeInMS(self):
  rep=self.sndrcv("ElapseTimeInMS").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ElemOrientGetOrientation(self,element_orientation,element):
  args=((ValueType.Address,c_uint64,getattr(element_orientation,'value',element_orientation)),
        (ValueType.Scalar,c_int64,element),)
  rep=self.sndrcv("ElemOrientGetOrientation",*args).Reply()
  self.chk(rep)
  return ElementOrientation(rep.Args(0).Int32Value())
 def ElemOrientGetReadableRef(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ElemOrientGetReadableRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def EventAddPostDrawCallback(self,draw_event_callback,client_data):
  args=((ValueType.Address,c_uint64,getattr(draw_event_callback,'value',draw_event_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("EventAddPostDrawCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def EventAddPreDrawCallback(self,draw_event_callback,client_data):
  args=((ValueType.Address,c_uint64,getattr(draw_event_callback,'value',draw_event_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("EventAddPreDrawCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Export(self,append):
  args=((ValueType.Scalar,c_bool,append),)
  rep=self.sndrcv("Export",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExportCancel(self):
  rep=self.sndrcv("ExportCancel").Reply()
  self.chk(rep)
 def ExportFinish(self):
  rep=self.sndrcv("ExportFinish").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ExportIsRecording(self):
  rep=self.sndrcv("ExportIsRecording").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ExportNextFrame(self):
  rep=self.sndrcv("ExportNextFrame").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExportSetup(self,attribute,sub_attribute,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Text,None,sub_attribute),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ExportSetup",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ExportStart(self):
  rep=self.sndrcv("ExportStart").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExtractFromGeom(self,extract_only_points_on_polyline,include_distance_variable,num_pts_to_extract_along_polyline,extract_to_file,extract_f_name):
  args=((ValueType.Scalar,c_bool,extract_only_points_on_polyline),
        (ValueType.Scalar,c_bool,include_distance_variable),
        (ValueType.Scalar,c_int64,num_pts_to_extract_along_polyline),
        (ValueType.Scalar,c_bool,extract_to_file),
        (ValueType.Text,None,extract_f_name),)
  rep=self.sndrcv("ExtractFromGeom",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExtractFromPolyline(self,polyline_x_pts__array,polyline_y_pts__array,polyline_z_pts__array,num_pts_in_polyline,extract_through_volume,extract_only_points_on_polyline,include_distance_variable,num_pts_to_extract_along_polyline,extract_to_file,extract_f_name):
  args=((ValueType.Array,c_double,polyline_x_pts__array),
        (ValueType.Array,c_double,polyline_y_pts__array),
        (ValueType.Array,c_double,polyline_z_pts__array),
        (ValueType.Scalar,c_int64,num_pts_in_polyline),
        (ValueType.Scalar,c_bool,extract_through_volume),
        (ValueType.Scalar,c_bool,extract_only_points_on_polyline),
        (ValueType.Scalar,c_bool,include_distance_variable),
        (ValueType.Scalar,c_int64,num_pts_to_extract_along_polyline),
        (ValueType.Scalar,c_bool,extract_to_file),
        (ValueType.Text,None,extract_f_name),)
  rep=self.sndrcv("ExtractFromPolyline",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExtractInstallCallback(self,extract_destination,information_line_text):
  args=((ValueType.Address,c_uint64,getattr(extract_destination,'value',extract_destination)),
        (ValueType.Text,None,information_line_text),)
  rep=self.sndrcv("ExtractInstallCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExtractIsoSurfacesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ExtractIsoSurfacesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExtractSlicesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ExtractSlicesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExtractStreamtracesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ExtractStreamtracesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ExtractTimesFromFileNames(self,file_names,times,require_alpha_token_matching):
  args=((ValueType.Address,c_uint64,getattr(file_names,'value',file_names)),
        (ValueType.Array,c_double,times),
        (ValueType.Scalar,c_bool,require_alpha_token_matching),)
  rep=self.sndrcv("ExtractTimesFromFileNames",*args).Reply()
  self.chk(rep)
  times[:] = cast(byref(rep.Args(0).Float64Array()), POINTER(type(times))).contents[:]
  return (rep.Status() == Status.Success)
 def FeatureIsEnabled(self,feature_id):
  args=((ValueType.Scalar,c_uint64,feature_id),)
  rep=self.sndrcv("FeatureIsEnabled",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldLayerIsActive(self,layer_show_flag):
  args=((ValueType.Text,None,layer_show_flag),)
  rep=self.sndrcv("FieldLayerIsActive",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldLayerIsActiveForFrame(self,frame_id,layer_show_flag):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Text,None,layer_show_flag),)
  rep=self.sndrcv("FieldLayerIsActiveForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldLayerSetIsActive(self,layer_show_flag,turn_on_field_layer):
  args=((ValueType.Text,None,layer_show_flag),
        (ValueType.Scalar,c_bool,turn_on_field_layer),)
  rep=self.sndrcv("FieldLayerSetIsActive",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def FieldMapGetActive(self):
  rep=self.sndrcv("FieldMapGetActive").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def FieldMapGetCandidateZone(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapGetCandidateZone",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def FieldMapGetCandidateZoneForFrame(self,frame_id,field_map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapGetCandidateZoneForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def FieldMapGetCount(self):
  rep=self.sndrcv("FieldMapGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def FieldMapGetCountForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("FieldMapGetCountForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def FieldMapGetMode(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapGetMode",*args).Reply()
  self.chk(rep)
  return FieldMapMode(rep.Args(0).Int32Value())
 def FieldMapGetModeForFrame(self,frame_id,field_map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapGetModeForFrame",*args).Reply()
  self.chk(rep)
  return FieldMapMode(rep.Args(0).Int32Value())
 def FieldMapGetZones(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapGetZones",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def FieldMapHasFEZones(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasFEZones",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasIJKOrderedZones(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasIJKOrderedZones",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasIJKOrderedZonesForFrame(self,frame_id,field_map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasIJKOrderedZonesForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasLinearZones(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasLinearZones",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasOrderedZones(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasOrderedZones",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasOrderedZonesForFrame(self,frame_id,field_map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasOrderedZonesForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasSurfaceZones(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasSurfaceZones",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasVolumeZones(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasVolumeZones",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapHasVolumeZonesForFrame(self,frame_id,field_map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapHasVolumeZonesForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapIsActive(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapIsActive",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapIsActiveForFrame(self,frame_id,field_map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapIsActiveForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapIsRelevant(self,field_map):
  args=((ValueType.Scalar,c_int32,field_map),)
  rep=self.sndrcv("FieldMapIsRelevant",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FieldMapSetActive(self,field_map_set,assign_modifier):
  args=((ValueType.Address,c_uint64,getattr(field_map_set,'value',field_map_set)),
        (ValueType.Scalar,c_int32,AssignOp(assign_modifier).value),)
  rep=self.sndrcv("FieldMapSetActive",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def FieldStyleGetArbValue(self,zone,s1,s2,s3):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Text,None,s1),
        (ValueType.Text,None,s2),
        (ValueType.Text,None,s3),)
  rep=self.sndrcv("FieldStyleGetArbValue",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def FieldStyleGetDoubleValue(self,zone,s1,s2,s3):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Text,None,s1),
        (ValueType.Text,None,s2),
        (ValueType.Text,None,s3),)
  rep=self.sndrcv("FieldStyleGetDoubleValue",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def FileGetTempDirName(self):
  rep=self.sndrcv("FileGetTempDirName").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def FileGetTempName(self):
  rep=self.sndrcv("FileGetTempName").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def FourierTransform(self,independent_var,window_function,dependent_vars,source_zones,include_conjugates,obey_source_zone_blanking):
  args=((ValueType.Scalar,c_int32,independent_var),
        (ValueType.Scalar,c_int32,WindowFunction(window_function).value),
        (ValueType.Address,c_uint64,getattr(dependent_vars,'value',dependent_vars)),
        (ValueType.Address,c_uint64,getattr(source_zones,'value',source_zones)),
        (ValueType.Scalar,c_bool,include_conjugates),
        (ValueType.Scalar,c_bool,obey_source_zone_blanking),)
  rep=self.sndrcv("FourierTransform",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FourierTransformIsValidZone(self,zone_num):
  args=((ValueType.Scalar,c_int32,zone_num),)
  rep=self.sndrcv("FourierTransformIsValidZone",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FourierTransformIsValidZoneByDataSetID(self,dataset_id,zone_num):
  args=((ValueType.Scalar,c_int64,dataset_id),
        (ValueType.Scalar,c_int32,zone_num),)
  rep=self.sndrcv("FourierTransformIsValidZoneByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FourierTransformX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("FourierTransformX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameActivateAtPosition(self,x,y):
  args=((ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),)
  rep=self.sndrcv("FrameActivateAtPosition",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameActivateByName(self,name):
  args=((ValueType.Text,None,name),)
  rep=self.sndrcv("FrameActivateByName",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameActivateByNumber(self,frame_num):
  args=((ValueType.Scalar,c_int32,frame_num),)
  rep=self.sndrcv("FrameActivateByNumber",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameActivateByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("FrameActivateByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameActivateTop(self):
  rep=self.sndrcv("FrameActivateTop").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameCreateNew(self,use_supplied_frame_size,x_pos,y_pos,width,height):
  args=((ValueType.Scalar,c_bool,use_supplied_frame_size),
        (ValueType.Scalar,c_double,x_pos),
        (ValueType.Scalar,c_double,y_pos),
        (ValueType.Scalar,c_double,width),
        (ValueType.Scalar,c_double,height),)
  rep=self.sndrcv("FrameCreateNew",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameDeleteActive(self):
  rep=self.sndrcv("FrameDeleteActive").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameDeleteByNumber(self,frame_num):
  args=((ValueType.Scalar,c_int32,frame_num),)
  rep=self.sndrcv("FrameDeleteByNumber",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameDeleteByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("FrameDeleteByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameFitAllToPaper(self):
  rep=self.sndrcv("FrameFitAllToPaper").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameGetActiveID(self):
  rep=self.sndrcv("FrameGetActiveID").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def FrameGetBackgroundColor(self):
  rep=self.sndrcv("FrameGetBackgroundColor").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def FrameGetCount(self):
  rep=self.sndrcv("FrameGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def FrameGetDataSetUniqueIDByFrameID(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("FrameGetDataSetUniqueIDByFrameID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def FrameGetName(self):
  rep=self.sndrcv("FrameGetName").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def FrameGetPlotType(self):
  rep=self.sndrcv("FrameGetPlotType").Reply()
  self.chk(rep)
  return PlotType(rep.Args(0).Int32Value())
 def FrameGetPlotTypeForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("FrameGetPlotTypeForFrame",*args).Reply()
  self.chk(rep)
  return PlotType(rep.Args(0).Int32Value())
 def FrameGetPosAndSize(self):
  rep=self.sndrcv("FrameGetPosAndSize").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value(),
   rep.Args(3).Float64Value())
 def FrameGetUniqueID(self):
  rep=self.sndrcv("FrameGetUniqueID").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def FrameLightweightForAllPagesLoopEnd(self):
  rep=self.sndrcv("FrameLightweightForAllPagesLoopEnd").Reply()
  self.chk(rep)
 def FrameLightweightForAllPagesLoopNext(self):
  rep=self.sndrcv("FrameLightweightForAllPagesLoopNext").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameLightweightForAllPagesLoopStart(self):
  rep=self.sndrcv("FrameLightweightForAllPagesLoopStart").Reply()
  self.chk(rep)
 def FrameLightweightLoopEnd(self):
  rep=self.sndrcv("FrameLightweightLoopEnd").Reply()
  self.chk(rep)
 def FrameLightweightLoopNext(self):
  rep=self.sndrcv("FrameLightweightLoopNext").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FrameLightweightLoopStart(self):
  rep=self.sndrcv("FrameLightweightLoopStart").Reply()
  self.chk(rep)
 def FrameMoveToBottomByName(self,name):
  args=((ValueType.Text,None,name),)
  rep=self.sndrcv("FrameMoveToBottomByName",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameMoveToBottomByNumber(self,frame_num):
  args=((ValueType.Scalar,c_int32,frame_num),)
  rep=self.sndrcv("FrameMoveToBottomByNumber",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameMoveToBottomByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("FrameMoveToBottomByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameMoveToTopByName(self,name):
  args=((ValueType.Text,None,name),)
  rep=self.sndrcv("FrameMoveToTopByName",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameMoveToTopByNumber(self,frame_num):
  args=((ValueType.Scalar,c_int32,frame_num),)
  rep=self.sndrcv("FrameMoveToTopByNumber",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameMoveToTopByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("FrameMoveToTopByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameNeedsRedraw(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("FrameNeedsRedraw",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def FramePopAtPosition(self,x,y):
  args=((ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),)
  rep=self.sndrcv("FramePopAtPosition",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameSetBackgroundColor(self,color):
  args=((ValueType.Scalar,c_int32,color),)
  rep=self.sndrcv("FrameSetBackgroundColor",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def FrameSetDataSet(self,source_data_set_id,target_frame_id):
  args=((ValueType.Scalar,c_int64,source_data_set_id),
        (ValueType.Scalar,c_int64,target_frame_id),)
  rep=self.sndrcv("FrameSetDataSet",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameSetName(self,name):
  args=((ValueType.Text,None,name),)
  rep=self.sndrcv("FrameSetName",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def FrameSetNumberByUniqueID(self,unique_id,new_number):
  args=((ValueType.Scalar,c_int64,unique_id),
        (ValueType.Scalar,c_int32,new_number),)
  rep=self.sndrcv("FrameSetNumberByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def FrameSetPlotType(self,new_plot_type):
  args=((ValueType.Scalar,c_int32,PlotType(new_plot_type).value),)
  rep=self.sndrcv("FrameSetPlotType",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def FrameSetPosAndSize(self,x,y,width,height):
  args=((ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),
        (ValueType.Scalar,c_double,width),
        (ValueType.Scalar,c_double,height),)
  rep=self.sndrcv("FrameSetPosAndSize",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def Geom2DLineSegmentCreate(self,position_coord_sys,x1,y1,x2,y2):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_double,x1),
        (ValueType.Scalar,c_double,y1),
        (ValueType.Scalar,c_double,x2),
        (ValueType.Scalar,c_double,y2),)
  rep=self.sndrcv("Geom2DLineSegmentCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def Geom2DMPolyCreate(self,position_coord_sys,num_polys,num_points_in_polylines__array):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_int32,num_polys),
        (ValueType.Array,c_int64,num_points_in_polylines__array),)
  rep=self.sndrcv("Geom2DMPolyCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def Geom2DMPolyGetPoint(self,gid,poly_num,point_index):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,poly_num),
        (ValueType.Scalar,c_int64,point_index),)
  rep=self.sndrcv("Geom2DMPolyGetPoint",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def Geom2DMPolySetPoint(self,gid,poly_num,point_index,x,y):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,poly_num),
        (ValueType.Scalar,c_int64,point_index),
        (ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),)
  rep=self.sndrcv("Geom2DMPolySetPoint",*args).Reply()
  self.chk(rep)
 def Geom2DMPolySetPolyline(self,gid,poly_num,x__array,y__array):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,poly_num),
        (ValueType.Array,c_double,x__array),
        (ValueType.Array,c_double,y__array),)
  rep=self.sndrcv("Geom2DMPolySetPolyline",*args).Reply()
  self.chk(rep)
 def Geom2DPolylineCreate(self,position_coord_sys,pts_x__array,pts_y__array,num_pts):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Array,c_double,pts_x__array),
        (ValueType.Array,c_double,pts_y__array),
        (ValueType.Scalar,c_int64,num_pts),)
  rep=self.sndrcv("Geom2DPolylineCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def Geom2DPolylineGetPoint(self,gid,point_index):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int64,point_index),)
  rep=self.sndrcv("Geom2DPolylineGetPoint",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def Geom2DPolylineSetPoint(self,gid,point_index,x,y):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int64,point_index),
        (ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),)
  rep=self.sndrcv("Geom2DPolylineSetPoint",*args).Reply()
  self.chk(rep)
 def Geom3DLineSegmentCreate(self,x1,y1,z1,x2,y2,z2):
  args=((ValueType.Scalar,c_double,x1),
        (ValueType.Scalar,c_double,y1),
        (ValueType.Scalar,c_double,z1),
        (ValueType.Scalar,c_double,x2),
        (ValueType.Scalar,c_double,y2),
        (ValueType.Scalar,c_double,z2),)
  rep=self.sndrcv("Geom3DLineSegmentCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def Geom3DMPolyCreate(self,num_polys,num_points_in_polylines__array):
  args=((ValueType.Scalar,c_int32,num_polys),
        (ValueType.Array,c_int64,num_points_in_polylines__array),)
  rep=self.sndrcv("Geom3DMPolyCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def Geom3DMPolyGetPoint(self,gid,poly_num,point_index):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,poly_num),
        (ValueType.Scalar,c_int64,point_index),)
  rep=self.sndrcv("Geom3DMPolyGetPoint",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def Geom3DMPolySetPoint(self,gid,poly_num,point_index,x,y,z):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,poly_num),
        (ValueType.Scalar,c_int64,point_index),
        (ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),
        (ValueType.Scalar,c_double,z),)
  rep=self.sndrcv("Geom3DMPolySetPoint",*args).Reply()
  self.chk(rep)
 def Geom3DMPolySetPolyline(self,gid,poly_num,x__array,y__array,z__array):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,poly_num),
        (ValueType.Array,c_double,x__array),
        (ValueType.Array,c_double,y__array),
        (ValueType.Array,c_double,z__array),)
  rep=self.sndrcv("Geom3DMPolySetPolyline",*args).Reply()
  self.chk(rep)
 def Geom3DPolylineCreate(self,pts_x__array,pts_y__array,pts_z__array,num_pts):
  args=((ValueType.Array,c_double,pts_x__array),
        (ValueType.Array,c_double,pts_y__array),
        (ValueType.Array,c_double,pts_z__array),
        (ValueType.Scalar,c_int64,num_pts),)
  rep=self.sndrcv("Geom3DPolylineCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def Geom3DPolylineGetPoint(self,gid,point_index):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int64,point_index),)
  rep=self.sndrcv("Geom3DPolylineGetPoint",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def Geom3DPolylineSetPoint(self,gid,point_index,x,y,z):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int64,point_index),
        (ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),
        (ValueType.Scalar,c_double,z),)
  rep=self.sndrcv("Geom3DPolylineSetPoint",*args).Reply()
  self.chk(rep)
 def GeomArcCreate(self,position_coord_sys,center_x,center_y,radius,start_angle,end_angle):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_double,center_x),
        (ValueType.Scalar,c_double,center_y),
        (ValueType.Scalar,c_double,radius),
        (ValueType.Scalar,c_double,start_angle),
        (ValueType.Scalar,c_double,end_angle),)
  rep=self.sndrcv("GeomArcCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomArrowheadGetAngle(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomArrowheadGetAngle",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def GeomArrowheadGetAttach(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomArrowheadGetAttach",*args).Reply()
  self.chk(rep)
  return ArrowheadAttachment(rep.Args(0).Int32Value())
 def GeomArrowheadGetSize(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomArrowheadGetSize",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def GeomArrowheadGetStyle(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomArrowheadGetStyle",*args).Reply()
  self.chk(rep)
  return ArrowheadStyle(rep.Args(0).Int32Value())
 def GeomArrowheadSetAngle(self,gid,arrowhead_angle):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,arrowhead_angle),)
  rep=self.sndrcv("GeomArrowheadSetAngle",*args).Reply()
  self.chk(rep)
 def GeomArrowheadSetAttach(self,gid,arrowhead_attachment):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,ArrowheadAttachment(arrowhead_attachment).value),)
  rep=self.sndrcv("GeomArrowheadSetAttach",*args).Reply()
  self.chk(rep)
 def GeomArrowheadSetSize(self,gid,arrowhead_size):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,arrowhead_size),)
  rep=self.sndrcv("GeomArrowheadSetSize",*args).Reply()
  self.chk(rep)
 def GeomArrowheadSetStyle(self,gid,arrowhead_style):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,ArrowheadStyle(arrowhead_style).value),)
  rep=self.sndrcv("GeomArrowheadSetStyle",*args).Reply()
  self.chk(rep)
 def GeomCircleCreate(self,position_coord_sys,center_x,center_y,radius):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_double,center_x),
        (ValueType.Scalar,c_double,center_y),
        (ValueType.Scalar,c_double,radius),)
  rep=self.sndrcv("GeomCircleCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomCircleGetRadius(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomCircleGetRadius",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def GeomCircleSetRadius(self,gid,radius):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,radius),)
  rep=self.sndrcv("GeomCircleSetRadius",*args).Reply()
  self.chk(rep)
 def GeomDelete(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomDelete",*args).Reply()
  self.chk(rep)
 def GeomEllipseCreate(self,position_coord_sys,center_x,center_y,h_axis,v_axis):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_double,center_x),
        (ValueType.Scalar,c_double,center_y),
        (ValueType.Scalar,c_double,h_axis),
        (ValueType.Scalar,c_double,v_axis),)
  rep=self.sndrcv("GeomEllipseCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomEllipseGetNumPoints(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomEllipseGetNumPoints",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def GeomEllipseGetSize(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomEllipseGetSize",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def GeomEllipseSetNumPoints(self,gid,num_ellipse_pts):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,num_ellipse_pts),)
  rep=self.sndrcv("GeomEllipseSetNumPoints",*args).Reply()
  self.chk(rep)
 def GeomEllipseSetSize(self,gid,h_axis,v_axis):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,h_axis),
        (ValueType.Scalar,c_double,v_axis),)
  rep=self.sndrcv("GeomEllipseSetSize",*args).Reply()
  self.chk(rep)
 def GeomGetAnchorPos(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetAnchorPos",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def GeomGetBase(self):
  rep=self.sndrcv("GeomGetBase").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomGetClipping(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetClipping",*args).Reply()
  self.chk(rep)
  return Clipping(rep.Args(0).Int32Value())
 def GeomGetColor(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetColor",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def GeomGetDrawOrder(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetDrawOrder",*args).Reply()
  self.chk(rep)
  return DrawOrder(rep.Args(0).Int32Value())
 def GeomGetFillColor(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetFillColor",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def GeomGetIsFilled(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetIsFilled",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def GeomGetLinePattern(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetLinePattern",*args).Reply()
  self.chk(rep)
  return LinePattern(rep.Args(0).Int32Value())
 def GeomGetLineThickness(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetLineThickness",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def GeomGetMacroFunctionCmd(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetMacroFunctionCmd",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def GeomGetNext(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetNext",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomGetPatternLength(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetPatternLength",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def GeomGetPositionCoordSys(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetPositionCoordSys",*args).Reply()
  self.chk(rep)
  return CoordSys(rep.Args(0).Int32Value())
 def GeomGetPrev(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetPrev",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomGetScope(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetScope",*args).Reply()
  self.chk(rep)
  return Scope(rep.Args(0).Int32Value())
 def GeomGetType(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetType",*args).Reply()
  self.chk(rep)
  return GeomForm(rep.Args(0).Int32Value())
 def GeomGetZoneOrMap(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomGetZoneOrMap",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def GeomImageCreate(self,f_name,corner_x,corner_y,size):
  args=((ValueType.Text,None,f_name),
        (ValueType.Scalar,c_double,corner_x),
        (ValueType.Scalar,c_double,corner_y),
        (ValueType.Scalar,c_double,size),)
  rep=self.sndrcv("GeomImageCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomImageGetFileName(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomImageGetFileName",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def GeomImageGetImage(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomImageGetImage",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value(),
   rep.Args(1).Int32Value(),
   copy(rep.Args(2).Uint8Array()))
 def GeomImageGetRawSize(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomImageGetRawSize",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def GeomImageGetResizeFilter(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomImageGetResizeFilter",*args).Reply()
  self.chk(rep)
  return ImageResizeFilter(rep.Args(0).Int32Value())
 def GeomImageGetSize(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomImageGetSize",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def GeomImageGetUseRatio(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomImageGetUseRatio",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def GeomImageResetAspectRatio(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomImageResetAspectRatio",*args).Reply()
  self.chk(rep)
 def GeomImageSetHeight(self,gid,height):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,height),)
  rep=self.sndrcv("GeomImageSetHeight",*args).Reply()
  self.chk(rep)
 def GeomImageSetResizeFilter(self,gid,resize_filter):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,ImageResizeFilter(resize_filter).value),)
  rep=self.sndrcv("GeomImageSetResizeFilter",*args).Reply()
  self.chk(rep)
 def GeomImageSetUseRatio(self,gid,maintain_aspect_ratio):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_bool,maintain_aspect_ratio),)
  rep=self.sndrcv("GeomImageSetUseRatio",*args).Reply()
  self.chk(rep)
 def GeomImageSetWidth(self,gid,width):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,width),)
  rep=self.sndrcv("GeomImageSetWidth",*args).Reply()
  self.chk(rep)
 def GeomIsAttached(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomIsAttached",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def GeomIsValid(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomIsValid",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def GeomMPolyGetPointCount(self,gid,poly_num):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,poly_num),)
  rep=self.sndrcv("GeomMPolyGetPointCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomMPolyGetPolylineCnt(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomMPolyGetPolylineCnt",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomPolyGetPointCount(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomPolyGetPointCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomRectangleCreate(self,position_coord_sys,corner_x,corner_y,width,height):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_double,corner_x),
        (ValueType.Scalar,c_double,corner_y),
        (ValueType.Scalar,c_double,width),
        (ValueType.Scalar,c_double,height),)
  rep=self.sndrcv("GeomRectangleCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomRectangleGetSize(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomRectangleGetSize",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def GeomRectangleSetSize(self,gid,width,height):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,width),
        (ValueType.Scalar,c_double,height),)
  rep=self.sndrcv("GeomRectangleSetSize",*args).Reply()
  self.chk(rep)
 def GeomSetAnchorPos(self,gid,x_pos,y_pos,z_pos):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,x_pos),
        (ValueType.Scalar,c_double,y_pos),
        (ValueType.Scalar,c_double,z_pos),)
  rep=self.sndrcv("GeomSetAnchorPos",*args).Reply()
  self.chk(rep)
 def GeomSetAttached(self,gid,attached):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_bool,attached),)
  rep=self.sndrcv("GeomSetAttached",*args).Reply()
  self.chk(rep)
 def GeomSetClipping(self,gid,clipping):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,Clipping(clipping).value),)
  rep=self.sndrcv("GeomSetClipping",*args).Reply()
  self.chk(rep)
 def GeomSetColor(self,gid,color):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,color),)
  rep=self.sndrcv("GeomSetColor",*args).Reply()
  self.chk(rep)
 def GeomSetDrawOrder(self,gid,draw_order):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,DrawOrder(draw_order).value),)
  rep=self.sndrcv("GeomSetDrawOrder",*args).Reply()
  self.chk(rep)
 def GeomSetFillColor(self,gid,fill_color):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,fill_color),)
  rep=self.sndrcv("GeomSetFillColor",*args).Reply()
  self.chk(rep)
 def GeomSetIsFilled(self,gid,is_filled):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_bool,is_filled),)
  rep=self.sndrcv("GeomSetIsFilled",*args).Reply()
  self.chk(rep)
 def GeomSetLinePattern(self,gid,line_pattern):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,LinePattern(line_pattern).value),)
  rep=self.sndrcv("GeomSetLinePattern",*args).Reply()
  self.chk(rep)
 def GeomSetLineThickness(self,gid,line_thickness):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,line_thickness),)
  rep=self.sndrcv("GeomSetLineThickness",*args).Reply()
  self.chk(rep)
 def GeomSetMacroFunctionCmd(self,gid,command):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Text,None,command),)
  rep=self.sndrcv("GeomSetMacroFunctionCmd",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def GeomSetPatternLength(self,gid,pattern_length):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,pattern_length),)
  rep=self.sndrcv("GeomSetPatternLength",*args).Reply()
  self.chk(rep)
 def GeomSetPositionCoordSys(self,gid,coord_sys):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,CoordSys(coord_sys).value),)
  rep=self.sndrcv("GeomSetPositionCoordSys",*args).Reply()
  self.chk(rep)
 def GeomSetScope(self,gid,scope):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,Scope(scope).value),)
  rep=self.sndrcv("GeomSetScope",*args).Reply()
  self.chk(rep)
 def GeomSetZoneOrMap(self,gid,zone_or_map):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_int32,zone_or_map),)
  rep=self.sndrcv("GeomSetZoneOrMap",*args).Reply()
  self.chk(rep)
 def GeomSquareCreate(self,position_coord_sys,corner_x,corner_y,size):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_double,corner_x),
        (ValueType.Scalar,c_double,corner_y),
        (ValueType.Scalar,c_double,size),)
  rep=self.sndrcv("GeomSquareCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def GeomSquareGetSize(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("GeomSquareGetSize",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def GeomSquareSetSize(self,gid,size):
  args=((ValueType.Scalar,c_int64,gid),
        (ValueType.Scalar,c_double,size),)
  rep=self.sndrcv("GeomSquareSetSize",*args).Reply()
  self.chk(rep)
 def GetBasePath(self,f_name):
  args=((ValueType.Text,None,f_name),)
  rep=self.sndrcv("GetBasePath",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def GetBoundingBoxOfAllFrames(self):
  rep=self.sndrcv("GetBoundingBoxOfAllFrames").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value(),
   rep.Args(3).Float64Value())
 def GetCurLayoutFName(self):
  rep=self.sndrcv("GetCurLayoutFName").Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def GetDefaultExportImageWidth(self,export_format,export_region):
  args=((ValueType.Scalar,c_int32,ExportFormat(export_format).value),
        (ValueType.Scalar,c_int32,ExportRegion(export_region).value),)
  rep=self.sndrcv("GetDefaultExportImageWidth",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def GetExportImageHeight(self,width,region):
  args=((ValueType.Scalar,c_int32,width),
        (ValueType.Scalar,c_int32,ExportRegion(region).value),)
  rep=self.sndrcv("GetExportImageHeight",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def GetNextNiceIncDecValue(self,start_value,min_value,max_value,preferred_divisions,is_increasing):
  args=((ValueType.Scalar,c_double,start_value),
        (ValueType.Scalar,c_double,min_value),
        (ValueType.Scalar,c_double,max_value),
        (ValueType.Scalar,c_int64,preferred_divisions),
        (ValueType.Scalar,c_bool,is_increasing),)
  rep=self.sndrcv("GetNextNiceIncDecValue",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def GetNextUniqueID(self):
  rep=self.sndrcv("GetNextUniqueID").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ImageBitmapCreateX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ImageBitmapCreateX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ImageBitmapDestroy(self):
  rep=self.sndrcv("ImageBitmapDestroy").Reply()
  self.chk(rep)
 def ImageGetColorTable(self,red__array,green__array,blue__array):
  args=((ValueType.Array,c_uint8,red__array),
        (ValueType.Array,c_uint8,green__array),
        (ValueType.Array,c_uint8,blue__array),)
  rep=self.sndrcv("ImageGetColorTable",*args).Reply()
  self.chk(rep)
  red__array[:] = cast(byref(rep.Args(0).Uint8Array()), POINTER(type(red__array))).contents[:]
  green__array[:] = cast(byref(rep.Args(1).Uint8Array()), POINTER(type(green__array))).contents[:]
  blue__array[:] = cast(byref(rep.Args(2).Uint8Array()), POINTER(type(blue__array))).contents[:]
 def ImageGetDimensions(self):
  rep=self.sndrcv("ImageGetDimensions").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value(),
   rep.Args(1).Int32Value())
 def ImageIndexedBitmapCreate(self,region,red_color_table__array,green_color_table__array,blue_color_table__array):
  args=((ValueType.Scalar,c_int32,BitDumpRegion(region).value),
        (ValueType.Array,c_uint8,red_color_table__array),
        (ValueType.Array,c_uint8,green_color_table__array),
        (ValueType.Array,c_uint8,blue_color_table__array),)
  rep=self.sndrcv("ImageIndexedBitmapCreate",*args).Reply()
  self.chk(rep)
  red_color_table__array[:] = cast(byref(rep.Args(0).Uint8Array()), POINTER(type(red_color_table__array))).contents[:]
  green_color_table__array[:] = cast(byref(rep.Args(1).Uint8Array()), POINTER(type(green_color_table__array))).contents[:]
  blue_color_table__array[:] = cast(byref(rep.Args(2).Uint8Array()), POINTER(type(blue_color_table__array))).contents[:]
  return (rep.Status() == Status.Success)
 def ImageIndexedGetScanLine(self,scan_line,rgb_index__array):
  args=((ValueType.Scalar,c_int32,scan_line),
        (ValueType.Array,c_uint8,rgb_index__array),)
  rep=self.sndrcv("ImageIndexedGetScanLine",*args).Reply()
  self.chk(rep)
  rgb_index__array[:] = cast(byref(rep.Args(0).Uint8Array()), POINTER(type(rgb_index__array))).contents[:]
  return (rep.Status() == Status.Success)
 def ImageRGBBitmapCreate(self,region):
  args=((ValueType.Scalar,c_int32,BitDumpRegion(region).value),)
  rep=self.sndrcv("ImageRGBBitmapCreate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ImageRGBGetScanLine(self,scan_line,red__array,green__array,blue__array):
  args=((ValueType.Scalar,c_int32,scan_line),
        (ValueType.Array,c_uint8,red__array),
        (ValueType.Array,c_uint8,green__array),
        (ValueType.Array,c_uint8,blue__array),)
  rep=self.sndrcv("ImageRGBGetScanLine",*args).Reply()
  self.chk(rep)
  red__array[:] = cast(byref(rep.Args(0).Uint8Array()), POINTER(type(red__array))).contents[:]
  green__array[:] = cast(byref(rep.Args(1).Uint8Array()), POINTER(type(green__array))).contents[:]
  blue__array[:] = cast(byref(rep.Args(2).Uint8Array()), POINTER(type(blue__array))).contents[:]
  return (rep.Status() == Status.Success)
 def ImportAddConverter(self,converter_callback,converter_name,f_name_extension):
  args=((ValueType.Address,c_uint64,getattr(converter_callback,'value',converter_callback)),
        (ValueType.Text,None,converter_name),
        (ValueType.Text,None,f_name_extension),)
  rep=self.sndrcv("ImportAddConverter",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ImportAddLoader(self,loader_callback,data_set_loader_name,loader_selected_callback,instruction_override_callback):
  args=((ValueType.Address,c_uint64,getattr(loader_callback,'value',loader_callback)),
        (ValueType.Text,None,data_set_loader_name),
        (ValueType.Address,c_uint64,getattr(loader_selected_callback,'value',loader_selected_callback)),
        (ValueType.Address,c_uint64,getattr(instruction_override_callback,'value',instruction_override_callback)),)
  rep=self.sndrcv("ImportAddLoader",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ImportAddLoaderX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ImportAddLoaderX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ImportGetLoaderInstr(self):
  rep=self.sndrcv("ImportGetLoaderInstr").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)),
   self.read_ptr(rep.Args(1)))
 def ImportGetLoaderInstrByNum(self,index):
  args=((ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("ImportGetLoaderInstrByNum",*args).Reply()
  self.chk(rep)
  return (
   self.read_text(rep.Args(0)),
   self.read_ptr(rep.Args(1)))
 def ImportGetLoaderInstrCount(self):
  rep=self.sndrcv("ImportGetLoaderInstrCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ImportResetLoaderInstr(self,data_set_loader_name,instructions):
  args=((ValueType.Text,None,data_set_loader_name),
        (ValueType.Address,c_uint64,getattr(instructions,'value',instructions)),)
  rep=self.sndrcv("ImportResetLoaderInstr",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ImportSetLoaderInstr(self,data_set_loader_name,instructions):
  args=((ValueType.Text,None,data_set_loader_name),
        (ValueType.Address,c_uint64,getattr(instructions,'value',instructions)),)
  rep=self.sndrcv("ImportSetLoaderInstr",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ImportWriteLoaderInstr(self,data_set_loader_name,instructions):
  args=((ValueType.Text,None,data_set_loader_name),
        (ValueType.Address,c_uint64,getattr(instructions,'value',instructions)),)
  rep=self.sndrcv("ImportWriteLoaderInstr",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def InterfaceGetBaseFontSize(self):
  rep=self.sndrcv("InterfaceGetBaseFontSize").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def InterfaceGetDotsPerInch(self):
  rep=self.sndrcv("InterfaceGetDotsPerInch").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def InterfaceSuspend(self,do_suspend):
  args=((ValueType.Scalar,c_bool,do_suspend),)
  rep=self.sndrcv("InterfaceSuspend",*args).Reply()
  self.chk(rep)
 def InterfaceWinAddPreMsgFn(self,pre_translate_message_proc):
  args=((ValueType.Address,c_uint64,getattr(pre_translate_message_proc,'value',pre_translate_message_proc)),)
  rep=self.sndrcv("InterfaceWinAddPreMsgFn",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def InternalDiagGetInfo(self,get_what):
  args=((ValueType.Scalar,c_int32,get_what),)
  rep=self.sndrcv("InternalDiagGetInfo",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def Interrupt(self):
  rep=self.sndrcv("Interrupt").Reply()
  self.chk(rep)
 def InterruptCheck(self):
  rep=self.sndrcv("InterruptCheck").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def InterruptIsSet(self):
  rep=self.sndrcv("InterruptIsSet").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def InverseDistInterpolation(self,source_zones,dest_zone,var_list,inv_dist_exponent,inv_dist_min_radius,interp_pt_selection,interp_n_points):
  args=((ValueType.Address,c_uint64,getattr(source_zones,'value',source_zones)),
        (ValueType.Scalar,c_int32,dest_zone),
        (ValueType.Address,c_uint64,getattr(var_list,'value',var_list)),
        (ValueType.Scalar,c_double,inv_dist_exponent),
        (ValueType.Scalar,c_double,inv_dist_min_radius),
        (ValueType.Scalar,c_int32,PtSelection(interp_pt_selection).value),
        (ValueType.Scalar,c_int32,interp_n_points),)
  rep=self.sndrcv("InverseDistInterpolation",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Krig(self,source_zones,dest_zone,var_list,krig_range,krig_zero_value,krig_drift,interp_pt_selection,interp_n_points):
  args=((ValueType.Address,c_uint64,getattr(source_zones,'value',source_zones)),
        (ValueType.Scalar,c_int32,dest_zone),
        (ValueType.Address,c_uint64,getattr(var_list,'value',var_list)),
        (ValueType.Scalar,c_double,krig_range),
        (ValueType.Scalar,c_double,krig_zero_value),
        (ValueType.Scalar,c_int32,Drift(krig_drift).value),
        (ValueType.Scalar,c_int32,PtSelection(interp_pt_selection).value),
        (ValueType.Scalar,c_int64,interp_n_points),)
  rep=self.sndrcv("Krig",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LastErrorMessage(self):
  rep=self.sndrcv("LastErrorMessage").Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def LastErrorMessageClear(self):
  rep=self.sndrcv("LastErrorMessageClear").Reply()
  self.chk(rep)
 def LastErrorMessageType(self):
  rep=self.sndrcv("LastErrorMessageType").Reply()
  self.chk(rep)
  return MessageBoxType(rep.Args(0).Int32Value())
 def LimitGetValue(self,limit_string):
  args=((ValueType.Text,None,limit_string),)
  rep=self.sndrcv("LimitGetValue",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def LineMapCopy(self,source_map,dest_map):
  args=((ValueType.Scalar,c_int32,source_map),
        (ValueType.Scalar,c_int32,dest_map),)
  rep=self.sndrcv("LineMapCopy",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LineMapCreate(self):
  rep=self.sndrcv("LineMapCreate").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LineMapDelete(self,maps_to_delete):
  args=((ValueType.Address,c_uint64,getattr(maps_to_delete,'value',maps_to_delete)),)
  rep=self.sndrcv("LineMapDelete",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LineMapGetActive(self):
  rep=self.sndrcv("LineMapGetActive").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def LineMapGetAssignment(self,line_map):
  args=((ValueType.Scalar,c_int32,line_map),)
  rep=self.sndrcv("LineMapGetAssignment",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int32Value(),
   rep.Args(1).Int32Value(),
   rep.Args(2).Int32Value(),
   rep.Args(3).Int32Value(),
   rep.Args(4).Int32Value(),
   FunctionDependency(rep.Args(5).Int32Value()))
 def LineMapGetCount(self):
  rep=self.sndrcv("LineMapGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def LineMapGetCountForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("LineMapGetCountForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def LineMapGetName(self,map):
  args=((ValueType.Scalar,c_int32,map),)
  rep=self.sndrcv("LineMapGetName",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def LineMapGetNameForFrame(self,frame_id,map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,map),)
  rep=self.sndrcv("LineMapGetNameForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def LineMapGetNumByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("LineMapGetNumByUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def LineMapGetUniqueID(self,line_map):
  args=((ValueType.Scalar,c_int32,line_map),)
  rep=self.sndrcv("LineMapGetUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def LineMapIsActive(self,line_map):
  args=((ValueType.Scalar,c_int32,line_map),)
  rep=self.sndrcv("LineMapIsActive",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def LineMapIsActiveForFrame(self,frame_id,line_map):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,line_map),)
  rep=self.sndrcv("LineMapIsActiveForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def LineMapSetActive(self,line_map_set,assign_modifier):
  args=((ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Scalar,c_int32,AssignOp(assign_modifier).value),)
  rep=self.sndrcv("LineMapSetActive",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetAssignment(self,attribute,line_map_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetAssignment",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetBarChart(self,attribute,line_map_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetBarChart",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetCurve(self,attribute,line_map_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetCurve",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetErrorBar(self,attribute,line_map_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetErrorBar",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetIndices(self,attribute,sub_attribute,line_map_set,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Text,None,sub_attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetIndices",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetLine(self,attribute,line_map_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetLine",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetName(self,line_map_set,new_name):
  args=((ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Text,None,new_name),)
  rep=self.sndrcv("LineMapSetName",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetSymbol(self,attribute,line_map_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetSymbol",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapSetSymbolShape(self,attribute,line_map_set,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LineMapSetSymbolShape",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineMapShiftToBottom(self,maps_to_shift):
  args=((ValueType.Address,c_uint64,getattr(maps_to_shift,'value',maps_to_shift)),)
  rep=self.sndrcv("LineMapShiftToBottom",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LineMapShiftToTop(self,maps_to_shift):
  args=((ValueType.Address,c_uint64,getattr(maps_to_shift,'value',maps_to_shift)),)
  rep=self.sndrcv("LineMapShiftToTop",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LineMapStyleGetArbValue(self,line_map,s1,s2,s3):
  args=((ValueType.Scalar,c_int32,line_map),
        (ValueType.Text,None,s1),
        (ValueType.Text,None,s2),
        (ValueType.Text,None,s3),)
  rep=self.sndrcv("LineMapStyleGetArbValue",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def LineMapStyleGetArbValueForFrame(self,frame_id,line_map,s1,s2,s3):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,line_map),
        (ValueType.Text,None,s1),
        (ValueType.Text,None,s2),
        (ValueType.Text,None,s3),)
  rep=self.sndrcv("LineMapStyleGetArbValueForFrame",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def LineMapStyleGetDoubleValue(self,line_map,s1,s2,s3):
  args=((ValueType.Scalar,c_int32,line_map),
        (ValueType.Text,None,s1),
        (ValueType.Text,None,s2),
        (ValueType.Text,None,s3),)
  rep=self.sndrcv("LineMapStyleGetDoubleValue",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def LinePlotLayerIsActive(self,layer_show_flag):
  args=((ValueType.Text,None,layer_show_flag),)
  rep=self.sndrcv("LinePlotLayerIsActive",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def LinePlotLayerIsActiveForFrame(self,frame_id,layer_show_flag):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Text,None,layer_show_flag),)
  rep=self.sndrcv("LinePlotLayerIsActiveForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def LinePlotLayerSetIsActive(self,layer_show_flag,turn_on_line_plot_layer):
  args=((ValueType.Text,None,layer_show_flag),
        (ValueType.Scalar,c_bool,turn_on_line_plot_layer),)
  rep=self.sndrcv("LinePlotLayerSetIsActive",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LineSegProbe(self,line_seg_probe_result,starting_position,ending_positions,num_ending_positions,i_cell,j_cell,k_cell,cur_zone,zones_to_search,vars_to_return,line_seg_probe_callback,client_data):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Array,c_double,starting_position),
        (ValueType.Array,c_double,ending_positions),
        (ValueType.Scalar,c_int64,num_ending_positions),
        (ValueType.Scalar,c_int64,i_cell),
        (ValueType.Scalar,c_int64,j_cell),
        (ValueType.Scalar,c_int64,k_cell),
        (ValueType.Scalar,c_int32,cur_zone),
        (ValueType.Address,c_uint64,getattr(zones_to_search,'value',zones_to_search)),
        (ValueType.Address,c_uint64,getattr(vars_to_return,'value',vars_to_return)),
        (ValueType.Address,c_uint64,getattr(line_seg_probe_callback,'value',line_seg_probe_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("LineSegProbe",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LineSegProbeGetFace(self,line_seg_probe_result,which_segment):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Scalar,c_int32,which_segment),)
  rep=self.sndrcv("LineSegProbeGetFace",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def LineSegProbeGetICell(self,line_seg_probe_result,which_segment):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Scalar,c_int32,which_segment),)
  rep=self.sndrcv("LineSegProbeGetICell",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def LineSegProbeGetJCell(self,line_seg_probe_result,which_segment):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Scalar,c_int32,which_segment),)
  rep=self.sndrcv("LineSegProbeGetJCell",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def LineSegProbeGetKCell(self,line_seg_probe_result,which_segment):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Scalar,c_int32,which_segment),)
  rep=self.sndrcv("LineSegProbeGetKCell",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def LineSegProbeGetStatus(self,line_seg_probe_result,which_segment):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Scalar,c_int32,which_segment),)
  rep=self.sndrcv("LineSegProbeGetStatus",*args).Reply()
  self.chk(rep)
  return ProbeStatus(rep.Args(0).Int32Value())
 def LineSegProbeGetVarValue(self,line_seg_probe_result,which_segment,var):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Scalar,c_int32,which_segment),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("LineSegProbeGetVarValue",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def LineSegProbeGetZone(self,line_seg_probe_result,which_segment):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),
        (ValueType.Scalar,c_int32,which_segment),)
  rep=self.sndrcv("LineSegProbeGetZone",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def LineSegProbeResultAlloc(self):
  rep=self.sndrcv("LineSegProbeResultAlloc").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def LineSegProbeResultClear(self,line_seg_probe_result):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),)
  rep=self.sndrcv("LineSegProbeResultClear",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def LineSegProbeResultDealloc(self,line_seg_probe_result):
  args=((ValueType.Address,c_uint64,line_seg_probe_result.contents.value),)
  rep=self.sndrcv("LineSegProbeResultDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def LineSegProbeResultGetCount(self,line_seg_probe_result):
  args=((ValueType.Address,c_uint64,getattr(line_seg_probe_result,'value',line_seg_probe_result)),)
  rep=self.sndrcv("LineSegProbeResultGetCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def LinearInterpolate(self,source_zones,dest_zone,var_list,linear_interp_const,linear_interp_mode):
  args=((ValueType.Address,c_uint64,getattr(source_zones,'value',source_zones)),
        (ValueType.Scalar,c_int32,dest_zone),
        (ValueType.Address,c_uint64,getattr(var_list,'value',var_list)),
        (ValueType.Scalar,c_double,linear_interp_const),
        (ValueType.Scalar,c_int32,LinearInterpMode(linear_interp_mode).value),)
  rep=self.sndrcv("LinearInterpolate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def LinkingGetValue(self,attribute,sub_attribute):
  args=((ValueType.Text,None,attribute),
        (ValueType.Text,None,sub_attribute),)
  rep=self.sndrcv("LinkingGetValue",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def LinkingSetValue(self,attribute,sub_attribute,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Text,None,sub_attribute),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("LinkingSetValue",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def LockFinish(self,add_on):
  args=((ValueType.Address,c_uint64,getattr(add_on,'value',add_on)),)
  rep=self.sndrcv("LockFinish",*args).Reply()
  self.chk(rep)
 def LockGetCount(self):
  rep=self.sndrcv("LockGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def LockGetCurrentOwnerName(self):
  rep=self.sndrcv("LockGetCurrentOwnerName").Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def LockIsOn(self):
  rep=self.sndrcv("LockIsOn").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def LockOff(self):
  rep=self.sndrcv("LockOff").Reply()
  self.chk(rep)
 def LockOn(self):
  rep=self.sndrcv("LockOn").Reply()
  self.chk(rep)
 def LockStart(self,add_on):
  args=((ValueType.Address,c_uint64,getattr(add_on,'value',add_on)),)
  rep=self.sndrcv("LockStart",*args).Reply()
  self.chk(rep)
 def MacroAddCommandCallback(self,command_processor_id_string,macro_command_callback):
  args=((ValueType.Text,None,command_processor_id_string),
        (ValueType.Address,c_uint64,getattr(macro_command_callback,'value',macro_command_callback)),)
  rep=self.sndrcv("MacroAddCommandCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroExecuteCommand(self,command):
  args=((ValueType.Text,None,command),)
  rep=self.sndrcv("MacroExecuteCommand",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroExecuteExtendedCommand(self,command_processor_id,command,raw_data):
  args=((ValueType.Text,None,command_processor_id),
        (ValueType.Text,None,command),
        (ValueType.Text,None,raw_data),)
  rep=self.sndrcv("MacroExecuteExtendedCommand",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroFunctionExists(self,function_name):
  args=((ValueType.Text,None,function_name),)
  rep=self.sndrcv("MacroFunctionExists",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroFunctionGetAcceleratorKey(self,index):
  args=((ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("MacroFunctionGetAcceleratorKey",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Text()[0]
 def MacroFunctionGetCount(self):
  rep=self.sndrcv("MacroFunctionGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def MacroFunctionGetName(self,index):
  args=((ValueType.Scalar,c_int32,index),)
  rep=self.sndrcv("MacroFunctionGetName",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def MacroGetDebugger(self):
  rep=self.sndrcv("MacroGetDebugger").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def MacroIsBatchModeActive(self):
  rep=self.sndrcv("MacroIsBatchModeActive").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def MacroIsRecordingActive(self):
  rep=self.sndrcv("MacroIsRecordingActive").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def MacroRecordExtComRaw(self,command_processor_id_string,command,raw_data):
  args=((ValueType.Text,None,command_processor_id_string),
        (ValueType.Text,None,command),
        (ValueType.Text,None,raw_data),)
  rep=self.sndrcv("MacroRecordExtComRaw",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroRecordExtCommand(self,command_processor_id_string,command):
  args=((ValueType.Text,None,command_processor_id_string),
        (ValueType.Text,None,command),)
  rep=self.sndrcv("MacroRecordExtCommand",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroRecordRawCommand(self,command):
  args=((ValueType.Text,None,command),)
  rep=self.sndrcv("MacroRecordRawCommand",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroRunFile(self,f_name):
  args=((ValueType.Text,None,f_name),)
  rep=self.sndrcv("MacroRunFile",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroRunFunction(self,quick_macro_name,macro_parameters):
  args=((ValueType.Text,None,quick_macro_name),
        (ValueType.Text,None,macro_parameters),)
  rep=self.sndrcv("MacroRunFunction",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MacroSetMacroVar(self,macro_var,value_string):
  args=((ValueType.Text,None,macro_var),
        (ValueType.Text,None,value_string),)
  rep=self.sndrcv("MacroSetMacroVar",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def MainlineInvoke(self,job,job_data):
  args=((ValueType.Address,c_uint64,getattr(job,'value',job)),
        (ValueType.ArbParam,None,job_data),)
  rep=self.sndrcv("MainlineInvoke",*args).Reply()
  self.chk(rep)
 def MenuActivate(self,activate):
  args=((ValueType.Scalar,c_bool,activate),)
  rep=self.sndrcv("MenuActivate",*args).Reply()
  self.chk(rep)
 def MenuAddStatusLineHelp(self,menu_item,status_line_help):
  args=((ValueType.Address,c_uint64,getattr(menu_item,'value',menu_item)),
        (ValueType.Text,None,status_line_help),)
  rep=self.sndrcv("MenuAddStatusLineHelp",*args).Reply()
  self.chk(rep)
 def MenuClearAll(self):
  rep=self.sndrcv("MenuClearAll").Reply()
  self.chk(rep)
 def MenuDelete(self,menu_item_ptr):
  args=((ValueType.Address,c_uint64,menu_item_ptr.contents.value),)
  rep=self.sndrcv("MenuDelete",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def MenuGetMain(self):
  rep=self.sndrcv("MenuGetMain").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def MenuGetStandard(self,standard_menu):
  args=((ValueType.Scalar,c_int32,StandardMenu(standard_menu).value),)
  rep=self.sndrcv("MenuGetStandard",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def MenuInsertSeparator(self,parent_menu,insert_pos):
  args=((ValueType.Address,c_uint64,getattr(parent_menu,'value',parent_menu)),
        (ValueType.Scalar,c_int32,insert_pos),)
  rep=self.sndrcv("MenuInsertSeparator",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def MenuInsertStandard(self,parent_menu,insert_pos,standard_menu):
  args=((ValueType.Address,c_uint64,getattr(parent_menu,'value',parent_menu)),
        (ValueType.Scalar,c_int32,insert_pos),
        (ValueType.Scalar,c_int32,StandardMenu(standard_menu).value),)
  rep=self.sndrcv("MenuInsertStandard",*args).Reply()
  self.chk(rep)
 def MenuInsertSubMenu(self,parent_menu,insert_pos,sub_menu_label):
  args=((ValueType.Address,c_uint64,getattr(parent_menu,'value',parent_menu)),
        (ValueType.Scalar,c_int32,insert_pos),
        (ValueType.Text,None,sub_menu_label),)
  rep=self.sndrcv("MenuInsertSubMenu",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def MenuInsertToggle(self,parent_menu,insert_pos,toggle_label,activate_callback,activate_client_data,get_toggle_state_callback,get_toggle_state_client_data):
  args=((ValueType.Address,c_uint64,getattr(parent_menu,'value',parent_menu)),
        (ValueType.Scalar,c_int32,insert_pos),
        (ValueType.Text,None,toggle_label),
        (ValueType.Address,c_uint64,getattr(activate_callback,'value',activate_callback)),
        (ValueType.ArbParam,None,activate_client_data),
        (ValueType.Address,c_uint64,getattr(get_toggle_state_callback,'value',get_toggle_state_callback)),
        (ValueType.ArbParam,None,get_toggle_state_client_data),)
  rep=self.sndrcv("MenuInsertToggle",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def MenuRegisterSensitivityCallback(self,menu_item,get_sensitivity_callback,get_sensitivity_client_data):
  args=((ValueType.Address,c_uint64,getattr(menu_item,'value',menu_item)),
        (ValueType.Address,c_uint64,getattr(get_sensitivity_callback,'value',get_sensitivity_callback)),
        (ValueType.ArbParam,None,get_sensitivity_client_data),)
  rep=self.sndrcv("MenuRegisterSensitivityCallback",*args).Reply()
  self.chk(rep)
 def MouseGetCurrentMode(self):
  rep=self.sndrcv("MouseGetCurrentMode").Reply()
  self.chk(rep)
  return MouseButtonMode(rep.Args(0).Int32Value())
 def MouseIsValidMode(self,mouse_mode):
  args=((ValueType.Scalar,c_int32,MouseButtonMode(mouse_mode).value),)
  rep=self.sndrcv("MouseIsValidMode",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def MouseSetMode(self,mouse_mode):
  args=((ValueType.Scalar,c_int32,MouseButtonMode(mouse_mode).value),)
  rep=self.sndrcv("MouseSetMode",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def NewLayout(self):
  rep=self.sndrcv("NewLayout").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def OEMDataSetCreate(self,loader_name,data_set_title,var_names,reset_style):
  args=((ValueType.Text,None,loader_name),
        (ValueType.Text,None,data_set_title),
        (ValueType.Address,c_uint64,getattr(var_names,'value',var_names)),
        (ValueType.Scalar,c_bool,reset_style),)
  rep=self.sndrcv("OEMDataSetCreate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def OnIdleQueueAddCallback(self,callback,client_data):
  args=((ValueType.Address,c_uint64,getattr(callback,'value',callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("OnIdleQueueAddCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def OnIdleQueueRemoveCallback(self,callback,client_data):
  args=((ValueType.Address,c_uint64,getattr(callback,'value',callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("OnIdleQueueRemoveCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def OpenLayout(self,f_name,alt_instructions,append):
  args=((ValueType.Text,None,f_name),
        (ValueType.Address,c_uint64,getattr(alt_instructions,'value',alt_instructions)),
        (ValueType.Scalar,c_bool,append),)
  rep=self.sndrcv("OpenLayout",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def OpenLayoutX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("OpenLayoutX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PageClear(self):
  rep=self.sndrcv("PageClear").Reply()
  self.chk(rep)
 def PageCreateNew(self):
  rep=self.sndrcv("PageCreateNew").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PageDelete(self):
  rep=self.sndrcv("PageDelete").Reply()
  self.chk(rep)
 def PageGetCount(self):
  rep=self.sndrcv("PageGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PageGetName(self):
  rep=self.sndrcv("PageGetName").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def PageGetPosByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("PageGetPosByUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PageGetUniqueID(self):
  rep=self.sndrcv("PageGetUniqueID").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def PageSetCurrentByName(self,page_name):
  args=((ValueType.Text,None,page_name),)
  rep=self.sndrcv("PageSetCurrentByName",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PageSetCurrentByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("PageSetCurrentByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PageSetCurrentToNext(self):
  rep=self.sndrcv("PageSetCurrentToNext").Reply()
  self.chk(rep)
 def PageSetCurrentToPrev(self):
  rep=self.sndrcv("PageSetCurrentToPrev").Reply()
  self.chk(rep)
 def PageSetName(self,name):
  args=((ValueType.Text,None,name),)
  rep=self.sndrcv("PageSetName",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def PaperGetDimensions(self):
  rep=self.sndrcv("PaperGetDimensions").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def ParentLockFinish(self):
  rep=self.sndrcv("ParentLockFinish").Reply()
  self.chk(rep)
 def ParentLockStart(self,shutdown_implicit_recording):
  args=((ValueType.Scalar,c_bool,shutdown_implicit_recording),)
  rep=self.sndrcv("ParentLockStart",*args).Reply()
  self.chk(rep)
 def PickAddAll(self,object_type):
  args=((ValueType.Scalar,c_int32,PickObjects(object_type).value),)
  rep=self.sndrcv("PickAddAll",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickAddAllInRectX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("PickAddAllInRectX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickAddAtPositionX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("PickAddAtPositionX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickAddFrameByUniqueID(self,collecting_objects,unique_id):
  args=((ValueType.Scalar,c_bool,collecting_objects),
        (ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("PickAddFrameByUniqueID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickAddLineMaps(self,collecting_objects,line_map_set):
  args=((ValueType.Scalar,c_bool,collecting_objects),
        (ValueType.Address,c_uint64,getattr(line_map_set,'value',line_map_set)),)
  rep=self.sndrcv("PickAddLineMaps",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickAddZones(self,collecting_objects,zone_set):
  args=((ValueType.Scalar,c_bool,collecting_objects),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),)
  rep=self.sndrcv("PickAddZones",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickClear(self):
  rep=self.sndrcv("PickClear").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickCopy(self):
  rep=self.sndrcv("PickCopy").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickCut(self):
  rep=self.sndrcv("PickCut").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickDeselect(self,pick_list_item):
  args=((ValueType.Scalar,c_int32,pick_list_item),)
  rep=self.sndrcv("PickDeselect",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickDeselectAll(self):
  rep=self.sndrcv("PickDeselectAll").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickEdit(self,action):
  args=((ValueType.Text,None,action),)
  rep=self.sndrcv("PickEdit",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickGeom(self,gid):
  args=((ValueType.Scalar,c_int64,gid),)
  rep=self.sndrcv("PickGeom",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickIsSnapToGridAllowed(self):
  rep=self.sndrcv("PickIsSnapToGridAllowed").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def PickIsSnapToPaperAllowed(self):
  rep=self.sndrcv("PickIsSnapToPaperAllowed").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def PickListGetAxisKind(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetAxisKind",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Text()[0]
 def PickListGetAxisNumber(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetAxisNumber",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickListGetAxisSubObject(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetAxisSubObject",*args).Reply()
  self.chk(rep)
  return AxisSubObject(rep.Args(0).Int32Value())
 def PickListGetCount(self):
  rep=self.sndrcv("PickListGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickListGetFrameName(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetFrameName",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def PickListGetFrameUniqueID(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetFrameUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def PickListGetGeom(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetGeom",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def PickListGetGeomInfo(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetGeomInfo",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int32Value(),
   rep.Args(1).Int64Value())
 def PickListGetIsoSurfaceGroup(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetIsoSurfaceGroup",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickListGetLabelsContourGroup(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetLabelsContourGroup",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickListGetLegendContourGroup(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetLegendContourGroup",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickListGetLineMapIndex(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetLineMapIndex",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def PickListGetLineMapNumber(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetLineMapNumber",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickListGetSliceGroup(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetSliceGroup",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickListGetText(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetText",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def PickListGetType(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetType",*args).Reply()
  self.chk(rep)
  return PickObjects(rep.Args(0).Int32Value())
 def PickListGetZoneIndices(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetZoneIndices",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value())
 def PickListGetZoneNumber(self,pick_list_index):
  args=((ValueType.Scalar,c_int32,pick_list_index),)
  rep=self.sndrcv("PickListGetZoneNumber",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def PickMagnify(self,mag_factor):
  args=((ValueType.Scalar,c_double,mag_factor),)
  rep=self.sndrcv("PickMagnify",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickPaste(self):
  rep=self.sndrcv("PickPaste").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickPop(self):
  rep=self.sndrcv("PickPop").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickPush(self):
  rep=self.sndrcv("PickPush").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickShift(self,dx_paper,dy_paper,pointer_style):
  args=((ValueType.Scalar,c_double,dx_paper),
        (ValueType.Scalar,c_double,dy_paper),
        (ValueType.Scalar,c_int32,PointerStyle(pointer_style).value),)
  rep=self.sndrcv("PickShift",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PickText(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("PickText",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PleaseWait(self,wait_message,do_wait):
  args=((ValueType.Text,None,wait_message),
        (ValueType.Scalar,c_bool,do_wait),)
  rep=self.sndrcv("PleaseWait",*args).Reply()
  self.chk(rep)
 def PopMainProcessWindow(self):
  rep=self.sndrcv("PopMainProcessWindow").Reply()
  self.chk(rep)
 def Print(self):
  rep=self.sndrcv("Print").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PrintSetup(self,attribute,sub_attribute,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Text,None,sub_attribute),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("PrintSetup",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ProbeAllowCOBs(self):
  rep=self.sndrcv("ProbeAllowCOBs").Reply()
  self.chk(rep)
 def ProbeAtFieldIndexX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ProbeAtFieldIndexX",*args).Reply()
  self.chk(rep)
 def ProbeAtFieldPositionX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ProbeAtFieldPositionX",*args).Reply()
  self.chk(rep)
 def ProbeAtLineIndexX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ProbeAtLineIndexX",*args).Reply()
  self.chk(rep)
 def ProbeAtLinePositionX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ProbeAtLinePositionX",*args).Reply()
  self.chk(rep)
 def ProbeAtPosSequenceBeginX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ProbeAtPosSequenceBeginX",*args).Reply()
  self.chk(rep)
 def ProbeAtPosSequenceEnd(self):
  rep=self.sndrcv("ProbeAtPosSequenceEnd").Reply()
  self.chk(rep)
 def ProbeAtPosition(self,x,y,z,i_cell,j_cell,k_cell,plane,cur_zone,start_with_local_cell,v_value__array,source_zones,search_volume,get_zone_only,get_nearest_point):
  args=((ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),
        (ValueType.Scalar,c_double,z),
        (ValueType.Scalar,c_int64,i_cell),
        (ValueType.Scalar,c_int64,j_cell),
        (ValueType.Scalar,c_int64,k_cell),
        (ValueType.Scalar,c_int32,IJKPlanes(plane).value),
        (ValueType.Scalar,c_int32,cur_zone),
        (ValueType.Scalar,c_bool,start_with_local_cell),
        (ValueType.Array,c_double,v_value__array),
        (ValueType.Address,c_uint64,getattr(source_zones,'value',source_zones)),
        (ValueType.Scalar,c_bool,search_volume),
        (ValueType.Scalar,c_bool,get_zone_only),
        (ValueType.Scalar,c_bool,get_nearest_point),)
  rep=self.sndrcv("ProbeAtPosition",*args).Reply()
  self.chk(rep)
  v_value__array[:] = cast(byref(rep.Args(5).Float64Array()), POINTER(type(v_value__array))).contents[:]
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value(),
   IJKPlanes(rep.Args(3).Int32Value()),
   rep.Args(4).Int32Value())
 def ProbeFieldGetCCValue(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldGetCCValue",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value())
 def ProbeFieldGetCZType(self):
  rep=self.sndrcv("ProbeFieldGetCZType").Reply()
  self.chk(rep)
  return CZType(rep.Args(0).Int32Value())
 def ProbeFieldGetCell(self):
  rep=self.sndrcv("ProbeFieldGetCell").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ProbeFieldGetFaceCell(self):
  rep=self.sndrcv("ProbeFieldGetFaceCell").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ProbeFieldGetFaceNumber(self):
  rep=self.sndrcv("ProbeFieldGetFaceNumber").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ProbeFieldGetName(self):
  rep=self.sndrcv("ProbeFieldGetName").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def ProbeFieldGetNativeRef(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldGetNativeRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ProbeFieldGetPlane(self):
  rep=self.sndrcv("ProbeFieldGetPlane").Reply()
  self.chk(rep)
  return IJKPlanes(rep.Args(0).Int32Value())
 def ProbeFieldGetReadableCCRef(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldGetReadableCCRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ProbeFieldGetReadableDerivedRef(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldGetReadableDerivedRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ProbeFieldGetReadableNLRef(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldGetReadableNLRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ProbeFieldGetReadableNativeRef(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldGetReadableNativeRef",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ProbeFieldGetValue(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldGetValue",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ProbeFieldGetZone(self):
  rep=self.sndrcv("ProbeFieldGetZone").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ProbeFieldIsVarValid(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("ProbeFieldIsVarValid",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ProbeGetPlotType(self):
  rep=self.sndrcv("ProbeGetPlotType").Reply()
  self.chk(rep)
  return PlotType(rep.Args(0).Int32Value())
 def ProbeGetPointIndex(self):
  rep=self.sndrcv("ProbeGetPointIndex").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ProbeInfoDealloc(self,probe_info):
  args=((ValueType.Address,c_uint64,probe_info.contents.value),)
  rep=self.sndrcv("ProbeInfoDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ProbeInfoGet(self):
  rep=self.sndrcv("ProbeInfoGet").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ProbeInstallCallback(self,probe_destination,information_line_text):
  args=((ValueType.Address,c_uint64,getattr(probe_destination,'value',probe_destination)),
        (ValueType.Text,None,information_line_text),)
  rep=self.sndrcv("ProbeInstallCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ProbeInstallCallbackX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ProbeInstallCallbackX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ProbeIsCallbackInstalled(self):
  rep=self.sndrcv("ProbeIsCallbackInstalled").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ProbeLinePlotGetDepValue(self,map_num):
  args=((ValueType.Scalar,c_int32,map_num),)
  rep=self.sndrcv("ProbeLinePlotGetDepValue",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value())
 def ProbeLinePlotGetIndAxisKind(self):
  rep=self.sndrcv("ProbeLinePlotGetIndAxisKind").Reply()
  self.chk(rep)
  return rep.Args(0).Text()[0]
 def ProbeLinePlotGetIndAxisNumber(self):
  rep=self.sndrcv("ProbeLinePlotGetIndAxisNumber").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ProbeLinePlotGetIndValue(self):
  rep=self.sndrcv("ProbeLinePlotGetIndValue").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ProbeLinePlotGetSourceMap(self):
  rep=self.sndrcv("ProbeLinePlotGetSourceMap").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ProbePerform(self,probe_info,callback):
  args=((ValueType.Address,c_uint64,getattr(probe_info,'value',probe_info)),
        (ValueType.Address,c_uint64,getattr(callback,'value',callback)),)
  rep=self.sndrcv("ProbePerform",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ProbeRepeatLastEvent(self):
  rep=self.sndrcv("ProbeRepeatLastEvent").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def PropagateLinking(self,link_type,frame_collection):
  args=((ValueType.Scalar,c_int32,LinkType(link_type).value),
        (ValueType.Scalar,c_int32,FrameCollection(frame_collection).value),)
  rep=self.sndrcv("PropagateLinking",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Publish(self,f_name,include_layout_package,image_selection):
  args=((ValueType.Text,None,f_name),
        (ValueType.Scalar,c_bool,include_layout_package),
        (ValueType.Scalar,c_int32,ImageSelection(image_selection).value),)
  rep=self.sndrcv("Publish",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def QueryCanPlotIsoSurfaces(self):
  rep=self.sndrcv("QueryCanPlotIsoSurfaces").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryCanPlotSlices(self):
  rep=self.sndrcv("QueryCanPlotSlices").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryCanPlotStreamtraces(self):
  rep=self.sndrcv("QueryCanPlotStreamtraces").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryCanPlotVolumeStreamtraces(self):
  rep=self.sndrcv("QueryCanPlotVolumeStreamtraces").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryColorBandsInUseForContourGroup(self,contour_group):
  args=((ValueType.Scalar,c_int32,contour_group),)
  rep=self.sndrcv("QueryColorBandsInUseForContourGroup",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryContourLevelModificationsAllowed(self):
  rep=self.sndrcv("QueryContourLevelModificationsAllowed").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryGetZoneRank(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("QueryGetZoneRank",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def QueryIsLayoutDirty(self):
  rep=self.sndrcv("QueryIsLayoutDirty").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryIsTechnologyPreviewFeatureEnabled(self,feature):
  args=((ValueType.Text,None,feature),)
  rep=self.sndrcv("QueryIsTechnologyPreviewFeatureEnabled",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryIsXYDependentAllowedForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("QueryIsXYDependentAllowedForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryLayoutHasStyle(self):
  rep=self.sndrcv("QueryLayoutHasStyle").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToAnimateIJKPlanes(self):
  rep=self.sndrcv("QueryOkToAnimateIJKPlanes").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToAnimateZones(self):
  rep=self.sndrcv("QueryOkToAnimateZones").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToClearPickedObjects(self):
  rep=self.sndrcv("QueryOkToClearPickedObjects").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToCopyPickedObjects(self):
  rep=self.sndrcv("QueryOkToCopyPickedObjects").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToExtractContourLines(self):
  rep=self.sndrcv("QueryOkToExtractContourLines").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToExtractIsoSurfaces(self):
  rep=self.sndrcv("QueryOkToExtractIsoSurfaces").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToExtractPoints(self):
  rep=self.sndrcv("QueryOkToExtractPoints").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToExtractSlices(self):
  rep=self.sndrcv("QueryOkToExtractSlices").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToExtractStream(self):
  rep=self.sndrcv("QueryOkToExtractStream").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToPastePickedObjects(self):
  rep=self.sndrcv("QueryOkToPastePickedObjects").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToPushPopPickedObjects(self):
  rep=self.sndrcv("QueryOkToPushPopPickedObjects").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryOkToSmooth(self):
  rep=self.sndrcv("QueryOkToSmooth").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryPlotContainsContourLines(self):
  rep=self.sndrcv("QueryPlotContainsContourLines").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryPlotContainsPoints(self):
  rep=self.sndrcv("QueryPlotContainsPoints").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryPlotContainsSurfaceZones(self):
  rep=self.sndrcv("QueryPlotContainsSurfaceZones").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryPlotContainsVolumeZones(self):
  rep=self.sndrcv("QueryPlotContainsVolumeZones").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryStreamtracesAreActive(self):
  rep=self.sndrcv("QueryStreamtracesAreActive").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryZoneCanPlotVolumeStreamtraces(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("QueryZoneCanPlotVolumeStreamtraces",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def QueryZoneHasVisibleFieldStyle(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("QueryZoneHasVisibleFieldStyle",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def Quit(self):
  rep=self.sndrcv("Quit").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def QuitAddQueryCallback(self,quit_query_callback):
  args=((ValueType.Address,c_uint64,getattr(quit_query_callback,'value',quit_query_callback)),)
  rep=self.sndrcv("QuitAddQueryCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def RawColorMap(self,num_raw_rgb_values,raw_r_values__array,raw_g_values__array,raw_b_values__array):
  args=((ValueType.Scalar,c_int32,num_raw_rgb_values),
        (ValueType.Array,c_uint8,raw_r_values__array),
        (ValueType.Array,c_uint8,raw_g_values__array),
        (ValueType.Array,c_uint8,raw_b_values__array),)
  rep=self.sndrcv("RawColorMap",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ReadColorMap(self,f_name):
  args=((ValueType.Text,None,f_name),)
  rep=self.sndrcv("ReadColorMap",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ReadDataSet(self,read_data_option,reset_style,file_names_or_instructions,data_set_reader,initial_plot_type,include_text,include_geom,include_custom_labels,include_data,collapse_zones_and_vars,zones_to_read,var_load_mode,var_position_list,var_name_list,i_skip,j_skip,k_skip):
  args=((ValueType.Scalar,c_int32,ReadDataOption(read_data_option).value),
        (ValueType.Scalar,c_bool,reset_style),
        (ValueType.Address,c_uint64,getattr(file_names_or_instructions,'value',file_names_or_instructions)),
        (ValueType.Text,None,data_set_reader),
        (ValueType.Scalar,c_int32,PlotType(initial_plot_type).value),
        (ValueType.Scalar,c_bool,include_text),
        (ValueType.Scalar,c_bool,include_geom),
        (ValueType.Scalar,c_bool,include_custom_labels),
        (ValueType.Scalar,c_bool,include_data),
        (ValueType.Scalar,c_bool,collapse_zones_and_vars),
        (ValueType.Address,c_uint64,getattr(zones_to_read,'value',zones_to_read)),
        (ValueType.Scalar,c_int32,VarLoadMode(var_load_mode).value),
        (ValueType.Address,c_uint64,getattr(var_position_list,'value',var_position_list)),
        (ValueType.Address,c_uint64,getattr(var_name_list,'value',var_name_list)),
        (ValueType.Scalar,c_int64,i_skip),
        (ValueType.Scalar,c_int64,j_skip),
        (ValueType.Scalar,c_int64,k_skip),)
  rep=self.sndrcv("ReadDataSet",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ReadStylesheet(self,f_name,include_plot_style,include_text,include_geom,include_stream_positions,include_contour_levels,merge_style,include_frame_size_and_position):
  args=((ValueType.Text,None,f_name),
        (ValueType.Scalar,c_bool,include_plot_style),
        (ValueType.Scalar,c_bool,include_text),
        (ValueType.Scalar,c_bool,include_geom),
        (ValueType.Scalar,c_bool,include_stream_positions),
        (ValueType.Scalar,c_bool,include_contour_levels),
        (ValueType.Scalar,c_bool,merge_style),
        (ValueType.Scalar,c_bool,include_frame_size_and_position),)
  rep=self.sndrcv("ReadStylesheet",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Redraw(self,do_full_drawing):
  args=((ValueType.Scalar,c_bool,do_full_drawing),)
  rep=self.sndrcv("Redraw",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def RedrawAll(self,do_full_drawing):
  args=((ValueType.Scalar,c_bool,do_full_drawing),)
  rep=self.sndrcv("RedrawAll",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Reset3DAngles(self):
  rep=self.sndrcv("Reset3DAngles").Reply()
  self.chk(rep)
 def Reset3DAxes(self):
  rep=self.sndrcv("Reset3DAxes").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Reset3DOrigin(self):
  rep=self.sndrcv("Reset3DOrigin").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Reset3DOriginX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("Reset3DOriginX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Reset3DScaleFactors(self):
  rep=self.sndrcv("Reset3DScaleFactors").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ResetRefVectorMagnitude(self):
  rep=self.sndrcv("ResetRefVectorMagnitude").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ResetVectorLength(self):
  rep=self.sndrcv("ResetVectorLength").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def RotateArbitrarySlice(self,axis,degrees,slice_group):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_double,degrees),
        (ValueType.Scalar,c_int32,slice_group),)
  rep=self.sndrcv("RotateArbitrarySlice",*args).Reply()
  self.chk(rep)
 def RotateToSpecificAngles(self,psi,theta,alpha):
  args=((ValueType.Scalar,c_double,psi),
        (ValueType.Scalar,c_double,theta),
        (ValueType.Scalar,c_double,alpha),)
  rep=self.sndrcv("RotateToSpecificAngles",*args).Reply()
  self.chk(rep)
 def SaveLayout(self,f_name,use_relative_paths):
  args=((ValueType.Text,None,f_name),
        (ValueType.Scalar,c_bool,use_relative_paths),)
  rep=self.sndrcv("SaveLayout",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def SaveLayoutX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("SaveLayoutX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ScatterResetRelSize(self):
  rep=self.sndrcv("ScatterResetRelSize").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ScriptExec(self,file_name):
  args=((ValueType.Text,None,file_name),)
  rep=self.sndrcv("ScriptExec",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ScriptExecRegisterCallback(self,file_ext,script_language,script_exec_callback,client_data):
  args=((ValueType.Text,None,file_ext),
        (ValueType.Text,None,script_language),
        (ValueType.Address,c_uint64,getattr(script_exec_callback,'value',script_exec_callback)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("ScriptExecRegisterCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ScriptProcessorGetClientData(self,script_extension):
  args=((ValueType.Text,None,script_extension),)
  rep=self.sndrcv("ScriptProcessorGetClientData",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_arbparam(rep.Args(0)))
 def Set3DEyeDistance(self,eye_distance):
  args=((ValueType.Scalar,c_double,eye_distance),)
  rep=self.sndrcv("Set3DEyeDistance",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def SetAddMember(self,set,member,show_err):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),
        (ValueType.Scalar,c_int64,member),
        (ValueType.Scalar,c_bool,show_err),)
  rep=self.sndrcv("SetAddMember",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def SetAlloc(self,show_err):
  args=((ValueType.Scalar,c_bool,show_err),)
  rep=self.sndrcv("SetAlloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def SetClear(self,set):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),)
  rep=self.sndrcv("SetClear",*args).Reply()
  self.chk(rep)
 def SetCopy(self,dst_set,src_set,show_err):
  args=((ValueType.Address,c_uint64,getattr(dst_set,'value',dst_set)),
        (ValueType.Address,c_uint64,getattr(src_set,'value',src_set)),
        (ValueType.Scalar,c_bool,show_err),)
  rep=self.sndrcv("SetCopy",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def SetDealloc(self,set):
  args=((ValueType.Address,c_uint64,set.contents.value),)
  rep=self.sndrcv("SetDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def SetGetMember(self,set,position):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),
        (ValueType.Scalar,c_int64,position),)
  rep=self.sndrcv("SetGetMember",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def SetGetMemberCount(self,set):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),)
  rep=self.sndrcv("SetGetMemberCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def SetGetNextMember(self,set,member):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),
        (ValueType.Scalar,c_int64,member),)
  rep=self.sndrcv("SetGetNextMember",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def SetGetPosition(self,set,member):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),
        (ValueType.Scalar,c_int64,member),)
  rep=self.sndrcv("SetGetPosition",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def SetGetPrevMember(self,set,member):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),
        (ValueType.Scalar,c_int64,member),)
  rep=self.sndrcv("SetGetPrevMember",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def SetIsEmpty(self,set):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),)
  rep=self.sndrcv("SetIsEmpty",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def SetIsEqual(self,set1,set2):
  args=((ValueType.Address,c_uint64,getattr(set1,'value',set1)),
        (ValueType.Address,c_uint64,getattr(set2,'value',set2)),)
  rep=self.sndrcv("SetIsEqual",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def SetIsMember(self,set,member):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),
        (ValueType.Scalar,c_int64,member),)
  rep=self.sndrcv("SetIsMember",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def SetRemoveMember(self,set,member):
  args=((ValueType.Address,c_uint64,getattr(set,'value',set)),
        (ValueType.Scalar,c_int64,member),)
  rep=self.sndrcv("SetRemoveMember",*args).Reply()
  self.chk(rep)
 def SetupTransformations(self):
  rep=self.sndrcv("SetupTransformations").Reply()
  self.chk(rep)
 def SliceFinishDragging(self):
  rep=self.sndrcv("SliceFinishDragging").Reply()
  self.chk(rep)
 def SliceSetArbitraryUsingThreePoints(self,frame_id,slice_group,x1,y1,z1,x2,y2,z2,x3,y3,z3):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,slice_group),
        (ValueType.Scalar,c_double,x1),
        (ValueType.Scalar,c_double,y1),
        (ValueType.Scalar,c_double,z1),
        (ValueType.Scalar,c_double,x2),
        (ValueType.Scalar,c_double,y2),
        (ValueType.Scalar,c_double,z2),
        (ValueType.Scalar,c_double,x3),
        (ValueType.Scalar,c_double,y3),
        (ValueType.Scalar,c_double,z3),)
  rep=self.sndrcv("SliceSetArbitraryUsingThreePoints",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def SliceSolidPlaneSetPosition(self,slice_position):
  args=((ValueType.Scalar,c_double,slice_position),)
  rep=self.sndrcv("SliceSolidPlaneSetPosition",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def SliceStartDragging(self):
  rep=self.sndrcv("SliceStartDragging").Reply()
  self.chk(rep)
 def Smooth(self,zone,smooth_var,num_smooth_passes,smooth_weight,smooth_bndry_cond):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,smooth_var),
        (ValueType.Scalar,c_int32,num_smooth_passes),
        (ValueType.Scalar,c_double,smooth_weight),
        (ValueType.Scalar,c_int32,BoundaryCondition(smooth_bndry_cond).value),)
  rep=self.sndrcv("Smooth",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def SolutionTimeGetCurrent(self):
  rep=self.sndrcv("SolutionTimeGetCurrent").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def SolutionTimeGetCurrentForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("SolutionTimeGetCurrentForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def SolutionTimeGetCurrentTimeStepForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("SolutionTimeGetCurrentTimeStepForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def SolutionTimeGetMax(self):
  rep=self.sndrcv("SolutionTimeGetMax").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def SolutionTimeGetMin(self):
  rep=self.sndrcv("SolutionTimeGetMin").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def SolutionTimeGetNumTimeStepsByDataSetID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("SolutionTimeGetNumTimeStepsByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def SolutionTimeGetNumTimeStepsForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("SolutionTimeGetNumTimeStepsForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def SolutionTimeGetSolutionTimeAtTimeStepByDataSetID(self,data_set_id,time_step):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,time_step),)
  rep=self.sndrcv("SolutionTimeGetSolutionTimeAtTimeStepByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value())
 def SolutionTimeGetSolutionTimeAtTimeStepForFrame(self,frame_id,time_step):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,time_step),)
  rep=self.sndrcv("SolutionTimeGetSolutionTimeAtTimeStepForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value())
 def SolutionTimeGetSolutionTimeMinMaxByDataSetID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("SolutionTimeGetSolutionTimeMinMaxByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def SolutionTimeGetSolutionTimeMinMaxForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("SolutionTimeGetSolutionTimeMinMaxForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def SolutionTimeGetSolutionTimesByDataSetID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("SolutionTimeGetSolutionTimesByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64ArrayLength(),
   copy(rep.Args(0).Float64Array()))
 def SolutionTimeGetSolutionTimesForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("SolutionTimeGetSolutionTimesForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64ArrayLength(),
   copy(rep.Args(0).Float64Array()))
 def SolutionTimeGetTimeStepAtSolutionTimeByDataSetID(self,data_set_id,solution_time):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_double,solution_time),)
  rep=self.sndrcv("SolutionTimeGetTimeStepAtSolutionTimeByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def SolutionTimeGetTimeStepAtSolutionTimeForFrame(self,frame_id,solution_time):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_double,solution_time),)
  rep=self.sndrcv("SolutionTimeGetTimeStepAtSolutionTimeForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def SolutionTimeSetCurrent(self,new_solution_time):
  args=((ValueType.Scalar,c_double,new_solution_time),)
  rep=self.sndrcv("SolutionTimeSetCurrent",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def SortUInt32ItemArray(self,item_array,item_count,item_comparator,client_data):
  args=((ValueType.Array,c_uint32,item_array),
        (ValueType.Scalar,c_uint64,item_count),
        (ValueType.Address,c_uint64,getattr(item_comparator,'value',item_comparator)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("SortUInt32ItemArray",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Uint32Array()
 def SortUInt64ItemArray(self,item_array,item_count,item_comparator,client_data):
  args=((ValueType.Array,c_uint64,item_array),
        (ValueType.Scalar,c_uint64,item_count),
        (ValueType.Address,c_uint64,getattr(item_comparator,'value',item_comparator)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("SortUInt64ItemArray",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Uint64Array()
 def StateChangeAddCallback(self,state_change_callback):
  args=((ValueType.Address,c_uint64,getattr(state_change_callback,'value',state_change_callback)),)
  rep=self.sndrcv("StateChangeAddCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StateChangeAddCallbackX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("StateChangeAddCallbackX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StateChangeGetArbEnum(self):
  rep=self.sndrcv("StateChangeGetArbEnum").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def StateChangeGetDataSetUniqueID(self):
  rep=self.sndrcv("StateChangeGetDataSetUniqueID").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value())
 def StateChangeGetFrameUniqueID(self):
  rep=self.sndrcv("StateChangeGetFrameUniqueID").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value())
 def StateChangeGetIndex(self):
  rep=self.sndrcv("StateChangeGetIndex").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value())
 def StateChangeGetInfoX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("StateChangeGetInfoX",*args).Reply()
  self.chk(rep)
 def StateChangeGetMap(self):
  rep=self.sndrcv("StateChangeGetMap").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def StateChangeGetName(self):
  rep=self.sndrcv("StateChangeGetName").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def StateChangeGetPageUniqueID(self):
  rep=self.sndrcv("StateChangeGetPageUniqueID").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value())
 def StateChangeGetStyleParam(self,param):
  args=((ValueType.Scalar,c_int32,param),)
  rep=self.sndrcv("StateChangeGetStyleParam",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def StateChangeGetUniqueID(self):
  rep=self.sndrcv("StateChangeGetUniqueID").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value())
 def StateChangeGetVar(self):
  rep=self.sndrcv("StateChangeGetVar").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def StateChangeGetVarSet(self):
  rep=self.sndrcv("StateChangeGetVarSet").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def StateChangeGetZone(self):
  rep=self.sndrcv("StateChangeGetZone").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int32Value())
 def StateChangeGetZoneSet(self):
  rep=self.sndrcv("StateChangeGetZoneSet").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def StateChangeRemoveCBX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("StateChangeRemoveCBX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StateChangeRemoveCallback(self,add_on_state_change_callback):
  args=((ValueType.Address,c_uint64,add_on_state_change_callback.contents.value),)
  rep=self.sndrcv("StateChangeRemoveCallback",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StateChangeSetMode(self,callback,mode):
  args=((ValueType.Address,c_uint64,getattr(callback,'value',callback)),
        (ValueType.Scalar,c_int32,StateChangeMode(mode).value),)
  rep=self.sndrcv("StateChangeSetMode",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StateChanged(self,state_change,call_data):
  args=((ValueType.Scalar,c_int32,StateChange(state_change).value),
        (ValueType.ArbParam,None,call_data),)
  rep=self.sndrcv("StateChanged",*args).Reply()
  self.chk(rep)
 def StateChangedX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("StateChangedX",*args).Reply()
  self.chk(rep)
 def StateIsProcessingJournal(self):
  rep=self.sndrcv("StateIsProcessingJournal").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def StateIsProcessingLayout(self):
  rep=self.sndrcv("StateIsProcessingLayout").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def StateIsProcessingMacro(self):
  rep=self.sndrcv("StateIsProcessingMacro").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def StateIsProcessingStylesheet(self):
  rep=self.sndrcv("StateIsProcessingStylesheet").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def StatusCheckPercentDone(self,percent_done):
  args=((ValueType.Scalar,c_int32,percent_done),)
  rep=self.sndrcv("StatusCheckPercentDone",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StatusFinishPercentDone(self):
  rep=self.sndrcv("StatusFinishPercentDone").Reply()
  self.chk(rep)
 def StatusSetPercentDoneText(self,percent_done_text):
  args=((ValueType.Text,None,percent_done_text),)
  rep=self.sndrcv("StatusSetPercentDoneText",*args).Reply()
  self.chk(rep)
 def StatusStartPercentDone(self,percent_done_text,show_stop_button,show_progress_bar):
  args=((ValueType.Text,None,percent_done_text),
        (ValueType.Scalar,c_bool,show_stop_button),
        (ValueType.Scalar,c_bool,show_progress_bar),)
  rep=self.sndrcv("StatusStartPercentDone",*args).Reply()
  self.chk(rep)
 def StatusSuspend(self,do_suspend):
  args=((ValueType.Scalar,c_bool,do_suspend),)
  rep=self.sndrcv("StatusSuspend",*args).Reply()
  self.chk(rep)
 def StreamtraceAdd(self,num_rake_points,stream_type,direction,start_x_pos,start_y_pos,start_z_pos,alt_start_x_pos,alt_start_y_pos,alt_start_z_pos):
  args=((ValueType.Scalar,c_int32,num_rake_points),
        (ValueType.Scalar,c_int32,Streamtrace(stream_type).value),
        (ValueType.Scalar,c_int32,StreamDir(direction).value),
        (ValueType.Scalar,c_double,start_x_pos),
        (ValueType.Scalar,c_double,start_y_pos),
        (ValueType.Scalar,c_double,start_z_pos),
        (ValueType.Scalar,c_double,alt_start_x_pos),
        (ValueType.Scalar,c_double,alt_start_y_pos),
        (ValueType.Scalar,c_double,alt_start_z_pos),)
  rep=self.sndrcv("StreamtraceAdd",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StreamtraceAddX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("StreamtraceAddX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StreamtraceDeleteAll(self):
  rep=self.sndrcv("StreamtraceDeleteAll").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StreamtraceDeleteRange(self,start,end):
  args=((ValueType.Scalar,c_int32,start),
        (ValueType.Scalar,c_int32,end),)
  rep=self.sndrcv("StreamtraceDeleteRange",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StreamtraceGetCount(self):
  rep=self.sndrcv("StreamtraceGetCount").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def StreamtraceGetPos(self,stream_number):
  args=((ValueType.Scalar,c_int32,stream_number),)
  rep=self.sndrcv("StreamtraceGetPos",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def StreamtraceGetType(self,stream_number):
  args=((ValueType.Scalar,c_int32,stream_number),)
  rep=self.sndrcv("StreamtraceGetType",*args).Reply()
  self.chk(rep)
  return Streamtrace(rep.Args(0).Int32Value())
 def StreamtraceHasTermLine(self):
  rep=self.sndrcv("StreamtraceHasTermLine").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def StreamtraceResetDelta(self):
  rep=self.sndrcv("StreamtraceResetDelta").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StreamtraceSetTermLine(self,num_points,x_term_line_pts__array,y_term_line_pts__array):
  args=((ValueType.Scalar,c_int32,num_points),
        (ValueType.Array,c_double,x_term_line_pts__array),
        (ValueType.Array,c_double,y_term_line_pts__array),)
  rep=self.sndrcv("StreamtraceSetTermLine",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StringAlloc(self,max_length,debug_info):
  args=((ValueType.Scalar,c_int64,max_length),
        (ValueType.Text,None,debug_info),)
  rep=self.sndrcv("StringAlloc",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StringConvOldFormatting(self,old_string,base_font):
  args=((ValueType.Text,None,old_string),
        (ValueType.Scalar,c_int32,Font(base_font).value),)
  rep=self.sndrcv("StringConvOldFormatting",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StringDealloc(self,s):
  args=((ValueType.Address,c_uint64,s.contents.value),)
  rep=self.sndrcv("StringDealloc",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StringFormatTimeDate(self,time_date_value,time_date_format):
  args=((ValueType.Scalar,c_double,time_date_value),
        (ValueType.Text,None,time_date_format),)
  rep=self.sndrcv("StringFormatTimeDate",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StringFormatValue(self,value,format,precision):
  args=((ValueType.Scalar,c_double,value),
        (ValueType.Scalar,c_int32,NumberFormat(format).value),
        (ValueType.Scalar,c_int32,precision),)
  rep=self.sndrcv("StringFormatValue",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StringListAlloc(self):
  rep=self.sndrcv("StringListAlloc").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def StringListAppend(self,target,source):
  args=((ValueType.Address,c_uint64,getattr(target,'value',target)),
        (ValueType.Address,c_uint64,getattr(source,'value',source)),)
  rep=self.sndrcv("StringListAppend",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StringListAppendString(self,string_list,string):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Text,None,string),)
  rep=self.sndrcv("StringListAppendString",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StringListClear(self,string_list):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),)
  rep=self.sndrcv("StringListClear",*args).Reply()
  self.chk(rep)
 def StringListCopy(self,string_list):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),)
  rep=self.sndrcv("StringListCopy",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def StringListDealloc(self,string_list):
  args=((ValueType.Address,c_uint64,string_list.contents.value),)
  rep=self.sndrcv("StringListDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def StringListFromNLString(self,string):
  args=((ValueType.Text,None,string),)
  rep=self.sndrcv("StringListFromNLString",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def StringListGetCount(self,string_list):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),)
  rep=self.sndrcv("StringListGetCount",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def StringListGetRawStringPtr(self,string_list,string_number):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Scalar,c_int64,string_number),)
  rep=self.sndrcv("StringListGetRawStringPtr",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StringListGetString(self,string_list,string_number):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Scalar,c_int64,string_number),)
  rep=self.sndrcv("StringListGetString",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StringListInsertString(self,string_list,string_number,string):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Scalar,c_int64,string_number),
        (ValueType.Text,None,string),)
  rep=self.sndrcv("StringListInsertString",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StringListRemoveString(self,string_list,string_number):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Scalar,c_int64,string_number),)
  rep=self.sndrcv("StringListRemoveString",*args).Reply()
  self.chk(rep)
 def StringListRemoveStrings(self,string_list,string_number,count):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Scalar,c_int64,string_number),
        (ValueType.Scalar,c_int64,count),)
  rep=self.sndrcv("StringListRemoveStrings",*args).Reply()
  self.chk(rep)
 def StringListSetString(self,string_list,string_number,string):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Scalar,c_int64,string_number),
        (ValueType.Text,None,string),)
  rep=self.sndrcv("StringListSetString",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StringListSort(self,string_list,comparator,client_data):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),
        (ValueType.Address,c_uint64,getattr(comparator,'value',comparator)),
        (ValueType.ArbParam,None,client_data),)
  rep=self.sndrcv("StringListSort",*args).Reply()
  self.chk(rep)
 def StringListToNLString(self,string_list):
  args=((ValueType.Address,c_uint64,getattr(string_list,'value',string_list)),)
  rep=self.sndrcv("StringListToNLString",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StyleGetLastErrorString(self):
  rep=self.sndrcv("StyleGetLastErrorString").Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def StyleGetLowLevelX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("StyleGetLowLevelX",*args).Reply()
  self.chk(rep)
  return GetValueReturnCode(rep.Args(0).Int32Value())
 def StyleSetBase(self,style_base):
  args=((ValueType.Scalar,c_int32,StyleBase(style_base).value),)
  rep=self.sndrcv("StyleSetBase",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def StyleSetLowLevel(self,text_field_widget,d_value,i_value,set_or_offset,assign_modifier,p1,p2,p3,p4,p5,p6,do_implicit_recording):
  args=((ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),
        (ValueType.ArbParam,None,set_or_offset),
        (ValueType.Scalar,c_int32,AssignOp(assign_modifier).value),
        (ValueType.Text,None,p1),
        (ValueType.Text,None,p2),
        (ValueType.Text,None,p3),
        (ValueType.Text,None,p4),
        (ValueType.Text,None,p5),
        (ValueType.Text,None,p6),
        (ValueType.Scalar,c_bool,do_implicit_recording),)
  rep=self.sndrcv("StyleSetLowLevel",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def StyleSetLowLevelX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("StyleSetLowLevelX",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def StyleValueGetMacroID(self,style_value_name):
  args=((ValueType.Text,None,style_value_name),)
  rep=self.sndrcv("StyleValueGetMacroID",*args).Reply()
  self.chk(rep)
  return self.read_arbparam(rep.Args(0))
 def System(self,command,wait):
  args=((ValueType.Text,None,command),
        (ValueType.Scalar,c_bool,wait),)
  rep=self.sndrcv("System",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def TecplotGetAppMode(self):
  rep=self.sndrcv("TecplotGetAppMode").Reply()
  self.chk(rep)
  return AppMode(rep.Args(0).Int32Value())
 def TecplotGetExePath(self):
  rep=self.sndrcv("TecplotGetExePath").Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def TecplotGetHomeDirectory(self):
  rep=self.sndrcv("TecplotGetHomeDirectory").Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def TecplotGetMajorRevision(self):
  rep=self.sndrcv("TecplotGetMajorRevision").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def TecplotGetMajorVersion(self):
  rep=self.sndrcv("TecplotGetMajorVersion").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def TecplotGetMinorRevision(self):
  rep=self.sndrcv("TecplotGetMinorRevision").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def TecplotGetMinorVersion(self):
  rep=self.sndrcv("TecplotGetMinorVersion").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def Text3DCreate(self,pos_x,pos_y,pos_z,height_units,height,text):
  args=((ValueType.Scalar,c_double,pos_x),
        (ValueType.Scalar,c_double,pos_y),
        (ValueType.Scalar,c_double,pos_z),
        (ValueType.Scalar,c_int32,Units(height_units).value),
        (ValueType.Scalar,c_double,height),
        (ValueType.Text,None,text),)
  rep=self.sndrcv("Text3DCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def TextBoxGetColor(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextBoxGetColor",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def TextBoxGetFillColor(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextBoxGetFillColor",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def TextBoxGetLineThickness(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextBoxGetLineThickness",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def TextBoxGetMargin(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextBoxGetMargin",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def TextBoxGetPosition(self,t):
  args=((ValueType.Scalar,c_int64,t),)
  rep=self.sndrcv("TextBoxGetPosition",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value(),
   rep.Args(3).Float64Value(),
   rep.Args(4).Float64Value(),
   rep.Args(5).Float64Value(),
   rep.Args(6).Float64Value(),
   rep.Args(7).Float64Value())
 def TextBoxGetType(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextBoxGetType",*args).Reply()
  self.chk(rep)
  return TextBox(rep.Args(0).Int32Value())
 def TextBoxSetColor(self,tid,box_color):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,box_color),)
  rep=self.sndrcv("TextBoxSetColor",*args).Reply()
  self.chk(rep)
 def TextBoxSetFillColor(self,tid,box_fill_color):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,box_fill_color),)
  rep=self.sndrcv("TextBoxSetFillColor",*args).Reply()
  self.chk(rep)
 def TextBoxSetLineThickness(self,tid,line_thickness):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_double,line_thickness),)
  rep=self.sndrcv("TextBoxSetLineThickness",*args).Reply()
  self.chk(rep)
 def TextBoxSetMargin(self,tid,margin):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_double,margin),)
  rep=self.sndrcv("TextBoxSetMargin",*args).Reply()
  self.chk(rep)
 def TextBoxSetType(self,tid,text_box_type):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,TextBox(text_box_type).value),)
  rep=self.sndrcv("TextBoxSetType",*args).Reply()
  self.chk(rep)
 def TextCreate(self,position_coord_sys,pos_x,pos_y,height_units,height,text):
  args=((ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_double,pos_x),
        (ValueType.Scalar,c_double,pos_y),
        (ValueType.Scalar,c_int32,Units(height_units).value),
        (ValueType.Scalar,c_double,height),
        (ValueType.Text,None,text),)
  rep=self.sndrcv("TextCreate",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def TextCreateX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("TextCreateX",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def TextDelete(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextDelete",*args).Reply()
  self.chk(rep)
 def TextGetAnchor(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetAnchor",*args).Reply()
  self.chk(rep)
  return TextAnchor(rep.Args(0).Int32Value())
 def TextGetAnchorPos(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetAnchorPos",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def TextGetAngle(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetAngle",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def TextGetBase(self):
  rep=self.sndrcv("TextGetBase").Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def TextGetClipping(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetClipping",*args).Reply()
  self.chk(rep)
  return Clipping(rep.Args(0).Int32Value())
 def TextGetColor(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetColor",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def TextGetFont(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetFont",*args).Reply()
  self.chk(rep)
  return Font(rep.Args(0).Int32Value())
 def TextGetHeight(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetHeight",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def TextGetLineSpacing(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetLineSpacing",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def TextGetMacroFunctionCmd(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetMacroFunctionCmd",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def TextGetNext(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetNext",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def TextGetPositionCoordSys(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetPositionCoordSys",*args).Reply()
  self.chk(rep)
  return CoordSys(rep.Args(0).Int32Value())
 def TextGetPrev(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetPrev",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def TextGetScope(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetScope",*args).Reply()
  self.chk(rep)
  return Scope(rep.Args(0).Int32Value())
 def TextGetSizeUnits(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetSizeUnits",*args).Reply()
  self.chk(rep)
  return Units(rep.Args(0).Int32Value())
 def TextGetString(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetString",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def TextGetType(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetType",*args).Reply()
  self.chk(rep)
  return TextType(rep.Args(0).Int32Value())
 def TextGetTypefaceFamily(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetTypefaceFamily",*args).Reply()
  self.chk(rep)
  return self.read_text(rep.Args(0))
 def TextGetTypefaceIsBold(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetTypefaceIsBold",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def TextGetTypefaceIsItalic(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetTypefaceIsItalic",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def TextGetZoneOrMap(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextGetZoneOrMap",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def TextIsAttached(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextIsAttached",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def TextIsValid(self,tid):
  args=((ValueType.Scalar,c_int64,tid),)
  rep=self.sndrcv("TextIsValid",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def TextSetAnchor(self,tid,anchor):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,TextAnchor(anchor).value),)
  rep=self.sndrcv("TextSetAnchor",*args).Reply()
  self.chk(rep)
 def TextSetAnchorPos(self,tid,x_or_theta_pos,y_or_r_pos,z_pos):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_double,x_or_theta_pos),
        (ValueType.Scalar,c_double,y_or_r_pos),
        (ValueType.Scalar,c_double,z_pos),)
  rep=self.sndrcv("TextSetAnchorPos",*args).Reply()
  self.chk(rep)
 def TextSetAngle(self,tid,angle):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_double,angle),)
  rep=self.sndrcv("TextSetAngle",*args).Reply()
  self.chk(rep)
 def TextSetAttached(self,tid,attached):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_bool,attached),)
  rep=self.sndrcv("TextSetAttached",*args).Reply()
  self.chk(rep)
 def TextSetClipping(self,tid,clipping):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,Clipping(clipping).value),)
  rep=self.sndrcv("TextSetClipping",*args).Reply()
  self.chk(rep)
 def TextSetColor(self,tid,color):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,color),)
  rep=self.sndrcv("TextSetColor",*args).Reply()
  self.chk(rep)
 def TextSetCoordSysAndUnits(self,tid,position_coord_sys,height_units):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,CoordSys(position_coord_sys).value),
        (ValueType.Scalar,c_int32,Units(height_units).value),)
  rep=self.sndrcv("TextSetCoordSysAndUnits",*args).Reply()
  self.chk(rep)
 def TextSetFont(self,tid,font):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,Font(font).value),)
  rep=self.sndrcv("TextSetFont",*args).Reply()
  self.chk(rep)
 def TextSetHeight(self,tid,height):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_double,height),)
  rep=self.sndrcv("TextSetHeight",*args).Reply()
  self.chk(rep)
 def TextSetLineSpacing(self,tid,line_spacing):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_double,line_spacing),)
  rep=self.sndrcv("TextSetLineSpacing",*args).Reply()
  self.chk(rep)
 def TextSetMacroFunctionCmd(self,tid,command):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Text,None,command),)
  rep=self.sndrcv("TextSetMacroFunctionCmd",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def TextSetScope(self,tid,scope):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,Scope(scope).value),)
  rep=self.sndrcv("TextSetScope",*args).Reply()
  self.chk(rep)
 def TextSetString(self,tid,text_string):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Text,None,text_string),)
  rep=self.sndrcv("TextSetString",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def TextSetType(self,tid,text_type):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,TextType(text_type).value),)
  rep=self.sndrcv("TextSetType",*args).Reply()
  self.chk(rep)
 def TextSetTypeface(self,tid,font_family,is_bold,is_italic):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Text,None,font_family),
        (ValueType.Scalar,c_bool,is_bold),
        (ValueType.Scalar,c_bool,is_italic),)
  rep=self.sndrcv("TextSetTypeface",*args).Reply()
  self.chk(rep)
 def TextSetZoneOrMap(self,tid,zone_or_map):
  args=((ValueType.Scalar,c_int64,tid),
        (ValueType.Scalar,c_int32,zone_or_map),)
  rep=self.sndrcv("TextSetZoneOrMap",*args).Reply()
  self.chk(rep)
 def ThreadBroadcastCondition(self,condition):
  args=((ValueType.Address,c_uint64,getattr(condition,'value',condition)),)
  rep=self.sndrcv("ThreadBroadcastCondition",*args).Reply()
  self.chk(rep)
 def ThreadConditionAlloc(self):
  rep=self.sndrcv("ThreadConditionAlloc").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ThreadConditionDealloc(self,condition):
  args=((ValueType.Address,c_uint64,condition.contents.value),)
  rep=self.sndrcv("ThreadConditionDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ThreadCreateDetached(self,thread_function,thread_data):
  args=((ValueType.Address,c_uint64,getattr(thread_function,'value',thread_function)),
        (ValueType.ArbParam,None,thread_data),)
  rep=self.sndrcv("ThreadCreateDetached",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ThreadMutexAlloc(self):
  rep=self.sndrcv("ThreadMutexAlloc").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ThreadMutexDealloc(self,mutex):
  args=((ValueType.Address,c_uint64,mutex.contents.value),)
  rep=self.sndrcv("ThreadMutexDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ThreadMutexLock(self,mutex):
  args=((ValueType.Address,c_uint64,getattr(mutex,'value',mutex)),)
  rep=self.sndrcv("ThreadMutexLock",*args).Reply()
  self.chk(rep)
 def ThreadMutexUnlock(self,mutex):
  args=((ValueType.Address,c_uint64,getattr(mutex,'value',mutex)),)
  rep=self.sndrcv("ThreadMutexUnlock",*args).Reply()
  self.chk(rep)
 def ThreadPoolAddJob(self,job,job_data,job_control):
  args=((ValueType.Address,c_uint64,getattr(job,'value',job)),
        (ValueType.ArbParam,None,job_data),
        (ValueType.Address,c_uint64,getattr(job_control,'value',job_control)),)
  rep=self.sndrcv("ThreadPoolAddJob",*args).Reply()
  self.chk(rep)
 def ThreadPoolJobControlAlloc(self):
  rep=self.sndrcv("ThreadPoolJobControlAlloc").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ThreadPoolJobControlDealloc(self,job_control):
  args=((ValueType.Address,c_uint64,job_control.contents.value),)
  rep=self.sndrcv("ThreadPoolJobControlDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ThreadPoolJobThreadOffset(self):
  rep=self.sndrcv("ThreadPoolJobThreadOffset").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ThreadPoolPoolSize(self):
  rep=self.sndrcv("ThreadPoolPoolSize").Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ThreadPoolWait(self,job_control):
  args=((ValueType.Address,c_uint64,getattr(job_control,'value',job_control)),)
  rep=self.sndrcv("ThreadPoolWait",*args).Reply()
  self.chk(rep)
 def ThreadRecursiveMutexAlloc(self):
  rep=self.sndrcv("ThreadRecursiveMutexAlloc").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ThreadSignalCondition(self,condition):
  args=((ValueType.Address,c_uint64,getattr(condition,'value',condition)),)
  rep=self.sndrcv("ThreadSignalCondition",*args).Reply()
  self.chk(rep)
 def ThreadTimedWaitForCondition(self,condition,mutex,wait_period_in_ms):
  args=((ValueType.Address,c_uint64,getattr(condition,'value',condition)),
        (ValueType.Address,c_uint64,getattr(mutex,'value',mutex)),
        (ValueType.Scalar,c_int32,wait_period_in_ms),)
  rep=self.sndrcv("ThreadTimedWaitForCondition",*args).Reply()
  self.chk(rep)
  return ConditionAwakeReason(rep.Args(0).Int32Value())
 def ThreadWaitForCondition(self,condition,mutex):
  args=((ValueType.Address,c_uint64,getattr(condition,'value',condition)),
        (ValueType.Address,c_uint64,getattr(mutex,'value',mutex)),)
  rep=self.sndrcv("ThreadWaitForCondition",*args).Reply()
  self.chk(rep)
 def ThreeDViewGetDistanceToRotateOriginPlane(self):
  rep=self.sndrcv("ThreeDViewGetDistanceToRotateOriginPlane").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ThreeDViewGetMedianAxisRange(self):
  rep=self.sndrcv("ThreeDViewGetMedianAxisRange").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ThreeDViewGetMidZPlane(self):
  rep=self.sndrcv("ThreeDViewGetMidZPlane").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ThreeDViewGetMinMaxPanes(self):
  rep=self.sndrcv("ThreeDViewGetMinMaxPanes").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def ThreeDViewGetNearZPlane(self):
  rep=self.sndrcv("ThreeDViewGetNearZPlane").Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ThreeDViewGetProjection(self):
  rep=self.sndrcv("ThreeDViewGetProjection").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Boolean())
 def ThreeDViewGetViewerAngle(self):
  rep=self.sndrcv("ThreeDViewGetViewerAngle").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def ThreeDViewGetViewerPos(self):
  rep=self.sndrcv("ThreeDViewGetViewerPos").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def ThreedViewGetDefaultAngles(self):
  rep=self.sndrcv("ThreedViewGetDefaultAngles").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value(),
   rep.Args(2).Float64Value())
 def ToolbarActivate(self,activate):
  args=((ValueType.Scalar,c_bool,activate),)
  rep=self.sndrcv("ToolbarActivate",*args).Reply()
  self.chk(rep)
 def TransformCoordinatesX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("TransformCoordinatesX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def Triangulate(self,source_zones,do_boundary,boundary_zones,include_boundary_pts,triangle_keep_factor):
  args=((ValueType.Address,c_uint64,getattr(source_zones,'value',source_zones)),
        (ValueType.Scalar,c_bool,do_boundary),
        (ValueType.Address,c_uint64,getattr(boundary_zones,'value',boundary_zones)),
        (ValueType.Scalar,c_bool,include_boundary_pts),
        (ValueType.Scalar,c_double,triangle_keep_factor),)
  rep=self.sndrcv("Triangulate",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Int64Value())
 def UndoCanUndo(self):
  rep=self.sndrcv("UndoCanUndo").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def UndoDoUndo(self):
  rep=self.sndrcv("UndoDoUndo").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def UndoGetCategoryText(self):
  rep=self.sndrcv("UndoGetCategoryText").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def UndoStateBegin(self,category):
  args=((ValueType.Scalar,c_int32,UndoStateCategory(category).value),)
  rep=self.sndrcv("UndoStateBegin",*args).Reply()
  self.chk(rep)
 def UndoStateEnd(self,do_invalidate,do_commit):
  args=((ValueType.Scalar,c_bool,do_invalidate),
        (ValueType.Scalar,c_bool,do_commit),)
  rep=self.sndrcv("UndoStateEnd",*args).Reply()
  self.chk(rep)
 def UninstallProbeCallback(self):
  rep=self.sndrcv("UninstallProbeCallback").Reply()
  self.chk(rep)
 def UserMacroIsRecordingActive(self):
  rep=self.sndrcv("UserMacroIsRecordingActive").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarGetEnabled(self):
  rep=self.sndrcv("VarGetEnabled").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def VarGetEnabledByDataSetID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("VarGetEnabledByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def VarGetEnabledForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("VarGetEnabledForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def VarGetEnabledNamesByDataSetID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("VarGetEnabledNamesByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def VarGetMinMax(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarGetMinMax",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def VarGetName(self,var_num):
  args=((ValueType.Scalar,c_int32,var_num),)
  rep=self.sndrcv("VarGetName",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def VarGetNameByDataSetID(self,data_set_id,var_num):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,var_num),)
  rep=self.sndrcv("VarGetNameByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def VarGetNameForFrame(self,frame_id,var_num):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,var_num),)
  rep=self.sndrcv("VarGetNameForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def VarGetNonBlankedMinMax(self,zone_set,var):
  args=((ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarGetNonBlankedMinMax",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value(),
   rep.Args(1).Float64Value())
 def VarGetNumByAssignment(self,var):
  args=((ValueType.Text,None,var),)
  rep=self.sndrcv("VarGetNumByAssignment",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def VarGetNumByName(self,var_name):
  args=((ValueType.Text,None,var_name),)
  rep=self.sndrcv("VarGetNumByName",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def VarGetNumByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("VarGetNumByUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def VarGetStatus(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarGetStatus",*args).Reply()
  self.chk(rep)
  return VarStatus(rep.Args(0).Int32Value())
 def VarGetStatusByRef(self,field_data):
  args=((ValueType.Address,c_uint64,getattr(field_data,'value',field_data)),)
  rep=self.sndrcv("VarGetStatusByRef",*args).Reply()
  self.chk(rep)
  return VarStatus(rep.Args(0).Int32Value())
 def VarGetUniqueID(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarGetUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def VarGetUniqueIDByDataSetID(self,data_set_id,var):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarGetUniqueIDByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def VarGetUniqueIDForFrame(self,frame_id,var):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarGetUniqueIDForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def VarIsEnabled(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarIsEnabled",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarIsEnabledByDataSetID(self,data_set_id,var):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarIsEnabledByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarIsEnabledForFrame(self,frame_id,var):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarIsEnabledForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarIsSZLData(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarIsSZLData",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarIsSpatial(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarIsSpatial",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarIsSpatialForFrame(self,frame_id,var):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarIsSpatialForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarRangeIsEstimated(self,zone,var):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VarRangeIsEstimated",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def VarRename(self,var_num,var_name):
  args=((ValueType.Scalar,c_int32,var_num),
        (ValueType.Text,None,var_name),)
  rep=self.sndrcv("VarRename",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def VarRenameByDataSetID(self,data_set_id,var_num,var_name):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,var_num),
        (ValueType.Text,None,var_name),)
  rep=self.sndrcv("VarRenameByDataSetID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def VarRenameForFrame(self,frame_id,var_num,var_name):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,var_num),
        (ValueType.Text,None,var_name),)
  rep=self.sndrcv("VarRenameForFrame",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def VariableIsLocked(self,var):
  args=((ValueType.Scalar,c_int32,var),)
  rep=self.sndrcv("VariableIsLocked",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Boolean(),
   VarLockMode(rep.Args(1).Int32Value()),
   self.read_text(rep.Args(2)))
 def VariableLockOff(self,var,lock_owner):
  args=((ValueType.Scalar,c_int32,var),
        (ValueType.Text,None,lock_owner),)
  rep=self.sndrcv("VariableLockOff",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def VariableLockOn(self,var,var_lock_mode,lock_owner):
  args=((ValueType.Scalar,c_int32,var),
        (ValueType.Scalar,c_int32,VarLockMode(var_lock_mode).value),
        (ValueType.Text,None,lock_owner),)
  rep=self.sndrcv("VariableLockOn",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def VectorCheckVariableAssignments(self):
  rep=self.sndrcv("VectorCheckVariableAssignments").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ViewAxisFit(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("ViewAxisFit",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewAxisFitToEntireCircle(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("ViewAxisFitToEntireCircle",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewAxisMakeCurValsNice(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("ViewAxisMakeCurValsNice",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewAxisNiceFit(self,axis,axis_num):
  args=((ValueType.Text,None,axis),
        (ValueType.Scalar,c_int32,axis_num),)
  rep=self.sndrcv("ViewAxisNiceFit",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewCenter(self):
  rep=self.sndrcv("ViewCenter").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewCopy(self):
  rep=self.sndrcv("ViewCopy").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewDataFit(self):
  rep=self.sndrcv("ViewDataFit").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewDealloc(self,view_state):
  args=((ValueType.Address,c_uint64,view_state.contents.value),)
  rep=self.sndrcv("ViewDealloc",*args).Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ViewFit(self):
  rep=self.sndrcv("ViewFit").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewFitSurfaces(self):
  rep=self.sndrcv("ViewFitSurfaces").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewGet(self):
  rep=self.sndrcv("ViewGet").Reply()
  self.chk(rep)
  return self.read_ptr(rep.Args(0))
 def ViewGetMagnification(self):
  rep=self.sndrcv("ViewGetMagnification").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   rep.Args(0).Float64Value())
 def ViewGetPlotType(self,view_state):
  args=((ValueType.Address,c_uint64,getattr(view_state,'value',view_state)),)
  rep=self.sndrcv("ViewGetPlotType",*args).Reply()
  self.chk(rep)
  return PlotType(rep.Args(0).Int32Value())
 def ViewLast(self):
  rep=self.sndrcv("ViewLast").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewMakeCurViewNice(self):
  rep=self.sndrcv("ViewMakeCurViewNice").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewNiceFit(self):
  rep=self.sndrcv("ViewNiceFit").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewOkToPaste(self):
  rep=self.sndrcv("ViewOkToPaste").Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ViewPaste(self):
  rep=self.sndrcv("ViewPaste").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewPush(self):
  rep=self.sndrcv("ViewPush").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewRotate3D(self,rotate_axis,rotate_amount_in_degrees,vector_x,vector_y,vector_z,rotate_origin_location):
  args=((ValueType.Scalar,c_int32,RotateAxis(rotate_axis).value),
        (ValueType.Scalar,c_double,rotate_amount_in_degrees),
        (ValueType.Scalar,c_double,vector_x),
        (ValueType.Scalar,c_double,vector_y),
        (ValueType.Scalar,c_double,vector_z),
        (ValueType.Scalar,c_int32,RotateOriginLocation(rotate_origin_location).value),)
  rep=self.sndrcv("ViewRotate3D",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewSet(self,view_state):
  args=((ValueType.Address,c_uint64,getattr(view_state,'value',view_state)),)
  rep=self.sndrcv("ViewSet",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewSetMagnification(self,magnification):
  args=((ValueType.Scalar,c_double,magnification),)
  rep=self.sndrcv("ViewSetMagnification",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewTranslate(self,x,y):
  args=((ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),)
  rep=self.sndrcv("ViewTranslate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ViewX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ViewZoom(self,x1,y1,x2,y2):
  args=((ValueType.Scalar,c_double,x1),
        (ValueType.Scalar,c_double,y1),
        (ValueType.Scalar,c_double,x2),
        (ValueType.Scalar,c_double,y2),)
  rep=self.sndrcv("ViewZoom",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WinCopyToClipboard(self):
  rep=self.sndrcv("WinCopyToClipboard").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WorkAreaGetDimensions(self):
  rep=self.sndrcv("WorkAreaGetDimensions").Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int32Value(),
   rep.Args(1).Int32Value())
 def WorkAreaSuspend(self,do_suspend):
  args=((ValueType.Scalar,c_bool,do_suspend),)
  rep=self.sndrcv("WorkAreaSuspend",*args).Reply()
  self.chk(rep)
 def WorkViewFitAllFrames(self):
  rep=self.sndrcv("WorkViewFitAllFrames").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WorkViewFitPaper(self):
  rep=self.sndrcv("WorkViewFitPaper").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WorkViewFitSelectFrames(self):
  rep=self.sndrcv("WorkViewFitSelectFrames").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WorkViewLastView(self):
  rep=self.sndrcv("WorkViewLastView").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WorkViewMaximize(self):
  rep=self.sndrcv("WorkViewMaximize").Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WorkViewTranslate(self,x,y):
  args=((ValueType.Scalar,c_double,x),
        (ValueType.Scalar,c_double,y),)
  rep=self.sndrcv("WorkViewTranslate",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WorkViewZoom(self,x1,y1,x2,y2):
  args=((ValueType.Scalar,c_double,x1),
        (ValueType.Scalar,c_double,y1),
        (ValueType.Scalar,c_double,x2),
        (ValueType.Scalar,c_double,y2),)
  rep=self.sndrcv("WorkViewZoom",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WriteColorMap(self,f_name):
  args=((ValueType.Text,None,f_name),)
  rep=self.sndrcv("WriteColorMap",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WriteDataSet(self,f_name,include_text,include_geom,include_custom_labels,include_data,zones_to_write,vars_to_write,write_binary,use_point_format,ascii_precision):
  args=((ValueType.Text,None,f_name),
        (ValueType.Scalar,c_bool,include_text),
        (ValueType.Scalar,c_bool,include_geom),
        (ValueType.Scalar,c_bool,include_custom_labels),
        (ValueType.Scalar,c_bool,include_data),
        (ValueType.Address,c_uint64,getattr(zones_to_write,'value',zones_to_write)),
        (ValueType.Address,c_uint64,getattr(vars_to_write,'value',vars_to_write)),
        (ValueType.Scalar,c_bool,write_binary),
        (ValueType.Scalar,c_bool,use_point_format),
        (ValueType.Scalar,c_int32,ascii_precision),)
  rep=self.sndrcv("WriteDataSet",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WriteStylesheet(self,f_name,include_plot_style,include_text,include_geom,include_stream_positions,include_contour_levels,include_factory_defaults):
  args=((ValueType.Text,None,f_name),
        (ValueType.Scalar,c_bool,include_plot_style),
        (ValueType.Scalar,c_bool,include_text),
        (ValueType.Scalar,c_bool,include_geom),
        (ValueType.Scalar,c_bool,include_stream_positions),
        (ValueType.Scalar,c_bool,include_contour_levels),
        (ValueType.Scalar,c_bool,include_factory_defaults),)
  rep=self.sndrcv("WriteStylesheet",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def WriteStylesheetX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("WriteStylesheetX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ZoneCopy(self,zone_used,i_min,i_max,i_skip,j_min,j_max,j_skip,k_min,k_max,k_skip):
  args=((ValueType.Scalar,c_int32,zone_used),
        (ValueType.Scalar,c_int64,i_min),
        (ValueType.Scalar,c_int64,i_max),
        (ValueType.Scalar,c_int64,i_skip),
        (ValueType.Scalar,c_int64,j_min),
        (ValueType.Scalar,c_int64,j_max),
        (ValueType.Scalar,c_int64,j_skip),
        (ValueType.Scalar,c_int64,k_min),
        (ValueType.Scalar,c_int64,k_max),
        (ValueType.Scalar,c_int64,k_skip),)
  rep=self.sndrcv("ZoneCopy",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ZoneCopyX(self,arg_list):
  args=((ValueType.Address,c_uint64,getattr(arg_list,'value',arg_list)),)
  rep=self.sndrcv("ZoneCopyX",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ZoneGetActive(self):
  rep=self.sndrcv("ZoneGetActive").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def ZoneGetActiveForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("ZoneGetActiveForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def ZoneGetEnabled(self):
  rep=self.sndrcv("ZoneGetEnabled").Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def ZoneGetEnabledByDataSetID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("ZoneGetEnabledByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def ZoneGetEnabledForFrame(self,frame_id):
  args=((ValueType.Scalar,c_int64,frame_id),)
  rep=self.sndrcv("ZoneGetEnabledForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def ZoneGetEnabledNamesByDataSetID(self,data_set_id):
  args=((ValueType.Scalar,c_int64,data_set_id),)
  rep=self.sndrcv("ZoneGetEnabledNamesByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_ptr(rep.Args(0)))
 def ZoneGetFieldMap(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetFieldMap",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ZoneGetIJK(self,cur_zone):
  args=((ValueType.Scalar,c_int32,cur_zone),)
  rep=self.sndrcv("ZoneGetIJK",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value())
 def ZoneGetIJKByUniqueID(self,dataset_id,zone):
  args=((ValueType.Scalar,c_int64,dataset_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetIJKByUniqueID",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value())
 def ZoneGetInfo(self,cur_zone):
  args=((ValueType.Scalar,c_int32,cur_zone),)
  rep=self.sndrcv("ZoneGetInfo",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value(),
   self.read_ptr(rep.Args(3)),
   self.read_ptr(rep.Args(4)),
   self.read_ptr(rep.Args(5)),
   self.read_ptr(rep.Args(6)),
   self.read_ptr(rep.Args(7)),
   self.read_ptr(rep.Args(8)),
   self.read_ptr(rep.Args(9)),
   self.read_ptr(rep.Args(10)),
   self.read_ptr(rep.Args(11)),
   self.read_ptr(rep.Args(12)))
 def ZoneGetInfoForFrame(self,frame_id,cur_zone):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,cur_zone),)
  rep=self.sndrcv("ZoneGetInfoForFrame",*args).Reply()
  self.chk(rep)
  return (
   rep.Args(0).Int64Value(),
   rep.Args(1).Int64Value(),
   rep.Args(2).Int64Value(),
   self.read_ptr(rep.Args(3)),
   self.read_ptr(rep.Args(4)),
   self.read_ptr(rep.Args(5)),
   self.read_ptr(rep.Args(6)),
   self.read_ptr(rep.Args(7)),
   self.read_ptr(rep.Args(8)),
   self.read_ptr(rep.Args(9)),
   self.read_ptr(rep.Args(10)),
   self.read_ptr(rep.Args(11)),
   self.read_ptr(rep.Args(12)))
 def ZoneGetName(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetName",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def ZoneGetNameByDataSetID(self,data_set_id,zone):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetNameByDataSetID",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def ZoneGetNameForFrame(self,frame_id,zone):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetNameForFrame",*args).Reply()
  self.chk(rep)
  return (
   (rep.Status() == Status.Success),
   self.read_text(rep.Args(0)))
 def ZoneGetNumByUniqueID(self,unique_id):
  args=((ValueType.Scalar,c_int64,unique_id),)
  rep=self.sndrcv("ZoneGetNumByUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ZoneGetParentZone(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetParentZone",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ZoneGetSolutionTime(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetSolutionTime",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Float64Value()
 def ZoneGetStrandID(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetStrandID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ZoneGetStrandIDByDataSetID(self,data_set_id,zone):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetStrandIDByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int32Value()
 def ZoneGetType(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetType",*args).Reply()
  self.chk(rep)
  return ZoneType(rep.Args(0).Int32Value())
 def ZoneGetTypeByDataSetID(self,data_set_id,zone):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetTypeByDataSetID",*args).Reply()
  self.chk(rep)
  return ZoneType(rep.Args(0).Int32Value())
 def ZoneGetUniqueID(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetUniqueID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ZoneGetUniqueIDByDataSetID(self,data_set_id,zone):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetUniqueIDByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ZoneGetUniqueIDForFrame(self,frame_id,zone):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneGetUniqueIDForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Int64Value()
 def ZoneIsActive(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsActive",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsEnabled(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsEnabled",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsEnabledByDataSetID(self,data_set_id,zone):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsEnabledByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsFEClassic(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsFEClassic",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsFEPolytope(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsFEPolytope",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsFiniteElement(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsFiniteElement",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsLinear(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsLinear",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsLinearByDataSetID(self,data_set_id,zone):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsLinearByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsLinearForFrame(self,frame_id,zone):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsLinearForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsOrdered(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsOrdered",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsOrderedByDataSetID(self,data_set_id,zone):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsOrderedByDataSetID",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsOrderedForFrame(self,frame_id,zone):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsOrderedForFrame",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneIsSZL(self,zone):
  args=((ValueType.Scalar,c_int32,zone),)
  rep=self.sndrcv("ZoneIsSZL",*args).Reply()
  self.chk(rep)
  return rep.Args(0).Boolean()
 def ZoneRealloc(self,zone,new_i_max_or_num_data_points,new_j_max_or_num_elements,new_k_max):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int64,new_i_max_or_num_data_points),
        (ValueType.Scalar,c_int64,new_j_max_or_num_elements),
        (ValueType.Scalar,c_int64,new_k_max),)
  rep=self.sndrcv("ZoneRealloc",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ZoneRename(self,zone,zone_name):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Text,None,zone_name),)
  rep=self.sndrcv("ZoneRename",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ZoneRenameByDataSetID(self,data_set_id,zone,zone_name):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),
        (ValueType.Text,None,zone_name),)
  rep=self.sndrcv("ZoneRenameByDataSetID",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ZoneRenameForFrame(self,frame_id,zone,zone_name):
  args=((ValueType.Scalar,c_int64,frame_id),
        (ValueType.Scalar,c_int32,zone),
        (ValueType.Text,None,zone_name),)
  rep=self.sndrcv("ZoneRenameForFrame",*args).Reply()
  self.chk(rep)
  return (rep.Status() == Status.Success)
 def ZoneSetActive(self,zone_set,assign_modifier):
  args=((ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_int32,AssignOp(assign_modifier).value),)
  rep=self.sndrcv("ZoneSetActive",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetBuildZoneOptInfo(self,zone,build_zone_opt_info):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_bool,build_zone_opt_info),)
  rep=self.sndrcv("ZoneSetBuildZoneOptInfo",*args).Reply()
  self.chk(rep)
 def ZoneSetContour(self,attribute,zone_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetContour",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetEdgeLayer(self,attribute,zone_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetEdgeLayer",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetMesh(self,attribute,zone_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetMesh",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetScatter(self,attribute,zone_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetScatter",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetScatterIJKSkip(self,attribute,zone_set,skip):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_int64,skip),)
  rep=self.sndrcv("ZoneSetScatterIJKSkip",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetScatterSymbolShape(self,attribute,zone_set,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetScatterSymbolShape",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetShade(self,attribute,zone_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetShade",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetSolutionTime(self,zone,solution_time):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_double,solution_time),)
  rep=self.sndrcv("ZoneSetSolutionTime",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetStrandID(self,zone,strand_id):
  args=((ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,strand_id),)
  rep=self.sndrcv("ZoneSetStrandID",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetStrandIDByDataSetID(self,data_set_id,zone,strand_id):
  args=((ValueType.Scalar,c_int64,data_set_id),
        (ValueType.Scalar,c_int32,zone),
        (ValueType.Scalar,c_int32,strand_id),)
  rep=self.sndrcv("ZoneSetStrandIDByDataSetID",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetVector(self,attribute,zone_set,d_value,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_double,d_value),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetVector",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetVectorIJKSkip(self,attribute,zone_set,skip):
  args=((ValueType.Text,None,attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.Scalar,c_int64,skip),)
  rep=self.sndrcv("ZoneSetVectorIJKSkip",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSetVolumeMode(self,attribute,sub_attribute,zone_set,i_value):
  args=((ValueType.Text,None,attribute),
        (ValueType.Text,None,sub_attribute),
        (ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),
        (ValueType.ArbParam,None,i_value),)
  rep=self.sndrcv("ZoneSetVolumeMode",*args).Reply()
  self.chk(rep)
  return SetValueReturnCode(rep.Args(0).Int32Value())
 def ZoneSolutionTimeModificationBegin(self):
  rep=self.sndrcv("ZoneSolutionTimeModificationBegin").Reply()
  self.chk(rep)
 def ZoneSolutionTimeModificationEnd(self):
  rep=self.sndrcv("ZoneSolutionTimeModificationEnd").Reply()
  self.chk(rep)
 def ZoneStyleApplyAuto(self,zone_set):
  args=((ValueType.Address,c_uint64,getattr(zone_set,'value',zone_set)),)
  rep=self.sndrcv("ZoneStyleApplyAuto",*args).Reply()
  self.chk(rep)