# pycube v0.5.2

class Cube:
    def __init__(self, key, nonce=""):
        self.key = ""
        self.master_list = []
        self.alphabet_dict = {}
        self.alphabet_dict_rev = {}
        self.start_char = 65
        self.alphabet_size = 26
        self.size_factor = 3
        for x in range(0,self.alphabet_size):
            self.alphabet_dict[chr(x + self.start_char)] = x
            self.alphabet_dict_rev[x] = chr(x + self.start_char)

        def gen_cube(depth, width, length):
            for z in range(0,depth):
                section_list = []
                for y in range(0,width):
                    alphabet = []
                    for x in range(0,length):
                        alphabet.append(chr(x + self.start_char))
                    for mod in range(0,y):
                        shift = alphabet.pop(0)
                        alphabet.append(shift)
                        shift = alphabet.pop(2)
                        alphabet.insert(44,shift)
                    section_list.append(alphabet)
                self.master_list.append(section_list)

        gen_cube(self.size_factor, self.size_factor, self.alphabet_size)
        self.init(key)
        if nonce != "":
            self.key_cube(nonce)

    def key_cube(self, key):
        for section in self.master_list:
            for char in key:
                char_value = self.alphabet_dict[char]
                sized_pos = char_value % self.size_factor
                for alphabet in section:
                    key_sub = alphabet.pop(char_value)
                    alphabet.append(key_sub)
                    for y in range(0,char_value):
                        if y % 2 == 0:
                            shuffle = alphabet.pop(0)
                            alphabet.append(shuffle)
                            shuffle = alphabet.pop(2)
                            alphabet.insert(44,shuffle)
        for char in key:
            char_value = self.alphabet_dict[char]
            sized_pos = char_value % self.size_factor
            for x in range(char_value):
                section = self.master_list.pop(sized_pos)
                self.master_list.append(section)

    def load_key(self, skey):
	self.key_list = []
        self.key = skey
        for element in self.key:
            self.key_list.append(element)

    def key_scheduler(self, key):
        sub_key = ""
        for element in key:
            pos = self.alphabet_dict[element]
            sized_pos = pos % self.size_factor
            section = self.master_list[sized_pos]
            sub_alpha = section[sized_pos]
            sub = sub_alpha.pop(pos)
            sub_alpha.append(sub)
            sub_key += sub
        self.load_key(sub_key)
        return sub_key
    
    def init(self, key):
        self.load_key(key)
        self.key_cube(key)

    def morph_cube(self, counter, sub_key):
        mod_value = counter % self.alphabet_size
        for section in self.master_list:
            for key_element in sub_key:
                key_value = self.alphabet_dict[key_element]
                shift_value = key_value % self.size_factor
                for alphabet in section:
                    alphabet[shift_value], alphabet[mod_value] = alphabet[mod_value], alphabet[shift_value]
            section_shift = self.master_list.pop(key_value % self.size_factor)
            self.master_list.append(section_shift)

    def encrypt(self, words):
        cipher_text = ""
        sub_key = self.key
        for counter, letter in enumerate(words):
            sub = letter
            for section in self.master_list:
                for alphabet in section:
                    sub_pos = self.alphabet_dict[sub]
                    sub = alphabet[sub_pos]
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
            cipher_text += sub
        return cipher_text

    def decrypt(self, words):
        plain_text = ""
        sub_key = self.key
        for counter, letter in enumerate(words):
            sub = letter
            for section in reversed(self.master_list):
                for alphabet in reversed(section):
                    sub_pos = alphabet.index(sub)
                    sub = self.alphabet_dict_rev[sub_pos]
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
            plain_text += sub
        return plain_text

class CubeRandom:
    def __init__(self, poolsize=16):
        from os import urandom
        entropy = urandom(poolsize)
        self.iv = chr(65)
        self.entropy = ""
        for byte in entropy:
            self.entropy += chr(ord(byte) % (90 - 65 + 1) + 65)

    def random(self, num=1, min=65, max=90):
        iv = self.iv * num
        return  Cube(self.entropy).encrypt(iv)
        result = ""
        for byte in randbytes:
            char = chr(ord(byte) % (max - min + 1) + min)
            result += char
        return result

class CubeHash:
    def __init__(self, hashlength=32, basechar=65):
        self.hashlength = hashlength
        self.base = chr(basechar) * hashlength

    def digest(self, data, key=""):
        return Cube(key+data, self.base).encrypt(self.base)

class CubeKDF:
    def __init__(self, keysize=32, iterations=10):
        self.iterations = iterations
        self.cubehash = CubeHash(keysize)

    def genkey(self, key):
        for x in range(self.iterations):
            key = self.cubehash.digest(key)
        return key

class CubeHMAC:
    def __init__(self, nonce_length=8):
        self.nonce_length = nonce_length
        self.digest_length = 32

    def encrypt(self, data, key, nonce="", aad="", pack=True):
        primary_key = CubeKDF().genkey(key)
        if nonce == "":
            nonce = CubeRandom().random(self.nonce_length)
        hash_key = CubeKDF().genkey(primary_key)
        msg = Cube(primary_key, nonce).encrypt(data)
        digest1 = CubeHash().digest(key+aad+nonce+msg)
        digest = CubeHash().digest(hash_key+digest1)
        if pack == False:
            return aad, nonce, digest, msg
        else:
            return aad+nonce+digest+msg

    def decrypt(self, data, key, nonce="", aad="", aadlen=0, digest="", pack=True):
        primary_key = CubeKDF().genkey(key)
        hash_key = CubeKDF().genkey(primary_key)
        if pack == False:
            digest1 = CubeHash(key+aad+nonce+data).digest(key+aad+nonce+data)
            if CubeHash().digest(hash_key+digest1) == digest:
                return Cube(primary_key, nonce).decrypt(data)
            else:
                raise ValueError('HMAC failed: Message has been tampered with!')
        else:
            aad = data[:aadlen]
            nonce = data[aadlen:aadlen+self.nonce_length]
            digest = data[aadlen+self.nonce_length:aadlen+self.nonce_length+self.digest_length]
            msg = data[aadlen+self.nonce_length+self.digest_length:]
            digest1 = CubeHash().digest(key+aad+nonce+msg)
            if CubeHash().digest(hash_key+digest1) == digest:
                return Cube(primary_key, nonce).decrypt(msg)
            else:
                raise ValueError('HMAC failed: Message has been tampered with!')

class DataNormalizer:
    def normalize(self, data):
        return "".join(data.split()).strip('\n').upper()
