#!./env/bin/python

'''
Simple 'todo' command. It allows to mantain a todo-list in the form of a stack.
Usage:

$ todo [option][argument]

Possible options are:
  -h : prints this message
  -a [text]: add a new todo to the stack
  -p : pop the last position of the stack
  -l : list all todos
  -r [number]: removes position indicated by numberkaging.python.org/tutorials/distributing-packages/
'''

#TODO: preparar setup que incluya el comando en el path
#todo: sube bien al repo de test y se instala. Pero la llamada directa de consola da error


import sys, getopt
from tinydb import TinyDB, Query

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:plr:", ["help", "add=", "pop", "list", "remove="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if len(opts)>1:
        usage()
        sys.exit(2)
    if len(opts)==0:
        list()
    else:
        source = "".join(args)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-a", "--add"):
                add(arg)
            elif opt in ("-p", "--pop"):
                pop()
            elif opt in ("-l", "--list"):
                list()
            elif opt in ("-r", "--remove"):
                remove(arg)



def usage():
    msg = """Simple 'todo' command. It allows to mantain a todo-list in the form of a stack.
        Usage:

        $ todo [option][argument]

        Possible options are:
          -h : prints this message
          -a [text]: add a new todo to the stack
          -p : pop the last position of the stack
          -l : list all todos
          -r [number]: removes position indicated by numberkaging.python.org/tutorials/distributing-packages/"""
    print(msg)

def add(texto):
    db = TinyDB('db.json')
    count = len(db)
    db.insert({'id':count+1, 'text':texto})

def pop():
    db = TinyDB('db.json')
    todo = Query()
    count = len(db)
    db.remove(todo.id == count)

def list():
    db = TinyDB('db.json')
    l = db.all()
    if len(l)>0:
        for reg in l:
            print("%d -- %s"%(reg['id'], reg['text']))
    else:
        print("-- Lista vacia --")

def remove(id):
    db = TinyDB('db.json')
    q = Query()
    print(db.remove(q.id == int(id)))
    renumera()

def renumera():
    db = TinyDB('db.json')
    q = Query()
    all = db.all()
    lista_ordenada = sorted(all, key=lambda doc:doc['id'])
    i=0
    for reg in lista_ordenada:
       i+=1
       db.update({'id': i}, q.id == reg['id'])


if __name__ == "__main__":
    main()

