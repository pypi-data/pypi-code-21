#!/usr/bin/env python3

from sys import stdin
from os import system,path


class getch:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def printLogo(filename):
    file=open(filename,'r')
    data=file.read()
    system("clear")
    print(data)

class Menu:
    def __init__(self,options,instructions,logoName):
        self.options=options
        self.instructions=instructions
        self.logoName=logoName

    def arrow(self,count,tabs):
        printLogo(self.logoName)
        print("\n\n\t\t\t\t     "+self.instructions+"\n\n")
        for i in range(len(self.options)):
            if(tabs):
                print("\t\t\t\t      ",end="")
            else:
                print("\t\t   ",end="")
            if(i==count):
                print("->>>>>>[ "+self.options[i]+"   \n")
            else:
                print("       [ "+self.options[i]+"    \n")

    def prompt(self,tabs=True):
        count=0
        getc=getch()
        self.arrow(count,tabs)
        key=" "
        while(ord(key)!=13):
            key=getc()
            if(ord(key)==66):
                if(count<len(self.options)-1):
                    count+=1
            elif(ord(key)==65):
                if(count>0):
                    count-=1
            self.arrow(count,tabs)
        return count

