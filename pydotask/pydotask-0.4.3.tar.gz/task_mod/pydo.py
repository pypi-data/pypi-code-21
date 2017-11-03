''' To Do App in Python '''

import sys, os
import subprocess
import task_mod.taskhandler as task
import task_mod.styles.text_style as text
import task_mod.styles.termcolor

# Function

def make_file():

    prompt = input("File 'tasks.csv' is not found here, Would you like to make a new one?")

    if prompt == 'yes' or prompt == 'y':
        subprocess.call(["touch","tasks.csv"])
# Global

def Main():

    #Reset Shortcut
    resetc = task_mod.styles.termcolor.colors.reset

    #Opening
    print(chr(27) + "[2J") #clears terminal
    text.hellotext()

    #Help
    task.helpme()

    while True:

        try:
            command = input(task_mod.styles.termcolor.colors.fg.lightcyan + 'PyDo $ ' + resetc).lower()

            task.update_program(task.task)

            #Checks Commands
            if command in ['add','-add','-a','-A']:
                task.addTask()
                print('\n')
            elif command in ['remove','-remove','-r','-R']:
                task.delTask(task.task)
                print('\n')
            elif command in ['show','-show','show task','showtask','-s','-S']:
                task.showTask(task.task)
                print('\n')
            elif command in ['help','-help','-h']:
                task.helpme()
            elif command in ['quit','end','End','-q','-Q','-quit']:
                sys.exit()
                break
            elif command in ['clear','-c','-clear']:
                print(chr(27) + "[2J")
                text.hellotext()
                task.helpme()
            #elif command == '-task': only for testing errors
            #    print(task.task)
            else:
                continue

        except IndexError:
            print(task_mod.styles.termcolor.colors.fg.lightred + 'Oops something went wrong :/\n' + resetc)

        except EOFError:
            sys.exit()
            break

        except FileNotFoundError:
            make_file()


        #print('\n')
Main()
