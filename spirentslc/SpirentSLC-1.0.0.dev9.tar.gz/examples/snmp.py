from SpirentSLC import SLC
slc = SLC.init(host='localhost:9005')
p = slc.my_project.open()
s = p.PC_tbml.pc1.snmp.open()
print(s.get('MIB-2::system.sysDescr'))