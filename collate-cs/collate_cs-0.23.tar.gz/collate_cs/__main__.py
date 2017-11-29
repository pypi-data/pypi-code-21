import collate_cs
import sys

def main():
    print('running')
    if len(sys.argv) < 4:
        print('usage:')
        print('collate before_path after_path depth')
        exit()

    collate_cs._(sys.argv[1], sys.argv[2], int(sys.argv[3]))

if __name__ == "__main__":
    main()
