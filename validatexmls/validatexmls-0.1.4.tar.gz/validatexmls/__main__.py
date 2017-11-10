import os
#from validatexmls import main, validatexmls
import validatexmls
import click

__main__dir = os.path.abspath(os.path.dirname(__file__))
print('Running __main__ in dir:', __main__dir)

def main():
   validatexmls.main()


if __name__ == '__main__':
    main()
