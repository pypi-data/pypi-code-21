import sys
from wtouch.touch import create_file


def main():
    if len(sys.argv) != 2:
        print('Usage: wtouch file_name')

        return

    file_name = sys.argv[1]

    create_file(file_name)

if __name__ == '__main__':
    main()
