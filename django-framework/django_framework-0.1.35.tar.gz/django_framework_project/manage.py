#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sys.path.insert(0,currentdir) 
    
    parentdir = os.path.dirname(currentdir)
#     parentdir = os.path.dirname(parentdir)
    print('test.py', parentdir)
    sys.path.insert(0,parentdir) 
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_framework_project.django_framework_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
