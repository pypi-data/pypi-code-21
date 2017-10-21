import argparse

def bytes2string(fpath):
    with open(fpath, 'rb') as f:
        data = f.read()
    print(data[0])

    txt = list(map(chr, data))
    print(txt[0])

    with open(fpath+'.txt', 'w') as f:
        f.write("".join(txt))

def string2bytes(fpath):
    with open(fpath) as f:
        txt = f.read()
    bytes_data = list(map(ord, txt))
    print(bytes_data[0])

    with open(fpath+'.bytes', 'wb') as f:
        f.write(bytearray(bytes_data))

def main():
    parser = argparse.ArgumentParser(description='Convert byte to string and vice versa.')
    parser.add_argument('fpath',
                        help='path to convert')
    parser.add_argument('--backwards', '-b', action='store_true',
                        help='convert back')

    args = parser.parse_args()
    if args.backwards:
        string2bytes(args.fpath)
    else:
        bytes2string(args.fpath)

if __name__ == "__main__":
    main()
