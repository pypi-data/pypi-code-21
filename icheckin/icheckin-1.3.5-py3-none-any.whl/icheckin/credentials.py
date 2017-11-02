import click
import operator
from icheckin import constants
from os.path import exists

def exist():
   '''
   -> boolean: whether the file exists
   '''
   return exists(constants.PATH)

def maximum():
   '''
   -> int: maximum credentials allowed
   '''
   return constants.MAX

def primary():
   '''
   -> (student id, password)  : Primary credentials 
   -> ()                      : No primary credentials
   '''
   credsList = read()
   if len(credsList) != 0:
      return credsList[0]
   else:
      return ()

def empty():
   '''
   -> True  : Empty credentials
   -> False : Non-empty credentials
   '''
   return len(read()) == 0

def display(credsList, title='Credentials', noPrimary=False, numbering=False):
   click.echo()
   click.echo(title)
   click.echo('-'*len(title))
   empty = True if len(credsList) == 0 else False
   if not empty:
      studentIds = map(operator.itemgetter(0), credsList)
      spacing = max(list(map(lambda x: len(x), studentIds))) + 1
      digits = len(str(len(credsList)-1))
      for i in range(len(credsList)):
         if numbering:
            click.echo('[%s] ' % str(i).rjust(digits), nl=False)
         click.echo('%s: %s' % (
            credsList[i][0].ljust(spacing),
            credsList[i][1]), nl=False)
         if i == 0:
            click.echo('%s' % '' if noPrimary else ' (Primary)')
         else:
            click.echo()
   else:
      click.echo('(Empty)')
   click.echo()

def prompt(prompt1='Student id', prompt2='Password'):
   ''' 
   -> tuple: (student id, password)
   '''
   studentId = input(prompt1+': ')
   password = input(prompt2+': ')
   return (studentId, password)

def read():
   '''
   -> list: [(student id, password), (), ...]
   '''
   credsList = []
   if exist():
      with open(constants.PATH, 'r') as file:
         lines = list(map(str.strip, file.readlines()))
         if len(lines) % 2 == 0:
            for i in range(0, len(lines), 2):
               credsList.append((lines[i], lines[i+1]))
   return credsList

def write(credsList, _mode='w'):
   assert len(credsList) <= maximum()
   with open(constants.PATH, _mode) as file:
      for creds in credsList:
         file.write(creds[0]+'\n')
         file.write(creds[1]+'\n')

def append(credsList):
   assert exist()
   assert len(read()) + len(credsList) <= maximum()
   write(credsList, _mode='a')

def delete(indexList):
   assert exist()
   creds = read()
   for index in sorted(indexList, reverse=True):
      assert index >= 0 and index < len(creds)
      creds.pop(index)
   write(creds)

def clear():
   assert exist()
   write([])