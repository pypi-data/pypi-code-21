import re

def reader():
    commands = []
    code = input('pshelf>  ')
    if code == "":
        return "empty"

    commands.append(code)
    lst = list(code)

    while True:
        c1 = lst.count('{')
        c2 = lst.count('}')
   
        if lst[-1] == ';':
            if c1==c2:
                break
            else:
                more = input('   ...   ')
                commands.append(more)
                lst.extend(list(more))    
        
        elif lst[-1] == '}':

            if  c1==c2:
                break
            else:
                while c1 != c2:
                    more = input('   ...   ')
                    commands.append(more)
                    l = list(more)

                    temp_c1 = l.count('{')
                    temp_c2 = l.count('}')

                    c1 += temp_c1
                    c2 += temp_c2

            break        

        else:
            more = input('   ...   ')
            commands.append(more)
            lst.extend(list(more))

    st = ''
    for i in commands:
        l = list(i)

        for j in range(len(l)):
            if l[j]=='{' or l[j]==';' or l[j]=='}':
                l.insert(j+1,'\n')

        if l[-1] == ';' or  l[-1] == '}' or l[-1] == '{':
            st += ''.join(l) + '\n'
        else:
            st += ''.join(l)        

    print ('#',st)

    return st

def methodCatch(command):
    p = re.compile(r'[)][\s]*(\bthrows \b[\w,\s]*[\w])?[\s]*[{]')
    eq = re.compile(r'=')
    if p.search(command):
        if eq.search(command):
            return (False, command)
        s = command.split()
        if 'static' not in s:
            if len(s)>1:
                i = 0
                for word in s:
                    if '(' in list(word):
                        break
                    i += 1
                s.insert(i-1, 'static')
            else:
                s.insert(0,'static')                
            return (True, ' '.join(s))
    else:
        return (False, command)

def codeblock(commands, lines):

    keywords = {
        'import': re.compile(r'import'),
        'interface': re.compile(r'interface'),
        'class' : re.compile(r'class'),
        'function': re.compile(r'function'),
        'enum':re.compile(r'enum'),
        'nested':(  
            re.compile(r'protected class'), re.compile(r'private class'),
            re.compile(r'protected interface'), re.compile(r'private interface')
            ),    
    }

    idx = 0

    flag = False
    for ptn in keywords['nested']:
        if ptn.search(commands):
            idx=lines.index('//nested\n') + 1
            flag = True
            s = commands.split()
            if 'class' in s:
                cIn = s.index('class')
                s.insert( cIn - 1 , 'static')
                commands = ' '.join(s)
            break

    if not flag:        

        if keywords['import'].search(commands):
            idx=lines.index('//imports\n') + 1

        elif keywords['interface'].search(commands):
            idx=lines.index('//interfaces\n') + 1

        elif keywords['class'].search(commands):
            idx=lines.index('//classes\n') + 1

        elif keywords['enum'].search(commands):
            idx=lines.index('//enums\n') + 1   
        elif methodCatch(commands)[0]:
            commands = methodCatch(commands)[1]
            idx = lines.index('//methods\n')
        else:        
            idx=lines.index('//code\n')   
    
    lines.insert(idx,commands + '\n')    

    return (lines, idx)

def mainOrNot(com):
    st1 = "public static void main(String[] args)"
    st2 = "public static void main(String args[])"
    if st1 not in com and st2 not in com:
        return False
    else:
        return True

def newOrNot(st):
    key = ('public')
    st = st.replace('{',' ')
    temp = st.split()

    if 'class' in temp:
        idx = temp.index('class')
        if idx>0 and temp[idx-1] in key: 
            return (True,temp[idx+1])
        elif idx==0 and mainOrNot(st):
            return (True,temp[idx+1])
        else:
            return(False, "No need")    
    
    elif 'interface' in temp:
        idx=temp.index('interface')
        if idx>0 and temp[idx-1] in key:
            return (True, temp[idx+1])
        else:
            return (False, "No need")        
    
    return (False,"No need")
