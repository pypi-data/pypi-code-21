# encoding: utf-8
#
# Autogenerated by Thrift Compiler (0.9.2)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:new_style
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
import sds.errors.ttypes


from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class ThriftProtocol(object):
  """
  thrift传输协议
  """
  TCOMPACT = 0
  TJSON = 1
  TBINARY = 2
  TBINARYACCELERATED = 3

  _VALUES_TO_NAMES = {
    0: "TCOMPACT",
    1: "TJSON",
    2: "TBINARY",
    3: "TBINARYACCELERATED",
  }

  _NAMES_TO_VALUES = {
    "TCOMPACT": 0,
    "TJSON": 1,
    "TBINARY": 2,
    "TBINARYACCELERATED": 3,
  }


class Version(object):
  """
  版本号，规则详见http://semver.org

  Attributes:
   - major: 主版本号，不同版本号之间不兼容
   - minor: 次版本号，不同版本号之间向后兼容
   - patch: 构建版本号，不同版本之间互相兼容
   - comments: 附加信息
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'major', None, 1, ), # 1
    (2, TType.I32, 'minor', None, 0, ), # 2
    (3, TType.STRING, 'patch', None, "1e36bc45", ), # 3
    (4, TType.STRING, 'comments', None, "", ), # 4
  )

  def __init__(self, major=thrift_spec[1][4], minor=thrift_spec[2][4], patch=thrift_spec[3][4], comments=thrift_spec[4][4],):
    self.major = major
    self.minor = minor
    self.patch = patch
    self.comments = comments

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.major = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.minor = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.patch = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.comments = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Version')
    if self.major is not None:
      oprot.writeFieldBegin('major', TType.I32, 1)
      oprot.writeI32(self.major)
      oprot.writeFieldEnd()
    if self.minor is not None:
      oprot.writeFieldBegin('minor', TType.I32, 2)
      oprot.writeI32(self.minor)
      oprot.writeFieldEnd()
    if self.patch is not None:
      oprot.writeFieldBegin('patch', TType.STRING, 3)
      oprot.writeString(self.patch)
      oprot.writeFieldEnd()
    if self.comments is not None:
      oprot.writeFieldBegin('comments', TType.STRING, 4)
      oprot.writeString(self.comments)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.major)
    value = (value * 31) ^ hash(self.minor)
    value = (value * 31) ^ hash(self.patch)
    value = (value * 31) ^ hash(self.comments)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
