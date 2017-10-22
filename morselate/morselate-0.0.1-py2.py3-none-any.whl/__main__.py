"""Main module to run morselate"""
import sys
from . import demorse, emorse

if __name__ == "__main__":
    if len(sys.argv) == 1 or '-h' in sys.argv:
        print("""
Usage: 
decode [-e] MORSE
Yet another morse encoder/decoder!

    -e  Encodes a text instead of decoding a morse
        """)

    if '-e' in sys.argv:
        print(emorse(sys.argv[2:]))    
    print(demorse(sys.argv[1:]))
