class Fold:
    def __init__(self, key="", alphabet="", foldsize=4, padding=True):
        self.padding = padding
        self.foldsize = foldsize
        if alphabet != "":
            self.alphabet = alphabet
        else:
            self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/!#%"
        self.charset = []
        for char in self.alphabet:
            self.charset.append(char)
        mid = len(self.charset) / 2
        if key != "":
            for byte in key:
                self.charset.append(self.charset.pop(ord(byte) % len(self.alphabet)))
                for x in range(ord(byte)):
                    self.charset.append(self.charset.pop(ord(byte) % len(self.alphabet)))
                    self.charset.append(self.charset.pop(0))
                    self.charset.insert(mid, self.charset.pop(3))

    def encode(self, data):
        encoded = ""
        for byte in data:
            byte_value = ord(byte) / self.foldsize
            extrabit = ord(byte) % self.foldsize
            block = ""
            for x in range(2):
                if x == 1:
                    if extrabit != 0:
                        block += self.charset[byte_value + extrabit]
                    else:
                        if self.padding == True:
                            if len(block) == 1:
                                block += "="
                else:
                    block += self.charset[byte_value]
            encoded += block
        return encoded
    
    def decode(self, data):
        if self.padding != True:
            raise ValueError('Error: decode not supported with padding enabled')
        decoded = ""
        blocks = []
        block = []
        start = 0
        end = 2
        nblocks = len(data) / 2
        for x in range(nblocks):
            block = data[start:end]
            start += 2
            end += 2
            blocks.append(block)
        data = ""

        for b in blocks:
            index0 = self.charset.index(b[0])
            val1 = index0 * self.foldsize
            val2 = 0
            if b[1] != "=":
                index1 = self.charset.index(b[1])
                diff = index1 - index0
                newbyte =  chr(val1 + diff)
            else:
                newbyte = chr(val1 + val2)
            decoded += newbyte
        return decoded
