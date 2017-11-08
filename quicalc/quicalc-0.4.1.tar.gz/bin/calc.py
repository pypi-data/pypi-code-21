#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Quick Calculator on Linux Terminal '''

# Imports
import sys, os
import math
import statistics

# Functions

def helper():

    # Openings
    print(bold + lite_blue + '\nQuick Calculator Guide' + reset)
    print(lite_blue + 'using python library math and statistics')

    print('make sure to specify the module along with the functions' + reset)
    print(lite_green + '\n ex : math.sqrt(2) -> module.function(value)' + reset)

    # Functions
    print(lite_cyan + '\nFunctions :' + reset)
    print(lite_green + '\tmath.ceil(...) ' + reset  + '---------- Round Up')
    print(lite_green + '\tmath.floor(...) ' + reset  + '--------- Round Down')
    print(lite_green + '\tmath.sin(...) ' + reset  + '----------- Sine Function')
    print(lite_green + '\tmath.cos(...) ' + reset  + '----------- Cosinus Function')
    print(lite_green + '\tmath.tan(...) ' + reset  + '----------- Tangent Wave')
    print(lite_green + '\tmath.pow(...) ' + reset  + '----------- Power / Exponents')
    print(lite_green + '\tmath.factorial(...) ' + reset  + '----- Factorials(!)')
    print(lite_green + '\tmath.log(...) ' + reset  + '----------- Logarithms (n log n)')
    print(lite_green + '\tmath.sqrt(...) ' + reset  + '---------- Square Roots (√x)')
    print(lite_green + '\tstatistics.mean(...) ' + reset  + '---- Average')
    print(lite_green + '\tstatistics.median(...) ' + reset  + '-- Middle Value')
    print(lite_green + '\tstatistics.mode(...) ' + reset  + '---- Most Common Value')

    # Variables
    print(lite_cyan + '\nVariables :' + reset)
    print(lite_green + '\tmath.pi' + reset  + ' ----------------- PI(π)')
    print(lite_green + '\tmath.e ' + reset  + '------------------ Euler\'s number(e)')
    print(lite_green + '\tAns ' + reset  + '--------------------- Previous Answer')

    print(lite_blue + '\nFor more functions and variable, Type in ' + bold + 'help(...)' + reset + lite_blue +' depending on module you are using' + reset)


def win_helper():

    # Openings
    print('\nQuick Calculator Guide')
    print('using python library math and statistics')

    print('make sure to specify the module along with the functions')
    print('\n ex : math.sqrt(2) -> module.function(value)')

    # Functions
    print('\nFunctions :')
    print('\tmath.ceil(...) ' + '---------- Round Up')
    print('\tmath.floor(...) ' + '--------- Round Down')
    print('\tmath.sin(...) ' + '----------- Sine Function')
    print('\tmath.cos(...) ' + '----------- Cosinus Function')
    print('\tmath.tan(...) ' + '----------- Tangent Wave')
    print('\tmath.pow(...) ' + '----------- Power / Exponents')
    print('\tmath.factorial(...) ' + '----- Factorials(!)')
    print('\tmath.log(...) ' + '----------- Logarithms (n log n)')
    print('\tmath.sqrt(...) ' + '---------- Square Roots (√x)')
    print('\tstatistics.mean(...) ' + '---- Average')
    print('\tstatistics.median(...) ' + '-- Middle Value')
    print('\tstatistics.mode(...) ' + '---- Most Common Value')

    # Variables
    print('\nVariables :')
    print('\tmath.pi' + ' ----------------- PI(π)')
    print('\tmath.e ' + '------------------ Euler\'s number(e)')
    print('\tAns ' + '--------------------- Previous Answer')

    print('\nFor more functions and variable, Type in ' + 'help(...)' +  ' depending on module you are using')


# Aesthetic Value

reset = '\033[0m'
bold = '\033[01m'
pink = '\033[95m'
lite_green = '\033[92m'
lite_blue = '\033[94m'
lite_cyan = '\033[96m'
blue = '\033[34m'
red = '\033[31m'
yellow = '\033[93m'

# Start of the program

def calc():

    ''' The main program of quicalc, handles all the calculations '''

    print(bold + pink + 'QuiCalc (Quick Calculator)' + reset)

    while True :

        print(pink + '\nCalculate :' + reset)

        try:
            userinp = input()

            if userinp in ['-q','-quit','quit']:
                sys.exit()
                break

            elif userinp == 'help' or userinp == 'docs':
                helper()

            else :
                Ans = eval(userinp)
                print(lite_green + str(Ans) + reset)

        # Error Handler...

        except NameError or ValueError:
            print(red + 'Something went wrong, Try Again...' + reset)

        except TypeError:
            print(yellow + 'Arguments are expected, type \'help\' for info' + reset)

        except AttributeError:
            print(yellow + 'Missing module or attribute, type \'help\' for info')

        except ZeroDivisionError:
            Ans = 'undefined'
            print(lite_green + str(Ans) + reset)

        except SyntaxError:
            print(red + 'Something went wrong, Try Again...' + reset)

        except EOFError:
            sys.exit()
            break

def win_calc():

    ''' This works on windows, the same as calc() but works better on windows '''

    print('QuiCalc (Quick Calculator)')

    while True :

        print('\nCalculate :')

        try:
            userinp = input()

            if userinp in ['-q','-quit','quit']:
                sys.exit()
                break

            elif userinp == 'help' or userinp == 'docs':
                win_helper()

            else :
                Ans = eval(userinp)
                print(str(Ans))

        # Error Handler...

        except NameError or ValueError:
            print('Something went wrong, Try Again...')

        except TypeError:
            print('Arguments are expected, type \'help\' for info')

        except AttributeError:
            print('Missing module or attribute, type \'help\' for info')

        except ZeroDivisionError:
            Ans = 'undefined'
            print(str(Ans))

        except SyntaxError:
            print('Something went wrong, Try Again...')

        except EOFError:
            sys.exit()
            break


def Main():

    ''' The main runner of the program, classifies which OS is being used and calling the function '''


    if os.name == 'nt':
        win_calc()
    else :
        calc()


Main()
