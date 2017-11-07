
import random
import string

def make_random_string(length=8):
   return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(length))
