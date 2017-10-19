from proteusisc.jtagDevice import JTAGDevice
from proteusisc.bittypes import ConstantBitarray, bitarray

import intelhex
#intelhex.IntelHex

class XilinxPlatformFlashXCFXXS(JTAGDevice):
    devices = (
        b'\x05\x04\x40\x93', #xcf01s
        b'\x05\x04\x50\x93', #xcf02s
        b'\x05\x04\x60\x93', #xcf04s
    )

    def erase(self):
        _, status = self.run_instruction("BYPASS", read_status=True)
        print("    PRE STATUS", status())
        #if status() != bitarray('00000001'):
        #    #attribute INSTRUCTION_CAPTURE : entity is "XXXXX001";
        #    #IR[7:6] Internal Erase/Program Error (10=success; 01=fail; 00/11=N/A)
        #    #IR[5] Internal Erase/Program Status (1=ready; 0=busy)
        #    #IR[4] ISP mode (1=in-system programming mode; 0=normal download mode)
        #    #IR[3] JTAG read-protection (1=secured; 0=unsecured)
        #    raise Exception("Device is write protected")

        self.run_instruction("ISPEN", data=bitarray('001101'))
        self.run_instruction("FADDR", loop=2,
                             data=bitarray('0000000000000001'))
        self.run_instruction("FERASE", loop=3000000)
        _, status = self.run_instruction("BYPASS", read_status=True)

        print("    POST STATUS", status())

    def program(self, confpath):
        pass
