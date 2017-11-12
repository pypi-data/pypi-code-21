from subprocess import call, check_output
import re
import readline
import click
import sys
from pshelf.cleanup import delete 
from pshelf.userInput import reader, codeblock, newOrNot, mainOrNot
import os 

@click.command()
@click.option('--empty', is_flag=True, help='Initializes an empty java file.')
def shelf(empty):
    '''
    pshelf is a pythonic way of learning Java. Let\'s get on the ride
    and be a pythonista.
    '''
    msg = '''# Welcome to pshelf.\n# Wanna say hello, start by \'System.out.println("Hello pshelf");\'.'''
    print (msg)
    entries = {}
    #variables = {}

    if not empty:
        with open("jTemplate.txt", "r") as template:
            lines  = template.readlines()

    else:
        print('Not yet implemented.')
        sys.exit(0)        

    try:
        while True:
            com = reader()
            if com == 'empty':
                continue
                
            flag, name = newOrNot(com)
            if flag:
                fileName = "./temporary/"+name+".java"
                with open(fileName, "w+") as destFile:
                    com = "package temporary; \n" + com
                    destFile.write(com)
                try:
                    if call(['javac',fileName]) == 0:
                        run = mainOrNot(com)
                        if run:
                            outputFile = "temporary." + name
                            if call(['java', outputFile]) == 0:
                                pass
                            else:
                                os.remove(fileName)
                    else:
                        os.remove(fileName)
                except KeyboardInterrupt:
                    pass        
                except Exception as e:
                    pass           

            else:    
                lines, idx= codeblock(com, lines)
                entries['latest'] = idx
    
                with open("./temporary/TempJava.java", "w+") as destFile:
                    for line in lines:
                        destFile.write(line)
                try:
                    if call(['javac','./temporary/TempJava.java']) == 0:
                        if call(['java', 'temporary.TempJava']) == 0:
                            out = check_output(['java', 'temporary.TempJava'])
                            if out:
                                del lines[entries['latest']]

                        else:
                            del lines[entries['latest']]

                    else:
                        del lines[entries['latest']]
                except KeyboardInterrupt:
                    pass        
                except Exception as e:
                    del lines[entries['latest']]            

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print (e)

    finally:
        delete()   
        print ("Extinguishing the light, exiting the shell.")
