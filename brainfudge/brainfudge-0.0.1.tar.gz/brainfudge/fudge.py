import argparse

from brainfudge.main import run

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", type=str, help="Directory to brainfudge file")
parser.add_argument("-r", "--repl", help="Open brainfudge in REPL mode", action="store_true")
args = parser.parse_args()

def main():
    if args.file:
        try:
            with open(args.file) as file:
                file.seek(0)
                run(file.read())
        except FileNotFoundError:
            print("File not found! Ending.")
    elif args.repl:
        try:
            while True:
                bf = input("\n>>> ")
                if bf == 'exit':
                    exit(0)
                run(bf)
        except KeyboardInterrupt:
            print("Ending.")
            exit(0)

if __name__ == '__main__':
    main()