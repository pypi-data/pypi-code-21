# -*- coding: utf-8 -*-
"""
Created on Thu May 29 15:52:42 2014

@author: danaukes
"""
import os
import importlib

def fileList(source,key='.py'):
    matches = []
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            if os.path.splitext(filename)[1]==key:
                matches.append(os.path.join(root, filename))
    return matches

def findinfile(filename,expression):
    code = []
    with open(filename,'r') as f:
        lines = f.readlines()
    code = [line for line in lines if expression in line]
    return code 

def filter_known(filter_list,modules):
    modules_out = [module for module in modules if any([key in module for key in filter_list])]
    return modules_out

def filter_python_packaged(modules):
    import sys
    modules_out = []
    for module in modules:
        found_key = False
        try:
            if 'C:\\Anaconda3\\lib\\' in sys.modules[module].__file__:
                if not 'C:\\Anaconda3\\lib\\site-packages' in sys.modules[module].__file__:
                    found_key = True
        except KeyError:
#            print(module+' is not loaded.  it must be a site-package')
            pass
        except AttributeError:
#            print(module+' is missing __file__ attribute')
            found_key = True
        if not found_key:
            modules_out.append(module)
    return modules_out

def filter_sub_modules(submodules,modules):
    submodules_out = [submodule for module in modules for submodule in submodules if module in submodule]
    return submodules_out

def clean_code(code):
    code = [line.strip('\n') for line in code]
    code = [line.split('#')[0] for line in code]
    code = [line for line in code if line != '']
    return code

def get_modules_from_code(code):
    fromsyntax = []
    importsyntax = []
    
    for line in code:
        if line.find('from')!=-1:
            fromsyntax.append(line)
        else:
            importsyntax.append(line)
    
    modules = []
    
    for line in fromsyntax:
        line2 = line.split(' ')
        try:
            ii = line2.index('from')
            modules.append(line2[ii+1])
        except ValueError:
            pass
        
    for line in importsyntax:
        line2 = line.split(' ')
        try:
            ii = line2.index('import')
            modules.append(line2[ii+1])
        except ValueError:
            pass
    modules = sorted(set(modules))
                
    return modules
    
def get_modules_and_submodules(module):
    mod = importlib.import_module(module)
    pathname = os.path.split(mod.__file__)[0]
#    file,pathname,description = imp.find_module(module)    
    files = fileList(pathname)
    code = []
    for filename in files:
        code.extend(findinfile(filename,'import'))
        
    code = clean_code(code)
    all_modules = get_modules_from_code(code)
    
    top_modules= [item.split('.')[0] for item in all_modules]        
    top_modules= [module for module in top_modules if module!='']        
    top_modules = filter_python_packaged(top_modules)
    top_modules = sorted(set(top_modules))


    submodules = all_modules[:]    
    submodules = filter_sub_modules(submodules,top_modules)
    
    submodules = sorted(set(submodules))
    return top_modules,submodules

def printinfo(modules,title='MODULES'):
    module_string = ''.join([module+'\n' for module in modules])
    
    print(title)
    print('###########################')
    print(module_string)


if __name__=='__main__'    :
    
#    my_modules = ['popupcad','dev_tools','popupcad_deprecated','popupcad_gazebo','popupcad_manufacturing_plugins','pypoly2tri']
    import sys
    my_modules = sys.argv[1:]
    modules_by_module = [get_modules_and_submodules(item) for item in my_modules]
    printinfo(modules_by_module[0][0])    
    printinfo(modules_by_module[0][1],'SUBMODULES')    
